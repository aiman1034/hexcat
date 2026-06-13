"""Universal, category-agnostic COMPLETENESS reconciler — local, deterministic, ZERO-DOLLAR.

Completeness is never *asserted* and never measured against the harvest itself (that is
circular). It is a VERIFIED reconcile of the harvested part-number set against an INDEPENDENT
authoritative yardstick — and not a single list, but the UNION of several independent official
enumerations, each of which covers the others' blind spots. For Cisco transceivers those are
the optics-to-device compatibility matrix (current-product list), the EOL/EOS bulletins (legacy
parts a current list drops), the ordering / product-family guide, and the GPL / price list.

This module carries NO category or brand knowledge. Like :mod:`lib.harvest`, every
category-specific fact lives in CONFIG — ``config/enumerations/<category>.yaml`` (a sibling of
``config/sources/``). Adding a category, or a brand within one, is a config edit and ZERO code
changes here. Each configured source points at a tracked plain-text SNAPSHOT file (one PN per
line, ``#`` comments) — a verbatim capture of an official list, never fabricated or
pattern-generated. The reconciler:

  * loads every source's snapshot into a normalized PN set,
  * builds the ground-truth UNIVERSE = the union of all populated sources,
  * reconciles a harvested PN set against it, and reports ``captured X of Y``,
  * lists every PN in the universe but NOT in the harvest — the real gaps to chase,
  * treats a PN proven permanently gone (hard 404/410) as ``confirmed_gone`` so it is excused
    from the gap list but recorded, never silently dropped.

Coverage is "complete" ONLY when the harvest ⊇ the authoritative union (modulo confirmed-gone)
*and* at least one independent source is actually populated — an empty universe is never
"complete" (that would be vacuous). The verdict is a computed property of real lists, never a
hand-set flag.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
ENUMERATIONS_DIR = _REPO_ROOT / "config" / "enumerations"

# Conservative PN normalization: official lists vary only in case, surrounding whitespace, and
# the trailing "=" Cisco appends to spares. Anything more aggressive risks merging distinct PNs.
_WS_RE = re.compile(r"\s+")


def normalize_pn(pn: str) -> str:
    """Canonicalize a part number for set comparison (uppercase, de-space, strip trailing '=')."""
    s = _WS_RE.sub("", str(pn)).strip().upper()
    while s.endswith("="):
        s = s[:-1]
    return s


def normalize_set(pns: Iterable[str]) -> frozenset[str]:
    return frozenset(normalize_pn(p) for p in pns if str(p).strip())


# --------------------------------------------------------------------------------------
# Config model — one (category) file lists per-brand independent enumeration sources.
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class EnumerationSource:
    """One independent official enumeration of a brand's parts, backed by a snapshot file."""

    id: str
    kind: str
    note: str
    snapshot: str = ""
    pns: frozenset[str] = field(default_factory=frozenset)

    @property
    def populated(self) -> bool:
        """True once the snapshot has been gathered (a non-empty official capture)."""
        return bool(self.pns)


@dataclass(frozen=True)
class BrandEnumerations:
    brand: str
    sources: tuple[EnumerationSource, ...] = ()
    confirmed_gone: frozenset[str] = field(default_factory=frozenset)


def _resolve(path_str: str, root: Path) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else (root / p)


def read_snapshot(path: Path) -> frozenset[str]:
    """Read a snapshot file -> normalized PN set. One PN per line; ``#`` comments and blanks
    ignored. A missing file is an un-gathered source (empty set), never an error — the
    completeness verdict will simply not count it as populated yet."""
    if not path.exists():
        return frozenset()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # tolerate "PN  # note" and "PN<TAB>description" rows in a captured list
        s = s.split("#", 1)[0].strip()
        s = re.split(r"[\t,;|]", s, 1)[0].strip()
        if s:
            out.add(normalize_pn(s))
    return frozenset(out)


def load_enumerations(category: str, *, root: Path | None = None) -> dict[str, BrandEnumerations]:
    """Load ``config/enumerations/<category>.yaml`` into per-brand enumeration sets, reading
    each source's tracked snapshot file. Pure config: no category knowledge in code."""
    root = root or _REPO_ROOT
    base = root / "config" / "enumerations"
    path = base / f"{category}.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    brands: dict[str, BrandEnumerations] = {}
    for bname, b in (doc.get("brands") or {}).items():
        b = b or {}
        sources: list[EnumerationSource] = []
        for s in (b.get("sources") or []):
            snap = s.get("snapshot", "")
            pns = read_snapshot(_resolve(snap, root)) if snap else frozenset()
            sources.append(EnumerationSource(
                id=s["id"],
                kind=s.get("kind", ""),
                note=s.get("note", ""),
                snapshot=snap,
                pns=pns,
            ))
        brands[bname] = BrandEnumerations(
            brand=bname,
            sources=tuple(sources),
            confirmed_gone=normalize_set(b.get("confirmed_gone") or []),
        )
    return brands


