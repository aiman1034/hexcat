"""§2 G2 — the residual-GAP flag artifact must be well-formed.

`config/attribute_gaps/residual_gaps.yaml` is the project's tracked account of every slot a
SKU is EXPECTED to carry but extraction hasn't filled and no deriver can ground — the exact
scope of the DEFERRED grounded datasheet pass. We lock its STRUCTURE (brands, sku totals,
that every flagged attribute is one of the locked 14, internal sum consistency), not the
individual counts (those legitimately shrink as the grounded pass closes gaps).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from hexcat import constants as C

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "config" / "attribute_gaps" / "residual_gaps.yaml"

EXPECTED_SKU_COUNT = {
    "Cisco": 297, "Arista": 347, "HPE": 147, "Fortinet": 87, "MikroTik": 24,
}


def test_artifact_exists_and_covers_every_brand():
    d = yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))
    assert d.get("policy")
    assert set(d["brands"]) == set(EXPECTED_SKU_COUNT)


def test_each_brand_block_is_consistent():
    d = yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))
    for brand, blk in d["brands"].items():
        assert blk["sku_count"] == EXPECTED_SKU_COUNT[brand], brand
        gaps = blk["gaps"] or {}
        # every flagged slot is one of the locked 14, with a positive count
        for name, cnt in gaps.items():
            assert name in C.ATTRIBUTE_NAMES_ORDERED, f"{brand}: unknown attribute {name!r}"
            assert isinstance(cnt, int) and cnt > 0, f"{brand}/{name}={cnt}"
        # declared total reconciles with the per-attribute counts
        assert blk["total_gaps"] == sum(gaps.values()), brand
