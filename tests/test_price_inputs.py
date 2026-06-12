"""§5 Pass-1 — the grounded price-input loader: the seam that unstubs the pricing engine.

These tests lock the loader's contract: it reads the in-session-gathered GPL anchors from
config/market_prices/list_prices.yaml, FX-converts USD list -> EUR, and hands the deterministic
engine a grounded PriceInputs per SKU. A SKU absent from the file is NEVER priced (it flags) —
the loader fabricates nothing (the 1000% rule). Pure and offline.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from hexcat.price_inputs import (
    LIST_PRICES_ARTIFACT,
    GroundedListPrice,
    load_price_inputs,
)
from hexcat.pricing import T2, FLAG, PricePolicy

REPO = Path(__file__).resolve().parents[1]
P = PricePolicy()  # neutral defaults (list_to_net 0.55)


# ---- the live grounded artifact loads and is well-formed -------------------------------

def test_artifact_exists_and_loads():
    assert LIST_PRICES_ARTIFACT.is_file(), "config/market_prices/list_prices.yaml must exist"
    book = load_price_inputs()
    assert book.usd_eur > 0, "a positive dated FX rate must be present"
    assert book.fx_as_of, "FX rate must be dated"
    assert book.fx_source, "FX rate must cite a source"
    assert book.entries, "at least one grounded anchor must be present"


def test_every_entry_traces_to_a_source_and_confidence():
    # The 1000% rule made testable: each grounded price carries a real URL and explicit confidence.
    book = load_price_inputs()
    for sku, e in book.entries.items():
        assert e.source.startswith("http"), f"{sku}: grounded price must cite a source URL"
        assert e.confidence in {"high", "medium", "low"}, f"{sku}: explicit confidence required"
        assert e.list_usd > 0, f"{sku}: list_usd must be positive"


def test_fx_conversion_is_applied():
    book = load_price_inputs()
    for sku, e in book.entries.items():
        assert e.list_eur == e.list_usd * book.usd_eur, f"{sku}: list_eur must be list_usd * fx"


# ---- grounded SKUs resolve at T2; absent SKUs flag (never invented) --------------------

def test_grounded_sku_resolves_at_t2():
    book = load_price_inputs()
    sku = next(iter(book.entries))
    res = book.resolve(sku, P)
    assert res.tier == T2, "a grounded list anchor must resolve at T2-LIST"
    assert not res.flagged
    # net = list_eur * list_to_net
    e = book.entries[sku]
    assert res.value == (e.list_eur * P.list_to_net).quantize(Decimal("0.01"))


def test_absent_sku_flags_and_is_not_invented():
    book = load_price_inputs()
    res = book.resolve("THIS-SKU-IS-NOT-GROUNDED-XYZ", P)
    assert res.flagged
    assert res.tier == FLAG
    assert res.value is None


def test_price_inputs_for_absent_sku_carries_no_list_price():
    book = load_price_inputs()
    pi = book.price_inputs("NOPE-404")
    assert pi.list_price is None
    assert pi.market_observations == []


def test_contains_and_get():
    book = load_price_inputs()
    sku = next(iter(book.entries))
    assert sku in book
    assert "definitely-not-here" not in book
    assert isinstance(book.get(sku), GroundedListPrice)
    assert book.get("definitely-not-here") is None


# ---- loader rejects malformed input (fail loud, never silently guess) ------------------

def test_rejects_nonpositive_fx(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("fx:\n  usd_eur: 0\nskus: {}\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_price_inputs(bad)


def test_rejects_entry_without_list_usd(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "fx:\n  usd_eur: 0.86\nskus:\n  FOO:\n    confidence: low\n", encoding="utf-8"
    )
    with pytest.raises(ValueError):
        load_price_inputs(bad)


def test_empty_skus_map_is_valid(tmp_path):
    ok = tmp_path / "empty.yaml"
    ok.write_text("fx:\n  usd_eur: 0.863\n  as_of: '2026-06-11'\n  source: http://x\nskus: {}\n",
                  encoding="utf-8")
    book = load_price_inputs(ok)
    assert book.entries == {}
    assert book.usd_eur == Decimal("0.863")


# ---- the live artifact agrees with what is actually written into the bundle ------------

def test_grounded_anchors_are_written_into_the_cisco_prices_csv():
    import csv
    import io

    book = load_price_inputs()
    prices = REPO / "output" / "stage3_Cisco" / "Hexwaren_Cisco_Transceivers_Prices.csv"
    raw = prices.read_bytes().decode("utf-8")
    assert not raw.startswith("﻿"), "Prices CSV must have NO BOM"
    rows = list(csv.reader(io.StringIO(raw), delimiter=";"))
    header = rows[0]
    ai, vi = header.index("Artikelnummer"), header.index("Netto-VK")
    by_sku = {r[ai]: r[vi] for r in rows[1:] if r}
    for sku, e in book.entries.items():
        if sku in by_sku:  # the Cisco anchors
            res = book.resolve(sku, P)
            assert by_sku[sku] == res.netto_vk, f"{sku}: bundle price must match engine result"
