from __future__ import annotations

from pathlib import Path

import pytest

from hexcat.validate import Validator, valid_gtin, validate_dir
from conftest import read_bytes_text, write_text_bytes


def test_valid_gtin_empty_is_false():
    # valid_gtin itself rejects empty; the GATE separately treats empty as "absent, OK".
    assert valid_gtin("") is False


@pytest.mark.parametrize("code", [
    "00012345600012",  # GTIN-14
    "4006381333931",   # EAN-13 (classic GS1 example)
    "036000291452",    # UPC-A / GTIN-12
    "73513537",        # GTIN-8
])
def test_valid_gtin_accepts_correct_check_digit(code):
    assert valid_gtin(code) is True


@pytest.mark.parametrize("code", [
    "12345678",        # GTIN-8 with wrong check digit
    "4006381333930",   # EAN-13 last digit off by one
    "1234567890",      # wrong length (10)
    "abcdefghijklm",   # non-numeric
    "400638133393X",   # trailing non-digit
])
def test_valid_gtin_rejects_bad(code):
    assert valid_gtin(code) is False


def _file(d: Path, glob: str) -> Path:
    matches = list(d.glob(glob))
    assert len(matches) == 1, f"{glob} -> {matches}"
    return matches[0]


def _mutate(path: Path, fn):
    write_text_bytes(path, fn(read_bytes_text(path)))


def _violations_str(result) -> str:
    return "\n".join(str(v) for v in result.violations)


# ---- the good bundle passes cleanly ----------------------------------------

def test_good_bundle_passes(good_bundle, rules):
    d, _ = good_bundle
    result = validate_dir(rules, d)
    assert result.ok, _violations_str(result)
    assert result.violations == []


# ---- seeded-bad fixtures (acceptance criterion 2) --------------------------

def test_wrong_column_name(good_bundle, rules):
    d, _ = good_bundle
    _mutate(_file(d, "*_Main.csv"),
            lambda t: t.replace("Artikelname", "Artikel_Name", 1))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any("header" in v.message.lower() for v in r.violations)


def test_wide_vs_long_attributes(good_bundle, rules):
    d, _ = good_bundle
    # Replace the long attributes file with a WIDE-format header.
    wide_header = "Artikelnummer," + ",".join(
        ["Formfaktor", "Geschwindigkeit", "Transceiver Typ"]
    )
    write_text_bytes(_file(d, "*_Attributes.csv"),
                     "﻿" + wide_header + "\r\nSFP-10G-SR,SFP+,10 Gigabit,SR\r\n")
    r = validate_dir(rules, d)
    assert not r.ok
    assert any("header" in v.message.lower() or "columns" in v.message.lower()
               for v in r.violations)


def test_dot_decimal_price(good_bundle, rules):
    d, _ = good_bundle
    _mutate(_file(d, "*_Prices.csv"), lambda t: t.replace("120,50", "120.50"))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any(v.field == "Netto-VK" for v in r.violations)


def test_missing_bom(good_bundle, rules):
    d, _ = good_bundle
    _mutate(_file(d, "*_Main.csv"), lambda t: t.lstrip("﻿"))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any("BOM" in v.message or v.field == "BOM" for v in r.violations)


def test_sonstige_in_kat_l3(good_bundle, rules):
    d, _ = good_bundle
    _mutate(_file(d, "*_Main.csv"), lambda t: t.replace(";SFP+;TRUE", ";Sonstige;TRUE"))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any("Sonstige" in v.got or "Sonstige" in v.message for v in r.violations)


def test_module_vs_modul_mixup(good_bundle, rules):
    d, _ = good_bundle
    # Attributgruppe must be "...Modul" (no e); inject the wrong "...Module".
    _mutate(_file(d, "*_Attributes.csv"),
            lambda t: t.replace("& SFP Modul,", "& SFP Module,"))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any(v.field == "Attributgruppe" for v in r.violations)


def test_titel_tag_too_long(good_bundle, rules):
    d, _ = good_bundle
    long_titel = "Cisco SFP-10G-SR sehr langer ueberlanger Produkttitel hier | Hexwaren"
    assert len(long_titel) > 60
    _mutate(_file(d, "*_Main.csv"),
            lambda t: t.replace("Cisco SFP-10G-SR 10G SR Multimode Modul | Hexwaren",
                                long_titel))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any(v.field == "Titel-Tag (SEO)" for v in r.violations)


