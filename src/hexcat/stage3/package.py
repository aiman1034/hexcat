"""Byte-exact v5.0 JTL-Ameise package: schema, derivation, and writers.

Format is locked to the authoritative proof slice (Corrected 7 Part Numbers/
Cisco_Audit_7SKUs_*.csv), confirmed byte-for-byte:
  * encoding   : UTF-8 with BOM (utf-8-sig)
  * line ending: CRLF
  * delimiter  : comma for Main / Attributes / Platform; SEMICOLON for Prices
  * quoting    : csv minimal (only fields containing , " or newline are quoted; " doubled)
  * FAQ        : embedded inside the Beschreibung HTML (no separate FAQ file)
Do NOT re-author this format — it is the reference the operator imports against.
"""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# --- exact column orders (verbatim from the proof-slice headers) -------------------------
MAIN_COLUMNS = [
    "Artikelnummer", "HAN", "Artikelname", "Hersteller", "Titel-Tag (SEO)",
    "Meta-Description (SEO)", "URL-Pfad", "Kategorie Ebene 1", "Kategorie Ebene 2",
    "Kategorie Ebene 3", "Kurzbeschreibung", "Beschreibung", "Artikelgewicht",
    "Versandgewicht", "Versandklasse", "Verkaufseinheit", "Bestandsführung aktiv",
    "Überverkäufe möglich", "Überverkauf Plattform Hexwaren",
]
ATTR_COLUMNS = [
    "Artikelnummer", "GTIN", "Attributgruppe", "Attributname", "Attributwert",
    "Sortiernummer", "Datentyp (sonst automatisch ermittelt)", "Attributart",
]
PLATFORM_COLUMNS = ["Artikelnummer", "Überverkauf Plattform Hexwaren"]
PRICES_COLUMNS = ["Artikelnummer", "Netto-VK"]
VERIFICATION_COLUMNS = [
    "Artikelnummer", "Attributname", "Attributwert", "Source_URL", "Confidence",
    "Verified_At",
]

# --- fixed catalog placement -------------------------------------------------------------
KAT_EBENE_1 = "Netzwerk & Infrastruktur"
KAT_EBENE_2 = "Transceivers & SFP Module"           # catalog category (WITH trailing 'e')
ATTRIBUTGRUPPE = "Transceivers & SFP Modul"          # attribute group (NO trailing 'e')
VERSANDKLASSE = "standard"
VERKAUFSEINHEIT = "Stk"
BESTANDSFUEHRUNG = "Y"
UEBERVERKAEUFE = "Y"
PLATTFORM_FLAG = "TRUE"
DATENTYP = "Wertliste"
ATTRIBUTART = "Attribut"
ZUSTAND_NEU = "Neu, versiegelt"
PRICE_PLACEHOLDER = "0.00"                           # operator-supplied; PRICES-PENDING flag

# --- Beschreibung composition (verbatim section markers from the proof slice) ------------
# The proof-slice Beschreibung is a composed HTML document, NOT free prose: 3 intro <p>,
# then a "Technische Daten" <ul> (rendered from the verified attributes — single source of
# truth, so it can never drift from Attributes.csv), an optional "Kompatibilität" <ul> + the
# fixed matrix note, the FAQ as <p><strong>Q?</strong><br>A</p> blocks, and an optional
# "Verwandte Produkte" <ul> of in-catalog links. The tool composes; the author supplies only
# verified facts (intro text, compatibility lines, FAQ pairs, related PNs).
TECH_HEADING = "Technische Daten:"
KOMPAT_HEADING = "Kompatibilität:"
FAQ_HEADING = "Häufig gestellte Fragen:"
VERWANDT_HEADING = "Verwandte Produkte:"
MATRIX_NOTE = ("Aktuelle Kompatibilität bitte über die Cisco Optics Compatibility Matrix "
               "(TMG) für die jeweilige Plattform und Software-Version prüfen.")
# Condition is a commerce flag, not a datasheet spec — it stays in Attributes.csv but is
# excluded from the embedded Technische-Daten list (matching the proof slice).
_TECH_EXCLUDE = {"Zustand"}

# --- Stage-3 content budgets (from the authoritative proof slice; NO Phase-2 closer) ------
KURZ_P_COUNT = 2
KURZ_MIN_WORDS, KURZ_MAX_WORDS = 40, 80
INTRO_P_COUNT = 3
INTRO_MIN_WORDS, INTRO_MAX_WORDS = 90, 175
TITEL_MAX_CHARS = 60
TITEL_SUFFIX = "| Hexwaren"
META_MIN_CHARS, META_MAX_CHARS = 140, 200
FAQ_MIN_PAIRS, FAQ_MAX_PAIRS = 3, 10

