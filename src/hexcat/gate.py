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
import re, csv, yaml
from dataclasses import dataclass, field
from pathlib import Path

from .config import load_rules
from .validate import validate_dir, Violation

_REPO = Path(__file__).resolve().parents[2]
REASON_CODES = {"out-of-scope", "un-groundable-after-ladder", "eol", "harvest-gap", "source-blocked"}


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


# ---- bundle helpers ------------------------------------------------------------------------------
def _read_csv(path: Path, delim: str) -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=delim))
    return (rows[0], rows[1:]) if rows else ([], [])


def _main(bundle: Path):
    f = next(bundle.glob("*_Main*.csv"), None)
    return _read_csv(f, ";") if f else ([], [])


def _attrs(bundle: Path):
    f = next(bundle.glob("*_Attributes*.csv"), None)
    return _read_csv(f, ",") if f else ([], [])


def _bundle_category(bundle: Path) -> str:
    hdr, rows = _main(bundle)
    if "Kategorie Ebene 2" in hdr:
        i = hdr.index("Kategorie Ebene 2")
        if any(r[i].strip() == "Switches" for r in rows if len(r) > i):
            return "switch"
    return "transceiver"


def _brand_category(bundle: Path) -> tuple[str, str]:
    """('Cisco','transceivers') / ('MikroTik','switches') from the bundle dir name."""
    name = bundle.name.replace("stage3_", "")
    if name.endswith("_Switches"):
        return name[:-9], "switches"
    return name, "transceivers"


# ---- L5 PLAUSIBILITY (NEW) -----------------------------------------------------------------------
_REACH_KM_MAX = 130.0     # ZR/coherent tops ~120 km
_LAMBDA_MIN, _LAMBDA_MAX = 800, 1650    # nm (850 MMF .. 1610 CWDM/DWDM)


def check_plausibility(bundle: Path) -> list[Violation]:
    out = []
    cat = _bundle_category(bundle)
    hdr, rows = _main(bundle)
    if "Artikelnummer" in hdr and "Artikelgewicht" in hdr:
        i_sku, i_w = hdr.index("Artikelnummer"), hdr.index("Artikelgewicht")
        for r in rows:
            if len(r) <= max(i_sku, i_w):
                continue
            try:
                w = float(r[i_w].replace(",", "."))
            except ValueError:
                continue
            if cat == "switch":
                if w < 0.15:
                    out.append(Violation(bundle.name, r[i_sku], "Artikelgewicht", "switch >= 0,15 kg",
                                         r[i_w], "L5: switch weight below floor (optic-placeholder on a switch?)"))
                elif w > 50:
                    out.append(Violation(bundle.name, r[i_sku], "Artikelgewicht", "switch <= 50 kg", r[i_w],
                                         "L5: implausible switch weight (>50 kg)"))
            else:  # transceiver/optic module: small
                if w > 1.0:
                    out.append(Violation(bundle.name, r[i_sku], "Artikelgewicht", "optic <= ~1 kg", r[i_w],
                                         "L5: implausible optic-module weight (>1 kg — switch weight on a transceiver?)"))
    # reach / wavelength band from Attributes
    ahdr, arows = _attrs(bundle)
    if ahdr and "Attributname" in ahdr and "Attributwert" in ahdr:
        i_sku, i_n, i_v = ahdr.index("Artikelnummer"), ahdr.index("Attributname"), ahdr.index("Attributwert")
        for r in arows:
            if len(r) <= max(i_sku, i_n, i_v):
                continue
            name, val = r[i_n], r[i_v]
            # coherent/amplified/ULH/DWDM optics legitimately exceed the grey-optic band (amplified spans
            # span thousands of km) — exempt them from the reach band (not an error).
            # the coherent signal may live in the value OR the SKU/type name (e.g. '400G-...-ZR+' whose
            # Reichweite is just 'bis 1000 km') — search both so a real coherent optic is exempt.
            coherent = re.search(r"amplifizier|kohär|coheren|\bDWDM\b|\bULH\b|durchstimmbar|\bZR\b",
                                 val + " " + (r[i_sku] if len(r) > i_sku else ""), re.I)
            if name in ("Reichweite", "Länge") and "km" in val.lower() and not coherent:
                m = re.search(r"(\d+(?:[.,]\d+)?)\s*km", val, re.I)
                if m and float(m.group(1).replace(",", ".")) > _REACH_KM_MAX:
                    out.append(Violation(bundle.name, r[i_sku], name, f"reach <= {_REACH_KM_MAX} km", val,
                                         "L5: reach out of band (non-coherent)"))
            if name in ("Wellenlänge",):
                for nm in re.findall(r"(\d{3,4})\s*nm", val):
                    if not (_LAMBDA_MIN <= int(nm) <= _LAMBDA_MAX):
                        out.append(Violation(bundle.name, r[i_sku], name, f"{_LAMBDA_MIN}-{_LAMBDA_MAX} nm", val,
                                             "L5: wavelength out of band"))
                        break
    return out


