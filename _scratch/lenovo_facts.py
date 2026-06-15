# -*- coding: utf-8 -*-
"""Lenovo (ThinkSystem; absorbs IBM System Networking / BNT-ex-BLADE) Ethernet optics — grounded from
Lenovo Press CURRENT product guides (Workflow-B, two independent current sources):
  - lp1652 ThinkSystem Broadcom 57504 (last updated 2025-12-12): 10G/25G transceivers + SFP+/SFP28
    DAC/AOC + 100G-breakout cables.
  - lp1417 ThinkSystem Broadcom 57508 (last updated 2026-05-07): 100G QSFP28-SR4 + 100G/200G DAC/AOC.
Every row below is a PRODUCT-ROW from those guides' "Supported transceivers/cables" tables (phantom-guard:
NOT lifted from a compatibility/interop note). Lenovo optics are OEM-rebadged -> specs grounded from the
IEEE standard the Lenovo description names (SR=850/300m, LR=1310/10km, SR4=850/100m-MPO, -T=copper),
lane-aware (§7.4). The Lenovo FEATURE CODE is woven into the Beschreibung as an alt order code (like the
Extreme AA-/MGBIC- handling). Scope: Ethernet transceivers + DAC/AOC/breakout only. OUT (documented):
LC-LC OM3/OM4 patch cords (generic), passive MTP-4xLC fibre breakout (no transceiver form factor — the
Dell precedent), Mellanox HDR InfiniBand AOC (non-Ethernet). No current 40G / 100G-LR4 optic in either
current guide -> not in the current Lenovo Ethernet catalogue (documented scope boundary, not a silent gap).
Writes output/stage3/lenovo_facts.json + lenovo_flags.txt.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "stage3" / "lenovo_facts.json"
FLAGS = ROOT / "output" / "stage3" / "lenovo_flags.txt"
flags = []

# (PN, feature_code, kind, desc) — kind: SR/LR/SR4/T(=copper)/SR25/SR25DR for optics; cable kinds below.
TRANSCEIVERS = [
    # 10G SFP+
    ("4TC7B13092", "CFPW", "T",  "Lenovo 10GBASE-T SFP+ (Accelink RTXL185-510)"),
    ("4TC7B12410", "CEHQ", "LR", "Lenovo 10GBASE-LR SFP+ (Finisar FTLX1475D3BCL)"),
    ("00FE331",    "B0RJ", "LR", "Lenovo 10GBASE-LR SFP+ Transceiver"),
    ("49Y4216",    "0069", "SR", "Lenovo 10Gb SFP+ SR Optical Transceiver (Brocade)"),
    ("49Y8578",    "5721", "SR", "Lenovo 10 GbE SW SFP+ Transceiver"),
    ("49Y4218",    "0064", "SR", "Lenovo 10Gb SFP+ SR Optical Transceiver (QLogic)"),
    ("90Y9412",    "A1PM", "LR", "Lenovo 10GBASE-LR SFP+ Transceiver"),
    ("46C3447",    "5053", "SR", "Lenovo 10GBASE-SR SFP+ Transceiver"),
    ("68Y6923",    "5722", "SR", "Lenovo 10Gb SFP+ SR Transceiver (Juniper)"),
    ("69Y0389",    "6416", "SR", "Lenovo 10GbE SR SFP+ Transceiver, 300m MMF"),
    ("4TC7A78615", "BNDR", "SR", "ThinkSystem Accelink 10G SR SFP+ Ethernet Transceiver"),
    # 25G SFP28 (dual-rate parts run 10G/25G)
    ("4M27A67041", "BFH2", "SR25",   "Lenovo 25Gb SR SFP28 Ethernet Transceiver"),
    ("4TC7A69045", "BF10", "SR25DR", "Lenovo Dual Rate 10G/25G SR SFP28 (85C) Transceiver"),
    ("7G17A03537", "AV1B", "SR25DR", "Lenovo Dual Rate 10G/25G SR SFP28 Transceiver"),
    ("4TC7A88638", "BYBJ", "SR25DR", "ThinkSystem Finisar Dual Rate 10G/25G SR SFP28 Transceiver"),
    # 100G QSFP28 (Lenovo's only current 100G optic is SR4)
    ("4M27A67042", "BFH1", "SR4", "Lenovo 100Gb SR4 QSFP28 Ethernet Transceiver"),
    ("7G17A03539", "AV1D", "SR4", "Lenovo 100GBASE-SR4 QSFP28 Transceiver"),
    ("4TC7A86257", "BVA4", "SR4", "Lenovo 100GBASE-SR4 QSFP28 Transceiver"),
]

# (PN, FC, ctype, speed, ff, length_m, breakout)  ctype: DAC-P/DAC-A/AOC
CABLES = [
    # SFP+ 10G AOC
    ("00YL634","ATYX","AOC","10G","SFP+","1",0),("00YL637","ATYY","AOC","10G","SFP+","3",0),
    ("00YL640","ATYZ","AOC","10G","SFP+","5",0),("00YL643","ATZ0","AOC","10G","SFP+","7",0),
    ("00YL646","ATZ1","AOC","10G","SFP+","15",0),("00YL649","ATZ2","AOC","10G","SFP+","20",0),
    # SFP+ 10G passive DAC
    ("00D6288","A3RG","DAC-P","10G","SFP+","0.5",0),("90Y9427","A1PH","DAC-P","10G","SFP+","1",0),
    ("00AY764","A51N","DAC-P","10G","SFP+","1.5",0),("00AY765","A51P","DAC-P","10G","SFP+","2",0),
    ("90Y9430","A1PJ","DAC-P","10G","SFP+","3",0),("90Y9433","A1PK","DAC-P","10G","SFP+","5",0),
    ("00D6151","A3RH","DAC-P","10G","SFP+","7",0),
    # SFP+ 10G active DAC
    ("00VX111","AT2R","DAC-A","10G","SFP+","1",0),("00VX114","AT2S","DAC-A","10G","SFP+","3",0),
    ("00VX117","AT2T","DAC-A","10G","SFP+","5",0),
    # SFP28 25G AOC (two PN-series = distinct order codes)
    ("4X97A94008","AV1F","AOC","25G","SFP28","3",0),("4X97A94011","AV1G","AOC","25G","SFP28","5",0),
    ("4X97A94012","AV1H","AOC","25G","SFP28","10",0),("4X97A94013","AV1J","AOC","25G","SFP28","15",0),
    ("4X97A94702","AV1K","AOC","25G","SFP28","20",0),("7Z57A03541","C10R","AOC","25G","SFP28","3",0),
    ("7Z57A03542","C10S","AOC","25G","SFP28","5",0),("7Z57A03543","C10N","AOC","25G","SFP28","10",0),
    ("7Z57A03544","C10T","AOC","25G","SFP28","15",0),("7Z57A03545","C1MB","AOC","25G","SFP28","20",0),
    # SFP28 25G passive DAC
    ("7Z57A03557","AV1W","DAC-P","25G","SFP28","1",0),("7Z57A03558","AV1X","DAC-P","25G","SFP28","3",0),
    ("7Z57A03559","AV1Y","DAC-P","25G","SFP28","5",0),
    # 100G QSFP28 AOC (two series)
    ("4X97A94703","B2UZ","AOC","100G","QSFP28","1",0),("4X97A94014","AV1L","AOC","100G","QSFP28","3",0),
    ("4X97A94015","AV1M","AOC","100G","QSFP28","5",0),("4X97A94016","AV1N","AOC","100G","QSFP28","10",0),
    ("4X97A94704","AV1P","AOC","100G","QSFP28","15",0),("4X97A94705","AV1Q","AOC","100G","QSFP28","20",0),
    ("4Z57A10844","C1MC","AOC","100G","QSFP28","1",0),("7Z57A03546","C10P","AOC","100G","QSFP28","3",0),
    ("7Z57A03547","C10Q","AOC","100G","QSFP28","5",0),("7Z57A03548","C10M","AOC","100G","QSFP28","10",0),
    ("7Z57A03549","C1MD","AOC","100G","QSFP28","15",0),("7Z57A03550","C1ME","AOC","100G","QSFP28","20",0),
    # 100G QSFP28 passive DAC
    ("7Z57A03561","AV1Z","DAC-P","100G","QSFP28","1",0),("7Z57A03562","AV20","DAC-P","100G","QSFP28","3",0),
    ("7Z57A03563","AV21","DAC-P","100G","QSFP28","5",0),
    # 200G QSFP56 passive DAC (Ethernet)
    ("4X97A11113","BF6W","DAC-P","200G","QSFP56","1",0),("4X97A12613","BF92","DAC-P","200G","QSFP56","3",0),
    # 100G->4x25G breakout AOC
    ("7Z57A03551","AV1R","AOC","100G","QSFP28","3",4),("7Z57A03552","AV1S","AOC","100G","QSFP28","5",4),
    ("7Z57A03553","AV1T","AOC","100G","QSFP28","10",4),("7Z57A03554","AV1U","AOC","100G","QSFP28","15",4),
    ("7Z57A03555","AV1V","AOC","100G","QSFP28","20",4),
    # 100G->4x25G breakout DAC
    ("7Z57A03564","AV22","DAC-P","100G","QSFP28","1",4),("4Z57A85043","BS32","DAC-P","100G","QSFP28","1.5",4),
    ("4Z57A85044","BS33","DAC-P","100G","QSFP28","2",4),("7Z57A03565","AV23","DAC-P","100G","QSFP28","3",4),
    ("7Z57A03566","AV24","DAC-P","100G","QSFP28","5",4),
]
# Documented OUT-of-scope (NOT captured): generic LC-LC patch cords, passive MTP-4xLC fibre breakout
# (no transceiver form factor — Dell precedent), Mellanox HDR InfiniBand AOC (non-Ethernet).
OUT_NOTE = ("OUT-of-scope (documented): LC-LC OM3/OM4 patch cords (00MN*/4Z57A108*), passive MTP-4xLC "
            "fibre breakout (00FM412/413/414 — no transceiver FF), Mellanox HDR IB AOC (4Z57A1418*-2 IB).")

STD = {"SR": ("10GBASE-SR", "MMF", "850 nm", "300 m", "LC", "2"),
       "LR": ("10GBASE-LR", "SMF", "1310 nm", "10 km", "LC", "2"),
       "T":  ("10GBASE-T", "Kupfer", "", "30 m", "RJ45", None),
       "SR25": ("25GBASE-SR", "MMF", "850 nm", "100 m", "LC", "2"),
       "SR25DR": ("25GBASE-SR", "MMF", "850 nm", "100 m", "LC", "2"),
       "SR4": ("100GBASE-SR4", "MMF", "850 nm", "100 m", "MPO-12", "8")}


def main():
    facts = {}
    for pn, fc, kind, desc in TRANSCEIVERS:
        std, media, wl, reach, conn, fz = STD[kind]
        sp = "100G" if kind == "SR4" else ("25G" if kind.startswith("SR25") else "10G")
        ff = "QSFP28" if kind == "SR4" else "SFP+"
        if kind.startswith("SR25"):
            ff = "SFP28"
        typ = std.split("BASE-")[-1] if "BASE-" in std else std
        facts[pn] = {"pn": pn, "speed": sp, "ff": ff, "type": typ, "standard": std, "connector": conn,
                     "media": media, "wavelength": (wl or None), "reach": reach, "faseranzahl": fz,
                     "cable": False, "feature_code": fc, "desc": desc, "dual_rate": kind == "SR25DR",
                     "alt_pns": [fc], "page": 0, "row": "Lenovo Press lp1652/lp1417 (current)"}
    for pn, fc, ct, sp, ff, ln, brk in CABLES:
        k3 = "AOC Kabel" if ct == "AOC" else "DAC Kabel"
        active = ct in ("AOC", "DAC-A")
        leg = "SFP28" if sp == "100G" else ff   # 100G->4x25G breaks out to SFP28
        ends = ("%s auf 4x %s" % (ff, leg)) if brk else ("%s auf %s" % (ff, ff))
        facts[pn] = {"pn": pn, "speed": sp, "ff": ff, "type": ("AOC" if ct == "AOC" else "DAC"),
                     "standard": "", "connector": None, "media": ("Kupfer" if ct.startswith("DAC") else None),
                     "wavelength": None, "reach": "", "length": ln, "cable": True, "k3": k3,
                     "active": active, "breakout": bool(brk), "ends_raw": ends, "feature_code": fc,
                     "alt_pns": [fc], "page": 0, "row": "Lenovo Press lp1652/lp1417 (current)"}
    flags.append(OUT_NOTE)
    flags.append("No current 40G QSFP+ or 100G-LR4/ER4 Lenovo Ethernet optic in either current adapter "
                 "guide -> not in the current Lenovo Ethernet catalogue (scope boundary, re-checkable).")
    OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    FLAGS.write_text("\n".join(flags), encoding="utf-8")
    import collections
    opt = [p for p, f in facts.items() if not f.get("cable")]
    print("LENOVO facts: %d (optics %d, cables %d)" % (len(facts), len(opt), len(facts) - len(opt)))
    print("optics by ff:", dict(collections.Counter(facts[p]["ff"] for p in opt)))
    print("cables by speed:", dict(collections.Counter(facts[p]["speed"] for p in facts if facts[p].get("cable"))))


if __name__ == "__main__":
    main()