# --- form-factor weight defaults (kg) — used only when the datasheet states none ---------
# (Artikelgewicht, Versandgewicht). Grounded in the proof slice (SFP+ 0.025/0.08, QSFP28
# 0.05/0.15, DAC ~0.15-0.30, XFP 0.03/0.10). Cable lengths refine these in-session.
_WEIGHTS: dict[str, tuple[str, str]] = {
    "SFP": ("0.025", "0.08"), "SFP+": ("0.025", "0.08"), "SFP28": ("0.025", "0.08"),
    "SFP56": ("0.025", "0.08"),
    "QSFP+": ("0.05", "0.15"), "QSFP28": ("0.05", "0.15"), "QSFP56": ("0.05", "0.15"),
    "QSFP112": ("0.05", "0.15"), "QSFP-DD": ("0.06", "0.16"), "QSFP-DD800": ("0.06", "0.16"),
    "OSFP": ("0.06", "0.16"),
    "XFP": ("0.03", "0.10"), "X2": ("0.10", "0.20"), "XENPAK": ("0.12", "0.22"),
    "CFP": ("0.12", "0.22"), "CFP2": ("0.10", "0.20"), "CPAK": ("0.10", "0.20"),
    "CXP": ("0.10", "0.20"), "GBIC": ("0.04", "0.12"),
    "DAC Kabel": ("0.15", "0.25"), "AOC Kabel": ("0.10", "0.20"), "MPO Kabel": ("0.10", "0.20"),
}
_DEFAULT_WEIGHT = ("0.05", "0.15")


def weights_for(unterkategorie: str) -> tuple[str, str]:
    return _WEIGHTS.get(unterkategorie, _DEFAULT_WEIGHT)


def url_slug(pn: str) -> str:
    """PN -> URL slug, matching the proof slice (SFP-H25G-CU1.5M -> sfp-h25g-cu1-5m)."""
    s = pn.strip().lower()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        else:  # '.', '/', ' ', '-', '+' etc. all collapse to a single dash separator
            out.append("-")
    # collapse runs of '-' and trim
    slug = "-".join(seg for seg in "".join(out).split("-") if seg)
    return slug


@dataclass
class SkuFacts:
    """Ledger-derived facts for one SKU (the deterministic spine)."""
    pn: str
    unterkategorie: str                 # locked-22 token -> Kategorie Ebene 3
    quell_url: str = ""
    verifiziert_am: str = ""
    notiz: str = ""


@dataclass
class SkuContent:
    """In-session-authored, datasheet-verified content + verified spec attributes.

    `attributes` is an ordered list of (Attributname, Attributwert) the author has
    round-tripped against the datasheet — it feeds BOTH Attributes.csv and the embedded
    Technische-Daten list. The Beschreibung is either supplied verbatim (`beschreibung`) or
    composed from the structured pieces (`intro` 3×, `kompatibilitaet`, `faq`, `verwandte`)
    via `rendered_beschreibung`. `netto_vk` is operator-supplied (None -> pending). Empty
    prose keeps the SKU in the GENERATED (not IMPORT-READY) state.
    """
    artikelname: str = ""
    titel_tag: str = ""
    meta_description: str = ""
    kurzbeschreibung: str = ""
    beschreibung: str = ""                              # verbatim override; else composed
    intro: list[str] = field(default_factory=list)      # 3 plain-text intro paragraphs
    kompatibilitaet: list[str] = field(default_factory=list)
    faq: list[tuple[str, str]] = field(default_factory=list)
    verwandte: list[tuple[str, str]] = field(default_factory=list)  # (PN, link text)
    attributes: list[tuple[str, str]] = field(default_factory=list)
    netto_vk: str | None = None
    # verification provenance for authored spec values (Attributname -> (Source_URL, Confidence))
    provenance: dict[str, tuple[str, str]] = field(default_factory=dict)

    def rendered_beschreibung(self, brand: str) -> str:
        """The final Beschreibung HTML — the verbatim override if set, else composed."""
        if self.beschreibung:
            return self.beschreibung
        if self.intro:
            return compose_beschreibung(
                intro=self.intro, attributes=self.attributes,
                kompatibilitaet=self.kompatibilitaet, faq=self.faq,
                verwandte=self.verwandte, brand=brand)
        return ""

    def is_complete(self) -> bool:
        has_beschr = bool(self.beschreibung or self.intro)
        return all([self.artikelname, self.titel_tag, self.meta_description,
                    self.kurzbeschreibung, has_beschr]) and bool(self.attributes)


