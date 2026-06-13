"""Stage-3 tests — the CONVERGED contract.

Stage 3 no longer has its own divergent writer. An in-session-authored content sidecar
(`*_content.json`) is reconciled onto the SAME canonical pipeline the proof slice was built
with: `reconcile_content` → `SkuIntake` → `intake.build_record` → `assemble.assemble_bundle`
→ seven byte-exact files → `validate.validate_dir`. There is exactly ONE output contract.

These tests freeze the convergence layer (physical Formfaktor extraction, attribute aliasing
onto the locked 14-schema, prose-only Beschreibung ending on the authenticity closer, FAQ as a
separate Q||A cell) and assert the full bundle passes the build gate GREEN.
"""
from __future__ import annotations

import json

from hexcat.assemble import assemble_bundle
from hexcat.stage3 import (
    ReconcileError,
    SkuFacts,
    entry_to_intake,
    physical_formfaktor,
    reconcile_content,
    write_content_template,
)
from hexcat.stage3.reconcile import (
    ATTR_ALIAS,
    _closer,
    _compose_beschreibung,
    map_attributes,
)
from hexcat.validate import validate_dir


# --- authored content fixtures (grounded, in-session-style prose) ------------------------
def _cisco_optic() -> tuple[str, dict]:
    """A Cisco SFP+ optical module — closer in the masculine 'Originaler …Transceiver' form."""
    return "SFP-10G-SR", {
        "_facts": {"unterkategorie": "SFP+", "quell_url": "https://cisco.example/sfp-10g-sr"},
        "artikelname": "Cisco SFP-10G-SR 10GBASE-SR SFP+ Transceiver",
        "titel_tag": "Cisco SFP-10G-SR 10GBASE-SR SFP+ | Hexwaren",
        "meta_description": (
            "Original Cisco SFP-10G-SR 10GBASE-SR SFP+ Transceiver kaufen: 850 nm Multimode, "
            "bis 300 m auf OM3, LC-Duplex, mit Digital Optical Monitoring und Hot-Swap. "
            "Neuware für Cisco Catalyst und Nexus."
        ),
        "kurzbeschreibung": (
            "<p>Der Cisco SFP-10G-SR ist ein originaler 10GBASE-SR SFP+ Transceiver für "
            "Multimode-Faser, der zehn Gigabit Ethernet bei 850 Nanometer über einen "
            "LC-Duplex-Anschluss überträgt und auf OM3 bis zu 300 Meter erreicht.</p>"
            "<p>Mit Unterstützung für Digital Optical Monitoring und voller Hot-Swap-Fähigkeit "
            "fügt sich das Modul nahtlos in Cisco Catalyst und Nexus Switches im Rechenzentrum "
            "sowie im Campus ein.</p>"
        ),
        "intro": [
            "Das Cisco SFP-10G-SR ist ein originaler 10GBASE-SR SFP+ Transceiver mit "
            "LC-Duplex-Anschluss, der zehn Gigabit Ethernet über Multimode-Faser bei 850 "
            "Nanometer in Rechenzentren und Campus-Netzwerken überträgt.",
            "Über OM3-Multimode-Faser erreicht das Modul eine Reichweite von bis zu 300 Metern "
            "und arbeitet vollständig konform zum Standard IEEE 802.3ae für zuverlässige "
            "Verbindungen im Aggregations- und Zugriffsbereich; auf OM4-Faser sind entsprechend "
            "größere Distanzen möglich, auf älterer OM2-Faser dagegen kürzere.",
            "Das Modul unterstützt Digital Optical Monitoring zur kontinuierlichen Überwachung "
            "von Temperatur, Spannung sowie Sende- und Empfangsleistung im laufenden Betrieb und "
            "arbeitet im kommerziellen Temperaturbereich von null bis siebzig Grad Celsius bei "
            "voller Hot-Swap-Fähigkeit.",
        ],
        "faq": [
            ["Ist dies ein originales Cisco-Modul?",
             "Ja, Original Cisco-Neuware, werkseitig versiegelt."],
            ["Welche Faser wird benötigt?",
             "Multimode-Faser (OM3) mit LC-Duplex-Anschluss, bis 300 Meter."],
            ["Welche Wellenlänge nutzt das Modul?",
             "850 Nanometer nach IEEE 802.3ae 10GBASE-SR."],
        ],
        "attributes": [
            ["Formfaktor", "SFP+"],
            ["Datenrate", "10 Gbit/s"],
            ["Wellenlänge", "850 nm"],
            ["Reichweite", "300 m"],
            ["Fasertyp", "Multimode (OM3)"],
            ["Standard", "IEEE 802.3ae 10GBASE-SR"],
            ["Anwendung", "Rechenzentrum und Campus (Kurzstrecke, Aggregation/Zugriff)"],
            ["Betriebstemperatur", "0 bis 70 °C (kommerziell)"],
            ["DOM Unterstützung", "Ja"],
            ["Zustand", "Neu, versiegelt"],
        ],
        "netto_vk": None,
    }


def _cisco_dac() -> tuple[str, dict]:
    """A Cisco DAC cable — category 'DAC Kabel' but Formfaktor is the physical 'SFP+' connector;
    closer is the neuter 'Originales …Direktanschlusskabel' form; cable word-floor flexes down."""
    return "SFP-H10GB-CU3M", {
        "_facts": {"unterkategorie": "DAC Kabel",
                   "quell_url": "https://cisco.example/sfp-h10gb-cu3m"},
        "artikelname": "Cisco SFP-H10GB-CU3M 10G SFP+ Direktanschlusskabel 3 m",
        "titel_tag": "Cisco SFP-H10GB-CU3M 10G SFP+ DAC 3m | Hexwaren",
        "meta_description": (
            "Original Cisco SFP-H10GB-CU3M kaufen: passives 10G SFP+ Direktanschlusskabel, "
            "3 m Twinax-Kupfer, beidseitig SFP+, ohne Stromversorgung. Neuware für "
            "Top-of-Rack-Verkabelung im Rechenzentrum."
        ),
        "kurzbeschreibung": (
            "<p>Das Cisco SFP-H10GB-CU3M ist ein originales passives "
            "SFP+-Direktanschlusskabel mit drei Metern Länge, das zwei "
            "10-Gigabit-SFP+-Ports über ein Twinax-Kupferkabel direkt miteinander "
            "verbindet.</p>"
            "<p>Es benötigt keine externe Stromversorgung, eignet sich ideal für die "
            "Top-of-Rack-Verkabelung im Rechenzentrum und bietet eine kostengünstige "
            "Alternative zu optischen Transceivern auf kurzen Distanzen.</p>"
        ),
        "intro": [
            "Das Cisco SFP-H10GB-CU3M ist ein passives 10-Gigabit-SFP+-Direktanschlusskabel "
            "mit drei Metern Länge und fest konfektionierten SFP+-Steckern an beiden Enden für "
            "kurze Verbindungen im Rack.",
            "Das Twinax-Kupferkabel verbindet zwei SFP+-Ports direkt ohne zusätzliche "
            "Transceiver und eignet sich besonders für die Top-of-Rack-Verkabelung zwischen "
            "Servern und Switches im selben oder benachbarten Rack des Rechenzentrums.",
            "Es benötigt keine externe Stromversorgung, erzeugt keine nennenswerte Verlustleistung "
            "und unterstützt die volle Bandbreite von zehn Gigabit Ethernet über die gesamte "
            "Kabellänge, womit es eine kostengünstige und stromsparende Alternative zu optischen "
            "Transceivern auf kurzen Distanzen bildet.",
        ],
        "faq": [
            ["Benötigt das Kabel eine Stromversorgung?",
             "Nein, es ist ein passives Twinax-Kupferkabel ohne aktive Elektronik."],
            ["Wie lang ist das Kabel?", "Drei Meter mit fest konfektionierten SFP+-Steckern."],
            ["Wofür eignet sich das Kabel?",
             "Für kurze 10-Gigabit-Verbindungen in der Top-of-Rack-Verkabelung."],
        ],
        "attributes": [
            ["Formfaktor", "SFP+"],
            ["Geschwindigkeit", "10 Gbit/s"],
            ["Länge", "3 m"],
            ["Kabeltyp", "Passives Twinax-Kupferkabel"],
            ["Reichweite", "3 m"],
            ["Anwendung", "Rechenzentrum (Top-of-Rack-Verkabelung)"],
            ["Betriebstemperatur", "0 bis 70 °C"],
            ["Zustand", "Neu, versiegelt"],
        ],
        "netto_vk": None,
    }


def _write_content(tmp_path, *entries) -> "object":
    data = {pn: entry for pn, entry in entries}
    p = tmp_path / "Cisco_content.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


# --- physical form-factor extraction -----------------------------------------------------
def test_physical_formfaktor_most_specific_first_and_sfp_guard():
    assert physical_formfaktor("SFP+") == "SFP+"
    assert physical_formfaktor("SFP") == "SFP"                 # bare SFP, no '+'
    assert physical_formfaktor("10GBASE-SR SFP") == "SFP"
    assert physical_formfaktor("QSFP28 optic") == "QSFP28"     # not collapsed to QSFP+/SFP
    assert physical_formfaktor("QSFP-DD800 module") == "QSFP-DD800"
    assert physical_formfaktor("100G QSFP-DD") == "QSFP-DD"
    assert physical_formfaktor("SFP28-Karte") == "SFP28"       # not "SFP"
    assert physical_formfaktor("nothing here") is None
    # candidates tried in order; first non-empty hit wins
    assert physical_formfaktor("", "OSFP-Anschluss", "ignored") == "OSFP"


