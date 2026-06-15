# -*- coding: utf-8 -*-
"""Ubiquiti (UniFi) Ethernet transceivers + DAC/AOC cables — grounded from the LOCKED denominator: the
techspecs.ui.com "SFP & Fiber (29)" roster (operator screen-cap, cached) cross-checked with per-PN
techspecs pages + official datasheets. Operator-signed-off enumeration: 20 IN (13 optic + 7 DAC/AOC
families) + 9 OUT, plus the GPON/EPON UFiber-OLT PON line OUT. Every spec web-verified (1000-rule).

Dedup: legacy UFiber UF-* and current UACC-* are the same physical optic across naming eras -> ONE SKU
(current UACC- code) with the UF- woven as an alternate order code (extra_log, the Lenovo pattern).
EXCEPTIONS: UF-RJ45-10G is SUPERSEDED-not-aliased by UACC-CM-RJ45-MG (different spec: MG adds 2.5/5G) ->
flagged in prose, NOT an alt-code. UF-SM-1G (1G SM duplex) has NO current roster SKU -> legacy-flagged,
NOT emitted. Writes output/stage3/ubiquiti_facts.json + ubiquiti_flags.txt.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "stage3" / "ubiquiti_facts.json"
FLAGS = ROOT / "output" / "stage3" / "ubiquiti_flags.txt"

TS = "https://techspecs.ui.com/unifi/accessories"          # per-PN spec source base (official)
UF_DS = "https://dl.ubnt.com/datasheets/fiber/U_Fiber_Modules_FiberCable_DS.pdf"   # legacy UF- alt-code source
_LANWDM = "1295,56 / 1300,05 / 1304,58 / 1309,14 nm (LAN-WDM, 4 Lanes)"            # 100GBASE-LR4

# OPTIC modules — (pn, type, standard, media, wavelength, reach, connector, faseranzahl, speed, ff, alt_uf, note)
# alt_uf = legacy UFiber alternate order code (dedup -> woven + logged), or None.
OPTICS = [
    # 1G SFP
    ("UACC-OM-MM-1G-D", "SX", "1000BASE-SX", "MMF", "850 nm", "550 m", "LC", "2", "1G", "SFP", "UF-MM-1G", None),
    ("UACC-OM-SM-1G-S", "BX", "1000BASE-BX (BiDi)", "SMF", "1310 nm (Tx) / 1550 nm (Rx)", "3 km", "LC", "1", "1G", "SFP", "UF-SM-1G-S", None),
    ("UACC-CM-RJ45",    "T",  "1000BASE-T", "Kupfer", "", "100 m", "RJ45", None, "1G", "SFP", "UF-RJ45-1G", None),
    # 10G SFP+
    ("UACC-OM-MM-10G-D", "SR", "10GBASE-SR", "MMF", "850 nm", "300 m", "LC", "2", "10G", "SFP+", "UF-MM-10G", None),
    ("UACC-OM-SM-10G-D", "LR", "10GBASE-LR", "SMF", "1310 nm", "10 km", "LC", "2", "10G", "SFP+", "UF-SM-10G", None),
    ("UACC-OM-SM-10G-S", "BX", "10GBASE-BX (BiDi)", "SMF", "1270 nm (Tx) / 1330 nm (Rx)", "10 km", "LC", "1", "10G", "SFP+", "UF-SM-10G-S", None),
    # multi-gig copper SFP+ (NBASE-T). UF-RJ45-10G is SUPERSEDED (different spec) -> NOT an alt code.
    ("UACC-CM-RJ45-MG", "T", "NBASE-T (10GBASE-T / 5GBASE-T / 2.5GBASE-T / 1000BASE-T)", "Kupfer", "", "100 m", "RJ45", None, "10G", "SFP+", None,
     "Mehrraten-Kupfermodul (1/2,5/5/10 Gbit/s); löst das ältere UFiber UF-RJ45-10G (1/10 Gbit/s) ab, ist aber kein identischer Ersatz"),
]
# 10G CWDM SFP+ — 12 channels (verified 1270-1590), SMF 20 km LC duplex DOM. Each channel a distinct PN.
CWDM_WL = ["1270", "1290", "1310", "1330", "1450", "1470", "1490", "1510", "1530", "1550", "1570", "1590"]
for _wl in CWDM_WL:
    OPTICS.append(("UACC-OM-SFP10-%s" % _wl, "CWDM", "10G CWDM (SFP+)", "SMF", "%s nm (CWDM)" % _wl,
                   "20 km", "LC", "2", "10G", "SFP+", None, None))
OPTICS += [
    # 25G SFP28
    ("UACC-OM-SFP28-SR", "SR", "25GBASE-SR", "MMF", "850 nm", "100 m", "LC", "2", "25G", "SFP28", None, None),
    ("UACC-OM-SFP28-LR", "LR", "25GBASE-LR", "SMF", "1310 nm", "10 km", "LC", "2", "25G", "SFP28", None, None),
    # 100G QSFP28 — SR4 / LR4 / PSM4 (PSM4 grounded independently: parallel SM, 8 fibres, MPO-12 APC, 1310 nm)
    ("UACC-OM-QSFP28-SR4",  "SR4",  "100GBASE-SR4",  "MMF", "850 nm", "100 m", "MPO-12", "8", "100G", "QSFP28", None, None),
    ("UACC-OM-QSFP28-LR4",  "LR4",  "100GBASE-LR4",  "SMF", _LANWDM, "10 km", "LC", "2", "100G", "QSFP28", None, None),
    ("UACC-OM-QSFP28-PSM4", "PSM4", "100GBASE-PSM4", "SMF", "1310 nm (PSM4, 4 Lanes)", "2 km", "MPO-12", "8", "100G", "QSFP28", None,
     "Parallel-Singlemode (PSM4): 8 Fasern über MPO-12 (APC); bis 2 km über OS2 bzw. 500 m über OS1 — kein Klon von SR4/LR4"),
]

# CABLES — (family_pn, ctype, speed, ff, [lengths_m], leg) ; ctype per LENGTH may switch (Uplink hybrid).
# DAC = passive copper (DAC Kabel); AOC = active optical (AOC Kabel).
CABLES = [
    ("UACC-DAC-SFP10",     "DAC", "10G",  "SFP+",   ["0.5", "1", "3"]),
    ("UACC-DAC-SFP28",     "DAC", "25G",  "SFP28",  ["0.5", "1", "3"]),
    ("UACC-DAC-QSFP28",    "DAC", "100G", "QSFP28", ["0.5", "1", "3"]),
    ("UACC-AOC-SFP10",     "AOC", "10G",  "SFP+",   ["5", "10", "20", "30"]),
    ("UACC-AOC-SFP28",     "AOC", "25G",  "SFP28",  ["5", "10", "20", "30"]),
    ("UACC-AOC-QSFP28",    "AOC", "100G", "QSFP28", ["5", "10", "20", "30"]),
]
# Uplink-SFP28 is HYBRID by length: 0.15/0.3 m = passive copper DAC; 3/30 m = active optical AOC.
UPLINK = ("UACC-Uplink-SFP28", "25G", "SFP28", [("0.15", "DAC"), ("0.3", "DAC"), ("3", "AOC"), ("30", "AOC")])

OUT_NOTE = ("OUT-of-scope, flagged (in the SFP&Fiber roster but not transceiver-class): UACC-OFC-S2-LULU, "
            "UACC-OFC-M2-LULU, UACC-OFC-SA-MPMP, UACC-OFC-MA-MPMP, FC-SM (fibre patch cords — no transceiver "
            "form factor); UACC-CWDM-4, UACC-CWDM-8 (CWDM mux/demux — passive infrastructure); UACC-SFP-Wizard "
            "(SFP programmer/diagnostic tool); F-POE-G2 (Optical Data Transport / PoE-over-fibre media converter).")
PON_NOTE = ("OUT-of-scope, flagged (separate product line): Ubiquiti UFiber GPON/EPON OLT optics "
            "(UF-GP-B+, UF-GP-C+, UF-INSTANT, UF-NANO, UF-LOCO, UF-OLT modules) — carrier-PON, out of scope "
            "like SONET/Fibre Channel. The RJ45 & Copper (17) catalog (patch/bulk Ethernet, couplers, USB "
            "adapters, media converter) is also entirely OUT and ignored.")
LEGACY_NOTE = ("Dedup (UFiber<->UACC naming eras): the current UACC- code is the SKU; the legacy UF- code is "
               "woven as an alternate order number (logged). UF-RJ45-10G is SUPERSEDED-not-aliased by "
               "UACC-CM-RJ45-MG (different spec) -> flagged, not an alt code. UF-SM-1G (1G SM duplex) has NO "
               "current roster SKU -> legacy/discontinued, FLAGGED, NOT emitted.")


def main():
    facts = {}
    for pn, typ, std, media, wl, reach, conn, fz, sp, ff, alt_uf, note in OPTICS:
        facts[pn] = {
            "pn": pn, "speed": sp, "ff": ff, "type": typ, "standard": std, "connector": conn,
            "media": media, "wavelength": (wl or None), "reach": reach, "faseranzahl": fz,
            "cable": False, "dual_rate": typ == "T" and "MG" in pn,
            "dual_rate_pair": ("1/2,5/5/10G" if (typ == "T" and "MG" in pn) else None),
            "alt_code": alt_uf, "alt_src": (UF_DS if alt_uf else None), "spec_note": note,
            "lifecycle": "current", "alt_pns": ([alt_uf] if alt_uf else []),
            "row": "%s/%s" % (TS, pn.lower()),
        }
    # straight DAC/AOC cable families
    for fam, ct, sp, ff, lengths in CABLES:
        for ln in lengths:
            pn = "%s-%sM" % (fam, ln)
            k3 = "AOC Kabel" if ct == "AOC" else "DAC Kabel"
            facts[pn] = {
                "pn": pn, "speed": sp, "ff": ff, "type": ("AOC" if ct == "AOC" else "DAC"),
                "standard": "", "connector": None, "media": ("Kupfer" if ct == "DAC" else None),
                "wavelength": None, "reach": "", "length": ln, "cable": True, "k3": k3,
                "active": ct == "AOC", "breakout": False, "ends_raw": "%s auf %s" % (ff, ff),
                "lifecycle": "current", "alt_pns": [], "row": "%s/%s" % (TS, fam.lower()),
            }
    # Uplink-SFP28 — hybrid copper(DAC)/fibre(AOC) by length
    ufam, usp, uff, ulen = UPLINK
    for ln, ct in ulen:
        pn = "%s-%sM" % (ufam, ln)
        k3 = "AOC Kabel" if ct == "AOC" else "DAC Kabel"
        facts[pn] = {
            "pn": pn, "speed": usp, "ff": uff, "type": ("AOC" if ct == "AOC" else "DAC"),
            "standard": "", "connector": None, "media": ("Kupfer" if ct == "DAC" else None),
            "wavelength": None, "reach": "", "length": ln, "cable": True, "k3": k3,
            "active": ct == "AOC", "breakout": False, "ends_raw": "%s auf %s" % (uff, uff),
            "lifecycle": "current", "alt_pns": [],
            "spec_note": ("Uplink-Kabel mit Auto-Negotiation; in dieser Länge als %s ausgeführt"
                          % ("aktives optisches Kabel (Glasfaser)" if ct == "AOC" else "passives Twinax-Kupferkabel")),
            "row": "%s/%s" % (TS, ufam.lower()),
        }
    FLAGS.write_text("\n".join([OUT_NOTE, PON_NOTE, LEGACY_NOTE]), encoding="utf-8")
    OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    import collections
    opt = [p for p, f in facts.items() if not f.get("cable")]
    cab = [p for p in facts if p not in opt]
    print("UBIQUITI facts: %d (optics %d, cables %d)" % (len(facts), len(opt), len(cab)))
    print("optics by speed:", dict(collections.Counter(facts[p]["speed"] for p in opt)))
    print("cables:", sorted(cab))


if __name__ == "__main__":
    main()