def compose_beschreibung(
    *,
    intro: list[str],
    attributes: list[tuple[str, str]],
    kompatibilitaet: list[str],
    faq: list[tuple[str, str]],
    verwandte: list[tuple[str, str]],
    brand: str,
) -> str:
    """Compose the proof-slice Beschreibung HTML from structured, verified pieces.

    Section order is fixed: intro <p>×N, Technische Daten <ul> (from `attributes`, minus
    Zustand, + empty GTIN), Kompatibilität <ul> + matrix note (omitted if empty), FAQ
    <p><strong>Q?</strong><br>A</p> blocks, Verwandte Produkte <ul> (omitted if empty).
    Related-product hrefs are slugged exactly like Main-file URL-Pfad (`/<brand>/<pn>`).
    """
    brand_slug = url_slug(brand)
    parts: list[str] = [f"<p>{p}</p>" for p in intro]

    tech = [(n, v) for n, v in attributes if n not in _TECH_EXCLUDE]
    if tech:
        lis = "".join(f"<li><strong>{n}:</strong> {v}</li>" for n, v in tech)
        lis += "<li><strong>GTIN:</strong> </li>"
        parts.append(f"<p><strong>{TECH_HEADING}</strong></p><ul>{lis}</ul>")

    if kompatibilitaet:
        lis = "".join(f"<li>{k}</li>" for k in kompatibilitaet)
        parts.append(f"<p><strong>{KOMPAT_HEADING}</strong></p><ul>{lis}</ul>")
        parts.append(f"<p>{MATRIX_NOTE}</p>")

    if faq:
        parts.append(f"<p><strong>{FAQ_HEADING}</strong></p>")
        parts.extend(f"<p><strong>{q}</strong><br>{a}</p>" for q, a in faq)

    if verwandte:
        lis = "".join(
            f'<li><a href="/{brand_slug}/{url_slug(pn)}">{text}</a></li>'
            for pn, text in verwandte)
        parts.append(f"<p><strong>{VERWANDT_HEADING}</strong></p><ul>{lis}</ul>")

    return "".join(parts)


@dataclass
class PackageResult:
    brand: str
    out_dir: Path
    sku_count: int
    state: str                                  # GENERATED | PRICES-PENDING | IMPORT-READY
    pending_content: list[str] = field(default_factory=list)
    pending_prices: list[str] = field(default_factory=list)
    paths: dict[str, Path] = field(default_factory=dict)


def _words(html: str) -> int:
    import re
    return len(re.sub(r"<[^>]+>", "", html).split())


