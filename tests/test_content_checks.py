from __future__ import annotations

from hexcat.content_checks import (
    banned_hard_hits,
    content_issues,
    count_paragraphs,
    plain_text,
    word_count,
)

# Known-good content (lifted from the example bundle, which passes the gate).
GOOD_KURZ = (
    "<p>Das Cisco SFP-10G-SR ist ein originales 10-Gigabit-SFP-Modul fuer kurze "
    "Distanzen ueber Multimode-Glasfaser im Rechenzentrum und in Campus-Netzwerken.</p>"
    "<p>Es arbeitet bei 850 Nanometern Wellenlaenge, nutzt einen LC-Duplex-Anschluss "
    "und ueberbruckt Strecken von bis zu 300 Metern an kompatiblen Cisco-Switches und "
    "-Routern mit voller Funktionsunterstuetzung im taeglichen Betrieb.</p>"
)
GOOD_BESCH = (
    "<p>Das Cisco SFP-10G-SR wurde fuer 10-Gigabit-Ethernet-Verbindungen ueber "
    "Multimode-Glasfaser entwickelt und ist eine bewaehrte, vielfach erprobte Wahl fuer "
    "Rechenzentren, Aggregations-Layer und Campus-Backbones, in denen kurze bis mittlere "
    "Distanzen jederzeit stabil und zuverlaessig abgedeckt werden muessen.</p>"
    "<p>Das Modul sendet bei einer Wellenlaenge von 850 Nanometern und erreicht ueber "
    "OM3-Fasern Reichweiten von bis zu 300 Metern. Der robuste LC-Duplex-Anschluss sorgt "
    "fuer eine einfache Installation, waehrend die DOM-Funktion eine laufende Ueberwachung "
    "der wichtigsten Betriebsparameter direkt im Switch ermoeglicht.</p>"
    "<p>Dank breiter Plattformkompatibilitaet laesst sich das Modul ohne Zusatzkonfiguration "
    "in vorhandene Cisco-Umgebungen integrieren und sofort produktiv nutzen. Originaler "
    "Cisco-Transceiver fuer den professionellen Einsatz in unternehmenskritischen "
    "Netzwerken.</p>"
)
GOOD_TITEL = "Cisco SFP-10G-SR 10G SR Multimode Modul | Hexwaren"
GOOD_META = (
    "Cisco SFP-10G-SR 10G SFP+ Modul fuer Multimode-Glasfaser, 850 nm, bis 300 m "
    "Reichweite, LC-Duplex und DOM. Originaler Cisco-Transceiver fuer Rechenzentren."
)


def _issues(rules, **overrides):
    kwargs = dict(
        hersteller="Cisco",
        kurzbeschreibung=GOOD_KURZ,
        beschreibung=GOOD_BESCH,
        titel_tag=GOOD_TITEL,
        meta_description=GOOD_META,
        faq_pair_count=3,
    )
    kwargs.update(overrides)
    return content_issues(rules, **kwargs)


def test_helpers():
    assert count_paragraphs(GOOD_KURZ) == (2, 2)
    assert count_paragraphs(GOOD_BESCH) == (3, 3)
    assert plain_text("<p>hallo</p>") == "hallo"
    assert word_count("<p>a b c</p>") == 3


def test_good_content_has_no_issues(rules):
    assert _issues(rules) == []


def test_kurz_paragraph_count(rules):
    issues = _issues(rules, kurzbeschreibung="<p>nur ein absatz mit zu wenigen woertern</p>")
    assert any("Kurzbeschreibung" in i and "<p>" in i for i in issues)


def test_kurz_word_budget(rules):
    issues = _issues(rules, kurzbeschreibung="<p>zu kurz</p><p>auch kurz</p>")
    assert any("Kurzbeschreibung" in i and "words" in i.lower() for i in issues)


def test_beschreibung_missing_closer(rules):
    no_closer = GOOD_BESCH.replace("Originaler Cisco-", "Echter Cisco-")
    issues = _issues(rules, beschreibung=no_closer)
    assert any("closer" in i.lower() or "Originaler Cisco-" in i for i in issues)


def test_titel_too_long(rules):
    long_titel = "Cisco SFP-10G-SR sehr langer ueberlanger Produkttitel hier drin | Hexwaren"
    issues = _issues(rules, titel_tag=long_titel)
    assert any("Titel-Tag" in i and "character" in i.lower() for i in issues)


def test_titel_missing_suffix(rules):
    issues = _issues(rules, titel_tag="Cisco SFP-10G-SR 10G SR Multimode Modul")
    assert any("Titel-Tag" in i and "suffix" in i.lower() for i in issues)


def test_meta_out_of_range(rules):
    issues = _issues(rules, meta_description="zu kurz")
    assert any("Meta-Description" in i for i in issues)


def test_faq_count_out_of_range(rules):
    assert any("FAQ" in i for i in _issues(rules, faq_pair_count=2))
    assert any("FAQ" in i for i in _issues(rules, faq_pair_count=99))


def test_banned_phrase_detected(rules):
    bad = GOOD_KURZ.replace("im taeglichen Betrieb", "sofort lieferbar")
    issues = _issues(rules, kurzbeschreibung=bad)
    assert any("forbidden phrase" in i.lower() for i in issues)
    # And the low-level helper agrees.
    assert "sofort lieferbar" in banned_hard_hits(rules, bad)
