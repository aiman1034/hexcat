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
    l5 = check_plausibility(bundle) + check_price_sanity(bundle) + check_fibre_connector(bundle)
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
