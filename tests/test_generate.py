"""Tests for the $0 content flow: skeleton -> worksheet -> draft -> validate -> build.

No API, no mocking — there is no model call anywhere in HexCat. These tests prove the
worksheet round-trips, the draft merge is faithful, the draft content gate enforces every
rule with a located message, and a draft that passes `validate_draft` passes `build`.
"""
from __future__ import annotations

import csv as _csv

import pytest

from hexcat.assemble import assemble_bundle
from hexcat.generate import (
    CONTENT_COLUMNS,
    FLAG_PREFIX,
    GenerateError,
    merge_fields,
    read_skeleton,
    read_worksheet,
    soft_spec_flags,
    write_draft,
    write_skeleton_template,
    write_worksheet,
)
from hexcat.intake import read_intake
from hexcat.models import INTAKE_COLUMNS
from hexcat.validate import validate_dir, validate_draft
from test_content_checks import GOOD_BESCH, GOOD_KURZ, GOOD_META, GOOD_TITEL

GOOD_FAQ_LINES = [
    "Ist das Cisco SFP-10G-SR ein Originalprodukt? :: Ja, ein originaler Cisco-Transceiver.",
    "Welche Reichweite erreicht das SFP-10G-SR? :: Ueber OM3-Multimode bis zu 300 Meter.",
    "Unterstuetzt das Modul DOM? :: Ja, Digital Optical Monitoring wird unterstuetzt.",
]
GOOD_FAQ_CELL = " ;; ".join(GOOD_FAQ_LINES)


# --------------------------------------------------------------------------- #
# Fixtures: a facts-only skeleton row                                          #
# --------------------------------------------------------------------------- #
def _skeleton_row() -> dict[str, str]:
    row = {c: "" for c in INTAKE_COLUMNS}
    row.update({
        "Artikelnummer": "SFP-10G-SR",
        "Vendor": "Cisco",
        "KategorieEbene3": "SFP+",
        "Artikelname": "Cisco SFP-10G-SR 10G SFP+ Transceiver Modul",
        "NettoVK": "120.50",
        "Formfaktor": "SFP+",
        "Geschwindigkeit": "10 Gigabit",
        "TransceiverTyp": "SR",
        "Faseranzahl": "2",
        "Fasertyp": "Multimode",
        "Anschlusstyp": "LC Duplex",
        "Wellenlaenge": "850 nm",
        "Anwendung": "Rechenzentrum",
        "Reichweite": "300 m",
        "DOMUnterstuetzung": "Ja",
        "Betriebstemperatur": "0 bis 70 Grad C",
        "Standard": "IEEE 802.3ae",
        "Condition": "new",
    })
    return row


def _good_content() -> dict[str, str]:
    return {
        "Kurzbeschreibung": GOOD_KURZ,
        "Beschreibung": GOOD_BESCH,
        "TitelTag": GOOD_TITEL,
        "MetaDescription": GOOD_META,
        "FAQ": GOOD_FAQ_CELL,
    }


def _write_skeleton(tmp_path, rows):
    path = tmp_path / "skeleton.csv"
    write_draft(path, rows)
    return path


def _fill_block(text: str, field: str, sku: str, body: str) -> str:
    """Insert authored `body` into the empty BEGIN/END block for (field, sku)."""
    begin = f"<!-- HEXCAT:BEGIN {field} | {sku} -->"
    end = f"<!-- HEXCAT:END {field} | {sku} -->"
    assert begin in text and end in text, f"missing block for {field}/{sku}"
    head, _, rest = text.partition(begin)
    _old_body, _, tail = rest.partition(end)
    return f"{head}{begin}\n{body}\n{end}{tail}"


def _author_worksheet(text: str, sku: str, *, faq_lines=None) -> str:
    """Fill all five content blocks of `sku` with known-good content."""
    text = _fill_block(text, "Kurzbeschreibung", sku, GOOD_KURZ)
    text = _fill_block(text, "Beschreibung", sku, GOOD_BESCH)
    text = _fill_block(text, "TitelTag", sku, GOOD_TITEL)
    text = _fill_block(text, "MetaDescription", sku, GOOD_META)
    text = _fill_block(text, "FAQ", sku, "\n".join(faq_lines or GOOD_FAQ_LINES))
    return text


# --------------------------------------------------------------------------- #
# read_skeleton                                                                #
# --------------------------------------------------------------------------- #
def test_read_skeleton_skips_comment_and_blank(tmp_path, rules):
    rows = [
        {**{c: "" for c in INTAKE_COLUMNS}, "Artikelnummer": "# example", "Vendor": "Cisco"},
        _skeleton_row(),
    ]
    facts = read_skeleton(_write_skeleton(tmp_path, rows), rules)
    assert len(facts) == 1
    assert facts[0].sku == "SFP-10G-SR"
    assert facts[0].hersteller == "Cisco"