def content_issues(pn: str, c: SkuContent, *, brand: str) -> list[str]:
    """Stage-3 content gate — verify one authored SKU against the proof-slice budgets.

    Returns human-readable problems ([] == passes). Mirrors the authoritative slice:
    Kurzbeschreibung 2×<p>/40-80 words, intro 3×<p>/90-175 words, Titel-Tag <=60 chars
    ending '| Hexwaren', Meta 140-200 chars, FAQ 3-10 pairs. (No Phase-2 authenticity
    closer — the slice carries authenticity in the FAQ/Meta, not a forced tail.)
    """
    issues: list[str] = []
    ko = c.kurzbeschreibung.count("<p>")
    kc = c.kurzbeschreibung.count("</p>")
    if ko != KURZ_P_COUNT or kc != KURZ_P_COUNT:
        issues.append(f"{pn}: Kurzbeschreibung needs exactly {KURZ_P_COUNT} <p>…</p> "
                      f"(found {ko}/{kc}).")
    kw = _words(c.kurzbeschreibung)
    if not (KURZ_MIN_WORDS <= kw <= KURZ_MAX_WORDS):
        issues.append(f"{pn}: Kurzbeschreibung {KURZ_MIN_WORDS}-{KURZ_MAX_WORDS} words "
                      f"(found {kw}).")

    # Intro: validate the structured paragraphs (or the override's leading prose).
    if c.intro:
        if len(c.intro) != INTRO_P_COUNT:
            issues.append(f"{pn}: Beschreibung intro needs exactly {INTRO_P_COUNT} "
                          f"paragraphs (found {len(c.intro)}).")
        iw = sum(_words(p) for p in c.intro)
        if not (INTRO_MIN_WORDS <= iw <= INTRO_MAX_WORDS):
            issues.append(f"{pn}: Beschreibung intro {INTRO_MIN_WORDS}-{INTRO_MAX_WORDS} "
                          f"words (found {iw}).")
    elif not c.beschreibung:
        issues.append(f"{pn}: Beschreibung missing (no intro paragraphs, no override).")

    if len(c.titel_tag) > TITEL_MAX_CHARS:
        issues.append(f"{pn}: Titel-Tag <= {TITEL_MAX_CHARS} chars (found {len(c.titel_tag)}).")
    if not c.titel_tag.endswith(TITEL_SUFFIX):
        issues.append(f"{pn}: Titel-Tag must end with '{TITEL_SUFFIX}'.")

    ml = len(c.meta_description)
    if not (META_MIN_CHARS <= ml <= META_MAX_CHARS):
        issues.append(f"{pn}: Meta-Description {META_MIN_CHARS}-{META_MAX_CHARS} chars "
                      f"(found {ml}).")

    if c.intro and not (FAQ_MIN_PAIRS <= len(c.faq) <= FAQ_MAX_PAIRS):
        issues.append(f"{pn}: FAQ {FAQ_MIN_PAIRS}-{FAQ_MAX_PAIRS} pairs (found {len(c.faq)}).")

    if not c.attributes:
        issues.append(f"{pn}: no verified attributes.")
    return issues


def _derive_attributes(facts: SkuFacts) -> list[tuple[str, str]]:
    """The only spec attributes derivable WITHOUT the datasheet: form factor + condition.
    Everything else (speed, wavelength, reach, FEC, temp, DOM) is authored + verified
    in-session, so the scaffold emits just these two and flags the rest as content-pending."""
    return [("Formfaktor", facts.unterkategorie), ("Zustand", ZUSTAND_NEU)]


def build_package(
    facts: list[SkuFacts],
    *,
    brand: str = "Cisco",
    content: dict[str, SkuContent] | None = None,
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict], PackageResult]:
    """Build the in-memory rows for all four package files + the Verification_Log.

    Returns (main_rows, attr_rows, platform_rows, prices_rows, verification_rows, result).
    `content[pn]` supplies authored prose + verified attributes + price; absent -> scaffold
    (derivable fields only, blank prose, placeholder price), tracked in result.pending_*.
    """
    content = content or {}
    today = date.today().isoformat()
    main_rows: list[dict] = []
    attr_rows: list[dict] = []
    platform_rows: list[dict] = []
    prices_rows: list[dict] = []
    verif_rows: list[dict] = []
    pending_content: list[str] = []
    pending_prices: list[str] = []

    brand_slug = url_slug(brand)

    for f in facts:
        c = content.get(f.pn)
        art_w, ship_w = weights_for(f.unterkategorie)
        url = f"{brand_slug}/{url_slug(f.pn)}"

        main_rows.append({
            "Artikelnummer": f.pn,
            "HAN": f.pn,
            "Artikelname": (c.artikelname if c else ""),
            "Hersteller": brand,
            "Titel-Tag (SEO)": (c.titel_tag if c else ""),
            "Meta-Description (SEO)": (c.meta_description if c else ""),
            "URL-Pfad": url,
            "Kategorie Ebene 1": KAT_EBENE_1,
            "Kategorie Ebene 2": KAT_EBENE_2,
            "Kategorie Ebene 3": f.unterkategorie,
            "Kurzbeschreibung": (c.kurzbeschreibung if c else ""),
            "Beschreibung": (c.rendered_beschreibung(brand) if c else ""),
            "Artikelgewicht": art_w,
            "Versandgewicht": ship_w,
            "Versandklasse": VERSANDKLASSE,
            "Verkaufseinheit": VERKAUFSEINHEIT,
            "Bestandsführung aktiv": BESTANDSFUEHRUNG,
            "Überverkäufe möglich": UEBERVERKAEUFE,
            "Überverkauf Plattform Hexwaren": PLATTFORM_FLAG,
        })

        # Attributes: authored+verified when present, else the two derivable ones.
        attrs = (c.attributes if (c and c.attributes) else _derive_attributes(f))
        for i, (name, value) in enumerate(attrs, start=1):
            attr_rows.append({
                "Artikelnummer": f.pn, "GTIN": "", "Attributgruppe": ATTRIBUTGRUPPE,
                "Attributname": name, "Attributwert": value, "Sortiernummer": str(i),
                "Datentyp (sonst automatisch ermittelt)": DATENTYP, "Attributart": ATTRIBUTART,
            })

        platform_rows.append({"Artikelnummer": f.pn,
                              "Überverkauf Plattform Hexwaren": PLATTFORM_FLAG})

        price = (c.netto_vk if (c and c.netto_vk) else None)
        if price is None:
            pending_prices.append(f.pn)
            price = PRICE_PLACEHOLDER
        prices_rows.append({"Artikelnummer": f.pn, "Netto-VK": price})

        # Verification_Log — one row per emitted fact, with provenance.
        def vlog(name: str, value: str, conf: str, src: str = f.quell_url):
            verif_rows.append({
                "Artikelnummer": f.pn, "Attributname": name, "Attributwert": value,
                "Source_URL": src, "Confidence": conf, "Verified_At": today,
            })

        vlog("Kategorie Ebene 3", f.unterkategorie, "ledger-classify")
        vlog("HAN", f.pn, "ledger-verbatim")
        vlog("Artikelgewicht", art_w,
             "datasheet" if (c and "Artikelgewicht" in c.provenance) else "form-factor-default")
        for name, value in attrs:
            src, conf = (c.provenance.get(name, (f.quell_url, "datasheet"))
                         if c else (f.quell_url, "derived"))
            vlog(name, value, conf, src)

        if not (c and c.is_complete()):
            pending_content.append(f.pn)

    all_complete = not pending_content
    prices_ok = not pending_prices
    if all_complete and prices_ok:
        state = "IMPORT-READY"
    elif all_complete:
        state = "PRICES-PENDING"
    else:
        state = "GENERATED"

    result = PackageResult(
        brand=brand, out_dir=Path("."), sku_count=len(facts), state=state,
        pending_content=pending_content, pending_prices=pending_prices,
    )
    return main_rows, attr_rows, platform_rows, prices_rows, verif_rows, result


