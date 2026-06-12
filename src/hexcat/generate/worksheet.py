"""The $0 content surface: turn a facts-only skeleton into a fill-in worksheet, and
read the authored worksheet back into per-SKU content.

`hexcat worksheet` writes a Markdown worksheet — the rendered voice guide, then one
section per SKU with its verified facts, the per-field rules restated from the live
config, and an empty BEGIN/END block for each of the five content fields. Claude Code
fills those blocks in-session (no API, no cost). `hexcat draft` then reads the worksheet
back, merges the authored content with the skeleton facts, and writes a draft intake CSV.

Parsing is deterministic: each content block is delimited by unambiguous HTML-comment
markers that carry both the field name and the SKU, so blocks can never be confused even
though the authored prose contains arbitrary HTML.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..config import Rules
from ..content_checks import closer_brand_tail
from .engine import CONTENT_COLUMNS, GenerateError, SkuFacts
from .prompt import GUIDE_VERSION, build_voice_guide, facts_block

# Order the content fields are presented in the worksheet (Artikelname is a FACT, not here).
_FIELD_ORDER = ("Kurzbeschreibung", "Beschreibung", "TitelTag", "MetaDescription", "FAQ")

_SKELETON_RE = re.compile(r"<!--\s*HEXCAT:SKELETON\s+(.+?)\s*-->")
# A content block: <!-- HEXCAT:BEGIN <Field> | <SKU> --> ... <!-- HEXCAT:END <Field> | <SKU> -->
_BLOCK_RE = re.compile(
    r"<!--\s*HEXCAT:BEGIN\s+(?P<field>\S+)\s*\|\s*(?P<sku>.+?)\s*-->"
    r"(?P<body>.*?)"
    r"<!--\s*HEXCAT:END\s+(?P=field)\s*\|\s*(?P=sku)\s*-->",
    re.DOTALL,
)


def _begin(field: str, sku: str) -> str:
    return f"<!-- HEXCAT:BEGIN {field} | {sku} -->"


def _end(field: str, sku: str) -> str:
    return f"<!-- HEXCAT:END {field} | {sku} -->"


def _field_rules(rules: Rules, hersteller: str) -> dict[str, str]:
    b = rules.budgets
    tail = closer_brand_tail(rules, hersteller)
    return {
        "Kurzbeschreibung": (
            f"HTML, genau {b.kurzbeschreibung.p_count} <p>…</p>-Absätze, insgesamt "
            f"{b.kurzbeschreibung.min_words}–{b.kurzbeschreibung.max_words} Wörter."
        ),
        "Beschreibung": (
            f"HTML, genau {b.beschreibung.p_count} <p>…</p>-Absätze, insgesamt "
            f"{b.beschreibung.min_words}–{b.beschreibung.max_words} Wörter. Der letzte "
            f"Absatz MUSS den Echtheits-Abschluss 'Original(er|es|e) {tail}' enthalten – "
            f"die Adjektivendung richtet sich nach dem Geschlecht des folgenden Substantivs "
            f"(z. B. 'Originaler {tail}Transceiver', 'Originales {tail}Direktanschlusskabel')."
        ),
        "TitelTag": (
            f"Reiner Text, höchstens {b.titel_tag.max_chars} Zeichen inkl. Suffix; MUSS "
            f"mit '{b.titel_tag.must_end_with}' enden."
        ),
        "MetaDescription": (
            f"Reiner Text, {b.meta_description.min_chars}–{b.meta_description.max_chars} Zeichen."
        ),
        "FAQ": (
            f"{b.faq.min_pairs}–{b.faq.max_pairs} Paare, je ein Paar pro Zeile als "
            f"'Frage? :: Antwort.'. Kein '||', '##' oder ';;' im Text."
        ),
    }


def write_worksheet(
    path: str | Path,
    facts_list: list[SkuFacts],
    rules: Rules,
    *,
    skeleton_path: str | Path,
) -> None:
    """Write the Markdown content worksheet for every SKU in `facts_list`."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    banned = ", ".join(f"'{p}'" for p in rules.banned_hard_fail)

    out: list[str] = [
        f"<!-- HEXCAT:WORKSHEET {GUIDE_VERSION} -->",
        f"<!-- HEXCAT:SKELETON {skeleton_path} -->",
        "# HexCat Content-Arbeitsblatt",
        "",
        "Fülle jeden Block zwischen den `BEGIN`/`END`-Markern. Schreibe NUR den Inhalt — "
        "Marker, Fakten und Regeln nicht verändern. Danach: `hexcat draft` ausführen.",
        "",
        "## Voice & Regeln (verbindlich)",
        "",
        build_voice_guide(rules).strip(),
        "",
        f"Verbotene Formulierungen (führen zum Fehler): {banned}",
        "",
        "---",
        "",
    ]

    for f in facts_list:
        rules_for_field = _field_rules(rules, f.hersteller)
        out += [
            f"## {f.sku}  ({f.hersteller} · {f.row.get('KategorieEbene3', '').strip()})",
            "",
            "### Fakten (nur Referenz — nicht bearbeiten)",
            facts_block(f.row, f.hersteller),
            f"- NettoVK: {f.row.get('NettoVK', '').strip()}",
            f"- Condition: {f.row.get('Condition', '').strip() or 'new'}",
            f"- SourceURLs: {f.row.get('SourceURLs', '').strip() or '(keine)'}",
            "",
            "### Inhalt",
            "",
        ]
        for field in _FIELD_ORDER:
            out += [
                f"**{field}** — {rules_for_field[field]}",
                "",
                _begin(field, f.sku),
                "",
                _end(field, f.sku),
                "",
            ]
        out += ["---", ""]

    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="")


def _faq_block_to_cell(body: str) -> str:
    """Join the per-line 'Frage :: Antwort' pairs into a friendly FAQ cell.

    Each non-empty line is one pair; `read_intake`/`validate` normalise the friendly
    'Q :: A ;; Q :: A' form (a malformed line surfaces there as a located FAQ error).
    """
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    return " ;; ".join(lines)


def read_worksheet(
    path: str | Path,
) -> tuple[str | None, dict[str, dict[str, str]]]:
    """Parse an authored worksheet.

    Returns (skeleton_path_or_None, {sku: {content_field: text}}). The FAQ field is
    converted to a friendly 'Q :: A ;; Q :: A' cell. Empty blocks come back as "".
    """
    path = Path(path)
    if not path.exists():
        raise GenerateError(f"worksheet file not found: {path}")
    text = path.read_text(encoding="utf-8")

    m = _SKELETON_RE.search(text)
    skeleton_path = m.group(1).strip() if m else None

    content: dict[str, dict[str, str]] = {}
    valid_fields = set(CONTENT_COLUMNS)
    for block in _BLOCK_RE.finditer(text):
        field = block.group("field")
        sku = block.group("sku").strip()
        if field not in valid_fields:
            raise GenerateError(
                f"worksheet block for SKU {sku!r} names unknown field {field!r}."
            )
        body = block.group("body").strip()
        if field == "FAQ":
            body = _faq_block_to_cell(body)
        content.setdefault(sku, {})[field] = body

    if not content:
        raise GenerateError(
            f"worksheet {path.name} has no HEXCAT content blocks. "
            f"Generate it with `hexcat worksheet`."
        )
    return skeleton_path, content
