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
    url_slug,
    write_package,
)
from hexcat.stage3.package import VERIFICATION_COLUMNS


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
