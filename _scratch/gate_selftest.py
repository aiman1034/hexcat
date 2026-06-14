# -*- coding: utf-8 -*-
"""Self-test for src/hexcat/gate.py — MISSION §8 L7 anti-blind-spot proof (full L1-L6).
Run: python _scratch/gate_selftest.py   (exit 0 = CERTIFIED)
  (1) KNOWN-GOOD: the 8 emitted bundles must PASS L1-L6.
  (2) NEGATIVE FIXTURES: one deliberately-broken copy per check class — gate MUST flag each at the
      expected layer. Any fixture that PASSES = gate blind -> fix the check (B.8 false-green lesson).
"""
import sys, shutil, tempfile, csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import hexcat.gate as G
from hexcat.config import load_rules
from hexcat.gate import gate

RULES = load_rules()
KNOWN = ["Cisco", "Arista", "HPE", "Fortinet", "Meraki", "NVIDIA", "MikroTik", "MikroTik_Switches", "Juniper", "Extreme"]
LIVE = ("L1", "L2", "L3", "L4", "L5", "L6")


def fails(d):
    return [L.layer for L in gate(d, RULES).layers if L.layer in LIVE and not L.passed]


def known_good():
    """Task #21 DOM backfill is COMPLETE + the L8-round-3 media<->DOM/Formfaktor tightening is live, so
    the honest bar is now ZERO violations on every emitted bundle. No DOM-GAP escape hatch — a missing
    DOM attribute OR a media<->DOM inconsistency (e.g. a copper SFP carrying DOM=Ja) is a REGRESSION, not
    a deferred gap. The old escape hatch masked exactly that (Arista SFP-1G-T). Certify = all PASS."""
    print("=== KNOWN-GOOD (L1-L6; backfill complete — zero-violation bar) ===")
    regressions = []
    for b in KNOWN:
        r = gate(ROOT / f"output/stage3_{b}", RULES)
        viol = [v for L in r.layers if L.layer in LIVE and not L.passed for v in L.violations]
        status = "PASS" if not viol else f"REGRESSION {[v.message[:50] for v in viol][:2]}"
        if viol:
            regressions.append(b)
        print(f"  {b:20s} {status}")
    return not regressions


# ---- CSV mutation helpers ------------------------------------------------------------------------
def _rw(path, delim, fn):
    rows = list(csv.reader(path.open(encoding="utf-8-sig", newline=""), delimiter=delim))
    rows = fn(rows)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh, delimiter=delim).writerows(rows)


def main_of(d): return next(d.glob("*_Main*.csv"))
def attrs_of(d): return next(d.glob("*_Attributes*.csv"))


def set_attr_value(d, attrname, newval, n=1):
    f = attrs_of(d)
    def fn(rows):
        h = rows[0]; ai, vi = h.index("Attributname"), h.index("Attributwert"); c = 0
        for r in rows[1:]:
            if c < n and len(r) > vi and r[ai] == attrname:
                r[vi] = newval; c += 1
        return rows
    _rw(f, ",", fn)


def drop_attr(d, attrname):
    f = attrs_of(d)
    _rw(f, ",", lambda rows: [rows[0]] + [r for r in rows[1:] if not (len(r) > rows[0].index("Attributname") and r[rows[0].index("Attributname")] == attrname)])


def set_main_value(d, col, newval, n=1):
    f = main_of(d)
    def fn(rows):
        h = rows[0]; ci = h.index(col); c = 0
        for r in rows[1:]:
            if c < n and len(r) > ci:
                r[ci] = newval; c += 1
        return rows
    _rw(f, ";", fn)


def set_price_cluster(d, val, n):
    """Force n SKUs to the SAME non-zero price (templated-cluster signature) — L5 price-sanity."""
    f = next(d.glob("*_Prices*.csv"))
    def fn(rows):
        pi = rows[0].index("Netto-VK"); c = 0
        for r in rows[1:]:
            if c < n and len(r) > pi:
                r[pi] = val; c += 1
        return rows
    _rw(f, ";", fn)


