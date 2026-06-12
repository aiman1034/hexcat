"""§2 G1 — source-disposition manifests must be well-formed and reconcile.

`config/source_disposition/<brand>.yaml` is the project's account of every datasheet it
considered: MINED (with per-source SKU count) or dropped (NON_TRANSCEIVER / SUPERSEDED /
FAILED, each with a reason). These tests prove the manifests are internally consistent and,
for Cisco, that the MINED set equals the curated SEED workbook EXACTLY — a tracked-to-tracked
reconciliation that needs no build output. This is what makes source coverage auditable
rather than asserted.
"""
from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
DISP_DIR = REPO / "config" / "source_disposition"
SEED_XLSX = REPO / "Cisco_Transceivers_SEED.xlsx"

ALLOWED_DISPOSITION = {"MINED", "NON_TRANSCEIVER", "SUPERSEDED", "FAILED", "EMPTY_NO_NEW"}
ALLOWED_STATUS = {"GROUNDED_COMPLETE", "FLAGGED_INCOMPLETE"}

# Locked per-brand SKU totals (regression guard — these are the shipped catalog counts).
EXPECTED_SKU_COUNT = {
    "Cisco": 297,
    "Arista": 347,
    "HPE": 147,
    "Fortinet": 87,
    "MikroTik": 24,
}


def _load(name: str) -> dict:
    return yaml.safe_load((DISP_DIR / f"{name}.yaml").read_text(encoding="utf-8"))


def _manifest_files():
    return sorted(DISP_DIR.glob("*.yaml"))


def test_one_manifest_per_brand():
    names = {p.stem for p in _manifest_files()}
    assert names == {b.lower() for b in EXPECTED_SKU_COUNT}, names


@pytest.mark.parametrize("brand", sorted(EXPECTED_SKU_COUNT), ids=sorted(EXPECTED_SKU_COUNT))
def test_manifest_well_formed_and_reconciles(brand):
    d = _load(brand.lower())
    assert d["brand"] == brand
    assert d["enumeration_status"] in ALLOWED_STATUS

    mined, other = [], []
    for s in d["sources"]:
        assert s["disposition"] in ALLOWED_DISPOSITION, s
        assert s.get("title"), f"every source needs a title: {s}"
        if s["disposition"] == "MINED":
            assert s.get("url"), f"MINED source must carry its grounding URL: {s}"
            assert isinstance(s.get("sku_count"), int) and s["sku_count"] > 0, s
            mined.append(s)
        else:
            # A drop must justify itself (flag-don't-emit: never an unexplained omission).
            assert s.get("reason"), f"non-MINED source must give a reason: {s}"
            other.append(s)

    # Internal reconciliation: declared totals == the MINED rows.
    assert len(mined) == d["mined_source_count"]
    assert sum(s["sku_count"] for s in mined) == d["mined_sku_count"]
    # The shipped catalog count is locked.
    assert d["mined_sku_count"] == EXPECTED_SKU_COUNT[brand]

    # MINED URLs are unique (no source double-counted).
    urls = [s["url"] for s in mined]
    assert len(urls) == len(set(urls)), "duplicate MINED source URL"

    # GROUNDED_COMPLETE means a single exhaustive datasheet, no unresolved residual.
    if d["enumeration_status"] == "GROUNDED_COMPLETE":
        assert len(mined) == 1 and not other


def test_cisco_mined_set_equals_curated_seed():
    """Tracked-to-tracked: the 29 MINED Cisco URLs must equal the curated SEED workbook."""
    d = _load("cisco")
    mined_urls = {s["url"] for s in d["sources"] if s["disposition"] == "MINED"}

    wb = openpyxl.load_workbook(SEED_XLSX, read_only=True)
    ws = wb["Quellen-Tracker"]
    seed_urls = set()
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        _g, ds, url = (list(row) + [None] * 3)[:3]
        if ds and url:
            seed_urls.add(str(url).strip())

    assert mined_urls == seed_urls, (
        f"Cisco MINED set drifted from the SEED.\n"
        f"  only in manifest: {sorted(mined_urls - seed_urls)}\n"
        f"  only in SEED:     {sorted(seed_urls - mined_urls)}"
    )
