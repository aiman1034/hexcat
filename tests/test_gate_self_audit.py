"""Gate self-audit — one minimal FAILING fixture per known defect class.

The build gate (`validate.py`) is only trustworthy if we can *prove* it rejects every
class of defect it claims to guard against. This suite mutates the clean reference bundle
(the 2-SKU Cisco example, assembled by the `good_bundle` fixture) with the SMALLEST change
that should trip each individual check, and asserts the gate FAILS — with a violation that
actually names the defect, not some unrelated collateral failure.

STANDING RULE (§3 of the mission directive): the gate is "comprehensive" only when every
fixture here is caught AND the clean reference stays green. Any future production defect the
gate misses must be reproduced as a new permanent fixture in this file before it is fixed,
so the gate can never silently regress on it again.

Defect taxonomy mirrors `validate.py`'s check groups:
  S*  structural        (_locate_and_load)
  M*  Main content      (_check_main_content)
  A*  Attributes        (_check_attributes)
  P*  Prices            (_check_prices)
  C*  Condition         (_check_condition)
  F*  FAQ               (_check_faq)
  X*  cross-file        (_check_cross_file)
  V*  verification log   (_check_verification)
"""
from __future__ import annotations

from pathlib import Path

import pytest

import hexcat.validate as V
from hexcat.validate import validate_dir
from conftest import read_bytes_text, write_text_bytes


# --------------------------------------------------------------------------- #
# small mutation helpers                                                       #
# --------------------------------------------------------------------------- #
def _file(d: Path, glob: str) -> Path:
    matches = list(d.glob(glob))
    assert len(matches) == 1, f"{glob} -> {matches}"
    return matches[0]


def _mutate(path: Path, fn):
    write_text_bytes(path, fn(read_bytes_text(path)))


def _has(result, *, field=None, msg=None, filesub=None) -> bool:
    """True if any violation matches the given field / message-substring / file-substring."""
    for v in result.violations:
        if field is not None and v.field != field:
            continue
        if msg is not None and msg.lower() not in v.message.lower():
            continue
        if filesub is not None and filesub not in v.file:
            continue
        return True
    return False


def _drop_lines(path: Path, prefix: str):
    def fn(t: str) -> str:
        keep = [ln for ln in t.split("\n") if not ln.lstrip("﻿").startswith(prefix)]
        return "\n".join(keep)
    _mutate(path, fn)


# Each mutation takes the bundle dir and edits files in place. Kept tiny + targeted so the
# gate failure can only come from the defect under test.
def _repl(glob, old, new, count=1):
    def mutate(d: Path):
        _mutate(_file(d, glob), lambda t: t.replace(old, new, count))
    return mutate


# --------------------------------------------------------------------------- #
# the defect table: (id, mutate(dir), predicate(result) -> bool)              #
# --------------------------------------------------------------------------- #
def _attr_swap_first_two(d: Path):
    """Swap the first two SFP attribute rows (Formfaktor#1, Geschwindigkeit#2) so the file
    order is no longer ascending-by-Sortiernummer, without touching either row's own
    name/Sortiernummer (isolates the canonical-order check from the per-row sort check)."""
    p = _file(d, "*_Attributes.csv")

    def fn(t: str) -> str:
        lines = t.split("\n")
        idxs = [i for i, ln in enumerate(lines) if ln.lstrip("﻿").startswith("SFP-10G-SR,")]
        i1, i2 = idxs[0], idxs[1]
        lines[i1], lines[i2] = lines[i2], lines[i1]
        return "\n".join(lines)

    _mutate(p, fn)


def _make_ambiguous(d: Path):
    f = _file(d, "*_Attributes.csv")
    (f.parent / "Hexwaren_Dup_Attributes.csv").write_bytes(f.read_bytes())


