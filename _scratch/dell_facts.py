# -*- coding: utf-8 -*-
"""Dell (PowerSwitch / Dell EMC Networking / Force10 legacy) optics — parse the cached spec sheet into
grounded facts. Source: datasheets/cache/dell-networking-optics-datasheet.pdf (8 pp; the official Dell
"Networking Transceivers and Cables" spec sheet, fetched from a reseller mirror after delltechnologies.com
403'd — the CONTENT is Dell's own datasheet, the source of truth). pdfplumber extract_tables() (the
technique that unblocked Extreme).

Pages 2-4 carry the FULL spec grid: Product | Model | Max.distance | IEEE Standard | MSA | Receptacle |
Fiber | Mode | Power | Wavelength | Temperature -> every grounded value. Page 8 is the flat
Part-number|Description list (the completeness denominator + the cable/accessory families). Page 5 is
DWDM/tunable (handled conservatively). Section rows ("1G optics", "40G optics", "Accessories") set the
speed group. Space-wrapped PNs are repaired (SFP-100M- FX -> SFP-100M-FX); multi-PN length families
(QSFP-40G-PSM-1M ... -5M ... -15M) are split into one SKU per length.

Out-of-scope / non-transceiver (flagged, NOT dropped silently):
  * QSA-QSFP-SFP+  -> form-factor ADAPTER, not a transceiver (= Cisco QSA) -> exclude.
  * SFP-8GFC-SW / SFP-8GFC-LW -> 8G FIBRE CHANNEL (storage, non-Ethernet) -> flag out-of-scope-pending
    (the SONET precedent: a non-Ethernet protocol family is the operator's scope call, not mine).
Writes output/stage3/dell_facts.json + dell_flags.txt.
"""
import json, re
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "datasheets" / "cache" / "dell-networking-optics-datasheet.pdf"
OUT = ROOT / "output" / "stage3" / "dell_facts.json"
FLAGS = ROOT / "output" / "stage3" / "dell_flags.txt"

SPEED_RE = re.compile(r"^\s*(1G|10G|25G|40G|50G|100G|100MB?|8G ?FC)\b.*optic", re.I)
SECTION_RE = re.compile(r"^(1G|10G|25G|40G|50G|100G)\s+optics|Accessories|DWDM", re.I)
ADAPTER = {"QSA-QSFP-SFP+"}
FC = {"SFP-8GFC-SW", "SFP-8GFC-LW"}
flags = []


def ws(s):
    return re.sub(r"\s+", " ", (s or "").replace("\n", " ")).strip()


def repair_pn(s):
    """Dell PNs never contain spaces; the PDF wraps them. Re-join: 'SFP-100M- FX' -> 'SFP-100M-FX',
    'QSFP-40G- SR4' -> 'QSFP-40G-SR4'. A cell can hold SEVERAL space-separated PNs (length family)."""
    s = ws(s)
    s = re.sub(r"-\s+", "-", s)                 # join a hyphen that wrapped
    s = re.sub(r"\s+-", "-", s)
    return s


def split_pns(cell):
    """A Model cell -> list of PNs. Length families list multiple PNs separated by space (each starts
    with a known optic/cable prefix)."""
    s = repair_pn(cell)
    parts = re.split(r"\s+(?=(?:DAC|AOC|SFP|QSFP|Q28|QSFP28|CXP|QSA)[-0-9])", s)
    return [p.strip() for p in parts if p.strip()]


# a real Dell optic/cable PN: a known prefix, a digit, a hyphen, no internal space, no stray words.
VALID_PN = re.compile(r"^(?:DAC|AOC|SFP|SFP28|QSFP|QSFP28|Q28|CXP)[-0-9A-Za-z.+]*$")
DWDM_PN = re.compile(r"SFP-10G-W\d+|-DWDM|Tunable", re.I)   # fixed-channel/tunable DWDM family (page-5 channels)


def is_cable_pn(pn):
    return pn.upper().startswith(("DAC", "AOC"))


def speed_from(blob):
    for sp in ("100G", "50G", "40G", "25G", "10G", "1G"):
        if re.search(r"\b%s\b" % sp, blob):
            return sp
    if re.search(r"100M", blob):
        return "1G"                              # 100M FX catalogued under the 1G group
    return ""


def ff_from(msa, pn):
    m = ws(msa).upper()
    for tok in ("QSFP28", "QSFP+", "QSFP-DD", "SFP28", "SFP+", "CXP", "CFP2", "CFP", "SFP"):
        if tok.replace("+", "") in m.replace("+", "") or tok in m:
            return tok
    p = pn.upper()
    if p.startswith("Q28") or "QSFP28" in p:
        return "QSFP28"
    if p.startswith("QSFP-40G") or p.startswith("QSFP+"):
        return "QSFP+"
    if p.startswith("SFP28") or "-25G" in p:
        return "SFP28"
    if p.startswith("SFP-10G") or p.startswith("SFP-8G"):
        return "SFP+"
    if p.startswith("CXP"):
        return "CXP"
    return "SFP"