# --------------------------------------------------------------------------------------
# The reconcile + verdict (pure, fully testable offline).
# --------------------------------------------------------------------------------------

def build_universe(sources: Iterable[EnumerationSource]) -> frozenset[str]:
    """Ground-truth universe = union of every source's snapshot. Built only from official
    lists; the code never fabricates or pattern-generates a PN."""
    u: set[str] = set()
    for s in sources:
        u |= s.pns
    return frozenset(u)


@dataclass(frozen=True)
class CompletenessReport:
    brand: str
    category: str
    universe: frozenset[str]
    harvested: frozenset[str]
    captured: frozenset[str]        # universe & harvested
    gaps: frozenset[str]            # in universe, not harvested, not confirmed-gone -> CHASE
    gone: frozenset[str]            # in universe, not harvested, but proven 404/410
    extra: frozenset[str]           # harvested but not in universe (informational)
    per_source: tuple[dict, ...]    # id/kind/total/populated/captured/gaps per source
    populated_sources: int

    @property
    def complete(self) -> bool:
        """Complete iff the harvest covers the whole authoritative union (modulo confirmed-gone)
        AND that union was actually built from at least one populated independent source. An
        empty universe is NEVER complete — that would be a vacuous, circular verdict."""
        return self.populated_sources > 0 and not self.universe ^ (self.captured | self.gone) \
            and not self.gaps

    def summary(self) -> str:
        verdict = "COMPLETE" if self.complete else "INCOMPLETE"
        return (f"[{self.category}/{self.brand}] captured {len(self.captured)} of "
                f"{len(self.universe)} | gaps={len(self.gaps)} gone={len(self.gone)} "
                f"extra={len(self.extra)} sources={self.populated_sources} -> {verdict}")

    def to_doc(self) -> dict:
        """A tracked-artifact dict (stable, sorted) suitable for YAML serialization."""
        return {
            "brand": self.brand,
            "category": self.category,
            "complete": self.complete,
            "universe_total": len(self.universe),
            "captured_count": len(self.captured),
            "gap_count": len(self.gaps),
            "confirmed_gone_count": len(self.gone),
            "extra_count": len(self.extra),
            "populated_sources": self.populated_sources,
            "per_source": [dict(s) for s in self.per_source],
            "gaps": sorted(self.gaps),
            "confirmed_gone": sorted(self.gone),
            "extra": sorted(self.extra),
        }


def reconcile(
    brand: str,
    category: str,
    harvested: Iterable[str],
    sources: Iterable[EnumerationSource],
    *,
    confirmed_gone: Iterable[str] = (),
) -> CompletenessReport:
    """Reconcile a harvested PN set against the union of independent official enumerations.

    Everything is normalized through :func:`normalize_pn` so the comparison is apples-to-apples.
    ``confirmed_gone`` are PNs proven permanently gone (hard 404/410): they are excused from the
    gap list but still reported, never silently dropped.
    """
    sources = tuple(sources)
    universe = build_universe(sources)
    harv = normalize_set(harvested)
    gone_all = normalize_set(confirmed_gone)

    captured = frozenset(universe & harv)
    missing = frozenset(universe - harv)
    gone = frozenset(missing & gone_all)
    gaps = frozenset(missing - gone)
    extra = frozenset(harv - universe)

    per_source: list[dict] = []
    for s in sources:
        per_source.append({
            "id": s.id,
            "kind": s.kind,
            "total": len(s.pns),
            "populated": s.populated,
            "captured": len(s.pns & harv),
            "gaps": len(s.pns - harv - gone_all),
        })

    return CompletenessReport(
        brand=brand,
        category=category,
        universe=universe,
        harvested=harv,
        captured=captured,
        gaps=gaps,
        gone=gone,
        extra=extra,
        per_source=tuple(per_source),
        populated_sources=sum(1 for s in sources if s.populated),
    )


def reconcile_brand(
    category: str,
    brand: str,
    harvested: Iterable[str],
    *,
    root: Path | None = None,
) -> CompletenessReport:
    """Convenience: load the brand's configured enumerations and reconcile a harvested set."""
    brands = load_enumerations(category, root=root)
    be = brands.get(brand) or BrandEnumerations(brand=brand)
    return reconcile(brand, category, harvested, be.sources, confirmed_gone=be.confirmed_gone)


def write_report(report: CompletenessReport, path: Path) -> None:
    """Persist the tracked completeness artifact as deterministic YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(report.to_doc(), allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )
