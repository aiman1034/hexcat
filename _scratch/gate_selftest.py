# -*- coding: utf-8 -*-
"""Self-test for src/hexcat/gate.py (MISSION §8 L7 anti-blind-spot proof).
Run: python _scratch/gate_selftest.py
  (1) KNOWN-GOOD: the 8 emitted bundles must PASS the LIVE layers (L1-L4).
  (2) NEGATIVE FIXTURES: deliberately-broken copies must FAIL at the expected layer — proves the
      gate isn't blind (the B.8 false-green lesson). Any fixture that PASSES = gate blind -> fix.
TODO (next chunk): institutionalize a fixture per L3/L4/L5/L6 check class once L5/L6 land.
"""
import sys, shutil, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hexcat.config import load_rules
from hexcat.gate import gate

RULES = load_rules()
KNOWN = ["Cisco", "Arista", "HPE", "Fortinet", "Meraki", "NVIDIA", "MikroTik", "MikroTik_Switches"]
LIVE = ("L1", "L2", "L3", "L4")


def live_fails(d):
    return [L.layer for L in gate(d, RULES).layers if L.layer in LIVE and not L.passed]


def known_good():
    print("=== KNOWN-GOOD (LIVE layers L1-L4 must PASS) ===")
    ok = True
    for b in KNOWN:
        f = live_fails(Path(f"output/stage3_{b}"))
        ok &= not f
        print(f"  {b:20s} {'PASS' if not f else 'FAIL '+str(f)}")
    return ok


def fixtures():
    base = Path("output/stage3_MikroTik_Switches")
    main = next(base.glob("*_Main*.csv")).name
    tmp = Path(tempfile.mkdtemp())
    def mk(n, mut):
        d = tmp / n; shutil.rmtree(d, ignore_errors=True); shutil.copytree(base, d); mut(d / main); return d
    rt = lambda f: f.read_text(encoding="utf-8-sig")
    wt = lambda f, s: f.write_text(s, encoding="utf-8-sig")
    FX = {
        "F1 mojibake-umlaut": (lambda f: f.write_bytes(f.read_bytes().replace("ü".encode(), "Ã¼".encode(), 1)), "L1"),
        "F2 BOM-in-body":     (lambda f: f.write_bytes(f.read_bytes()[:200] + b"\xef\xbb\xbf" + f.read_bytes()[200:]), "L1"),
        "F3 unbalanced-<p>":  (lambda f: wt(f, rt(f).replace("</p>", "", 1)), "L1"),
        "F4 stray-<":         (lambda f: wt(f, rt(f).replace("<p>", "<p> 3 < 5 ", 1)), "L1"),
        "F5 wrong-delimiter": (lambda f: wt(f, rt(f).replace(";", ",")), "L1"),
        "F6 banned-phrase":   (lambda f: wt(f, rt(f).replace("</p>", " sofort lieferbar</p>", 1)), "L2"),
    }
    print("\n=== NEGATIVE FIXTURES (each MUST FAIL at the expected layer) ===")
    ok = True
    for name, (mut, exp) in FX.items():
        f = live_fails(mk(name.split()[0], mut))
        caught = exp in f
        ok &= caught
        print(f"  {name:22s} failed={f or 'NONE!'} expect {exp} {'OK' if caught else 'BLIND!'}")
    shutil.rmtree(tmp, ignore_errors=True)
    return ok


if __name__ == "__main__":
    kg, fx = known_good(), fixtures()
    print(f"\nKNOWN-GOOD all-pass: {kg} | FIXTURES all-caught: {fx}")
    print("GATE L1-L4 CERTIFIED" if (kg and fx) else "GATE NOT CERTIFIED")
    sys.exit(0 if (kg and fx) else 1)