# ---- L5 PRICE SANITY (NEW, L8 round-3) -----------------------------------------------------------
# The Cisco market-pricing engine emitted templated junk — 4 identical clusters (33/32/32/5 SKUs at
# one price). This guard refuses that signature: (a) the SAME non-zero price shared by >= N distinct
# SKUs, and (b) a handful of stray non-zero prices in an otherwise all-zero (Phase-1) bundle. An
# all-zero bundle and a genuinely varied future price list both pass cleanly.
_PRICE_CLUSTER_MIN = 5    # Cisco's smallest junk cluster was 5; identical-to-the-cent across >=5 SKUs = templated


def _prices(bundle: Path):
    f = next(bundle.glob("*_Prices*.csv"), None)
    return _read_csv(f, ";") if f else ([], [])


def check_price_sanity(bundle: Path) -> list[Violation]:
    out = []
    hdr, rows = _prices(bundle)
    if not hdr or "Netto-VK" not in hdr:
        return out
    from collections import Counter
    i_sku = hdr.index("Artikelnummer") if "Artikelnummer" in hdr else 0
    i_p = hdr.index("Netto-VK")
    nonzero = [(r[i_sku], r[i_p].strip()) for r in rows
               if len(r) > max(i_sku, i_p) and r[i_p].strip() not in ("", "0,00", "0.00", "0")]
    total = len([r for r in rows if len(r) > i_p])
    for val, c in Counter(v for _, v in nonzero).items():
        if c >= _PRICE_CLUSTER_MIN:
            out.append(Violation(bundle.name, "", "Netto-VK", f"< {_PRICE_CLUSTER_MIN} SKUs at one price",
                                 f"{val} x{c}",
                                 f"L5: identical-price cluster — {c} distinct SKUs at {val} (templated pricing, not grounded)"))
    if nonzero and len(nonzero) <= 3 and (total - len(nonzero)) >= 10:
        out.append(Violation(bundle.name, ",".join(s for s, _ in nonzero[:3]), "Netto-VK", "uniform 0,00 (Phase-1)",
                             f"{len(nonzero)}/{total} non-zero",
                             "L5: stray non-zero price(s) in an otherwise all-zero (Phase-1 catalog-consistent) bundle"))
    return out


# ---- L6 COMPLETENESS (NEW) -----------------------------------------------------------------------
# Clean machine-readable record (the prose per-brand *_completeness.yaml docs aren't valid YAML in
# places). Keyed "{Brand}_{category}": {enumerated, captured, flagged:[{family/pn, reason_code}]}.
_GATE_COMPLETENESS = _REPO / "config" / "coverage" / "gate_completeness.yaml"


def check_completeness(bundle: Path) -> list[Violation]:
    """L6 (operator-confirmed): PASS when every enumerated PN is grounded OR flagged WITH a valid
    reason-code, counts reconcile (captured == emitted), no silent shortfall. REFUSE on: no record,
    count mismatch, or a flagged gap with no/invalid reason-code (blocks 'flag everything to pass')."""
    out = []
    brand, category = _brand_category(bundle)
    key = f"{brand}_{category}"
    allrec = yaml.safe_load(_GATE_COMPLETENESS.read_text(encoding="utf-8")) if _GATE_COMPLETENESS.exists() else {}
    rec = (allrec or {}).get(key)
    emitted = len(_main(bundle)[1])
    if rec is None:
        out.append(Violation(bundle.name, "", "completeness", f"a gate_completeness record for {key}", "(none)",
                             f"L6: no machine-readable completeness record for {key} in gate_completeness.yaml"))
        return out
    captured = rec.get("captured")
    enumerated = rec.get("enumerated", captured)
    flagged = rec.get("flagged") or []
    if captured != emitted:
        out.append(Violation(bundle.name, "", "completeness", f"captured == emitted ({emitted})", str(captured),
                             "L6: count mismatch — captured != emitted SKUs (silent shortfall)"))
    for fl in flagged:
        rc = fl.get("reason_code") if isinstance(fl, dict) else None
        if not rc or str(rc).lower() not in REASON_CODES:
            out.append(Violation(bundle.name, str(fl)[:30], "completeness",
                                 f"reason_code in {sorted(REASON_CODES)}", str(rc),
                                 "L6: flagged gap without a valid reason-code (blocks flag-to-pass)"))
    if enumerated is not None and captured is not None and (captured + len(flagged)) < enumerated:
        out.append(Violation(bundle.name, "", "completeness",
                             f"captured+flagged ({captured}+{len(flagged)}) >= enumerated ({enumerated})", "",
                             "L6: silent shortfall — enumerated PNs neither grounded nor flagged"))
    return out


