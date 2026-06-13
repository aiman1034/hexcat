"""§2 G2 — attribute-depth model: populate-or-prove-absent + physics-grounded derivers.

Locks the pure classification (POPULATED / PROVABLY_ABSENT / GAP) for the 14 slots and the
deterministic derivations. The point of these tests is that an empty cell is NEVER silently
ignored: it is either provably-absent (category-gated) or a real GAP — and that the derivers
fill only what physics pins unambiguously, never a guess.
"""
from __future__ import annotations

import pytest

from hexcat import attribute_depth as D
from hexcat import constants as C


# --------------------------------------------------------------------------- #
# Media classification                                                          #
# --------------------------------------------------------------------------- #
def test_optical_module_is_fibre_not_copper_not_cable():
    m = D.classify_media("Transceiver", ["SFP+", "10GBASE-SR", "850 nm"])
    assert m.is_optical_module
    assert m.is_fibre
    assert not m.is_copper
    assert not m.is_cable


def test_copper_detected_from_blob():
    m = D.classify_media("Transceiver", ["SFP+", "10GBASE-T", "RJ-45"])
    assert m.is_copper
    assert not m.is_fibre
    assert not m.is_optical_module


def test_dac_category_is_copper_cable():
    m = D.classify_media("DAC Kabel", ["QSFP28", "100G"])
    assert m.is_cable
    assert m.is_copper
    assert not m.is_fibre
    assert not m.is_optical_module


def test_aoc_cable_is_fibre_but_not_module():
    m = D.classify_media("AOC Kabel", ["QSFP28", "100G"])
    assert m.is_cable
    assert not m.is_copper
    assert m.is_fibre              # glass, but...
    assert not m.is_optical_module  # ...still a cable, not a pluggable module


def test_smart_sfp_flagged():
    m = D.classify_media("Transceiver", ["SFP", "Smart SFP", "framer"])
    assert m.is_smart_sfp
    assert m.is_optical_module


# --------------------------------------------------------------------------- #
# Applicability table integrity                                                 #
# --------------------------------------------------------------------------- #
def test_expected_when_covers_exactly_the_14():
    assert set(D.EXPECTED_WHEN) == set(C.ATTRIBUTE_NAMES_ORDERED)


def test_optional_slots_never_a_gap():
    # Anwendung + Betriebstemperatur are soft: prove-absent is always OK, never a GAP.
    media = D.classify_media("Transceiver", ["SFP+", "10GBASE-SR", "850 nm"])
    assert not D.is_expected("Anwendung", media)
    assert not D.is_expected("Betriebstemperatur", media)


# --------------------------------------------------------------------------- #
# attribute_status: POPULATED / PROVABLY_ABSENT / GAP                           #
# --------------------------------------------------------------------------- #
def test_optical_module_missing_dom_is_a_gap():
    present = {
        "Formfaktor": "SFP+",
        "Geschwindigkeit": "10G",
        "Transceiver Typ": "SR",
        "Anschlusstyp": "LC Duplex",
        "Wellenlänge": "850 nm",
        # DOM Unterstützung deliberately missing -> expected on a module -> GAP
    }
    status = D.attribute_status("Transceiver", present)
    assert status["DOM Unterstützung"] == D.GAP
    assert status["Formfaktor"] == D.POPULATED
    # cable-only slots are provably absent on a module
    assert status["Länge"] == D.PROVABLY_ABSENT
    assert status["Kabeltyp"] == D.PROVABLY_ABSENT


def test_copper_module_optical_slots_provably_absent():
    present = {
        "Formfaktor": "SFP+",
        "Geschwindigkeit": "10G",
        "Anschlusstyp": "RJ-45",
        "Transceiver Typ": "10GBASE-T",
    }
    status = D.attribute_status("Transceiver", present)
    # copper carries no optical carrier / glass
    assert status["Wellenlänge"] == D.PROVABLY_ABSENT
    assert status["Faseranzahl"] == D.PROVABLY_ABSENT
    assert status["Fasertyp"] == D.PROVABLY_ABSENT


def test_cable_length_and_type_expected():
    present = {
        "Formfaktor": "QSFP28",
        "Geschwindigkeit": "100G",
        "Anschlusstyp": "QSFP28",
        # Länge + Kabeltyp missing -> expected on a cable -> GAP
    }
    status = D.attribute_status("DAC Kabel", present)
    assert status["Länge"] == D.GAP
    assert status["Kabeltyp"] == D.GAP
    # a cable has no reach-code / DOM / IEEE-module slots
    assert status["Reichweite"] == D.PROVABLY_ABSENT
    assert status["DOM Unterstützung"] == D.PROVABLY_ABSENT
    assert status["Transceiver Typ"] == D.PROVABLY_ABSENT


