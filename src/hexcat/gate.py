# -*- coding: utf-8 -*-
"""Consolidated automated gate — MISSION.md §8, layers L1-L7 (L8 = operator milestone, not here).

gate.py wraps the battle-tested validate.validate_dir (L1-core contract / L2 content / L3 semantic /
L4 grounding) and ADDS, as automated assertions over a 7-file bundle (+ the brand's completeness record):
  L1  two silent-corruption guards — HTML-well-formedness + UTF-8/umlaut-integrity  [THIS COMMIT]
  L5  plausibility (spec sanity)                                                     [next chunk]
  L6  completeness-vs-record/manifest                                                [next chunk]
  L7  negative-fixture suite (prove the gate isn't blind)                            [scaffold here]
It prints a per-LAYER PASS/FAIL report. No check is trusted until L7 proves it fires (B.8 lesson).

Build status: L1(core+guards)/L2/L3/L4 LIVE + self-tested vs the 8 known-good bundles; L5/L6 + the full
L7 fixture suite are stubbed with TODOs — gate() returns layer='?' for them so nothing is silently
green. The gate is NOT certified until selftest() shows known-good all-PASS AND every fixture FAILs.
"""
from __future__ import annotations
import re, unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .config import load_rules
from .validate import validate_dir, Violation


# ---- layer mapping for validate_dir's violations -------------------------------------------------
_L2_KEYS = ("word count", "paragraph", "<p>", "kurz", "beschreib", "titel", "meta", "banned",
            "closer", "boilerplate", "wörter", "zeichen")
_L3_KEYS = ("attributgruppe", "kategorie", "attribut", "sortiernummer", "switch", "s.1", "s.2",
            "s.3", "s.4", "s.5", "s.6", "b.1", "b.2", "b.3", "b.4", "b.5", "b.6", "b.7", "b.8",
            "formfaktor", "anschluss", "wellenlänge", "l3 token", "token")
_L4_KEYS = ("verification", "[verify]", "citation", "grounding", "verifikation")


def _layer_of(v: Violation) -> str:
    blob = f"{v.field} {v.message}".lower()
    if any(k in blob for k in _L4_KEYS): return "L4"
    if any(k in blob for k in _L3_KEYS): return "L3"
    if any(k in blob for k in _L2_KEYS): return "L2"
    return "L1"   # default: byte-contract / structure


# ---- L1 silent-corruption guards (NEW) -----------------------------------------------------------
# Mojibake = UTF-8 bytes mis-decoded as latin-1/cp1252 then re-saved. Telltale sequences:
_MOJIBAKE = re.compile(
    r"Ã[\x80-\xbf€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ\xa0-\xff¤¶©®°²³µ¼½¾¡¿]"  # Ã-prefixed (ä=Ã¤, ö=Ã¶, ü=Ã¼, ß=ÃŸ...)
    r"|Â[\x80-\xbf\xa0-\xff°±´·»«¿¡©®]"                                  # Â-prefixed (Â°, Â , ...)
    r"|â€[\x9c\x9d“”™˜¦\xa2\xa6]"                                        # smart-quote/dash mojibake
    r"|ï¿½|�"                                                       # replacement char (lost bytes)
)
_UMLAUT = "äöüÄÖÜß"


def _files(bundle: Path) -> list[Path]:
    return sorted(p for p in bundle.glob("*.csv"))


def check_utf8_umlaut(bundle: Path) -> list[Violation]:
    """L1: every file decodes as valid UTF-8; BOM only at byte 0 (never mid-body); zero mojibake;
    German umlauts intact (not stripped to ae/oe/ue or replacement char)."""
    out = []
    for p in _files(bundle):
        raw = p.read_bytes()
        try:
            text = raw.decode("utf-8-sig")          # tolerate the legitimate leading BOM
        except UnicodeDecodeError as e:
            out.append(Violation(p.name, "", "encoding", "valid UTF-8", "decode error",
                                 f"L1/UTF-8: file is not valid UTF-8 ({e})")); continue
        body = raw[3:] if raw[:3] == b"\xef\xbb\xbf" else raw
        if b"\xef\xbb\xbf" in body:
            out.append(Violation(p.name, "", "encoding", "BOM only at byte 0", "BOM in body",
                                 "L1/UTF-8: stray UTF-8 BOM mid-file (Mac+Excel re-save corruption)"))
        for m in _MOJIBAKE.finditer(text):
            out.append(Violation(p.name, "", "encoding", "intact UTF-8", repr(m.group(0)),
                                 f"L1/UTF-8: mojibake/double-encode artefact {m.group(0)!r} (umlaut corruption)"))
            break
    return out


_TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)[^>]*>")
_ALLOWED_HTML = {"p", "br", "ul", "li", "ol", "strong", "em", "b", "i"}


def _html_balanced(html: str) -> str | None:
    """Return an error string if the HTML fragment is not well-formed, else None."""
    # stray angle brackets that aren't part of a tag
    stripped = _TAG.sub("", html)
    if "<" in stripped or ">" in stripped:
        return f"stray angle bracket near {stripped[max(0,stripped.find('<')-10):stripped.find('<')+10]!r}"
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>", html):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if tag not in _ALLOWED_HTML:
            return f"disallowed/unknown tag <{tag}>"
        if attrs.strip().endswith("/") or tag == "br":
            continue                                 # self-closing
        if not closing:
            stack.append(tag)
        else:
            if not stack or stack[-1] != tag:
                return f"unbalanced </{tag}> (stack={stack})"
            stack.pop()
    if stack:
        return f"unclosed tag(s) {stack}"
    # invalid/raw ampersands (entities must be &..; ) — bare & is invalid
    if re.search(r"&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)", html):
        return "raw/invalid & entity"
    return None


def check_html_wellformed(bundle: Path) -> list[Violation]:
    """L1: every HTML content cell (Kurzbeschreibung, Beschreibung, FAQ answers) is well-formed —
    balanced/allowed tags, no stray <>, valid entities."""
    import csv
    out = []
    for p in _files(bundle):
        low = p.name.lower()
        is_main = "_main" in low
        is_faq = "faq" in low
        if not (is_main or is_faq):
            continue
        with p.open(encoding="utf-8-sig", newline="") as fh:
            delim = ";" if is_main else ","
            rows = list(csv.reader(fh, delimiter=delim))
        if not rows:
            continue
        hdr = rows[0]
        cols = [i for i, h in enumerate(hdr)
                if any(k in h.lower() for k in ("kurzbeschreibung", "beschreibung", "faq"))]
        sku_i = 0
        for r in rows[1:]:
            for i in cols:
                if i < len(r) and ("<" in r[i] or "&" in r[i]):
                    err = _html_balanced(r[i])
                    if err:
                        out.append(Violation(p.name, r[sku_i] if r else "", hdr[i],
                                             "well-formed HTML", r[i][:40],
                                             f"L1/HTML: {err}"))
    return out


# ---- gate orchestration + per-layer report -------------------------------------------------------
@dataclass
class LayerResult:
    layer: str
    passed: bool
    violations: list = field(default_factory=list)
    note: str = ""


@dataclass
class GateResult:
    bundle: str
    layers: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(L.passed for L in self.layers if L.layer not in ("L5", "L6", "L7"))  # only LIVE layers gate today


def gate(bundle_dir, rules=None) -> GateResult:
    rules = rules or load_rules()
    bundle = Path(bundle_dir)
    res = GateResult(bundle=bundle.name)

    # L1-L4 core via the battle-tested validator, bucketed by layer
    vr = validate_dir(rules, bundle)
    by = {"L1": [], "L2": [], "L3": [], "L4": []}
    for v in vr.violations:
        by[_layer_of(v)].append(v)
    # L1 also includes the two NEW silent-corruption guards
    by["L1"] += check_utf8_umlaut(bundle)
    by["L1"] += check_html_wellformed(bundle)

    for L in ("L1", "L2", "L3", "L4"):
        res.layers.append(LayerResult(L, not by[L], by[L]))
    # L5/L6/L7 not yet implemented — surfaced explicitly so they're never silently green
    res.layers.append(LayerResult("L5", True, note="TODO plausibility — NOT YET IMPLEMENTED (not trusted)"))
    res.layers.append(LayerResult("L6", True, note="TODO completeness-vs-record — NOT YET IMPLEMENTED (not trusted)"))
    res.layers.append(LayerResult("L7", True, note="TODO full fixture suite — NOT YET IMPLEMENTED (not trusted)"))
    return res


def print_report(res: GateResult) -> None:
    print(f"=== GATE {res.bundle} : {'PASS' if res.ok else 'FAIL'} (LIVE layers L1-L4) ===")
    for L in res.layers:
        tag = "PASS" if L.passed else "FAIL"
        extra = f"  [{L.note}]" if L.note else (f"  ({len(L.violations)} violations)" if L.violations else "")
        print(f"  {L.layer}: {tag}{extra}")
        for v in L.violations[:6]:
            print(f"       - {v.file} {v.sku}: {v.message[:80]}")
