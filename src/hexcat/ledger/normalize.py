"""Normalize feed/live part numbers against the datasheet — Stage 1, deterministic.

The mined datasheet PN set is the authority. A raw PN is cleaned by:
  1. stripping a feed-ID suffix (-P-####),
  2. applying a known spelling fix (missing hyphen, etc.),
then CONFIRMED only if the result is actually in the datasheet's PN set. If it is not,
the PN is FLAGGED (unconfirmed) — never forced into a canonical it can't prove (the same
flag-don't-guess discipline as the 1000% rule). Each applied correction becomes one
PN-Korrekturen row.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .spec import LedgerSpec


@dataclass
class NormalizeResult:
    raw: str
    canonical: str
    problems: list[str] = field(default_factory=list)
    confirmed: bool = True       # is `canonical` present in the datasheet PN set?
    changed: bool = False        # did normalization alter the raw PN?

    @property
    def is_correction(self) -> bool:
        return self.changed

    @property
    def problem(self) -> str:
        return " + ".join(self.problems)


def normalize_pn(raw: str, canonical_set: set[str], spec: LedgerSpec) -> NormalizeResult:
    pn = (raw or "").strip()
    if pn in canonical_set:
        return NormalizeResult(raw=pn, canonical=pn, confirmed=True, changed=False)

    cur = pn
    problems: list[str] = []

    stripped = spec.normalize.feed_id_re.sub("", cur)
    if stripped != cur:
        problems.append(spec.normalize.problem_feed_id)
        cur = stripped

    if cur in spec.normalize.spelling_fixes:
        cur = spec.normalize.spelling_fixes[cur]
        problems.append(spec.normalize.problem_spelling)

    return NormalizeResult(
        raw=pn,
        canonical=cur,
        problems=problems,
        confirmed=cur in canonical_set,
        changed=cur != pn,
    )
