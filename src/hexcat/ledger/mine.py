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


def mine_html_cards(html: str, spec: LedgerSpec) -> list[MinedPN]:
    """Extract (pn, description) from a product-card GRID (no <table>).

    Each product is a card `div[wire:key^="product-"]`. The authoritative SKU is the only
    place it is printed as the manufacturer's own product identity: the card's
    `<a title="{card_title_prefix}{CODE}">` deep link. The description is the card's `<p>`
    whose class contains `desc_class_contains` (the line-clamped blurb). We walk cards in
    document order, dedup, and guard every code with the brand's pn_token so a stray link
    cannot leak a non-SKU into the ledger.
    """
    from bs4 import BeautifulSoup

    hspec = spec.mine.html
    if hspec is None or hspec.mode != "card":
        raise MineError("mine_html_cards called without mine.html.mode == 'card'.")
    soup = BeautifulSoup(html, "html.parser")
    token_re = spec.mine.pn_token_re
    prefix = hspec.card_title_prefix

    mined: list[MinedPN] = []
    seen: set[str] = set()
    found_card = False
    for card in soup.find_all("div", attrs={"wire:key": True}):
        if not str(card.get("wire:key", "")).startswith("product-"):
            continue
        found_card = True
        a = card.find("a", title=lambda t: bool(t) and t.startswith(prefix))
        if not a:
            continue
        pn = a["title"][len(prefix):].strip()
        if not token_re.match(pn) or pn in seen:
            continue
        desc = ""
        for cand in card.find_all("p"):
            cls = " ".join(cand.get("class", []))
            if hspec.desc_class_contains and hspec.desc_class_contains in cls:
                desc = _clean(cand.get_text(" ", strip=True))
                break
        seen.add(pn)
        mined.append(MinedPN(pn=pn, description=desc))

    if not found_card:
        raise MineError(
            "No product cards found (no div[wire:key^='product-']). "
            "The card-grid layout may have changed."
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
        pn = pdf_cfg.rewrite_sku(m.group(0))  # repair footnote-superscript contamination
        if pn not in seen:
            seen.add(pn)
            mined.append(MinedPN(pn=pn, description=""))
    return mined


def _mine_pdf_token_columns(data: bytes, pdf_cfg) -> list[MinedPN]:
    """Column-aware token mining: read the SKU *column* by word x-band, not the whole row.

    pdfplumber's table extractor returns empty cells on borderless ordering tables, and a flat
    text scan cannot tell an authoritative SKU-column token (FN-TRAN-SFP-1BU40, x0≈179) from a
    SKU-shaped string bleeding through Description prose (FN-TRAN-1BU40, x0≈480). So we bucket
    every word into rows by its rounded `top`, split each row at the Description x-band, and keep
    a SKU only when the SKU-column text is *exactly* one SKU token. The Description-column text is
    carried along to drive the universal V5 cable classifier. Distinct tokens that differ only by
    a trailing '+' (FN-TRAN-QSFPDD-DR4 vs …-DR4+) stay distinct — no silent collision.
    """
    import io
    from collections import defaultdict

    import pdfplumber

    trans = {0x2010: "-", 0x2011: "-", 0x2012: "-", 0x2013: "-", 0x00AD: "-", 0x00A0: " "}

    def tr(s: str) -> str:
        return (s or "").translate(trans)

    sku_re = pdf_cfg.sku_re
    sku_hdr, desc_hdr = pdf_cfg.sku_column, pdf_cfg.desc_column
    top_max = pdf_cfg.header_top_max
    mined: list[MinedPN] = []
    seen: set[str] = set()
    found_scope = False

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text = tr(page.extract_text() or "")
            if pdf_cfg.scope_heading and pdf_cfg.scope_heading not in text:
                continue
            found_scope = True
            words = page.extract_words()
            hdr = {
                tr(w["text"]): w["x0"]
                for w in words
                if tr(w["text"]) in (sku_hdr, desc_hdr) and w["top"] < top_max
            }
            if sku_hdr not in hdr:
                continue
            sku_x = hdr[sku_hdr]
            desc_x = hdr.get(desc_hdr, sku_x + 1e9)
            bytop: dict[int, list[dict]] = defaultdict(list)
            for w in words:
                bytop[round(w["top"])].append(w)
            for top in sorted(bytop):
                row = sorted(bytop[top], key=lambda w: w["x0"])
                sku_txt = " ".join(
                    tr(w["text"]) for w in row if sku_x - 8 <= w["x0"] < desc_x - 8
                ).strip()
                desc_txt = re.sub(
                    r"\s+", " ",
                    " ".join(tr(w["text"]) for w in row if w["x0"] >= desc_x - 8),
                ).strip()
                m = sku_re.fullmatch(sku_txt)
                if not m:
                    continue
                pn = pdf_cfg.rewrite_sku(m.group(0))  # repair footnote-superscript contamination
                if pn in seen:
                    continue
                seen.add(pn)
                mined.append(MinedPN(pn=pn, description=desc_txt))

    if not found_scope:
        raise MineError(
            f"PDF column scan found no pages containing scope_heading "
            f"{pdf_cfg.scope_heading!r}. The datasheet layout may have changed."
        )
    if not mined:
        raise MineError(
            f"PDF column scan found no SKU-column tokens under header {sku_hdr!r}. "
            "The datasheet layout may have changed."
        )
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
                # The matched noun (the text before the '(SKU)') is the manufacturer's own
                # label for this SKU. Carrying it as the description lets the universal V5 rule
                # reclassify 'DAC (sku)'/'AOC (sku)' callouts to DAC/AOC Kabel uniformly with
                # every other brand, while 'Transceiver (sku)' keeps the chapter form factor.
                noun = m.group(0)[: m.start(1) - m.start(0)].rstrip(" (")
                mined.append(MinedPN(pn=pn, description=noun, unterkategorie=current))
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
    if pdf_cfg.mode == "section":
        return _mine_pdf_section(_pdf_pages_text(data), pdf_cfg, spec)
    # token mode: column-aware when a SKU column is configured (isolates the authoritative SKU
    # column from Description prose — kills description-bleed phantoms at the root), else the
    # legacy flat text scan.
    if pdf_cfg.sku_column:
        return _mine_pdf_token_columns(data, pdf_cfg)
    return _mine_pdf_token(_pdf_pages_text(data), pdf_cfg)


def mine_source(fetched: FetchResult, spec: LedgerSpec) -> list[MinedPN]:
    """Dispatch on content type and return the mined PN set for one source."""
    if fetched.content_type == "html":
        html = fetched.read_text()
        if spec.mine.html is not None and spec.mine.html.mode == "card":
            return mine_html_cards(html, spec)
        return mine_html(html, spec)
    return mine_pdf(fetched.read_bytes(), spec)
