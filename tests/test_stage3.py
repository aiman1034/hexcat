"""Stage-3 v5.0 package generator tests — byte-exact format against the proof slice.

The authoritative reference is Corrected 7 Part Numbers/Cisco_Audit_7SKUs_*.csv: UTF-8 BOM,
CRLF, comma-delimited (Prices semicolon), csv-minimal quoting, FAQ embedded in Beschreibung.
These tests freeze the FORMAT (headers/delimiters/encoding/quoting/state machine); the German
prose itself is authored in-session and verified separately.
"""
from __future__ import annotations

import csv
import io

from hexcat.stage3 import (
    ATTR_COLUMNS,
    MAIN_COLUMNS,
    PLATFORM_COLUMNS,
    PRICES_COLUMNS,
    SkuContent,
    SkuFacts,
    build_package,
    compose_beschreibung,
    content_issues,
    read_content,
    url_slug,
    write_content_template,
    write_package,
)
from hexcat.stage3.package import MATRIX_NOTE, VERIFICATION_COLUMNS


def test_url_slug_matches_proof_slice():
    assert url_slug("QSFP-100G-SL") == "qsfp-100g-sl"
    assert url_slug("SFP-H25G-CU1.5M") == "sfp-h25g-cu1-5m"     # dot -> dash (slice-verified)
    assert url_slug("SFP-H25G-CU2.5M") == "sfp-h25g-cu2-5m"
    assert url_slug("XFP10GER192IRRGDRF") == "xfp10ger192irrgdrf"


def test_main_header_order_matches_slice():
    assert MAIN_COLUMNS[:6] == [
        "Artikelnummer", "HAN", "Artikelname", "Hersteller", "Titel-Tag (SEO)",
        "Meta-Description (SEO)",
    ]
    assert MAIN_COLUMNS[-1] == "Überverkauf Plattform Hexwaren"
    assert len(MAIN_COLUMNS) == 19
    assert ATTR_COLUMNS[6] == "Datentyp (sonst automatisch ermittelt)"


def test_scaffold_fills_derivable_and_flags_pending():
    facts = [SkuFacts(pn="QSFP-100G-SL", unterkategorie="QSFP28",
                      quell_url="https://cisco.example/ds")]
    main, attrs, plat, prices, verif, res = build_package(facts, brand="Cisco")
    row = main[0]
    assert row["Artikelnummer"] == "QSFP-100G-SL"
    assert row["HAN"] == "QSFP-100G-SL"
    assert row["Hersteller"] == "Cisco"
    assert row["URL-Pfad"] == "cisco/qsfp-100g-sl"
    assert row["Kategorie Ebene 1"] == "Netzwerk & Infrastruktur"
    assert row["Kategorie Ebene 2"] == "Transceivers & SFP Module"   # WITH 'e'
    assert row["Kategorie Ebene 3"] == "QSFP28"
    assert row["Überverkauf Plattform Hexwaren"] == "TRUE"
    assert row["Artikelgewicht"] == "0.05" and row["Versandgewicht"] == "0.15"
    assert row["Artikelname"] == ""                                  # prose pending
    # attribute group is the NO-'e' form; derivable attrs only in scaffold
    assert attrs[0]["Attributgruppe"] == "Transceivers & SFP Modul"
    assert {a["Attributname"] for a in attrs} == {"Formfaktor", "Zustand"}
    assert plat[0]["Überverkauf Plattform Hexwaren"] == "TRUE"
    assert prices[0]["Netto-VK"] == "0.00"
    assert res.state == "GENERATED"
    assert res.pending_content == ["QSFP-100G-SL"]
    assert res.pending_prices == ["QSFP-100G-SL"]


def test_import_ready_when_content_and_price_present():
    facts = [SkuFacts(pn="SFP-10G-SR", unterkategorie="SFP+", quell_url="https://x")]
    content = {"SFP-10G-SR": SkuContent(
        artikelname="Cisco SFP-10G-SR 10GBASE-SR SFP+ — 300 m OM3",
        titel_tag="Cisco SFP-10G-SR 10G SR | Hexwaren",
        meta_description="Original Cisco SFP-10G-SR kaufen — 10GBASE-SR, 850 nm, 300 m OM3.",
        kurzbeschreibung="<p>Kurz.</p><p>Text.</p>",
        beschreibung="<p>Lang.</p><p>Mehr.</p><p>Originaler Cisco-Transceiver.</p>",
        attributes=[("Formfaktor", "SFP+"), ("Geschwindigkeit", "10 Gbit/s"),
                    ("Zustand", "Neu, versiegelt")],
        netto_vk="89.00",
    )}
    main, attrs, plat, prices, verif, res = build_package(facts, brand="Cisco", content=content)
    assert res.state == "IMPORT-READY"
    assert not res.pending_content and not res.pending_prices
    assert prices[0]["Netto-VK"] == "89.00"
    assert {a["Attributname"] for a in attrs} == {"Formfaktor", "Geschwindigkeit", "Zustand"}


