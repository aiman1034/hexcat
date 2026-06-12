"""Generate the committed COLUMN-LAYOUT ordering fixture — sample_ordering_columns.pdf.

This fixture exists to lock the Stage-1 self-audit bug classes as permanent regressions WITHOUT
depending on the gitignored real datasheets. It is a one-page "Ordering Information" table with a
genuine two-column geometry (SKU column at x≈70, Description column at x≈210) that reproduces
every defect the verifier was built to catch:

  * description-bleed phantom — a SKU-shaped token (FX-PHANTOM-XX) sits in the DESCRIPTION
    column; a flat scan would mine it, column extraction must not.
  * trailing '+' separator — FX-CABLE-DAC1 and FX-CABLE-DAC1+ are DISTINCT products that
    collapse to the same string if the '+' is stripped (the DR4/DR4+ collision in miniature).
  * V5 classification from description — a DAC, an MPO breakout, and an AOC row that must be
    classified from the manufacturer description, NOT the PN substring.
  * pack-of-four — FX-TRAN-SX-4PACK must carry the Viererpack Notiz.

Built from raw bytes (no reportlab/fpdf), text placed by an absolute text matrix (Tm) so each
cell lands in its own x-band. Run once to (re)produce the committed fixture.
"""
from __future__ import annotations

from pathlib import Path

# (sku, description) rows of the ordering table. The phantom is embedded in a description.
ROWS = [
    ("FX-TRAN-SFP+LR", "10 GE SFP+ transceiver module, long range 10km, LC connector, SMF"),
    ("FX-CABLE-DAC1", "10 GE SFP+ passive direct attach cable, 1m, transceivers included"),
    ("FX-CABLE-DAC1+", "10 GE SFP+ passive direct attach cable, 1.5m, transceivers included"),
    ("FX-CABLE-SR10", "100 GE parallel breakout MPO to 10xLC connectors, OM3 MMF, "
                      "transceivers not included"),
    ("FX-CABLE-AOC03", "400 GE active optical cable, 3m, transceivers included"),
    ("FX-TRAN-SX-4PACK", "Pack of four 1 GE SFP transceiver module, short range 500m"),
    ("FX-TRAN-NOTE", "1 GE SFP module; see FX-PHANTOM-XX for the legacy ordering code"),
]

SKU_X = 70.0
DESC_X = 210.0
TOP_Y = 700.0      # first content row y (PDF origin is bottom-left)
HEADER_Y = 740.0
LINE_DY = 18.0


def _esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _content_stream() -> bytes:
    body = ["BT", "/F1 11 Tf"]

    def place(x: float, y: float, text: str) -> None:
        body.append(f"1 0 0 1 {x:.1f} {y:.1f} Tm")
        body.append(f"({_esc(text)}) Tj")

    place(SKU_X, HEADER_Y, "SKU")
    place(DESC_X, HEADER_Y, "Description")
    place(SKU_X, HEADER_Y + 20, "Ordering Information")
    y = TOP_Y
    for sku, desc in ROWS:
        place(SKU_X, y, sku)
        place(DESC_X, y, desc)
        y -= LINE_DY
    body.append("ET")
    return ("\n".join(body) + "\n").encode("latin-1")


def build_pdf() -> bytes:
    stream = _content_stream()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
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
    out = Path(__file__).with_name("sample_ordering_columns.pdf")
    out.write_bytes(build_pdf())
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