# ---- L4 GROUNDING (checkable part) ---------------------------------------------------------------
def check_grounding(bundle: Path) -> list[Violation]:
    """L4: an EMITTED bundle must carry no unresolved grounding placeholder — any literal '[VERIFY]'
    (or a bare '[FLAG]') in a cell means a value was shipped ungrounded; it must be grounded, or the
    SKU flagged out of the batch, before emit."""
    out = []
    for p in _files(bundle):
        delim = ";" if "_main" in p.name.lower() or "platformflag" in p.name.lower() or "prices" in p.name.lower() else ","
        hdr, rows = _read_csv(p, delim)
        for r in rows:
            for c in r:
                if "[VERIFY]" in c or "[FLAG]" in c:
                    out.append(Violation(p.name, r[0] if r else "", "", "no [VERIFY]/[FLAG] placeholder",
                                         c[:40], "L4: ungrounded placeholder shipped in an emitted bundle"))
                    break
    return out


# ---- L5 fibre-count vs connector (NEW, L8 Dell finding #2) ---------------------------------------
def check_fibre_connector(bundle: Path) -> list[Violation]:
    """A parallel optic's Faseranzahl must physically fit its connector: >=16 fibres need MPO-16 or
    2×MPO-12 (never a bare MPO-12, which carries 8 fibres / 4 lanes). Catches the 800G 2×R4 mislabel
    (Faseranzahl 16 on 'MPO-12'). Single-MPO-16 VR8/DR8 and duplex-LC parts pass."""
    out = []
    ahdr, arows = _attrs(bundle)
    if not ahdr or "Attributname" not in ahdr or "Artikelnummer" not in ahdr:
        return out
    i_s, i_n, i_v = ahdr.index("Artikelnummer"), ahdr.index("Attributname"), ahdr.index("Attributwert")
    bysku: dict = {}
    for r in arows:
        if len(r) > max(i_s, i_n, i_v):
            bysku.setdefault(r[i_s], {})[r[i_n]] = r[i_v]
    for sku, a in bysku.items():
        fz = a.get("Faseranzahl", "")
        conn = a.get("Anschlusstyp") or a.get("Anschluss") or ""
        if not fz.isdigit():
            continue
        # Flag ONLY the precise impossible case (operator rule): >=16 fibres on a BARE MPO-12. A 16/24-fibre
        # MPO/MTP (MPO-16, MPO-24, MTP-24, 24-Faser), a Dual/2× MPO-12, or a 1×16 MTP all carry enough fibres.
        bare_mpo12 = re.search(r"MPO-?12\b", conn, re.I) and not re.search(r"dual|\d\s*[x×]\s*MPO|\b2\s*MPO", conn, re.I)
        if int(fz) >= 16 and bare_mpo12:
            out.append(Violation(bundle.name, sku, "Faseranzahl", "MPO-16 or 2×MPO-12 for >=16 fibres",
                                 "%s fibres / %s" % (fz, conn or "(no connector)"),
                                 "L5: fibre count vs connector — %s fibres cannot fit a bare '%s' (MPO-12 carries 8)" % (fz, conn)))
    return out


# ---- L5 breakout-ends guard (NEW, L8 Dell finding #1) --------------------------------------------
_BREAKOUT_PN = re.compile(r"\b\d+\s*[xX]\s*\d+G\b|\b\d+(?:Q28|Q56|Q112|S28|S56|SFP)\b|\b\d+[xX]SFP", re.I)


