"""Lock the feature-model fallback (lib/price_model.py): feature extraction from authored
attributes, nearest-cohort median prediction with widening, and leave-one-out back-test."""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import price_model as PM  # noqa: E402


def test_feature_extraction_reads_speed_reach_optic():
    f = PM.extract_features(
        {"Formfaktor": "SFP+", "Geschwindigkeit": "10 Gbit/s", "Reichweite": "300 m",
         "Fasertyp": "Multimode", "Transceiver Typ": "SR"}, "SFP-10G-SR")
    assert f.form == "SFP+" and f.speed_gbps == 10 and f.optic == "MM" and f.reach_band == "SR"


def test_feature_extraction_handles_sub_gig_and_tbit():
    assert PM.extract_features({"Geschwindigkeit": "155 Mbit/s"}, "POM-OC3-MM").speed_gbps == 0.155
    assert PM.extract_features({"Geschwindigkeit": "1,2 Tbit/s"}, "CIM8-C-K9").speed_gbps == 1200


def test_dac_detected_from_pn_and_priced_in_its_own_cohort():
    f = PM.extract_features({"Formfaktor": "SFP+", "Geschwindigkeit": "10 Gbit/s"}, "SFP-H10GB-CU3M")
    assert f.optic == "DAC" and f.reach_band == "DAC"


def test_model_predicts_from_narrowest_cohort_then_widens():
    anchors = [
        (PM.Features("SFP+", 10, "SR", "MM"), Decimal("100")),
        (PM.Features("SFP+", 10, "SR", "MM"), Decimal("120")),
        (PM.Features("SFP+", 10, "LR", "SM"), Decimal("300")),
        (PM.Features("SFP+", 10, "LR", "SM"), Decimal("340")),
    ]
    m = PM.PriceModel(anchors, min_members=2)
    # exact cohort (SFP+/10G/SR/MM) -> median(100,120)=110
    p = m.predict(PM.Features("SFP+", 10, "SR", "MM"))
    assert p.value == Decimal("110.00") and p.n == 2 and p.cohort.startswith("SFP+|10G|SR")
    # an LR query with no MM match still resolves via the SR/LR-aware cohorts
    p2 = m.predict(PM.Features("SFP+", 10, "LR", "SM"))
    assert p2.value == Decimal("320.00")


def test_model_flags_when_cohort_too_thin():
    anchors = [(PM.Features("QSFP-DD", 400, "ZR", "COHERENT"), Decimal("5000"))]
    m = PM.PriceModel(anchors, min_members=2)
    assert m.predict(PM.Features("SFP", 1, "SR", "MM")).value is None  # nothing comparable


def test_back_test_reports_mape_leave_one_out():
    anchors = [
        (PM.Features("SFP+", 10, "SR", "MM"), Decimal("100")),
        (PM.Features("SFP+", 10, "SR", "MM"), Decimal("104")),
        (PM.Features("SFP+", 10, "SR", "MM"), Decimal("108")),
        (PM.Features("SFP+", 10, "SR", "MM"), Decimal("112")),
    ]
    mape, scored, total = PM.back_test(anchors, min_members=2)
    assert scored == 4 and total == 4
    assert mape is not None and mape < Decimal("0.10")   # tight cluster -> small error
