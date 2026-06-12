"""Attribute-depth model (§2 G2, ideal-data D3): populate-or-prove-absent.

For each of the locked 14 transceiver attributes, this module says whether a given SKU is
*expected* to carry it — so an empty cell can be classified as PROVABLY_ABSENT (the attribute
does not apply to this kind of part) or as a GAP (it applies, but extraction missed it). That
distinction is what makes "every slot populated or proven absent" auditable instead of asserted.

Pure functions only: category + the SKU's already-known attribute values in, classification out.
No I/O, no model calls, no invention. The deterministic *derivations* (filling a slot from a
physically-implied sibling slot, e.g. Fasertyp from Wellenlänge) live here too, grounded in
physics — they never guess.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import constants as C

# A status for each of the 14 slots on a given SKU.
POPULATED = "POPULATED"
PROVABLY_ABSENT = "PROVABLY_ABSENT"
GAP = "GAP"

# Copper / direct-attach media carry no optical carrier: no wavelength, no fibre type/count.
_COPPER_RE = re.compile(
    r"kupfer|rj-?45|twinax|\bcx4\b|base-t\b|base-cr|base-cx|\bdac\b|cat\s?-?\d|koax|coax",
    re.IGNORECASE,
)
# Smart-SFP framer/mapper modules: optical (SMF) but the datasheet publishes no wavelength.
_SMART_SFP_RE = re.compile(r"smart\s*sfp", re.IGNORECASE)


@dataclass(frozen=True)
class MediaClass:
    """What kind of part this is, derived from its category + known attribute values."""
    is_cable: bool
    is_copper: bool
    is_smart_sfp: bool

    @property
    def is_optical_module(self) -> bool:
        return not self.is_cable and not self.is_copper

    @property
    def is_fibre(self) -> bool:
        # Carries glass: any non-copper optic, modules and fibre cables (AOC/MPO) alike.
        return not self.is_copper


def classify_media(category: str, values: list[str]) -> MediaClass:
    blob = " ".join(values)
    is_cable = category in C.CABLE_CATEGORIES
    is_copper = bool(_COPPER_RE.search(blob)) or category == "DAC Kabel"
    is_smart = bool(_SMART_SFP_RE.search(blob))
    return MediaClass(is_cable=is_cable, is_copper=is_copper, is_smart_sfp=is_smart)


# Each attribute -> a predicate(MediaClass) that is True when the slot is EXPECTED for this SKU.
# `True`/`False` constants are wrapped so the table reads declaratively.
def _always(_m: MediaClass) -> bool: return True
def _optical_module(m: MediaClass) -> bool: return m.is_optical_module
def _non_cable(m: MediaClass) -> bool: return not m.is_cable
def _fibre(m: MediaClass) -> bool: return m.is_fibre and not m.is_cable
def _cable(m: MediaClass) -> bool: return m.is_cable
def _wavelength(m: MediaClass) -> bool: return m.is_optical_module and not m.is_smart_sfp
def _optional(_m: MediaClass) -> bool: return False  # soft: never a GAP, prove-absent always OK

# Applicability table. Names MUST match constants.TRANSCEIVER_ATTRIBUTES exactly.
EXPECTED_WHEN = {
    "Formfaktor": _always,            # the physical connector — every part has one
    "Geschwindigkeit": _always,       # every optic/cable has a line rate
    "Transceiver Typ": _non_cable,    # SR/LR/ER… reach code — modules only
    "Faseranzahl": _fibre,            # fibre count — glass parts only
    "Fasertyp": _fibre,               # Multimode/Singlemode — glass parts only
    "Anschlusstyp": _always,          # connector type — every part terminates somehow
    "Länge": _cable,                  # physical cable length — cables only
    "Kabeltyp": _cable,               # cable construction — cables only
    "Wellenlänge": _wavelength,       # optical carrier — non-copper, non-smart modules
    "Anwendung": _optional,           # use-case label — soft, not on every datasheet
    "Reichweite": _optical_module,    # link reach — modules (cables use Länge)
    "DOM Unterstützung": _optical_module,  # digital optical monitoring — optical modules
    "Betriebstemperatur": _optional,  # operating temp — soft (commercial 0-70 near-universal)
    "Standard": _optical_module,      # IEEE standard — optical Ethernet modules
}
assert set(EXPECTED_WHEN) == set(C.ATTRIBUTE_NAMES_ORDERED), "depth table out of sync with the 14"


def is_expected(attr_name: str, media: MediaClass) -> bool:
    return EXPECTED_WHEN[attr_name](media)


def attribute_status(
    category: str, present: dict[str, str]
) -> dict[str, str]:
    """Classify all 14 slots for one SKU.

    `present` maps Attributname -> value for the attributes the SKU actually carries.
    Returns Attributname -> POPULATED | PROVABLY_ABSENT | GAP.
    """
    media = classify_media(category, [v for v in present.values() if v])
    out: dict[str, str] = {}
    for name in C.ATTRIBUTE_NAMES_ORDERED:
        if present.get(name, "").strip():
            out[name] = POPULATED
        elif is_expected(name, media):
            out[name] = GAP
        else:
            out[name] = PROVABLY_ABSENT
    return out


# --------------------------------------------------------------------------- #
# Deterministic, physics-grounded derivations (G2b uses these to FILL slots).  #
# Each returns (value, rule_label) or None — NEVER a guess. A derivation fires  #
# only when its grounding slot pins the answer unambiguously.                   #
# --------------------------------------------------------------------------- #
# 850 nm is a multimode VCSEL window; the 1270-1610 nm O/C/L bands are singlemode.
_MM_NM_RE = re.compile(r"\b8\d{2}\s*nm\b", re.IGNORECASE)            # 8xx nm  -> MM
_SM_NM_RE = re.compile(r"\b1(?:2[7-9]\d|[3-6]\d{2})\s*nm\b", re.IGNORECASE)  # 1270-1610 -> SM


def derive_fasertyp(present: dict[str, str]) -> tuple[str, str] | None:
    """Fasertyp from Wellenlänge: 8xx nm is multimode, 1270-1610 nm is singlemode."""
    if present.get("Fasertyp", "").strip():
        return None
    wl = present.get("Wellenlänge", "").strip()
    if not wl:
        return None
    if _MM_NM_RE.search(wl):
        return "Multimode", "derived:wavelength-850nm-band->multimode"
    if _SM_NM_RE.search(wl):
        return "Singlemode", "derived:wavelength-1270-1610nm-band->singlemode"
    return None


# A duplex/dual LC connector carries EXACTLY 2 fibres (1 Tx + 1 Rx) — that is what "duplex"
# means physically, in every textual form the datasheets use ("LC (Duplex)", "Duplex LC",
# "Dual LC/PC", ...). We derive 2 from it. We deliberately do NOT derive from:
#   * a *single*/simplex/BiDi LC  -> 1 fibre (single strand, bidirectional)  -> excluded
#   * bare "LC"                    -> ambiguous (could be simplex or duplex)
#   * MPO-n                        -> position count != active fibre count (8-vs-12) -> ambiguous
_LC_DUPLEX_RE = re.compile(r"\blc\b", re.IGNORECASE)
_DUPLEX_WORD_RE = re.compile(r"duplex|dual", re.IGNORECASE)
_SIMPLEX_WORD_RE = re.compile(r"single|simplex|bidi", re.IGNORECASE)


def derive_faseranzahl(present: dict[str, str]) -> tuple[str, str] | None:
    """Faseranzahl from an unambiguous connector: a duplex/dual LC pins 2 fibres.

    Fires only when the connector names LC *and* duplex/dual *and* does not say single/
    simplex/BiDi. Everything ambiguous (bare LC, single-fibre BiDi, MPO) returns None.
    """
    if present.get("Faseranzahl", "").strip():
        return None
    conn = present.get("Anschlusstyp", "").strip()
    if not conn:
        return None
    if (
        _LC_DUPLEX_RE.search(conn)
        and _DUPLEX_WORD_RE.search(conn)
        and not _SIMPLEX_WORD_RE.search(conn)
    ):
        return "2", "derived:duplex-lc-connector->2-fibres"
    return None


DERIVERS = (derive_fasertyp, derive_faseranzahl)


def derive_all(present: dict[str, str]) -> dict[str, tuple[str, str]]:
    """Return {Attributname: (value, rule_label)} for every slot a deriver can fill."""
    out: dict[str, tuple[str, str]] = {}
    name_by_deriver = {"derive_fasertyp": "Fasertyp", "derive_faseranzahl": "Faseranzahl"}
    for d in DERIVERS:
        res = d(present)
        if res is not None:
            out[name_by_deriver[d.__name__]] = res
    return out