def check_breakout_ends(bundle: Path) -> list[Violation]:
    """A cable whose PN encodes a BREAKOUT (Nx400G / NxQ28 / NxS28 / NxSFP / 8xSFP56, N>1) must have an
    'auf Nx …' multiplier in its Anschlusstyp; a same-to-same 'X auf X' means the breakout end was dropped
    (e.g. O112->OSFP collapsed both ends of DAC-O112-800G2x400G-Q112). Straight cables (no Nx in the PN)
    are exempt — DAC-O112-800G-xM legitimately reads 'OSFP auf OSFP'."""
    out = []
    ahdr, arows = _attrs(bundle)
    if not ahdr or "Attributname" not in ahdr or "Artikelnummer" not in ahdr:
        return out
    i_s, i_n, i_v = ahdr.index("Artikelnummer"), ahdr.index("Attributname"), ahdr.index("Attributwert")
    bysku: dict = {}
    for r in arows:
        if len(r) > max(i_s, i_n, i_v):
            bysku.setdefault(r[i_s], {})[r[i_n]] = r[i_v]
    for sku, a in bysku.items():
        ends = a.get("Anschlusstyp") or a.get("Anschlussenden") or ""
        if "auf" not in ends:                       # not a cable (modules carry a single Anschlusstyp)
            continue
        m = _BREAKOUT_PN.search(sku)
        if not m:
            continue
        n = next((int(g) for g in re.findall(r"(\d+)", m.group(0)) if int(g) > 1), 0)
        if n > 1 and not re.search(r"auf\s+\d+\s*[xX]", ends):
            out.append(Violation(bundle.name, sku, "Anschlusstyp", "a 'auf Nx …' breakout multiplier", ends,
                                 "L5: breakout PN but Anschlusstyp has no 'auf Nx' multiplier (breakout end dropped)"))
    return out


# ---- L5 NEAR-DUPLICATE PROSE (NEW, L8 Lenovo finding ①) ------------------------------------------
# §7.7 forbids same-spec SKUs sharing near-identical Beschreibung. Exact-match dup checks miss templated
# clones (only PN/feature-code differ). This masks PN + feature-code, clusters OPTIC modules by
# (Standard, Formfaktor, Reichweite, Wellenlänge), and flags any cluster whose pairwise word-3-shingle
# Jaccard similarity >= _NEAR_DUP_SIM. CABLES are exempt (length-variant prose reuse is the accepted
# norm — MikroTik precedent). Same-product alias/revision/variant clusters in already-cleared brands are
# carried in config/near_dup_exempt.yaml (reason-coded baseline, the completeness-flag pattern) so the
# check enforces "no NEW near-dups" catalog-wide without re-opening operator-cleared prose.
_NEAR_DUP_SIM = 0.85
_NEAR_DUP_EXEMPT = _REPO / "config" / "near_dup_exempt.yaml"
_FC_MASK = re.compile(r"Feature-Code\s+\w+", re.I)
_CABLE_STD = re.compile(r"\b(CR\d?|Twinax|Direct[ -]?Attach|Active Optical|AOC|DAC)\b", re.I)
# λ-channel mask (Pass 2): wavelengths (nm), ITU frequencies (THz/GHz), C-Band, "Kanal …" — so prose that
# differs ONLY by wavelength collapses and a templated CWDM/DWDM channel family is caught.
_LAMBDA_MASK = re.compile(r"\b1[0-9]{3}(?:[.,]\d+)?\s*nm|\b1[0-9]{3}(?:[.,]\d+)?\b|"
                          r"\b\d{2,3}[.,]\d+\s*THz|\bGHz\b|C-Band|Kanal\s*\S+|"
                          r"CWDM\s*\(\s*ch\s*\d+\s*\)|\(\s*(?:CW|DW)\s*\d+\s*\)|\b(?:CW|DW)\d+\b|\bch\s?\d+\b", re.I)
# Channel-code stripper for the Pass-2 CLUSTERING KEY: some brands bake the channel into the Standard
# attribute (e.g. "25G-LR CWDM(ch47)", "100G LR (CW27)"), so each channel reads as a different Std and the
# family never clusters -> never flags. Strip parentheticals + CW/DW/CH+digits so all channels of a family
# collapse regardless of WHERE the channel identity is recorded. ("CWDM"/"DWDM" type tokens are preserved.)
_CHAN_CODE = re.compile(r"\([^)]*\)|\b(?:CW|DW|CH)\s*\d+\b|\bch\d+\b", re.I)


