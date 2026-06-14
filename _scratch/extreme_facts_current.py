# -*- coding: utf-8 -*-
"""Extreme optics — RE-HARVEST from the CURRENT official datasheet (Workflow B, operator L8 finding B:
one guide undercounts the universe). Source: datasheets/cache/extreme-optical-transceivers-cables-
current.pdf (Extreme "Optical Transceivers and Cables", sitecorecontenthub — the current version, 15 pp).
Same 3-logical-column schema as the cached Optics Solution Guide (Standard/Type | Description | Extreme
Products) but rendered as 9 RAW columns (merged cells) -> collapse to the 3 logical columns, then reuse
extreme_facts.py's proven per-row grounding helpers verbatim. Output: extreme_facts_current.json.
"""
import sys, json, re
from collections import Counter
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scratch"))
import extreme_facts as EF  # reuse the verified helpers

PDF = ROOT / "datasheets" / "cache" / "extreme-optical-transceivers-cables-current.pdf"
OUT = ROOT / "output" / "stage3" / "extreme_facts_current.json"
FLAGS = ROOT / "output" / "stage3" / "extreme_flags_current.txt"
EF.flags = []                                   # fresh flag list for this harvest


def collapse_rows(pdf):
    """9-col merged-cell tables -> (page, std, desc, products) logical rows."""
    out = []
    for pi, pg in enumerate(pdf.pages):
        for tb in (pg.extract_tables() or []):
            if not tb or not tb[0]:
                continue
            hdr = [(c or "").strip() for c in tb[0]]
            if "Standard/Type" not in hdr:
                continue
            si = hdr.index("Standard/Type")
            di = hdr.index("Description") if "Description" in hdr else 4
            pidx = hdr.index("Extreme Products") if "Extreme Products" in hdr else 7
            for r in tb[1:]:
                std = (r[si] or "").replace("\n", " ").strip() if si < len(r) else ""
                desc = (r[di] or "").replace("\n", " ").strip() if di < len(r) else ""
                sku = (r[pidx] or "").replace("\n", " ").strip() if pidx < len(r) else ""
                if any((std, desc, sku)) and std != "Standard/Type":
                    out.append((pi, std, desc, sku))
    return out


def main():
    facts = {}

    def add(pn, **kw):
        pn = pn.strip()
        if pn in facts:
            EF.flag("DUP PN %s -> keeping first" % pn); return
        facts[pn] = kw

    with pdfplumber.open(PDF) as pdf:
        rows = collapse_rows(pdf)

    for pi, std, desc, sku in rows:
        std_c = EF.repair_wrap(std)
        toks = EF.tokens(sku)
        kinds = [EF.classify(t) for t in toks]
        desc_pns = [t for t, k in zip(toks, kinds) if k == "desc"]
        num_pns = [t for t, k in zip(toks, kinds) if k == "num"]
        aa_pns = [t for t, k in zip(toks, kinds) if k == "aa"]
        speed = EF.parse_speed(std_c, desc)
        ff = EF.parse_ff(desc)
        conn = EF.parse_connector(desc)
        media = EF.parse_media(desc)
        cable = EF.is_cable_row(std_c, desc)
        breakout = bool(re.search(r"Breakout|to 4x|to 2x|4xSFP|2xSFP|2SFP|4SFP|1SFP", std_c + " " + desc, re.I))
        ttype = std_c.split("BASE-")[-1] if "BASE-" in std_c else std_c
        base = dict(standard=std_c, speed=speed, ff=ff, connector=conn, media=media,
                    breakout=breakout, page=pi, row="%s | %s | %s" % (std, desc, sku), alt_pns=[])
        if cable:
            desc_lengths = re.findall(r"(\d+)(?:\.\d+)?\s*m\b", desc)
            ff_cab = ff or EF.CABLE_FF.get(speed)
            fam_pns = [p for p in desc_pns if EF.cable_marker(p)]
            if desc_pns and not fam_pns:
                EF.flag("CORRUPT/SHIFTED cable row '%s' PNs lack DAC/AOC: %s -> EXCLUDED" % (std, desc_pns)); continue
            if not fam_pns:
                EF.flag("AMBIGUOUS cable '%s' no descriptive length-PN (num %s) -> EXCLUDED" % (std, num_pns)); continue
            for p in fam_pns:
                ln = EF.length_from_pn(p, desc_lengths)
                tinfo = EF.cable_type_from_pn(p)
                if ln is None:
                    EF.flag("cable PN %s ('%s') no length -> EXCLUDED" % (p, std)); continue
                if tinfo is None:
                    EF.flag("cable PN %s ('%s') no DAC/AOC marker -> EXCLUDED" % (p, std)); continue
                ctype, active = tinfo
                add(p, **{**base, "ff": ff_cab, "type": ctype, "active": active, "length": ln,
                          "reach_m": None, "om": EF.parse_om(desc), "wavelength": None,
                          "alt_pns": [t for t in toks if t != p]})
        else:
            if desc_pns:
                primary = desc_pns[0]
            elif num_pns:
                primary = num_pns[0]
            elif aa_pns:
                primary = aa_pns[0]
            else:
                EF.flag("NO usable PN for transceiver row '%s' (toks=%s) -> EXCLUDED" % (std, toks)); continue
            add(primary, **{**base, "type": ttype.strip(), "active": False, "length": None,
                            "reach": EF.parse_reach(desc), "om": EF.parse_om(desc),
                            "wavelength": EF.derive_wavelength(std_c, ttype, media),
                            "alt_pns": [t for t in toks if t != primary]})

    OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    FLAGS.write_text("\n".join(EF.flags), encoding="utf-8")
    cab = sum(1 for v in facts.values() if v.get("type") in ("DAC", "AOC"))
    print("CURRENT-datasheet SKUs: %d (transceivers %d, cables %d)" % (len(facts), len(facts) - cab, cab))
    print("by speed:", dict(Counter(v.get("speed") for v in facts.values())))
    print("flags:", len(EF.flags))


if __name__ == "__main__":
    main()
