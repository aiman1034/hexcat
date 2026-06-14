# -*- coding: utf-8 -*-
"""Ground the remaining Juniper tiers (40G/25G/10G/1G/FE/200G) from the MSA standard each PN encodes.
type/reach/connector/media grounded from the standard; λ decoded where the PN encodes it unambiguously
(GE80KCW1470, CWDM1471, DW3033, 13R14 BiDi pairs), else flagged [VERIFY]. AddOn -J codes -> alias/flag."""
import json, re
from pathlib import Path
from collections import Counter
R = Path(__file__).resolve().parents[1] / "output" / "stage3"
G = json.loads((R / "juniper_grounded_facts.json").read_text(encoding="utf-8"))
AL = json.loads((R / "juniper_aliases.json").read_text(encoding="utf-8"))
FO = json.loads((R / "juniper_flagged_out.json").read_text(encoding="utf-8"))
mods = set(json.loads((R / "juniper_locked_universe.json").read_text(encoding="utf-8"))["modules"])
remaining = sorted(mods - set(G) - set(AL) - set(FO))
SRC = "juniper distributor enumeration + MSA standard (PN-encoded)"


def E(pn, ff, sp, std, reach, wl, conn, media, lanes=1, bidi=False, flags=None, note=""):
    return {"sku": pn, "form_factor": ff, "speed": sp, "standard": std, "type": std.split()[-1],
            "media": media, "connector": conn, "reach": reach, "wavelengths_nm": wl, "lanes": lanes,
            "bidi": bidi, "grounded": True, "source": SRC, "flags": flags or [], "note": note}


def dw(code):   # DW3033 -> 1530.33 nm
    m = re.search(r"DW(\d{2})(\d{2})", code)
    return f"15{m.group(1)}.{m.group(2)} nm" if m else "[VERIFY]"


def bidi(code):  # 13R14 -> [TX 1310, RX 1490]
    m = re.search(r"(\d)(\d)R(\d)(\d)", code)
    mp = {"13": "1310", "14": "1490", "15": "1550", "12": "1270", "31": "1310", "49": "1490"}
    if m:
        tx, rx = mp.get(m.group(1) + m.group(2)), mp.get(m.group(3) + m.group(4))
        if tx and rx:
            return [f"TX {tx}", f"RX {rx}"]
    return ["[VERIFY]"]


ALIASES = {"QSFP-40GBASE-LR4-20-J": "JNP-QSFP-40G-LR4-20"}
FLAGOUT = {k: "AddOn house code; not a genuine Juniper PN in the guides" for k in
           ("QSFP-40GB-ZR4-J", "QSFP-40GBASE-PLR-J", "QSFP-40GBASE-SR4L-J",
            "XFP-10G-BX-D-20KM-J", "XFP-10G-BX-U-20KM-J", "XFP-10GB-BX-D-60-J", "XFP-10GB-BX-U-60-J")}
CWDM4 = ["1271", "1291", "1311", "1331"]
LANWDM = ["1295", "1300", "1305", "1309"]

