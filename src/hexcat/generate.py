"""Phase 2: AI content generation.

This is the ONLY module in HexCat that makes network/model calls. It reads a facts-only
*skeleton* intake CSV, drafts the five German content fields per SKU
(Kurzbeschreibung, Beschreibung, TitelTag, MetaDescription, FAQ) via the Anthropic API,
self-checks each draft against the SAME budget/banned rules the build gate enforces
(`content_checks`), retries with feedback up to a bound, and writes a NEW *draft* intake
CSV. A human reviews/edits that draft, then runs the deterministic `hexcat build` on it.

The build/validate/intake core stays fully offline; nothing here is imported by them.

Testability: `Generator` takes an injectable `completer(system, user) -> str`. The CLI
wires a real Anthropic-backed completer; tests pass a deterministic fake. So the test
suite never touches the network, exactly like Phase 1.
"""
from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import constants as C
from .config import Rules
from .content_checks import content_issues, required_closer, word_count
from .models import INTAKE_COLUMNS, FaqPair

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_RETRIES = 4
DEFAULT_MAX_TOKENS = 1800
DEFAULT_TEMPERATURE = 0.7

# (system_prompt, user_prompt) -> raw model text
Completer = Callable[[str, str], str]

# Content-bearing intake columns this module fills.
CONTENT_COLUMNS = ("Kurzbeschreibung", "Beschreibung", "TitelTag", "MetaDescription", "FAQ")

# Facts the model is shown (intake column -> human label). Order is presentation order.
_FACT_LABELS = (
    ("Artikelnummer", "Artikelnummer (SKU)"),
    ("Artikelname", "Artikelname"),
    ("KategorieEbene3", "Kategorie (Formfaktor-Kategorie)"),
)
# The 14 transceiver attribute columns are appended after the above (when non-empty).


class GenerateError(Exception):
    """Raised for skeleton/parse/config problems. Message is operator-actionable."""


# --------------------------------------------------------------------------- #
# Skeleton intake (facts only)                                                 #
# --------------------------------------------------------------------------- #
@dataclass
class SkuFacts:
    lineno: int
    row: dict[str, str]   # the full intake row as read (content cells may be blank)
    sku: str
    vendor: str
    hersteller: str


