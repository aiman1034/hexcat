"""Phase 3 Stage-1 ledger engine tests — deterministic, no network.

Covers: ledger spec + locked-22 drift guard, HTML mining (ordering-table targeting +
dedup + token filter), §6 PN normalization acceptance, fetch tier fallback (mocked),
classification buckets, workbook structure, and the §7 skeleton export.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from hexcat.ledger import (
    export_skeleton,
    fetch_datasheet,
    load_ledger_spec,
    normalize_pn,
    run_source,
    verify_ledger_spec,
    write_workbook,
)
from hexcat.ledger import fetch as fetch_mod
from hexcat.ledger.engine import Source
from hexcat.ledger.mine import MinedPN, mine_html
from hexcat.models import INTAKE_COLUMNS

SPEC = load_ledger_spec()

# A tiny datasheet stand-in: a decoy spec table + the ordering table (Description |
# Product Number), with a duplicate row and a junk cell to exercise dedup + token filter.
FIXTURE_HTML = """
<html><body>
<table>
  <tr><th>Parameter</th><th>Symbol</th></tr>
  <tr><td>Wavelength</td><td>850 nm</td></tr>
</table>
<table>
  <tr><th>Description</th><th>Product Number</th></tr>
  <tr><td>10GBASE-SR SFP+ Module for MMF</td><td>SFP-10G-SR</td></tr>
  <tr><td>10GBASE-LR SFP+ Module for SMF</td><td>SFP-10G-LR</td></tr>
  <tr><td>dup row (same PN)</td><td>SFP-10G-SR</td></tr>
  <tr><td>10GBASE-CU SFP+ Cable 3 Meter, passive</td><td>SFP-H10GB-CU3M</td></tr>
  <tr><td>10GBASE-AOC SFP+ Cable 3 Meter</td><td>SFP-10G-AOC3M</td></tr>
  <tr><td>not a part number</td><td>See note 1</td></tr>