added = 0
for pn in remaining:
    u = pn.upper()
    if pn in ALIASES:
        AL[pn] = ALIASES[pn]; continue
    if pn in FLAGOUT:
        FO[pn] = {"reason_code": "un-groundable-after-ladder", "note": FLAGOUT[pn]}; continue
    e = None
    if re.search(r'40G|QSFPP-40|QSFP-40', u):
        ff = "QSFP+"
        if "SR4" in u:    e = E(pn, ff, "40G", "40GBASE-SR4", "150 m (OM4)", ["850"], "MPO-12", "MMF", 4)
        elif "ESR4" in u: e = E(pn, ff, "40G", "40G-ESR4", "400 m (OM4)", ["850"], "MPO-12", "MMF", 4)
        elif "SWDM4" in u:e = E(pn, ff, "40G", "40G-SWDM4", "350 m (OM4)", ["850", "880", "910", "940"], "Duplex LC", "MMF", 4, note="SWDM 4λ")
        elif "BXSR" in u: e = E(pn, ff, "40G", "40G SR BiDi", "100 m (OM4)", ["832", "918"], "Duplex LC", "MMF", 2, bidi=True)
        elif "LX4" in u:  e = E(pn, ff, "40G", "40G-LX4", "2 km (SMF) / 150 m (OM4)", CWDM4, "Duplex LC", "SMF/MMF", 4)
        elif "ER4" in u:  e = E(pn, ff, "40G", "40GBASE-ER4", "40 km", CWDM4, "Duplex LC", "SMF", 4)
        elif "IR4" in u:  e = E(pn, ff, "40G", "40G-IR4", "2 km", CWDM4, "Duplex LC", "SMF", 4)
        elif "LR4-20" in u: e = E(pn, ff, "40G", "40GBASE-LR4", "20 km", CWDM4, "Duplex LC", "SMF", 4)
        elif "LR4" in u:  e = E(pn, ff, "40G", "40GBASE-LR4", "10 km", CWDM4, "Duplex LC", "SMF", 4)
    elif "25G" in u:
        ff = "SFP28"
        if re.search(r'-SR\b', u) or u.endswith("-SR"): e = E(pn, ff, "25G", "25GBASE-SR", "100 m (OM4)", ["850"], "Duplex LC", "MMF")
        elif "DW" in u:   e = E(pn, ff, "25G", "25G-LR DWDM", "10 km", [dw(u)], "Duplex LC", "SMF", note="fixed DWDM channel" + (" (ind.)" if "-I-" in u else ""))
        elif re.search(r'CW-?\d\d', u):
            ch = re.search(r'CW-?(\d\d)', u).group(1); r = "40 km" if "40" in u else "10 km"
            e = E(pn, ff, "25G", f"25G-LR CWDM(ch{ch})", r, ["[VERIFY]"], "Duplex LC", "SMF", flags=["CWDM channel λ [VERIFY] per-SKU"], note="single CWDM λ")
        elif "BX" in u:
            r = "40 km" if "40" in u else "10 km"
            e = E(pn, ff, "25G", "25G-LR BiDi", r, ["[VERIFY]"], "Simplex LC", "SMF", bidi=True, flags=["BiDi λ-pair [VERIFY]"], note="single-fiber BiDi" + (" (ind.)" if u.endswith("-I") else ""))
        elif "LR" in u:   e = E(pn, ff, "25G", "25GBASE-LR", "10 km", ["1310"], "Duplex LC", "SMF")
    elif re.search(r'10G|10GE|SFPP', u):
        ff = "XFP" if u.startswith("XFP") else "SFP+"
        if "4X10G" in u:
            r = "10 km" if "LR" in u else "1.4 km"; e = E(pn, "QSFP+", "40G", "40G 4x10GE", r, ["1310"], "MPO-12 / breakout", "SMF", 4, note="QSFP+ breakout 4x10G")
        elif "CWDM" in u:
            m = re.search(r'CWDM(\d{4})', u); e = E(pn, ff, "10G", "10G-CWDM", "80 km", [m.group(1) if m else "[VERIFY]"], "Duplex LC", "SMF")
        elif "BX" in u:
            m = re.search(r'BX(\d{2})', u); r = (m.group(1) + " km") if m else ("80 km" if "80" in u else "40 km" if "40" in u else "20 km" if "20" in u else "10 km")
            e = E(pn, ff, "10G", "10G-BX BiDi", r, ["[VERIFY]"], "Simplex LC", "SMF", bidi=True, flags=["BiDi λ-pair [VERIFY]"], note="single-fiber BiDi" + (" (ind. temp)" if "-IT" in u else ""))
        elif u.endswith("-T") or "10GE-T" in u: e = E(pn, ff, "10G", "10GBASE-T", "30 m (Cat6a)", [], "RJ45", "Kupfer")
        elif "LRM" in u: e = E(pn, ff, "10G", "10GBASE-LRM", "220 m (OM3)", ["1310"], "Duplex LC", "MMF")
        elif "USR" in u: e = E(pn, ff, "10G", "10G-USR", "100 m (OM4)", ["850"], "Duplex LC", "MMF")
        elif "ZR" in u:  e = E(pn, ff, "10G", "10G-ZR", "80 km", ["1550"], "Duplex LC", "SMF")
        elif "ER" in u:  e = E(pn, ff, "10G", "10GBASE-ER", "40 km", ["1550"], "Duplex LC", "SMF")
        elif "LR" in u:  e = E(pn, ff, "10G", "10GBASE-LR", "10 km", ["1310"], "Duplex LC", "SMF")
        elif "SR" in u:  e = E(pn, ff, "10G", "10GBASE-SR", "300 m (OM3)", ["850"], "Duplex LC", "MMF")
    elif re.search(r'1GE|1000|GE\d*KT|GE80KCW|RX-', u):
        ff = "SFP"
        if "GE80KCW" in u:
            m = re.search(r'CW(\d{4})', u); e = E(pn, ff, "1G", "1G-CWDM", "80 km", [m.group(1) if m else "[VERIFY]"], "Duplex LC", "SMF")
        elif re.search(r'GE(\d+)KT', u):
            km = re.search(r'GE(\d+)KT', u).group(1); e = E(pn, ff, "1G", "1000BASE-BX", f"{km} km", bidi(u), "Simplex LC", "SMF", bidi=True, note="single-fiber BiDi" + (" (ind.)" if u.endswith("-I") else ""))
        elif "LX40K" in u: e = E(pn, ff, "1G", "1000BASE-EX", "40 km", ["1310"], "Duplex LC", "SMF", note="LX 40km" + (" (ind.)" if "-I" in u else ""))
        elif "LH" in u:  e = E(pn, ff, "1G", "1000BASE-ZX/LH", "70 km", ["1550"], "Duplex LC", "SMF")
        elif "LX" in u:  e = E(pn, ff, "1G", "1000BASE-LX", "10 km", ["1310"], "Duplex LC", "SMF")
        elif "SX" in u:  e = E(pn, ff, "1G", "1000BASE-SX", "550 m (OM3)", ["850"], "Duplex LC", "MMF")
        elif u.endswith("-T") or "1GE-T" in u: e = E(pn, ff, "1G", "1000BASE-T", "100 m (Cat5e)", [], "RJ45", "Kupfer")
        elif "FE" in u: e = E(pn, ff, "1G", "1000/100 dual", "", ["[VERIFY]"], "[VERIFY]", "[VERIFY]", flags=["type [VERIFY] per-SKU"])
    elif re.search(r'1FE|FE20KT|FXSM', u):
        ff = "SFP"
        if "FE20KT" in u: e = E(pn, ff, "100M", "100BASE-BX", "20 km", bidi(u), "Simplex LC", "SMF", bidi=True, note="single-fiber BiDi")
        elif "LX40K" in u or "LH" in u: e = E(pn, ff, "100M", "100BASE-LX", "40 km", ["1310"], "Duplex LC", "SMF")
        elif "LX" in u: e = E(pn, ff, "100M", "100BASE-LX", "10 km", ["1310"], "Duplex LC", "SMF")
        elif "FX" in u: e = E(pn, ff, "100M", "100BASE-FX", "2 km", ["1310"], "Duplex LC", "MMF")
    elif "2X100G" in u:
        r = "2 km" if "CWDM4" in u else "10 km"; wl = CWDM4 if "CWDM4" in u else LANWDM
        e = E(pn, "QSFP28-DD", "200G", "2x 100G " + ("CWDM4" if "CWDM4" in u else "LR4"), r, wl, "Duplex LC", "SMF", 8, note="2x100G aggregate")
    if e is None:
        FO[pn] = {"reason_code": "un-groundable-after-ladder", "note": "type not resolvable from PN/MSA — per-SKU datasheet needed"}
        continue
    G[pn] = e; added += 1

(R / "juniper_grounded_facts.json").write_text(json.dumps(G, ensure_ascii=False, indent=1), encoding="utf-8")
(R / "juniper_aliases.json").write_text(json.dumps(AL, ensure_ascii=False, indent=1), encoding="utf-8")
(R / "juniper_flagged_out.json").write_text(json.dumps(FO, ensure_ascii=False, indent=1), encoding="utf-8")
vfy = [pn for pn, e in G.items() if e.get("connector") == "[VERIFY]" or e.get("reach") == "[VERIFY]" or any("[VERIFY]" in str(f) for f in e.get("flags", []))]
print(f"grounded this pass: {added} | master grounded: {len(G)} | aliases: {len(AL)} | flagged-out: {len(FO)}")
print("grounded by speed:", dict(sorted(Counter(e["speed"] for e in G.values()).items())))
print(f"[VERIFY] (λ/connector to confirm per-SKU): {len(vfy)}")
print("  ", vfy)
