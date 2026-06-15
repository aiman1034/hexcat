"""Assemble the six output files + the verification log from SkuRecord objects.

This module ONLY builds rows and writes them byte-exactly via writers.write_csv.
It performs no validation — that is validate.py's job, run after assembly.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import constants as C
from .config import Rules
from .models import SkuRecord
from .writers import write_csv


def _safe_name(value: str) -> str:
    """Make a string safe for use in a filename component."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("_") or "Batch"


@dataclass
class BundleFile:
    role: str          # "main", "attributes", ...
    path: Path
    rows: int          # data rows (excludes header)


@dataclass
class BundleManifest:
    batch: str
    category: str
    out_dir: Path
    files: list[BundleFile] = field(default_factory=list)
    skus: list[str] = field(default_factory=list)
    build_time: str = ""

    def by_role(self, role: str) -> BundleFile:
        for f in self.files:
            if f.role == role:
                return f
        raise KeyError(role)


def _main_rows(records: list[SkuRecord], rules: Rules) -> list[list[str]]:
    c = rules.constants
    rows = []
    for r in records:
        rows.append([
            r.artikelnummer,
            r.artikelname,
            r.kurzbeschreibung,
            r.beschreibung,
            r.url_pfad,
            r.artikelgewicht_de,
            r.versandgewicht_de,
            r.artikelnummer,                      # HAN = Artikelnummer
            r.hersteller,
            c.versandklasse,
            c.verkaufseinheit,
            r.titel_tag,
            r.meta_description,
            r.kategorie_ebene_1,
            r.kategorie_ebene_2,
            r.kategorie_ebene_3,
            c.ueberverkauf_plattform_hexwaren,    # TRUE
            c.bestandsfuehrung_aktiv,             # Y
            c.ueberverkaeufe_moeglich,            # Y
        ])
    return rows


def _attribute_rows(records: list[SkuRecord], rules: Rules) -> list[list[str]]:
    grp_tx = rules.constants.attributgruppe_transceiver  # "Transceivers & SFP Modul"
    grp_sw = rules.constants.attributgruppe_switch        # "Switch"
    rows = []
    for r in records:
        grp = grp_sw if r.kategorie_ebene_2 == rules.constants.kategorie_ebene_2_switch else grp_tx
        for a in r.attributes:
            rows.append([
                r.artikelnummer,
                "",                       # GTIN empty
                grp,
                a.name,
                a.value,
                str(a.sortiernummer),
                C.ATTRIBUTES_DATENTYP,    # Wertliste
                C.ATTRIBUTES_ATTRIBUTART, # Attribut
            ])
    return rows


def _platformflag_rows(records: list[SkuRecord], rules: Rules) -> list[list[str]]:
    flag = rules.constants.ueberverkauf_plattform_hexwaren
    return [[r.artikelnummer, flag] for r in records]


def _price_rows(records: list[SkuRecord]) -> list[list[str]]:
    return [[r.artikelnummer, r.netto_vk_de] for r in records]


def _condition_rows(records: list[SkuRecord]) -> list[list[str]]:
    return [[
        r.artikelnummer,
        "",                          # Attributgruppe empty
        C.CONDITION_ATTRIBUTNAME,    # condition
        C.CONDITION_ATTRIBUTART,     # Funktionsattribut
        C.CONDITION_DATENTYP,        # Wertliste
        C.CONDITION_SPRACHE,         # Deutsch
        r.condition,                 # new / used / refurbished
    ] for r in records]


def _faq_rows(records: list[SkuRecord]) -> list[list[str]]:
    return [[r.artikelnummer, r.faq_cell] for r in records]


def _verification_rows(records: list[SkuRecord], build_time: str) -> list[list[str]]:
    rows = []
    for r in records:
        for a in r.attributes:
            rows.append([
                r.artikelnummer,
                a.name,
                a.value,
                a.source_url,
                a.confidence or C.VERIFICATION_CONFIDENCE_OPERATOR,
                build_time,
            ])
        # Verification_Log-only rows for grounded prose claims that are not schema attributes
        # (e.g. a woven feature code) — logs the source WITHOUT an Attributes CSV row (§1000-rule).
        for e in getattr(r, "extra_log", None) or []:
            rows.append([
                r.artikelnummer, str(e[0]), str(e[1]), str(e[2]),
                (str(e[3]) if len(e) > 3 and e[3] else "datasheet"), build_time,
            ])
    return rows


def assemble_bundle(
    records: list[SkuRecord],
    rules: Rules,
    *,
    batch: str,
    category: str,
    out_dir: str | Path,
    build_time: str | None = None,
) -> BundleManifest:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bt = build_time or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cat = _safe_name(category)
    bat = _safe_name(batch)

    manifest = BundleManifest(
        batch=batch, category=category, out_dir=out_dir,
        skus=[r.artikelnummer for r in records], build_time=bt,
    )

    faq_force_quote = frozenset({C.FAQ_COLUMNS.index("FAQ")})

    # (role, filename, header, rows, delimiter, bom, force_quote_cols)
    plan = [
        ("main", C.FN_MAIN.format(category=cat), C.MAIN_COLUMNS,
         _main_rows(records, rules), C.MAIN_DELIMITER, C.MAIN_BOM, frozenset()),
        ("attributes", C.FN_ATTRIBUTES.format(category=cat), C.ATTRIBUTES_COLUMNS,
         _attribute_rows(records, rules), C.ATTRIBUTES_DELIMITER, C.ATTRIBUTES_BOM, frozenset()),
        ("platformflag", C.FN_PLATFORMFLAG.format(category=cat), C.PLATFORMFLAG_COLUMNS,
         _platformflag_rows(records, rules), C.PLATFORMFLAG_DELIMITER, C.PLATFORMFLAG_BOM, frozenset()),
        ("prices", C.FN_PRICES.format(category=cat), C.PRICES_COLUMNS,
         _price_rows(records), C.PRICES_DELIMITER, C.PRICES_BOM, frozenset()),
        ("condition", C.FN_CONDITION.format(batch=bat), C.CONDITION_COLUMNS,
         _condition_rows(records), C.CONDITION_DELIMITER, C.CONDITION_BOM, frozenset()),
        ("faq", C.FN_FAQ.format(batch=bat), C.FAQ_COLUMNS,
         _faq_rows(records), C.FAQ_DELIMITER, C.FAQ_BOM, faq_force_quote),
        ("verification", C.FN_VERIFICATION_LOG.format(batch=bat), C.VERIFICATION_LOG_COLUMNS,
         _verification_rows(records, bt), C.VERIFICATION_LOG_DELIMITER, C.VERIFICATION_LOG_BOM, frozenset()),
    ]

    for role, filename, header, rows, delim, bom, fq in plan:
        path = out_dir / filename
        write_csv(path, header, rows, delimiter=delim, bom=bom, force_quote_columns=fq)
        manifest.files.append(BundleFile(role=role, path=path, rows=len(rows)))

    return manifest
