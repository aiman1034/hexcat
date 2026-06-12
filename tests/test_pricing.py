"""§5 — the deterministic pricing engine: tiers, guards, back-test, and the debt artifact."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import yaml

from hexcat.pricing import (
    FLAG,
    T1,
    T2,
    T3,
    BackTestSample,
    PriceInputs,
    PricePolicy,
    back_test,
    fetch_market_observations,
    from_eur,
    resolve_price,
    to_eur,
)

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "config" / "price_disposition.yaml"
EXPECTED_SKU_COUNT = {"Cisco": 297, "Arista": 347, "HPE": 147, "Fortinet": 87, "MikroTik": 24}

P = PricePolicy()  # neutral defaults


# ---- formatting -----------------------------------------------------------------------

def test_to_eur_german_decimal_two_places():
    assert to_eur(Decimal("120.5")) == "120,50"
    assert to_eur(Decimal("1350")) == "1350,00"
    assert to_eur(Decimal("0.005")) == "0,01"  # half-up


def test_from_eur_parses_and_strips_thousands():
    assert from_eur("120,50") == Decimal("120.50")
    assert from_eur("1.234,00") == Decimal("1234.00")
    assert from_eur("nope") is None


# ---- the stub -------------------------------------------------------------------------

def test_market_ingestion_is_stubbed_zero_dollar():
    assert fetch_market_observations("SFP-10G-SR") == []


# ---- tier selection -------------------------------------------------------------------

def test_t1_market_wins_when_present():
    r = resolve_price(PriceInputs("x", market_observations=[Decimal("90"), Decimal("110")],
                                  list_price=Decimal("1000"), cost=Decimal("50")), P)
    assert r.tier == T1 and r.value == Decimal("100.00")  # median of 90/110


def test_t2_list_used_when_no_market():
    r = resolve_price(PriceInputs("x", list_price=Decimal("100")), P)
    assert r.tier == T2 and r.value == Decimal("55.00")  # 100 * 0.55


def test_t3_cost_used_when_only_cost():
    r = resolve_price(PriceInputs("x", cost=Decimal("100")), P)
    assert r.tier == T3 and r.value == Decimal("135.00")  # 100 * 1.35


def test_no_input_flags_no_price():
    r = resolve_price(PriceInputs("x"), P)
    assert r.flagged and r.tier == FLAG and r.value is None and r.netto_vk == ""


# ---- guards ---------------------------------------------------------------------------

def test_margin_below_floor_blocks_to_flag():
    # market 105 vs cost 100 -> ~4.8% margin, below the 10% floor -> guarded out.
    r = resolve_price(PriceInputs("x", market_observations=[Decimal("105")], cost=Decimal("100")), P)
    assert r.flagged and any(g.startswith("BLOCK:") for g in r.guards)


def test_margin_within_band_is_grounded():
    r = resolve_price(PriceInputs("x", cost=Decimal("100")), P)  # T3 135 -> 25.9% margin
    assert not r.flagged and r.tier == T3


def test_cross_tier_disagreement_warns_but_keeps_price():
    # market 200 vs list 100 (T2=55): chosen T1, but T2 deviates >25% -> WARN, still priced.
    r = resolve_price(PriceInputs("x", market_observations=[Decimal("200")],
                                  list_price=Decimal("100")), P)
    assert not r.flagged and r.tier == T1
    assert any(g.startswith("WARN:") for g in r.guards)


# ---- back-test ------------------------------------------------------------------------

def test_back_test_passes_when_model_tracks_truth():
    samples = [
        BackTestSample(PriceInputs("a", cost=Decimal("100")), true_price=Decimal("135")),  # ape 0
        BackTestSample(PriceInputs("b", cost=Decimal("200")), true_price=Decimal("250")),  # ape .08
    ]
    rep = back_test(samples, P)
    assert rep.n == 2 and rep.n_scored == 2
    assert rep.passed and rep.mape is not None and rep.mape <= P.backtest_max_mape


def test_back_test_fails_when_model_is_off():
    tight = PricePolicy(backtest_max_mape=Decimal("0.01"))
    samples = [BackTestSample(PriceInputs("a", cost=Decimal("100")), true_price=Decimal("200"))]
    rep = back_test(samples, tight)
    assert not rep.passed


def test_back_test_no_scorable_samples_does_not_pass():
    samples = [BackTestSample(PriceInputs("a"), true_price=Decimal("100"))]  # no grounded input
    rep = back_test(samples, P)
    assert rep.n_scored == 0 and not rep.passed and rep.mape is None


# ---- policy load ----------------------------------------------------------------------

def test_policy_loads_from_tracked_config():
    pol = PricePolicy.load()
    assert pol.list_to_net == Decimal("0.55")
    assert pol.cost_markup == Decimal("0.35")
    assert pol.backtest_max_mape == Decimal("0.20")


# ---- the tracked debt artifact --------------------------------------------------------

def _load() -> dict:
    return yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_covers_every_brand_and_reconciles():
    d = _load()
    assert d["total_skus"] == sum(EXPECTED_SKU_COUNT.values())
    assert set(d["brands"]) == set(EXPECTED_SKU_COUNT)
    sum_flagged = sum_grounded = 0
    for brand, blk in d["brands"].items():
        assert blk["sku_count"] == EXPECTED_SKU_COUNT[brand], brand
        grounded = blk["grounded_T1"] + blk["grounded_T2"] + blk["grounded_T3"]
        assert grounded + blk["flagged"] == blk["sku_count"], brand
        sum_flagged += blk["flagged"]
        sum_grounded += grounded
    assert d["total_flagged"] == sum_flagged
    assert d["total_grounded"] == sum_grounded
    assert d["total_grounded"] + d["total_flagged"] == d["total_skus"]
