"""Stage 1/2 ledger engine — PHASE 3 (not implemented this session).

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
"""
