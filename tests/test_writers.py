from __future__ import annotations

import pytest

from hexcat.writers import (
    BOM,
    GERMAN_DECIMAL_RE,
    GermanDecimalError,
    german_decimal,
    serialize_field,
    write_csv,
)


@pytest.mark.parametrize("raw,expected", [
    ("1350", "1350,00"),
    ("120.50", "120,50"),
    ("120,5", "120,50"),
    ("49", "49,00"),
    (0.1, "0,10"),
    ("1350.005", "1350,01"),  # rounding half-up
])
def test_german_decimal_ok(raw, expected):
    out = german_decimal(raw)
    assert out == expected
    assert GERMAN_DECIMAL_RE.match(out)


@pytest.mark.parametrize("bad", ["1.350,00", "1,350.00", "abc", "", "  "])
def test_german_decimal_rejects(bad):
    with pytest.raises(GermanDecimalError):
        german_decimal(bad)


def test_serialize_field_quoting():
    # delimiter present -> quoted
    assert serialize_field("a,b", ",") == '"a,b"'
    # no delimiter -> bare
    assert serialize_field("ab", ",") == "ab"
    # comma value but delimiter ';' -> not quoted
    assert serialize_field("120,50", ";") == "120,50"
    # inner quote doubled
    assert serialize_field('he said "hi"', ",") == '"he said ""hi"""'
    # force quote
    assert serialize_field("plain", ",", force_quote=True) == '"plain"'


def test_write_csv_bom_and_crlf(tmp_path):
    p = tmp_path / "x.csv"
    write_csv(p, ("A", "B"), [["1", "x;y"]], delimiter=";", bom=True)
    raw = p.read_bytes()
    assert raw[:3] == b"\xef\xbb\xbf"          # UTF-8 BOM
    text = raw.decode("utf-8")[len(BOM):]
    assert text == "A;B\r\n1;\"x;y\"\r\n"       # ; delimiter quotes the ;-containing field


def test_write_csv_no_bom(tmp_path):
    p = tmp_path / "x.csv"
    write_csv(p, ("A",), [["1"]], delimiter=",", bom=False)
    assert p.read_bytes()[:3] != b"\xef\xbb\xbf"


def test_write_csv_force_quote_column(tmp_path):
    p = tmp_path / "faq.csv"
    write_csv(p, ("Artikelnummer", "FAQ"), [["SKU1", "Q||A##Q2||A2"]],
              delimiter=",", bom=True, force_quote_columns=frozenset({1}))
    line = p.read_bytes().decode("utf-8")[len(BOM):].split("\r\n")[1]
    assert line == 'SKU1,"Q||A##Q2||A2"'


def test_write_csv_row_width_mismatch(tmp_path):
    with pytest.raises(ValueError):
        write_csv(tmp_path / "x.csv", ("A", "B"), [["only-one"]], delimiter=",", bom=False)
