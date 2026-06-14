"""config/taxonomy/transceivers.yaml is the canonical taxonomy and must stay in lockstep
with the structural contract (constants.py + rules.yaml)."""
from __future__ import annotations

import pytest

from hexcat import constants as C
from hexcat.config import ConfigError, load_taxonomy, verify_taxonomy


def test_taxonomy_loads_with_23_subcategories_and_14_attributes():
    tax = load_taxonomy()
    assert tax.category == "transceivers"
    # 23 form factors. CIM8 (Cisco NCS 1014 Coherent Interface Module 8 — a coherent DWDM trunk
    # pluggable) stays: a real current Cisco form factor, catalogued rather than dropped. POM (Cisco
    # SONET/SDH Pluggable Optic Module) was REMOVED 2026-06-14 (L8 round-3): SONET/SDH is out of scope
    # for the Ethernet/datacom catalog — the one operator-authorized domain exclusion. Every in-domain
    # transceiver PN is still included; a taxonomy gap is fixed, never used as an exclusion.
    assert len(tax.subcategories) == 23
    assert "CIM8" in tax.subcategories
    assert "POM" not in tax.subcategories
    assert "Sonstige" not in tax.subcategories
    assert len(tax.attributes) == 14


def test_verify_taxonomy_passes_against_the_locked_contract():
    tax = verify_taxonomy()
    # attribute names + intake fields + order == the Sortiernummer tuple in constants.py
    assert tax.attribute_pairs == list(C.TRANSCEIVER_ATTRIBUTES)


def test_verify_taxonomy_fails_loudly_on_attribute_drift(tmp_path):
    bad = tmp_path / "transceivers.yaml"
    bad.write_text(
        "category: transceivers\n"
        "subcategories: [SFP]\n"
        "attributes:\n"
        "  - { name: Formfaktor, intake_field: Formfaktor }\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        verify_taxonomy(str(bad))
