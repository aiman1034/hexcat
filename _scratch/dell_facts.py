# -*- coding: utf-8 -*-
"""Dell (PowerSwitch / Dell EMC / Force10 legacy) optics — harvest the CURRENT official spec sheet.
Workflow-B (operator L8 lesson): the andovercg mirror was Dell's © 2017 v1.2 sheet (1G–100G only) —
a ~3x UNDERCOUNT. The current sheet (© 2026, 19 pp, fetched via WebFetch past the delltechnologies.com
403) spans 1G→800G. Source: datasheets/cache/dell-networking-optics-CURRENT.pdf.

STRUCTURE: optic spec tables pp3-9 (Model | Connector Type | Wavelength(s) | Transmission media |
Distance(max) | …); cable spec tables pp10-12 (Model[xM family] | Available Lengths | Connection |
Media); flat Model|Description denominator pp18-19. The Wavelength + Connector columns are EXPLICIT
(no derivation) — the SET is grounded verbatim.

Scope (operator policy): FIBRE CHANNEL out catalog-wide (SFP-16GFC/QSFP-64GFC); QSA adapters out;
'tunable DWDM' ZR+ = coherent (kept, λ='durchstimmbar'). Writes output/stage3/dell_facts.json + flags.
"""
import json, re
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "datasheets" / "cache" / "dell-networking-optics-CURRENT.pdf"
OUT = ROOT / "output" / "stage3" / "dell_facts.json"
FLAGS = ROOT / "output" / "stage3" / "dell_flags.txt"
flags = []


def rep(s):
    return re.sub(r"-\s+", "-", re.sub(r"\s+", " ", (s or "").replace("\n", " "))).strip()


def clean_pn(model):
    """A clean SKU PN from a Model cell that may carry spec-note parentheticals. Gen2/3/4 + low-power +
    rate-adaptive are GENUINE distinct variants -> kept as a -GenN/-LP/-RA suffix; everything else in
    parens/brackets is a note -> stripped. Dual-rate '/40G' '/80G' notes dropped; internal spaces removed."""
    s = model
    g = re.search(r"\(?\bGen\s*(\d)\)?", s, re.I)
    lp = bool(re.search(r"low\s*power", s, re.I))
    ra = bool(re.search(r"rate\s*adaptive", s, re.I))
    s = re.sub(r"[\[\]]", "", s)                       # bracket chars (cable breakout notation) -> keep content
    s = re.sub(r"\s*\(.*?\)", "", s)                   # (Gen 3), (Supports FEC …) -> drop
    s = re.sub(r"\s*-?\s*low\s*power|\s*rate\s*adaptive", "", s, flags=re.I)
    s = re.sub(r"/\s*\d+G", "", s)                     # dual-rate /40G /80G
    s = re.sub(r"\s+", "", s).rstrip("-")
    suf = ("-Gen%s" % g.group(1) if g else "") + ("-LP" if lp else "") + ("-RA" if ra else "")
    return s + suf


def is_fc(m):       return bool(re.search(r"\d+GFC", m, re.I))
def is_qsa(m):      return m.upper().startswith("QSA")


def ff_of(m):
    u = m.upper().replace("-", "")
    if "O112" in u or "OSFP" in u:        return "OSFP"
    if "Q56DD" in u or "Q56-DD" in u:     return "QSFP-DD"          # QSFP56-DD = 400G
    if "Q28DD" in u:                       return "QSFP28-DD"        # 200G dual-100G (now a locked token)
    if "S56DD" in u or "SFPDD" in u:      return "SFP-DD"           # SFP56-DD = 100G (now a locked token)
    if "Q56" in u or "QSFP56" in u:       return "QSFP56"           # 200G
    if "Q28" in u or "QSFP28" in u or m.upper().startswith("100G"): return "QSFP28"
    if "QSFP" in u or m.upper().startswith("40G") or "-40G-" in m.upper(): return "QSFP+"
    if "SFP28" in u or "25G" in u:        return "SFP28"
    if "SFP10G" in u or "-10G-" in m.upper(): return "SFP+"
    if "CXP" in u:                         return "CXP"
    return "SFP"