def _norm_key(s: str) -> str:
    return re.sub(r"\s+", " ", _CHAN_CODE.sub("", s or "")).strip()
# integer wavelength tokens from a Wellenlänge attribute value (e.g. "1530,33 nm" -> "1530",
# "1270 nm (Tx) / 1330 nm (Rx)" -> 1270,1330). Used for the Pass-2 channel-identity test.
_LAMBDA_NM = re.compile(r"(\d{3,4})(?:[.,]\d+)?\s*nm")
# BiDi matched-pair signal in a Wellenlänge attr (Tx/Rx pair / "BiDi"). A D/U BiDi pair is two
# complementary halves of ONE link — near-identical prose is expected; the identity is the swapped
# Tx/Rx wavelength (in the attr) + the direction (in the PN), not per-channel prose.
_BIDI = re.compile(r"BiDi|\bT[xX]\b|\bR[xX]\b")


def _shingles(html: str, k: int = 3) -> set:
    w = re.sub(r"<[^>]+>", " ", html)
    w = re.sub(r"[^\wäöüÄÖÜß ]", " ", w).lower().split()
    return {tuple(w[i:i + k]) for i in range(len(w) - k + 1)} if len(w) >= k else set()


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0


def _near_dup_exemptions(brand: str) -> set:
    """frozenset(member-PNs) per exempted (same-product) cluster for this brand."""
    if not _NEAR_DUP_EXEMPT.exists():
        return set()
    rec = yaml.safe_load(_NEAR_DUP_EXEMPT.read_text(encoding="utf-8")) or {}
    out = set()
    for grp in (rec.get(brand) or []):
        members = grp.get("members") if isinstance(grp, dict) else grp
        if members:
            out.add(frozenset(members))
    return out


