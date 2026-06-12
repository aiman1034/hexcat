"""§2 G3 — the weight-disposition flag artifact must be well-formed.

`config/weight_disposition.yaml` is the tracked account of every emitted weight: GROUNDED
(operator-supplied) or a flagged PLACEHOLDER derived from weights.yaml by Formfaktor. We lock
its STRUCTURE and internal reconciliation (not whether a weight is grounded yet — that count
rises as a later datasheet/measurement pass grounds them). This makes the placeholder-weight
debt auditable instead of silently passing the build gate.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from hexcat import constants as C

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "config" / "weight_disposition.yaml"

EXPECTED_SKU_COUNT = {
    "Cisco": 297, "Arista": 347, "HPE": 147, "Fortinet": 87, "MikroTik": 24,
}


def _load() -> dict:
    return yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_exists_and_covers_every_brand():
    d = _load()
    assert d.get("policy")
    assert set(d["brands"]) == set(EXPECTED_SKU_COUNT)


def test_totals_reconcile():
    d = _load()
    assert d["total_skus"] == sum(EXPECTED_SKU_COUNT.values())
    assert d["total_skus"] == sum(b["sku_count"] for b in d["brands"].values())
    assert d["total_placeholder"] == sum(b["placeholder"] for b in d["brands"].values())


def test_each_brand_block_is_consistent():
    d = _load()
    for brand, blk in d["brands"].items():
        assert blk["sku_count"] == EXPECTED_SKU_COUNT[brand], brand
        # grounded + placeholder accounts for every SKU
        assert blk["grounded"] + blk["placeholder"] == blk["sku_count"], brand
        by_ff = blk.get("placeholder_by_formfaktor") or {}
        assert sum(by_ff.values()) == blk["placeholder"], brand
        # every form factor flagged is a real physical connector (never a commerce category)
        for ff in by_ff:
            assert ff in C.PHYSICAL_FORMFAKTOR, f"{brand}: non-physical Formfaktor {ff!r}"