def test_prices_pending_when_content_complete_but_no_price():
    facts = [SkuFacts(pn="SFP-10G-SR", unterkategorie="SFP+")]
    content = {"SFP-10G-SR": SkuContent(
        artikelname="A", titel_tag="T", meta_description="M",
        kurzbeschreibung="<p>k</p>", beschreibung="<p>b</p>",
        attributes=[("Formfaktor", "SFP+")],
    )}
    *_, res = build_package(facts, brand="Cisco", content=content)
    assert res.state == "PRICES-PENDING"


def test_written_files_are_bom_crlf_and_correct_delimiters(tmp_path):
    facts = [SkuFacts(pn="QSFP-100G-SL", unterkategorie="QSFP28", quell_url="https://x")]
    res = write_package(facts, tmp_path, brand="Cisco")
    main_bytes = res.paths["main"].read_bytes()
    assert main_bytes.startswith(b"\xef\xbb\xbf")                    # UTF-8 BOM
    assert b"\r\n" in main_bytes                                     # CRLF
    text = main_bytes.decode("utf-8-sig")
    assert text.splitlines()[0] == ",".join(MAIN_COLUMNS)           # comma-delimited header
    # Prices is semicolon-delimited
    prices_text = res.paths["prices"].read_bytes().decode("utf-8-sig")
    assert prices_text.splitlines()[0] == "Artikelnummer;Netto-VK"
    assert res.paths["verification"].exists()


def test_csv_minimal_quoting_doubles_embedded_quotes(tmp_path):
    """Beschreibung with embedded quotes (related-product <a href>) must round-trip clean —
    the proof slice doubles inner quotes via csv-minimal; verify ours parses back identically."""
    facts = [SkuFacts(pn="X", unterkategorie="SFP+")]
    desc = '<p>See <a href="/cisco/y">Cisco Y, fast</a></p>'        # has comma AND quotes
    content = {"X": SkuContent(
        artikelname="N", titel_tag="T", meta_description="M",
        kurzbeschreibung="<p>k</p>", beschreibung=desc,
        attributes=[("Formfaktor", "SFP+")], netto_vk="1.00")}
    res = write_package(facts, tmp_path, brand="Cisco", content=content)
    text = res.paths["main"].read_bytes().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    assert rows[0]["Beschreibung"] == desc                          # exact round-trip


def test_content_template_seeds_facts_and_derivable_attrs(tmp_path):
    facts = [SkuFacts(pn="QSFP-100G-SL", unterkategorie="QSFP28", quell_url="https://ds")]
    p = write_content_template(facts, tmp_path / "content.json")
    import json
    data = json.loads(p.read_text(encoding="utf-8"))
    entry = data["QSFP-100G-SL"]
    assert entry["_facts"]["unterkategorie"] == "QSFP28"            # spine carried for the author
    assert entry["_facts"]["quell_url"] == "https://ds"            # datasheet to round-trip against
    assert entry["artikelname"] == "" and entry["netto_vk"] is None # blank prose, no price
    assert entry["attributes"] == [["Formfaktor", "QSFP28"], ["Zustand", "Neu, versiegelt"]]


def test_blank_template_reads_as_no_content_then_lifts_when_filled(tmp_path):
    facts = [SkuFacts(pn="SFP-10G-SR", unterkategorie="SFP+", quell_url="https://x")]
    p = write_content_template(facts, tmp_path / "content.json")
    # Untouched template: all prose blank -> read_content yields nothing -> still GENERATED.
    assert read_content(p) == {}
    *_, res0 = build_package(facts, brand="Cisco", content=read_content(p))
    assert res0.state == "GENERATED"
    # Author it in-session (prose + a verified attr + provenance), leave price null.
    import json
    data = json.loads(p.read_text(encoding="utf-8"))
    data["SFP-10G-SR"].update({
        "artikelname": "Cisco SFP-10G-SR 10GBASE-SR SFP+ — 300 m OM3",
        "titel_tag": "Cisco SFP-10G-SR 10G SR | Hexwaren",
        "meta_description": "Original Cisco SFP-10G-SR — 10GBASE-SR, 850 nm, 300 m OM3.",
        "kurzbeschreibung": "<p>k</p><p>k2</p>",
        "beschreibung": "<p>b</p><p>b2</p><p>Originaler Cisco-Transceiver.</p>",
        "attributes": [["Formfaktor", "SFP+"], ["Geschwindigkeit", "10 Gbit/s"],
                       ["Zustand", "Neu, versiegelt"]],
        "provenance": {"Geschwindigkeit": ["https://x", "datasheet"]},
    })
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    authored = read_content(p)
    assert set(authored) == {"SFP-10G-SR"}
    assert authored["SFP-10G-SR"].provenance["Geschwindigkeit"] == ("https://x", "datasheet")
    main, attrs, plat, prices, verif, res = build_package(
        facts, brand="Cisco", content=authored)
    assert res.state == "PRICES-PENDING"                            # prose complete, price null
    assert {a["Attributname"] for a in attrs} == {"Formfaktor", "Geschwindigkeit", "Zustand"}
    # Provenance flows into the Verification_Log.
    geo = [v for v in verif if v["Attributname"] == "Geschwindigkeit"][0]
    assert geo["Source_URL"] == "https://x" and geo["Confidence"] == "datasheet"