def check_near_dup_prose(bundle: Path) -> list[Violation]:
    from itertools import combinations
    out: list = []
    mhdr, mrows = _main(bundle)
    if not mhdr or "Beschreibung" not in mhdr or "Artikelnummer" not in mhdr:
        return out
    i_sku, i_be = mhdr.index("Artikelnummer"), mhdr.index("Beschreibung")
    i_k3 = mhdr.index("Kategorie Ebene 3") if "Kategorie Ebene 3" in mhdr else -1
    i_ti = next((i for i, c in enumerate(mhdr) if c.startswith("Titel-Tag")), -1)
    desc = {r[i_sku]: r[i_be] for r in mrows if len(r) > max(i_sku, i_be)}
    k3 = {r[i_sku]: (r[i_k3] if i_k3 >= 0 and len(r) > i_k3 else "") for r in mrows if len(r) > i_sku}
    titel = {r[i_sku]: (r[i_ti] if i_ti >= 0 and len(r) > i_ti else "") for r in mrows if len(r) > i_sku}
    ahdr, arows = _attrs(bundle)
    if not ahdr or "Attributname" not in ahdr:
        return out
    a_s, a_n, a_v = ahdr.index("Artikelnummer"), ahdr.index("Attributname"), ahdr.index("Attributwert")
    attr: dict = {}
    for r in arows:
        if len(r) > max(a_s, a_n, a_v):
            attr.setdefault(r[a_s], {})[r[a_n]] = r[a_v]
    brand, _ = _brand_category(bundle)
    exempt = _near_dup_exemptions(brand)
    # per-optic record. `ident` = channel-identity present: the member's wavelength (from its Wellenlänge
    # attr) appears BOTH in its Titel-Tag (λ via descriptive text or the PN both count) AND in its
    # PN-masked Beschreibung (λ surfaced as prose, not merely embedded in the PN). A well-formed λ-grid
    # has ident on every member; a "thin near-dup wearing a wavelength" (λ only in the PN, templated body)
    # does not -> that is what Pass 2 flags.
    recs = []
    for sku, be in desc.items():
        a = attr.get(sku, {})
        std, ff = a.get("Standard", ""), a.get("Formfaktor", "")
        ends = a.get("Anschlusstyp") or a.get("Anschlussenden") or ""
        if (not std or _CABLE_STD.search(std) or " auf " in ends
                or ff.endswith("Kabel") or "Kabel" in (k3.get(sku) or "")):
            continue                                        # cable exemption
        be_text = re.sub(r"<[^>]+>", " ", be)
        base = _FC_MASK.sub("Feature-Code X", re.sub(re.escape(sku), "PN", be, flags=re.I))
        base_text = re.sub(re.escape(sku), "", be_text, flags=re.I)   # PN-stripped prose text
        wl_nums = set(_LAMBDA_NM.findall(a.get("Wellenlänge", "") or ""))
        ident = bool(wl_nums) and any(n in (titel.get(sku) or "") for n in wl_nums) \
            and any(n in base_text for n in wl_nums)
        recs.append((sku, std, ff, a.get("Reichweite", ""), a.get("Wellenlänge", ""),
                     _shingles(base), _shingles(_LAMBDA_MASK.sub("WL", base)), ident))
    seen = set()

    def _emit(s1, s2, sim, std, ff, why):
        key = frozenset((s1, s2))
        if key in seen:
            return
        seen.add(key)
        out.append(Violation(bundle.name, "%s~%s" % (s1, s2), "Beschreibung",
                             "distinct same-spec SKUs need unique prose (<%.2f)" % _NEAR_DUP_SIM, "%.2f" % sim,
                             "L5: near-duplicate Beschreibung — %s vs %s share %.0f%% of prose (%s); "
                             "§7.7 unique-language" % (s1, s2, sim * 100, why)))

    # PASS 1 — exact same-spec (Std,FF,reach,λ): PN+FC masked. Same-product alias/revision clusters stay
    # grandfathered via the reason-coded registry (these are NOT λ-grids — they share one wavelength).
    p1: dict = {}
    for sku, std, ff, reach, wl, sh, _shl, _id in recs:
        p1.setdefault((std, ff, reach, wl), []).append((sku, sh))
    for sig, mem in p1.items():
        if len(mem) < 2 or frozenset(s for s, _ in mem) in exempt:
            continue
        for (s1, h1), (s2, h2) in combinations(mem, 2):
            sim = _jaccard(h1, h2)
            if sim >= _NEAR_DUP_SIM:
                _emit(s1, s2, sim, sig[0], sig[1], "same %s/%s, only PN/feature-code differ" % (sig[0], sig[1]))
    # PASS 2 — wavelength-CHANNEL family (Std,FF,reach, >=2 distinct λ). STRUCTURAL channel-identity gate
    # (replaces the blanket λ-family grandfather): a grid where EVERY member surfaces its wavelength in
    # Titel + Wellenlänge attr + prose is a well-formed grid (λ IS the per-SKU distinction, like cable
    # lengths) -> EXEMPT, no registry needed. Flag ONLY families with a member missing that identity
    # (λ in the PN only, templated body) whose λ-masked framing collapses >= the threshold — thin near-dup.
    p2: dict = {}
    for sku, std, ff, reach, wl, _sh, shl, ident in recs:
        p2.setdefault((_norm_key(std), _norm_key(ff), _norm_key(reach)), []).append((sku, wl, shl, ident))
    for sig, mem in p2.items():
        if len(mem) < 2 or len({w for _, w, _, _ in mem}) < 2:        # need a genuine multi-λ family
            continue
        if all(ident for _, _, _, ident in mem):                      # well-formed grid (λ in Titel+prose) -> exempt
            continue
        if any(_BIDI.search(w) for _, w, _, _ in mem) or "BX" in sig[0] or "BiDi" in sig[0]:
            continue   # BiDi matched-pair (D/U complementary halves; identity = swapped Tx/Rx λ in PN + attr)
        if frozenset(s for s, _, _, _ in mem) in exempt:              # reason-coded thin-grid baseline (fix-pending)
            continue
        for (s1, _w1, h1, i1), (s2, _w2, h2, i2) in combinations(mem, 2):
            if i1 and i2:                  # both carry channel identity -> legit grid pair (don't flag a
                continue                   # well-formed channel just because a thin sibling polluted the family)
            sim = _jaccard(h1, h2)
            if sim >= _NEAR_DUP_SIM:
                _emit(s1, s2, sim, sig[0], sig[1],
                      "%s λ-channel family but a member lacks channel identity (wavelength in PN only, "
                      "templated body) — thin near-dup, not a grounded grid" % sig[0])
    return out


