# -*- coding: utf-8 -*-
"""Extreme L8 finding B — MERGE the genuinely-new parts from the CURRENT datasheet into the verified 86
(extreme_facts.json). Each is grounded EXPLICITLY from the current-datasheet product row (standard +
connector + reach + media; λ lane-aware from the IEEE standard) — more reliable than the merged-cell
line-parse. The verified 86 (operator round-1 + fix A) are untouched. flag-don't-fabricate: 400G-LR4P
(4×100G-LR breakout — λ/standard vs the parallel lanes unprovable without the EXOS DB) is flagged out.
Run: python _scratch/extreme_supplement.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / "output" / "stage3" / "extreme_facts.json"
FLAGGED = ROOT / "output" / "stage3" / "extreme_flagged_out.json"
SET_CWDM4 = "1271 / 1291 / 1311 / 1331 nm (CWDM4, 4 Lanes)"
SET_LANWDM = "1295,56 / 1300,05 / 1304,58 / 1309,14 nm (LAN-WDM, 4 Lanes)"


def opt(pn, sp, ff, typ, std, conn, media, wl, reach, om=None):
    return {"pn": pn, "speed": sp, "ff": ff, "type": typ, "standard": std, "connector": conn,
            "media": media, "wavelength": wl, "reach": reach, "om": om, "length": None, "active": False,
            "breakout": False, "cable": False, "alt_pns": [], "page": 0,
            "row": "current Extreme datasheet (Workflow-B finding B)"}


def cab(pn, sp, ff, typ, length, om=None):
    return {"pn": pn, "speed": sp, "ff": ff, "type": typ, "standard": "", "connector": None,
            "media": ("Kupfer" if typ == "DAC" else None), "wavelength": None, "reach": "", "om": om,
            "length": length, "active": (typ == "AOC"), "breakout": False, "cable": True, "alt_pns": [],
            "page": 0, "row": "current Extreme datasheet (Workflow-B finding B)"}


# 400G QSFP-DD optics (p3). DR4/SR8 = parallel single-λ; FR4/LR4 = WDM SET; DR4X = DR4 breakout (single λ).
NEW = {
    "400G-DR4-QSFPDD500M": opt("400G-DR4-QSFPDD500M", "400G", "QSFP-DD", "DR4", "400GBASE-DR4", "MPO-12", "SMF", "1310 nm", "500 m"),
    "400G-FR4-QSFPDD2KM": opt("400G-FR4-QSFPDD2KM", "400G", "QSFP-DD", "FR4", "400GBASE-FR4", "LC", "SMF", SET_CWDM4, "2 km"),
    "400G-LR4-QSFPDD10KM": opt("400G-LR4-QSFPDD10KM", "400G", "QSFP-DD", "LR4", "400GBASE-LR4", "LC", "SMF", SET_CWDM4, "10 km"),
    "400G-SR8-QSFPDD100M": opt("400G-SR8-QSFPDD100M", "400G", "QSFP-DD", "SR8", "400GBASE-SR8", "MPO-16", "MMF", "850 nm", "100 m", om="OM4"),
    "400G-DR4X-QSFPDD2KM": opt("400G-DR4X-QSFPDD2KM", "400G", "QSFP-DD", "DR4X", "400GBASE-DR4", "MPO-12", "SMF", "1310 nm", "2 km"),
    # 100G additions
    "100G-DR-SFPDD500M": opt("100G-DR-SFPDD500M", "100G", "SFP-DD", "DR", "100GBASE-DR", "LC", "SMF", "1310 nm", "500 m"),
    "100G-FR-SFPDD": opt("100G-FR-SFPDD", "100G", "SFP-DD", "FR", "100GBASE-FR", "LC", "SMF", "1310 nm", "2 km"),
    "100G-LR-SFPDD": opt("100G-LR-SFPDD", "100G", "SFP-DD", "LR", "100GBASE-LR", "LC", "SMF", "1310 nm", "10 km"),
    "100G-PSM4-QSFP10KM": opt("100G-PSM4-QSFP10KM", "100G", "QSFP28", "PSM4", "100GBASE-PSM4", "MPO-12", "SMF", "1310 nm", "10 km"),
    "100G-ER4-QSFP40KM": opt("100G-ER4-QSFP40KM", "100G", "QSFP28", "ER4", "100GBASE-ER4", "LC", "SMF", SET_LANWDM, "40 km"),
    # 10G variants (commercial + industrial-temp + length)
    "10G-ER-SFP40KM": opt("10G-ER-SFP40KM", "10G", "SFP+", "ER", "10GBASE-ER", "LC", "SMF", "1550 nm", "40 km"),
    "10G-LR-SFP10KM-IT": opt("10G-LR-SFP10KM-IT", "10G", "SFP+", "LR", "10GBASE-LR", "LC", "SMF", "1310 nm", "10 km"),
    "10G-SR-SFP100M": opt("10G-SR-SFP100M", "10G", "SFP+", "SR", "10GBASE-SR", "LC", "MMF", "850 nm", "100 m", om="OM3"),
    "10G-SR-SFP300M": opt("10G-SR-SFP300M", "10G", "SFP+", "SR", "10GBASE-SR", "LC", "MMF", "850 nm", "300 m", om="OM3"),
    "10G-ZR-SFP80KM": opt("10G-ZR-SFP80KM", "10G", "SFP+", "ZR", "10GBASE-ZR", "LC", "SMF", "1550 nm", "80 km"),
}
# 400G QSFP-DD cables (p3): AOC 5/10/20M, passive DAC 1/2/2.5/3M.
for L in ("5", "10", "20"):
    NEW["400G-AOC-QSFPDD%sM" % L] = cab("400G-AOC-QSFPDD%sM" % L, "400G", "QSFP-DD", "AOC", L)
for L in ("1", "2", "2.5", "3"):
    pn = "400G-DACP-QSFPDD%sM" % L.replace(".", "")  # 2.5 -> 25? keep readable: use the datasheet form
    pn = "400G-DACP-QSFPDD%sM" % L
    NEW[pn] = cab(pn, "400G", "QSFP-DD", "DAC", L)

FLAG_OUT = {"400G-LR4P-QSFPDD10KM": "un-groundable-after-ladder"}  # 4×100G-LR breakout: parallel λ/standard unprovable


def main():
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    flagged = json.loads(FLAGGED.read_text(encoding="utf-8"))
    added = 0
    for pn, e in NEW.items():
        if pn not in facts:
            facts[pn] = e; added += 1
    for pn, rc in FLAG_OUT.items():
        flagged[pn] = {"reason_code": rc, "note": "current-datasheet 400G breakout; λ/standard unprovable"}
    FACTS.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    FLAGGED.write_text(json.dumps(flagged, ensure_ascii=False, indent=1), encoding="utf-8")
    opt_n = sum(1 for e in NEW.values() if not e["cable"])
    print("merged %d new parts (%d optics + %d cables); flagged-out +%d (LR4P)" % (added, opt_n, len(NEW) - opt_n, len(FLAG_OUT)))
    print("extreme_facts.json now: %d" % len(facts))


if __name__ == "__main__":
    main()