def media_from(fiber, pn):
    f = ws(fiber).upper()
    if "MMF" in f or "MULTIMODE" in f:
        return "MMF"
    if "SMF" in f or "SINGLE" in f or "SINGLEMODE" in f:
        return "SMF"
    if "COPPER" in f or "CAT" in f or pn.upper().endswith("-T"):
        return "Kupfer"
    return ""


def conn_from(recept):
    r = ws(recept).upper()
    if "MPO" in r or "MTP" in r:
        return "MPO"
    if "LC" in r:
        return "LC"
    if "RJ" in r or "RJ45" in r:
        return "RJ45"
    return ws(recept)


def type_from(pn, standard):
    """Optic type token (SR/LR/ER/SR4/LR4/PSM4/CWDM4/SWDM4/T/...) from the PN tail."""
    p = pn.upper()
    m = re.search(r"(SR10|SR4|ESR4|LR4-LITE|LR4|ER4|PSM4-LR|PSM4|PSM|CWDM4|SWDM4|LM4|USR|SR-12|SR|LRM|LR|ER|ZR|FX|SX|LX|T-DWDM|T)\b", p)
    return m.group(1) if m else ""


def main():
    facts = {}
    pdf = pdfplumber.open(PDF)
    for pi in (1, 2, 3):                          # pages 2-4: the full spec grid
        for t in pdf.pages[pi].extract_tables():
            if not t or not t[0] or "Model" not in [ws(c) for c in t[0]]:
                continue
            h = [ws(c) for c in t[0]]
            ix = {name: h.index(name) for name in h}
            def col(r, *names):
                for n in names:
                    for hk in ix:
                        if hk.lower().startswith(n.lower()):
                            j = ix[hk]
                            return ws(r[j]) if j < len(r) else ""
                return ""
            for r in t[1:]:
                model = ws(r[h.index("Model")]) if "Model" in h else ""
                prod = ws(r[0])
                if not model and SECTION_RE.match(prod):
                    continue                      # section header row
                if not model:
                    continue
                reach = col(r, "Max")
                standard = col(r, "IEEE")
                msa = col(r, "MSA")
                recept = col(r, "Receptacle")
                fiber = col(r, "Fiber")
                wl = col(r, "Wavelength")
                temp = col(r, "Temp")
                grp = speed_from(prod + " " + model + " " + standard)
                for pn in split_pns(model):
                    pn = pn.strip()
                    if not pn or not VALID_PN.match(pn):
                        continue                              # PDF artifact ("Pack of 12", "Range", "...to")
                    if pn in ADAPTER:
                        flags.append("%s | adapter (QSFP->SFP), not a transceiver -> exclude" % pn); continue
                    if pn in FC:
                        flags.append("%s | 8G Fibre Channel (non-Ethernet) -> out-of-scope-pending operator" % pn); continue
                    if DWDM_PN.search(pn):
                        flags.append("%s | fixed-channel/tunable DWDM (page-5 ITU channel family) -> deferred sub-family" % pn); continue
                    cable = is_cable_pn(pn)
                    lm = re.search(r"-(\d+(?:\.\d+)?)M\b", pn)
                    typ = ("AOC" if pn.upper().startswith("AOC") else "DAC") if cable else type_from(pn, standard)
                    facts[pn] = {
                        "pn": pn, "speed": grp or speed_from(pn), "standard": standard or "", "type": typ,
                        "ff": ff_from(msa, pn), "media": ("Kupfer" if (cable and pn.upper().startswith("DAC")) else media_from(fiber, pn)),
                        "connector": conn_from(recept), "wavelength": (None if cable else (ws(wl).replace("mn", "nm") or None)),
                        "reach": reach or "", "temperature": temp or "", "length": (lm.group(1) if lm else None),
                        "active": (cable and pn.upper().startswith("AOC")), "breakout": ("4SFP" in pn.upper() or "4RJ45" in pn.upper()),
                        "cable": cable, "alt_pns": [], "page": pi + 1, "product": prod,
                    }
    # page 8: cross-check + capture anything missed (cables/accessories live here as families)
    p8 = {}
    for t in pdf.pages[7].extract_tables():
        for r in t:
            pn = repair_pn(r[0]); ds = ws(r[1]) if len(r) > 1 else ""
            if not pn or SECTION_RE.match(pn) or pn == "Part number":
                continue
            for one in split_pns(pn):
                p8[one] = ds
    missed = [pn for pn in p8 if pn not in facts and pn not in ADAPTER and pn not in FC]
    pdf.close()
    OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    FLAGS.write_text("\n".join(flags), encoding="utf-8")
    print("DELL facts: %d optics parsed from the spec grid (pages 2-4)" % len(facts))
    print("flags:", len(flags), "->", "; ".join(flags) if flags else "none")
    print("\npage-8 PNs NOT in the spec grid (cables/accessories + any gap) = %d:" % len(missed))
    for pn in missed:
        print("   %-26s | %s" % (pn, p8.get(pn, "")[:46]))


if __name__ == "__main__":
    main()
