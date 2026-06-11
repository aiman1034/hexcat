from __future__ import annotations

import json

import pytest

from hexcat.assemble import assemble_bundle
from hexcat.generate import (
    CONTENT_COLUMNS,
    GenerateError,
    Generator,
    merge_fields,
    parse_response,
    read_skeleton,
    write_draft,
)
from hexcat.intake import read_intake
from hexcat.models import INTAKE_COLUMNS
from hexcat.validate import validate_dir
from test_content_checks import GOOD_BESCH, GOOD_KURZ, GOOD_META, GOOD_TITEL


# --------------------------------------------------------------------------- #
# Fixtures: a facts-only skeleton row + canned model responses                 #
# --------------------------------------------------------------------------- #
def _skeleton_row() -> dict[str, str]:
    """A single SFP+ SKU with all content columns blank (facts only)."""
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


def _good_payload() -> dict:
    return {
        "kurzbeschreibung": GOOD_KURZ,
        "beschreibung": GOOD_BESCH,
        "titel_tag": GOOD_TITEL,
        "meta_description": GOOD_META,
        "faq": [
            {"frage": "Ist das Cisco SFP-10G-SR ein Originalprodukt?",
             "antwort": "Ja, es handelt sich um einen originalen Cisco-Transceiver."},
            {"frage": "Welche Reichweite erreicht das SFP-10G-SR?",
             "antwort": "Ueber OM3-Multimode-Glasfaser werden bis zu 300 Meter erreicht."},
            {"frage": "Unterstuetzt das Modul DOM?",
             "antwort": "Ja, Digital Optical Monitoring wird unterstuetzt."},
        ],
    }


def _good_completer(system, user):
    return json.dumps(_good_payload())


def _write_skeleton(tmp_path, rows):
    path = tmp_path / "skeleton.csv"
    write_draft(path, rows)  # write_draft emits all INTAKE_COLUMNS; content cells blank
    return path


# --------------------------------------------------------------------------- #
# read_skeleton                                                                #
# --------------------------------------------------------------------------- #
def test_read_skeleton_skips_comment_and_blank(tmp_path, rules):
    rows = [
        {**{c: "" for c in INTAKE_COLUMNS}, "Artikelnummer": "# example", "Vendor": "Cisco"},
        _skeleton_row(),
    ]
    path = _write_skeleton(tmp_path, rows)
    facts = read_skeleton(path, rules)
    assert len(facts) == 1
    assert facts[0].sku == "SFP-10G-SR"
    assert facts[0].hersteller == "Cisco"


def test_read_skeleton_unknown_vendor(tmp_path, rules):
    bad = _skeleton_row()
    bad["Vendor"] = "Acme"
    path = _write_skeleton(tmp_path, [bad])
    with pytest.raises(GenerateError, match="Vendor"):
        read_skeleton(path, rules)


# --------------------------------------------------------------------------- #
# parse_response                                                               #
# --------------------------------------------------------------------------- #
def test_parse_plain_json():
    fields, pairs, cell = parse_response(json.dumps(_good_payload()))
    assert set(CONTENT_COLUMNS) == set(fields)
    assert len(pairs) == 3
    assert cell.count("##") == 2 and cell.count("||") == 3


def test_parse_strips_code_fences():
    raw = "```json\n" + json.dumps(_good_payload()) + "\n```"
    fields, pairs, _ = parse_response(raw)
    assert fields["TitelTag"] == GOOD_TITEL
    assert len(pairs) == 3


def test_parse_extracts_json_from_prose():
    raw = "Hier ist das JSON:\n" + json.dumps(_good_payload()) + "\nVielen Dank!"
    fields, _, _ = parse_response(raw)
    assert fields["Kurzbeschreibung"] == GOOD_KURZ


def test_parse_sanitizes_faq_separators():
    payload = _good_payload()
    payload["faq"][0]["antwort"] = "Antwort mit || und ## Zeichen"
    _, pairs, cell = parse_response(json.dumps(payload))
    # Separators inside text must be neutralized so the canonical cell stays well-formed.
    assert "||" not in pairs[0].answer and "##" not in pairs[0].answer
    assert cell.count("##") == 2 and cell.count("||") == 3


def test_parse_non_json_raises():
    with pytest.raises(GenerateError):
        parse_response("Das ist nur Fließtext ohne JSON.")


# --------------------------------------------------------------------------- #
# Generator: success, retry, exhaustion                                        #
# --------------------------------------------------------------------------- #
def test_generate_one_success(tmp_path, rules):
    path = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(path, rules)
    gen = Generator(rules, completer=_good_completer)
    res = gen.generate_one(facts[0])
    assert res.ok
    assert res.attempts == 1
    assert res.faq_pairs == 3


def test_generate_one_retries_then_succeeds(tmp_path, rules):
    bad = _good_payload()
    bad["kurzbeschreibung"] = "<p>viel zu kurz</p><p>immer noch kurz</p>"  # fails word budget
    responses = [json.dumps(bad), json.dumps(_good_payload())]

    def flaky(system, user):
        return responses.pop(0)

    path = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(path, rules)
    res = Generator(rules, completer=flaky, max_retries=3).generate_one(facts[0])
    assert res.ok
    assert res.attempts == 2


def test_generate_one_flags_after_exhaustion(tmp_path, rules):
    bad = _good_payload()
    bad["titel_tag"] = "Titel ganz ohne den notwendigen Suffix"  # always fails

    def always_bad(system, user):
        return json.dumps(bad)

    path = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(path, rules)
    res = Generator(rules, completer=always_bad, max_retries=3).generate_one(facts[0])
    assert not res.ok
    assert res.attempts == 3
    assert res.issues


# --------------------------------------------------------------------------- #
# End-to-end: generate -> draft -> read_intake -> assemble -> validate PASSES   #
# --------------------------------------------------------------------------- #
def test_generated_draft_passes_the_build_gate(tmp_path, rules, weights):
    skeleton = _write_skeleton(tmp_path, [_skeleton_row()])
    facts = read_skeleton(skeleton, rules)
    gen = Generator(rules, completer=_good_completer)

    out_rows = []
    for f in facts:
        res = gen.generate_one(f)
        assert res.ok
        out_rows.append(merge_fields(f.row, res.fields))

    draft = tmp_path / "draft.csv"
    write_draft(draft, out_rows)

    # The deterministic core must consume the draft and the gate must pass.
    records = read_intake(draft, rules, weights)
    assert len(records) == 1
    bundle_dir = tmp_path / "out"
    assemble_bundle(records, rules, batch="GenBatch", category="Transceivers",
                    out_dir=bundle_dir, build_time="2026-06-11T00:00:00Z")
    result = validate_dir(rules, bundle_dir)
    assert result.ok, "\n".join(str(v) for v in result.violations)
