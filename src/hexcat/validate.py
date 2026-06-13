"""The validation gate.

Runs AFTER assembly, against the files on disk (so `hexcat validate --dir` works on
any already-produced bundle). Every failure is a hard stop with an actionable, located
message: {file, SKU, field, expected, got}. Never let a non-compliant file ship.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import constants as C
from .config import Rules
from .content_checks import (
    banned_hard_hits,
    banned_warn_hits,
    closer_brand_tail,
    closer_present,
    count_paragraphs,
    plain_text,
    reuse_candidate_sentences,
    word_count,
)
from .writers import BOM, GERMAN_DECIMAL_RE

# Glob patterns to locate each role's file in a bundle directory.
ROLE_GLOBS = {
    "main": "Hexwaren_*_Main.csv",
    "attributes": "Hexwaren_*_Attributes.csv",
    "platformflag": "Hexwaren_*_PlatformFlag.csv",
    "prices": "Hexwaren_*_Prices.csv",
    "condition": "Hexwaren_Condition_*.csv",
    "faq": "Hexwaren_FAQ_*.csv",
    "verification": "Verification_Log_*.csv",
}
SIX_FILES = ("main", "attributes", "platformflag", "prices", "condition", "faq")

# Beschreibung must be PROSE-ONLY (item 6): the only markup allowed is <p>/</p>. A spec
# <ul>, an emphasis <strong>, a <br> or an <a> anchor is a divergent-writer composition
# artifact and a hard fail — specs live in the Attributes file, FAQ in the FAQ file.
_ANY_TAG_RE = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")
_ALLOWED_BESCH_TAGS = {"p"}
# The Beschreibung word-floor flexes DOWN for sparse cable/DAC assemblies (item 6): a passive
# DAC needs less grounded prose than a coherent transceiver, and we NEVER pad to a floor.
# Modules keep the full rules floor; cables get this lower floor.
CABLE_BESCHREIBUNG_MIN_WORDS = 90   # gold-slice bar: every Beschreibung >= 90 words, cables included

# --- cross-SKU sentence reuse (FAIL) ---------------------------------------------------
# A non-closer body sentence shared by more than this fraction of a brand's SKUs is
# boilerplate padding (a genuine shared spec belongs in the Attributes CSV, not the prose).
# It promotes to a hard FAIL; below it we still WARN so near-misses stay visible.
SENTENCE_REUSE_FAIL_FRACTION = 0.25
# Only escalate to FAIL once the brand bundle is big enough that a fraction is meaningful
# (a 3-SKU slice trivially shares sentences; that is a WARN, not a ship-blocker).
SENTENCE_REUSE_MIN_SKUS = 8
# The ONLY by-design-identical sentence is the "Original…" authenticity closer, exempted
# below via `startswith("original")`. Everything else — including sealed/new-goods/Quality-ID
# *condition* statements — must be varied per SKU (e.g. by welding the part number) to stay
# unique, exactly like every physics sentence. We deliberately do NOT blanket-exempt
# "versiegelt/Neuware" wording: a broad keyword exemption would silently mask unvaried
# boilerplate (it previously hid Arista's 243/347 cable + 104/347 module condition sentences).

# --- cross-SKU FAQ uniqueness (G5) -----------------------------------------------------
# Each SKU's FAQ must add per-SKU value. Individual pairs may legitimately recur — the
# universal authenticity question ("Ist dies ein originales <Brand>-Produkt?") and category
# questions (cable power, host compatibility) — but the SUBSTANTIVE remainder (everything
# except the by-design authenticity pair) must NOT be byte-identical across many SKUs, which
# would be copy-pasted boilerplate with zero per-SKU value. Calibrated to the shipped data
# (max legitimate duplication is a 2-SKU BiDi -D/-U pair): WARN at 2, FAIL at 4.
FAQ_CELL_REUSE_WARN_SKUS = 2
FAQ_CELL_REUSE_FAIL_SKUS = 4
_FAQ_AUTHENTICITY_RE = re.compile(r"^\s*ist dies ein original", re.IGNORECASE)


# --- optical-module completeness (FAIL) ------------------------------------------------
# Any module whose Kategorie Ebene 3 is a transceiver form factor (NOT a DAC/AOC/MPO cable)
# must carry a Wellenlänge attribute — a missing one is shallow extraction. Two grounded
# exceptions, detected from the SKU's own attribute values, legitimately have NO published
# wavelength and are EXEMPT:
#   * copper/coax media (RJ-45/Twinax/CX4/…BASE-T/coax) — no optical carrier at all;
#   * Smart SFP framer/mapper modules (TDM-over-Packet) — the official datasheet states only
#     SMF + reach and publishes no wavelength, so flag-or-omit forbids inventing one.
_WAVELENGTH_EXEMPT_RE = re.compile(
    r"kupfer|rj-?45|twinax|\bcx4\b|base-t\b|base-cr|base-cx|\bdac\b|cat\s?-?\d|koax|coax|"
    r"smart\s*sfp",
    re.IGNORECASE,
)
_WELLENLAENGE_NAME = "Wellenlänge"

# --- gold-slice applicable-attribute completeness (FAIL) -------------------------------
# Beyond Wellenlänge, the gold proof-slice schema requires these attributes to be present
# (a missing applicable attribute = shallow extraction, FAIL):
#   * Anwendung           — on EVERY SKU (the datasheet-grounded use case);
#   * Geschwindigkeit     — on EVERY SKU (line/data rate);
#   * Betriebstemperatur  — on every optical/active module AND on passive Twinax DAC cables. The
#     gold proof-slice DACs (SFP-H10GB-CU*) carry an operating temperature even with DOM=Nein, and
#     every DAC datasheet states a "Copper cable operation temperature: 0 to 70C" line, so DAC is
#     NOT exempt (gate bar == gold-slice schema). Only MPO fibre patch/breakout assemblies — purely
#     passive glass with no per-cable operating-temperature spec — remain exempt.
_ANWENDUNG_NAME = "Anwendung"
_GESCHWINDIGKEIT_NAME = "Geschwindigkeit"
_BETRIEBSTEMP_NAME = "Betriebstemperatur"
_BETRIEBSTEMP_EXEMPT_K3 = frozenset({"MPO Kabel"})  # passive fibre patch/breakout only

# --- permanent SEMANTIC cross-checks (structurally-valid-but-WRONG; FAIL) ----------------
# These catch the class of error the byte/format gate and even adversarial-verify let through.
_SFP_FAMILY_FF = frozenset({"SFP", "SFP+", "SFP28", "SFP56"})
_QSFP_CONN_RE = re.compile(r"QSFP|MPO|MTP|CXP|CPAK", re.IGNORECASE)         # a QSFP/MPO connector...
# \b guards stop a PARALLEL single-mode type (PLR4/PLR8 — one 1310 nm wavelength over parallel
# fibres) from matching its WDM cousin (LR4/LR8 — a true multi-wavelength SET): "PLR8" has no word
# boundary before "LR8", so \bLR8 won't match it, while "400GBASE-LR8" (boundary after "-") does.
_MULTI_WL_RE = re.compile(r"\bLR4|\bER4|\bFR4|\bLR8|\bCWDM4|LAN-?WDM|kohär|coheren", re.IGNORECASE)
_SINGLE_WL_RE = re.compile(r"^\s*[~≈]?\s*\d{3,4}(?:[.,]\d+)?\s*nm")          # exactly one wavelength
_FIBRE_CONN_GATE_RE = re.compile(r"MPO|MTP|\bLC\b|\bCS\b", re.IGNORECASE)    # optical fibre connector
# B.6 — a TUNABLE / "durchstimmbar" wavelength is only valid on a genuinely coherent/tunable part.
# (Catches the inverse of B.3: a grey fixed-wavelength optic, e.g. 10GBASE-ZR, wrongly given a
#  C-band-tunable wavelength — which a single-value multi-λ check would NOT flag.)
_TUNABLE_WL_RE = re.compile(r"durchstimmbar|tunable", re.IGNORECASE)
_COHERENT_TYPE_RE = re.compile(r"kohär|coheren|\bDCO\b|\bACO\b|400ZR|800ZR|DWDM|tunable|durchstimmbar",
                               re.IGNORECASE)
_COPPER_GATE_RE = re.compile(r"kupfer|copper|twinax|rj-?45|\bcx4\b|base-t", re.IGNORECASE)
# B.7 — a DAC/AOC cable (identified by its Kabeltyp) must be classified under a CABLE Kat-Ebene-3
# token (DAC/AOC Kabel), never under a module form-factor token (QSFP28/SFP+/…). Catches the class
# where a direct-attach/active cable wears a transceiver-module k3 (found in HPE: 21 DACs + 3 AOCs
# carried QSFP28/SFP+/… k3 instead of DAC/AOC Kabel). Modules carry no Kabeltyp, so FP-risk is low.
_CABLE_KABELTYP_RE = re.compile(r"twinax|\bdac\b|\baoc\b|active optical|aktiv.{0,4}optisch|direct attach", re.IGNORECASE)
_PLACEHOLDER_VALS = frozenset({"—", "-", "–", "--", "N/A", "n/a", "k.A.", "keine", "none"})
# B.5 known product-line guard: a PN family that belongs to a specific Hersteller, used ONLY to
# CATCH a misassignment (never as the assignment rule). MGB*/MFE* mini-GBICs are Cisco Small Business.
_HERSTELLER_LINE_GUARD = ((re.compile(r"^(MGB|MFE)", re.IGNORECASE), "Cisco"),)


def valid_gtin(s: str) -> bool:
    """True if `s` is a structurally valid GTIN-8/12/13/14 (correct GS1 check digit).

    EAN-13/UPC-A/GTIN-14 all share the same modulo-10 scheme: the rightmost body digit is
    weighted 3, then weights alternate 1/3 leftward; the check digit makes the weighted sum a
    multiple of 10. We never *fabricate* a GTIN (1000% rule) — but if one is ever supplied, a
    transposed/typo'd barcode must not reach a live import, so the gate rejects an invalid one.
    """
    s = s.strip()
    if not s.isdigit() or len(s) not in (8, 12, 13, 14):
        return False
    *body, check = (int(c) for c in s)
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(body)))
    return (10 - total % 10) % 10 == check

ROLE_SPEC = {
    "main": (C.MAIN_COLUMNS, C.MAIN_DELIMITER, C.MAIN_BOM),
    "attributes": (C.ATTRIBUTES_COLUMNS, C.ATTRIBUTES_DELIMITER, C.ATTRIBUTES_BOM),
    "platformflag": (C.PLATFORMFLAG_COLUMNS, C.PLATFORMFLAG_DELIMITER, C.PLATFORMFLAG_BOM),
    "prices": (C.PRICES_COLUMNS, C.PRICES_DELIMITER, C.PRICES_BOM),
    "condition": (C.CONDITION_COLUMNS, C.CONDITION_DELIMITER, C.CONDITION_BOM),
    "faq": (C.FAQ_COLUMNS, C.FAQ_DELIMITER, C.FAQ_BOM),
    "verification": (C.VERIFICATION_LOG_COLUMNS, C.VERIFICATION_LOG_DELIMITER, C.VERIFICATION_LOG_BOM),
}

@dataclass
class Violation:
    file: str
    sku: str
    field: str
    expected: str
    got: str
    message: str

    def __str__(self) -> str:
        loc = f"{self.file}"
        if self.sku:
            loc += f" / SKU {self.sku}"
        if self.field:
            loc += f" / {self.field}"
        return f"{loc}: {self.message} (expected {self.expected!r}, got {self.got!r})"


@dataclass
class Warning_:
    file: str
    sku: str
    field: str
    message: str

    def __str__(self) -> str:
        loc = self.file + (f" / SKU {self.sku}" if self.sku else "")
        return f"{loc} / {self.field}: {self.message}"


@dataclass
class ValidationResult:
    violations: list[Violation] = field(default_factory=list)
    warnings: list[Warning_] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


@dataclass
class Table:
    role: str
    path: Path
    bom_present: bool
    header: list[str]
    rows: list[list[str]]
    raw_lines: list[str]  # data lines only (no header), BOM stripped


def _read_table(role: str, path: Path, delimiter: str) -> Table:
    raw = path.read_bytes().decode("utf-8")
    bom_present = raw.startswith(BOM)
    if bom_present:
        raw = raw[len(BOM):]
    # Parse with the EXPECTED delimiter. A wrong delimiter in the file collapses each
    # row into a single field -> header mismatch -> caught downstream.
    reader = csv.reader(io.StringIO(raw), delimiter=delimiter)
    all_rows = [r for r in reader if r != []]
    header = all_rows[0] if all_rows else []
    data = all_rows[1:]
    # raw data lines for quote inspection
    raw_lines = raw.replace("\r\n", "\n").split("\n")
    raw_data_lines = [ln for ln in raw_lines[1:] if ln.strip() != ""]
    return Table(role, path, bom_present, header, data, raw_data_lines)


class Validator:
    def __init__(self, rules: Rules, directory: str | Path):
        self.rules = rules
        self.dir = Path(directory)
        self.result = ValidationResult()
        self.tables: dict[str, Table] = {}
        # slug -> hersteller map (all vendors sharing a slug map to one hersteller)
        self.slug_to_hersteller: dict[str, str] = {}
        for v in rules.vendors.values():
            self.slug_to_hersteller[v.slug] = v.hersteller

    # -- violation helpers ---------------------------------------------------
    def _fail(self, file, sku, fieldname, expected, got, message):
        self.result.violations.append(
            Violation(file=file, sku=sku, field=fieldname,
                      expected=str(expected), got=str(got), message=message)
        )

    def _warn(self, file, sku, fieldname, message):
        self.result.warnings.append(Warning_(file=file, sku=sku, field=fieldname, message=message))

    # -- file discovery + structural header/bom ------------------------------
    def _locate_and_load(self) -> bool:
        ok = True
        for role, pattern in ROLE_GLOBS.items():
            matches = sorted(self.dir.glob(pattern))
            if len(matches) == 0:
                self._fail(role, "", "", "exactly 1 file", "0 files",
                           f"missing {role} file matching {pattern}")
                ok = False
                continue
            if len(matches) > 1:
                self._fail(role, "", "", "exactly 1 file", f"{len(matches)} files",
                           f"ambiguous {role}: {[m.name for m in matches]}")
                ok = False
                continue
            cols, delim, expect_bom = ROLE_SPEC[role]
            table = _read_table(role, matches[0], delim)
            self.tables[role] = table
            fname = matches[0].name
            # Header exact (names + order + count) — also detects wrong delimiter.
            if tuple(table.header) != tuple(cols):
                self._fail(fname, "", "header", list(cols), table.header,
                           "header/columns/order/delimiter mismatch")
                ok = False
            # BOM where the contract requires it.
            if expect_bom and not table.bom_present:
                self._fail(fname, "", "BOM", "UTF-8 BOM present", "no BOM",
                           "required UTF-8 BOM is missing")
        return ok

    # -- helpers to access a column by name ----------------------------------
    def _col(self, table: Table, name: str) -> int:
        return list(table.header).index(name)

    # -- check groups --------------------------------------------------------
    def _check_main_content(self):
        t = self.tables.get("main")
        if not t:
            return
        fname = t.path.name
        b = self.rules.budgets
        c = self.rules.constants
        i_sku = self._col(t, "Artikelnummer")
        i_kurz = self._col(t, "Kurzbeschreibung")
        i_besch = self._col(t, "Beschreibung")
        i_titel = self._col(t, "Titel-Tag (SEO)")
        i_meta = self._col(t, "Meta-Description (SEO)")
        i_url = self._col(t, "URL-Pfad")
        i_art = self._col(t, "Artikelgewicht")
        i_ver = self._col(t, "Versandgewicht")
        i_han = self._col(t, "HAN")
        i_herst = self._col(t, "Hersteller")
        i_k1 = self._col(t, "Kategorie Ebene 1")
        i_k2 = self._col(t, "Kategorie Ebene 2")
        i_k3 = self._col(t, "Kategorie Ebene 3")

        # sentence -> set of SKUs whose Beschreibung contains it (cross-SKU reuse check)
        besch_sentences: dict[str, set[str]] = {}
        all_skus: set[str] = set()
        for row in t.rows:
            sku = row[i_sku]
            all_skus.add(sku)
            # 7. Kurzbeschreibung
            kurz = row[i_kurz]
            self._check_paragraphs(fname, sku, "Kurzbeschreibung", kurz,
                                   b.kurzbeschreibung.p_count,
                                   b.kurzbeschreibung.min_words, b.kurzbeschreibung.max_words)
            # 8. Beschreibung + closer
            besch = row[i_besch]
            # Category-aware floor: cables flex DOWN (item 6), modules keep the full floor.
            besch_k3 = row[i_k3]
            besch_min = (CABLE_BESCHREIBUNG_MIN_WORDS
                         if besch_k3 in C.CABLE_CATEGORIES else b.beschreibung.min_words)
            self._check_paragraphs(fname, sku, "Beschreibung", besch,
                                   b.beschreibung.p_count,
                                   besch_min, b.beschreibung.max_words)
            # Prose-only: the only allowed markup is <p>/</p>.
            for m in _ANY_TAG_RE.finditer(besch):
                tag = m.group(1).lower()
                if tag not in _ALLOWED_BESCH_TAGS:
                    self._fail(fname, sku, "Beschreibung", "prose-only <p> blocks",
                               f"<{tag}>",
                               "Beschreibung must be prose-only — no spec list or "
                               "markup besides <p> (specs belong in the Attributes file)")
                    break
            besch_plain = plain_text(besch)
            # Inline-Q&A leak (FAIL): the Beschreibung is prose-only; a question mark means FAQ
            # prose leaked into the body (FAQ belongs in its own file). House style is strictly
            # declarative — all 902 authored Beschreibungen are '?'-free — so this is a hard stop,
            # not a warning. (Promoted from WARN by the §3 gate self-audit: a listed defect class
            # the gate must FAIL, not merely flag.)
            if "?" in besch_plain:
                self._fail(fname, sku, "Beschreibung", "no '?' (prose-only body)", "contains '?'",
                           "inline Q&A leaked into the Beschreibung (FAQ belongs in the FAQ file)")
            # Collect substantive sentences for the reuse check (see reuse_candidate_sentences:
            # tag->space tokenization so sentences don't fuse across "</p><p>"; only the
            # "Original…" closer and <6-word fragments are exempt — condition statements
            # included must be unique per SKU).
            for s in reuse_candidate_sentences(besch):
                besch_sentences.setdefault(s, set()).add(sku)
            hersteller = row[i_herst]
            if not closer_present(self.rules, hersteller, plain_text(besch)):
                tail = closer_brand_tail(self.rules, hersteller)
                self._fail(fname, sku, "Beschreibung", f"contains 'Original(er|es|e) {tail}…'",
                           plain_text(besch)[-60:],
                           "Beschreibung missing the authenticity closer")
            # 9. Titel-Tag
            titel = row[i_titel]
            if len(titel) > b.titel_tag.max_chars:
                self._fail(fname, sku, "Titel-Tag (SEO)", f"<= {b.titel_tag.max_chars} chars",
                           f"{len(titel)} chars", "Titel-Tag too long")
            if not titel.endswith(b.titel_tag.must_end_with):
                self._fail(fname, sku, "Titel-Tag (SEO)", f"ends with '{b.titel_tag.must_end_with}'",
                           titel[-15:], "Titel-Tag must end with the Hexwaren suffix")
            # 10. Meta-Description
            meta = row[i_meta]
            if not (b.meta_description.min_chars <= len(meta) <= b.meta_description.max_chars):
                self._fail(fname, sku, "Meta-Description (SEO)",
                           f"{b.meta_description.min_chars}-{b.meta_description.max_chars} chars",
                           f"{len(meta)} chars", "Meta-Description length out of range")
            # 11. Categories
            if row[i_k1] != c.kategorie_ebene_1:
                self._fail(fname, sku, "Kategorie Ebene 1", c.kategorie_ebene_1, row[i_k1],
                           "Kategorie Ebene 1 constant mismatch")
            if row[i_k2] != c.kategorie_ebene_2:
                self._fail(fname, sku, "Kategorie Ebene 2", c.kategorie_ebene_2, row[i_k2],
                           "Kategorie Ebene 2 mismatch (must be '…Module' WITH final e)")
            k3 = row[i_k3]
            if k3 == "Sonstige":
                self._fail(fname, sku, "Kategorie Ebene 3", "a locked category", "Sonstige",
                           "'Sonstige' is never allowed")
            elif k3 not in set(self.rules.kategorie_ebene_3_allowed):
                self._fail(fname, sku, "Kategorie Ebene 3", "one of the locked 22", k3,
                           "Kategorie Ebene 3 not in the locked set")
            # 15. URL-Pfad / Hersteller / vendor consistency
            url = row[i_url]
            expected_url = None
            if "/" in url:
                slug, _, tail = url.partition("/")
                if slug not in self.slug_to_hersteller:
                    self._fail(fname, sku, "URL-Pfad", "vendor slug", slug,
                               "URL-Pfad slug not in vendor mapping")
                else:
                    expected_url = f"{slug}/{sku.lower()}"
                    exp_herst = self.slug_to_hersteller[slug]
                    if hersteller != exp_herst:
                        self._fail(fname, sku, "Hersteller", exp_herst, hersteller,
                                   "Hersteller does not match the URL-Pfad vendor slug")
                if expected_url and url != expected_url:
                    self._fail(fname, sku, "URL-Pfad", expected_url, url,
                               "URL-Pfad must be '{slug}/{sku-lower}'")
            else:
                self._fail(fname, sku, "URL-Pfad", "{slug}/{sku-lower}", url,
                           "URL-Pfad missing slug/sku structure")
            if hersteller not in self.rules.allowed_hersteller:
                self._fail(fname, sku, "Hersteller", sorted(self.rules.allowed_hersteller),
                           hersteller, "Hersteller token not in allowed set")
            # B.5 product-line guard: a PN family that belongs to a known Hersteller must be assigned
            # to it (verified against the real product line, never a naive PN-prefix split rule).
            for pat, exp_line in _HERSTELLER_LINE_GUARD:
                if pat.search(sku) and hersteller != exp_line:
                    self._fail(fname, sku, "Hersteller", exp_line, hersteller,
                               f"semantic: {sku} is a {exp_line} product line, mis-assigned to {hersteller}")
            # HAN == Artikelnummer
            if row[i_han] != sku:
                self._fail(fname, sku, "HAN", sku, row[i_han], "HAN must equal Artikelnummer")
            # 18. Weights numeric + versand > artikel
            art, ver = row[i_art], row[i_ver]
            a = self._num(fname, sku, "Artikelgewicht", art)
            v = self._num(fname, sku, "Versandgewicht", ver)
            if a is not None and v is not None and not v > a:
                self._fail(fname, sku, "Versandgewicht", f"> {art}", ver,
                           "Versandgewicht must be greater than Artikelgewicht")
            # 13. banned language across main text fields
            for fieldname in ("Artikelname", "Kurzbeschreibung", "Beschreibung",
                              "Titel-Tag (SEO)", "Meta-Description (SEO)"):
                self._scan_banned(fname, sku, fieldname, row[self._col(t, fieldname)])

        # Cross-SKU sentence reuse: identical (non-authenticity) body sentences across many
        # SKUs are boilerplate padding — a genuine shared spec belongs in the Attributes CSV.
        # FAIL when a sentence is shared by more than SENTENCE_REUSE_FAIL_FRACTION of a brand's
        # SKUs (only once the bundle is large enough for a fraction to be meaningful); below
        # that threshold it stays a WARN so near-misses remain visible.
        n_skus = len(all_skus)
        for sent, skus in besch_sentences.items():
            n = len(skus)
            if n <= 1:
                continue
            sample = ", ".join(sorted(skus)[:5])
            more = "…" if n > 5 else ""
            frac = n / n_skus if n_skus else 0
            if n_skus >= SENTENCE_REUSE_MIN_SKUS and frac > SENTENCE_REUSE_FAIL_FRACTION:
                self._fail(fname, "", "Beschreibung",
                           f"no non-closer sentence in >{SENTENCE_REUSE_FAIL_FRACTION:.0%} of SKUs",
                           f"reused across {n}/{n_skus} SKUs ({frac:.0%}: {sample}{more})",
                           "boilerplate: shared sentence over the reuse threshold "
                           "(move genuine shared specs to the Attributes CSV)")
            else:
                self._warn(fname, "", "Beschreibung",
                           f"sentence reused across {n} SKUs ({sample}{more}): "
                           "possible boilerplate padding")

    def _num(self, fname, sku, fieldname, value):
        """Validate German-decimal weight, return float or None (and record fail)."""
        if not re.match(r"^\d+,\d+$", value):
            self._fail(fname, sku, fieldname, "German decimal (comma)", value,
                       "weight is not a valid German-decimal number")
            return None
        return float(value.replace(",", "."))

    def _check_paragraphs(self, fname, sku, fieldname, html, want_p, min_w, max_w):
        n_open, n_close = count_paragraphs(html)
        if n_open != want_p or n_close != want_p:
            self._fail(fname, sku, fieldname, f"exactly {want_p} <p>…</p>",
                       f"{n_open} <p>/{n_close} </p>", "wrong number of <p> paragraphs")
        words = word_count(html)
        if not (min_w <= words <= max_w):
            self._fail(fname, sku, fieldname, f"{min_w}-{max_w} words", f"{words} words",
                       "word count out of range")

    def _scan_banned(self, fname, sku, fieldname, text):
        for phrase in banned_hard_hits(self.rules, text):
            self._fail(fname, sku, fieldname, "no banned phrase", phrase,
                       f"banned (hard-fail) phrase present: {phrase!r}")
        for phrase in banned_warn_hits(self.rules, text):
            self._warn(fname, sku, fieldname,
                       f"puffery flagged for review: {phrase!r}")

    def _check_attributes(self):
        t = self.tables.get("attributes")
        if not t:
            return
        fname = t.path.name
        grp_expected = self.rules.constants.attributgruppe_transceiver
        name_to_sort = {n: i for i, (n, _) in enumerate(C.TRANSCEIVER_ATTRIBUTES, start=1)}
        i_sku = self._col(t, "Artikelnummer")
        i_gtin = self._col(t, "GTIN")
        i_grp = self._col(t, "Attributgruppe")
        i_name = self._col(t, "Attributname")
        i_val = self._col(t, "Attributwert")
        i_sort = self._col(t, "Sortiernummer")
        i_dt = self._col(t, "Datentyp (sonst automatisch ermittelt)")
        i_art = self._col(t, "Attributart")

        per_sku_order: dict[str, list[int]] = {}
        per_sku_names: dict[str, set[str]] = {}
        per_sku_vals: dict[str, dict[str, str]] = {}
        per_sku_wl_exempt: dict[str, bool] = {}
        for row in t.rows:
            sku = row[i_sku]
            name = row[i_name]
            per_sku_names.setdefault(sku, set()).add(name)
            per_sku_vals.setdefault(sku, {})[name] = row[i_val]
            if _WAVELENGTH_EXEMPT_RE.search(row[i_val]):
                per_sku_wl_exempt[sku] = True
            if row[i_grp] != grp_expected:
                self._fail(fname, sku, "Attributgruppe", grp_expected, row[i_grp],
                           "Attributgruppe must be 'Transceivers & SFP Modul' (NO final e)")
            if name not in name_to_sort:
                self._fail(fname, sku, "Attributname", "one of the fixed 14", name,
                           "unknown attribute name (wide-vs-long or typo)")
            else:
                want_sort = name_to_sort[name]
                if row[i_sort] != str(want_sort):
                    self._fail(fname, sku, "Sortiernummer", str(want_sort), row[i_sort],
                               f"wrong Sortiernummer for attribute {name!r}")
                per_sku_order.setdefault(sku, []).append(want_sort)
                # 8. Formfaktor VALUE must be a physical connector, never a commerce
                # category (e.g. "DAC Kabel" stays in Kategorie Ebene 3).
                if name == "Formfaktor" and row[i_val].strip() not in C.PHYSICAL_FORMFAKTOR:
                    self._fail(fname, sku, "Attributwert (Formfaktor)",
                               "a physical connector (e.g. QSFP-DD, SFP+, OSFP)",
                               row[i_val],
                               "Formfaktor must be a physical connector, not a category")
            if row[i_dt] != C.ATTRIBUTES_DATENTYP:
                self._fail(fname, sku, "Datentyp", C.ATTRIBUTES_DATENTYP, row[i_dt],
                           "attribute Datentyp must be Wertliste")
            if row[i_art] != C.ATTRIBUTES_ATTRIBUTART:
                self._fail(fname, sku, "Attributart", C.ATTRIBUTES_ATTRIBUTART, row[i_art],
                           "attribute Attributart must be Attribut")
            if row[i_val].strip() == "":
                self._fail(fname, sku, "Attributwert", "non-empty", "(empty)",
                           "empty Wertliste row must not be emitted")
            # B.4 semantic: a genuinely-N/A attribute is OMITTED, never emitted as a "—" placeholder.
            if row[i_val].strip() in _PLACEHOLDER_VALS:
                self._fail(fname, sku, f"Attributwert ({name})", "omit the attribute (N/A)",
                           row[i_val], "semantic: never emit a '—'/N-A placeholder — omit the attribute")
            # GTIN is populate-or-prove-absent: empty is allowed (grounding deferred), but a
            # PRESENT GTIN must pass the GS1 check digit — no fabricated/typo'd barcodes.
            gtin = row[i_gtin].strip()
            if gtin and not valid_gtin(gtin):
                self._fail(fname, sku, "GTIN",
                           "valid GTIN-8/12/13/14 (GS1 check digit) or empty", gtin,
                           "GTIN present but fails the GS1 check digit")
            self._scan_banned(fname, sku, f"attribute:{name}", row[i_val])
        # order ascending within each SKU
        for sku, order in per_sku_order.items():
            if order != sorted(order):
                self._fail(fname, sku, "Sortiernummer order", "ascending by fixed 14",
                           order, "attribute rows out of canonical order")

        # Optical-module completeness: a transceiver form factor (non-cable) must carry a
        # Wellenlänge — a missing one signals shallow datasheet extraction. Copper-media
        # modules (RJ-45/Twinax/CX4/…BASE-T) legitimately have no wavelength and are exempt.
        main_t = self.tables.get("main")
        if main_t is not None:
            mi_sku = self._col(main_t, "Artikelnummer")
            mi_k3 = self._col(main_t, "Kategorie Ebene 3")
            sku_k3 = {r[mi_sku]: r[mi_k3] for r in main_t.rows}
            for sku, names in per_sku_names.items():
                k3 = sku_k3.get(sku, "")
                vals = per_sku_vals.get(sku, {})
                ff_v = vals.get("Formfaktor", "")
                ans_v = vals.get("Anschlusstyp", "")
                # B.1 Formfaktor <-> Anschlusstyp: an SFP-family module can't have a QSFP/MPO/CXP connector.
                if ff_v in _SFP_FAMILY_FF and _QSFP_CONN_RE.search(ans_v):
                    self._fail(fname, sku, "Formfaktor↔Anschlusstyp", f"a connector matching {ff_v}",
                               f"{ff_v} / {ans_v}",
                               "semantic: an SFP-family Formfaktor cannot carry a QSFP/MPO/CXP connector")
                # B.2 Faseranzahl present for any optical fibre-connector module (deriver fills it).
                copper_v = bool(_COPPER_GATE_RE.search(vals.get("Fasertyp", "") + " " + ans_v))
                if (not copper_v and _FIBRE_CONN_GATE_RE.search(ans_v)
                        and "Faseranzahl" not in names and k3 not in C.CABLE_CATEGORIES):
                    self._fail(fname, sku, "Attributwert (Faseranzahl)",
                               "a fibre count for the connector (duplex 2 / MPO parallel 8/16/…)",
                               "(missing)",
                               "semantic: an optical fibre-connector module must carry Faseranzahl")
                # B.3 multi-wavelength: LR4/ER4/FR4/coherent must carry the full set, not one centre value.
                wl_v = vals.get(_WELLENLAENGE_NAME, "")
                if (wl_v and _MULTI_WL_RE.search(vals.get("Standard", "") + " " + vals.get("Transceiver Typ", ""))
                        and _SINGLE_WL_RE.match(wl_v) and "/" not in wl_v and "–" not in wl_v
                        and "bis" not in wl_v.lower() and "durchstimmbar" not in wl_v.lower()):
                    self._fail(fname, sku, "Attributwert (Wellenlänge)",
                               "the full multi-lane wavelength set (e.g. 1271/1291/1311/1331 nm)", wl_v,
                               "semantic: LR4/ER4/FR4/coherent carries a wavelength SET, never one centre value")
                # B.6 tunable wavelength only on a coherent/tunable part (grey fixed optics must not).
                if (wl_v and _TUNABLE_WL_RE.search(wl_v)
                        and not _COHERENT_TYPE_RE.search(vals.get("Standard", "") + " " + vals.get("Transceiver Typ", ""))):
                    self._fail(fname, sku, "Attributwert (Wellenlänge)",
                               "a fixed wavelength (this is not a coherent/tunable part)", wl_v,
                               "semantic: a tunable/'durchstimmbar' wavelength is only valid on a coherent/tunable part")
                # B.7 a DAC/AOC cable (by Kabeltyp) must carry a CABLE k3, not a module form factor.
                kab_v = vals.get("Kabeltyp", "")
                if kab_v and _CABLE_KABELTYP_RE.search(kab_v) and k3 not in C.CABLE_CATEGORIES:
                    self._fail(fname, sku, "Kategorie Ebene 3",
                               "a cable Kat-3 token (DAC Kabel / AOC Kabel)", f"{k3} / Kabeltyp={kab_v}",
                               "semantic: a DAC/AOC cable must be classified under a cable Kat-Ebene-3 "
                               "token (DAC/AOC Kabel), not a transceiver-module form factor")
                # Gold-slice schema: Anwendung + Geschwindigkeit are required on EVERY SKU.
                if _ANWENDUNG_NAME not in names:
                    self._fail(fname, sku, "Attributwert (Anwendung)",
                               "an Anwendung attribute (every SKU)", "(missing)",
                               "gold-slice completeness: every SKU must carry a datasheet-grounded "
                               "Anwendung (use-case) attribute")
                if _GESCHWINDIGKEIT_NAME not in names:
                    self._fail(fname, sku, "Attributwert (Geschwindigkeit)",
                               "a Geschwindigkeit attribute (every SKU)", "(missing)",
                               "gold-slice completeness: every SKU must carry a Geschwindigkeit "
                               "(line/data rate) attribute")
                # Betriebstemperatur: required on optical/active modules; passive DAC/MPO exempt.
                if k3 not in _BETRIEBSTEMP_EXEMPT_K3 and _BETRIEBSTEMP_NAME not in names:
                    self._fail(fname, sku, "Attributwert (Betriebstemperatur)",
                               "a Betriebstemperatur attribute (optical/active module)", "(missing)",
                               "gold-slice completeness: every optical/active module must carry a "
                               "datasheet-grounded Betriebstemperatur attribute")
                # Wellenlänge: optical modules only (cables + copper/Smart-SFP exempt).
                if k3 in C.CABLE_CATEGORIES:
                    continue
                if per_sku_wl_exempt.get(sku):
                    continue
                if _WELLENLAENGE_NAME not in names:
                    self._fail(fname, sku, "Attributwert (Wellenlänge)",
                               "a Wellenlänge attribute (optical module)", "(missing)",
                               "optical-module completeness: a non-cable transceiver form "
                               "factor must carry a Wellenlänge attribute (shallow extraction)")

    def _check_prices(self):
        t = self.tables.get("prices")
        if not t:
            return
        fname = t.path.name
        i_sku = self._col(t, "Artikelnummer")
        i_p = self._col(t, "Netto-VK")
        for row in t.rows:
            sku, price = row[i_sku], row[i_p]
            if not GERMAN_DECIMAL_RE.match(price):
                self._fail(fname, sku, "Netto-VK",
                           "comma decimal, 2 places, no thousands sep", price,
                           "price not in German-decimal format")

    def _check_condition(self):
        t = self.tables.get("condition")
        if not t:
            return
        fname = t.path.name
        i_sku = self._col(t, "Artikelnummer")
        i_grp = self._col(t, "Attributgruppe")
        i_name = self._col(t, "Attributname")
        i_art = self._col(t, "Attributart")
        i_dt = self._col(t, "Datentyp")
        i_spr = self._col(t, "Sprache")
        i_val = self._col(t, "Attributwert")
        allowed = set(self.rules.condition.allowed)
        for row in t.rows:
            sku = row[i_sku]
            if row[i_grp] != "":
                self._fail(fname, sku, "Attributgruppe", "(empty)", row[i_grp],
                           "Condition Attributgruppe must be empty")
            if row[i_name] != C.CONDITION_ATTRIBUTNAME:
                self._fail(fname, sku, "Attributname", C.CONDITION_ATTRIBUTNAME, row[i_name], "bad")
            if row[i_art] != C.CONDITION_ATTRIBUTART:
                self._fail(fname, sku, "Attributart", C.CONDITION_ATTRIBUTART, row[i_art], "bad")
            if row[i_dt] != C.CONDITION_DATENTYP:
                self._fail(fname, sku, "Datentyp", C.CONDITION_DATENTYP, row[i_dt], "bad")
            if row[i_spr] != C.CONDITION_SPRACHE:
                self._fail(fname, sku, "Sprache", C.CONDITION_SPRACHE, row[i_spr], "bad")
            if row[i_val] not in allowed:
                self._fail(fname, sku, "Attributwert", sorted(allowed), row[i_val],
                           "Condition value not in {new, used, refurbished}")

    def _check_faq(self):
        t = self.tables.get("faq")
        if not t:
            return
        fname = t.path.name
        i_sku = self._col(t, "Artikelnummer")
        i_faq = self._col(t, "FAQ")
        b = self.rules.budgets.faq
        substantive_skus: dict[str, list[str]] = {}  # G5: dedup key -> SKUs
        for idx, row in enumerate(t.rows):
            sku = row[i_sku]
            cell = row[i_faq]
            # raw line: FAQ cell must be double-quoted (always)
            raw = t.raw_lines[idx] if idx < len(t.raw_lines) else ""
            after_first_comma = raw.split(",", 1)[1] if "," in raw else ""
            if not after_first_comma.startswith('"'):
                self._fail(fname, sku, "FAQ", 'double-quoted cell', after_first_comma[:12],
                           "FAQ cell must always be double-quoted")
            if C.FAQ_QA_SEP not in cell:
                self._fail(fname, sku, "FAQ", f"contains '{C.FAQ_QA_SEP}'", cell[:20],
                           "FAQ cell missing Question||Answer separator")
                continue
            pairs = [p for p in cell.split(C.FAQ_PAIR_SEP) if p != ""]
            for p in pairs:
                if C.FAQ_QA_SEP not in p:
                    self._fail(fname, sku, "FAQ", f"'{C.FAQ_QA_SEP}' in every pair", p[:20],
                               "FAQ pair missing || separator")
            n = len(pairs)
            if not (b.min_pairs <= n <= b.max_pairs):
                self._fail(fname, sku, "FAQ", f"{b.min_pairs}-{b.max_pairs} pairs",
                           f"{n} pairs", "FAQ pair count out of range")
            # G5: dedup on the substantive remainder (authenticity pair stripped).
            substantive = [p for p in pairs if not _FAQ_AUTHENTICITY_RE.match(p)]
            key = C.FAQ_PAIR_SEP.join(substantive)
            if key.strip():
                substantive_skus.setdefault(key, []).append(sku)

        # G5: a substantive FAQ block byte-identical across many SKUs is boilerplate.
        for key, skus in substantive_skus.items():
            cnt = len(skus)
            if cnt < FAQ_CELL_REUSE_WARN_SKUS:
                continue
            sample = ", ".join(sorted(skus)[:5])
            if cnt >= FAQ_CELL_REUSE_FAIL_SKUS:
                self._fail(fname, sorted(skus)[0], "FAQ", "distinctive per-SKU FAQ",
                           f"identical across {cnt} SKUs ({sample})",
                           "boilerplate: same substantive FAQ block reused across too many SKUs")
            else:
                self._warn(fname, sorted(skus)[0], "FAQ",
                           f"substantive FAQ identical across {cnt} SKUs ({sample}): "
                           "review for boilerplate")

    def _check_cross_file(self):
        if "main" not in self.tables:
            return
        sku_sets: dict[str, set[str]] = {}
        for role in SIX_FILES:
            t = self.tables.get(role)
            if not t:
                return
            i_sku = self._col(t, "Artikelnummer")
            sku_sets[role] = {r[i_sku] for r in t.rows}
        base = sku_sets["main"]
        for role in SIX_FILES:
            if sku_sets[role] != base:
                missing = base - sku_sets[role]
                extra = sku_sets[role] - base
                self._fail(self.tables[role].path.name, "", "Artikelnummer set",
                           "identical to Main", f"missing={sorted(missing)} extra={sorted(extra)}",
                           "SKU set differs across the six files")

    def _check_verification(self):
        ta = self.tables.get("attributes")
        tv = self.tables.get("verification")
        if not ta or not tv:
            return
        fname = tv.path.name
        ai_sku = self._col(ta, "Artikelnummer")
        ai_name = self._col(ta, "Attributname")
        ai_val = self._col(ta, "Attributwert")
        vi_sku = self._col(tv, "Artikelnummer")
        vi_name = self._col(tv, "Attributname")
        vi_val = self._col(tv, "Attributwert")
        logged = {(r[vi_sku], r[vi_name], r[vi_val]) for r in tv.rows}
        for r in ta.rows:
            key = (r[ai_sku], r[ai_name], r[ai_val])
            if key not in logged:
                self._fail(fname, r[ai_sku], r[ai_name], "a Verification-Log row",
                           "(none)", "attribute value has no verification-log entry")

    def run(self) -> ValidationResult:
        if not self._locate_and_load():
            return self.result  # files missing/headers wrong — stop, already failed
        # Only run content checks if headers were OK (avoids index errors on bad headers)
        if not self.result.violations:
            self._check_main_content()
            self._check_attributes()
            self._check_prices()
            self._check_condition()
            self._check_faq()
            self._check_cross_file()
            self._check_verification()
        return self.result


def validate_dir(rules: Rules, directory: str | Path) -> ValidationResult:
    return Validator(rules, directory).run()


# --------------------------------------------------------------------------- #
# Draft validation (pre-build content gate on a wide intake/draft CSV)          #
# --------------------------------------------------------------------------- #
# Map a content_issues message prefix -> the intake field it concerns.
_DRAFT_ISSUE_FIELD = {
    "Kurzbeschreibung": "Kurzbeschreibung",
    "Beschreibung": "Beschreibung",
    "Titel-Tag": "TitelTag",
    "Meta-Description": "MetaDescription",
    "FAQ": "FAQ",
}


def _draft_field_for(issue: str) -> str:
    for prefix, field in _DRAFT_ISSUE_FIELD.items():
        if issue.startswith(prefix):
            return field
    return ""


def validate_draft(rules: Rules, path: str | Path) -> ValidationResult:
    """Validate the authored content of a draft/intake CSV against the build gate's rules.

    Reuses the SAME predicates the build gate uses (`content_checks.content_issues`,
    `intake.normalize_faq`), so a draft that passes here passes `hexcat build`'s content
    checks. Unlike `read_intake` it collects EVERY content problem (it does not stop at the
    first) and reports each as a located violation {SKU, field, rule, got}. It also fails on
    any '[FLAG] ' marker left in a content cell, and surfaces soft spec flags as warnings.
    """
    # Imported here to avoid any import-order coupling with the generate package.
    from .content_checks import content_issues
    from .generate import FLAG_PREFIX, soft_spec_flags
    from .intake import IntakeError, normalize_faq
    from .models import INTAKE_COLUMNS

    path = Path(path)
    result = ValidationResult()
    fname = path.name

    if not path.exists():
        result.violations.append(
            Violation(fname, "", "", "an existing file", "(missing)", "draft file not found")
        )
        return result

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.violations.append(
                Violation(fname, "", "", "header row", "(empty)", "draft file is empty")
            )
            return result
        missing = [c for c in INTAKE_COLUMNS if c not in reader.fieldnames]
        if missing:
            result.violations.append(
                Violation(fname, "", "header", list(INTAKE_COLUMNS), missing,
                          "draft header missing required columns")
            )
            return result

        seen_rows = False
        for row in reader:
            sku = (row.get("Artikelnummer") or "").strip()
            if not sku or sku.startswith("#"):
                continue
            seen_rows = True

            vendor = (row.get("Vendor") or "").strip()
            entry = rules.resolve_vendor(vendor)
            if entry is None:
                result.violations.append(
                    Violation(fname, sku, "Vendor", sorted(rules.vendors), vendor,
                              "Vendor not in the allowed set")
                )
                continue
            hersteller = entry.hersteller

            fields = {
                "Kurzbeschreibung": (row.get("Kurzbeschreibung") or "").strip(),
                "Beschreibung": (row.get("Beschreibung") or "").strip(),
                "TitelTag": (row.get("TitelTag") or "").strip(),
                "MetaDescription": (row.get("MetaDescription") or "").strip(),
            }

            # Any leftover [FLAG] marker means the content was never reviewed/fixed.
            for fld in ("Kurzbeschreibung", "Beschreibung", "TitelTag", "MetaDescription", "FAQ"):
                val = (row.get(fld) or "")
                if val.lstrip().startswith(FLAG_PREFIX):
                    result.violations.append(
                        Violation(fname, sku, fld, "no [FLAG] marker", FLAG_PREFIX.strip(),
                                  "content still flagged — review and remove the [FLAG] marker")
                    )

            # FAQ pair count via the same normaliser the build path uses.
            faq_pairs = 0
            try:
                pairs, _ = normalize_faq(row.get("FAQ") or "", sku)
                faq_pairs = len(pairs)
            except IntakeError as e:
                result.violations.append(
                    Violation(fname, sku, "FAQ", "well-formed Q::A pairs",
                              (row.get("FAQ") or "")[:40], str(e))
                )

            for issue in content_issues(
                rules,
                hersteller=hersteller,
                kurzbeschreibung=fields["Kurzbeschreibung"],
                beschreibung=fields["Beschreibung"],
                titel_tag=fields["TitelTag"],
                meta_description=fields["MetaDescription"],
                faq_pair_count=faq_pairs,
            ):
                result.violations.append(
                    Violation(fname, sku, _draft_field_for(issue), "rule satisfied",
                              "(see message)", issue)
                )

            for sf in soft_spec_flags({**fields, "FAQ": ""}, {k: (row.get(k) or "") for k in INTAKE_COLUMNS}):
                result.warnings.append(Warning_(fname, sku, _draft_field_for(sf) or "content", sf))

        if not seen_rows:
            result.violations.append(
                Violation(fname, "", "", "at least one SKU row", "(none)",
                          "draft contained no SKU rows")
            )
    return result
