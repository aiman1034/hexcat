"""Lock the Cisco transceiver coverage closure under the NON-NEGOTIABLE completeness rule:

  Every physical part number that is a real Ethernet/datacom transceiver is in the catalog. Two
  permitted exclusions only: (1) a part that is genuinely NOT a transceiver (license, bracket,
  adapter, software, passive cable, or CPE box); (2) a part in a DIFFERENT protocol domain that
  the operator has explicitly ruled out of scope — SONET/SDH (POM) was ruled out 2026-06-14 (L8
  round-3), the same call as Juniper SONET. "Legacy", "EOL", and "obsolete" are NEVER valid
  exclusion reasons for an IN-DOMAIN (Ethernet/datacom) transceiver — EOL is an informational
  flag; the part still belongs in the catalog. A missing form factor is a taxonomy gap to FIX,
  never a reason to drop an in-domain part.

These assert config/coverage/cisco_transceivers_disposition.yaml stays consistent with that
rule. The decisive regression — test_legacy_transceivers_are_added_not_excluded — pins that
XENPAK / GBIC / DWDM-GBIC (all real Ethernet transceivers, all EOL) are ADD/authored, not dropped:
an earlier triage wrongly excluded 75 of them as "out of scope", directly violating the mission.
That can never silently come back. The ONE authorized domain exclusion (SONET/SDH POM) is pinned
explicitly and separately, so it stays a deliberate, traceable, operator-owned decision.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DISP = ROOT / "config" / "coverage" / "cisco_transceivers_disposition.yaml"
COV = ROOT / "config" / "coverage" / "cisco_transceivers_coverage.yaml"
TAX = ROOT / "config" / "taxonomy" / "transceivers.yaml"
CONTENT = ROOT / "stage3_content" / "Cisco_content.json"

_BUCKET_KEYS = ("add", "exclude_not_transceiver")


def _disp() -> dict:
    return yaml.safe_load(DISP.read_text(encoding="utf-8"))


def _taxonomy() -> set[str]:
    return set(yaml.safe_load(TAX.read_text(encoding="utf-8"))["subcategories"])


def _all_entries(d: dict) -> list[dict]:
    return [e for k in _BUCKET_KEYS for e in (d.get(k) or [])]


# ---- accounting: nothing silently dropped, nothing double-counted ---------------------

def test_every_surfaced_pn_accounted_exactly_once():
    d = _disp()
    pns = [e["pn"] for e in _all_entries(d)]
    assert len(pns) == d["surfaced_total"], "bucket entries must sum to surfaced_total"
    assert len(set(pns)) == len(pns), "a PN may not appear in two buckets"


def test_counts_block_matches_actual_bucket_lengths():
    d = _disp()
    assert d["counts"]["ADD"] == len(d.get("add") or [])
    assert d["counts"]["EXCLUDE_NOT_TRANSCEIVER"] == len(d.get("exclude_not_transceiver") or [])
    assert sum(d["counts"].values()) == d["surfaced_total"]


def test_surfaced_total_matches_coverage_and_orphan_zero():
    d = _disp()
    cov = yaml.safe_load(COV.read_text(encoding="utf-8"))
    assert d["surfaced_total"] == cov["missing_count"]
    # No UNDOCUMENTED orphans: every shipped SKU is re-found in a mined datasheet, EXCEPT a small
    # explicitly-documented set grounded from datasheets the generic optic miner cannot parse
    # (CIM8 = NCS-1014 coherent trunk modules). Those are listed in `grounded_orphans` with source;
    # anything else orphaned is a real defect.
    assert d["orphan_catalog_skus"] == 0
    documented = {o["pn"] for o in (d.get("grounded_orphans") or [])}
    assert set(cov.get("orphan", [])) <= documented, "undocumented orphan catalog SKU"


def test_excluded_nontransceiver_pn_never_in_catalog():
    """A part classified `exclude_not_transceiver` must never be shipped in the catalog. ADD parts,
    by contrast, GRADUATE into the catalog as they are authored (that is the mission's goal), so an
    ADD PN legitimately appears in both the disposition's add bucket and the catalog — that is not a
    double-listing defect. The invariant that still matters: nothing we deemed 'not a transceiver'
    ever leaks into the shipped set."""
    d = _disp()
    catalog = set(json.loads(CONTENT.read_text(encoding="utf-8")).keys())
    for e in (d.get("exclude_not_transceiver") or []):
        assert e["pn"] not in catalog, f"excluded non-transceiver PN is in catalog: {e['pn']}"


# ---- the core rule: every real transceiver is ADD; only non-transceivers excluded -----

def test_add_families_are_valid_taxonomy_tokens():
    d = _disp()
    tax = _taxonomy()
    assert d["add"], "expected real transceivers to ADD"
    for e in d["add"]:
        assert "family" in e, f"ADD entry missing family: {e['pn']}"
        assert e["family"] in tax, f"ADD family not a taxonomy token: {e['pn']} -> {e['family']}"


def test_only_genuine_non_transceivers_are_excluded():
    """Every excluded PN must be a recognised non-transceiver class: a passive M12 patch cable,
    a Routed-PON ONT (CPE box), the NCS-FAB-OPT bundle wrapper, an ONS 15454 MSPP line card
    (host device, not a pluggable), or a pluggable C-band EDFA optical amplifier (a different
    device class with no bit rate). Nothing else may be dropped."""
    d = _disp()
    is_line_card = {"E1000-2-G"}            # ONS 15454 MSPP line card (host device)
    is_amplifier = {"ONS-QDD-OLS"}          # C-band EDFA / Open Line System amplifier (no bit rate)
    for e in (d.get("exclude_not_transceiver") or []):
        pn = e["pn"]
        ok = (pn.startswith("CB-M12") or pn.startswith("ENC-10G-ONT") or pn == "NCS-FAB-OPT"
              or pn in is_line_card or pn in is_amplifier)
        assert ok, f"excluded PN is not a known non-transceiver: {pn}"


def test_legacy_transceivers_are_added_not_excluded():
    """THE regression: XENPAK / GBIC / POM are real transceivers (and EOL). They MUST be ADD or
    already AUTHORED — never excluded for being legacy/EOL/'out of scope'. As the grind authors a
    legacy family it graduates from the disposition's ADD bucket into the shipped catalog; the
    invariant is that it is NEVER in exclude_not_transceiver, and is present in catalog ∪ add."""
    d = _disp()
    catalog = set(json.loads(CONTENT.read_text(encoding="utf-8")).keys())
    add_pns = {e["pn"] for e in d["add"]}
    excluded_pns = {e["pn"] for e in (d.get("exclude_not_transceiver") or [])}

    # In-domain (Ethernet/datacom) legacy families — POM (SONET/SDH) is NOT here; it is the operator's
    # authorized domain exclusion, pinned separately below.
    def is_legacy(pn: str) -> bool:
        return "XENPAK" in pn.upper() or pn.startswith(("DWDM-GBIC", "WS-G548"))

    # 1) no in-domain legacy real transceiver is ever excluded
    for pn in excluded_pns:
        assert not is_legacy(pn), f"legacy real transceiver wrongly excluded: {pn}"
    # 2) the in-domain legacy families are present in the AUTHORED catalog — proof they were added
    assert any("XENPAK" in p.upper() for p in catalog), "no XENPAK authored"
    assert any(p.startswith("DWDM-GBIC") for p in catalog), "no DWDM-GBIC authored"
    # 3) any in-domain legacy part still surfaced (not yet authored) is ADD, never dropped
    for e in _all_entries(d):
        if is_legacy(e["pn"]):
            assert e["pn"] in add_pns and e["pn"] not in excluded_pns

    # in-domain legacy form factors must be present in the taxonomy
    tax = _taxonomy()
    assert {"XENPAK", "GBIC"} <= tax

    # THE authorized domain exclusion: SONET/SDH POM is out of scope (operator, L8 round-3) — so its
    # SKUs are NOT authored and its form-factor token is NOT in the taxonomy. This is the deliberate,
    # documented exception that proves the rule; it is distinct from EOL/legacy, which never exclude.
    assert not any(p.startswith("POM-") for p in catalog), "POM (SONET/SDH) must be out of scope, not authored"
    assert "POM" not in tax, "POM form-factor token must be removed (SONET/SDH out of scope)"


def test_eol_is_a_flag_not_an_exclusion_reason():
    """EOL parts are still ADD. The disposition flags lifecycle=EOL informationally; an EOL part
    is never moved to the exclude bucket. Most surfaced parts are EOL — all of them are ADD."""
    d = _disp()
    # lifecycle=EOL only ever appears on ADD entries
    for e in (d.get("exclude_not_transceiver") or []):
        assert e.get("lifecycle") != "EOL"
    eol_add = [e for e in d["add"] if e.get("lifecycle") == "EOL"]
    assert eol_add, "expected EOL-flagged real transceivers in ADD"
    assert d["add_eol_flagged"] == len(eol_add)


def test_no_exclusion_reason_mentions_legacy_or_scope():
    """Guard against regressing to a lifecycle/scope-based exclusion reason."""
    for e in (_disp().get("exclude_not_transceiver") or []):
        r = e["reason"].lower()
        for forbidden in ("legacy", "eol", "obsolete", "out of scope", "out of curated", "expected_families"):
            assert forbidden not in r, f"exclusion reason cites {forbidden!r} (forbidden): {e['pn']}"
