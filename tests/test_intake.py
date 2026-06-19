from __future__ import annotations

import pytest

from hexcat.intake import IntakeError, build_record, normalize_faq
from hexcat.models import SkuIntake


def _base_intake(**over) -> SkuIntake:
    data = dict(
        Artikelnummer="SFP-10G-SR", Vendor="Cisco", KategorieEbene3="SFP+",
        Artikelname="Cisco SFP-10G-SR", NettoVK="120.50",
        Formfaktor="SFP+", Geschwindigkeit="10 Gigabit", TransceiverTyp="SR",
        Condition="", FAQ="Q1?||A1.##Q2?||A2.##Q3?||A3.",
    )
    data.update(over)
    return SkuIntake(**data)


def test_normalize_faq_canonical():
    pairs, cell = normalize_faq("Q1?||A1.##Q2?||A2.##Q3?||A3.", "SKU")
    assert len(pairs) == 3
    assert pairs[0].question == "Q1?" and pairs[0].answer == "A1."
    assert cell == "Q1?||A1.##Q2?||A2.##Q3?||A3."


def test_normalize_faq_friendly_normalizes_to_canonical():
    pairs, cell = normalize_faq("Q1? :: A1. ;; Q2? :: A2. ;; Q3? :: A3.", "SKU")
    assert len(pairs) == 3
    assert cell == "Q1?||A1.##Q2?||A2.##Q3?||A3."  # no spaces around separators


def test_normalize_faq_no_separator_raises():
    with pytest.raises(IntakeError):
        normalize_faq("just a sentence with no separator", "SKU")


def test_vendor_resolution_and_url(rules, weights):
    r = build_record(_base_intake(), rules, weights)
    assert r.hersteller == "Cisco"
    assert r.slug == "cisco"
    assert r.url_pfad == "cisco/sfp-10g-sr"          # sku lowercased
    assert r.netto_vk_de == "120,50"


def test_hpe_aruba_share_slug(rules, weights):
    r = build_record(_base_intake(Vendor="Aruba"), rules, weights)
    assert r.hersteller == "HP" and r.slug == "hpe-aruba"


def test_unknown_vendor_raises(rules, weights):
    with pytest.raises(IntakeError):
        build_record(_base_intake(Vendor="Netgear"), rules, weights)


def test_bad_price_raises(rules, weights):
    with pytest.raises(IntakeError):
        build_record(_base_intake(NettoVK="1.350,00"), rules, weights)


def test_condition_default_and_validation(rules, weights):
    assert build_record(_base_intake(Condition=""), rules, weights).condition == "new"
    assert build_record(_base_intake(Condition="used"), rules, weights).condition == "used"
    with pytest.raises(IntakeError):
        build_record(_base_intake(Condition="brandnew"), rules, weights)


def test_weights_derived_are_placeholder(rules, weights):
    r = build_record(_base_intake(Artikelgewicht="", Versandgewicht=""), rules, weights)
    assert r.weights_are_placeholder is True
    assert r.artikelgewicht_de and r.versandgewicht_de


def test_weights_explicit_not_placeholder(rules, weights):
    r = build_record(_base_intake(Artikelgewicht="0.02", Versandgewicht="0.15"),
                     rules, weights)
    assert r.weights_are_placeholder is False
    assert r.artikelgewicht_de == "0,02" and r.versandgewicht_de == "0,15"


def test_weights_versand_must_exceed_artikel(rules, weights):
    with pytest.raises(IntakeError):
        build_record(_base_intake(Artikelgewicht="0.20", Versandgewicht="0.10"),
                     rules, weights)


def test_weights_partial_raises(rules, weights):
    with pytest.raises(IntakeError):
        build_record(_base_intake(Artikelgewicht="0.20", Versandgewicht=""),
                     rules, weights)


def test_empty_attributes_skipped(rules, weights):
    r = build_record(_base_intake(Laenge="", Kabeltyp=""), rules, weights)
    names = {a.name for a in r.attributes}
    assert "Länge" not in names and "Kabeltyp" not in names
    assert "Länge" in r.skipped_attributes
    # non-empty attribute keeps its canonical Sortiernummer
    ff = next(a for a in r.attributes if a.name == "Formfaktor")
    assert ff.sortiernummer == 1


def test_missing_artikelnummer_raises(rules, weights):
    with pytest.raises(IntakeError):
        build_record(_base_intake(Artikelnummer=""), rules, weights)


# --- §2 G2b: physics-grounded derivations wired into build_record ------------- #
def test_derives_fasertyp_from_wavelength(rules, weights):
    # Wellenlänge known, Fasertyp left empty -> derived Singlemode, stamped + canonically placed.
    r = build_record(
        _base_intake(Wellenlaenge="1310 nm", Fasertyp=""), rules, weights
    )
    ft = next(a for a in r.attributes if a.name == "Fasertyp")
    assert ft.value == "Singlemode"
    assert ft.confidence.startswith("derived:")
    assert ft.sortiernummer == 4            # canonical position in the fixed 14 (live-JTL: Fasertyp→4, Phase-2)
    assert "Fasertyp" not in r.skipped_attributes


def test_derives_faseranzahl_from_duplex_lc(rules, weights):
    r = build_record(
        _base_intake(Anschlusstyp="LC (Duplex)", Faseranzahl=""), rules, weights
    )
    fa = next(a for a in r.attributes if a.name == "Faseranzahl")
    assert fa.value == "2"
    assert fa.confidence.startswith("derived:")


def test_does_not_derive_when_ungrounded(rules, weights):
    # No Wellenlänge, ambiguous connector -> nothing invented; both stay real GAPs.
    r = build_record(
        _base_intake(Wellenlaenge="", Fasertyp="", Anschlusstyp="MPO", Faseranzahl=""),
        rules, weights,
    )
    names = {a.name for a in r.attributes}
    assert "Fasertyp" not in names and "Faseranzahl" not in names
    assert "Fasertyp" in r.skipped_attributes and "Faseranzahl" in r.skipped_attributes


def test_explicit_value_not_overridden_by_derivation(rules, weights):
    # An extracted Fasertyp must win over the deriver and keep operator confidence.
    r = build_record(
        _base_intake(Wellenlaenge="850 nm", Fasertyp="Singlemode"), rules, weights
    )
    ft = next(a for a in r.attributes if a.name == "Fasertyp")
    assert ft.value == "Singlemode"         # operator value kept, not the 850nm->Multimode guess
    assert ft.confidence == ""              # not a derivation