def test_compose_beschreibung_matches_proof_section_order():
    """Composed Beschreibung reproduces the proof-slice section structure & markers, and the
    Technische-Daten list is rendered from attributes (single source of truth, no Zustand)."""
    html = compose_beschreibung(
        intro=["Erster Absatz.", "Zweiter Absatz.", "Dritter Absatz."],
        attributes=[("Formfaktor", "QSFP28"), ("Geschwindigkeit", "100 Gbit/s"),
                    ("Zustand", "Neu, versiegelt")],
        kompatibilitaet=["Cisco Nexus 9300 — NX-OS 7.0(3)I7(1) und höher"],
        faq=[("Frage eins?", "Antwort eins."), ("Frage zwei?", "Antwort zwei."),
             ("Frage drei?", "Antwort drei.")],
        verwandte=[("QSFP-100G-SR4-S", "Cisco QSFP-100G-SR4-S — 100G SR4")],
        brand="Cisco",
    )
    # intro paragraphs first, in order
    assert html.startswith("<p>Erster Absatz.</p><p>Zweiter Absatz.</p><p>Dritter Absatz.</p>")
    # Technische Daten rendered from attributes, Zustand excluded, empty GTIN appended
    assert "<p><strong>Technische Daten:</strong></p><ul>" in html
    assert "<li><strong>Formfaktor:</strong> QSFP28</li>" in html
    assert "<li><strong>Geschwindigkeit:</strong> 100 Gbit/s</li>" in html
    assert "Zustand" not in html.split("Kompatibilität")[0]        # not in the tech list
    assert "<li><strong>GTIN:</strong> </li>" in html
    # Kompatibilität + the fixed matrix note
    assert f"<p><strong>Kompatibilität:</strong></p>" in html
    assert MATRIX_NOTE in html
    # FAQ block markup
    assert "<p><strong>Häufig gestellte Fragen:</strong></p>" in html
    assert "<p><strong>Frage eins?</strong><br>Antwort eins.</p>" in html
    # Verwandte Produkte with slugged in-catalog href
    assert ('<li><a href="/cisco/qsfp-100g-sr4-s">Cisco QSFP-100G-SR4-S — 100G SR4</a></li>'
            in html)
    # section order: intro < tech < kompat < faq < verwandte
    assert (html.index("Technische Daten") < html.index("Kompatibilität")
            < html.index("Häufig gestellte Fragen") < html.index("Verwandte Produkte"))


def test_compose_omits_optional_empty_sections():
    html = compose_beschreibung(
        intro=["Nur Intro."], attributes=[("Formfaktor", "SFP+")],
        kompatibilitaet=[], faq=[], verwandte=[], brand="Cisco")
    assert "Kompatibilität" not in html and MATRIX_NOTE not in html
    assert "Häufig gestellte Fragen" not in html
    assert "Verwandte Produkte" not in html
    assert "Technische Daten" in html                              # attrs present -> rendered


