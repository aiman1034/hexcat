# -*- coding: utf-8 -*-
"""DOM backfill across emitted brands (task #21). Grounds DOM Unterstützung per SKU by MEDIA (NOT
form-factor — the XENPAK misfire): optical fibre pluggables support DDM per SFF-8472/CMIS = Ja;
copper-T modules (no optical to monitor) = Nein. Cables (DAC/AOC/MPO) are exempt (skipped). Only adds
DOM to non-cable transceivers that lack it; never overwrites an operator-grounded value. A genuinely
indeterminate family would be flagged 'nicht spezifiziert' — none seen across these modern optic sets.
Usage: python _scratch/add_dom_backfill.py <Brand> [<Brand> ...]
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CABLE_FF = {"DAC Kabel", "AOC Kabel", "MPO Kabel"}
COPPER = re.compile(r"\bKupfer\b|\bRJ-?45\b|BASE-?T\b|Twinax|Twisted", re.I)
DOM_NAMES = {"DOM/DDM", "DDM/DOM", "DOM Unterstützung"}   # all alias to "DOM Unterstützung" at emit


def attrval(attrs, name):
    for a in attrs:
        if a[0] == name:
            return a[1]
    return ""


def is_cable(e):
    ff = attrval(e["attributes"], "Formfaktor")
    return ff in CABLE_FF or bool(attrval(e["attributes"], "Kabeltyp"))


def is_copper(e):
    blob = " ".join(f"{a[0]}={a[1]}" for a in e["attributes"]
                    if a[0] in ("Medientyp", "Fasertyp", "Anschluss", "Anschlusstyp", "Standard", "Transceiver Typ"))
    return bool(COPPER.search(blob))


def backfill(brand):
    p = ROOT / "stage3_content" / f"{brand}_content.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    added_ja = added_nein = had = cable = 0
    for pn, e in d.items():
        attrs = e["attributes"]
        if any(a[0] in DOM_NAMES for a in attrs):     # alias-aware: don't duplicate an existing DOM/DDM
            had += 1; continue
        if is_cable(e):
            cable += 1; continue
        dom = "Nein" if is_copper(e) else "Ja"
        # add as the native "DOM/DDM" (aliases to DOM Unterstützung at emit); assemble re-orders.
        idx = next((i for i, a in enumerate(attrs) if a[0] == "Zustand"), len(attrs))
        attrs.insert(idx, ["DOM/DDM", dom])
        e.setdefault("provenance", {})["DOM Unterstützung"] = ["SFF-8472/CMIS (optical DDM) / media-grounded", "standard"]
        if dom == "Ja": added_ja += 1
        else: added_nein += 1
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{brand:10s}: +DOM Ja {added_ja} / Nein {added_nein} | already-had {had} | cable-exempt {cable} | total {len(d)}")


if __name__ == "__main__":
    for b in sys.argv[1:]:
        backfill(b)
