"""Load and validate config/rules.yaml and config/weights.yaml."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

# config/ lives at the repo root (two levels up from this file's package dir).
_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_DIR.parents[1]  # .../hexcat
DEFAULT_RULES_PATH = _REPO_ROOT / "config" / "rules.yaml"
DEFAULT_WEIGHTS_PATH = _REPO_ROOT / "config" / "weights.yaml"
DEFAULT_TAXONOMY_PATH = _REPO_ROOT / "config" / "taxonomy" / "transceivers.yaml"


class ConfigError(Exception):
    """Raised when a config file is structurally invalid or has drifted from the contract."""


class VendorEntry(BaseModel):
    hersteller: str
    slug: str


class Constants(BaseModel):
    kategorie_ebene_1: str
    kategorie_ebene_2: str
    versandklasse: str
    verkaufseinheit: str
    bestandsfuehrung_aktiv: str
    ueberverkaeufe_moeglich: str
    ueberverkauf_plattform_hexwaren: str
    attributgruppe_transceiver: str


class WordRange(BaseModel):
    min_words: int
    max_words: int
    p_count: int


class TitelBudget(BaseModel):
    max_chars: int
    must_end_with: str


class MetaBudget(BaseModel):
    min_chars: int
    max_chars: int


class FaqBudget(BaseModel):
    min_pairs: int
    max_pairs: int


class Budgets(BaseModel):
    kurzbeschreibung: WordRange
    beschreibung: WordRange
    titel_tag: TitelBudget
    meta_description: MetaBudget
    faq: FaqBudget


class ConditionRule(BaseModel):
    attribute_name: str
    allowed: list[str]
    default: str

    @model_validator(mode="after")
    def _default_in_allowed(self) -> "ConditionRule":
        if self.default not in self.allowed:
            raise ValueError(
                f"condition.default '{self.default}' not in allowed {self.allowed}"
            )
        return self


class Rules(BaseModel):
    vendors: dict[str, VendorEntry]
    constants: Constants
    kategorie_ebene_3_allowed: list[str]
    budgets: Budgets
    beschreibung_closer_prefix: str
    banned_hard_fail: list[str]
    banned_warn: list[str]
    condition: ConditionRule

    # Case-insensitive vendor lookup cache, built lazily.
    def resolve_vendor(self, vendor: str) -> VendorEntry | None:
        key = vendor.strip().lower()
        for name, entry in self.vendors.items():
            if name.lower() == key:
                return entry
        return None

    @property
    def allowed_hersteller(self) -> set[str]:
        return {v.hersteller for v in self.vendors.values()}

    @property
    def allowed_slugs(self) -> set[str]:
        return {v.slug for v in self.vendors.values()}


class WeightEntry(BaseModel):
    artikel: float
    versand: float
    placeholder: bool = False

    @model_validator(mode="after")
    def _versand_gt_artikel(self) -> "WeightEntry":
        if not self.versand > self.artikel:
            raise ValueError(
                f"versand ({self.versand}) must be > artikel ({self.artikel})"
            )
        return self


class Weights(BaseModel):
    defaults: WeightEntry
    form_factors: dict[str, WeightEntry]

    def lookup(self, form_factor: str) -> tuple[WeightEntry, bool]:
        """Return (entry, used_default)."""
        entry = self.form_factors.get(form_factor.strip())
        if entry is not None:
            return entry, False
        return self.defaults, True


def _mark_placeholders(raw_text: str, weights: Weights) -> None:
    """Flag any weight whose source YAML line carries 'PLACEHOLDER'.

    We re-scan the raw YAML text because comments are stripped by the parser.
    A weight is a placeholder if its form-factor key line (or the line within
    its inline mapping) contains the word PLACEHOLDER.
    """
    placeholder_keys: set[str] = set()
    defaults_placeholder = False
    for line in raw_text.splitlines():
        if "PLACEHOLDER" not in line.upper():
            continue
        stripped = line.strip()
        # inline form "KEY": { ... }   # PLACEHOLDER
        if ":" in stripped and not stripped.startswith("#"):
            key = stripped.split(":", 1)[0].strip().strip('"').strip("'")
            if key in weights.form_factors:
                placeholder_keys.add(key)
            if key in ("artikel", "versand"):
                defaults_placeholder = True
        # Heuristic: under `defaults:` block, artikel/versand lines flagged.
    for k in placeholder_keys:
        weights.form_factors[k].placeholder = True
    if defaults_placeholder:
        weights.defaults.placeholder = True


@lru_cache(maxsize=8)
def load_rules(path: str | None = None) -> Rules:
    p = Path(path) if path else DEFAULT_RULES_PATH
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return Rules.model_validate(data)


@lru_cache(maxsize=8)
def load_weights(path: str | None = None) -> Weights:
    p = Path(path) if path else DEFAULT_WEIGHTS_PATH
    raw = p.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    weights = Weights.model_validate(data)
    _mark_placeholders(raw, weights)
    return weights


class TaxonomyAttribute(BaseModel):
    name: str
    intake_field: str


class Taxonomy(BaseModel):
    """The operator-facing canonical taxonomy for one category (config/taxonomy/*.yaml)."""

    category: str
    subcategories: list[str]
    attributes: list[TaxonomyAttribute]
    kategorie_ebene_2: str | None = None
    attributgruppe: str | None = None

    @model_validator(mode="after")
    def _checks(self) -> "Taxonomy":
        if "Sonstige" in self.subcategories:
            raise ValueError("'Sonstige' is never an allowed sub-category")
        if len(set(self.subcategories)) != len(self.subcategories):
            raise ValueError("duplicate sub-categories in taxonomy")
        return self

    @property
    def attribute_pairs(self) -> list[tuple[str, str]]:
        return [(a.name, a.intake_field) for a in self.attributes]


@lru_cache(maxsize=8)
def load_taxonomy(path: str | None = None) -> Taxonomy:
    p = Path(path) if path else DEFAULT_TAXONOMY_PATH
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return Taxonomy.model_validate(data)


def verify_taxonomy(path: str | None = None) -> Taxonomy:
    """Load the taxonomy and fail loudly if it has drifted from the locked contract.

    The 14 attributes (name + order = Sortiernummer) and the 22 sub-categories are part
    of the byte-exact output contract, mirrored in constants.py / rules.yaml. This guard
    makes config/taxonomy/transceivers.yaml load-bearing: an inconsistent edit stops the
    build instead of silently corrupting a live import.
    """
    from . import constants as C

    tax = load_taxonomy(path)

    code_attrs = list(C.TRANSCEIVER_ATTRIBUTES)
    yaml_attrs = tax.attribute_pairs
    if yaml_attrs != code_attrs:
        raise ConfigError(
            "taxonomy attributes drifted from constants.TRANSCEIVER_ATTRIBUTES "
            f"(Sortiernummer contract).\n  taxonomy.yaml: {yaml_attrs}\n  constants.py : {code_attrs}"
        )

    rules = load_rules()
    if list(tax.subcategories) != list(rules.kategorie_ebene_3_allowed):
        raise ConfigError(
            "taxonomy sub-categories drifted from rules.kategorie_ebene_3_allowed.\n"
            f"  taxonomy.yaml: {tax.subcategories}\n  rules.yaml   : {rules.kategorie_ebene_3_allowed}"
        )

    constants_block = rules.constants
    if tax.kategorie_ebene_2 not in (None, constants_block.kategorie_ebene_2):
        raise ConfigError(
            f"taxonomy kategorie_ebene_2 {tax.kategorie_ebene_2!r} != "
            f"rules {constants_block.kategorie_ebene_2!r}"
        )
    if tax.attributgruppe not in (None, constants_block.attributgruppe_transceiver):
        raise ConfigError(
            f"taxonomy attributgruppe {tax.attributgruppe!r} != "
            f"rules {constants_block.attributgruppe_transceiver!r}"
        )
    return tax
