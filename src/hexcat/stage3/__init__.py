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

# Template flow (still live): read the verified ledger + emit the $0 in-session content
# sidecar. The package.py *writer* (build_package/write_package/compose_beschreibung) is
# RETIRED from the live path — Stage-3 packages are now assembled by the canonical
# `assemble_bundle` via `reconcile_content` so there is exactly ONE output contract.
from .package import (
    SkuFacts,
    read_ledger_facts,
    write_content_template,
)
from .reconcile import (
    ReconcileError,
    entry_to_intake,
    physical_formfaktor,
    reconcile_content,
)

__all__ = [
    # template flow
    "SkuFacts",
    "read_ledger_facts",
    "write_content_template",
    # converged build flow
    "reconcile_content",
    "entry_to_intake",
    "physical_formfaktor",
    "ReconcileError",
]
