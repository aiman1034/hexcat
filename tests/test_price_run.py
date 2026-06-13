"""Lock the tiered price-resolution glue (lib/price_run.py):
authorized > secondary > family(authorized) > family(secondary) > T2-LIST > MODEL > FLAG,
with secondary/family/modeled tags, band-BLOCK -> honest flagged-debt."""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import price_run as PR  # noqa: E402
from lib.price_model import Features, PriceModel  # noqa: E402

FX = Decimal("0.863")
POLICY_DOC = {
    "policy": {"high_value_eur": 1500, "max_spread": 0.6},
    "market": {"min_sources": 1},
    "category_bands": {"SFP+": {"floor": 8, "ceiling": 2000}, "GBIC": {"floor": 10, "ceiling": 2500},
                       "_default": {"floor": 5, "ceiling": 80000}},
}


def _d(tier, *vals):
    return [(tier, Decimal(str(v))) for v in vals]


def test_authorized_direct_wins_and_is_high_conf():
    out = PR.resolve("SFP-10G-SR", unterkat="SFP+", attrs={},
                     direct=_d("authorized", 100, 120, 140), sources=["bechtle", "senetic", "jacob"],
                     policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "T1-MARKET" and out.value == Decimal("120.00") and out.confidence == "high"
    assert not any("secondary" in f for f in out.flags)


def test_secondary_used_when_no_authorized_and_flagged():
    out = PR.resolve("XENPAK-10GB-LR", unterkat="SFP+", attrs={},
                     direct=_d("secondary", 380, 420), sources=["router-switch", "ebay"],
                     policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "T1-MARKET" and out.value == Decimal("400.00")
    assert any("secondary-anchored" in f for f in out.flags)
    assert out.confidence == "medium"


def test_family_anchor_prices_a_channel_variant_with_no_direct_obs():
    # DWDM-GBIC-30.33 has no direct listing, but its DWDM-GBIC family siblings do
    out = PR.resolve("DWDM-GBIC-30.33", unterkat="GBIC", attrs={}, direct=[],
                     family=_d("secondary", 300, 340, 320), sources=[],
                     policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "FAMILY" and out.value == Decimal("320.00")
    assert any("family-anchored" in f for f in out.flags)


def test_authorized_family_beats_secondary_family():
    out = PR.resolve("DWDM-GBIC-31.12", unterkat="GBIC", attrs={}, direct=[],
                     family=_d("authorized", 500, 520) + _d("secondary", 100), sources=[],
                     policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "FAMILY" and out.value == Decimal("510.00")   # authorized family pool used


def test_list_then_model_then_flag_fallback():
    # no market at all -> T2 list
    out = PR.resolve("X", unterkat="SFP+", attrs={}, direct=[], family=[],
                     list_eur=Decimal("400"), policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "T2-LIST" and out.value is not None
    # nothing anywhere -> flagged debt
    out2 = PR.resolve("Y", unterkat="SFP+", attrs={}, direct=[], family=[],
                      policy_doc=POLICY_DOC, fx=FX)
    assert out2.tier == "FLAG" and out2.value is None


def test_band_block_downgrades_to_flag():
    out = PR.resolve("SFP-WEIRD", unterkat="SFP+", attrs={}, direct=_d("secondary", 4),
                     sources=["x"], policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "FLAG" and out.value is None and out.netto_vk == "0,00"


def test_family_band_override_admits_premium_channel_optic():
    # a DWDM-XFP channel priced at €8000 must pass (family band ceiling 12000), though its generic
    # "XFP" category band (ceiling 4000) would have blocked it
    pol = dict(POLICY_DOC)
    pol = {**POLICY_DOC, "category_bands": {**POLICY_DOC["category_bands"], "XFP": {"floor": 20, "ceiling": 4000}},
           "family_bands": {"DWDM-XFP": {"floor": 150, "ceiling": 12000}}}
    out = PR.resolve("DWDM-XFP-30.33", unterkat="XFP", attrs={}, direct=_d("secondary", 8000),
                     sources=["x"], policy_doc=pol, fx=FX)
    assert out.value == Decimal("8000.00") and out.tier == "T1-MARKET"
    assert not any(f.startswith("BLOCK") for f in out.flags)
