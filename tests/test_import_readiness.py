"""§2 G7 — the import-readiness validator (catalog-level GO / NO-GO).

Two halves:
  1. Unit tests on the pure verdict logic + the artifact-reading checks (synthetic inputs).
  2. An integration test that runs `assess_readiness` over a REAL assembled bundle (the
     conftest `good_bundle`) and asserts the honest verdict: STRUCTURE GO, PRICES BLOCK
     (the shipped catalog is at the 0,00 placeholder), overall NO-GO.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from hexcat import import_readiness as IR
from hexcat.import_readiness import (
    BLOCK,
    GO,
    WARN,
    Check,
    ReadinessReport,
    _check_attribute_gaps,
    _check_weights,
    _unpriced,
    assess_readiness,
)


# ---- verdict logic --------------------------------------------------------------------

def test_go_only_when_zero_blockers():
    r = ReadinessReport(checks=[Check("A", GO, ""), Check("B", WARN, "")])
    assert r.go and r.verdict == "GO"
    assert r.warnings and not r.blockers


def test_any_block_makes_no_go():
    r = ReadinessReport(checks=[Check("A", GO, ""), Check("B", BLOCK, "x"), Check("C", WARN, "")])
    assert not r.go and r.verdict == "NO-GO"
    assert [c.name for c in r.blockers] == ["B"]
    assert [c.name for c in r.warnings] == ["C"]


def test_unpriced_detects_placeholder_and_zero():
    assert _unpriced("0,00") is True
    assert _unpriced("0") is True
    assert _unpriced("") is True
    assert _unpriced("n/a") is True
    assert _unpriced("120,50") is False
    assert _unpriced("1.234,00") is False  # thousands sep stripped -> 1234.0


# ---- artifact-reading checks (synthetic artifacts) ------------------------------------

def test_weights_warn_when_placeholders_remain(tmp_path):
    p = tmp_path / "w.yaml"
    p.write_text(yaml.safe_dump({"total_skus": 100, "total_placeholder": 40}), encoding="utf-8")
    c = _check_weights(p)
    assert c.status == WARN and "40/100" in c.detail


def test_weights_go_when_all_grounded(tmp_path):
    p = tmp_path / "w.yaml"
    p.write_text(yaml.safe_dump({"total_skus": 100, "total_placeholder": 0}), encoding="utf-8")
    assert _check_weights(p).status == GO


def test_attribute_gaps_sum_across_brands(tmp_path):
    p = tmp_path / "g.yaml"
    p.write_text(yaml.safe_dump(
        {"brands": {"Cisco": {"total_gaps": 3}, "Arista": {"total_gaps": 5}}}), encoding="utf-8")
    c = _check_attribute_gaps(p)
    assert c.status == WARN and "8 residual" in c.detail


def test_attribute_gaps_go_when_zero(tmp_path):
    p = tmp_path / "g.yaml"
    p.write_text(yaml.safe_dump({"brands": {"Cisco": {"total_gaps": 0}}}), encoding="utf-8")
    assert _check_attribute_gaps(p).status == GO


# ---- integration over a REAL assembled bundle -----------------------------------------

def _clean_artifacts(tmp_path):
    """Synthetic all-grounded deferred-debt artifacts, so only data-derived checks drive."""
    wp = tmp_path / "w.yaml"
    wp.write_text(yaml.safe_dump({"total_skus": 2, "total_placeholder": 0}), encoding="utf-8")
    gp = tmp_path / "g.yaml"
    gp.write_text(yaml.safe_dump({"brands": {"Cisco": {"total_gaps": 0}}}), encoding="utf-8")
    return wp, gp


def test_real_priced_bundle_is_go(good_bundle, rules, tmp_path):
    # The reference example ships REAL prices, so a single clean brand with grounded
    # deferred-debt artifacts is import-ready (GTIN deferral is a WARN, not a blocker).
    d, _ = good_bundle
    wp, gp = _clean_artifacts(tmp_path)
    report = assess_readiness({"Cisco": d}, rules, weight_artifact=wp, gaps_artifact=gp)
    by_name = {c.name: c for c in report.checks}
    assert by_name["STRUCTURE"].status == GO, by_name["STRUCTURE"].detail
    assert by_name["CROSS-BRAND"].status == GO   # single brand cannot collide
    assert by_name["PRICES"].status == GO         # example carries grounded Netto-VK
    assert by_name["WEIGHTS"].status == GO
    assert by_name["ATTR-GAPS"].status == GO
    assert report.go and report.verdict == "GO"
    assert report.n_skus == 2


def test_placeholder_prices_block_the_import(good_bundle, rules, tmp_path):
    # Knock every Netto-VK back to the 0,00 placeholder -> PRICES BLOCK -> NO-GO.
    d, _ = good_bundle
    wp, gp = _clean_artifacts(tmp_path)
    prices = next(Path(d).glob("Hexwaren_*_Prices.csv"))
    raw = prices.read_bytes().decode("utf-8")
    lines = raw.split("\r\n")
    out = [lines[0]]  # header
    for ln in lines[1:]:
        if ";" in ln:
            sku = ln.split(";", 1)[0]
            out.append(f"{sku};0,00")
        else:
            out.append(ln)
    prices.write_bytes("\r\n".join(out).encode("utf-8"))

    report = assess_readiness({"Cisco": d}, rules, weight_artifact=wp, gaps_artifact=gp)
    by_name = {c.name: c for c in report.checks}
    assert by_name["PRICES"].status == BLOCK
    assert "placeholder" in by_name["PRICES"].detail
    assert not report.go and report.verdict == "NO-GO"


def test_default_artifacts_are_readable():
    # The real tracked artifacts must parse and yield a definite (non-crashing) check.
    assert _check_weights(IR.WEIGHT_ARTIFACT).status in {GO, WARN, BLOCK}
    assert _check_attribute_gaps(IR.GAPS_ARTIFACT).status in {GO, WARN, BLOCK}