def read_ledger_facts(xlsx_path: str | Path) -> list[SkuFacts]:
    """Read the Stage-1 ledger workbook's 'Neue Artikel' sheet into SkuFacts (the spine).

    Columns (verbatim, see workbook.py): Artikelnummer (Part Number) | Hauptkategorie |
    Unterkategorie | Quelle (... Datasheet) | Quell-URL | Verifiziert am | Notiz.
    """
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb["Neue Artikel"]
    facts: list[SkuFacts] = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # header
        cells = (list(row) + [None] * 7)[:7]
        pn, _haupt, unter, _quelle, quell_url, verif_am, notiz = cells
        if not pn:
            continue
        facts.append(SkuFacts(
            pn=str(pn), unterkategorie=str(unter or ""),
            quell_url=str(quell_url or ""), verifiziert_am=str(verif_am or ""),
            notiz=str(notiz or ""),
        ))
    return facts


# --- in-session content sidecar (the $0 authoring bridge) --------------------------------
# A JSON file keyed by Part Number carries the authored, datasheet-verified prose + verified
# spec attributes back into the package. JSON (not Markdown blocks) because the prose embeds
# HTML and an FAQ — any text delimiter would collide. The tool EMITS a template (facts +
# source URL per SKU, content fields blank, the two derivable attributes pre-seeded); Claude
# FILLS it in-session ($0, never an API); the tool READS it into dict[str, SkuContent].
CONTENT_FIELDS = ("artikelname", "titel_tag", "meta_description", "kurzbeschreibung",
                  "beschreibung")