# ---- L5 UNGROUNDED-CLAIM guard (NEW, L8 Lenovo finding ① — paired with the near-dup detector) --------
# A low near-dup score is meaningless if the uniqueness came from INVENTED content. This fails any
# Beschreibung that names a third-party OEM/vendor (Brocade/QLogic/Finisar/Accelink/Mellanox/Broadcom)
# or makes a "<Vendor>-qualifiziert" claim WITHOUT a matching Verification_Log row for that SKU (the
# §1000-rule: no prose claim without a logged source). Own brand + known sub-brand mentions are exempt,
# as are tokens grounded by a Verification_Log Source_URL/value. Bare "qualifiziert" (a common German
# word) is NOT a token — only the vendor-compound form is.
_OEM_TOKENS = re.compile(r"\b(Brocade|QLogic|Finisar|Accelink|Mellanox|Broadcom)\b", re.I)
_QUAL_CLAIM = re.compile(r"\b([A-ZÄÖÜ][A-Za-zÄÖÜäöüß]+)-qualifizier")
_OEM_SUBBRAND = {"NVIDIA": {"mellanox"}, "Meraki": {"cisco"}}     # legitimate parent/sub-brand mentions


def _verif_text(bundle: Path) -> dict:
    f = next(bundle.glob("*Verification_Log*.csv"), None)
    out: dict = {}
    if f:
        _, rows = _read_csv(f, ",")
        for r in rows:
            if r:
                out.setdefault(r[0], []).append(" ".join(r[1:]))
    return {k: " ".join(v).lower() for k, v in out.items()}


def check_ungrounded_claim(bundle: Path) -> list[Violation]:
    out: list = []
    mhdr, mrows = _main(bundle)
    if not mhdr or "Beschreibung" not in mhdr or "Artikelnummer" not in mhdr:
        return out
    i_sku, i_be = mhdr.index("Artikelnummer"), mhdr.index("Beschreibung")
    brand, _ = _brand_category(bundle)
    own = {brand.lower()} | {x.lower() for x in _OEM_SUBBRAND.get(brand, set())}
    vlog = _verif_text(bundle)
    for r in mrows:
        if len(r) <= i_be:
            continue
        sku, be = r[i_sku], re.sub(r"<[^>]+>", " ", r[i_be])
        claims = {m.group(1).lower() for m in _OEM_TOKENS.finditer(be)}
        claims |= {m.group(1).lower() for m in _QUAL_CLAIM.finditer(be)}
        log = vlog.get(sku, "")
        for t in sorted(claims):
            if t in own or t in log:                 # own/sub-brand, or grounded by a Verification_Log row
                continue
            out.append(Violation(bundle.name, sku, "Beschreibung",
                                 "external-vendor/OEM/qualification claim requires a Verification_Log row",
                                 t, "L5: ungrounded vendor/OEM claim '%s' in Beschreibung with no matching "
                                 "Verification_Log row for %s (fabrication guard, §1000-rule)" % (t, sku)))
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
        return all(L.passed for L in self.layers if L.layer != "L7")  # L1-L6 all gate; L7 = the harness proof


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
    by["L4"] += check_grounding(bundle)

    for L in ("L1", "L2", "L3", "L4"):
        res.layers.append(LayerResult(L, not by[L], by[L]))
    l5 = (check_plausibility(bundle) + check_price_sanity(bundle) + check_fibre_connector(bundle)
          + check_breakout_ends(bundle) + check_near_dup_prose(bundle) + check_ungrounded_claim(bundle))
    res.layers.append(LayerResult("L5", not l5, l5))
    l6 = check_completeness(bundle)
    res.layers.append(LayerResult("L6", not l6, l6))
    res.layers.append(LayerResult("L7", True, note="anti-blind-spot proof = _scratch/gate_selftest.py (not a per-bundle layer)"))
    return res


def print_report(res: GateResult) -> None:
    print(f"=== GATE {res.bundle} : {'PASS' if res.ok else 'FAIL'} (L1-L6) ===")
    for L in res.layers:
        tag = "PASS" if L.passed else "FAIL"
        extra = f"  [{L.note}]" if L.note else (f"  ({len(L.violations)} violations)" if L.violations else "")
        print(f"  {L.layer}: {tag}{extra}")
        for v in L.violations[:6]:
            print(f"       - {v.file} {v.sku}: {v.message[:80]}")
