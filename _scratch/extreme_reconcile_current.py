# -*- coding: utf-8 -*-
"""Extreme L8 finding B — reconcile the FULL current universe (the cached Optics Solution Guide
undercounted: missing a 400G QSFP-DD tier + 100G SFP-DD/PSM4-10km/ER4-QSFP + temp variants). Parse the
CURRENT datasheet (extreme-optical-transceivers-cables-current.pdf) by TEXT LINE — its merged-cell
tables defeat extract_tables, but each product row is one text line: '{STANDARD} {desc…} {PN}'
(standards carry "BASE"; the product PN is the trailing token without "BASE"). Diff vs the verified 86
in extreme_facts.json; GROUND only the genuinely-new parts (from the line's standard/desc + lane-aware
λ) and MERGE them in. Existing 86 (operator-verified round-1 + fix A) are untouched. $0, flag-don't-fabricate.
"""
import json, re, sys
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scratch"))
import extreme_facts as EF
PDF = ROOT / "datasheets" / "cache" / "extreme-optical-transceivers-cables-current.pdf"
FACTS = ROOT / "output" / "stage3" / "extreme_facts.json"
FLAGGED = ROOT / "output" / "stage3" / "extreme_flagged_out.json"

SET_LANWDM_100G = "1295,56 / 1300,05 / 1304,58 / 1309,14 nm (LAN-WDM, 4 Lanes)"
SET_CWDM4 = "1271 / 1291 / 1311 / 1331 nm (CWDM4, 4 Lanes)"
SET_LANWDM_400G = "1271 / 1291 / 1311 / 1331 nm (CWDM4, 4 Lanes)"   # 400G-FR4/LR4 use the CWDM4 grid
SET_SWDM4 = "850 / 880 / 910 / 940 nm (SWDM4, 4 Lanes)"

PN_RE = re.compile(r"\b(\d{2,3}G-[A-Z0-9.]+(?:-[A-Z0-9.]+)+)\b")
STD_RE = re.compile(r"\b(\d{2,3}G(?:BASE|Base)\s*-?\s*[A-Z0-9.\-]+)")
FLAG_OUT_NEW = {}     # spec-uncertain new parts -> flagged (reason-coded)


def norm(p):
    return p.upper().replace("SFP-DD", "SFPDD").replace("-", "").replace(" ", "")


def ff_from(line, pn):
    u = (line + " " + pn).upper()
    if "QSFPDD" in u or "QSFP-DD" in u or "QSFPDD" in pn.upper():
        return "QSFP-DD"
    if "SFPDD" in u:
        return "SFP-DD"
    if "OSFP" in u:
        return "OSFP"
    if "QSFP28" in u:
        return "QSFP28"
    if "QSFP56" in u:
        return "QSFP56"
    if "QSFP" in u:
        return "QSFP+"
    if "SFP28" in u or pn.startswith("25G"):
        return "SFP28"
    return "SFP+"


def wl_for(standard, typ, sp, media):
    blob = (standard + " " + typ).upper()
    if re.search(r"\bLR4|\bER4|\bERLT|\bFR4|\bCWDM4|\bSWDM4|LAN-?WDM", blob):
        if "SWDM4" in blob:
            return SET_SWDM4
        if "CWDM4" in blob:
            return SET_CWDM4
        return SET_LANWDM_100G if sp == "100G" else SET_CWDM4
    if media == "MMF":
        return "850 nm"
    if re.search(r"\bER\b|\bZR\b", blob):
        return "1550 nm"
    if re.search(r"\bLR\b|\bDR\b|\bFR\b|PSM4", blob):
        return "1310 nm"
    return None


def main():
    exist = json.loads(FACTS.read_text(encoding="utf-8"))
    have = set(norm(p) for p in exist)
    for f in exist.values():
        have |= set(norm(a) for a in (f.get("alt_pns") or []))
    have |= set(norm(p) for p in json.loads(FLAGGED.read_text(encoding="utf-8")))

    pdf = pdfplumber.open(PDF)
    new = {}
    for pi, pg in enumerate(pdf.pages):
        for raw in (pg.extract_text() or "").split("\n"):
            line = re.sub(r"\s+", " ", raw).strip()
            pns = [p for p in PN_RE.findall(line) if "BASE" not in p.upper()]
            if not pns:
                continue
            pn = pns[-1].strip().rstrip(".")
            # join a trailing length-note PDF-split onto the PN ("100G-FR-SFPDD 2KM" stays PN=100G-FR-SFPDD)
            if norm(pn) in have or pn in new:
                continue
            sm = STD_RE.search(line)
            standard = re.sub(r"\s*-\s*", "-", sm.group(1)).replace("Base", "BASE") if sm else ""
            sp = (re.match(r"(\d{2,3}G)", pn) or [None, ""])[1]
            cable = bool(re.search(r"\bAOC\b|\bDAC\b|DACP|DACA", line + " " + pn, re.I))
            media = EF.parse_media(line) or ("MMF" if re.search(r"SR|MMF|Multimode|OM[1-5]", line) else
                                             ("SMF" if re.search(r"LR|ER|FR|DR|ZR|Singlemode|SMF", line) else None))
            typ = pn.split("-")[1] if len(pn.split("-")) > 1 else ""
            conn = EF.parse_connector(line) or ("MPO" if "MPO" in line.upper() else ("LC" if " LC" in line.upper() else None))
            reach = EF.parse_reach(line)
            # 4WDM λ-plan still unprovable (the round-1 flag-out reason); keep flagged
            if re.search(r"4WDM", pn, re.I):
                FLAG_OUT_NEW[pn] = "un-groundable-after-ladder"
                continue
            entry = {"pn": pn, "speed": sp, "standard": standard, "type": typ, "ff": ff_from(line, pn),
                     "connector": conn, "media": media, "reach": reach or "", "page": pi + 1,
                     "cable": cable, "alt_pns": [], "_source": "current Extreme datasheet (Workflow-B)"}
            if not cable:
                entry["wavelength"] = wl_for(standard, typ, sp, media)
            new[pn] = entry
    pdf.close()
    print("genuinely-NEW parts vs the verified 86: %d" % len(new))
    for pn, e in sorted(new.items()):
        tag = "CABLE" if e["cable"] else "%s/%s/%s" % (e["ff"], e.get("wavelength"), e["reach"])
        print("  %-26s | %-16s | %s" % (pn, e["standard"], tag))
    if FLAG_OUT_NEW:
        print("flag-out (4WDM λ-plan):", list(FLAG_OUT_NEW))
    (ROOT / "output" / "stage3" / "extreme_new_facts.json").write_text(
        json.dumps({"new": new, "flag_out": FLAG_OUT_NEW}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
