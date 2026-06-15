# -*- coding: utf-8 -*-
"""Probe: measure the near-duplicate-prose blast radius BEFORE wiring the detector into gate.py.
Per bundle, per (Standard, Formfaktor, Reichweite, Wellenlänge) OPTIC cluster (cables exempt — length
variants legitimately reuse prose, MikroTik precedent), mask PN + feature-code, then compute the max
pairwise word-3-shingle Jaccard similarity. Report clusters with max >= THRESHOLD (operator's ~0.85)."""
import csv, re, sys
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]
THRESHOLD = 0.85
KNOWN = ["Cisco", "Arista", "HPE", "Fortinet", "Meraki", "NVIDIA", "MikroTik", "MikroTik_Switches",
         "Juniper", "Extreme", "Dell", "Lenovo"]


def _rd(path, delim):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=delim))
    return (rows[0], rows[1:]) if rows else ([], [])


def shingles(text, k=3):
    w = re.sub(r"<[^>]+>", " ", text)
    w = re.sub(r"[^\wäöüÄÖÜß ]", " ", w).lower().split()
    return set(tuple(w[i:i + k]) for i in range(len(w) - k + 1)) if len(w) >= k else set()


def jacc(a, b):
    return len(a & b) / len(a | b) if (a or b) else 0.0


def probe(brand):
    d = ROOT / f"output/stage3_{brand}"
    mh, mr = _rd(next(d.glob("*_Main*.csv")), ";")
    ah, ar = _rd(next(d.glob("*_Attributes*.csv")), ",")
    if not mh or "Beschreibung" not in mh:
        return []
    i_sku, i_be = mh.index("Artikelnummer"), mh.index("Beschreibung")
    desc = {r[i_sku]: r[i_be] for r in mr if len(r) > i_be}
    si, ni, vi = ah.index("Artikelnummer"), ah.index("Attributname"), ah.index("Attributwert")
    attr = {}
    for r in ar:
        if len(r) > vi:
            attr.setdefault(r[si], {})[r[ni]] = r[vi]
    clusters = {}
    for sku, be in desc.items():
        a = attr.get(sku, {})
        ff = a.get("Formfaktor", "")
        if ff.endswith("Kabel"):                      # cable exemption
            continue
        sig = (a.get("Standard", ""), ff, a.get("Reichweite", ""), a.get("Wellenlänge", ""))
        masked = re.sub(re.escape(sku), "PN", be, flags=re.I)
        masked = re.sub(r"Feature-Code\s+\w+", "Feature-Code X", masked)
        clusters.setdefault(sig, []).append((sku, shingles(masked)))
    hits = []
    for sig, members in clusters.items():
        if len(members) < 2:
            continue
        mx = 0.0; worst = None
        for (s1, sh1), (s2, sh2) in combinations(members, 2):
            j = jacc(sh1, sh2)
            if j > mx:
                mx, worst = j, (s1, s2)
        if mx >= THRESHOLD:
            hits.append((sig, len(members), mx, worst))
    return hits


if __name__ == "__main__":
    for b in KNOWN:
        hits = probe(b)
        if hits:
            print(f"\n### {b}: {len(hits)} cluster(s) >= {THRESHOLD}")
            for sig, n, mx, worst in sorted(hits, key=lambda x: -x[2])[:8]:
                print(f"   sim={mx:.2f} n={n} {worst}  sig={sig[0]}/{sig[1]}/{sig[2]}/{sig[3][:18]}")
        else:
            print(f"{b}: clean (no optic cluster >= {THRESHOLD})")