def test_read_skeleton_unknown_vendor(tmp_path, rules):
    bad = _skeleton_row()
    bad["Vendor"] = "Acme"
    with pytest.raises(GenerateError, match="Vendor"):
        read_skeleton(_write_skeleton(tmp_path, [bad]), rules)


# --------------------------------------------------------------------------- #
# Skeleton emitter                                                             #
# --------------------------------------------------------------------------- #
def test_write_skeleton_template(tmp_path, rules):
    path = tmp_path / "skel.csv"
    write_skeleton_template(path)
    with path.open(encoding="utf-8-sig", newline="") as fh:
        emitted = list(_csv.DictReader(fh))
    assert len(emitted) == 1
    assert emitted[0]["Artikelnummer"].startswith("#")
    for c in CONTENT_COLUMNS:
        assert emitted[0][c] == ""
    with pytest.raises(GenerateError):
        read_skeleton(path, rules)


# --------------------------------------------------------------------------- #
# Worksheet round-trip                                                         #
# --------------------------------------------------------------------------- #
def test_worksheet_has_block_per_field_and_skeleton_header(tmp_path, rules):
    skeleton = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(skeleton, rules)
    wk = tmp_path / "wk.md"
    write_worksheet(wk, facts, rules, skeleton_path=skeleton)
    text = wk.read_text(encoding="utf-8")
    assert "HEXCAT:SKELETON" in text and str(skeleton) in text
    for field in CONTENT_COLUMNS:
        assert f"HEXCAT:BEGIN {field} | SFP-10G-SR" in text
    # The rendered voice guide and the banned list are embedded for Claude to read.
    assert "Hexwaren" in text and "sofort lieferbar" in text


def test_empty_worksheet_blocks_round_trip_as_blank(tmp_path, rules):
    skeleton = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(skeleton, rules)
    wk = tmp_path / "wk.md"
    write_worksheet(wk, facts, rules, skeleton_path=skeleton)
    embedded, content = read_worksheet(wk)
    assert embedded == str(skeleton)
    assert content["SFP-10G-SR"]["Kurzbeschreibung"] == ""
    assert content["SFP-10G-SR"]["FAQ"] == ""


def test_authored_worksheet_round_trips(tmp_path, rules):
    skeleton = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(skeleton, rules)
    wk = tmp_path / "wk.md"
    write_worksheet(wk, facts, rules, skeleton_path=skeleton)
    wk.write_text(_author_worksheet(wk.read_text(encoding="utf-8"), "SFP-10G-SR"),
                  encoding="utf-8")

    _embedded, content = read_worksheet(wk)
    c = content["SFP-10G-SR"]
    assert c["Kurzbeschreibung"] == GOOD_KURZ
    assert c["Beschreibung"] == GOOD_BESCH
    # FAQ lines are joined into a friendly Q::A;;Q::A cell.
    assert c["FAQ"] == GOOD_FAQ_CELL
    assert c["FAQ"].count("::") == 3 and c["FAQ"].count(";;") == 2


def test_read_worksheet_missing_file(tmp_path):
    with pytest.raises(GenerateError, match="not found"):
        read_worksheet(tmp_path / "nope.md")


# --------------------------------------------------------------------------- #
# Draft validation: good draft passes the content gate                          #
# --------------------------------------------------------------------------- #
def _good_draft(tmp_path, rules):
    row = merge_fields(_skeleton_row(), _good_content())
    draft = tmp_path / "draft.csv"
    write_draft(draft, [row])
    return draft


def test_validate_draft_good_passes(tmp_path, rules):
    result = validate_draft(rules, _good_draft(tmp_path, rules))
    assert result.ok, "\n".join(str(v) for v in result.violations)


def test_validate_draft_missing_file(tmp_path, rules):
    result = validate_draft(rules, tmp_path / "nope.csv")
    assert not result.ok
    assert "not found" in result.violations[0].message