def test_banned_phrase_present(good_bundle, rules):
    d, _ = good_bundle
    _mutate(_file(d, "*_Main.csv"),
            lambda t: t.replace("im taeglichen Betrieb", "sofort lieferbar"))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any("banned" in v.message.lower() for v in r.violations)


def test_beschreibung_missing_closer(good_bundle, rules):
    d, _ = good_bundle
    _mutate(_file(d, "*_Main.csv"),
            lambda t: t.replace("Originaler Cisco-", "Echter Cisco-"))
    r = validate_dir(rules, d)
    assert not r.ok
    assert any(v.field == "Beschreibung" and "closer" in v.message.lower()
               for v in r.violations)


def test_sku_missing_from_one_file(good_bundle, rules):
    d, _ = good_bundle
    # Drop the QSFP SKU's price row.
    def drop(t: str) -> str:
        lines = t.split("\r\n")
        return "\r\n".join(l for l in lines if not l.startswith("QSFP-100G-SR4-S;"))
    _mutate(_file(d, "*_Prices.csv"), drop)
    r = validate_dir(rules, d)
    assert not r.ok
    assert any("SKU set" in v.field or "set differs" in v.message for v in r.violations)


def test_warn_list_is_not_a_failure(good_bundle, rules):
    d, _ = good_bundle
    # Inject puffery "Premium" -> should WARN, not fail.
    _mutate(_file(d, "*_Main.csv"),
            lambda t: t.replace("originales 10-Gigabit", "Premium 10-Gigabit"))
    r = validate_dir(rules, d)
    assert r.ok, _violations_str(r)
    assert any("Premium" in w.message for w in r.warnings)


# ---- switch semantic S.4: Stacking is keyed off the management tier, EXACT "Managed" -------
# "Smart-Managed" contains the substring "Managed", so a substring test would wrongly pass it;
# S.4 must use an exact match. These pin both directions.

def _switch_vals(switch_typ: str, stacking: str, layer: str = "L2") -> dict:
    return {
        "Switch-Typ": switch_typ, "Layer": layer, "Portanzahl": "10",
        "Port-Konfiguration": "8× 1G-RJ45 + 2× 1G-SFP", "Port-Geschwindigkeit": "1G",
        "PoE": "Nein", "Bauform": "19-Zoll-Rackmontage (1 HE)",
        "Anwendung": "Kleine Bueros", "Betriebstemperatur": "0 bis 50 °C",
        "Stacking": stacking,
    }


def test_s4_smart_managed_stacking_fails(rules, tmp_path):
    v = Validator(rules, tmp_path)
    vals = _switch_vals("Smart-Managed", "Ja – Single-IP-Management")
    v._check_switch_sku("X_Main.csv", "SG350-10", "Smart-Managed Switch", set(vals), vals)
    s4 = [vio for vio in v.result.violations if "S.4" in vio.message]
    assert s4, [str(x) for x in v.result.violations]
    assert s4[0].field == "Stacking"


def test_s4_managed_stacking_ok(rules, tmp_path):
    # A fully Managed switch may stack (StackWise) — no S.4 violation (exact-match companion).
    v = Validator(rules, tmp_path)
    vals = _switch_vals("Managed", "Ja – Cisco StackWise (bis zu 4)")
    v._check_switch_sku("X_Main.csv", "C9300-24T", "Managed Switch (L2)", set(vals), vals)
    assert not [vio for vio in v.result.violations if "S.4" in vio.message], \
        [str(x) for x in v.result.violations]


def test_verification_log_missing_row(good_bundle, rules):
    d, _ = good_bundle
    # Remove one verification-log line; its attribute value is then unbacked.
    def drop_one(t: str) -> str:
        lines = t.split("\r\n")
        kept, dropped = [], False
        for l in lines:
            if not dropped and l.startswith("SFP-10G-SR,Formfaktor,"):
                dropped = True
                continue
            kept.append(l)
        return "\r\n".join(kept)
    _mutate(_file(d, "Verification_Log_*.csv"), drop_one)
    r = validate_dir(rules, d)
    assert not r.ok
    assert any("verification-log" in v.message.lower() for v in r.violations)
