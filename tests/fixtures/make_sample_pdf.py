"""Generate the committed PDF mining fixture — sample_datasheet.pdf.

Run once to (re)produce the fixture; the test itself depends only on pdfplumber, never on
this generator. We build the PDF from raw bytes (no reportlab/fpdf dependency) so authoring
the fixture costs $0 and adds nothing to the project's deps.

The fixture is a 2-page mini datasheet that exercises BOTH PDF mining modes and their tricky
edges in one file:

  Page 1 — token mode. An "Ordering Information" scope heading followed by three SKU-shaped
           tokens (and noise). Proves flat-token scanning + scope_heading page filtering.
  Page 2 — section mode. A non-doubled contents line ('SFP+ Modules listed on page 2') that
           must NOT switch the chapter, a bold double-rendered heading
           ('SSFFPP++  MMoodduulleess') that MUST, an adjacent '<noun> (SKU)' optic callout
           that is kept, and a 'Module (SKU)' callout that is dropped (Module is a
           switch-line-card noun, excluded from context_noun). Proves doubled-heading
           detection, the contents-line guard, adjacency, and Module exclusion.
"""
from __future__ import annotations

from pathlib import Path

# Each page is a list of text lines drawn top-to-bottom.
PAGE1 = [
    "Sample Transceiver Datasheet",
    "Ordering Information",
    "SKU FN-TRAN-SFP+LR single mode",
    "SKU FN-TRAN-QSFP28-SR4 multimode",
    "SKU FG-CABLE-SR10-SFP breakout",
    "random marketing line with no part number",
]
PAGE2 = [
    "Contents and chapter index",
    "SFP+ Modules listed on page 2",          # non-doubled contents line -> must NOT trigger
    "SSFFPP++  MMoodduulleess",                # bold double-render -> triggers SFP+ chapter
    "100G MMF Transceiver (R0Z21A) details",  # adjacent optic callout -> kept as SFP+
    "Switch Module (JL999A) ignore this one",  # Module noun -> dropped (switch line card)
]


def _esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _content_stream(lines: list[str]) -> bytes:
    body = ["BT", "/F1 12 Tf", "14 TL", "72 720 Td"]
    for i, ln in enumerate(lines):
        if i:
            body.append("T*")          # next line (uses leading set by TL)
        body.append(f"({_esc(ln)}) Tj")
    body.append("ET")
    return ("\n".join(body) + "\n").encode("latin-1")


def build_pdf(pages: list[list[str]]) -> bytes:
    objects: list[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)  # 1-based object number

    # Reserve catalog(1) and pages(2); fill page/content/font objects, then patch.
    font_num = None
    page_nums: list[int] = []
    content_nums: list[int] = []
    # Pre-assign numbers: 1=catalog, 2=pages, then per page a page obj + content obj, then font.
    n_pages = len(pages)
    catalog_num, pages_num = 1, 2
    next_num = 3
    for _ in pages:
        page_nums.append(next_num); next_num += 1
        content_nums.append(next_num); next_num += 1
    font_num = next_num

    # Build in object-number order so objects[i] is object i+1.
    kids = " ".join(f"{p} 0 R" for p in page_nums)
    add(b"<< /Type /Catalog /Pages 2 0 R >>")                                  # 1
    add(f"<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>".encode())        # 2
    for pi, lines in enumerate(pages):
        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_num} 0 R >> >> "
            f"/Contents {content_nums[pi]} 0 R >>"
        ).encode()
        add(page_obj)                                                          # page
        stream = _content_stream(lines)
        add(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))  # content
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")            # font

    # Serialize with a cross-reference table.
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (len(objects) + 1)
    for i, obj in enumerate(objects, start=1):
        offsets[i] = len(out)
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for i in range(1, len(objects) + 1):
        out += f"{offsets[i]:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    return bytes(out)


def main() -> None:
    pdf = build_pdf([PAGE1, PAGE2])
    out = Path(__file__).with_name("sample_datasheet.pdf")
    out.write_bytes(pdf)
    print(f"wrote {out} ({len(pdf)} bytes)")


if __name__ == "__main__":
    main()
