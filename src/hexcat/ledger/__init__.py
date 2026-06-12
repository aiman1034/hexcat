"""Stage 1/2 ledger engine — PHASE 3 (Stage 1 implemented; Cisco pilot).

The ledger is the operator's working data model and is **Excel-first, files-only**
(no database). Phase 3 builds it as one workbook per brand with five sheets:

    Fortschritt      — progress counters (existing-cleaned / newly-verified / total)
    Neue Artikel     — canonical record, one row per part number:
                       Artikelnummer | Hauptkategorie | Unterkategorie |
                       Quelle (Datasheet) | Quell-URL | Verifiziert am | Notiz
    Quellen-Tracker  — one row per datasheet/source:
                       Gruppe | Datasheet | URL | Status | Notiz
    PN-Korrekturen   — part-number corrections:
                       In Daten vorhanden | Korrekte PN | Tab | Problem |
                       bestätigt via Datasheet
    Familien-Audit   — coverage audit per family:
                       Bereich | Familie | Anzahl PNs | Status | Befund

Stage 1 (steps 1-7) mines/cleans/classifies/dedupes/audits part numbers across all
brands for one category; Stage 2 (step 8) exports one workbook per brand, one tab per
sub-category. Every part number carries its source datasheet + URL (the catalog-scale
1000% rule) — no part number without a source.

Dedup against the live catalog + ledger happens here, by reading the workbooks with
openpyxl — NOT via SQLite/Postgres. Implement with openpyxl in this package.

Phase 3 status: Stage 1 (fetch -> mine -> normalize -> classify -> dedup -> workbook) is
implemented and proven on the Cisco SFP+ Modules datasheet (C78-455693). PDF mining and
non-Cisco brand adapters remain stubs (Phase 3.1 / Phase 4).
"""
from .engine import (
    CorrectionRow,
    LedgerRow,
    Source,
    SourceResult,
    load_live_pns,
    read_sources_from_workbook,
    run_source,
)
from .export import export_skeleton
from .fetch import FetchError, FetchResult, fetch_datasheet, source_id_from_url
from .mine import MinedPN, mine_source
from .normalize import NormalizeResult, normalize_pn
from .spec import LedgerSpec, load_ledger_spec, verify_ledger_spec
from .workbook import build_workbook, write_workbook

__all__ = [
    "Source", "SourceResult", "LedgerRow", "CorrectionRow",
    "run_source", "read_sources_from_workbook", "load_live_pns",
    "fetch_datasheet", "FetchResult", "FetchError", "source_id_from_url",
    "mine_source", "MinedPN",
    "normalize_pn", "NormalizeResult",
    "LedgerSpec", "load_ledger_spec", "verify_ledger_spec",
    "build_workbook", "write_workbook",
    "export_skeleton",
]
