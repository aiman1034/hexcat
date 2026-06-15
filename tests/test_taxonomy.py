"""config/taxonomy/transceivers.yaml is the canonical taxonomy and must stay in lockstep
with the structural contract (constants.py + rules.yaml)."""
from __future__ import annotations

import pytest

from hexcat import constants as C
from hexcat.config import ConfigError, load_taxonomy, verify_taxonomy


def test_taxonomy_loads_with_25_subcategories_and_14_attributes():
    tax = load_taxonomy()
    assert tax.category == "transceivers"
    # 25 form factors. CIM8 (Cisco NCS 1014 coherent module) stays. POM (Cisco SONET/SDH) was REMOVED
    # 2026-06-14 (out of scope, the one operator-authorized domain exclusion). SFP-DD + QSFP28-DD were
    # ADDED 2026-06-15 — real current Dell module form factors (S56DD-100G, Q28DD-200G): a missing form
    # factor is a taxonomy gap to FIX, never an exclusion. Every in-domain transceiver PN is included.
    assert len(tax.subcategories) == 25
    assert "CIM8" in tax.subcategories
    assert {"SFP-DD", "QSFP28-DD"} <= set(tax.subcategories)
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
