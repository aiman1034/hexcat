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

# Thin clusters HELD for an operator scope decision (NOT re-author candidates). The Juniper
# JNP-QSFP-100G-LR-CW27/29/31/33 are absent from Juniper's official optics guide, physically impossible
# as single-λ 100G (single-λ 100G exists only at 1311 nm / 100G-LR1), and sourced from a compatible-optics
# catalog — the four lanes of ONE JNP-QSFP-100G-CWDM4 module mis-exploded into single-λ SKUs. Likely
# OUT-OF-SCOPE. See PROJECT_AUDIT. (The other 22 Juniper thin SKUs were re-authored per-channel, 2026-06-16.)
SCOPE_HELD = {"JNP-QSFP-100G-LR-CW27", "JNP-QSFP-100G-LR-CW29",
              "JNP-QSFP-100G-LR-CW31", "JNP-QSFP-100G-LR-CW33"}
SCOPE_HELD_REASON = ("HELD pending operator scope decision — phantom single-λ 100G (the four CWDM lanes of "
                     "one JNP-QSFP-100G-CWDM4 mis-exploded into single-λ SKUs); absent from Juniper's official "
                     "optics guide, sourced from a compatible-optics catalog. Likely OUT-OF-SCOPE; NOT a "
                     "per-channel re-author candidate. See PROJECT_AUDIT.")


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
    iti = next((i for i, c in enumerate(mh) if c.startswith("Titel-Tag")), -1)
    desc = {r[isku]: r[ibe] for r in mr if len(r) > max(isku, ibe)}
    k3 = {r[isku]: (r[ik3] if ik3 >= 0 and len(r) > ik3 else "") for r in mr if len(r) > isku}
    titel = {r[isku]: (r[iti] if iti >= 0 and len(r) > iti else "") for r in mr if len(r) > isku}
    si, ni, vi = ah.index("Artikelnummer"), ah.index("Attributname"), ah.index("Attributwert")
    at = {}
    for r in ar:
        if len(r) > vi:
            at.setdefault(r[si], {})[r[ni]] = r[vi]
    recs = []
    for sku, be in desc.items():
        a = at.get(sku, {}); std = a.get("Standard", ""); ff = a.get("Formfaktor", "")
        ends = a.get("Anschlusstyp") or a.get("Anschlussenden") or ""
        if (not std or G._CABLE_STD.search(std) or " auf " in ends
                or ff.endswith("Kabel") or "Kabel" in (k3.get(sku) or "")):
            continue
        be_text = re.sub(r"<[^>]+>", " ", be)
        base = G._FC_MASK.sub("Feature-Code X", re.sub(re.escape(sku), "PN", be, flags=re.I))
        base_text = re.sub(re.escape(sku), "", be_text, flags=re.I)
        wl = a.get("Wellenlänge", "")
        nums = set(G._LAMBDA_NM.findall(wl or ""))
        ident = bool(nums) and any(n in (titel.get(sku) or "") for n in nums) and any(n in base_text for n in nums)
        recs.append((sku, std, ff, a.get("Reichweite", ""), wl,
                     G._shingles(base), G._shingles(G._LAMBDA_MASK.sub("WL", base)), ident))
    hits, seen = [], set()

    def _add(mem_pns, std, ff, reason):
        key = frozenset(mem_pns)
        if key in seen:
            return
        seen.add(key)
        hits.append({"members": sorted(mem_pns), "std": std, "ff": ff, "reason": reason})

    # PASS 1 — same (Std,FF,reach,λ) same-product alias/revision clusters (kept).
    p1 = {}
    for sku, std, ff, reach, wl, sh, _shl, _id in recs:
        p1.setdefault((std, ff, reach, wl), []).append((sku, sh))
    for sig, mem in p1.items():
        if len(mem) >= 2 and any(G._jaccard(h1, h2) >= G._NEAR_DUP_SIM for (s1, h1), (s2, h2) in combinations(mem, 2)):
            pns = [s for s, _ in mem]
            reason = ("revision/variant family (shared PN stem) — same optic, prose reuse accepted at L8"
                      if len({stem(p) for p in pns}) == 1 else
                      "cross-name alias(es) of one optic — prose reuse accepted at L8")
            _add(pns, sig[0], sig[1], reason)
    # PASS 2 — λ-channel families. The gate exempts well-formed grids (λ in Titel+prose) + BiDi matched-pairs
    # STRUCTURALLY (no entry). We baseline ONLY the genuinely-THIN grids the gate would flag — non-BiDi,
    # members lacking channel identity in prose — with an HONEST fix-pending reason (NOT "correct").
    p2 = {}
    for sku, std, ff, reach, wl, _sh, shl, ident in recs:
        p2.setdefault((G._norm_key(std), G._norm_key(ff), G._norm_key(reach)), []).append((sku, wl, shl, ident))
    for sig, mem in p2.items():
        if len(mem) < 2 or len({w for _, w, _, _ in mem}) < 2 or all(i for _, _, _, i in mem):
            continue
        if any(re.search(r"BiDi|\bT[xX]\b|\bR[xX]\b", w) for _, w, _, _ in mem) or "BX" in sig[0] or "BiDi" in sig[0]:
            continue   # BiDi matched-pair -> gate exempts structurally, no entry
        # only the members in flagged (>=0.85, at-least-one-thin) pairs are the genuinely-thin grid SKUs
        thin = set()
        for (s1, w1, h1, i1), (s2, w2, h2, i2) in combinations(mem, 2):
            if not (i1 and i2) and G._jaccard(h1, h2) >= G._NEAR_DUP_SIM:
                thin.add(s1); thin.add(s2)
        if thin:
            reason = (SCOPE_HELD_REASON if set(thin) <= SCOPE_HELD else
                      "THIN λ-grid — wavelength in PN/attr only, generic templated prose (below the Cisco "
                      "λ-in-prose standard). KNOWN DEFECT, fix-pending (re-author per-channel); NOT certified-correct")
            _add(sorted(thin), sig[0], sig[1], reason)
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
