"""Lock the Cisco transceiver coverage closure (the proof that the universal harvester
reached the manufacturer's full published set and every surfaced PN was accounted for).

These assert the *disposition* artifact — config/coverage/cisco_transceivers_disposition.yaml,
the deterministic triage of the 120 PNs Cisco publishes that the shipped 297-SKU catalog
lacks — stays internally consistent and grounded in the real config (the locked-22 taxonomy
and the Cisco ledger's curated coverage.expected_families).

The decisive regression here is the XENPAK/GBIC-vs-POM distinction: an earlier triage wrongly
dropped XENPAK and GBIC as "not in the locked-22 taxonomy" when both ARE locked-22 form
factors — they are merely outside the *curated Cisco scope*. POM, by contrast, genuinely is
not a locked-22 token. test_legacy_form_factors_bucketed_correctly pins that down so the
contradiction can never silently come back.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DISP = ROOT / "config" / "coverage" / "cisco_transceivers_disposition.yaml"
COV = ROOT / "config" / "coverage" / "cisco_transceivers_coverage.yaml"
TAX = ROOT / "config" / "taxonomy" / "transceivers.yaml"
LEDGER = ROOT / "config" / "ledger" / "cisco_transceivers.yaml"
CONTENT = ROOT / "stage3_content" / "Cisco_content.json"

_BUCKET_KEYS = ("add", "review", "exclude_scope", "exclude_taxonomy", "exclude_not_transceiver")


def _disp() -> dict:
    return yaml.safe_load(DISP.read_text(encoding="utf-8"))


def _locked22() -> set[str]:
    return set(yaml.safe_load(TAX.read_text(encoding="utf-8"))["subcategories"])


def _expected() -> set[str]:
    return set(yaml.safe_load(LEDGER.read_text(encoding="utf-8"))["coverage"]["expected_families"])


def _all_entries(d: dict) -> list[dict]:
    return [e for k in _BUCKET_KEYS for e in (d.get(k) or [])]


# ---- accounting: nothing silently dropped, nothing double-counted ---------------------

def test_every_surfaced_pn_accounted_exactly_once():
    d = _disp()
    entries = _all_entries(d)
    pns = [e["pn"] for e in entries]
    assert len(pns) == d["surfaced_total"], "bucket entries must sum to surfaced_total"
    assert len(set(pns)) == len(pns), "a PN may not appear in two buckets"


def test_counts_block_matches_actual_bucket_lengths():
    d = _disp()
    bucket_for_count = {
        "ADD": "add",
        "REVIEW": "review",
        "EXCLUDE_SCOPE": "exclude_scope",
        "EXCLUDE_TAXONOMY": "exclude_taxonomy",
        "EXCLUDE_NOT_TRANSCEIVER": "exclude_not_transceiver",
    }
    for count_key, list_key in bucket_for_count.items():
        assert d["counts"][count_key] == len(d.get(list_key) or []), count_key
    assert sum(d["counts"].values()) == d["surfaced_total"]


def test_surfaced_total_matches_coverage_missing_count():
    d = _disp()
    cov = yaml.safe_load(COV.read_text(encoding="utf-8"))
    assert d["surfaced_total"] == cov["missing_count"]
    assert d["orphan_catalog_skus"] == cov["orphan_count"] == 0  # every shipped SKU re-found


def test_no_surfaced_pn_already_in_catalog():
    # "missing" means missing — a surfaced PN must not already be in the shipped catalog.
    d = _disp()
    catalog = set(json.loads(CONTENT.read_text(encoding="utf-8")).keys())
    for e in _all_entries(d):
        assert e["pn"] not in catalog, f"surfaced PN already in catalog: {e['pn']}"


# ---- grounding: dispositions agree with the real config -------------------------------

def test_add_families_are_locked22_and_in_curated_scope():
    d = _disp()
    locked22, expected = _locked22(), _expected()
    assert d["add"], "expected at least one ADD candidate"
    for e in d["add"]:
        assert "family" in e, f"ADD entry missing family: {e['pn']}"
        assert e["family"] in locked22, f"ADD family not locked-22: {e['pn']} -> {e['family']}"
        assert e["family"] in expected, f"ADD family not in expected_families: {e['pn']} -> {e['family']}"


def test_legacy_form_factors_bucketed_correctly():
    """The exact regression: XENPAK/GBIC are valid locked-22 form factors held out of the
    curated scope (EXCLUDE_SCOPE); POM genuinely is not a locked-22 token (EXCLUDE_TAXONOMY)."""
    d = _disp()
    locked22, expected = _locked22(), _expected()
    # sanity: the taxonomy really does list XENPAK + GBIC but not POM
    assert {"XENPAK", "GBIC"} <= locked22
    assert "POM" not in locked22
    assert {"XENPAK", "GBIC"}.isdisjoint(expected)  # valid form factor, but out of curated scope

    scope_pns = {e["pn"] for e in (d.get("exclude_scope") or [])}
    tax_pns = {e["pn"] for e in (d.get("exclude_taxonomy") or [])}

    for e in _all_entries(d):
        pn, desc = e["pn"], (e.get("description") or "")
        is_xenpak = "XENPAK" in pn or "xenpak" in desc.lower()
        is_gbic = pn.startswith(("DWDM-GBIC", "WS-G548")) or "gbic" in desc.lower()
        is_pom = pn.startswith("POM-OC")
        if is_xenpak or is_gbic:
            assert pn in scope_pns, f"legacy locked-22 optic must be EXCLUDE_SCOPE: {pn}"
        if is_pom:
            assert pn in tax_pns, f"POM must be EXCLUDE_TAXONOMY: {pn}"

    # and the buckets must be non-trivial (guards an empty-file false pass)
    assert scope_pns and tax_pns


def test_exclude_scope_reasons_do_not_claim_taxonomy_absence():
    # The reason must not regress to the false "not in the locked-22 taxonomy" wording.
    for e in (_disp().get("exclude_scope") or []):
        r = e["reason"].lower()
        assert "not in the locked-22" not in r, f"stale taxonomy-absence reason: {e['pn']}"
        assert "expected_families" in r or "curated" in r, f"scope reason ungrounded: {e['pn']}"
