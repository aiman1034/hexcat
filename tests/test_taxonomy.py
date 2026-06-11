"""config/taxonomy/transceivers.yaml is the canonical taxonomy and must stay in lockstep
with the structural contract (constants.py + rules.yaml)."""
from __future__ import annotations

import pytest

from hexcat import constants as C
from hexcat.config import ConfigError, load_taxonomy, verify_taxonomy


def test_taxonomy_loads_with_22_subcategories_and_14_attributes():
    tax = load_taxonomy()
    assert tax.category == "transceivers"
    assert len(tax.subcategories) == 22
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