</table>
</body></html>
"""


# --- spec + locked-22 drift guard ------------------------------------------------
def test_verify_ledger_spec_passes():
    spec = verify_ledger_spec()
    assert spec.brand == "Cisco"
    assert spec.hauptkategorie == "Transceivers"


def test_classify_buckets():
    assert SPEC.classify_pn("SFP-10G-SR") == "SFP+ (10G)"
    assert SPEC.classify_pn("SFP-10G-T-X") == "SFP+ (10G)"     # 10GBASE-T module, NOT a cable
    assert SPEC.classify_pn("SFP-H10GB-CU3M") == "DAC Kabel"
    assert SPEC.classify_pn("SFP-H10GB-ACU7M") == "DAC Kabel"  # active copper -> DAC
    assert SPEC.classify_pn("SFP-10G-AOC3M") == "AOC Kabel"


def test_locked22_mapping():
    assert SPEC.to_locked22("SFP+ (10G)") == "SFP+"
    assert SPEC.to_locked22("DAC Kabel") == "DAC Kabel"
    assert SPEC.to_locked22("AOC Kabel") == "AOC Kabel"
    assert SPEC.to_locked22("XFP") == "XFP"  # identity for unlisted


# --- mining ----------------------------------------------------------------------
def test_mine_html_targets_ordering_table_and_dedups():
    mined = mine_html(FIXTURE_HTML, SPEC)
    pns = [m.pn for m in mined]
    assert pns == ["SFP-10G-SR", "SFP-10G-LR", "SFP-H10GB-CU3M", "SFP-10G-AOC3M"]
    assert "See note 1" not in pns          # token filter drops prose
    assert pns.count("SFP-10G-SR") == 1      # dedup against itself
    assert mined[0].description.startswith("10GBASE-SR")


# --- §6 normalization acceptance (grounded in the operator's own PN-Korrekturen) --
CANONICAL = {"SFP-10G-SR", "SFP-10G-T-X", "SFP-10G-LR"}


def test_norm_feed_id_suffix_stripped():
    r = normalize_pn("SFP-10G-SR-P-4683", CANONICAL, SPEC)
    assert r.canonical == "SFP-10G-SR"
    assert r.confirmed and r.is_correction
    assert r.problem == "Feed-ID-Anhang -P-####"


def test_norm_spelling_missing_hyphen():
    r = normalize_pn("SFP-10G-TX", CANONICAL, SPEC)
    assert r.canonical == "SFP-10G-T-X"
    assert r.confirmed and r.is_correction
    assert r.problem == "Schreibweise (fehlender Bindestrich)"


def test_norm_already_clean_no_correction():
    r = normalize_pn("SFP-10G-SR", CANONICAL, SPEC)
    assert r.canonical == "SFP-10G-SR"
    assert not r.is_correction and r.confirmed


def test_norm_unconfirmed_is_flagged_not_forced():
    # Stripping yields a form NOT in the datasheet set -> changed but unconfirmed.
    r = normalize_pn("SFP-10G-BOGUS-P-99", CANONICAL, SPEC)
    assert r.is_correction          # the suffix was stripped
    assert not r.confirmed          # but the result isn't datasheet-confirmed -> flag


# --- fetch tier fallback (mocked; no network) ------------------------------------
def test_fetch_tier1_success_writes_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_mod, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(fetch_mod, "MANUAL_DIR", tmp_path / "manual")

    def fake_get(url):
        return 200, b"<html>ok</html>", "text/html;charset=utf-8"

    res = fetch_datasheet("https://x/data_sheet_c78-455693.html", http_get=fake_get)
    assert res.tier == "tier1-httpx" and res.content_type == "html"
    assert res.path.exists() and res.read_text() == "<html>ok</html>"

    # Second call hits the cache (no getter needed).
    res2 = fetch_datasheet("https://x/data_sheet_c78-455693.html",
                           http_get=lambda u: (_ for _ in ()).throw(AssertionError("should not fetch")))
    assert res2.tier == "cache"


def test_fetch_falls_back_to_manual_dropin(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_mod, "CACHE_DIR", tmp_path / "cache")
    manual_dir = tmp_path / "manual"
    manual_dir.mkdir()
    monkeypatch.setattr(fetch_mod, "MANUAL_DIR", manual_dir)
    (manual_dir / "c78-999999.html").write_text("<html>manual</html>", encoding="utf-8")

    def boom(url):
        raise RuntimeError("blocked 403")

    res = fetch_datasheet("https://x/data_sheet_c78-999999.html", http_get=boom)
    assert res.tier == "tier3-manual"
    assert res.read_text() == "<html>manual</html>"


def test_fetch_raises_when_all_tiers_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_mod, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(fetch_mod, "MANUAL_DIR", tmp_path / "manual")
    with pytest.raises(fetch_mod.FetchError):
        fetch_datasheet("https://x/data_sheet_c78-000000.html",
                        http_get=lambda u: (500, b"", "text/html"))


# --- engine + workbook + export end-to-end (on the fixture) ----------------------
def _fixture_result():
    src = Source(gruppe="10G", datasheet="Cisco 10GBASE SFP+ Modules",
                 url="https://x/data_sheet_c78-455693.html")
    fetched = type("F", (), {"tier": "fixture", "content_type": "html",
                             "read_text": lambda self: FIXTURE_HTML})()
    return run_source(src, SPEC, verified_date="2026-06-12", fetched=fetched)


def test_run_source_classifies_and_counts():
    res = _fixture_result()
    assert res.mined_count == 4
    assert res.coverage() == {"SFP+ (10G)": 2, "DAC Kabel": 1, "AOC Kabel": 1}
    assert res.new_count is None  # no live list


def test_run_source_with_live_list_tags_and_corrects():
    src = Source(gruppe="10G", datasheet="Cisco 10GBASE SFP+ Modules",
                 url="https://x/data_sheet_c78-455693.html")
    fetched = type("F", (), {"tier": "fixture", "content_type": "html",
                             "read_text": lambda self: FIXTURE_HTML})()
    # live feed: one messy (feed-id) existing PN + one clean existing PN.
    res = run_source(src, SPEC, verified_date="2026-06-12",
                     live_pns=["SFP-10G-SR-P-4683", "SFP-10G-LR"], fetched=fetched)
    assert res.new_count == 2  # CU3M + AOC3M are new; SR + LR already live
    corr = {c.raw: c for c in res.corrections}
    assert "SFP-10G-SR-P-4683" in corr
    assert corr["SFP-10G-SR-P-4683"].canonical == "SFP-10G-SR"
    assert corr["SFP-10G-SR-P-4683"].tab == "SFP+ (10G)"
    assert "C78-455693" in corr["SFP-10G-SR-P-4683"].confirmed_via


def test_workbook_structure(tmp_path):
    import openpyxl

    res = _fixture_result()
    out = write_workbook([res], tmp_path / "ledger.xlsx", run_date="2026-06-12")
    wb = openpyxl.load_workbook(out)
    assert wb.sheetnames == [
        "Fortschritt", "Neue Artikel", "Quellen-Tracker",
        "PN-Korrekturen (Feed-ID)", "Familien-Audit",
    ]
    neue = wb["Neue Artikel"]
    assert [c.value for c in neue[1]] == [
        "Artikelnummer (Part Number)", "Hauptkategorie", "Unterkategorie",
        "Quelle (Cisco Datasheet)", "Quell-URL", "Verifiziert am", "Notiz",
    ]
    assert neue.max_row == 1 + 4  # header + 4 mined PNs


def test_export_skeleton_maps_to_locked22(tmp_path):
    import csv

    res = _fixture_result()
    out = export_skeleton([res], tmp_path / "skeleton.csv", SPEC)
    with out.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert list(rows[0].keys()) == list(INTAKE_COLUMNS)
    by_pn = {r["Artikelnummer"]: r for r in rows}
    assert by_pn["SFP-10G-SR"]["KategorieEbene3"] == "SFP+"        # mapped from "SFP+ (10G)"
    assert by_pn["SFP-H10GB-CU3M"]["KategorieEbene3"] == "DAC Kabel"
    assert by_pn["SFP-10G-SR"]["Vendor"] == "Cisco"
    assert by_pn["SFP-10G-SR"]["Kurzbeschreibung"] == ""           # specs/prose stay blank
    assert by_pn["SFP-10G-SR"]["SourceURLs"].endswith("c78-455693.html")


# --- optional integration: real cached datasheet, if present ---------------------
def test_real_datasheet_yields_35_if_cached():
    cached = Path(__file__).resolve().parents[1] / "datasheets" / "cache" / "c78-455693.html"
    if not cached.exists():
        pytest.skip("cached datasheet not present (network/cache-dependent)")
    mined = mine_html(cached.read_text(encoding="utf-8"), SPEC)
    pns = {m.pn for m in mined}
    assert len(mined) == 35
    for expected in ["SFP-10G-SR", "SFP-10G-LR", "SFP-10G-ER", "SFP-10G-LRM",
                     "SFP-10G-ZR", "SFP-10G-T-X", "SFP-H10GB-CU3M", "SFP-10G-AOC3M"]:
        assert expected in pns
