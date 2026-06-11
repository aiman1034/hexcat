"""Phase 2 engine: facts-only skeleton intake, draft writing, and shared helpers.

HexCat is a ZERO-DOLLAR tool: it never makes a paid LLM API call. The German prose is
written by Claude Code in-session (under the operator's existing subscription), not by the
tool. This module owns the deterministic parts of that flow:

  * `read_skeleton`  — parse a facts-only intake CSV (content cells may be blank),
  * `merge_fields`   — fold authored content into a full intake row,
  * `write_draft`    — emit a draft intake CSV (the shape `hexcat build` consumes),
  * `soft_spec_flags`— advisory check for numeric specs in prose not backed by the facts,
  * `write_skeleton_template` — the `hexcat new-skeleton` emitter.

The actual content rules live in `content_checks.py` and are enforced by `hexcat validate`
(and `hexcat build`), so a draft that validates passes the build gate unchanged.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from ..config import Rules
from ..models import INTAKE_COLUMNS


class GenerateError(Exception):
    """Raised for skeleton/worksheet/draft problems. Message is operator-actionable."""


# Content-bearing intake columns authored by Claude (everything else is a fact).
CONTENT_COLUMNS = ("Kurzbeschreibung", "Beschreibung", "TitelTag", "MetaDescription", "FAQ")

FLAG_PREFIX = "[FLAG] "

_WS_RE = re.compile(r"\s+")


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
    Resolves vendor->Hersteller now (needed for the worksheet and the closer). Fails fast
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
                f"Run `hexcat new-skeleton` for the correct template."
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
# Soft safety check (non-blocking): spec tokens in prose not backed by facts   #
# --------------------------------------------------------------------------- #
_SPEC_RE = re.compile(
    r"\d+(?:[.,]\d+)?\s?(?:km|nm|µm|um|Gbit|Gigabit|GHz|MHz|dB|°C|G|W|m)\b",
    re.IGNORECASE,
)


def _norm(s: str) -> str:
    return _WS_RE.sub("", s).lower()


def soft_spec_flags(fields: dict[str, str], facts_row: dict[str, str]) -> list[str]:
    """Best-effort: flag numeric spec tokens in the prose not present in the facts.

    Purely advisory (never blocks the draft). Catches plausible hallucinated specs
    (e.g. a wavelength or reach the operator never supplied) for human review.
    """
    fact_cols = [k for k in INTAKE_COLUMNS if k not in CONTENT_COLUMNS]
    facts_blob = _norm(" ".join(facts_row.get(k, "") or "" for k in fact_cols))
    flags: list[str] = []
    seen: set[str] = set()
    for label in ("Kurzbeschreibung", "Beschreibung", "TitelTag", "MetaDescription"):
        for tok in _SPEC_RE.findall(fields.get(label, "")):
            key = _norm(tok)
            if key in seen or key in facts_blob:
                continue
            seen.add(key)
            flags.append(f"{label}: spec '{tok.strip()}' not found in the supplied facts.")
    return flags


# --------------------------------------------------------------------------- #
# Draft + skeleton writers                                                     #
# --------------------------------------------------------------------------- #
def merge_fields(row: dict[str, str], fields: dict[str, str]) -> dict[str, str]:
    """Return a copy of the intake row with the five content columns filled."""
    merged = dict(row)
    for col in CONTENT_COLUMNS:
        merged[col] = fields.get(col, "")
    return merged


def write_draft(path: str | Path, rows: list[dict[str, str]]) -> None:
    """Write a draft intake CSV (UTF-8 BOM, CRLF, every data cell double-quoted)."""
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


# A single commented example row for the facts-only skeleton (content cells blank).
_SKELETON_EXAMPLE = {
    "Artikelnummer": "# SFP-10G-SR",
    "Vendor": "Cisco",
    "KategorieEbene3": "SFP+",
    "Artikelname": "Cisco SFP-10G-SR 10G SFP+ Modul",
    "NettoVK": "120.50",
    "Formfaktor": "SFP+",
    "Geschwindigkeit": "10 Gigabit",
    "TransceiverTyp": "SR",
    "Faseranzahl": "2",
    "Fasertyp": "Multimode",
    "Anschlusstyp": "LC Duplex",
    "Wellenlaenge": "850 nm",
    "Anwendung": "Rechenzentrum",
    "Reichweite": "300 m",
    "DOMUnterstuetzung": "Ja",
    "Betriebstemperatur": "0 bis 70 Grad C",
    "Standard": "IEEE 802.3ae",
    "Condition": "new",
}


def write_skeleton_template(path: str | Path) -> None:
    """Write a facts-only intake skeleton: header + one commented example, content blank.

    The five content columns (Kurzbeschreibung, Beschreibung, TitelTag, MetaDescription,
    FAQ) are intentionally empty — `hexcat worksheet` turns the facts into a fill surface
    that Claude Code completes in-session.
    """
    row = {c: "" for c in INTAKE_COLUMNS}
    row.update(_SKELETON_EXAMPLE)
    write_draft(path, [row])
