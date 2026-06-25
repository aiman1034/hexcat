"""Structural constants for the output contract.

These are NOT operator-tweakable (they are the byte-exact Ameise contract), so they
live in code rather than config/rules.yaml. Locked values the operator *might* tweak
(vendor map, budgets, banned words, ...) live in config/rules.yaml.

If any tuple/header below changes, the output is no longer Ameise-importable.
"""
from __future__ import annotations

import re

# ---- File 1: MAIN -----------------------------------------------------------
# UTF-8 WITH BOM, delimiter ";", one row per SKU, exactly these 19 columns in order.
MAIN_DELIMITER = ";"
MAIN_BOM = True
MAIN_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "Artikelname",
    "Kurzbeschreibung",
    "Beschreibung",
    "URL-Pfad",
    "Artikelgewicht",
    "Versandgewicht",
    "HAN",
    "Hersteller",
    "Versandklasse",
    "Verkaufseinheit",
    "Titel-Tag (SEO)",          # exact label — never abbreviate
    "Meta-Description (SEO)",   # exact label — never abbreviate
    "Kategorie Ebene 1",
    "Kategorie Ebene 2",
    "Kategorie Ebene 3",
    "Überverkauf Plattform Hexwaren",
    "Bestandsführung aktiv",
    "Überverkäufe möglich",
)

# ---- File 2: ATTRIBUTES -----------------------------------------------------
# UTF-8 WITH BOM, delimiter "," (different from Main!), LONG format.
ATTRIBUTES_DELIMITER = ","
ATTRIBUTES_BOM = True
ATTRIBUTES_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "GTIN",
    "Attributgruppe",
    "Attributname",
    "Attributwert",
    "Sortiernummer",
    "Datentyp (sonst automatisch ermittelt)",
    "Attributart",
)
ATTRIBUTES_DATENTYP = "Wertliste"
ATTRIBUTES_ATTRIBUTART = "Attribut"

# Fixed 14 transceiver attribute order. Tuple of (Attributname, intake_field).
# Sortiernummer is the 1-based index into this tuple.
TRANSCEIVER_ATTRIBUTES: tuple[tuple[str, str], ...] = (
    ("Formfaktor", "Formfaktor"),
    ("Geschwindigkeit", "Geschwindigkeit"),
    ("Transceiver Typ", "TransceiverTyp"),
    ("Fasertyp", "Fasertyp"),
    ("Faseranzahl", "Faseranzahl"),
    ("Anschlusstyp", "Anschlusstyp"),
    ("Länge", "Laenge"),
    ("Wellenlänge", "Wellenlaenge"),
    ("Kabeltyp", "Kabeltyp"),
    ("Reichweite", "Reichweite"),
    ("Anwendung", "Anwendung"),
    ("DOM Unterstützung", "DOMUnterstuetzung"),
    ("Betriebstemperatur", "Betriebstemperatur"),
    ("Standard", "Standard"),
)
# Sortiernummer order aligned to the live-JTL 14-sequence (Phase-2, 2026-06-17): the 3 deterministic
# transpositions vs the prior order — Fasertyp↔Faseranzahl, Wellenlänge↔Kabeltyp, Reichweite↔Anwendung.
# The other 8 positions are unchanged (a Sortiernummer shift on any of them = drift). Both the emitter
# (intake._build_attributes) and the gate (validate sort_tx) derive Sortiernummer from this tuple, so
# they stay in lock-step; the change is visible only against a pre-Phase-2 (cleared) bundle.
ATTRIBUTE_NAMES_ORDERED: tuple[str, ...] = tuple(n for n, _ in TRANSCEIVER_ATTRIBUTES)

# Fixed 15 SWITCH attribute order (Rule-7 signed off 2026-06-14; SWITCHES_SCHEMA_PROPOSAL.md).
# Tuple of (Attributname, intake_field); Sortiernummer = 1-based index. Distinct Merkmal names from
# the transceiver set on purpose (amendments 2 & 4: Port-Geschwindigkeit ≠ transceiver Geschwindigkeit;
# Bauform ≠ transceiver Formfaktor) so the two categories never share a JTL Wertliste.
SWITCH_ATTRIBUTES: tuple[tuple[str, str], ...] = (
    ("Switch-Typ", "SwitchTyp"),
    ("Layer", "Layer"),
    ("Portanzahl", "Portanzahl"),
    ("Port-Konfiguration", "PortKonfiguration"),
    ("Port-Geschwindigkeit", "PortGeschwindigkeit"),
    ("Uplink-Ports", "UplinkPorts"),
    ("PoE", "PoE"),
    ("Switching-Kapazität", "SwitchingKapazitaet"),
    ("Durchsatz", "Durchsatz"),
    ("Bauform", "Bauform"),
    ("Stromversorgung", "Stromversorgung"),
    ("Kühlung", "Kuehlung"),
    ("Stacking", "Stacking"),
    ("Betriebstemperatur", "Betriebstemperatur"),
    ("Anwendung", "Anwendung"),
)
SWITCH_ATTRIBUTE_NAMES_ORDERED: tuple[str, ...] = tuple(n for n, _ in SWITCH_ATTRIBUTES)

