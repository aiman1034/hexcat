"""The V1-V8 invariants. Each returns a CheckResult; none mutates state.

Inputs are the EMITTED ledger rows (what the miner produced) and the AUTHORITATIVE source
tokens (what the verifier independently re-derived from raw bytes). A check FAILs by listing
offending SKUs — never by raising — so the report can show every problem at once.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .extract import SourceToken
from ..ledger.spec import LedgerSpec, classify_cable_from_description


@dataclass
class EmittedRow:
    pn: str
    unterkategorie: str
    notiz: str = ""


@dataclass
class CheckResult:
    name: str           # "V1"
    title: str
    passed: bool
    summary: str
    offenders: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


# The loci that count as AUTHORITATIVE provenance — a SKU physically printed in the
# manufacturer's own SKU/PN column ('sku_column'/'pn_column'), flat ordering list ('flat'),
# '<noun> (SKU)' optic callout ('callout'), or product-card deep link ('card'). A SKU found
# only in 'description' prose is NOT authoritative (V2 flags it). Single source of truth so
# every check agrees on what "authoritative" means.
AUTHORITATIVE_LOCI = ("sku_column", "pn_column", "flat", "callout", "card")

# --- helpers -----------------------------------------------------------------------------
_SKU_CHAR = "A-Za-z0-9+"


def appears_as_whole_token(pn: str, raw_text: str) -> bool:
    """True iff `pn` occurs in raw_text not flanked by SKU-continuation chars.

    'SP-CABLE-ADASFP' is a substring of the source 'SP-CABLE-ADASFP+' but is NOT a whole
    token there (the next char '+' continues the SKU), so a trailing-'+'-mangled SKU fails
    this — which is exactly how V1 catches the separator-stripping bug. A genuine SKU like
    'FN-TRAN-QSFPDD-DR4' still passes because it appears elsewhere followed by a space.
    """
    pat = re.compile(r"(?<![" + _SKU_CHAR + r"])" + re.escape(pn) + r"(?![" + _SKU_CHAR + r"])")
    return pat.search(raw_text) is not None


def _closest(pn: str, candidates: list[str]) -> str | None:
    import difflib

    hit = difflib.get_close_matches(pn, candidates, n=1, cutoff=0.6)
    return hit[0] if hit else None


# --- V1: verbatim round-trip -------------------------------------------------------------
def v1_verbatim(emitted: list[EmittedRow], raw_text: str,
                source_skus: list[str]) -> CheckResult:
    offenders, detail = [], {}
    for r in emitted:
        if not appears_as_whole_token(r.pn, raw_text):
            offenders.append(r.pn)
            near = _closest(r.pn, source_skus)
            if near:
                detail[r.pn] = f"closest source token: {near!r}"
    return CheckResult(
        "V1", "Verbatim round-trip", not offenders,
        f"{len(emitted) - len(offenders)}/{len(emitted)} emitted SKUs appear verbatim "
        "(as whole tokens) in the raw source.",
        offenders, detail,
    )


# --- V2: authoritative-locus provenance --------------------------------------------------
def v2_provenance(emitted: list[EmittedRow], tokens: list[SourceToken]) -> CheckResult:
    authoritative = {t.pn for t in tokens if t.locus in AUTHORITATIVE_LOCI}
    desc_only = {t.pn for t in tokens if t.locus == "description"} - authoritative
    offenders, detail = [], {}
    for r in emitted:
        if r.pn not in authoritative:
            # Only an offender if it originated from prose / a cross-reference, not the SKU
            # column. (A mangled SKU absent from both is V1/V4's to flag, not V2's.)
            if r.pn in desc_only:
                offenders.append(r.pn)
                detail[r.pn] = "found only in Description prose, not the authoritative SKU locus"
    return CheckResult(
        "V2", "Authoritative-locus provenance", not offenders,
        "Every emitted SKU originates from the SKU/PN column or an optic callout, "
        "never from Description prose / cross-references.",
        offenders, detail,
    )


# --- V3: no silent dedup / collision -----------------------------------------------------
def v3_no_silent_collision(emitted: list[EmittedRow], tokens: list[SourceToken],
                           spec: LedgerSpec) -> CheckResult:
    """Two DISTINCT authoritative source tokens must not silently become one emitted SKU.

    We detect it structurally: group authoritative tokens by the string they would collapse
    to if a trailing separator were stripped (the historical bug). Any group with >1 distinct
    source token but <2 emitted survivors lost a SKU to a silent collision.
    """
    authoritative = sorted({t.pn for t in tokens if t.locus in AUTHORITATIVE_LOCI})
    emitted_set = {r.pn for r in emitted}
    collide: dict[str, set[str]] = {}
    for pn in authoritative:
        key = pn.rstrip("+")  # the lossy transform that caused the DR4/DR4+ collision
        collide.setdefault(key, set()).add(pn)
    offenders, detail = [], {}
    for key, group in collide.items():
        if len(group) > 1:
            survivors = group & emitted_set
            if len(survivors) < len(group):
                lost = sorted(group - emitted_set)
                offenders.extend(lost)
                detail[key] = (f"{sorted(group)} are distinct source SKUs but emitted only "
                               f"{sorted(survivors)} — {lost} lost to a trailing-separator collision")
    return CheckResult(
        "V3", "No silent dedup / collision", not offenders,
        "Distinct source tokens that differ only by a trailing separator stay distinct in "
        "the ledger (none silently deduped away).",
        offenders, detail,
    )


# --- V4: separator integrity -------------------------------------------------------------
def v4_separator_integrity(emitted: list[EmittedRow], tokens: list[SourceToken]) -> CheckResult:
    """No emitted SKU may be a proper prefix of a source token that differs only by a
    trailing separator char (the '+'-stripping mangle)."""
    source_tokens = {t.pn for t in tokens}
    emitted_set = {r.pn for r in emitted}
    offenders, detail = [], {}
    for r in emitted:
        for st in source_tokens:
            # Flag only a genuine mangle: emitted SKU is the source SKU with its trailing
            # separator stripped AND the full source SKU was itself NOT emitted. When BOTH the
            # base and the '+' form are emitted (DR4 and DR4+), the base is a legitimate
            # distinct SKU, not a mangle — so we must not false-positive on the fixed ledger.
            if st != r.pn and st.startswith(r.pn) and len(st) == len(r.pn) + 1 \
                    and not st[-1].isalnum() and st not in emitted_set:
                offenders.append(r.pn)
                detail[r.pn] = f"is a trailing-separator-stripped form of source SKU {st!r}"
                break
    return CheckResult(
        "V4", "Separator integrity", not offenders,
        "No emitted SKU is a separator-stripped prefix of a real source SKU "
        "(trailing '+'/'-' preserved).",
        offenders, detail,
    )


# --- V5: classification invariants -------------------------------------------------------
def v5_classification(emitted: list[EmittedRow], tokens: list[SourceToken]) -> CheckResult:
    """Where the manufacturer's description proves a cable category (DAC/AOC/MPO), the emitted
    Unterkategorie must match it. One rule, applied identically to every brand."""
    desc_by_pn: dict[str, str] = {}
    for t in tokens:
        if t.description and t.pn not in desc_by_pn:
            desc_by_pn[t.pn] = t.description
    offenders, detail = [], {}
    for r in emitted:
        desc = desc_by_pn.get(r.pn)
        if not desc:
            continue  # no description available (V1/V7 own missing/mangled SKUs)
        expected = classify_cable_from_description(desc)
        if expected is not None and r.unterkategorie != expected:
            offenders.append(r.pn)
            detail[r.pn] = (f"classified {r.unterkategorie!r} but description proves "
                            f"{expected!r}: {desc[:70]!r}")
    return CheckResult(
        "V5", "Classification invariants", not offenders,
        "DAC/AOC/MPO classification matches the manufacturer description (uniform rule, "
        "all brands).",
        offenders, detail,
    )


# --- V6: switch / non-transceiver exclusion ----------------------------------------------
def v6_switch_exclusion(emitted: list[EmittedRow], tokens: list[SourceToken]) -> CheckResult:
    """No emitted SKU may come from a switch / line-card / chassis / 'Module (SKU)' context.
    Such a SKU appears in the source only in description/prose locus, never the SKU column."""
    switch_terms = ("line card", "line-card", "chassis", "switch module", "uplink module")
    desc_by_pn: dict[str, str] = {}
    authoritative = set()
    for t in tokens:
        if t.locus in AUTHORITATIVE_LOCI:
            authoritative.add(t.pn)
        if t.description and t.pn not in desc_by_pn:
            desc_by_pn[t.pn] = t.description.lower()
    offenders, detail = [], {}
    for r in emitted:
        d = desc_by_pn.get(r.pn, "")
        if r.pn in authoritative and any(term in d for term in switch_terms):
            offenders.append(r.pn)
            detail[r.pn] = f"description reads as a switch/line-card item: {d[:60]!r}"
    return CheckResult(
        "V6", "Switch / non-transceiver exclusion", not offenders,
        "No switch / line-card / chassis SKU leaked into the transceiver ledger.",
        offenders, detail,
    )


# --- V7: completeness cross-check (second independent method) -----------------------------
def v7_completeness(emitted: list[EmittedRow], tokens: list[SourceToken],
                    v2: CheckResult, v4: CheckResult) -> CheckResult:
    """Symmetric difference between the emitted set and the independently re-derived
    authoritative set. Every difference must be EXPLAINED by another check, else FAIL."""
    authoritative = {t.pn for t in tokens if t.locus in AUTHORITATIVE_LOCI}
    emitted_set = {r.pn for r in emitted}
    emitted_not_source = sorted(emitted_set - authoritative)
    source_not_emitted = sorted(authoritative - emitted_set)
    explained = set(v2.offenders) | set(v4.offenders)
    unexplained_extra = [pn for pn in emitted_not_source if pn not in explained]
    offenders = sorted(set(emitted_not_source) | set(source_not_emitted))
    detail = {
        "emitted_not_in_source": emitted_not_source,
        "source_not_in_emitted": source_not_emitted,
        "explained_by_V2_V4": sorted(explained & set(emitted_not_source)),
        "unexplained_extras": unexplained_extra,
    }
    # FAIL whenever the two methods disagree at all — a true negative has an empty symmetric
    # difference. (Calibration: Cisco -> empty -> PASS; pre-fix Fortinet -> non-empty -> FAIL.)
    passed = not emitted_not_source and not source_not_emitted
    return CheckResult(
        "V7", "Completeness cross-check (2nd method)", passed,
        f"{len(authoritative)} authoritative vs {len(emitted_set)} emitted; "
        f"{len(emitted_not_source)} extra, {len(source_not_emitted)} missing.",
        offenders, detail,
    )


# --- V8: count honesty -------------------------------------------------------------------
def v8_count_honesty(emitted: list[EmittedRow], tokens: list[SourceToken]) -> CheckResult:
    authoritative = {t.pn for t in tokens if t.locus in AUTHORITATIVE_LOCI}
    emitted_distinct = len({r.pn for r in emitted})
    passed = emitted_distinct == len(authoritative)
    return CheckResult(
        "V8", "Count honesty", passed,
        f"emitted distinct={emitted_distinct}, authoritative distinct={len(authoritative)}.",
        [] if passed else [f"{emitted_distinct} != {len(authoritative)}"],
        {"emitted_distinct": emitted_distinct, "authoritative_distinct": len(authoritative)},
    )


# --- V9: catalog coverage (whole-brand, runs on the MERGED ledger) -----------------------
def v9_catalog_coverage(emitted: list[EmittedRow],
                        expected_families: list[str]) -> CheckResult:
    """Every transceiver family the brand's line is known to span must be represented by at
    least one emitted SKU in the merged ledger.

    Unlike V1-V8 (per-source integrity), V9 is a WHOLE-CATALOG completeness gate: it runs once
    over the merged emitted set across every source. A missing family does NOT mean the mine is
    wrong (the SKUs that ARE present are still verbatim/provenanced) — it means the catalog is
    KNOWN-INCOMPLETE and may not advance to DONE-VERIFIED until the gap is closed (another
    source mined) or explicitly justified. Naming the missing families is the whole point: the
    operator sees exactly which form factors still need a source.
    """
    emitted_families = {r.unterkategorie for r in emitted}
    expected = list(dict.fromkeys(expected_families))  # de-dup, keep order
    missing = [f for f in expected if f not in emitted_families]
    extra = sorted(emitted_families - set(expected))
    passed = not missing
    by_family = {f: sum(1 for r in emitted if r.unterkategorie == f) for f in expected}
    return CheckResult(
        "V9", "Catalog coverage", passed,
        (f"{len(expected) - len(missing)}/{len(expected)} expected families present"
         + (f"; KNOWN-INCOMPLETE — missing: {', '.join(missing)}" if missing else "")),
        missing,
        {
            "expected_families": expected,
            "missing_families": missing,
            "emitted_only_families": extra,  # present but not in the expected set (informational)
            "skus_per_expected_family": by_family,
        },
    )