def speed_of(m):
    u = m.upper()
    for sp in ("800G", "400G", "200G", "100G", "40G", "25G", "10G"):
        if sp in u or sp.replace("G", "GBE") in u:
            return sp
    if "100M" in u:  return "1G"          # FE catalogued in the 1G group
    if "1G" in u or u.startswith("SFP-1G"): return "1G"
    # FF-shorthand fallback (cables whose PN names only the form factor): O112=800G, Q56DD=400G,
    # Q28DD/Q56=200G, S56DD=100G.
    if "O112" in u:  return "800G"
    if "Q56DD" in u: return "400G"
    if "Q28DD" in u or ("Q56" in u and "DD" not in u): return "200G"
    if "S56DD" in u: return "100G"
    return ""


def media_of(s):
    u = (s or "").upper()
    if "SMF" in u or "SINGLE" in u:  return "SMF"
    if "MMF" in u or "OM" in u:      return "MMF"
    if "COPPER" in u or "CAT" in u:  return "Kupfer"
    return ""


def conn_of(s):
    u = (s or "").upper()
    if re.search(r"2\s*[X×]\s*MPO", u): return "2x MPO-12"   # 800G 2×R4 (16 fibres over two MPO-12)
    if "MPO-16" in u: return "MPO-16"
    if "MPO" in u:    return "MPO-12" if "12" in u else "MPO"
    if "LC" in u:     return "LC"
    if "RJ" in u:     return "RJ45"
    return rep(s)


# cable Anschlussenden from the PN (robust — the connection COLUMN truncates/leaks English in the PDF).
# Dell shorthand -> locked form-factor tokens; counts from the NxFF breakout pattern.
_FFTOK = [("O112", "OSFP"), ("OSFP", "OSFP"), ("Q112", "QSFP112"), ("Q56DD", "QSFP-DD"), ("Q28DD", "QSFP28-DD"),
          ("S56DD", "SFP-DD"), ("QSFP112", "QSFP112"), ("QSFP56", "QSFP56"), ("Q56", "QSFP56"), ("QSFP28", "QSFP28"),
          ("Q28", "QSFP28"), ("SFP56", "SFP56"), ("S56", "SFP56"), ("SFP28", "SFP28"), ("S28", "SFP28"),
          ("QSFP", "QSFP+"), ("SFP", "SFP+")]


def _resolve_ff(tok):
    for k, v in _FFTOK:
        m = re.match(r"(\d+)?[xX]?(%s)\b" % re.escape(k), tok, re.I)
        if m:
            return (int(m.group(1)) if m.group(1) else 1), v
    return None


def cable_ends_from_pn(pn):
    body = re.sub(r"^(DAC|AOC|AEC)-", "", pn, flags=re.I)
    ffs = [r for r in (_resolve_ff(t) for t in body.split("-")) if r]
    if not ffs:
        return ""
    prim = ffs[0][1]
    if len(ffs) >= 2:
        cnt, sec = ffs[1]
        # a standalone NxSPEED multiplier (e.g. "800G2x400G") carries the breakout count when the
        # secondary FF token itself had none (e.g. O112 -> 2x QSFP112 from "...2x400G-Q112").
        if cnt == 1:
            mm = re.search(r"(\d+)\s*[xX]\s*\d+G", pn)
            if mm:
                cnt = int(mm.group(1))
        return "%s auf %dx %s" % (prim, cnt, sec) if cnt > 1 else "%s auf %s" % (prim, sec)
    return "%s auf %s" % (prim, prim)


