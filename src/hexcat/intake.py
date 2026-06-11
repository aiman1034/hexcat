"""Read the wide intake CSV and produce validated, normalized SkuRecord objects.

Responsibilities (deterministic, offline):
  * parse the wide CSV (one row per SKU),
  * normalize FAQ into the canonical Q||A##Q||A cell,
  * resolve vendor -> Hersteller/slug, build URL-Pfad,
  * derive weights from config when intake cells are blank,
  * transpose the 14 wide attribute columns into long AttributeValue rows
    (skipping empty cells so we never emit an empty Wertliste row),
  * fail loudly with an actionable, located message on bad input.
"""
from __future__ import annotations

import csv
from pathlib import Path

from . import constants as C
from .config import Rules, Weights
from .models import (
    INTAKE_COLUMNS,
    AttributeValue,
    FaqPair,
    SkuIntake,
    SkuRecord,
)
from .writers import GermanDecimalError, german_decimal


class IntakeError(ValueError):
    """Raised for any malformed intake. Message includes SKU + field context."""


# Friendlier FAQ delimiters the operator may use; normalized to canonical.
_FRIENDLY_PAIR_SEP = ";;"
_FRIENDLY_QA_SEP = "::"


def normalize_faq(raw: str, sku: str) -> tuple[list[FaqPair], str]:
    """Parse a FAQ cell (canonical Q||A##Q||A or friendly Q::A;;Q::A) -> pairs + cell."""
    text = raw.strip()
    if not text:
        return [], ""

    if C.FAQ_QA_SEP in text:  # canonical
        pair_sep, qa_sep = C.FAQ_PAIR_SEP, C.FAQ_QA_SEP
    elif _FRIENDLY_QA_SEP in text:  # friendly
        pair_sep, qa_sep = _FRIENDLY_PAIR_SEP, _FRIENDLY_QA_SEP
    else:
        raise IntakeError(
            f"[{sku}] FAQ: no recognizable delimiter; expected '{C.FAQ_QA_SEP}' "
            f"between question and answer (or friendly '{_FRIENDLY_QA_SEP}')."
        )

    pairs: list[FaqPair] = []
    for chunk in text.split(pair_sep):
        chunk = chunk.strip()
        if not chunk:
            continue
        if qa_sep not in chunk:
            raise IntakeError(
                f"[{sku}] FAQ: pair {chunk!r} missing '{qa_sep}' separator."
            )
        q, a = chunk.split(qa_sep, 1)
        q, a = q.strip(), a.strip()
        if not q or not a:
            raise IntakeError(
                f"[{sku}] FAQ: empty question or answer in pair {chunk!r}."
            )
        pairs.append(FaqPair(question=q, answer=a))

    # Canonical cell: no spaces around separators, no trailing ##.
    cell = C.FAQ_PAIR_SEP.join(
        f"{p.question}{C.FAQ_QA_SEP}{p.answer}" for p in pairs
    )
    return pairs, cell


def _derive_weights(
    intake: SkuIntake, weights: Weights, sku: str
) -> tuple[str, str, bool]:
    """Return (artikelgewicht_de, versandgewicht_de, is_placeholder)."""
    art_raw = intake.Artikelgewicht.strip()
    ver_raw = intake.Versandgewicht.strip()

    if art_raw and ver_raw:
        try:
            art = german_decimal(art_raw)
            ver = german_decimal(ver_raw)
        except GermanDecimalError as e:
            raise IntakeError(f"[{sku}] weight: {e}") from e
        # versand > artikel invariant
        a = float(art.replace(",", "."))
        v = float(ver.replace(",", "."))
        if not v > a:
            raise IntakeError(
                f"[{sku}] Versandgewicht ({ver}) must be > Artikelgewicht ({art})."
            )
        return art, ver, False

    if art_raw or ver_raw:
        raise IntakeError(
            f"[{sku}] weights: provide BOTH Artikelgewicht and Versandgewicht, "
            f"or neither (to derive from weights.yaml by Formfaktor)."
        )

    # Derive from config by Formfaktor.
    ff = intake.Formfaktor.strip()
    entry, used_default = weights.lookup(ff)
    return (
        german_decimal(entry.artikel),
        german_decimal(entry.versand),
        entry.placeholder or used_default,
    )


