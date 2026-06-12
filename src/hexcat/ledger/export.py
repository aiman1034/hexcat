"""Thin hand-off seam: Neue Artikel ledger rows -> a Stage-3 skeleton intake CSV.

Seeds the existing `new-skeleton` flow with discovered, classified, deduped PNs so the
operator doesn't re-type them. Maps ONLY identity facts — Artikelnummer, Vendor=Cisco,
KategorieEbene3 (= Unterkategorie mapped to the locked-22 token), and SourceURLs (the
datasheet URL for provenance). Specs and prose stay blank — that is Stage 3 / in-session
work, never auto-authored here.
"""
from __future__ import annotations

import csv
from pathlib import Path

from ..models import INTAKE_COLUMNS
from .engine import SourceResult
from .spec import LedgerSpec, load_ledger_spec


def export_skeleton(results: list[SourceResult], out_path: str | Path,
                    spec: LedgerSpec | None = None) -> Path:
    spec = spec or load_ledger_spec()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(INTAKE_COLUMNS))
        w.writeheader()
        for res in results:
            for r in res.rows:
                row = {col: "" for col in INTAKE_COLUMNS}
                row["Artikelnummer"] = r.pn
                row["Vendor"] = spec.brand
                row["KategorieEbene3"] = spec.to_locked22(r.unterkategorie)
                row["SourceURLs"] = r.quell_url
                w.writerow(row)
    return out