# --- attribute aliasing onto the locked 14-schema ----------------------------------------
def test_map_attributes_folds_aliases_first_wins_and_drops_unknown():
    out = map_attributes(
        [("Datenrate", "100 Gbit/s"),
         ("Geschwindigkeit", "SHOULD-NOT-WIN"),   # collides with Datenrate's slot
         ("Frei erfunden", "x"),                   # no canonical slot -> dropped
         ("Anschluss", "LC"),
         ("Wellenlänge", "")],                     # empty -> skipped
        formfaktor="QSFP28",
    )
    assert out == {
        "Geschwindigkeit": "100 Gbit/s",   # first authored value wins
        "Anschlusstyp": "LC",
        "Formfaktor": "QSFP28",            # forced to the physical connector token
    }


def test_attr_alias_only_targets_canonical_names():
    canonical = {n for n, _ in __import__("hexcat.constants", fromlist=["x"]).TRANSCEIVER_ATTRIBUTES}
    assert set(ATTR_ALIAS.values()) <= canonical


# --- closer gender + prose-only composition ----------------------------------------------
def test_closer_agrees_with_product_gender():
    assert _closer("Cisco", "SFP+").startswith("Originaler Cisco-Transceiver")
    assert _closer("Cisco", "DAC Kabel").startswith("Originales Cisco-Direktanschlusskabel")
    assert _closer("Cisco", "AOC Kabel").startswith("Originales Cisco-AOC-Kabel")
    assert _closer("Cisco", "MPO Kabel").startswith("Originales Cisco-MPO-Kabel")


def test_compose_beschreibung_is_prose_only_and_ends_on_closer():
    html = _compose_beschreibung(
        ["Erster grundlegender Absatz.", "Zweiter Absatz.", "Dritter Absatz"],
        hersteller="Cisco", kategorie3="SFP+",
    )
    assert html.count("<p>") == 3 and html.count("</p>") == 3
    for tag in ("<ul>", "<li>", "<strong>", "<br>", "<a "):
        assert tag not in html                                 # NO spec list / markup
    # closer welded onto the final paragraph so the Beschreibung ENDS on it
    assert html.endswith("Originaler Cisco-Transceiver für den professionellen Einsatz in "
                         "Cisco-Netzwerkumgebungen.</p>")


def test_compose_raises_on_empty_intro():
    try:
        _compose_beschreibung([], hersteller="Cisco", kategorie3="SFP+")
    except ReconcileError:
        return
    raise AssertionError("expected ReconcileError on empty intro")


# --- entry_to_intake: one authored entry -> a wide intake row ----------------------------
def test_entry_to_intake_dac_keeps_category_but_physical_formfaktor(rules):
    pn, entry = _cisco_dac()
    intake = entry_to_intake(pn, entry, brand="Cisco", rules=rules)
    assert intake.Artikelnummer == pn
    assert intake.KategorieEbene3 == "DAC Kabel"               # category stays in Ebene 3
    assert intake.Formfaktor == "SFP+"                          # connector, never the category
    # Beschreibung is prose-only and ends on the neuter cable closer.
    assert "<ul>" not in intake.Beschreibung
    assert intake.Beschreibung.endswith(
        "Originales Cisco-Direktanschlusskabel für den professionellen Einsatz in "
        "Cisco-Netzwerkumgebungen.</p>")
    # FAQ flows out as the canonical Q||A##… cell (never inline in the Beschreibung).
    assert "||" in intake.FAQ and "##" in intake.FAQ
    assert "?" not in intake.Beschreibung


def test_entry_to_intake_unknown_brand_raises(rules):
    pn, entry = _cisco_optic()
    try:
        entry_to_intake(pn, entry, brand="Nonexistent", rules=rules)
    except ReconcileError:
        return
    raise AssertionError("expected ReconcileError for an unmapped brand")


# --- reconcile_content -> SkuRecords -----------------------------------------------------
def test_reconcile_content_yields_records(tmp_path, rules, weights):
    p = _write_content(tmp_path, _cisco_optic(), _cisco_dac())
    records = reconcile_content(p, brand="Cisco", rules=rules, weights=weights)
    assert {r.artikelnummer for r in records} == {"SFP-10G-SR", "SFP-H10GB-CU3M"}
    for r in records:
        assert r.hersteller == "Cisco"
        assert r.beschreibung.rstrip().endswith("Cisco-Netzwerkumgebungen.</p>")
        ff = [a for a in r.attributes if a.name == "Formfaktor"][0]
        assert ff.value == "SFP+"                              # physical connector token
        assert "Zustand" not in {a.name for a in r.attributes}  # condition is its own file
        assert r.condition == "new"
        assert r.faq_cell.count("||") == 3                     # three Q||A pairs
        assert r.netto_vk_de == "0,00"                          # PRICES-PENDING placeholder


