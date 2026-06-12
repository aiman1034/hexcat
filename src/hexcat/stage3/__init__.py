"""Stage 3 — the v5.0 JTL-Ameise import package generator.

The DONE-VERIFIED Stage-1 ledger is the spine; Stage 3 turns it into the operator's
byte-exact import deliverable. The format is fixed by the authoritative proof slice
(`Corrected 7 Part Numbers/Cisco_Audit_7SKUs_*.csv`): four CSV files per brand, UTF-8 BOM,
CRLF, comma-delimited (Prices is semicolon-delimited), FAQ embedded in the Beschreibung HTML.

Division of labour (HexCat hard rule — ZERO-DOLLAR, deterministic core, flag-don't-emit):
  * DETERMINISTIC (this module): all ledger-derivable fields — Artikelnummer, HAN,
    Hersteller, URL-Pfad, Kategorie Ebene 1/2/3, flags, Verkaufseinheit, Versandklasse,
    form-factor weight defaults, placeholder prices (+ PRICES-PENDING), and the
    Verification_Log scaffold seeded with each SKU's source URL.
  * IN-SESSION ($0, by Claude under Max — NEVER the tool, NEVER a paid API): the German
    prose (Artikelname, Kurzbeschreibung, Beschreibung incl. embedded FAQ, Titel-Tag,
    Meta-Description) and the per-SKU verified spec attribute VALUES — every claim
    round-tripped against the datasheet; anything unverifiable is omitted, not invented.
"""
from __future__ import annotations

from .package import (
    ATTR_COLUMNS,
    MAIN_COLUMNS,
    PLATFORM_COLUMNS,
    PRICES_COLUMNS,
    PackageResult,
    SkuContent,
    SkuFacts,
    build_package,
    compose_beschreibung,
    content_issues,
    read_content,
    read_ledger_facts,
    url_slug,
    write_content_template,
    write_package,
)

__all__ = [
    "MAIN_COLUMNS",
    "ATTR_COLUMNS",
    "PLATFORM_COLUMNS",
    "PRICES_COLUMNS",
    "SkuFacts",
    "SkuContent",
    "PackageResult",
    "build_package",
    "write_package",
    "read_ledger_facts",
    "read_content",
    "write_content_template",
    "compose_beschreibung",
    "content_issues",
    "url_slug",
]