def test_structured_content_round_trips_and_composes_in_package(tmp_path):
    facts = [SkuFacts(pn="X2-10GB-LR", unterkategorie="X2", quell_url="https://ds")]
    content = {"X2-10GB-LR": SkuContent(
        artikelname="Cisco X2-10GB-LR 10GBASE-LR X2 Modul — 10 km SMF, 1310 nm",
        titel_tag="Cisco X2-10GB-LR 10G LR 10 km | Hexwaren",
        meta_description=("Original Cisco X2-10GB-LR 10GBASE-LR X2 Modul kaufen — 1310 nm "
                          "Singlemode, 10 km, Dual-SC. Neu, versiegelt. Für Cisco Catalyst "
                          "und Router mit X2-Steckplatz."),
        kurzbeschreibung=("<p>Das Cisco X2-10GB-LR ist ein originales 10GBASE-LR X2 Modul "
                          "mit Dual-SC-Anschluss und überträgt 10 Gigabit Ethernet über "
                          "1310 nm bis zehn Kilometer auf Singlemode-Faser nach IEEE "
                          "802.3ae im Campus und Rechenzentrum.</p><p>Voll hot-swappable "
                          "und mit Cisco Quality-ID ausgestattet, fügt es sich nahtlos in "
                          "Catalyst Switches und Router mit X2-Steckplatz ein und bietet "
                          "ausreichend Leistungsreserve für lange Backbone-Strecken.</p>"),
        intro=["Das Cisco X2-10GB-LR ist ein 10GBASE-LR X2 Modul mit Dual-SC-Anschluss für "
               "Singlemode-Faser, das 10 Gigabit Ethernet über 1310 nm bis zehn Kilometer "
               "überträgt und sich in Cisco Catalyst Switches und Router mit X2-Steckplatz "
               "einfügt für klassische Backbone- und Campus-Verbindungen im Rechenzentrum.",
               "Mit einer Sendeleistung von 0,5 dBm und einer Empfangsempfindlichkeit bis "
               "-14,4 dBm bietet das Modul ausreichend Reserve für lange Singlemode-Strecken "
               "nach IEEE 802.3ae und bleibt dabei voll hot-swappable im laufenden Betrieb.",
               "Die Leistungsaufnahme liegt unter vier Watt je Modul, der Betrieb erfolgt im "
               "kommerziellen Temperaturbereich von null bis siebzig Grad Celsius, und die "
               "Cisco Quality-ID stellt die Erkennung als geprüftes Original-Modul sicher."],
        kompatibilitaet=["Cisco Catalyst und Router mit X2-Steckplatz — siehe Xenpak/X2 "
                         "Compatibility Matrix"],
        faq=[("Ist dies ein originales Cisco-Modul?",
              "Ja, Original Cisco-Neuware aus autorisiertem Kanal, versiegelt."),
             ("Welche Faser wird benötigt?",
              "Singlemode-Faser (SMF, G.652) mit Dual-SC-Anschluss, bis 10 km."),
             ("Welche Wellenlänge nutzt das Modul?", "1310 nm nach IEEE 802.3ae 10GBASE-LR.")],
        verwandte=[("X2-10GB-ER", "Cisco X2-10GB-ER — 10GBASE-ER 40 km SMF")],
        attributes=[("Formfaktor", "X2"), ("Geschwindigkeit", "10 Gbit/s"),
                    ("Standard", "IEEE 802.3ae 10GBASE-LR"), ("Wellenlänge", "1310 nm"),
                    ("Reichweite", "10 km"), ("Anschluss", "Dual SC/PC"),
                    ("Fasertyp", "Singlemode (SMF, G.652)"), ("Zustand", "Neu, versiegelt")],
        provenance={"Reichweite": ("https://ds", "datasheet")},
    )}
    assert content_issues("X2-10GB-LR", content["X2-10GB-LR"], brand="Cisco") == []
    res = write_package(facts, tmp_path, brand="Cisco", content=content)
    assert res.state == "PRICES-PENDING"                            # complete prose, no price
    text = res.paths["main"].read_bytes().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    b = rows[0]["Beschreibung"]
    assert b.startswith("<p>Das Cisco X2-10GB-LR")
    assert "<li><strong>Reichweite:</strong> 10 km</li>" in b
    assert MATRIX_NOTE in b
    assert '<li><a href="/cisco/x2-10gb-er">' in b                  # slugged related link


def test_content_gate_flags_budget_violations():
    bad = SkuContent(
        artikelname="x", titel_tag="Way too long a title tag that definitely exceeds sixty chars | Hexwaren",
        meta_description="too short",
        kurzbeschreibung="<p>only one paragraph here</p>",
        intro=["one", "two"],                                       # 2 not 3 paragraphs
        faq=[("q?", "a")],                                          # 1 < 3 pairs
        attributes=[("Formfaktor", "SFP+")],
    )
    issues = content_issues("BAD", bad, brand="Cisco")
    joined = " ".join(issues)
    assert "Kurzbeschreibung needs exactly 2" in joined
    assert "intro needs exactly 3" in joined
    assert "Titel-Tag <= 60" in joined
    assert "Meta-Description 140-200" in joined
    assert "FAQ 3-10 pairs" in joined
