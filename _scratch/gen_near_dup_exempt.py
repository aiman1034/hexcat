# -*- coding: utf-8 -*-
"""Generate config/near_dup_exempt.yaml — the reason-coded baseline of same-product near-duplicate optic
clusters in already-operator-CLEARED brands (the completeness-flag pattern, applied to prose). The new L5
near-dup detector enforces "no NEW near-dups" catalog-wide; this baseline records the pre-existing,
L8-accepted alias/revision/variant prose so cleared brands stay green without re-opening their copy.
Lenovo is EXCLUDED — its clusters were genuinely de-duplicated (unique voices), not baselined.
Re-run only when a cleared brand is re-authored. Spawns nothing; a backlog task tracks weaving these."""
import csv, re, yaml
from pathlib import Path
from itertools import combinations
import hexcat.gate as G

ROOT = Path(__file__).resolve().parents[1]
# every cleared brand EXCEPT Lenovo (Lenovo is fixed, not baselined)
BRANDS = ["Cisco", "Arista", "HPE", "Fortinet", "Meraki", "NVIDIA", "MikroTik", "Juniper", "Extreme", "Dell"]


def _rd(p, d):
    rows = list(csv.reader(p.open(encoding="utf-8-sig", newline=""), delimiter=d))
    return (rows[0], rows[1:]) if rows else ([], [])


def stem(pn):
    s = re.sub(r"[^A-Z0-9]", "", pn.upper())
    s = re.sub(r"^(JNP|QFX|EX|MX|PTX|ACX|SRX|CTP|RX)", "", s)
    s = re.sub(r"(LP|INT|ON|ET|GEN\d|[A-D])$", "", s)
    return s


def clusters_for(brand):
    d = ROOT / f"output/stage3_{brand}"
    mh, mr = _rd(next(d.glob("*_Main*.csv")), ";")
    ah, ar = _rd(next(d.glob("*_Attributes*.csv")), ",")
    if "Beschreibung" not in mh:
        return []
    isku, ibe = mh.index("Artikelnummer"), mh.index("Beschreibung")
    ik3 = mh.index("Kategorie Ebene 3") if "Kategorie Ebene 3" in mh else -1
    desc = {r[isku]: r[ibe] for r in mr if len(r) > max(isku, ibe)}
    k3 = {r[isku]: (r[ik3] if ik3 >= 0 and len(r) > ik3 else "") for r in mr if len(r) > isku}
    si, ni, vi = ah.index("Artikelnummer"), ah.index("Attributname"), ah.index("Attributwert")
    at = {}
    for r in ar:
        if len(r) > vi:
            at.setdefault(r[si], {})[r[ni]] = r[vi]
    cl = {}
    for sku, be in desc.items():
        a = at.get(sku, {}); std = a.get("Standard", ""); ff = a.get("Formfaktor", "")
        ends = a.get("Anschlusstyp") or a.get("Anschlussenden") or ""
        if (not std or G._CABLE_STD.search(std) or " auf " in ends
                or ff.endswith("Kabel") or "Kabel" in (k3.get(sku) or "")):
            continue
        sig = (std, ff, a.get("Reichweite", ""), a.get("Wellenlänge", ""))
        masked = G._FC_MASK.sub("Feature-Code X", re.sub(re.escape(sku), "PN", be, flags=re.I))
        cl.setdefault(sig, []).append((sku, G._shingles(masked)))
    hits = []
    for sig, mem in cl.items():
        if len(mem) < 2:
            continue
        if any(G._jaccard(h1, h2) >= G._NEAR_DUP_SIM for (s1, h1), (s2, h2) in combinations(mem, 2)):
            pns = sorted(s for s, _ in mem)
            reason = ("revision/variant family (shared PN stem) — same optic, prose reuse accepted at L8"
                      if len({stem(p) for p in pns}) == 1 else
                      "cross-name alias(es) of one optic — prose reuse accepted at L8")
            hits.append({"members": pns, "std": sig[0], "ff": sig[1], "reason": reason})
    return hits


def main():
    rec = {}
    total = 0
    for b in BRANDS:
        h = clusters_for(b)
        if h:
            rec[b] = h
            total += len(h)
    out = ROOT / "config" / "near_dup_exempt.yaml"
    header = ("# Near-duplicate-prose exemption baseline (L8 Lenovo finding ①). Reason-coded record of\n"
              "# same-product alias/revision/variant optic clusters in operator-CLEARED brands whose prose\n"
              "# was accepted before the L5 near-dup detector existed. The detector enforces NO NEW near-dups\n"
              "# catalog-wide; these are the grandfathered baseline (cables are exempt in-code, not listed).\n"
              "# Lenovo is intentionally ABSENT — its clusters were de-duplicated, not baselined.\n"
              "# Backlog: weave these per dedup rule #4. Re-generate via _scratch/gen_near_dup_exempt.py.\n")
    out.write_text(header + yaml.safe_dump(rec, allow_unicode=True, sort_keys=True, width=120), encoding="utf-8")
    print("wrote %s : %d brands, %d exempted clusters" % (out.name, len(rec), total))
    for b in sorted(rec):
        print("   %-10s %d cluster(s)" % (b, len(rec[b])))


if __name__ == "__main__":
    main()
