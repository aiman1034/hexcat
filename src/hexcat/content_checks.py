"""Pure content predicates shared by the build gate and the Phase 2 generator.

The build gate (`validate.py`) and the Phase 2 self-check (`generate.py`) MUST judge
prose against the *same* rules, or generated content could pass the generator and then
fail the gate (or vice-versa). To guarantee zero drift, both import the predicates here.

These functions are pure: text in, facts out. No I/O, no model calls.
"""
from __future__ import annotations

import re

from .config import Rules

_TAG_RE = re.compile(r"<[^>]+>")
_P_OPEN_RE = re.compile(r"<p>")
_P_CLOSE_RE = re.compile(r"</p>")


def plain_text(html: str) -> str:
    """Strip HTML tags, leaving the visible text the word/closer checks operate on."""
    return _TAG_RE.sub("", html)


def word_count(html: str) -> int:
    return len(plain_text(html).split())


def count_paragraphs(html: str) -> tuple[int, int]:
    """Return (number of <p>, number of </p>)."""
    return len(_P_OPEN_RE.findall(html)), len(_P_CLOSE_RE.findall(html))


def banned_hard_hits(rules: Rules, text: str) -> list[str]:
    low = text.lower()
    return [p for p in rules.banned_hard_fail if p.lower() in low]


def banned_warn_hits(rules: Rules, text: str) -> list[str]:
    low = text.lower()
    return [p for p in rules.banned_warn if p.lower() in low]


def required_closer(rules: Rules, hersteller: str) -> str:
    """The exact authenticity-closer substring the Beschreibung must contain."""
    return rules.beschreibung_closer_prefix.format(brand=hersteller)


def content_issues(
    rules: Rules,
    *,
    hersteller: str,
    kurzbeschreibung: str,
    beschreibung: str,
    titel_tag: str,
    meta_description: str,
    faq_pair_count: int,
) -> list[str]:
    """Return human-readable problems for the five generated fields.

    Empty list == this content would pass the build gate's content checks. The strings
    are written to be fed straight back to the model as retry feedback.
    """
    b = rules.budgets
    issues: list[str] = []

    # Kurzbeschreibung — exactly N <p> blocks, word budget.
    n_open, n_close = count_paragraphs(kurzbeschreibung)
    if n_open != b.kurzbeschreibung.p_count or n_close != b.kurzbeschreibung.p_count:
        issues.append(
            f"Kurzbeschreibung must contain exactly {b.kurzbeschreibung.p_count} "
            f"<p>…</p> blocks (found {n_open} <p> / {n_close} </p>)."
        )
    w = word_count(kurzbeschreibung)
    if not (b.kurzbeschreibung.min_words <= w <= b.kurzbeschreibung.max_words):
        issues.append(
            f"Kurzbeschreibung must be {b.kurzbeschreibung.min_words}-"
            f"{b.kurzbeschreibung.max_words} words (found {w})."
        )

    # Beschreibung — exactly N <p> blocks, word budget, authenticity closer.
    n_open, n_close = count_paragraphs(beschreibung)
    if n_open != b.beschreibung.p_count or n_close != b.beschreibung.p_count:
        issues.append(
            f"Beschreibung must contain exactly {b.beschreibung.p_count} "
            f"<p>…</p> blocks (found {n_open} <p> / {n_close} </p>)."
        )
    w = word_count(beschreibung)
    if not (b.beschreibung.min_words <= w <= b.beschreibung.max_words):
        issues.append(
            f"Beschreibung must be {b.beschreibung.min_words}-"
            f"{b.beschreibung.max_words} words (found {w})."
        )
    closer = required_closer(rules, hersteller)
    if closer not in plain_text(beschreibung):
        issues.append(
            f"Beschreibung must contain the exact authenticity closer text "
            f"'{closer}' (immediately followed by a German noun, e.g. '{closer}Transceiver')."
        )

    # Titel-Tag — length cap and mandatory suffix.
    if len(titel_tag) > b.titel_tag.max_chars:
        issues.append(
            f"Titel-Tag must be at most {b.titel_tag.max_chars} characters "
            f"(found {len(titel_tag)})."
        )
    if not titel_tag.endswith(b.titel_tag.must_end_with):
        issues.append(
            f"Titel-Tag must end with the exact suffix '{b.titel_tag.must_end_with}'."
        )

    # Meta-Description — character window.
    if not (b.meta_description.min_chars <= len(meta_description) <= b.meta_description.max_chars):
        issues.append(
            f"Meta-Description must be {b.meta_description.min_chars}-"
            f"{b.meta_description.max_chars} characters (found {len(meta_description)})."
        )

    # FAQ — pair count window.
    if not (b.faq.min_pairs <= faq_pair_count <= b.faq.max_pairs):
        issues.append(
            f"FAQ must have {b.faq.min_pairs}-{b.faq.max_pairs} question/answer "
            f"pairs (found {faq_pair_count})."
        )

    # Banned (hard-fail) language across the generated Main-file text fields.
    for label, text in (
        ("Kurzbeschreibung", kurzbeschreibung),
        ("Beschreibung", beschreibung),
        ("Titel-Tag", titel_tag),
        ("Meta-Description", meta_description),
    ):
        for hit in banned_hard_hits(rules, text):
            issues.append(f"{label} contains a forbidden phrase: '{hit}'. Remove it.")

    return issues
