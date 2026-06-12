"""Stage-1 ledger engine — orchestrate one datasheet source into ledger data.

Per source: fetch (cheapest tier) -> mine the ordering table -> classify each canonical
PN into the operator Unterkategorie -> (optionally) normalize a supplied live/feed PN list
against the datasheet for new-vs-existing tagging + PN-Korrekturen. Pure data out; the
workbook writer renders it. Deterministic, $0, no model calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .fetch import FetchResult, fetch_datasheet, source_id_from_url
from .mine import mine_source
from .normalize import normalize_pn
from .spec import LedgerSpec, load_ledger_spec


def _pack_notiz(m) -> str:
    """Flag a pack-of-N SKU (e.g. FN-TRAN-SXI-4PACK) so the operator knows it is not a single
    unit. Detected from the manufacturer's own '-4PACK' suffix or 'Pack of four' description."""
    desc = (m.description or "").lower()
    if "4pack" in m.pn.upper() or "pack of four" in desc:
        return "Viererpack (Pack of four) — Mengeneinheit beachten"
    return ""


@dataclass(frozen=True)
class Source:
    gruppe: str
    datasheet: str
    url: str

    @property
    def source_id(self) -> str:
        return source_id_from_url(self.url)

    @property
    def confirmed_via(self) -> str:
        return f"{self.datasheet} ({self.source_id.upper()})"


@dataclass
class LedgerRow:
    pn: str
    hauptkategorie: str
    unterkategorie: str
    quelle: str
    quell_url: str
    verifiziert_am: str
    notiz: str = ""


@dataclass
class CorrectionRow:
    raw: str
    canonical: str
    tab: str
    problem: str
    confirmed_via: str


@dataclass
class SourceResult:
    source: Source
    tier: str
    rows: list[LedgerRow]
    corrections: list[CorrectionRow]
    flagged: list[str] = field(default_factory=list)   # unconfirmed PNs (not forced)
    mined_count: int = 0
    new_count: int | None = None     # None when no live list supplied
    live_matched: int = 0

    @property
    def status(self) -> str:
        if self.new_count is None:
            return f"FERTIG ({self.mined_count} gefunden)"
        return f"FERTIG ({self.new_count} neu)"

    def coverage(self) -> dict[str, int]:
        cov: dict[str, int] = {}
        for r in self.rows:
            cov[r.unterkategorie] = cov.get(r.unterkategorie, 0) + 1
        return cov


def read_sources_from_workbook(xlsx_path: str | Path) -> list[Source]:
    """Read the Quellen-Tracker sheet (the operator-curated seed list)."""
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb["Quellen-Tracker"]
    sources: list[Source] = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # header
        gruppe, datasheet, url = (row + (None, None, None))[:3]
        if not url or not isinstance(url, str) or not url.lower().startswith("http"):
            continue  # skip rows without a single resolvable URL (e.g. "2 DS")
        sources.append(Source(gruppe=str(gruppe or ""), datasheet=str(datasheet or ""), url=url))
    return sources


def load_live_pns(path: str | Path | None) -> list[str] | None:
    """Load an optional single-column CSV of existing PNs. Absent -> None (never blocks)."""
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    import csv

    out: list[str] = []
    with p.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue
            val = row[0].strip()
            if val and val.lower() not in ("artikelnummer", "part number", "pn"):
                out.append(val)
    return out


def run_source(
    source: Source,
    spec: LedgerSpec | None = None,
    *,
    verified_date: str | None = None,
    live_pns: list[str] | None = None,
    fetched: FetchResult | None = None,
) -> SourceResult:
    spec = spec or load_ledger_spec()
    vdate = verified_date or date.today().isoformat()
    fetched = fetched or fetch_datasheet(source.url, source.source_id)

    mined_all = mine_source(fetched, spec)
    # Flag-don't-emit: drop non-transceiver tokens (licenses, RTUs, converter adapters) that do
    # not fit the locked-22 taxonomy. Symmetric with the verifier (see verify_ledger), so the
    # emitted set still equals the independently re-derived authoritative set (V7/V8 honest).
    excluded_pns: list[str] = []
    mined = []
    for m in mined_all:
        reason = spec.is_excluded(m.pn, m.description)
        if reason:
            excluded_pns.append(m.pn)
        else:
            mined.append(m)
    canonical_set = {m.pn for m in mined}

    rows: list[LedgerRow] = []
    for m in mined:
        # Universal V5 rule: the manufacturer DESCRIPTION decides DAC/AOC/MPO (identical across
        # brands); otherwise the section-mode chapter hint (form factor where the PN is opaque);
        # otherwise the per-brand PN-substring rules.
        uk = spec.resolve_unterkategorie(m.pn, description=m.description, hint=m.unterkategorie)
        rows.append(
            LedgerRow(
                pn=m.pn,
                hauptkategorie=spec.hauptkategorie,
                unterkategorie=uk,
                quelle=source.datasheet,
                quell_url=source.url,
                verifiziert_am=vdate,
                notiz=_pack_notiz(m),
            )
        )

    corrections: list[CorrectionRow] = []
    flagged: list[str] = list(excluded_pns)  # non-transceivers flagged, not emitted
    new_count: int | None = None
    live_matched = 0

    if live_pns is not None:
        live_canonicals: set[str] = set()
        for raw in live_pns:
            res = normalize_pn(raw, canonical_set, spec)
            if res.is_correction and res.confirmed:
                corrections.append(
                    CorrectionRow(
                        raw=res.raw,
                        canonical=res.canonical,
                        tab=spec.classify_pn(res.canonical),
                        problem=res.problem,
                        confirmed_via=source.confirmed_via,
                    )
                )
            if res.confirmed:
                live_canonicals.add(res.canonical)
            elif res.is_correction:
                flagged.append(res.raw)  # changed but not datasheet-confirmed -> flag
        live_matched = len(live_canonicals & canonical_set)
        # Tag mined rows new-vs-existing.
        new_count = 0
        for r in rows:
            tag = "bereits im Katalog" if r.pn in live_canonicals else "neu"
            if r.pn not in live_canonicals:
                new_count += 1
            # Preserve any pack-of-N flag already set at mine time.
            r.notiz = f"{tag}; {r.notiz}" if r.notiz else tag

    return SourceResult(
        source=source,
        tier=fetched.tier,
        rows=rows,
        corrections=corrections,
        flagged=flagged,
        mined_count=len(mined),
        new_count=new_count,
        live_matched=live_matched,
    )
