"""Structural constants for the output contract.

These are NOT operator-tweakable (they are the byte-exact Ameise contract), so they
live in code rather than config/rules.yaml. Locked values the operator *might* tweak
(vendor map, budgets, banned words, ...) live in config/rules.yaml.

If any tuple/header below changes, the output is no longer Ameise-importable.
"""
from __future__ import annotations

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
    ("Faseranzahl", "Faseranzahl"),
    ("Fasertyp", "Fasertyp"),
    ("Anschlusstyp", "Anschlusstyp"),
    ("Länge", "Laenge"),
    ("Kabeltyp", "Kabeltyp"),
    ("Wellenlänge", "Wellenlaenge"),
    ("Anwendung", "Anwendung"),
    ("Reichweite", "Reichweite"),
    ("DOM Unterstützung", "DOMUnterstuetzung"),
    ("Betriebstemperatur", "Betriebstemperatur"),
    ("Standard", "Standard"),
)
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

# The physical connector form-factors (the connector subset of the locked Kategorie-Ebene-3
# set). The `Formfaktor` attribute VALUE must be one of these — never a commerce category like
# "DAC Kabel" (the category stays in Kategorie Ebene 3, the connector goes in Formfaktor).
# Ordered most-specific-first so prefix extraction never captures a shorter token by mistake
# (e.g. "QSFP-DD800" before "QSFP-DD", "SFP28" before "SFP").
PHYSICAL_FORMFAKTOR_ORDERED: tuple[str, ...] = (
    "QSFP-DD800", "QSFP-DD", "QSFP112", "QSFP56", "QSFP28", "QSFP+",
    "OSFP", "SFP56", "SFP28", "SFP+", "SFP",
    "CFP2", "CFP", "CPAK", "CXP", "XENPAK", "XFP", "X2", "GBIC", "POM", "CIM8",
)
PHYSICAL_FORMFAKTOR: frozenset[str] = frozenset(PHYSICAL_FORMFAKTOR_ORDERED)

# Cable categories (Kategorie Ebene 3) — these are direct-attach/fibre assemblies, not optical
# modules. Their Beschreibung word-floor flexes DOWN (a passive DAC needs less prose than a
# coherent transceiver) and they are exempt from optics-only attribute expectations.
CABLE_CATEGORIES: frozenset[str] = frozenset({"DAC Kabel", "AOC Kabel", "MPO Kabel"})

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