def test_reconcile_empty_file_raises(tmp_path, rules, weights):
    p = tmp_path / "empty_content.json"
    p.write_text("{}", encoding="utf-8")
    try:
        reconcile_content(p, brand="Cisco", rules=rules, weights=weights)
    except ReconcileError:
        return
    raise AssertionError("expected ReconcileError on an empty content file")


# --- end-to-end: reconcile -> assemble -> validate GREEN ---------------------------------
def test_end_to_end_assemble_then_validate_is_green(tmp_path, rules, weights):
    content = tmp_path / "Cisco_content.json"
    data = {pn: e for pn, e in (_cisco_optic(), _cisco_dac())}
    content.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    records = reconcile_content(content, brand="Cisco", rules=rules, weights=weights)
    out = tmp_path / "bundle"
    assemble_bundle(records, rules, batch="Cisco_Transceivers",
                    category="Transceivers", out_dir=out,
                    build_time="2026-06-12T00:00:00Z")

    result = validate_dir(rules, out)
    assert result.ok, "expected GREEN bundle, got violations:\n" + "\n".join(
        str(v) for v in result.violations)


def test_end_to_end_seven_files_emitted(tmp_path, rules, weights):
    content = tmp_path / "Cisco_content.json"
    data = {pn: e for pn, e in (_cisco_optic(),)}
    content.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    records = reconcile_content(content, brand="Cisco", rules=rules, weights=weights)
    out = tmp_path / "bundle"
    manifest = assemble_bundle(records, rules, batch="Cisco_Transceivers",
                               category="Transceivers", out_dir=out,
                               build_time="2026-06-12T00:00:00Z")
    roles = {f.role for f in manifest.files}
    assert roles == {"main", "attributes", "platformflag", "prices",
                     "condition", "faq", "verification"}


# --- template flow (still live: emit a blank content sidecar to author in-session) -------
def test_write_content_template_seeds_facts_and_derivable_attrs(tmp_path):
    facts = [SkuFacts(pn="QSFP-100G-SL", unterkategorie="QSFP28",
                      quell_url="https://cisco.example/ds")]
    p = write_content_template(facts, tmp_path / "content.json")
    entry = json.loads(p.read_text(encoding="utf-8"))["QSFP-100G-SL"]
    assert entry["_facts"]["unterkategorie"] == "QSFP28"
    assert entry["_facts"]["quell_url"] == "https://cisco.example/ds"
    assert entry["artikelname"] == "" and entry["netto_vk"] is None
    assert entry["attributes"] == [["Formfaktor", "QSFP28"], ["Zustand", "Neu, versiegelt"]]


# --- gold-slice gate: the tightened completeness bar must FAIL on a missing applicable attr ---
def test_gate_fails_missing_anwendung_geschwindigkeit_betriebstemperatur(tmp_path, rules, weights):
    import copy
    from hexcat.validate import validate_dir
    pn, base = _cisco_optic()
    for drop, label in (("Anwendung", "Anwendung"), ("Geschwindigkeit", "Geschwindigkeit"),
                        ("Betriebstemperatur", "Betriebstemperatur")):
        e = copy.deepcopy(base)
        # rebuild attributes without the canonical attr under test (Datenrate aliases Geschwindigkeit)
        e["attributes"] = [a for a in e["attributes"]
                           if a[0] != drop and not (drop == "Geschwindigkeit" and a[0] == "Datenrate")]
        content = tmp_path / f"c_{drop}.json"
        content.write_text(json.dumps({pn: e}, ensure_ascii=False, indent=2), encoding="utf-8")
        recs = reconcile_content(content, brand="Cisco", rules=rules, weights=weights)
        out = tmp_path / f"b_{drop}"
        assemble_bundle(recs, rules, batch="Cisco_Transceivers", category="Transceivers",
                        out_dir=out, build_time="2026-06-12T00:00:00Z")
        res = validate_dir(rules, out)
        assert not res.ok, f"gate must FAIL when {label} is missing"
        assert any(label in (v.field or "") or label.lower() in (v.message or "").lower()
                   for v in res.violations), f"expected a {label} completeness violation"


def test_gate_beschreibung_floor_is_90():
    import yaml
    from pathlib import Path
    r = yaml.safe_load((Path(__file__).resolve().parents[1] / "config" / "rules.yaml").read_text(encoding="utf-8"))
    assert r["budgets"]["beschreibung"]["min_words"] == 90
