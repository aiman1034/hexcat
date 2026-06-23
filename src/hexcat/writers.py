"""Low-level, byte-exact CSV writing with full control over delimiter, BOM, and
German decimal locale.

We deliberately hand-roll the CSV line serializer (rather than use csv.writer or
pandas.to_csv) so that:
  * BOM is present exactly where the contract requires it,
  * the delimiter is exactly what each file needs,
  * we can force-quote specific columns (the FAQ cell is ALWAYS double-quoted),
  * line endings are uniform CRLF.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

LINE_TERMINATOR = "\r\n"
BOM = "﻿"

# German decimal: comma decimal separator, NO thousands separator, exactly two decimals.
# e.g. "1899,00", "14000,00", "49,00". Ungrouped is unambiguous to JTL-Ameise (a '.' would be
# misread as a decimal point) and is the codebase's standing choice. Enforced on write AND in
# validation — any grouped value ("1.899,00") HARD-FAILs the gate.
GERMAN_DECIMAL_RE = re.compile(r"^\d+,\d{2}$")


class GermanDecimalError(ValueError):
    pass


def german_decimal(value: str | int | float | Decimal, decimals: int = 2) -> str:
    """Format a number to German locale: comma decimal, no thousands separator.

    Accepts plain numbers given with either '.' or ',' as the decimal mark.
    Raises GermanDecimalError on non-numeric or thousands-separated input.
    """
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            raise GermanDecimalError("empty numeric value")
        # Reject thousands separators outright (ambiguous): both '.' and ',' present,
        # or grouped digits like 1.350,00 / 1,350.00.
        if "." in s and "," in s:
            raise GermanDecimalError(
                f"ambiguous number with both separators: {value!r}"
            )
        normalized = s.replace(",", ".")
    else:
        normalized = str(value)
    try:
        dec = Decimal(normalized)
    except (InvalidOperation, ValueError):
        raise GermanDecimalError(f"not a number: {value!r}")
    quantum = Decimal(1).scaleb(-decimals)  # e.g. 0.01
    dec = dec.quantize(quantum, rounding=ROUND_HALF_UP)
    out = f"{dec:f}".replace(".", ",")
    if "," not in out:  # e.g. decimals=0
        return out
    return out


def serialize_field(value: str, delimiter: str, force_quote: bool = False) -> str:
    """Serialize one CSV field with RFC-4180 quoting rules."""
    text = "" if value is None else str(value)
    needs_quote = (
        force_quote
        or delimiter in text
        or '"' in text
        or "\r" in text
        or "\n" in text
    )
    if needs_quote:
        return '"' + text.replace('"', '""') + '"'
    return text


def serialize_row(
    fields: list[str],
    delimiter: str,
    force_quote_indices: frozenset[int] = frozenset(),
) -> str:
    return delimiter.join(
        serialize_field(f, delimiter, force_quote=(i in force_quote_indices))
        for i, f in enumerate(fields)
    )


def write_csv(
    path: str | Path,
    header: tuple[str, ...] | list[str],
    rows: list[list[str]],
    delimiter: str,
    bom: bool,
    force_quote_columns: frozenset[int] = frozenset(),
) -> None:
    """Write a CSV file byte-exactly.

    force_quote_columns: 0-based column indices whose value is ALWAYS quoted
    (used for the FAQ cell).
    """
    path = Path(path)
    lines = [serialize_row(list(header), delimiter)]
    for row in rows:
        if len(row) != len(header):
            raise ValueError(
                f"row has {len(row)} fields, expected {len(header)} for {path.name}"
            )
        lines.append(serialize_row(row, delimiter, force_quote_columns))
    text = LINE_TERMINATOR.join(lines) + LINE_TERMINATOR
    if bom:
        text = BOM + text
    # newline="" so Python does not translate our explicit CRLF.
    path.write_text(text, encoding="utf-8", newline="")