# Category dispatch — the pipeline (intake/reconcile/assemble/validate) selects the attribute set,
# Attributgruppe and semantic-check family by the SKU's Kategorie Ebene 2. "Switches" → switch set,
# everything else → the transceiver set (the original, default category).
CATEGORY_SWITCH_L2 = "Switches"


def attributes_for_category(kat_ebene_2: str) -> tuple[tuple[str, str], ...]:
    """Return the fixed (Attributname, intake_field) tuple for a SKU's Kategorie Ebene 2."""
    return SWITCH_ATTRIBUTES if kat_ebene_2 == CATEGORY_SWITCH_L2 else TRANSCEIVER_ATTRIBUTES

# Per-Kat-L3 Kategorie-Ebene-2 overrides for switch-class tokens whose Ebene-2 is NOT the default
# "Switches". Fibre Channel SAN switches are switch-class (they use the SWITCH attribute set + the
# "Switch" Attributgruppe) but live under a distinct Ebene-2 branch. Additive + single-source-of-truth:
# a token absent from this map falls back to the switch/transceiver default, so existing switch and
# transceiver behaviour is byte-for-byte unchanged. Read by intake (emit), assemble (emit) and
# validate (expected) so the emitted and expected Ebene-2 can never drift.
KATEGORIE_EBENE_2_BY_KAT3: dict[str, str] = {
    "Fibre-Channel-Switch": "SAN & Fibre Channel",
    "Fibre-Channel-Director": "SAN & Fibre Channel",   # modular FC director chassis (same SAN branch)
}

# Every Kategorie-Ebene-2 value that denotes a SWITCH-class bundle: the default "Switches" plus any
# per-Kat-L3 override (e.g. "SAN & Fibre Channel"). Used where a layer must tell switch bundles from
# transceiver bundles by Ebene-2 alone (gate L5 weight plausibility) without re-importing the rules.
SWITCH_EBENE2_VALUES: frozenset[str] = frozenset({CATEGORY_SWITCH_L2, *KATEGORIE_EBENE_2_BY_KAT3.values()})

# CHASSIS-SWITCH class (modular directors / chassis): a bare chassis has no fixed ports — line cards
# (and their ports/PoE) are sold separately. Detected purely by Kat-L3 ∈ this set (config-driven, so a
# future Ethernet chassis like Catalyst 9400/9600 or Nexus 9500 extends it by adding its Kat-L3 value —
# no logic rewrite). Chassis-class SKUs carry a REDUCED 7-Merkmal set (Anwendung, Bauform,
# Betriebstemperatur, Kühlung, Stromversorgung, Switch-Typ, Switching-Kapazität), FORBID the port-centric
# Merkmale (Portanzahl/Port-Konfiguration/Port-Geschwindigkeit/PoE/Stacking), and skip the port-rules
# S.1/S.3/S.4 while keeping S.2/S.5. Additive: empty for every non-chassis SKU → no behaviour change.
CHASSIS_KAT3_VALUES: frozenset[str] = frozenset({"Fibre-Channel-Director"})
CHASSIS_REQUIRED_ATTRS: tuple[str, ...] = (
    "Anwendung", "Bauform", "Betriebstemperatur", "Kühlung", "Stromversorgung",
    "Switch-Typ", "Switching-Kapazität",
)
CHASSIS_FORBIDDEN_ATTRS: tuple[str, ...] = (
    "Portanzahl", "Port-Konfiguration", "Port-Geschwindigkeit", "PoE", "Stacking",
)
# A chassis legitimately weighs tens of kg (a 26 HE director with 16 PSUs ≈ 136 kg); the fixed-switch
# L5 ceiling (50 kg) would wrongly flag it. Chassis-class uses this higher ceiling instead.
CHASSIS_WEIGHT_CEILING_KG: float = 200.0


def ebene2_for(kat_ebene_3: str, *, is_switch: bool, switch_default: str, transceiver_default: str) -> str:
    """Resolve the Kategorie Ebene 2 for a SKU: a per-Kat-L3 override wins, else the switch/transceiver
    default. Keeps emit (intake/assemble) and expected (validate) in lock-step from one definition."""
    override = KATEGORIE_EBENE_2_BY_KAT3.get(kat_ebene_3.strip())
    if override is not None:
        return override
    return switch_default if is_switch else transceiver_default

