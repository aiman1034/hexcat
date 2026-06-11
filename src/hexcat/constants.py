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