def _build_attributes(intake: SkuIntake, source_url: str) -> tuple[list[AttributeValue], list[str]]:
    """Transpose the fixed 14 attribute columns -> long rows; skip empty cells."""
    attrs: list[AttributeValue] = []
    skipped: list[str] = []
    for idx, (attr_name, field) in enumerate(C.TRANSCEIVER_ATTRIBUTES, start=1):
        value = getattr(intake, field, "").strip()
        if not value:
            skipped.append(attr_name)
            continue
        attrs.append(
            AttributeValue(
                name=attr_name,
                value=value,
                sortiernummer=idx,  # canonical position in the fixed 14
                source_url=source_url,
            )
        )
    return attrs, skipped


def build_record(intake: SkuIntake, rules: Rules, weights: Weights) -> SkuRecord:
    sku = intake.Artikelnummer.strip()
    if not sku:
        raise IntakeError("intake row missing Artikelnummer (required).")

    # Vendor -> Hersteller / slug.
    vendor = intake.Vendor.strip()
    vendor_entry = rules.resolve_vendor(vendor)
    if vendor_entry is None:
        raise IntakeError(
            f"[{sku}] Vendor {vendor!r} not in allowed set "
            f"{sorted(rules.vendors)}."
        )

    url_pfad = f"{vendor_entry.slug}/{sku.lower()}"

    # Price.
    try:
        netto_vk_de = german_decimal(intake.NettoVK)
    except GermanDecimalError as e:
        raise IntakeError(f"[{sku}] NettoVK: {e}") from e

    # Weights.
    art_de, ver_de, weights_ph = _derive_weights(intake, weights, sku)

    # Condition.
    condition = intake.Condition.strip() or rules.condition.default
    if condition not in rules.condition.allowed:
        raise IntakeError(
            f"[{sku}] Condition {condition!r} not in {rules.condition.allowed}."
        )

    # Verification source (Phase 1: human is the source unless URLs supplied).
    source_url = intake.SourceURLs.strip() or C.VERIFICATION_SOURCE_OPERATOR

    attributes, skipped = _build_attributes(intake, source_url)
    faq_pairs, faq_cell = normalize_faq(intake.FAQ, sku)

    return SkuRecord(
        artikelnummer=sku,
        vendor=vendor,
        hersteller=vendor_entry.hersteller,
        slug=vendor_entry.slug,
        url_pfad=url_pfad,
        artikelname=intake.Artikelname.strip(),
        kurzbeschreibung=intake.Kurzbeschreibung.strip(),
        beschreibung=intake.Beschreibung.strip(),
        titel_tag=intake.TitelTag.strip(),
        meta_description=intake.MetaDescription.strip(),
        kategorie_ebene_1=rules.constants.kategorie_ebene_1,
        kategorie_ebene_2=rules.constants.kategorie_ebene_2,
        kategorie_ebene_3=intake.KategorieEbene3.strip(),
        netto_vk_de=netto_vk_de,
        artikelgewicht_de=art_de,
        versandgewicht_de=ver_de,
        weights_are_placeholder=weights_ph,
        attributes=attributes,
        skipped_attributes=skipped,
        condition=condition,
        faq_pairs=faq_pairs,
        faq_cell=faq_cell,
    )


def read_intake(path: str | Path, rules: Rules, weights: Weights) -> list[SkuRecord]:
    path = Path(path)
    if not path.exists():
        raise IntakeError(f"intake file not found: {path}")

    # utf-8-sig tolerates a BOM if the operator's editor added one.
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise IntakeError(f"intake file {path.name} is empty.")
        missing = [c for c in INTAKE_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise IntakeError(
                f"intake header missing required columns: {missing}. "
                f"Run `hexcat new-intake` for the correct template."
            )
        records: list[SkuRecord] = []
        seen: set[str] = set()
        for lineno, row in enumerate(reader, start=2):
            # Skip blank lines and the commented example row in the template.
            sku_cell = (row.get("Artikelnummer") or "").strip()
            if not sku_cell or sku_cell.startswith("#"):
                continue
            payload = {k: (row.get(k) or "") for k in INTAKE_COLUMNS}
            try:
                intake = SkuIntake(**payload)
                record = build_record(intake, rules, weights)
            except IntakeError:
                raise
            except Exception as e:  # pydantic or unexpected
                raise IntakeError(f"intake line {lineno}: {e}") from e
            if record.artikelnummer in seen:
                raise IntakeError(
                    f"intake line {lineno}: duplicate Artikelnummer "
                    f"{record.artikelnummer!r} within the same file."
                )
            seen.add(record.artikelnummer)
            records.append(record)

    if not records:
        raise IntakeError(f"intake file {path.name} contained no SKU rows.")
    return records
