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
    count_paragraphs,
    plain_text,
    word_count,
)
from .writers import BOM, GERMAN_DECIMAL_RE

# Glob patterns to locate each role's file in a bundle directory.
ROLE_GLOBS = {
    "main": "Hexwaren_*_v5_0_Main.csv",
    "attributes": "Hexwaren_*_Attributes_v5_0.csv",
    "platformflag": "Hexwaren_*_PlatformFlag.csv",
    "prices": "Hexwaren_*_Prices.csv",
    "condition": "Hexwaren_Condition_*.csv",
    "faq": "Hexwaren_FAQ_*_Batch_*.csv",
    "verification": "Verification_Log_*.csv",
}
SIX_FILES = ("main", "attributes", "platformflag", "prices", "condition", "faq")

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

        for row in t.rows:
            sku = row[i_sku]
            # 7. Kurzbeschreibung
            kurz = row[i_kurz]
            self._check_paragraphs(fname, sku, "Kurzbeschreibung", kurz,
                                   b.kurzbeschreibung.p_count,
                                   b.kurzbeschreibung.min_words, b.kurzbeschreibung.max_words)
            # 8. Beschreibung + closer
            besch = row[i_besch]
            self._check_paragraphs(fname, sku, "Beschreibung", besch,
                                   b.beschreibung.p_count,
                                   b.beschreibung.min_words, b.beschreibung.max_words)
            hersteller = row[i_herst]
            closer = self.rules.beschreibung_closer_prefix.format(brand=hersteller)
            if closer not in plain_text(besch):
                self._fail(fname, sku, "Beschreibung", f"ends with '{closer}…'",
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
        for row in t.rows:
            sku = row[i_sku]
            name = row[i_name]
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
            if row[i_dt] != C.ATTRIBUTES_DATENTYP:
                self._fail(fname, sku, "Datentyp", C.ATTRIBUTES_DATENTYP, row[i_dt],
                           "attribute Datentyp must be Wertliste")
            if row[i_art] != C.ATTRIBUTES_ATTRIBUTART:
                self._fail(fname, sku, "Attributart", C.ATTRIBUTES_ATTRIBUTART, row[i_art],
                           "attribute Attributart must be Attribut")
            if row[i_val].strip() == "":
                self._fail(fname, sku, "Attributwert", "non-empty", "(empty)",
                           "empty Wertliste row must not be emitted")
            self._scan_banned(fname, sku, f"attribute:{name}", row[i_val])
        # order ascending within each SKU
        for sku, order in per_sku_order.items():
            if order != sorted(order):
                self._fail(fname, sku, "Sortiernummer order", "ascending by fixed 14",
                           order, "attribute rows out of canonical order")

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
