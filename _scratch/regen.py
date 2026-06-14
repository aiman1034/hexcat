# -*- coding: utf-8 -*-
"""Regenerate a brand's Stage-3 bundle from its content file and validate. $0, deterministic.
Usage: python _scratch/regen.py [Brand ...]   (default: all five)"""
import sys, shutil
from pathlib import Path
from hexcat.config import load_rules, load_weights
from hexcat.stage3 import reconcile_content, ReconcileError
from hexcat.assemble import assemble_bundle
from hexcat.validate import validate_dir

BRANDS = sys.argv[1:] or ["Cisco", "Arista", "HPE", "Fortinet", "MikroTik"]
rules = load_rules()
weights = load_weights()

# author->emit parity advisory (operator L8: non-schema data must not vanish SILENTLY). A content
# `attributes` entry whose name neither aliases to the 14-schema nor lands in another emitted file
# (Zustand -> Condition CSV) is DROPPED -> warn. Decorative top-level keys (kompatibilitaet/verwandte)
# are known-not-emitted: never put load-bearing data there (alt-PNs belong woven into the Beschreibung).
from hexcat.stage3.reconcile import ATTR_ALIAS  # noqa: E402
import hexcat.constants as _C  # noqa: E402
import json as _json  # noqa: E402
_EMITTED_ELSEWHERE = {"Zustand"}  # -> Condition CSV, not an Attributes row


def parity_advisory(brand):
    p = Path(f"stage3_content/{brand}_content.json")
    if not p.exists():
        return
    data = _json.loads(p.read_text(encoding="utf-8"))
    canon = set(_C.TRANSCEIVER_ATTRIBUTES)
    dropped = {}
    for pn, e in data.items():
        for a in e.get("attributes", []):
            nm = a[0]
            if nm in _EMITTED_ELSEWHERE or nm in canon or ATTR_ALIAS.get(nm):
                continue
            dropped.setdefault(nm, 0)
            dropped[nm] += 1
    if dropped:
        print(f"  ⚠ author→emit parity: {brand} attributes NOT emitted (silently dropped): {dropped}")

for brand in BRANDS:
    content = Path(f"stage3_content/{brand}_content.json")
    out = Path(f"output/stage3_{brand}")
    staging = out / ".staging"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        records = reconcile_content(content, brand=brand, rules=rules, weights=weights)
    except ReconcileError as e:
        print(f"{brand:10s} RECONCILE-ERROR: {e}")
        continue
    assemble_bundle(records, rules, batch=brand, category=f"{brand}_Transceivers", out_dir=staging)
    r = validate_dir(rules, staging)
    n = len(records)
    if r.ok:
        for f in staging.glob("*"):
            shutil.move(str(f), str(out / f.name))
        shutil.rmtree(staging, ignore_errors=True)
        print(f"{brand:10s} GREEN  ({n} SKUs)  warnings={len(r.warnings)}")
        parity_advisory(brand)
    else:
        reuse = [v for v in r.violations if "boilerplate" in v.message]
        well = [v for v in r.violations if "optical-module" in v.message]
        floor = [v for v in r.violations if "word count" in v.message]
        other = [v for v in r.violations if v not in reuse and v not in well and v not in floor]
        print(f"{brand:10s} RED ({n} SKUs) viol={len(r.violations)} "
              f"| reuse={len(reuse)} well={len(well)} floor={len(floor)} other={len(other)}")
        for v in (reuse[:3] + well[:3] + floor[:3] + other[:5]):
            print(f"    [{v.field}] {v.sku}: {v.message[:75]} :: got={v.got[:60]}")