def read_skeleton(path: str | Path, rules: Rules) -> list[SkuFacts]:
    """Read a facts-only intake CSV. Unlike `read_intake`, content fields may be blank.

    Skips blank rows and the commented example row (Artikelnummer starts with '#').
    Resolves vendor->Hersteller now (needed for the prompt and the closer). Fails fast
    on unknown vendors and duplicate SKUs — both are operator input errors.
    """
    path = Path(path)
    if not path.exists():
        raise GenerateError(f"skeleton intake file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise GenerateError(f"skeleton intake file {path.name} is empty.")
        missing = [c for c in INTAKE_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise GenerateError(
                f"skeleton header missing required columns: {missing}. "
                f"Run `hexcat new-intake` for the correct template."
            )

        facts: list[SkuFacts] = []
        seen: set[str] = set()
        for lineno, row in enumerate(reader, start=2):
            sku = (row.get("Artikelnummer") or "").strip()
            if not sku or sku.startswith("#"):
                continue
            if sku in seen:
                raise GenerateError(
                    f"skeleton line {lineno}: duplicate Artikelnummer {sku!r}."
                )
            seen.add(sku)
            vendor = (row.get("Vendor") or "").strip()
            entry = rules.resolve_vendor(vendor)
            if entry is None:
                raise GenerateError(
                    f"skeleton line {lineno} [{sku}]: Vendor {vendor!r} not in allowed "
                    f"set {sorted(rules.vendors)}."
                )
            payload = {k: (row.get(k) or "") for k in INTAKE_COLUMNS}
            facts.append(
                SkuFacts(lineno=lineno, row=payload, sku=sku,
                         vendor=vendor, hersteller=entry.hersteller)
            )

    if not facts:
        raise GenerateError(f"skeleton intake file {path.name} contained no SKU rows.")
    return facts


# --------------------------------------------------------------------------- #
# Prompt construction                                                          #
# --------------------------------------------------------------------------- #
def build_system_prompt(rules: Rules) -> str:
    """System prompt derived from the live rules, so it never drifts from the gate."""
    b = rules.budgets
    banned = "; ".join(f"'{p}'" for p in rules.banned_hard_fail)
    puffery = "; ".join(f"'{p}'" for p in rules.banned_warn)
    return (
        "Du bist ein erfahrener deutscher B2B-E-Commerce-Texter für Hexwaren, einen "
        "Händler für ORIGINALE, fabrikneue OEM-Netzwerk-Hardware (z. B. Cisco, HPE/Aruba, "
        "Juniper, Arista, Meraki).\n\n"
        "POSITIONIERUNG (zwingend): Es handelt sich ausschließlich um originale, "
        "fabrikneue Herstellerware. Schreibe NIEMALS, dass ein Produkt 'kompatibel', "
        "'compatible', 'refurbished', 'gebraucht' oder ein Nachbau/Drittanbieter-Produkt "
        "sei. Betone Authentizität und OEM-Herkunft sachlich, ohne Superlative.\n\n"
        "VERBOTENE FORMULIERUNGEN (rechtlich riskant, dürfen NICHT vorkommen): "
        f"{banned}.\n"
        f"ZU VERMEIDENDE Werbe-Floskeln (Puffery): {puffery}.\n\n"
        "AUSGABEFORMAT: Antworte AUSSCHLIESSLICH mit einem einzigen JSON-Objekt, ohne "
        "Markdown-Codefences, ohne Kommentar davor oder danach. Schlüssel:\n"
        '  "kurzbeschreibung": HTML-String mit GENAU '
        f"{b.kurzbeschreibung.p_count} <p>…</p>-Absätzen, insgesamt "
        f"{b.kurzbeschreibung.min_words}–{b.kurzbeschreibung.max_words} Wörter "
        "(reiner Text ohne Tags gezählt). Keine anderen HTML-Tags.\n"
        '  "beschreibung": HTML-String mit GENAU '
        f"{b.beschreibung.p_count} <p>…</p>-Absätzen, insgesamt "
        f"{b.beschreibung.min_words}–{b.beschreibung.max_words} Wörter. Der LETZTE Absatz "
        "MUSS den Authentizitäts-Schlusssatz enthalten (siehe Vorgabe im User-Prompt). "
        "Keine anderen HTML-Tags.\n"
        '  "titel_tag": reiner Text, höchstens '
        f"{b.titel_tag.max_chars} Zeichen INKLUSIVE des Pflicht-Suffixes "
        f"'{b.titel_tag.must_end_with}', mit dem der Titel enden MUSS.\n"
        '  "meta_description": reiner Text, '
        f"{b.meta_description.min_chars}–{b.meta_description.max_chars} Zeichen.\n"
        '  "faq": Array aus '
        f"{b.faq.min_pairs}–{b.faq.max_pairs} Objekten, je {{\"frage\": …, \"antwort\": …}} "
        "auf Deutsch. Verwende in Fragen/Antworten NIEMALS die Zeichenfolgen '||' oder "
        "'##'.\n"
    )


def _facts_block(facts: SkuFacts) -> str:
    lines: list[str] = []
    for col, label in _FACT_LABELS:
        val = (facts.row.get(col) or "").strip()
        if val:
            lines.append(f"- {label}: {val}")
    lines.append(f"- Hersteller: {facts.hersteller}")
    for attr_name, intake_field in C.TRANSCEIVER_ATTRIBUTES:
        val = (facts.row.get(intake_field) or "").strip()
        if val:
            lines.append(f"- {attr_name}: {val}")
    return "\n".join(lines)


def build_user_prompt(facts: SkuFacts, rules: Rules, feedback: list[str] | None = None) -> str:
    closer = required_closer(rules, facts.hersteller)
    parts = [
        "Erstelle den Produktinhalt für folgenden Artikel. Verwende ausschließlich die "
        "angegebenen Fakten; erfinde keine technischen Spezifikationen.\n",
        _facts_block(facts),
        "",
        f"Der Authentizitäts-Schlusssatz im letzten Beschreibung-Absatz MUSS exakt die "
        f"Zeichenfolge '{closer}' enthalten, unmittelbar gefolgt von einem deutschen "
        f"Substantiv (z. B. '{closer}Transceiver' oder '{closer}Modul').",
    ]
    if feedback:
        parts += [
            "",
            "Dein vorheriger Entwurf hat folgende verbindliche Vorgaben NICHT erfüllt. "
            "Korrigiere ALLE Punkte und gib erneut das vollständige JSON-Objekt aus:",
            *(f"- {f}" for f in feedback),
        ]
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Response parsing                                                             #
# --------------------------------------------------------------------------- #
_FENCE_RE = re.compile(r"^```[a-zA-Z0-9]*\n?|\n?```$")
_SEP_RE = re.compile(r"\|\||##|::|;;")
_WS_RE = re.compile(r"\s+")


def _oneline(text: str) -> str:
    """Collapse all whitespace (incl. newlines) to single spaces; trim ends.

    Keeps each CSV cell on one physical line so the draft writer stays simple and the
    file round-trips cleanly through read_intake. Does not affect word counts.
    """
    return _WS_RE.sub(" ", text).strip()


def _sanitize_faq_text(text: str) -> str:
    """Neutralize FAQ separator tokens and newlines inside a question/answer."""
    return _oneline(_SEP_RE.sub(" - ", text))


def _strip_fences(text: str) -> str:
    t = text.strip()
    t = _FENCE_RE.sub("", t)
    return _FENCE_RE.sub("", t).strip()


def parse_response(raw: str) -> tuple[dict[str, str], list[FaqPair], str]:
    """Parse a model JSON response into (content_fields, faq_pairs, canonical_faq_cell).

    Raises GenerateError if no JSON object can be recovered.
    """
    text = _strip_fences(raw)
    data = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                data = json.loads(m.group(0))
            except json.JSONDecodeError:
                data = None
    if not isinstance(data, dict):
        raise GenerateError("model response was not a JSON object.")

    pairs: list[FaqPair] = []
    for item in (data.get("faq") or []):
        if not isinstance(item, dict):
            continue
        q = _sanitize_faq_text(str(item.get("frage") or item.get("question") or ""))
        a = _sanitize_faq_text(str(item.get("antwort") or item.get("answer") or ""))
        if q and a:
            pairs.append(FaqPair(question=q, answer=a))

    faq_cell = C.FAQ_PAIR_SEP.join(
        f"{p.question}{C.FAQ_QA_SEP}{p.answer}" for p in pairs
    )

    fields = {
        "Kurzbeschreibung": _oneline(str(data.get("kurzbeschreibung") or "")),
        "Beschreibung": _oneline(str(data.get("beschreibung") or "")),
        "TitelTag": _oneline(str(data.get("titel_tag") or "")),
        "MetaDescription": _oneline(str(data.get("meta_description") or "")),
        "FAQ": faq_cell,
    }
    return fields, pairs, faq_cell


# --------------------------------------------------------------------------- #
# Generation with bounded retry                                                #
# --------------------------------------------------------------------------- #
@dataclass
class SkuResult:
    sku: str
    ok: bool
    attempts: int
    issues: list[str] = field(default_factory=list)
    fields: dict[str, str] = field(default_factory=dict)  # the 5 CONTENT_COLUMNS
    kurz_words: int = 0
    besch_words: int = 0
    faq_pairs: int = 0


class Generator:
    def __init__(
        self,
        rules: Rules,
        *,
        completer: Completer,
        model: str = DEFAULT_MODEL,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.rules = rules
        self.completer = completer
        self.model = model
        self.max_retries = max(1, max_retries)
        self._system = build_system_prompt(rules)

    def generate_one(self, facts: SkuFacts) -> SkuResult:
        feedback: list[str] | None = None
        last_fields: dict[str, str] = {c: "" for c in CONTENT_COLUMNS}
        last_issues: list[str] = ["no successful generation attempt"]
        last_pairs: list[FaqPair] = []

        for attempt in range(1, self.max_retries + 1):
            user = build_user_prompt(facts, self.rules, feedback)
            raw = self.completer(self._system, user)
            try:
                fields, pairs, _cell = parse_response(raw)
            except GenerateError as e:
                feedback = [f"Ungültige Ausgabe: {e} Gib NUR das JSON-Objekt aus."]
                last_issues = [str(e)]
                continue

            issues = content_issues(
                self.rules,
                hersteller=facts.hersteller,
                kurzbeschreibung=fields["Kurzbeschreibung"],
                beschreibung=fields["Beschreibung"],
                titel_tag=fields["TitelTag"],
                meta_description=fields["MetaDescription"],
                faq_pair_count=len(pairs),
            )
            last_fields, last_issues, last_pairs = fields, issues, pairs
            if not issues:
                return SkuResult(
                    sku=facts.sku, ok=True, attempts=attempt, issues=[],
                    fields=fields,
                    kurz_words=word_count(fields["Kurzbeschreibung"]),
                    besch_words=word_count(fields["Beschreibung"]),
                    faq_pairs=len(pairs),
                )
            feedback = issues

        return SkuResult(
            sku=facts.sku, ok=False, attempts=self.max_retries, issues=last_issues,
            fields=last_fields,
            kurz_words=word_count(last_fields.get("Kurzbeschreibung", "")),
            besch_words=word_count(last_fields.get("Beschreibung", "")),
            faq_pairs=len(last_pairs),
        )


# --------------------------------------------------------------------------- #
# Draft intake writer                                                          #
# --------------------------------------------------------------------------- #
def merge_fields(row: dict[str, str], fields: dict[str, str]) -> dict[str, str]:
    """Return a copy of the intake row with the five content columns filled."""
    merged = dict(row)
    for col in CONTENT_COLUMNS:
        merged[col] = fields.get(col, "")
    return merged


def write_draft(path: str | Path, rows: list[dict[str, str]]) -> None:
    """Write a draft intake CSV (UTF-8 BOM, CRLF, every data cell double-quoted).

    Matches the `new-intake` template format so the draft round-trips through
    `read_intake` unchanged.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["﻿" + ",".join(INTAKE_COLUMNS)]
    for row in rows:
        cells = [
            '"' + (row.get(c, "") or "").replace('"', '""') + '"'
            for c in INTAKE_COLUMNS
        ]
        lines.append(",".join(cells))
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")


# --------------------------------------------------------------------------- #
# Anthropic-backed completer (the only network code path)                      #
# --------------------------------------------------------------------------- #
def make_anthropic_completer(
    model: str = DEFAULT_MODEL,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> Completer:
    """Build a completer backed by the Anthropic Messages API.

    Imports `anthropic` lazily so the core install (build/validate) needs no SDK.
    Raises GenerateError with an actionable message if the SDK or API key is missing.
    """
    try:
        import anthropic
    except ImportError as e:
        raise GenerateError(
            "The 'anthropic' package is required for `hexcat generate`. "
            "Install it with:  pip install 'hexcat[generate]'"
        ) from e

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise GenerateError(
            "ANTHROPIC_API_KEY is not set. Export your Anthropic API key before running "
            "`hexcat generate`."
        )

    client = anthropic.Anthropic()

    def complete(system: str, user: str) -> str:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            block.text for block in resp.content
            if getattr(block, "type", None) == "text"
        )

    return complete
