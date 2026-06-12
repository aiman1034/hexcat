"""§2 G7 — the import-readiness validator (catalog-level GO / NO-GO).

The per-bundle gate (`validate.py`) proves a bundle is *well-formed*; G6 (`merged_sweep.py`)
proves the bundles don't *collide*. G7 is the capstone: is the merged catalog actually ready to
go LIVE via a JTL-Ameise import? "Provably gap-proof" means this question gets an honest,
itemized answer — not a green light that hides deferred debt.

It composes every signal into one verdict:
  * STRUCTURE     — every bundle passes the build gate                       (BLOCK on fail)
  * CROSS-BRAND   — no merged-catalog collisions                            (BLOCK on fail)
  * PRICES        — every Netto-VK is a real grounded price, not the 0,00   (BLOCK while pending)
                    placeholder (the §5 pricing pass produces these)
  * WEIGHTS       — every weight is operator-grounded, not a flagged        (WARN — deferred)
                    form-factor placeholder (config/weight_disposition.yaml)
  * ATTR GAPS     — no residual attribute GAPs awaiting a datasheet pass    (WARN — deferred)
                    (config/attribute_gaps/residual_gaps.yaml)
  * GTIN          — every SKU carries a valid GTIN                          (WARN — deferred)

A BLOCK means "not importable yet"; a WARN means "importable but with a known, tracked,
deferred-grounding debt the operator accepted". The verdict is GO only when there are zero
BLOCKs. Each non-GO line points at the artifact/pass that will clear it. Deterministic, $0.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import Rules
from .merged_sweep import ROLE_GLOBS, ROLE_SPEC, _read_table, sweep_catalog
from .validate import valid_gtin, validate_dir

REPO = Path(__file__).resolve().parents[2]
WEIGHT_ARTIFACT = REPO / "config" / "weight_disposition.yaml"
GAPS_ARTIFACT = REPO / "config" / "attribute_gaps" / "residual_gaps.yaml"

# A Netto-VK that parses to <= 0 is the not-yet-priced placeholder (emitted as "0,00").
PRICE_PLACEHOLDER = "0,00"

GO, BLOCK, WARN = "GO", "BLOCK", "WARN"


@dataclass
class Check:
    name: str
    status: str   # GO | BLOCK | WARN
    detail: str

    def __str__(self) -> str:
        return f"[{self.status}] {self.name}: {self.detail}"


@dataclass
class ReadinessReport:
    checks: list[Check] = field(default_factory=list)
    n_brands: int = 0
    n_skus: int = 0

    @property
    def blockers(self) -> list[Check]:
        return [c for c in self.checks if c.status == BLOCK]

    @property
    def warnings(self) -> list[Check]:
        return [c for c in self.checks if c.status == WARN]

    @property
    def go(self) -> bool:
        return not self.blockers

    @property
    def verdict(self) -> str:
        return "GO" if self.go else "NO-GO"


def _load_role(directory: Path, role: str):
    pattern = ROLE_GLOBS[role]
    matches = sorted(Path(directory).glob(pattern))
    if len(matches) != 1:
        return None
    _, delim, _ = ROLE_SPEC[role]
    return _read_table(role, matches[0], delim)


def _col(table, name: str) -> int:
    return list(table.header).index(name)


def _unpriced(value: str) -> bool:
    v = value.strip().replace(".", "").replace(",", ".")
    try:
        return float(v) <= 0
    except ValueError:
        return True  # unparseable -> not a real price either


# --- individual checks (each pure over already-parsed inputs where possible) -----------

def _check_structure(bundles: dict[str, Path], rules: Rules) -> Check:
    bad = {}
    for brand, d in bundles.items():
        r = validate_dir(rules, d)
        if not r.ok:
            bad[brand] = len(r.violations)
    if bad:
        items = ", ".join(f"{b}={n}" for b, n in sorted(bad.items()))
        return Check("STRUCTURE", BLOCK, f"build gate FAILs: {items}")
    return Check("STRUCTURE", GO, f"all {len(bundles)} bundles pass the build gate")


def _check_cross_brand(bundles: dict[str, Path]) -> Check:
    r = sweep_catalog(bundles)
    if r.findings:
        kinds: dict[str, int] = {}
        for f in r.findings:
            kinds[f.kind] = kinds.get(f.kind, 0) + 1
        items = ", ".join(f"{k}×{n}" for k, n in sorted(kinds.items()))
        return Check("CROSS-BRAND", BLOCK, f"{len(r.findings)} merged-catalog collision(s): {items}")
    extra = f" ({len(r.warnings)} warn)" if r.warnings else ""
    return Check("CROSS-BRAND", GO, f"no merged-catalog collisions{extra}")


def _check_prices(bundles: dict[str, Path]) -> Check:
    total = unpriced = 0
    for d in bundles.values():
        t = _load_role(d, "prices")
        if t is None:
            return Check("PRICES", BLOCK, f"missing Prices file in {d.name}")
        i_p = _col(t, "Netto-VK")
        for row in t.rows:
            total += 1
            if _unpriced(row[i_p]):
                unpriced += 1
    if unpriced:
        return Check("PRICES", BLOCK,
                     f"{unpriced}/{total} SKUs at the {PRICE_PLACEHOLDER} placeholder "
                     f"(awaiting the §5 pricing pass)")
    return Check("PRICES", GO, f"all {total} SKUs carry a grounded Netto-VK")


def _check_gtin(bundles: dict[str, Path]) -> Check:
    total = with_gtin = bad = 0
    seen: set[tuple[str, str]] = set()
    for brand, d in bundles.items():
        t = _load_role(d, "attributes")
        if t is None:
            continue
        i_sku, i_g = _col(t, "Artikelnummer"), _col(t, "GTIN")
        skus_done: set[str] = set()
        for row in t.rows:
            sku = row[i_sku]
            if sku in skus_done:
                continue
            skus_done.add(sku)
            total += 1
            g = row[i_g].strip()
            if not g:
                continue
            with_gtin += 1
            if not valid_gtin(g):
                bad += 1
    if bad:
        return Check("GTIN", BLOCK, f"{bad} SKUs carry a GTIN that fails the GS1 check digit")
    if with_gtin < total:
        return Check("GTIN", WARN,
                     f"{with_gtin}/{total} SKUs carry a GTIN (rest deferred to a barcode pass)")
    return Check("GTIN", GO, f"all {total} SKUs carry a valid GTIN")


def _check_weights(artifact: Path) -> Check:
    if not artifact.exists():
        return Check("WEIGHTS", WARN, "weight_disposition artifact missing")
    d = yaml.safe_load(artifact.read_text(encoding="utf-8"))
    ph, tot = d.get("total_placeholder", 0), d.get("total_skus", 0)
    if ph:
        return Check("WEIGHTS", WARN,
                     f"{ph}/{tot} weights are flagged placeholders "
                     f"(deferred datasheet/measurement pass)")
    return Check("WEIGHTS", GO, f"all {tot} weights operator-grounded")


def _check_attribute_gaps(artifact: Path) -> Check:
    if not artifact.exists():
        return Check("ATTR-GAPS", WARN, "residual_gaps artifact missing")
    d = yaml.safe_load(artifact.read_text(encoding="utf-8"))
    total = sum(b.get("total_gaps", 0) for b in (d.get("brands") or {}).values())
    if total:
        return Check("ATTR-GAPS", WARN,
                     f"{total} residual attribute GAPs (deferred grounded datasheet pass)")
    return Check("ATTR-GAPS", GO, "no residual attribute GAPs")


def assess_readiness(
    bundles: dict[str, str | Path],
    rules: Rules,
    *,
    weight_artifact: Path | None = None,
    gaps_artifact: Path | None = None,
) -> ReadinessReport:
    """Aggregate every readiness signal into one GO / NO-GO report."""
    bundles = {b: Path(d) for b, d in bundles.items()}
    report = ReadinessReport(n_brands=len(bundles))
    report.checks.append(_check_structure(bundles, rules))
    report.checks.append(_check_cross_brand(bundles))
    report.checks.append(_check_prices(bundles))
    report.checks.append(_check_gtin(bundles))
    report.checks.append(_check_weights(weight_artifact or WEIGHT_ARTIFACT))
    report.checks.append(_check_attribute_gaps(gaps_artifact or GAPS_ARTIFACT))
    # SKU total from the Main files (authoritative).
    n = 0
    for d in bundles.values():
        t = _load_role(d, "main")
        if t is not None:
            n += len(t.rows)
    report.n_skus = n
    return report
