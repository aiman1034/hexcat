"""Lock the price-resolution glue (lib/price_run.py): market observations -> engine T1 median;
feature-model fallback when ungrounded; category-band BLOCK downgrades to honest flagged-debt."""
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
    "category_bands": {"SFP+": {"floor": 8, "ceiling": 2000}, "_default": {"floor": 5, "ceiling": 80000}},
}


def test_market_observations_resolve_to_engine_median():
    out = PR.resolve("SFP-10G-SR", unterkat="SFP+", attrs={"Formfaktor": "SFP+"},
                     net_values=[Decimal("100"), Decimal("120"), Decimal("140")],
                     sources=["bechtle", "senetic", "router-switch"], model=None,
                     policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "T1-MARKET" and out.value == Decimal("120.00")
    assert out.confidence == "high" and out.n_sources == 3
    assert out.netto_vk == "120,00"


def test_single_source_market_is_grounded_but_flagged():
    out = PR.resolve("SFP-10G-LR", unterkat="SFP+", attrs={}, net_values=[Decimal("250")],
                     sources=["bechtle"], model=None, policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "T1-MARKET" and out.value == Decimal("250.00")
    assert out.confidence == "low" and any("single-source" in f for f in out.flags)


def test_feature_model_fallback_when_no_observations():
    anchors = [(Features("SFP+", 10, "SR", "MM"), Decimal("100")),
               (Features("SFP+", 10, "SR", "MM"), Decimal("120"))]
    model = PriceModel(anchors, min_members=2)
    out = PR.resolve("SFP-10G-SR-NEW", unterkat="SFP+",
                     attrs={"Formfaktor": "SFP+", "Geschwindigkeit": "10 Gbit/s",
                            "Reichweite": "300 m", "Fasertyp": "Multimode", "Transceiver Typ": "SR"},
                     net_values=[], sources=[], model=model, policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "MODEL" and out.value == Decimal("110.00")
    assert any("modeled" in f for f in out.flags)


def test_band_block_downgrades_to_flag():
    # an absurd €4 result for an SFP+ is below the €8 floor -> blocked -> no price shipped
    out = PR.resolve("SFP-WEIRD", unterkat="SFP+", attrs={}, net_values=[Decimal("4")],
                     sources=["bechtle"], model=None, policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "FLAG" and out.value is None and not out.shipped
    assert out.netto_vk == "0,00"


def test_ungrounded_is_flagged_debt():
    out = PR.resolve("MYSTERY", unterkat="SFP+", attrs={}, net_values=[], sources=[],
                     model=None, policy_doc=POLICY_DOC, fx=FX)
    assert out.tier == "FLAG" and out.value is None
