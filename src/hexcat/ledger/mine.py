"""Mine candidate part numbers from a fetched datasheet — Stage 1, deterministic.

The ordering table is located structurally: the single table whose header row carries a
Product-Number column (per the spec's `pn_header_patterns`). The PN column yields the
canonical, orderable PNs as printed by the manufacturer — the single source of truth for
spelling. Variant suffixes (-RF/-WS/-CCL remanufactured/spare codes) live in prose, not in
a PN-column table, so this approach reproduces the operator's base orderable set exactly.

HTML is implemented (the pilot, C78-455693). PDF mining is a clean stub (Tier-3 manual PDF
drop-in still caches; turning a PDF into rows needs a text/table extractor — Phase 3.1).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .fetch import FetchResult
from .spec import LedgerSpec


class MineError(Exception):
    """No ordering table could be located in the datasheet."""


@dataclass(frozen=True)
class MinedPN:
    pn: str
    description: str


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def mine_html(html: str, spec: LedgerSpec) -> list[MinedPN]:
    """Extract (pn, description) rows from the datasheet's ordering table."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    token_re = spec.mine.pn_token_re

    def cells(tr):
        return [_clean(c.get_text(" ", strip=True)) for c in tr.find_all(["td", "th"])]

    mined: list[MinedPN] = []
    seen: set[str] = set()
    found_table = False

    for table in soup.find_all("table"):
        rows = [cells(tr) for tr in table.find_all("tr")]
        if not rows:
            continue
        header = rows[0]
        pn_cols = [i for i, h in enumerate(header) if spec.mine.is_pn_header(h)]
        if not pn_cols:
            continue
        found_table = True
        pn_col = pn_cols[0]
        desc_col = 0 if pn_col != 0 else (1 if len(header) > 1 else 0)
        for row in rows[1:]:
            if pn_col >= len(row):
                continue
            pn = row[pn_col]
            if not pn or not token_re.match(pn):
                continue
            if pn in seen:  # dedup against itself within the run
                continue
            seen.add(pn)
            desc = row[desc_col] if desc_col < len(row) and desc_col != pn_col else ""
            mined.append(MinedPN(pn=pn, description=desc))

    if not found_table:
        raise MineError(
            "No ordering table found (no table header matched "
            f"{spec.mine.pn_header_patterns}). The datasheet layout may have changed."
        )
    return mined


def mine_pdf(data: bytes, spec: LedgerSpec) -> list[MinedPN]:  # pragma: no cover - stub
    raise NotImplementedError(
        "PDF datasheet mining is not implemented this session (pilot C78-455693 is HTML). "
        "A manual PDF drop-in caches fine; extracting its ordering table needs a PDF "
        "text/table parser (e.g. pdfplumber) — Phase 3.1."
    )


def mine_source(fetched: FetchResult, spec: LedgerSpec) -> list[MinedPN]:
    """Dispatch on content type and return the mined PN set for one source."""
    if fetched.content_type == "html":
        return mine_html(fetched.read_text(), spec)
    return mine_pdf(fetched.read_bytes(), spec)
