"""Mine candidate part numbers from a fetched datasheet — Stage 1, deterministic.

The ordering table is located structurally: the single table whose header row carries a
Product-Number column (per the spec's `pn_header_patterns`). The PN column yields the
canonical, orderable PNs as printed by the manufacturer — the single source of truth for
spelling. Variant suffixes (-RF/-WS/-CCL remanufactured/spare codes) live in prose, not in
a PN-column table, so this approach reproduces the operator's base orderable set exactly.

HTML is the pilot (C78-455693). PDF mining (Phase 4) is a second input front-end into the
SAME normalize -> classify -> dedup -> workbook flow, not a new pipeline. A datasheet PDF is
turned into PNs by pdfplumber text extraction under one of two per-brand structural modes
(config in mine.pdf, never code):

  token    — flat SKU scan over the ordering section (e.g. Fortinet's "Ordering Information").
  section  — walk form-factor chapters and read each chapter's transceiver-SKU callouts,
             tagging the form factor from the heading (e.g. HPE/Aruba's compatibility guide).
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
    # Form factor decided at mine time (section-mode PDFs read it from the chapter heading,
    # where the PN itself is opaque). None -> the engine classifies from the PN via spec rules.
    unterkategorie: str | None = None


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


def _pdf_pages_text(data: bytes) -> list[str]:
    """Per-page text via pdfplumber. Normalizes the unicode hyphen/non-breaking variants
    that manufacturer PDFs sprinkle into SKUs (U+2010/2011/00AD) to a plain ASCII '-' so a
    single SKU regex matches regardless of the typesetter's dash choice.
    """
    import io

    import pdfplumber

    trans = {0x2010: "-", 0x2011: "-", 0x2012: "-", 0x2013: "-", 0x00AD: "-", 0x00A0: " "}
    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            pages.append((page.extract_text() or "").translate(trans))
    return pages


def _collapse_runs(text: str) -> str:
    """Collapse any run of a repeated char to one ('SSFFPP++ MMoodduulleess' -> 'SFP+ Moduls').
    Lossy for genuine double letters, so used ONLY to compare a bold-doubled heading line
    against a configured heading that is collapsed the same way — both sides normalize
    identically, so the comparison is exact despite uneven rendering."""
    return re.sub(r"(.)\1+", r"\1", text)


def _mine_pdf_token(pages: list[str], pdf_cfg) -> list[MinedPN]:
    """Flat SKU scan over the document text, optionally scoped to the manufacturer's own
    ordering section (the page run whose text carries `scope_heading`). Repairs SKUs split
    across a line break ('FN-TRAN-SFP-1BD40\\n***'), dedups, and drops any token that is a
    strict prefix of another kept token (typeset truncation artifact)."""
    if pdf_cfg.scope_heading:
        text = "\n".join(p for p in pages if pdf_cfg.scope_heading in p)
    else:
        text = "\n".join(pages)
    if not text.strip():
        raise MineError(
            f"PDF token scan found no pages containing scope_heading "
            f"{pdf_cfg.scope_heading!r}. The datasheet layout may have changed."
        )
    text = re.sub(r"-\s*\n\s*", "-", text)   # rejoin hyphen-broken SKUs
    text = text.replace("\n", " ")
    mined: list[MinedPN] = []
    seen: set[str] = set()
    for m in pdf_cfg.sku_re.finditer(text):
        pn = m.group(0)
        if pn not in seen:
            seen.add(pn)
            mined.append(MinedPN(pn=pn, description=""))
    return mined


def _mine_pdf_section(pages: list[str], pdf_cfg, spec: "LedgerSpec") -> list[MinedPN]:
    """Walk form-factor CHAPTERS in document order; within each, take transceiver SKUs from
    their model entries and tag them with the chapter's form factor. A SKU is only kept where
    it is the manufacturer's own '<noun> (SKU)' callout (e.g. 'Transceiver (JL310A)'), which
    sits in the model listing — NOT in the switch-compatibility tables — so switch SKUs and
    software part numbers stay out. The chapter heading supplies the Unterkategorie, since the
    Aruba SKU itself is opaque to form factor.

    Line-oriented: a chapter is recognized only on a heading LINE whose run-collapsed,
    casefolded form contains a configured chapter heading collapsed the SAME way — so the
    bold double-rendering ('SSFFPP++  MMoodduulleess') and the plain configured text
    ('SFP+ Modules') normalize to the same key and compare exactly. Body lines under the
    current chapter then yield their '<noun> (SKU)' callouts."""
    ctx_re = pdf_cfg.context_re
    if ctx_re is None:
        raise MineError("section mode requires `context_noun` in the PDF spec.")
    collapse = pdf_cfg.collapse_bold_doubling

    def norm(s: str) -> str:
        return (_collapse_runs(s) if collapse else s).casefold()

    # Pre-normalize the configured chapter headings once (longest first, so a more specific
    # heading like 'QSFP28 …' wins over a prefix it contains).
    chapters = sorted(
        ((norm(h), ff) for h, ff in pdf_cfg.chapters.items()),
        key=lambda kv: len(kv[0]),
        reverse=True,
    )
    current: str | None = None
    mined: list[MinedPN] = []
    seen: set[str] = set()
    for page in pages:
        for line in page.split("\n"):
            # A chapter switch is honored only on a *bold* heading line. Under bold
            # double-rendering, a real heading line is fully doubled, so collapsing it
            # changes it; the plain TOC entry ('QSFP-DD modules' on the contents page) is
            # NOT doubled and collapses to itself — excluding it keeps the contents page
            # from mis-setting the active form factor for the chapters that follow.
            is_heading_line = (not collapse) or (_collapse_runs(line) != line)
            cmp_line = norm(line)
            heading_hit = (
                next((ff for key, ff in chapters if key and key in cmp_line), None)
                if is_heading_line
                else None
            )
            if heading_hit is not None:
                current = heading_hit
                continue  # the heading line itself carries no model-entry SKU callout
            if current is None:
                continue  # front matter / TOC before the first form-factor chapter
            for m in ctx_re.finditer(line):
                pn = m.group(1)
                if pn in seen:
                    continue
                seen.add(pn)
                mined.append(MinedPN(pn=pn, description="", unterkategorie=current))
    if not mined:
        raise MineError(
            "PDF section scan found no transceiver SKUs (no chapter heading + "
            f"'{pdf_cfg.context_noun} (SKU)' callout matched). Layout may have changed."
        )
    return mined


def mine_pdf(data: bytes, spec: LedgerSpec) -> list[MinedPN]:
    """Mine PNs from a datasheet PDF per the brand's `mine.pdf` config (token | section)."""
    pdf_cfg = getattr(spec.mine, "pdf", None)
    if pdf_cfg is None:
        raise MineError(
            f"No PDF mining config for brand {spec.brand!r} (mine.pdf is unset). "
            "Add a mine.pdf block to the ledger spec to enable PDF extraction."
        )
    pages = _pdf_pages_text(data)
    if pdf_cfg.mode == "section":
        return _mine_pdf_section(pages, pdf_cfg, spec)
    return _mine_pdf_token(pages, pdf_cfg)


def mine_source(fetched: FetchResult, spec: LedgerSpec) -> list[MinedPN]:
    """Dispatch on content type and return the mined PN set for one source."""
    if fetched.content_type == "html":
        return mine_html(fetched.read_text(), spec)
    return mine_pdf(fetched.read_bytes(), spec)