CASES = [
    # ---- S* structural -------------------------------------------------------
    ("S1-missing-file",
     lambda d: _file(d, "*_PlatformFlag.csv").unlink(),
     lambda r: _has(r, msg="missing")),
    ("S2-ambiguous-file",
     _make_ambiguous,
     lambda r: _has(r, msg="ambiguous")),
    ("S3-header-mismatch",
     _repl("*_Main.csv", "Artikelname", "Artikel_Name"),
     lambda r: _has(r, msg="header")),
    ("S4-missing-bom",
     lambda d: _mutate(_file(d, "*_Main.csv"), lambda t: t.lstrip("﻿")),
     lambda r: _has(r, msg="BOM") or _has(r, field="BOM")),

    # ---- M* Main content -----------------------------------------------------
    ("M1-kurz-paragraph-count",
     _repl("*_Main.csv", "Campus-Netzwerken.</p><p>Es arbeitet", "Campus-Netzwerken. Es arbeitet"),
     lambda r: _has(r, field="Kurzbeschreibung", msg="paragraph")),
    ("M2-kurz-word-budget",
     _repl("*_Main.csv", "im taeglichen Betrieb.</p>",
           "im taeglichen Betrieb. " + ("Zusatzwort " * 50) + "</p>"),
     lambda r: _has(r, field="Kurzbeschreibung", msg="word count")),
    ("M3-besch-paragraph-count",
     _repl("*_Main.csv", "muessen.</p><p>Das Modul sendet", "muessen. Das Modul sendet"),
     lambda r: _has(r, field="Beschreibung", msg="paragraph")),
    ("M4-besch-word-budget",
     _repl("*_Main.csv", "Dank breiter Plattformkompatibilitaet",
           ("Zusatzwort " * 130) + "Dank breiter Plattformkompatibilitaet"),
     lambda r: _has(r, field="Beschreibung", msg="word count")),
    ("M5-besch-non-p-tag",
     _repl("*_Main.csv", "Der robuste LC-Duplex-Anschluss",
           "Der <strong>robuste</strong> LC-Duplex-Anschluss"),
     lambda r: _has(r, field="Beschreibung", msg="prose-only")),
    ("M6-inline-qa-question-mark",
     _repl("*_Main.csv", "direkt im Switch ermoeglicht.", "direkt im Switch ermoeglicht?"),
     lambda r: _has(r, field="Beschreibung", msg="Q&A")),
    ("M8-missing-closer",
     _repl("*_Main.csv", "Originaler Cisco-", "Echter Cisco-", count=1),
     lambda r: _has(r, field="Beschreibung", msg="closer")),
    ("M9-titel-too-long",
     _repl("*_Main.csv", "Cisco SFP-10G-SR 10G SR Multimode Modul | Hexwaren",
           "Cisco SFP-10G-SR sehr langer ueberlanger Produkttitel hier drin | Hexwaren"),
     lambda r: _has(r, field="Titel-Tag (SEO)", msg="too long")),
    ("M10-titel-missing-suffix",
     _repl("*_Main.csv", "Multimode Modul | Hexwaren", "Multimode Modul"),
     lambda r: _has(r, field="Titel-Tag (SEO)", msg="suffix")),
    ("M11-meta-out-of-range",
     _repl("*_Main.csv",
           "Cisco SFP-10G-SR 10G SFP+ Modul fuer Multimode-Glasfaser, 850 nm, bis 300 m "
           "Reichweite, LC-Duplex und DOM. Originaler Cisco-Transceiver fuer Rechenzentren.",
           "Zu kurz."),
     lambda r: _has(r, field="Meta-Description (SEO)")),
    ("M12-kategorie-1-mismatch",
     _repl("*_Main.csv", "Netzwerk & Infrastruktur", "Netzwerk und Infrastruktur"),
     lambda r: _has(r, field="Kategorie Ebene 1")),
    ("M13-kategorie-2-mismatch",
     _repl("*_Main.csv", ";Transceivers & SFP Module;", ";Transceivers & SFP Modul;"),
     lambda r: _has(r, field="Kategorie Ebene 2")),
    ("M14-kategorie-3-sonstige",
     _repl("*_Main.csv", ";SFP+;TRUE", ";Sonstige;TRUE"),
     lambda r: _has(r, field="Kategorie Ebene 3", msg="Sonstige")),
    ("M15-kategorie-3-unknown",
     _repl("*_Main.csv", ";SFP+;TRUE", ";FooBar;TRUE"),
     lambda r: _has(r, field="Kategorie Ebene 3", msg="locked set")),
    ("M16-url-slug-unknown",
     _repl("*_Main.csv", "cisco/sfp-10g-sr", "nichtvendor/sfp-10g-sr"),
     lambda r: _has(r, field="URL-Pfad", msg="not in vendor mapping")),
    ("M17-url-no-structure",
     _repl("*_Main.csv", "cisco/sfp-10g-sr", "sfp-10g-sr"),
     lambda r: _has(r, field="URL-Pfad", msg="missing slug")),
    ("M18-url-mismatch",
     _repl("*_Main.csv", "cisco/sfp-10g-sr", "cisco/falscher-pfad"),
     lambda r: _has(r, field="URL-Pfad", msg="must be")),
    ("M19-hersteller-slug-mismatch",
     _repl("*_Main.csv", ";Cisco;standard;", ";Arista;standard;"),
     lambda r: _has(r, field="Hersteller", msg="does not match")),
    ("M20-hersteller-not-allowed",
     _repl("*_Main.csv", ";Cisco;standard;", ";Foobrand;standard;"),
     lambda r: _has(r, field="Hersteller", msg="not in allowed")),
    ("M21-han-not-equal-sku",
     _repl("*_Main.csv", "0,15;SFP-10G-SR;Cisco", "0,15;WRONG-HAN;Cisco"),
     lambda r: _has(r, field="HAN")),
    ("M22-weight-non-numeric",
     _repl("*_Main.csv", ";0,02;0,15;", ";abc;0,15;"),
     lambda r: _has(r, msg="weight is not a valid")),
    ("M23-versand-not-greater",
     _repl("*_Main.csv", ";0,02;0,15;", ";0,20;0,15;"),
     lambda r: _has(r, field="Versandgewicht", msg="greater")),
    ("M24-banned-language",
     _repl("*_Main.csv", "im taeglichen Betrieb", "sofort lieferbar"),
     lambda r: _has(r, msg="banned")),

    # ---- A* Attributes -------------------------------------------------------
    ("A1-attributgruppe-wrong",
     _repl("*_Attributes.csv", "Transceivers & SFP Modul,Formfaktor",
           "Transceivers & SFP Module,Formfaktor"),
     lambda r: _has(r, field="Attributgruppe")),
    ("A2-unknown-attr-name",
     _repl("*_Attributes.csv", ",Formfaktor,SFP+,1,", ",Formfaktr,SFP+,1,"),
     lambda r: _has(r, msg="unknown attribute")),
    ("A3-wrong-sortiernummer",
     _repl("*_Attributes.csv", ",Formfaktor,SFP+,1,Wertliste", ",Formfaktor,SFP+,7,Wertliste"),
     lambda r: _has(r, field="Sortiernummer", msg="wrong Sortiernummer")),
    ("A4-formfaktor-not-physical",
     _repl("*_Attributes.csv", ",Formfaktor,SFP+,1,", ",Formfaktor,DAC Kabel,1,"),
     lambda r: _has(r, msg="physical connector")),
    ("A5-datentyp-not-wertliste",
     _repl("*_Attributes.csv", ",Formfaktor,SFP+,1,Wertliste,Attribut",
           ",Formfaktor,SFP+,1,Freitext,Attribut"),
     lambda r: _has(r, field="Datentyp", msg="Wertliste")),
    ("A6-attributart-not-attribut",
     _repl("*_Attributes.csv", ",Formfaktor,SFP+,1,Wertliste,Attribut",
           ",Formfaktor,SFP+,1,Wertliste,Merkmal"),
     lambda r: _has(r, field="Attributart")),
    ("A7-empty-attributwert",
     _repl("*_Attributes.csv", ",Geschwindigkeit,10 Gigabit,2,", ",Geschwindigkeit,,2,"),
     lambda r: _has(r, field="Attributwert", msg="empty")),
    ("A8-rows-out-of-order",
     _attr_swap_first_two,
     lambda r: _has(r, msg="canonical order")),
    ("A9-missing-wellenlaenge",
     lambda d: _drop_lines(_file(d, "*_Attributes.csv"), "SFP-10G-SR,,Transceivers & SFP Modul,Wellenlänge,"),
     lambda r: _has(r, msg="optical-module completeness")),

    # ---- P* Prices -----------------------------------------------------------
    ("P1-price-dot-decimal",
     _repl("*_Prices.csv", "120,50", "120.50"),
     lambda r: _has(r, field="Netto-VK")),

    # ---- C* Condition --------------------------------------------------------
    ("C1-condition-group-not-empty",
     _repl("Hexwaren_Condition_*.csv", "SFP-10G-SR,,condition", "SFP-10G-SR,X,condition"),
     lambda r: _has(r, field="Attributgruppe", filesub="Condition")),
    ("C2-condition-name-wrong",
     _repl("Hexwaren_Condition_*.csv", ",condition,Funktionsattribut,", ",zustand,Funktionsattribut,"),
     lambda r: _has(r, field="Attributname", filesub="Condition")),
    ("C3-condition-art-wrong",
     _repl("Hexwaren_Condition_*.csv", ",condition,Funktionsattribut,Wertliste,",
           ",condition,Merkmal,Wertliste,"),
     lambda r: _has(r, field="Attributart", filesub="Condition")),
    ("C4-condition-datentyp-wrong",
     _repl("Hexwaren_Condition_*.csv", ",Funktionsattribut,Wertliste,Deutsch,",
           ",Funktionsattribut,Freitext,Deutsch,"),
     lambda r: _has(r, field="Datentyp", filesub="Condition")),
    ("C5-condition-sprache-wrong",
     _repl("Hexwaren_Condition_*.csv", ",Wertliste,Deutsch,new", ",Wertliste,Englisch,new"),
     lambda r: _has(r, field="Sprache", filesub="Condition")),
    ("C6-condition-value-not-allowed",
     _repl("Hexwaren_Condition_*.csv", ",Deutsch,new", ",Deutsch,brandneu"),
     lambda r: _has(r, field="Attributwert", filesub="Condition")),

    # ---- F* FAQ --------------------------------------------------------------
    ("F1-faq-not-double-quoted",
     _repl("Hexwaren_FAQ_*.csv", 'SFP-10G-SR,"Ist das', "SFP-10G-SR,Ist das"),
     lambda r: _has(r, field="FAQ", msg="double-quoted")),
    ("F2-faq-missing-separator",
     lambda d: _mutate(_file(d, "Hexwaren_FAQ_*.csv"), lambda t: t.replace("||", "::")),
     lambda r: _has(r, field="FAQ", msg="separator")),
    ("F3-faq-pair-count",
     _repl("Hexwaren_FAQ_*.csv",
           "##Unterstuetzt das Modul DOM?||Ja, Digital Optical Monitoring wird unterstuetzt.",
           ""),
     lambda r: _has(r, field="FAQ", msg="pair count")),

    # ---- X* cross-file -------------------------------------------------------
    ("X1-sku-set-differs",
     lambda d: _drop_lines(_file(d, "*_Prices.csv"), "QSFP-100G-SR4-S;"),
     lambda r: _has(r, msg="set differs")),

    # ---- V* verification log -------------------------------------------------
    ("V1-attr-value-unbacked",
     lambda d: _drop_lines(_file(d, "Verification_Log_*.csv"), "SFP-10G-SR,Formfaktor,"),
     lambda r: _has(r, msg="verification-log")),
]


