"""§2 G6 — the merged-catalog cross-brand sweep.

The build gate (`validate.py`) judges ONE bundle at a time, so it is structurally blind to
collisions BETWEEN brands. When the five per-brand bundles (902 SKUs) are merged into one
JTL import, a clash that no single-bundle gate can see becomes a live-store defect:

  * two brands emitting the SAME Artikelnummer would overwrite each other on import;
  * a shared URL-Pfad collides two products onto one storefront route;
  * the same non-empty GTIN on two distinct SKUs is a barcode conflict (and a GS1 violation);
  * a duplicate Titel-Tag (SEO) splits page rank between two products;
  * a Beschreibung body sentence shared ACROSS brands is boilerplate that spans the catalog
    (each brand's prose is independently authored about different physical parts — an identical
    non-trivial sentence across brands is padding, not a grounded fact).

This module reads the already-produced bundles on disk and reports every cross-brand clash as a
located finding. Identity collisions are always FAIL (never acceptable for an import). The
cross-brand sentence sweep FAILs only above a calibrated brand-spread threshold so a genuinely
generic short clause does not trip it. Deterministic, files-only, $0.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .content_checks import plain_text, reuse_candidate_sentences
from .validate import ROLE_GLOBS, ROLE_SPEC, _read_table

# A non-closer Beschreibung sentence shared by SKUs spanning at least this many DISTINCT brands
# is cross-catalog boilerplate. Two independently-authored brand prose sets sharing a 6+-word
# sentence verbatim is already suspicious; three brands is unambiguous padding. Calibrated to
# the shipped 902-SKU catalog (see _scratch/g6_merged_sweep.py --calibrate).
SENTENCE_CROSS_BRAND_FAIL_BRANDS = 3
SENTENCE_CROSS_BRAND_WARN_BRANDS = 2


class SweepError(RuntimeError):
    """A bundle could not be located/loaded for the sweep (structural, pre-content)."""


@dataclass
class Finding:
    kind: str           # "Artikelnummer" | "URL-Pfad" | "GTIN" | "Titel-Tag (SEO)" | "Beschreibung"
    value: str          # the colliding value (truncated for prose)
    skus: list[str]     # "Brand:SKU" labels that share it
    message: str
    severity: str = "FAIL"  # "FAIL" | "WARN"

    def __str__(self) -> str:
        return f"[{self.severity}] {self.kind}: {self.message} ({', '.join(self.skus)})"


@dataclass
class SweepResult:
    findings: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)
    n_brands: int = 0
    n_skus: int = 0

    @property
    def ok(self) -> bool:
        return not self.findings


def _load_role(directory: Path, role: str):
    pattern = ROLE_GLOBS[role]
    matches = sorted(Path(directory).glob(pattern))
    if len(matches) != 1:
        raise SweepError(
            f"{directory.name}: expected exactly 1 {role} file matching {pattern}, "
            f"found {len(matches)}"
        )
    _, delim, _ = ROLE_SPEC[role]
    return _read_table(role, matches[0], delim)


def _col(table, name: str) -> int:
    return list(table.header).index(name)


def sweep_catalog(bundles: dict[str, str | Path]) -> SweepResult:
    """Cross-brand sweep over a {brand: bundle_dir} mapping.

    Reads each bundle's Main + Attributes CSV and reports every cross-brand collision. A
    single brand's internal duplicates are already the single-bundle gate's job (and Main's
    Artikelnummer is unique within a bundle by construction); this sweep is specifically about
    clashes that only appear once brands are combined.
    """
    result = SweepResult(n_brands=len(bundles))

    # value -> list of "Brand:SKU"
    artikelnummer: dict[str, list[str]] = {}
    url_pfad: dict[str, list[str]] = {}
    gtin: dict[str, list[str]] = {}
    titel: dict[str, list[str]] = {}
    # sentence -> {brand -> set(sku-labels)}
    sentences: dict[str, dict[str, list[str]]] = {}

    total_skus = 0
    for brand in sorted(bundles):
        main = _load_role(Path(bundles[brand]), "main")
        attrs = _load_role(Path(bundles[brand]), "attributes")
        m_sku = _col(main, "Artikelnummer")
        m_url = _col(main, "URL-Pfad")
        m_titel = _col(main, "Titel-Tag (SEO)")
        m_besch = _col(main, "Beschreibung")
        for row in main.rows:
            sku = row[m_sku]
            label = f"{brand}:{sku}"
            total_skus += 1
            artikelnummer.setdefault(sku, []).append(label)
            url_pfad.setdefault(row[m_url], []).append(label)
            titel.setdefault(row[m_titel], []).append(label)
            for sent in reuse_candidate_sentences(row[m_besch]):
                sentences.setdefault(sent, {}).setdefault(brand, []).append(label)
        # GTIN lives in the Attributes file (one or more rows per SKU; the value is constant
        # per SKU, so collapse to the SKU set rather than counting each attribute row).
        a_sku = _col(attrs, "Artikelnummer")
        a_gtin = _col(attrs, "GTIN")
        seen_gtin: set[tuple[str, str]] = set()
        for row in attrs.rows:
            g = row[a_gtin].strip()
            if not g:
                continue
            sku = row[a_sku]
            if (sku, g) in seen_gtin:
                continue
            seen_gtin.add((sku, g))
            gtin.setdefault(g, []).append(f"{brand}:{sku}")

    result.n_skus = total_skus

    # --- identity collisions: always FAIL ---------------------------------------------
    def _collide(table: dict[str, list[str]], kind: str, what: str, trunc: int = 60):
        for value, labels in table.items():
            # distinct SKUs only (a single SKU naturally appears once per its own rows)
            uniq = sorted(set(labels))
            if len(uniq) > 1:
                result.findings.append(Finding(
                    kind=kind, value=value[:trunc], skus=uniq,
                    message=f"{what} shared across {len(uniq)} SKUs in the merged catalog",
                ))

    _collide(artikelnummer, "Artikelnummer",
             "Artikelnummer (SKU)")
    _collide(url_pfad, "URL-Pfad", "URL-Pfad")
    _collide(gtin, "GTIN", "GTIN (barcode)")
    _collide(titel, "Titel-Tag (SEO)", "Titel-Tag")

    # --- cross-brand Beschreibung sentence reuse --------------------------------------
    for sent, by_brand in sentences.items():
        n_brands = len(by_brand)
        if n_brands < SENTENCE_CROSS_BRAND_WARN_BRANDS:
            continue
        labels = sorted({lab for labs in by_brand.values() for lab in labs})
        sample = labels[:6]
        more = "…" if len(labels) > 6 else ""
        finding = Finding(
            kind="Beschreibung", value=sent[:80], skus=sample + ([more] if more else []),
            message=(f"non-closer body sentence reused across {n_brands} brands "
                     f"({', '.join(sorted(by_brand))}): cross-catalog boilerplate"),
            severity=("FAIL" if n_brands >= SENTENCE_CROSS_BRAND_FAIL_BRANDS else "WARN"),
        )
        (result.findings if finding.severity == "FAIL" else result.warnings).append(finding)

    return result
