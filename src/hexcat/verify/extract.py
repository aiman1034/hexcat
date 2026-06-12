"""Authoritative-locus extraction — the verifier's independent second path (method A).

This reads the raw PDF bytes by COLUMN GEOMETRY (word x-bands), not by the miner's flat text
scan, so it can answer two questions the flat scan cannot:

  * Where did a SKU-shaped token physically come from — the authoritative SKU column of the
    ordering table, or Description prose / a cross-reference? (powers V2 provenance, V6 switch
    exclusion)
  * What does the manufacturer's own description say about it? (powers V5 classification)

It deliberately shares NO code path with src/hexcat/ledger/mine.py's token scanner, so a
disagreement between the two (V7) is a genuine cross-check rather than a tautology.
"""
from __future__ import annotations

import io
import re
from collections import defaultdict
from dataclasses import dataclass

# Unicode hyphen / non-breaking-space normalization — identical to the miner so both sides
# compare the same canonical bytes (a SKU is never split by which dash the typesetter chose).
_TRANS = {0x2010: "-", 0x2011: "-", 0x2012: "-", 0x2013: "-", 0x00AD: "-", 0x00A0: " "}


def normalize_text(s: str) -> str:
    return (s or "").translate(_TRANS)


def ws_normalize(s: str) -> str:
    """Collapse all whitespace runs to single spaces (for verbatim round-trip comparison)."""
    return re.sub(r"\s+", " ", normalize_text(s)).strip()


@dataclass(frozen=True)
class SourceToken:
    """One SKU-shaped token found in the raw source, tagged with where it came from."""
    pn: str
    description: str
    locus: str          # "sku_column" | "description" | "flat"
    page: int           # 1-based page index it was found on


def _page_texts(data: bytes) -> list[str]:
    import pdfplumber

    out: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            out.append(normalize_text(page.extract_text() or ""))
    return out


def raw_source_text(data: bytes) -> str:
    """Whitespace-normalized full-document text — the corpus V1 round-trips every SKU against."""
    return ws_normalize("\n".join(_page_texts(data)))