def test_smart_sfp_wavelength_provably_absent():
    present = {
        "Formfaktor": "SFP",
        "Geschwindigkeit": "1G",
        "Anschlusstyp": "LC Duplex",
        "Transceiver Typ": "Smart SFP",
    }
    status = D.attribute_status("Transceiver", present)
    # smart-SFP datasheets publish no wavelength -> not a GAP
    assert status["Wellenlänge"] == D.PROVABLY_ABSENT


def test_every_slot_classified():
    status = D.attribute_status("Transceiver", {"Formfaktor": "SFP+"})
    assert set(status) == set(C.ATTRIBUTE_NAMES_ORDERED)
    assert all(v in (D.POPULATED, D.PROVABLY_ABSENT, D.GAP) for v in status.values())


# --------------------------------------------------------------------------- #
# Derivers — physics-grounded, never a guess                                    #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("wl,expect", [
    ("850 nm", "Multimode"),
    ("850nm", "Multimode"),
    ("1310 nm", "Singlemode"),
    ("1270 nm", "Singlemode"),
    ("1610 nm", "Singlemode"),
])
def test_derive_fasertyp_from_wavelength(wl, expect):
    res = D.derive_fasertyp({"Wellenlänge": wl})
    assert res is not None
    assert res[0] == expect
    assert res[1].startswith("derived:")


def test_derive_fasertyp_skips_when_already_present():
    assert D.derive_fasertyp({"Wellenlänge": "850 nm", "Fasertyp": "Multimode"}) is None


def test_derive_fasertyp_none_when_no_wavelength():
    assert D.derive_fasertyp({}) is None


def test_derive_fasertyp_none_for_out_of_window_band():
    # 1064 nm is neither the 8xx multimode VCSEL window nor the 1270-1610 SM telecom
    # band, so the deriver refuses to classify it rather than guess.
    assert D.derive_fasertyp({"Wellenlänge": "1064 nm"}) is None


@pytest.mark.parametrize("conn", [
    "LC Duplex",
    "LC (Duplex)",
    "Duplex LC",
    "Duplex LC (PC/UPC)",
    "Dual LC/PC",
])
def test_derive_faseranzahl_duplex_lc_forms(conn):
    res = D.derive_faseranzahl({"Anschlusstyp": conn})
    assert res is not None
    assert res[0] == "2"


@pytest.mark.parametrize("conn", [
    "Single LC",
    "Single LC/PC (Single-Fiber BiDi)",
    "LC (Simplex, Einzelfaser)",
])
def test_derive_faseranzahl_single_fibre_bidi_is_one(conn):
    # A single-fibre / simplex / single-fibre-BiDi connector pins exactly 1 strand.
    res = D.derive_faseranzahl({"Anschlusstyp": conn})
    assert res is not None and res[0] == "1"


def test_derive_faseranzahl_bare_lc_defaults_duplex():
    # An LC/CS optical connector with no simplex/BiDi hint is duplex by convention -> 2 fibres.
    assert D.derive_faseranzahl({"Anschlusstyp": "LC"})[0] == "2"
    assert D.derive_faseranzahl({"Anschlusstyp": "Dual Duplex CS"})[0] == "2"


@pytest.mark.parametrize("typ,exp", [("SR4", "8"), ("SR8", "16"), ("SR10", "20"), ("VR8", "16")])
def test_derive_faseranzahl_mpo_parallel_from_lanes(typ, exp):
    # MPO ribbon: fibre count = 2 × parallel lanes (SR4->8, SR8/VR8->16, SR10->20).
    res = D.derive_faseranzahl({"Anschlusstyp": "MPO-12", "Transceiver Typ": typ})
    assert res is not None and res[0] == exp


@pytest.mark.parametrize("conn", ["MPO-12", "MPO"])
def test_derive_faseranzahl_mpo_without_lane_context_not_derived(conn):
    # A bare MPO with no lane class / N×rate / N×100GBASE pattern stays ambiguous (not guessed).
    assert D.derive_faseranzahl({"Anschlusstyp": conn}) is None


def test_derive_faseranzahl_skips_when_present():
    assert D.derive_faseranzahl({"Anschlusstyp": "LC Duplex", "Faseranzahl": "2"}) is None


def test_derive_all_fills_both_when_grounded():
    out = D.derive_all({"Wellenlänge": "1310 nm", "Anschlusstyp": "LC Duplex"})
    assert out["Fasertyp"][0] == "Singlemode"
    assert out["Faseranzahl"][0] == "2"


def test_derive_all_empty_when_nothing_grounds():
    assert D.derive_all({"Formfaktor": "SFP+"}) == {}
