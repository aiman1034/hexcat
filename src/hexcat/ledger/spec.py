"""Load the Stage-1 ledger spec (config/ledger/*.yaml).

The spec is the deterministic contract for one brand+category: how to mine PNs from a
datasheet, normalize feed variants, classify into the operator's Unterkategorie, and map
that to the locked-22 token for the Stage-3 hand-off. Pydantic-validated, like config.py.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, model_validator

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_DIR.parents[2]  # .../hexcat
LEDGER_CONFIG_DIR = _REPO_ROOT / "config" / "ledger"
DEFAULT_SPEC_PATH = LEDGER_CONFIG_DIR / "cisco_transceivers.yaml"


class LedgerSpecError(Exception):
    """Raised when a ledger spec is structurally invalid or drifts from the taxonomy."""


class PdfMineSpec(BaseModel):
    """Per-brand PDF extraction config — the same 'config, not code' seam as the HTML
    adapter. Two structural modes (the engine supports both; config picks one):

      token    — scan text for SKU-shaped tokens, optionally scoped to the manufacturer's
                 own ordering section (e.g. Fortinet's "Ordering Information"). For PDFs
                 whose ordering list is a clean, flat SKU enumeration.
      section  — walk the document's form-factor CHAPTERS (e.g. "SFP+ Modules", "QSFP28
                 modules") and pull transceiver SKUs from their model entries, tagging each
                 with the chapter's form factor. For compatibility-matrix guides (HPE/Aruba)
                 where a flat token scan would conflate switch SKUs and lose classification.
    """
    mode: str = "token"                       # "token" | "section"
    sku_token: str                            # SKU shape kept from the scan
    scope_heading: str | None = None          # token: restrict to pages whose text has this
    collapse_bold_doubling: bool = False      # section: undo bold double-render for headings
    chapters: dict[str, str] = {}             # section: chapter-heading substring -> form factor
    context_noun: str | None = None           # section: SKU parenthetical must follow this noun
    # token: when set, mine the SKU *column* by word x-band rather than scanning whole rows.
    # This isolates the authoritative SKU column from Description prose (kills description-bleed
    # phantoms). desc_column captures the row's description for V5 classification.
    sku_column: str | None = None             # header text of the SKU column (e.g. "SKU")
    desc_column: str | None = None            # header text of the description column
    header_top_max: float = 200.0             # only words above this y are header candidates

    @property
    def sku_re(self) -> re.Pattern[str]:
        return re.compile(self.sku_token)

    @property
    def context_re(self) -> re.Pattern[str] | None:
        if not self.context_noun:
            return None
        # The manufacturer's own '<noun> (SKU)' callout: the optic noun must DIRECTLY label
        # the SKU (whitespace only). A wider window pulls in switch part numbers that merely
        # mention an optic nearby — e.g. 'All 400G AOCs … 9300S model (S0F84A)' is a switch
        # chassis, not an AOC. Keeping the noun adjacent is the flag-don't-guess boundary.
        return re.compile(self.context_noun + r"\s*\((" + self.sku_token + r")\)")


class MineSpec(BaseModel):
    pn_header_patterns: list[str]
    pn_token: str
    pdf: PdfMineSpec | None = None

    @property
    def pn_token_re(self) -> re.Pattern[str]:
        return re.compile(self.pn_token)

    def is_pn_header(self, header_cell: str) -> bool:
        h = (header_cell or "").strip().lower()
        return any(p in h for p in self.pn_header_patterns)


class NormalizeSpec(BaseModel):
    feed_id_suffix: str
    problem_feed_id: str
    spelling_fixes: dict[str, str] = {}
    problem_spelling: str = ""

    @property
    def feed_id_re(self) -> re.Pattern[str]:
        return re.compile(self.feed_id_suffix)


class ClassifyRule(BaseModel):
    pn_contains: str | None = None
    pn_prefix: str | None = None
    unterkategorie: str

    def matches(self, pn: str) -> bool:
        if self.pn_prefix is not None and pn.startswith(self.pn_prefix):
            return True
        if self.pn_contains is not None and self.pn_contains in pn:
            return True
        return False


class ClassifySpec(BaseModel):
    rules: list[ClassifyRule]
    default: str


class ExcludeRule(BaseModel):
    """A 'flag, don't emit' rule. A mined token matching this is NOT a transceiver/optic that
    fits the locked-22 taxonomy (e.g. a software license, an RTU, a QSFP-to-SFP converter
    adapter) — forcing it into a form-factor bucket would violate the 1000% rule. It is
    dropped from the emitted ledger AND from the verifier's independently re-derived
    authoritative set (symmetric, so V7/V8 stay honest), and reported on the flagged list.
    Matched against the canonical PN (pn_prefix/pn_contains) and/or the manufacturer
    description (description_contains, case-insensitive)."""
    pn_prefix: str | None = None
    pn_contains: str | None = None
    description_contains: str | None = None
    reason: str = "non-transceiver (flagged, not emitted)"

    def matches(self, pn: str, description: str | None = None) -> bool:
        if self.pn_prefix is not None and pn.startswith(self.pn_prefix):
            return True
        if self.pn_contains is not None and self.pn_contains in pn:
            return True
        if self.description_contains is not None:
            return self.description_contains.lower() in (description or "").lower()
        return False


# Universal cable classification (V5) — ONE rule, identical across every brand. Derived from
# the manufacturer's own description text, not the PN substring (a PN like FG-CABLE-SR10-SFP+
# contains "CABLE" and "SFP+" but the description proves it is an OM3 MPO breakout, not a DAC).
# The three returned tokens are locked-22 categories; None means "not a cable — use form factor".
UNIVERSAL_CABLE_CATEGORIES = ("DAC Kabel", "AOC Kabel", "MPO Kabel")


def classify_cable_from_description(description: str | None) -> str | None:
    """Map a manufacturer optic/cable description to its locked-22 cable category, or None.

    Order matters — the classes are disjoint in practice but we check the most specific
    phrasing first:
      * 'active optical cable'            -> AOC Kabel  (fibre, powered)
      * 'breakout MPO to <n>xLC' / parallel breakout MPO -> MPO Kabel (optical fan-out;
                                            often 'transceivers not included')
      * 'direct attach cable' (passive OR active copper, incl. 'active direct attach') -> DAC Kabel
    A transceiver module ('... transceiver module, MPO-12 connector ...') has an MPO *connector*
    but is NOT a breakout cable, so it falls through to form-factor classification (returns None).
    """
    d = (description or "").lower()
    if not d:
        return None
    # Explicit manufacturer label as the SKU's own noun (e.g. HPE/Aruba's '<noun> (SKU)'
    # callout where the noun IS 'DAC' or 'AOC'). The whole-string check keeps 'transceiver'
    # and prose descriptions from matching here.
    if d.strip() == "dac":
        return "DAC Kabel"
    if d.strip() == "aoc":
        return "AOC Kabel"
    if "active optical cable" in d:
        return "AOC Kabel"
    # Optical MPO fan-out cable: the discriminator is "breakout MPO to" (vs a transceiver's
    # bare "MPO-12 connector"). A copper DAC breakout says "direct attach cable", not "MPO".
    if "breakout mpo" in d or ("parallel breakout" in d and "mpo" in d):
        return "MPO Kabel"
    if "direct attach cable" in d:
        return "DAC Kabel"
    return None


class LedgerSpec(BaseModel):
    brand: str
    hauptkategorie: str
    mine: MineSpec
    normalize: NormalizeSpec
    classify: ClassifySpec
    exclude: list[ExcludeRule] = []
    locked22_map: dict[str, str] = {}

    # --- exclusion ------------------------------------------------------------
    def is_excluded(self, pn: str, description: str | None = None) -> str | None:
        """Return the exclusion reason if this mined token is a non-transceiver to flag
        (not emit), else None. Applied identically by the engine and the verifier so the
        emitted set and the independently re-derived authoritative set stay equal."""
        for rule in self.exclude:
            if rule.matches(pn, description):
                return rule.reason
        return None

    # --- classification -------------------------------------------------------
    def classify_pn(self, pn: str) -> str:
        """Return the operator-convention Unterkategorie for a canonical PN."""
        for rule in self.classify.rules:
            if rule.matches(pn):
                return rule.unterkategorie
        return self.classify.default

    def resolve_unterkategorie(self, pn: str, description: str | None = None,
                               hint: str | None = None) -> str:
        """Resolve the Unterkategorie for one mined PN, applying the universal V5 rule.

        Precedence: a cable category proven by the manufacturer's DESCRIPTION wins over every
        other signal (it is the only thing that can tell an OM3 MPO breakout apart from a DAC,
        or a copper DAC apart from its host form factor). Only when the description does not
        prove a cable type do we fall back to the section-mode chapter `hint`, then to the
        per-brand PN-substring rules. This keeps DAC/AOC/MPO identical across all brands.
        """
        cable = classify_cable_from_description(description)
        if cable is not None:
            return cable
        if hint is not None:
            return hint
        return self.classify_pn(pn)

    def to_locked22(self, unterkategorie: str) -> str:
        """Map an operator Unterkategorie to its locked-22 token (identity if unlisted)."""
        return self.locked22_map.get(unterkategorie, unterkategorie)

    @model_validator(mode="after")
    def _nonempty(self) -> "LedgerSpec":
        if not self.classify.default:
            raise ValueError("classify.default must be a non-empty Unterkategorie")
        return self


@lru_cache(maxsize=8)
def load_ledger_spec(path: str | None = None) -> LedgerSpec:
    p = Path(path) if path else DEFAULT_SPEC_PATH
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return LedgerSpec.model_validate(data)


def verify_ledger_spec(path: str | None = None) -> LedgerSpec:
    """Load the spec and fail loudly if any Unterkategorie target / locked-22 value is
    not in the locked-22 taxonomy. Keeps the ledger's classification honest against the
    same Kategorie-Ebene-3 contract Stage 3 enforces.
    """
    from ..config import load_taxonomy

    spec = load_ledger_spec(path)
    locked22 = set(load_taxonomy().subcategories)

    # Every locked22_map TARGET must be a real locked-22 token.
    for src, dst in spec.locked22_map.items():
        if dst not in locked22:
            raise LedgerSpecError(
                f"locked22_map[{src!r}] -> {dst!r} is not in the locked-22 taxonomy "
                f"(config/taxonomy/transceivers.yaml subcategories)."
            )

    # Every Unterkategorie the classifier can emit must map (directly or by identity)
    # into the locked-22 set — otherwise the Stage-3 hand-off would be invalid. Section-mode
    # PDFs emit the form factor straight from the chapter heading (bypassing classify), so
    # those chapter tags are emittable too and must be checked here.
    emittable = {r.unterkategorie for r in spec.classify.rules} | {spec.classify.default}
    emittable |= set(UNIVERSAL_CABLE_CATEGORIES)  # V5 can emit these from any brand
    if spec.mine.pdf is not None:
        emittable |= set(spec.mine.pdf.chapters.values())
    for uk in emittable:
        mapped = spec.to_locked22(uk)
        if mapped not in locked22:
            raise LedgerSpecError(
                f"classifier can emit Unterkategorie {uk!r} which maps to {mapped!r}, "
                f"not in the locked-22 taxonomy. Add a locked22_map entry."
            )
    return spec