# The physical connector form-factors (the connector subset of the locked Kategorie-Ebene-3
# set). The `Formfaktor` attribute VALUE must be one of these — never a commerce category like
# "DAC Kabel" (the category stays in Kategorie Ebene 3, the connector goes in Formfaktor).
# Ordered most-specific-first so prefix extraction never captures a shorter token by mistake
# (e.g. "QSFP-DD800" before "QSFP-DD", "SFP28" before "SFP").
PHYSICAL_FORMFAKTOR_ORDERED: tuple[str, ...] = (
    "QSFP-DD800", "QSFP-DD", "QSFP112", "QSFP56", "QSFP28-DD", "QSFP28", "QSFP+",
    "OSFP", "SFP-DD", "DSFP", "SFP56", "SFP28", "SFP+", "SFP",
    "CFP2", "CFP", "CPAK", "CXP", "XENPAK", "XFP", "X2", "GBIC",
)
# DSFP (Dual SFP, an SFP-sized 2-lane MSA, distinct from SFP-DD) added Phase-2 (2026-06-17) for the
# Arista C-Y100-* 100G DACs — physically DSFP per Arista's DS, not SFP-DD. Placed after SFP-DD; the
# earliest-position match in physical_formfaktor() returns "DSFP" for a "DSFP…" string (the internal
# "SFP" substring sits at a later index, so it never wins).
PHYSICAL_FORMFAKTOR: frozenset[str] = frozenset(PHYSICAL_FORMFAKTOR_ORDERED)

# Cable categories (Kategorie Ebene 3) — these are direct-attach/fibre assemblies, not optical
# modules. Their Beschreibung word-floor flexes DOWN (a passive DAC needs less prose than a
# coherent transceiver) and they are exempt from optics-only attribute expectations.
CABLE_CATEGORIES: frozenset[str] = frozenset({"DAC Kabel", "AOC Kabel", "MPO Kabel"})

# ---- Category-agnostic MEDIUM classifier (MISSION §8 hardening, 2026-06-19) ------------------
# Decides copper vs optical from GENERIC fields (Artikelnummer tokens + Kabeltyp + Fasertyp +
# Standard), NOT from form-factor — so EVERY category (transceivers / routers / NICs / PSUs / …)
# inherits the media<->DOM gate unchanged (no per-category re-solve). Both PASSIVE and ACTIVE copper
# classify as copper: the active-copper twinax DAC (ACU*/AC* tokens, Kabeltyp "Twinax-Kupfer, aktiv")
# was misread as optical and shipped DOM=Ja (L8 2026-06-19) — this is the permanent fix. An AOC is an
# active *optical* cable -> optical. Used by validate.py media<->DOM AND any DOM (re-)ground path.
_COPPER_PN_TOKEN_RE = re.compile(r"(?:^|[-_])(?:ACU|AC|CU)\d|(?:^|[-_])DAC(?:$|[-_\d])|TWINAX", re.IGNORECASE)
_COPPER_FIELD_RE = re.compile(r"kupfer|copper|twinax|rj-?45|\bcx4\b|cat-?\d|base-?t|twisted", re.IGNORECASE)
_COPPER_STD_RE = re.compile(r"\bCR\d?\b|direct.?attach|twinax|sff-?8431|\bdac\b", re.IGNORECASE)
_OPTICAL_FIELD_RE = re.compile(r"singlemode|multimode|single-?mode|multi-?mode|\bsmf\b|\bmmf\b|glasfaser", re.IGNORECASE)
_AOC_FIELD_RE = re.compile(r"\baoc\b|active optical|aktiv.{0,6}optisch", re.IGNORECASE)


def classify_medium(artikelnummer: str = "", kabeltyp: str = "", fasertyp: str = "",
                    standard: str = "", medientyp: str = "") -> str:
    """Return 'copper' | 'optical' | 'unknown'. Category-agnostic (MISSION §8): keyed off generic
    fields, never form-factor. Copper (passive OR active) is decided FIRST — an active-copper twinax
    DAC must never be read as optical. AOC (active *optical* cable) classifies as optical."""
    if (_COPPER_PN_TOKEN_RE.search(artikelnummer or "")
            or _COPPER_FIELD_RE.search(f"{kabeltyp or ''} {fasertyp or ''} {medientyp or ''}")
            or _COPPER_STD_RE.search(standard or "")):
        return "copper"
    if _OPTICAL_FIELD_RE.search(f"{fasertyp or ''} {medientyp or ''}") or _AOC_FIELD_RE.search(kabeltyp or ""):
        return "optical"
    return "unknown"