@pytest.mark.parametrize("case_id,mutate,predicate", CASES, ids=[c[0] for c in CASES])
def test_gate_catches_defect(good_bundle, rules, case_id, mutate, predicate):
    """Every defect-class mutation must make the gate FAIL, with the *named* violation."""
    d, _ = good_bundle
    mutate(d)
    r = validate_dir(rules, d)
    assert not r.ok, f"{case_id}: gate passed a bundle it should have rejected"
    assert predicate(r), (
        f"{case_id}: gate failed but not on the expected defect. Violations:\n"
        + "\n".join(str(v) for v in r.violations)
    )


def test_clean_reference_stays_green(good_bundle, rules):
    """The unmutated reference bundle must pass — proves the suite isn't failing everything."""
    d, _ = good_bundle
    r = validate_dir(rules, d)
    assert r.ok, "\n".join(str(v) for v in r.violations)


def test_reuse_fail_with_shared_sentence(good_bundle, rules, monkeypatch):
    """Cross-SKU boilerplate: a non-closer sentence shared by >25% of SKUs is a hard FAIL.

    The reference bundle has only 2 SKUs, below SENTENCE_REUSE_MIN_SKUS, so lower the floor
    for this case and inject one identical substantive sentence into BOTH Beschreibungen
    (2/2 = 100% > 25%). Also exercises the gate end-to-end on the reuse detector that the
    tag->space tokenizer fix feeds."""
    monkeypatch.setattr(V, "SENTENCE_REUSE_MIN_SKUS", 2)
    d, _ = good_bundle
    shared = "Dieser geteilte Satz erscheint in jeder einzelnen Produktbeschreibung voellig unveraendert. "
    _mutate(_file(d, "*_Main.csv"),
            lambda t: t.replace("Originaler Cisco-Transceiver", shared + "Originaler Cisco-Transceiver"))
    r = validate_dir(rules, d)
    assert not r.ok
    assert _has(r, field="Beschreibung", msg="boilerplate"), \
        "\n".join(str(v) for v in r.violations)
