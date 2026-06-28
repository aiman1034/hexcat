"""Pydantic schemas: raw intake row and the normalized per-SKU record."""
from __future__ import annotations

from pydantic import BaseModel, Field

# Wide intake CSV header (one row per SKU). Order is the template column order.
INTAKE_COLUMNS: tuple[str, ...] = (
    "Artikelnummer",
    "Vendor",
    "KategorieEbene3",
    "Artikelname",
    "Kurzbeschreibung",
    "Beschreibung",
    "TitelTag",
    "MetaDescription",
    "NettoVK",
    "Artikelgewicht",   # optional — else derived from weights.yaml by Formfaktor
    "Versandgewicht",   # optional — else derived
    "Formfaktor",
    "Geschwindigkeit",
    "TransceiverTyp",
    "Faseranzahl",
    "Fasertyp",
    "Anschlusstyp",
    "Laenge",
    "Kabeltyp",
    "Wellenlaenge",
    "Anwendung",
    "Reichweite",
    "DOMUnterstuetzung",
    "Betriebstemperatur",
    "Standard",
    "Condition",
    "FAQ",
    "SourceURLs",       # optional
)


class SkuIntake(BaseModel):
    """A raw, as-read intake row. All fields are strings (CSV cells)."""

    Artikelnummer: str = ""
    Vendor: str = ""
    KategorieEbene3: str = ""
    Artikelname: str = ""
    Kurzbeschreibung: str = ""
    Beschreibung: str = ""
    TitelTag: str = ""
    MetaDescription: str = ""
    NettoVK: str = ""
    Artikelgewicht: str = ""
    Versandgewicht: str = ""
    Formfaktor: str = ""
    Geschwindigkeit: str = ""
    TransceiverTyp: str = ""
    Faseranzahl: str = ""
    Fasertyp: str = ""
    Anschlusstyp: str = ""
    Laenge: str = ""
    Kabeltyp: str = ""
    Wellenlaenge: str = ""
    Anwendung: str = ""
    Reichweite: str = ""
    DOMUnterstuetzung: str = ""
    Betriebstemperatur: str = ""
    Standard: str = ""
    # Switch (Rule-7) intake fields — Betriebstemperatur + Anwendung are shared with the set above.
    SwitchTyp: str = ""
    Layer: str = ""
    Portanzahl: str = ""
    PortKonfiguration: str = ""
    PortGeschwindigkeit: str = ""
    UplinkPorts: str = ""
    PoE: str = ""
    SwitchingKapazitaet: str = ""
    Durchsatz: str = ""
    Bauform: str = ""
    Stromversorgung: str = ""
    Kuehlung: str = ""
    Stacking: str = ""
    # Modular-chassis (Class A) intake fields — only the Catalyst 4500-E/6500-E chassis populate them;
    # every fixed switch leaves them "" (additive, backward-compatible).
    Steckplaetze: str = ""
    SupervisorEngines: str = ""
    Redundanz: str = ""
    # Class-B module intake fields — only Switch-Module & Komponenten SKUs populate them (additive).
    Modultyp: str = ""
    KompatibleSerie: str = ""
    Condition: str = ""
    FAQ: str = ""
    SourceURLs: str = ""


class FaqPair(BaseModel):
    question: str
    answer: str


class AttributeValue(BaseModel):
    """One emitted attribute row (only non-empty attributes are kept)."""

    name: str           # e.g. "Formfaktor"
    value: str
    sortiernummer: int  # 1-based position in the fixed 14 order
    source_url: str     # real URL or VERIFICATION_SOURCE_OPERATOR
    confidence: str = ""  # blank -> operator confidence; "derived:<rule>" for G2b derivations


class SkuRecord(BaseModel):
    """Normalized, derived record ready for byte-exact assembly."""

    artikelnummer: str
    vendor: str
    hersteller: str
    slug: str
    url_pfad: str

    artikelname: str
    kurzbeschreibung: str
    beschreibung: str
    titel_tag: str
    meta_description: str

    kategorie_ebene_1: str
    kategorie_ebene_2: str
    kategorie_ebene_3: str

    netto_vk_de: str          # German-formatted, e.g. "1350,00"
    artikelgewicht_de: str    # German-formatted
    versandgewicht_de: str    # German-formatted
    weights_are_placeholder: bool

    attributes: list[AttributeValue] = Field(default_factory=list)
    skipped_attributes: list[str] = Field(default_factory=list)  # empty intake cells
    # Verification_Log-ONLY rows for grounded prose claims that are not schema attributes (e.g. a woven
    # manufacturer feature code / alt order code): [name, value, source_url(, confidence)]. Emitted to
    # the Verification_Log so "no prose claim without a logged source" (§1000-rule) holds WITHOUT
    # polluting the Attributes CSV. Defaults empty -> zero effect on brands that don't use it.
    extra_log: list = Field(default_factory=list)

    condition: str
    faq_pairs: list[FaqPair] = Field(default_factory=list)
    faq_cell: str = ""        # canonical "Q||A##Q||A" (unquoted; writer quotes it)