# --------------------------------------------------------------------------- #
# Draft validation: a seeded-bad draft flags EVERY defect, each located         #
# --------------------------------------------------------------------------- #
def test_validate_draft_seeded_defects(tmp_path, rules):
    content = _good_content()
    # 1. Beschreibung too long (keep 3 <p>, blow the word budget).
    filler = " ".join(["Wort"] * 200)
    content["Beschreibung"] = (
        f"<p>{filler}</p><p>Zweiter Absatz.</p>"
        "<p>Originaler Cisco-Transceiver fuer den Einsatz.</p>"
    )
    # 2. banned hard-fail phrase in Kurzbeschreibung.
    content["Kurzbeschreibung"] = GOOD_KURZ.replace("im taeglichen Betrieb", "sofort lieferbar")
    # 3. Titel-Tag too long (still ends with the suffix).
    content["TitelTag"] = "Cisco SFP-10G-SR viel zu langer ueberlanger Produkttitel hier | Hexwaren"
    # 4. malformed FAQ (no recognizable separator).
    content["FAQ"] = "Frage ohne Trenner und ohne Antwort"

    row = merge_fields(_skeleton_row(), content)
    draft = tmp_path / "bad.csv"
    write_draft(draft, [row])

    result = validate_draft(rules, draft)
    assert not result.ok
    fields = {v.field for v in result.violations}
    msgs = " | ".join(v.message for v in result.violations)
    assert "Beschreibung" in fields and "words" in msgs.lower()
    assert "Kurzbeschreibung" in fields and "forbidden" in msgs.lower()
    assert "TitelTag" in fields and "character" in msgs.lower()
    assert "FAQ" in fields
    # Every violation is located to the SKU.
    assert all(v.sku == "SFP-10G-SR" for v in result.violations)


def test_validate_draft_missing_closer(tmp_path, rules):
    content = _good_content()
    content["Beschreibung"] = GOOD_BESCH.replace("Originaler Cisco-", "Echter Cisco-")
    row = merge_fields(_skeleton_row(), content)
    draft = tmp_path / "noclose.csv"
    write_draft(draft, [row])
    result = validate_draft(rules, draft)
    assert not result.ok
    assert any(v.field == "Beschreibung" and "closer" in v.message.lower()
               for v in result.violations)


def test_validate_draft_flag_marker_blocks(tmp_path, rules):
    content = _good_content()
    content["TitelTag"] = FLAG_PREFIX + GOOD_TITEL
    row = merge_fields(_skeleton_row(), content)
    draft = tmp_path / "flagged.csv"
    write_draft(draft, [row])
    result = validate_draft(rules, draft)
    assert not result.ok
    assert any(v.field == "TitelTag" and "flag" in v.message.lower()
               for v in result.violations)


# --------------------------------------------------------------------------- #
# End-to-end: worksheet -> draft -> validate_draft -> read_intake -> build PASS  #
# --------------------------------------------------------------------------- #
def test_full_zero_dollar_flow_passes_build(tmp_path, rules, weights):
    skeleton = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(skeleton, rules)

    wk = tmp_path / "wk.md"
    write_worksheet(wk, facts, rules, skeleton_path=skeleton)
    wk.write_text(_author_worksheet(wk.read_text(encoding="utf-8"), "SFP-10G-SR"),
                  encoding="utf-8")

    embedded, content = read_worksheet(wk)
    rows = [merge_fields(f.row, {c: content[f.sku].get(c, "") for c in CONTENT_COLUMNS})
            for f in facts]
    draft = tmp_path / "draft.csv"
    write_draft(draft, rows)

    # The draft content gate must pass...
    assert validate_draft(rules, draft).ok

    # ...and therefore so must the real build gate.
    records = read_intake(draft, rules, weights)
    assert len(records) == 1
    bundle_dir = tmp_path / "out"
    assemble_bundle(records, rules, batch="GenBatch", category="Transceivers",
                    out_dir=bundle_dir, build_time="2026-06-11T00:00:00Z")
    result = validate_dir(rules, bundle_dir)
    assert result.ok, "\n".join(str(v) for v in result.violations)


# --------------------------------------------------------------------------- #
# Soft safety check (non-blocking)                                              #
# --------------------------------------------------------------------------- #
def test_soft_spec_flags_unbacked_spec():
    facts = _skeleton_row()
    fields = {c: "" for c in CONTENT_COLUMNS}
    fields["MetaDescription"] = "Reichweite bis zu 4000 km ueber Singlemode-Glasfaser."
    flags = soft_spec_flags(fields, facts)
    assert any("4000 km" in f for f in flags)


def test_soft_spec_flags_backed_spec_is_silent():
    facts = _skeleton_row()  # has Reichweite '300 m', Wellenlaenge '850 nm'
    fields = {c: "" for c in CONTENT_COLUMNS}
    fields["MetaDescription"] = "Bis zu 300 m Reichweite bei 850 nm."
    assert soft_spec_flags(fields, facts) == []


def test_validate_draft_surfaces_soft_flag_as_warning(tmp_path, rules):
    content = _good_content()
    content["MetaDescription"] = (
        "Originaler Cisco-Transceiver mit bis zu 4000 km Reichweite und LC-Duplex-Anschluss "
        "fuer den professionellen Einsatz in grossen Netzwerken jeder Art heute."
    )
    row = merge_fields(_skeleton_row(), content)
    draft = tmp_path / "soft.csv"
    write_draft(draft, [row])
    result = validate_draft(rules, draft)
    # The unbacked '4000 km' is advisory: a warning, not a blocking violation.
    assert any("4000 km" in str(w) for w in result.warnings)