def reach_of(dist):
    """First/primary distance, datasheet-verbatim (cell may list several per media: '70 m 100 m')."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*(km|m)\b", dist or "")
    return ("%s %s" % (m.group(1), m.group(2))) if m else ""


def wl_of(wlcell, ff, m):
    """Wavelength SET verbatim from the explicit column. Multi-value -> '/'-joined SET (B.3-valid)."""
    s = rep(wlcell)
    if not s:
        return None
    if re.search(r"tunable|durchstimm|dwdm", s, re.I):
        return "durchstimmbar (DWDM, kohärent)"
    nums = re.findall(r"\d{3,4}", s)
    if not nums:
        return None
    if len(nums) == 1:
        return "%s nm" % nums[0]
    uniq = list(dict.fromkeys(nums))
    if len(uniq) == 2:                      # BiDi SR4.2 (850/910) or BX pair
        return "%s / %s nm (BiDi)" % (uniq[0], uniq[1])
    tag = "CWDM4" if uniq[0] == "1271" else ("LAN-WDM" if uniq[0].startswith("129") else "WDM")
    return "%s nm (%s, %d Lanes)" % (" / ".join(uniq), tag, len(uniq))


def type_of(m):
    u = m.upper()
    mt = re.search(r"(SR4\.2|SR1\.2|SR10|SR8|SR4|SR-?12|ESR4|ESR|VR8|VR4|EDR8|EDR4|LDR4|DR8|DR4|DR|LR4|LR|ER4-?LITE|ER4|ER|ZR\+|ZR|FR4|FR|PSM4|CWDM4|SWDM4|SM4|BIDI|USR|SX|LX|FX|ELX|2SR|2FR4|2EDR4|2VR4|2DR4|T)\b", u)
    return mt.group(1) if mt else ""


def parse_optics(pdf):
    out = {}
    for pi in range(2, 9):                  # pp3-9
        for t in pdf.pages[pi].extract_tables():
            if not t or not t[0] or "Model" not in (t[0][0] or ""):
                continue
            for r in t[1:]:
                m = rep(r[0])
                conn = rep(r[1]) if len(r) > 1 else ""
                if not m or not conn:        # section-header row (Model only)
                    continue
                m = clean_pn(m)
                if is_fc(m):
                    flags.append("%s | Fibre Channel -> out-of-scope (catalog-wide FC policy)" % m); continue
                if is_qsa(m):
                    flags.append("%s | QSFP->SFP adapter, not a transceiver -> exclude" % m); continue
                ff = ff_of(m)
                wl = rep(r[2]) if len(r) > 2 else ""
                med = rep(r[3]) if len(r) > 3 else ""
                dist = rep(r[4]) if len(r) > 4 else ""
                out[m] = {"pn": m, "speed": speed_of(m), "ff": ff, "type": type_of(m),
                          "connector": conn_of(conn), "connector_raw": conn, "wavelength": wl_of(wl, ff, m),
                          "media": media_of(med), "reach": reach_of(dist), "standard": "",
                          "cable": False, "alt_pns": [], "page": pi + 1}
    return out


def parse_cables(pdf):
    out = {}
    for pi in range(9, 12):                 # pp10-12
        for t in pdf.pages[pi].extract_tables():
            if not t or not t[0] or "Model" not in (t[0][0] or ""):
                continue
            for r in t[1:]:
                fam = clean_pn(rep(r[0])); lengths = rep(r[1]) if len(r) > 1 else ""
                conn = rep(r[2]) if len(r) > 2 else ""; med = rep(r[3]) if len(r) > 3 else ""
                if not fam or "M" not in fam.upper():
                    continue
                u = fam.upper()
                # SCOPE (operator): keep TRANSCEIVER-CLASS cables only — active direct-attach DAC/AOC/AEC
                # (incl. their breakouts) + passive MPO->xLC breakouts (MPO Kabel). DROP generic passive
                # patch/trunk (plain MPO-MPO, LC-LC, MPO-DD) — commodity structured cabling, no locked token.
                if u.startswith(("DAC", "AEC")):
                    k3, ctype = "DAC Kabel", "DAC"
                elif u.startswith("AOC"):
                    k3, ctype = "AOC Kabel", "AOC"
                else:
                    # CBL-* are PASSIVE optical patch/trunk/breakout — generic structured cabling with no
                    # inherent transceiver form factor (the active DAC/AOC breakouts, which carry a QSFP/SFP
                    # form factor, are kept above). Flagged out — operator can re-scope with an assigned FF.
                    flags.append("%s (%s) | passive CBL fibre patch/trunk/breakout, no transceiver form factor -> EXCLUDED" % (fam, conn)); continue
                lens = re.findall(r"\d+(?:\.\d+)?", lengths)
                if not lens:
                    flags.append("%s | cable family no lengths -> EXCLUDED" % fam); continue
                ff = ff_of(fam)
                ends = cable_ends_from_pn(fam)                # from the PN, not the truncatable column
                brk = bool(re.search(r"\bauf \d", ends))
                for ln in lens:
                    pn = re.sub(r"xM?\b", "%sM" % ln, fam, flags=re.I) if re.search(r"xM?\b", fam, re.I) else fam
                    out[pn] = {"pn": pn, "speed": speed_of(fam) or "", "ff": ff, "type": ctype,
                               "connector": conn_of(conn), "wavelength": None, "media": media_of(med),
                               "reach": "", "length": ln, "standard": "", "cable": True, "k3": k3,
                               "active": (ctype == "AOC"),
                               "breakout": brk, "ends_raw": ends, "alt_pns": [], "page": pi + 1}
                    if not re.search(r"xM?\b", fam, re.I):
                        break                    # single-length family (already has its length)
    return out


# Matrix-only 40G optics: in the 2026 SUPPORT MATRIX (p15: "40GbE SR4 ESR4 LM4 SM4 BIDI PSM4 LR4 ER4")
# but with NO 2026 spec-table/PN-list row (Dell streamlined the detail tables) -> grounded from the 2017
# Dell sheet's spec rows (cross-source; both Dell-official, parts matrix-confirmed current, not EOL).
# (operator L8 finding #1; all other tiers cross-checked against the matrix — 40G was the only gap.)
def _supplement():
    base = lambda **k: {"cable": False, "alt_pns": [], "page": 15,
                        "_source": "Dell 2017 spec sheet, confirmed current by the 2026 support matrix p15", **k}
    return {
        "QSFP-40G-ESR4": base(pn="QSFP-40G-ESR4", speed="40G", ff="QSFP+", type="ESR4", connector="MPO-12",
                              connector_raw="MPO", wavelength="850 nm", media="MMF", reach="400 m", standard="40GBASE-ESR4"),
        "QSFP-40G-ER4": base(pn="QSFP-40G-ER4", speed="40G", ff="QSFP+", type="ER4", connector="LC",
                             connector_raw="duplex LC", wavelength="1271 / 1291 / 1311 / 1331 nm (CWDM4, 4 Lanes)",
                             media="SMF", reach="40 km", standard="40GBASE-ER4"),
        "QSFP-40G-LM4": base(pn="QSFP-40G-LM4", speed="40G", ff="QSFP+", type="LM4", connector="LC",
                             connector_raw="duplex LC", wavelength="1310 nm", media="MMF", dual_media=True,
                             reach="150 m (MMF) / 1 km (SMF)", standard="40GBASE-LM4"),
    }


def main():
    pdf = pdfplumber.open(PDF)
    facts = parse_optics(pdf)
    facts.update(parse_cables(pdf))
    for pn, e in _supplement().items():
        facts.setdefault(pn, e)
    OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    FLAGS.write_text("\n".join(flags), encoding="utf-8")
    import collections
    opt = [p for p, f in facts.items() if not f.get("cable")]
    print("DELL CURRENT facts: %d (optics %d, cables %d)" % (len(facts), len(opt), len(facts) - len(opt)))
    print("optics by speed:", dict(collections.Counter(facts[p]["speed"] for p in opt)))
    print("optics by ff:   ", dict(collections.Counter(facts[p]["ff"] for p in opt)))
    print("flags:", len(flags))
    for f in flags: print("  ", f)


if __name__ == "__main__":
    main()
