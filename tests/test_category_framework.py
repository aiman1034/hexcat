"""§4 — the category-framework guard test.

HexCat's engine is category-agnostic: everything that makes the catalog *about transceivers*
lives in a small set of named seams (config files + a few code constants), inventoried in
docs/ADD_A_CATEGORY.md. This suite LOCKS that inventory so it cannot silently drift: every seam
the runbook names must exist and stay aligned with its sibling seams. When a real second category
arrives and someone lifts seams 2-6 behind a CategoryProfile, these assertions are the consistent
base that refactor starts from — and they catch an inconsistent edit (an attribute added to the
taxonomy but not constants.py, a form factor dropped from rules.yaml, a missing intake column)
before it can corrupt a live import.

If you are ADDING a category, read docs/ADD_A_CATEGORY.md first: these checks describe the
transceiver profile, and a new profile must satisfy the same cross-seam consistency.
"""
from __future__ import annotations

from pathlib import Path

from hexcat import constants as C
from hexcat.config import load_rules, load_taxonomy, verify_taxonomy
from hexcat.models import INTAKE_COLUMNS

REPO = Path(__file__).resolve().parents[1]
TAXONOMY = REPO / "config" / "taxonomy" / "transceivers.yaml"
CONTENT_PROMPT = REPO / "config" / "prompts" / "transceiver_content.txt"


# ---- seam 1+2: taxonomy file <-> attribute schema (the Sortiernummer contract) -------------

def test_taxonomy_file_exists():
    assert TAXONOMY.is_file(), "seam 1: config/taxonomy/<category>.yaml must exist"


def test_verify_taxonomy_passes():
    # config.verify_taxonomy() is the load-bearing guard: it fails loudly if the taxonomy file
    # and constants.TRANSCEIVER_ATTRIBUTES (or rules.kategorie_ebene_3_allowed) ever drift.
    verify_taxonomy(str(TAXONOMY))  # raises ConfigError on drift


def test_attribute_names_ordered_mirrors_the_tuple():
    # seam 2: ATTRIBUTE_NAMES_ORDERED IS the names of TRANSCEIVER_ATTRIBUTES, in order.
    assert C.ATTRIBUTE_NAMES_ORDERED == tuple(n for n, _ in C.TRANSCEIVER_ATTRIBUTES)


def test_taxonomy_attribute_pairs_equal_constants_tuple():
    tax = load_taxonomy(str(TAXONOMY))
    assert tax.attribute_pairs == list(C.TRANSCEIVER_ATTRIBUTES), (
        "seam 1<->2: taxonomy attributes must equal constants.TRANSCEIVER_ATTRIBUTES"
    )


def test_attribute_schema_is_fourteen_and_unique():
    names = [n for n, _ in C.TRANSCEIVER_ATTRIBUTES]
    assert len(names) == 14
    assert len(set(names)) == 14, "attribute names must be unique"


# ---- seam 3: wide-intake columns cover every intake_field --------------------------------

def test_every_intake_field_is_a_known_intake_column():
    fields = {f for _, f in C.TRANSCEIVER_ATTRIBUTES}
    missing = fields - set(INTAKE_COLUMNS)
    assert not missing, f"seam 3: intake_field(s) absent from models.INTAKE_COLUMNS: {missing}"


# ---- seam 4: category vocabulary <-> the Kategorie-Ebene-3 set ----------------------------

def test_physical_formfaktor_set_matches_its_ordered_tuple():
    assert C.PHYSICAL_FORMFAKTOR == frozenset(C.PHYSICAL_FORMFAKTOR_ORDERED)
    assert len(C.PHYSICAL_FORMFAKTOR_ORDERED) == len(C.PHYSICAL_FORMFAKTOR), "no duplicates"


def test_taxonomy_subcategories_equal_rules_kategorie_ebene_3():
    tax = load_taxonomy(str(TAXONOMY))
    rules = load_rules()
    assert list(tax.subcategories) == list(rules.kategorie_ebene_3_allowed), (
        "seam 4: taxonomy subcategories must equal rules.kategorie_ebene_3_allowed"
    )


def test_physical_formfaktor_is_subset_of_kategorie_ebene_3():
    allowed = set(load_rules().kategorie_ebene_3_allowed)
    assert C.PHYSICAL_FORMFAKTOR <= allowed, (
        "seam 4: every physical Formfaktor must be an allowed Kategorie Ebene 3"
    )


def test_cable_categories_are_a_subset_of_kategorie_ebene_3():
    allowed = set(load_rules().kategorie_ebene_3_allowed)
    assert C.CABLE_CATEGORIES <= allowed, (
        "seam 4: every cable sub-type must be an allowed Kategorie Ebene 3"
    )


def test_cable_and_physical_formfaktor_partition_cleanly():
    # A sub-type is either a physical optical module slot OR a cable, never both.
    assert not (C.CABLE_CATEGORIES & C.PHYSICAL_FORMFAKTOR), (
        "cable sub-types and physical form factors must not overlap"
    )


# ---- seam 8+9: prose policy + content prompt exist ---------------------------------------

def test_rules_carry_the_prose_policy_seams():
    rules = load_rules()
    assert rules.beschreibung_closer_prefix.strip(), "seam 8: closer prefix must be set"
    assert rules.banned_hard_fail, "seam 8: banned_hard_fail must be populated"
    assert rules.budgets is not None, "seam 8: budgets must be present"


def test_content_prompt_exists():
    assert CONTENT_PROMPT.is_file(), "seam 9: config/prompts/<category>_content.txt must exist"


# ---- the runbook itself is tracked -------------------------------------------------------

def test_add_a_category_runbook_is_present():
    doc = REPO / "docs" / "ADD_A_CATEGORY.md"
    assert doc.is_file(), "the §4 runbook docs/ADD_A_CATEGORY.md must be tracked"