def fixtures():
    tx = ROOT / "output/stage3_Cisco"           # transceiver base (14-attr, reach)
    sw = ROOT / "output/stage3_MikroTik_Switches"  # switch base (S.1-S.6)
    tmp = Path(tempfile.mkdtemp())

    def mk(name, base, mut):
        d = tmp / name; shutil.rmtree(d, ignore_errors=True); shutil.copytree(base, d); mut(d); return d

    rt = lambda f: f.read_text(encoding="utf-8-sig"); wt = lambda f, s: f.write_text(s, encoding="utf-8-sig")
    FX = [
        ("F01 mojibake-umlaut",   sw, lambda d: main_of(d).write_bytes(main_of(d).read_bytes().replace("ü".encode(), "Ã¼".encode(), 1)), "L1"),
        ("F02 BOM-in-body",       sw, lambda d: main_of(d).write_bytes(main_of(d).read_bytes()[:200] + b"\xef\xbb\xbf" + main_of(d).read_bytes()[200:]), "L1"),
        ("F03 unbalanced-</p>",   sw, lambda d: wt(main_of(d), rt(main_of(d)).replace("</p>", "", 1)), "L1"),
        ("F04 stray-<",           sw, lambda d: wt(main_of(d), rt(main_of(d)).replace("<p>", "<p> 3 < 5 ", 1)), "L1"),
        ("F05 wrong-delimiter",   sw, lambda d: wt(main_of(d), rt(main_of(d)).replace(";", ",")), "L1"),
        ("F06 banned-phrase",     sw, lambda d: wt(main_of(d), rt(main_of(d)).replace("</p>", " sofort lieferbar</p>", 1)), "L2"),
        ("F07 wrong-Attributgrp", sw, lambda d: _rw(attrs_of(d), ",", lambda rows: [rows[0]] + [[*(["Switche" if (i == rows[0].index("Attributgruppe")) else c for i, c in enumerate(r)])] for r in rows[1:]]), "L3"),
        ("F08 L3-on-unmanaged",   sw, lambda d: set_attr_value(d, "Switch-Typ", "Unmanaged", n=50), "L3"),
        ("F09 Portanzahl-wrong",  sw, lambda d: set_attr_value(d, "Portanzahl", "999", n=1), "L3"),
        ("F10 [VERIFY]-shipped",  sw, lambda d: set_attr_value(d, "Anwendung", "[VERIFY]", n=1), "L4"),
        ("F11 optic-wt-on-switch", sw, lambda d: set_main_value(d, "Artikelgewicht", "0,05", n=1), "L5"),
        ("F12 reach-out-of-band", tx, lambda d: set_attr_value(d, "Reichweite", "500 km", n=1), "L5"),
        ("F15 missing-DOM",       ROOT / "output/stage3_Juniper",
         lambda d: _rw(attrs_of(d), ",", lambda rows: [rows[0]] + [r for r in rows[1:]
                   if not (len(r) > rows[0].index("Attributname") and r[rows[0].index("Attributname")] == "DOM Unterstützung")]), "L3"),
        # L8 round-3 gate-tightening fixtures (back-applied):
        ("F16 optical-DOM=Nein",  tx, lambda d: set_attr_value(d, "DOM Unterstützung", "Nein", n=300), "L3"),
        ("F17 Formfaktor-unlocked", tx, lambda d: set_attr_value(d, "Formfaktor", "BOGUSFF", n=20), "L3"),
        ("F18 price-cluster",     tx, lambda d: set_price_cluster(d, "1234,56", n=8), "L5"),
        ("F13 count-mismatch-L6", sw, lambda d: _rw(main_of(d), ";", lambda rows: rows[:-1]), "L6"),
    ]
    print("\n=== NEGATIVE FIXTURES (each MUST FAIL at the expected layer) ===")
    ok = True
    for name, base, mut, exp in FX:
        f = fails(mk(name.split()[0], base, mut))
        caught = exp in f
        ok &= caught
        print(f"  {name:24s} failed={f or 'NONE!'} expect {exp} {'OK' if caught else 'BLIND!'}")

    # F14 flag-without-reason-code (L6) — monkeypatch the completeness record to a bad temp one
    badrec = tmp / "bad_completeness.yaml"
    badrec.write_text("MikroTik_switches: {enumerated: 37, captured: 36, flagged: [{family: foo}]}\n", encoding="utf-8")
    orig = G._GATE_COMPLETENESS; G._GATE_COMPLETENESS = badrec
    f = fails(sw)
    G._GATE_COMPLETENESS = orig
    caught = "L6" in f
    ok &= caught
    print(f"  {'F14 flag-no-reason-code':24s} failed={f or 'NONE!'} expect L6 {'OK' if caught else 'BLIND!'}")
    shutil.rmtree(tmp, ignore_errors=True)
    return ok


if __name__ == "__main__":
    kg, fx = known_good(), fixtures()
    print(f"\nKNOWN-GOOD all-pass: {kg} | FIXTURES all-caught: {fx}")
    print("FULL GATE L1-L6 CERTIFIED" if (kg and fx) else "GATE NOT CERTIFIED — fix + re-run")
    sys.exit(0 if (kg and fx) else 1)
