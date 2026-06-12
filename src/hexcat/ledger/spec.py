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


class LedgerSpec(BaseModel):
    brand: str
    hauptkategorie: str
    mine: MineSpec
    normalize: NormalizeSpec
    classify: ClassifySpec
    locked22_map: dict[str, str] = {}

    # --- classification -------------------------------------------------------
    def classify_pn(self, pn: str) -> str:
        """Return the operator-convention Unterkategorie for a canonical PN."""
        for rule in self.classify.rules:
            if rule.matches(pn):
                return rule.unterkategorie
        return self.classify.default

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
