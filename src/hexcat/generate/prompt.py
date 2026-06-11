"""Voice guide construction for the $0 content flow.

The voice guide is rendered from an external template
(`config/prompts/transceiver_content.txt`) whose budget/banned tokens are filled
from the LIVE rules, so the guidance can never drift from the build gate. Tokens are
substituted with str.replace (NOT str.format) so any literal braces in the template
survive untouched. The rendered guide is embedded at the top of `hexcat worksheet`
output, so Claude Code authors prose against the exact rules the gate enforces.

GUIDE_VERSION stamps the worksheet so a stale worksheet against new rules is visible.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from ..config import Rules
from .. import constants as C

GUIDE_VERSION = "transceiver-content-v2"

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_DIR.parents[2]  # .../hexcat
DEFAULT_TEMPLATE_PATH = _REPO_ROOT / "config" / "prompts" / "transceiver_content.txt"

# Facts the model is shown (intake column -> human label). Order is presentation order.
# NOTE: Artikelname is a PASSED-THROUGH FACT, not a generated field (operator decision;
# this diverges from the Phase 2 spec's field list and is flagged in the README/report).
_FACT_LABELS = (
    ("Artikelnummer", "Artikelnummer (SKU)"),
    ("Artikelname", "Artikelname"),
    ("KategorieEbene3", "Kategorie (Formfaktor-Kategorie)"),
)


@lru_cache(maxsize=4)
def _load_template(path: str | None = None) -> str:
    p = Path(path) if path else DEFAULT_TEMPLATE_PATH
    return p.read_text(encoding="utf-8")


def build_voice_guide(rules: Rules, template_path: str | None = None) -> str:
    """Render the voice template with the live budget/banned values from `rules`."""
    b = rules.budgets
    banned = "; ".join(f"'{p}'" for p in rules.banned_hard_fail)
    puffery = "; ".join(f"'{p}'" for p in rules.banned_warn)
    tokens = {
        "{{BANNED}}": banned,
        "{{PUFFERY}}": puffery,
        "{{KURZ_P}}": str(b.kurzbeschreibung.p_count),
        "{{KURZ_MIN}}": str(b.kurzbeschreibung.min_words),
        "{{KURZ_MAX}}": str(b.kurzbeschreibung.max_words),
        "{{BESCH_P}}": str(b.beschreibung.p_count),
        "{{BESCH_MIN}}": str(b.beschreibung.min_words),
        "{{BESCH_MAX}}": str(b.beschreibung.max_words),
        "{{TITEL_MAX}}": str(b.titel_tag.max_chars),
        "{{TITEL_SUFFIX}}": b.titel_tag.must_end_with,
        "{{META_MIN}}": str(b.meta_description.min_chars),
        "{{META_MAX}}": str(b.meta_description.max_chars),
        "{{FAQ_MIN}}": str(b.faq.min_pairs),
        "{{FAQ_MAX}}": str(b.faq.max_pairs),
    }
    text = _load_template(template_path)
    for tok, val in tokens.items():
        text = text.replace(tok, val)
    return text


def facts_block(row: dict[str, str], hersteller: str) -> str:
    lines: list[str] = []
    for col, label in _FACT_LABELS:
        val = (row.get(col) or "").strip()
        if val:
            lines.append(f"- {label}: {val}")
    lines.append(f"- Hersteller: {hersteller}")
    for attr_name, intake_field in C.TRANSCEIVER_ATTRIBUTES:
        val = (row.get(intake_field) or "").strip()
        if val:
            lines.append(f"- {attr_name}: {val}")
    return "\n".join(lines)