def write_content_template(facts: list[SkuFacts], path: str | Path) -> Path:
    """Emit a JSON content template — one entry per SKU, content blank, facts as `_facts`.

    `_facts` (PN, Unterkategorie, Quell-URL) is the author's spine: every claim is
    round-tripped against that datasheet URL. `attributes` is pre-seeded with the two
    derivable values (Formfaktor, Zustand); the author appends verified spec rows and
    records each in `provenance` (Attributname -> [Source_URL, Confidence]). `netto_vk`
    stays null (operator-supplied). Keys with a leading underscore are hints, ignored on read.
    """
    out = Path(path)
    template: dict[str, dict] = {}
    for f in facts:
        template[f.pn] = {
            "_facts": {"unterkategorie": f.unterkategorie, "quell_url": f.quell_url,
                       "verifiziert_am": f.verifiziert_am},
            "artikelname": "",
            "titel_tag": "",
            "meta_description": "",
            "kurzbeschreibung": "",          # 2× <p>, 40-80 words
            "intro": [],                      # 3 plain-text paragraphs (composed into <p>)
            "kompatibilitaet": [],            # platform support lines (optional)
            "faq": [],                        # [["Frage?","Antwort"], …] 3-10 pairs
            "verwandte": [],                  # [["PN","Linktext"], …] related products (optional)
            "beschreibung": "",              # leave blank — composed from intro/faq/etc.
            "attributes": [list(pair) for pair in _derive_attributes(f)],
            "netto_vk": None,
            "provenance": {},
        }
    out.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def read_content(path: str | Path) -> dict[str, SkuContent]:
    """Read an authored content sidecar JSON into dict[PN -> SkuContent].

    Entries whose prose fields are all blank are skipped (still GENERATED/pending), so a
    partially-authored sidecar yields content only for the SKUs actually filled in.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    content: dict[str, SkuContent] = {}
    for pn, entry in data.items():
        if not isinstance(entry, dict):
            continue
        def _pairs(key: str) -> list[tuple[str, str]]:
            return [(str(a[0]), str(a[1])) for a in (entry.get(key) or [])
                    if isinstance(a, (list, tuple)) and len(a) >= 2]

        attrs = _pairs("attributes")
        prov = {str(k): (str(v[0]), str(v[1]))
                for k, v in (entry.get("provenance") or {}).items()
                if isinstance(v, (list, tuple)) and len(v) >= 2}
        c = SkuContent(
            artikelname=entry.get("artikelname") or "",
            titel_tag=entry.get("titel_tag") or "",
            meta_description=entry.get("meta_description") or "",
            kurzbeschreibung=entry.get("kurzbeschreibung") or "",
            beschreibung=entry.get("beschreibung") or "",
            intro=[str(p) for p in (entry.get("intro") or [])],
            kompatibilitaet=[str(k) for k in (entry.get("kompatibilitaet") or [])],
            faq=_pairs("faq"),
            verwandte=_pairs("verwandte"),
            attributes=attrs,
            netto_vk=(entry.get("netto_vk") or None),
            provenance=prov,
        )
        # Skip wholly-blank scaffold entries so they remain content-pending, not half-emitted.
        if c.kurzbeschreibung or c.beschreibung or c.intro or any(
                getattr(c, fld) for fld in CONTENT_FIELDS):
            content[pn] = c
    return content


def _write_csv(path: Path, columns: list[str], rows: list[dict], *, delimiter: str = ",") -> None:
    """Write a CSV byte-exactly to the proof-slice convention: UTF-8 BOM, CRLF, csv-minimal."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, delimiter=delimiter, lineterminator="\r\n",
                       quoting=csv.QUOTE_MINIMAL, extrasaction="raise")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    path.write_text(buf.getvalue(), encoding="utf-8-sig", newline="")


def write_package(
    facts: list[SkuFacts],
    out_dir: str | Path,
    *,
    brand: str = "Cisco",
    content: dict[str, SkuContent] | None = None,
    stem: str | None = None,
) -> PackageResult:
    """Build + write the package files. Filenames mirror the proof slice naming convention
    `<stem>_<File>.csv` (stem defaults to `<Brand>_Transceivers`)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = stem or f"{brand}_Transceivers"
    main_rows, attr_rows, plat_rows, price_rows, verif_rows, result = build_package(
        facts, brand=brand, content=content)

    paths = {
        "main": out / f"{stem}_v5_0.csv",
        "attributes": out / f"{stem}_Attributes.csv",
        "platform": out / f"{stem}_Platform.csv",
        "prices": out / f"{stem}_Prices.csv",
        "verification": out / f"{stem}_Verification_Log.csv",
    }
    _write_csv(paths["main"], MAIN_COLUMNS, main_rows)
    _write_csv(paths["attributes"], ATTR_COLUMNS, attr_rows)
    _write_csv(paths["platform"], PLATFORM_COLUMNS, plat_rows)
    _write_csv(paths["prices"], PRICES_COLUMNS, price_rows, delimiter=";")
    _write_csv(paths["verification"], VERIFICATION_COLUMNS, verif_rows)

    result.out_dir = out
    result.paths = paths
    return result