def extract_authoritative_html(html: str, spec) -> list[SourceToken]:
    """HTML second path: take SKUs from the ordering table's Product-Number COLUMN (locus
    'pn_column', authoritative) and tag any SKU-shaped token found in a NON-PN cell as locus
    'description' (prose bleed). Independent of the miner's dedup/order so V7 is a real check.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    token_re = spec.mine.pn_token_re
    tokens: list[SourceToken] = []

    def cell_text(c) -> str:
        return ws_normalize(c.get_text(" ", strip=True))

    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        if not trs:
            continue
        header = [cell_text(c) for c in trs[0].find_all(["td", "th"])]
        pn_cols = [i for i, h in enumerate(header) if spec.mine.is_pn_header(h)]
        if not pn_cols:
            continue
        pn_col = pn_cols[0]
        desc_col = 0 if pn_col != 0 else (1 if len(header) > 1 else 0)
        for tr in trs[1:]:
            cells = [cell_text(c) for c in tr.find_all(["td", "th"])]
            if pn_col >= len(cells):
                continue
            pn = cells[pn_col]
            desc = cells[desc_col] if desc_col < len(cells) and desc_col != pn_col else ""
            if token_re.match(pn):
                tokens.append(SourceToken(pn, desc, "pn_column", 1))
    return tokens


def extract_authoritative_html_cards(html: str, spec) -> list[SourceToken]:
    """HTML card-grid second path (locus 'card', authoritative).

    Deliberately re-derives the SKU set by RAW-STRING geometry — split the document into card
    chunks at each `wire:key="product-"` marker, then regex the card's `<a title="{prefix}{CODE}">`
    deep link and its line-clamped `<p>` description out of the chunk. This shares no DOM-tree /
    dedup code with mine.mine_html_cards (which walks the parsed BeautifulSoup tree), so a
    disagreement (V7) is a genuine cross-check rather than a tautology.
    """
    hspec = getattr(spec.mine, "html", None)
    if hspec is None or hspec.mode != "card":
        return []
    token_re = spec.mine.pn_token_re
    title_re = re.compile(r'title="' + re.escape(hspec.card_title_prefix) + r'([^"]+)"')
    desc_re = re.compile(
        r'<p[^>]*class="[^"]*' + re.escape(hspec.desc_class_contains) + r'[^"]*"[^>]*>(.*?)</p>',
        re.S,
    )
    tokens: list[SourceToken] = []
    chunks = re.split(r'wire:key="product-', html)[1:]
    for chunk in chunks:
        tm = title_re.search(chunk)
        if not tm:
            continue
        pn = tm.group(1).strip()
        if not token_re.match(pn):
            continue
        dm = desc_re.search(chunk)
        desc = ws_normalize(re.sub(r"<[^>]+>", " ", dm.group(1))) if dm else ""
        tokens.append(SourceToken(pn, desc, "card", 1))
    return tokens


def _collapse_runs(text: str) -> str:
    return re.sub(r"(.)\1+", r"\1", text)


def extract_authoritative_section(data: bytes, pdf_cfg) -> list[SourceToken]:
    """Section-mode second path: walk the form-factor chapters and keep each chapter's own
    '<noun> (SKU)' optic callouts (locus 'callout', description = the noun). Independent
    re-derivation of the same authoritative set the section miner produces, so V1/V5/V6/V8
    stay meaningful without a flat scan dragging in the 220-page switch matrix (which would
    'cry wolf' with hundreds of false missings).
    """
    ctx_re = pdf_cfg.context_re
    if ctx_re is None:
        return []
    collapse = pdf_cfg.collapse_bold_doubling

    def norm(s: str) -> str:
        return (_collapse_runs(s) if collapse else s).casefold()

    chapters = sorted(
        ((norm(h), ff) for h, ff in pdf_cfg.chapters.items()),
        key=lambda kv: len(kv[0]),
        reverse=True,
    )
    tokens: list[SourceToken] = []
    current: str | None = None
    for pidx, page in enumerate(_page_texts(data), start=1):
        for line in page.split("\n"):
            is_heading_line = (not collapse) or (_collapse_runs(line) != line)
            cmp_line = norm(line)
            heading_hit = (
                next((ff for key, ff in chapters if key and key in cmp_line), None)
                if is_heading_line else None
            )
            if heading_hit is not None:
                current = heading_hit
                continue
            if current is None:
                continue
            for m in ctx_re.finditer(line):
                noun = m.group(0)[: m.start(1) - m.start(0)].rstrip(" (")
                tokens.append(SourceToken(m.group(1), noun, "callout", pidx))
    return tokens


def extract_authoritative(data: bytes, pdf_cfg) -> list[SourceToken]:
    """Re-derive the source's SKU tokens by column geometry.

    For a column-table PDF (sku_column configured), every word-row is split at the
    Description x-band: SKU-shaped tokens in the SKU band are locus 'sku_column' (authoritative);
    SKU-shaped tokens in the Description band are locus 'description' (prose bleed — phantoms).
    For a PDF without column config we fall back to a flat per-page scan tagged 'flat'.
    """
    import pdfplumber

    sku_re: re.Pattern[str] = pdf_cfg.sku_re
    scope = getattr(pdf_cfg, "scope_heading", None)
    sku_hdr = getattr(pdf_cfg, "sku_column", None)
    desc_hdr = getattr(pdf_cfg, "desc_column", None)
    top_max = getattr(pdf_cfg, "header_top_max", 200.0)

    tokens: list[SourceToken] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for pidx, page in enumerate(pdf.pages, start=1):
            text = normalize_text(page.extract_text() or "")
            if scope and scope not in text:
                continue
            if not sku_hdr:
                # No column geometry available — flat scan of the page text.
                for m in sku_re.finditer(text.replace("\n", " ")):
                    tokens.append(SourceToken(m.group(0), "", "flat", pidx))
                continue

            words = page.extract_words()
            hdr = {
                normalize_text(w["text"]): w["x0"]
                for w in words
                if normalize_text(w["text"]) in (sku_hdr, desc_hdr) and w["top"] < top_max
            }
            if sku_hdr not in hdr:
                continue
            sku_x = hdr[sku_hdr]
            desc_x = hdr.get(desc_hdr, sku_x + 1e9)  # no desc column -> everything is SKU band

            bytop: dict[int, list[dict]] = defaultdict(list)
            for w in words:
                bytop[round(w["top"])].append(w)
            for top in sorted(bytop):
                row = sorted(bytop[top], key=lambda w: w["x0"])
                sku_txt = " ".join(
                    normalize_text(w["text"]) for w in row
                    if sku_x - 8 <= w["x0"] < desc_x - 8
                ).strip()
                desc_txt = ws_normalize(
                    " ".join(normalize_text(w["text"]) for w in row if w["x0"] >= desc_x - 8)
                )
                m = sku_re.fullmatch(sku_txt)
                if m:
                    tokens.append(SourceToken(m.group(0), desc_txt, "sku_column", pidx))
                # Any SKU-shaped token sitting in the Description band is prose bleed.
                for dm in sku_re.finditer(desc_txt):
                    tokens.append(SourceToken(dm.group(0), desc_txt, "description", pidx))
    return tokens