# ---- Betriebstemperatur grounding guard (MISSION §8, L8 2026-06-19) --------------------------
# A temperature value that deviates from the commercial default MUST be datasheet-verified PER PART.
# A per-part exception must NEVER propagate to a family sibling by symmetry: QSFP-100G-SM-SR is
# +10..+60 °C (DS c78-736282), but its sibling QSFP-100G-SR1.2 is 0..70 °C — giving SR1.2 the SM-SR
# value "by analogy" was a real error. Category-agnostic: inherited by every category that grounds a
# temperature field.
TEMP_COMMERCIAL_DEFAULT = "0 bis 70 °C"


def ungrounded_temp_exceptions(corrections: dict, verified_pns) -> list:
    """`corrections` = {PN: temp_value}. Return PNs whose temp DEVIATES from the commercial default yet
    are NOT in `verified_pns` (the per-part datasheet-verified allowlist) — i.e. an exception applied
    without that part's own datasheet line (the sibling-symmetry propagation bug). MUST be empty before
    any temperature correction is imported/emitted."""
    vp = set(verified_pns)
    return [pn for pn, val in corrections.items()
            if (val or "").strip() and (val or "").strip() != TEMP_COMMERCIAL_DEFAULT and pn not in vp]

# ---- File 3: PLATFORM FLAG --------------------------------------------------
# UTF-8 WITH BOM. Columns: Artikelnummer + Überverkauf Plattform Hexwaren (= TRUE).
PLATFORMFLAG_DELIMITER = ";"
PLATFORMFLAG_BOM = True
PLATFORMFLAG_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "Überverkauf Plattform Hexwaren",
)

# ---- File 4: PRICES ---------------------------------------------------------
# UTF-8 (NO BOM specified), delimiter ";". Two columns only.
PRICES_DELIMITER = ";"
PRICES_BOM = False
PRICES_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "Netto-VK",
)

# ---- File 5: CONDITION ------------------------------------------------------
# UTF-8 WITH BOM, delimiter ",". Always a SEPARATE file from Attributes.
CONDITION_DELIMITER = ","
CONDITION_BOM = True
CONDITION_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "Attributgruppe",   # empty in every row
    "Attributname",     # "condition"
    "Attributart",      # "Funktionsattribut"
    "Datentyp",         # "Wertliste"
    "Sprache",          # "Deutsch"
    "Attributwert",     # new / used / refurbished
)
CONDITION_ATTRIBUTNAME = "condition"
CONDITION_ATTRIBUTART = "Funktionsattribut"
CONDITION_DATENTYP = "Wertliste"
CONDITION_SPRACHE = "Deutsch"

# ---- File 6: FAQ ------------------------------------------------------------
# UTF-8 WITH BOM, delimiter ",". FAQ cell double-quoted; Q||A pairs joined by ##.
FAQ_DELIMITER = ","
FAQ_BOM = True
FAQ_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "FAQ",
)
FAQ_PAIR_SEP = "##"
FAQ_QA_SEP = "||"

# ---- File 7: VERIFICATION LOG ----------------------------------------------
# UTF-8 (BOM not specified by contract; we emit WITH BOM for Excel/Ameise consistency).
VERIFICATION_LOG_DELIMITER = ","
VERIFICATION_LOG_BOM = True
VERIFICATION_LOG_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "Attributname",
    "Attributwert",
    "Source_URL",
    "Confidence",
    "Verified_At",
)
# Phase-1 source sentinel when the operator supplied no SourceURLs.
VERIFICATION_SOURCE_OPERATOR = "operator-provided"
VERIFICATION_CONFIDENCE_OPERATOR = "operator-provided"

# Optical DOM/DDM=Ja provenance (operator L8 2026-06-17 standing policy). Vendor spec sheets / techspecs
# pages seldom carry a per-part DDM field; a "Ja" rests on SFF-8472 family-standard compliance, so it is
# logged UNIFORMLY as an INFERENCE — never as a datasheet/page ground the source does not actually contain.
DOM_INFERENCE_SOURCE = "SFF-8472 (DDM/DOM) Familienstandard — Inferenz (kein herstellerseitiger Per-Part-Nachweis)"
DOM_INFERENCE_CONFIDENCE = "inference: SFF-8472 family-standard"

# ---- Output filename patterns ----------------------------------------------
# {category} = category slug/name; {batch} = batch name. Names follow the prompt's exact
# output contract; format is built to the v5.0 baseline (v5.1 confirmation pending).
FN_MAIN = "Hexwaren_{category}_Main.csv"
FN_ATTRIBUTES = "Hexwaren_{category}_Attributes.csv"
FN_PLATFORMFLAG = "Hexwaren_{category}_PlatformFlag.csv"
FN_PRICES = "Hexwaren_{category}_Prices.csv"
FN_CONDITION = "Hexwaren_Condition_{batch}.csv"
FN_FAQ = "Hexwaren_FAQ_{batch}.csv"
FN_VERIFICATION_LOG = "Verification_Log_{batch}.csv"
