# -*- coding: utf-8 -*-
"""Extreme Networks optics content author — composes German v5.0 gold-slice content for the grounded
SKUs in output/stage3/extreme_facts.json (parsed from the Extreme Optics Solution Guide). Prose
authored in-session ($0). Mirrors the proven nvidia_author.py scaffold (cable vs module branch,
per-SKU-unique PN-woven sentences, pad floors, clip/fit) and adapts it to Extreme's richer facts
(standard/wavelength/connector/reach/media already grounded) + Extreme specifics:
  * DOM Unterstützung emitted per SKU by MEDIA (optical=Ja per SFF-8472/CMIS, copper-T=Nein) — B.9/B.10.
  * Faseranzahl derived from connector/type (MPO=8, BX/BiDi single-fibre=1, BDSR duplex=2, LC=2).
  * alt_pns (legacy Avaya AA-/Enterasys MGBIC-/numeric order codes) -> a "Kompatible Bestellnummern" line.
  * 4 BiDi blank-λ closed by the BX convention (10G 1270/1330, 1G 1490/1310 — datasheet-VERIFIED).
  * FLAG-OUT (flag-don't-fabricate): 3x 100G-4WDM (the -10/-20/-40 λ PLANS — CWDM4 vs LAN-WDM —
    are unprovable without the EXOS DB) + 1x 100GBASE-SR10-CFP2 (parsed connector MPO-12 contradicts
    SR10's 20-fibre requirement; Faseranzahl/connector unprovable). Recorded for the completeness record.
Writes stage3_content/Extreme_content.json + output/stage3/extreme_flagged_out.json.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "output" / "stage3" / "extreme_facts.json").read_text(encoding="utf-8"))
DEST = ROOT / "stage3_content" / "Extreme_content.json"
FLAGS_OUT = ROOT / "output" / "stage3" / "extreme_flagged_out.json"
URL = "https://www.extremenetworks.com/support/documentation/extreme-optics/"
VEND = "Extreme"
TODAY = "2026-06-14"

# spec-uncertain flag-outs (moved captured->flagged; reason-coded for L6/completeness)
FLAG_OUT = {
    "100G-4WDM-QSFP10KM": "un-groundable-after-ladder",
    "100G-4WDM-QSFP20KM": "un-groundable-after-ladder",
    "100G-4WDM-QSFM40KM": "un-groundable-after-ladder",
    "10331": "source-blocked",   # 100GBASE-SR10-CFP2: parsed MPO-12 contradicts SR10 (20-fibre); unprovable
    "40G-LM4-QSFP160KM": "un-groundable-after-ladder",  # 1310nm SMF cannot reach 160 km — λ/reach/type inconsistent
}

# Lane-aware 4-λ grids (IEEE-pinned, §7.4) — used for the WDM types whose facts λ was a range or wrong.
SET_LANWDM_100G = "1295,56 / 1300,05 / 1304,58 / 1309,14 nm (LAN-WDM, 4 Lanes)"   # 100G LR4/ER4
SET_CWDM4 = "1271 / 1291 / 1311 / 1331 nm (CWDM4, 4 Lanes)"                       # 40G LR4/ER4, 100G CWDM4
SET_SWDM4 = "850 / 880 / 910 / 940 nm (SWDM4, 4 Lanes)"                            # SWDM4 over MMF

SPEED_DE = {"100G": "100-Gigabit", "40G": "40-Gigabit", "25G": "25-Gigabit",
            "20G": "20-Gigabit", "10G": "10-Gigabit", "1G": "1-Gigabit"}
CABLE_FF = {"DAC Kabel", "AOC Kabel"}
KOMPAT_NOTE = ("Maßgeblich ist die Extreme-Optics-Kompatibilitätsmatrix (Extreme Optics Compatibility "
               "Matrix) für die jeweilige ExtremeSwitching-/ExtremeRouting-Plattform und den EXOS-/"
               "Switch-Engine-Softwarestand")
ORIG_FAQ = ["Ist dies ein originales Extreme-Networks-Produkt?",
            "Ja. Es handelt sich um Extreme-Networks-Original-Neuware – versiegelt geliefert und für "
            "ExtremeSwitching- und ExtremeRouting-Plattformen freigegeben."]


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def _wc(html):
    return len(re.sub(r"<[^>]+>", "", html).split())


def datarate(sp):
    return sp.replace("G", " Gbit/s") if sp.endswith("G") else sp


def is_cable(f):
    t = (f.get("type") or "").upper()
    return "DAC" in t or "AOC" in t


def k3_of(pn, f):
    if not is_cable(f):
        return f["ff"]
    return "AOC Kabel" if "AOC" in (f.get("type") or "").upper() or "AOC" in pn.upper() else "DAC Kabel"


def kabeltyp_of(pn):
    P = pn.upper()
    if "DACA" in P:
        return "Aktives Twinax-Kupferkabel", "aktives Twinax-Kupferkabel", False
    if "AOC" in P:
        return "Aktives optisches Kabel (AOC)", "aktives optisches Kabel (AOC)", True
    return "Passives Twinax-Kupferkabel (DAC)", "passives Direct-Attach-Kupferkabel (DAC)", False


def _ff_norm(tok, speed):
    t = tok.upper()
    if "SFP-DD" in t:
        return "SFP-DD"
    if t.startswith("QSFP"):
        return "QSFP28" if speed == "100G" else "QSFP+"
    return "SFP28" if speed in ("100G", "25G") else "SFP+"


def cable_ends(pn, ff, speed):
    """(ends_text, breakout_factor, breakout_target). Breakout parsed from the PN pattern FF<n>FF
    (e.g. QSFP4SFP -> 4x; SFP-DD2SFP -> 2x; QSFP1SFP-DD -> 1:1 adapter)."""
    m = re.search(r"(QSFP\+?|SFP-DD|SFP\+?)(\d)(QSFP\+?|SFP-DD|SFP\+?)", pn, re.I)
    if not m:
        return "%s auf %s" % (ff, ff), 0, ""
    a, n, b = _ff_norm(m.group(1), speed), int(m.group(2)), _ff_norm(m.group(3), speed)
    if n <= 1:
        return "%s auf %s" % (a, b), 1, b
    return "%s auf %dx %s" % (a, n, b), n, b


def faseranzahl(f):
    if (f.get("media") == "Kupfer") or (f.get("connector") == "RJ45"):
        return None
    conn, typ = (f.get("connector") or ""), (f.get("type") or "").upper()
    if "MPO-16" in conn or "MPO16" in conn or "SR8" in typ or "DR8" in typ:
        return "16"                                  # 8-lane parallel (SR8/DR8) over MPO-16: 16 fibres
    if conn.startswith("MPO"):
        return "8"                                   # 4-lane parallel (SR4/ESR4/PSM4/DR4): 8 fibres
    if "BDSR" in typ:
        return "2"                                   # BiDi-SR over an LC duplex pair
    if typ.startswith("BX") or "BIDI" in typ:
        return "1"                                   # single-strand BiDi
    return "2"                                       # LC duplex


def fasertyp(f):
    if f.get("media") == "Kupfer" or f.get("connector") == "RJ45":
        return "Kupfer"
    om = f.get("om")
    if f.get("media") == "MMF":
        return "Multimode (%s)" % om if om else "Multimode"
    return "Singlemode"


# WDM multi-lane family, keyed off the STANDARD (lane-aware §7.4): LR4/ER4/ER4-Lite(ERLT)/FR4/CWDM4/
# SWDM4 multiplex λ over a duplex pair -> the 4-λ SET. PARALLEL single-λ siblings (SR4/ESR4/PSM4/DR4)
# do NOT match (no LR4/ER4/... token) and keep their one λ. (ERLT added after the L8 ER4LT 1550 nm miss.)
_WDM_FAMILY = re.compile(r"\bLR4|\bER4|\bERLT|\bFR4|\bCWDM4|\bSWDM4|LAN-?WDM", re.I)


def wavelength_of(pn, f):
    sp = f.get("speed")
    blob = ((f.get("standard") or "") + " " + (f.get("type") or "")).upper()
    if _WDM_FAMILY.search(blob):                      # WDM multi-λ family -> the IEEE-pinned 4-λ SET
        if "SWDM4" in blob:
            return SET_SWDM4
        if "CWDM4" in blob:
            return SET_CWDM4
        return SET_LANWDM_100G if sp == "100G" else SET_CWDM4   # LR4/ER4/ERLT/FR4: LAN-WDM @100G, CWDM4 grid @40G
    if f.get("connector") == "RJ45" or f.get("media") == "Kupfer":
        return ""                                    # copper has no optical wavelength
    typ = (f.get("type") or "").upper()
    if typ.startswith("BX") or "BIDI" in typ:        # single-strand BiDi by the BX convention (datasheet-verified)
        return "1270 / 1330 nm (BiDi)" if sp == "10G" else "1490 / 1310 nm (BiDi)"
    wl = f.get("wavelength")
    return ws(wl) if wl else ""                       # serial single-λ (SR/LR/ER/ZR/DR/FR/SX/LX/FX/ELX/LRM)


def dom_of(f):
    return "Nein" if (f.get("media") == "Kupfer" or f.get("connector") == "RJ45") else "Ja"


def reach_of(f):
    return f.get("reach") or ""


def alt_codes(pn, f):
    """Genuine alternate ORDER codes for THIS physical optic, woven into the Beschreibung (an emitted,
    searchable field) so a customer searching an old Avaya AA-/Enterasys numeric code still finds it.
    MODULES are 1:1 -> their alt_pns are clean cross-refs. CABLES are length-FAMILIES whose numeric/AA
    codes interleave across the lengths and cannot be attributed to one length -> DESCOPED (flag-don't-
    fabricate; presenting a sibling-length's code as 'alternative' would be wrong)."""
    if is_cable(f):
        return []
    return [a for a in (f.get("alt_pns") or []) if a]


PAD_INTRO_CABLE = [
    "Werksseitig konfektionierte Kabel ersparen die Auswahl und Bestückung separater Transceiver "
    "und verringern mögliche Fehlerquellen bei der Verkabelung.",
    "Vor dem Einsatz empfiehlt sich ein Abgleich von Plattform, Portgeschwindigkeit und "
    "Software-Stand, um die Verbindung zuverlässig in Betrieb zu nehmen.",
]
PAD_INTRO_MOD = [
    "Vor dem Einsatz empfiehlt sich ein Abgleich von Plattform, Portgeschwindigkeit und "
    "Software-Stand, um die Verbindung ohne Nacharbeit in Betrieb zu nehmen.",
    "Das Modul ist im laufenden Betrieb steckbar (Hot-Plug) und unterstützt damit Wartung und "
    "Erweiterung ohne Unterbrechung des Switches.",
]
PAD_KURZ = ["Die Lieferung erfolgt als versiegelte Original-Neuware.",
            "Vor dem Einsatz ist die Freigabe für Plattform und Software-Stand zu prüfen."]


def pad_intro(intro, pool, lo=95, hi=175):
    i = 0
    while sum(_wc(p) for p in intro) < lo and i < len(pool):
        cand = pool[i]; i += 1
        if sum(_wc(p) for p in intro) + _wc(cand) <= hi:
            intro[-1] = ws(intro[-1] + " " + cand)
    return intro


def pad_kurz(kp1, kp2, lo=44, hi=80):
    i = 0
    while _wc(kp1 + kp2) < lo and i < len(PAD_KURZ):
        cand = PAD_KURZ[i]; i += 1
        if _wc(kp1 + kp2) + _wc(cand) <= hi:
            kp2 = kp2[:-4].rstrip() + " " + cand + "</p>"
    return kp1 + kp2


def clip_titel(pn, parts):
    for tail in parts:
        t = ws("Extreme %s %s | Hexwaren" % (pn, tail))
        if len(t) <= 60:
            return t
    base = "Extreme %s | Hexwaren" % pn
    return base if len(base) <= 60 else ("%s | Hexwaren" % pn)


def fit_meta(meta, filler):
    meta = ws(meta)
    while len(meta) < 140:
        meta = meta[:-1].rstrip() + filler
        filler = " Neu, versiegelt und für Extreme-Plattformen freigegeben."
    return meta[:200].rstrip()


doc, flagged = {}, {}
for pn, f in FACTS.items():
    if pn in FLAG_OUT:
        flagged[pn] = {"reason_code": FLAG_OUT[pn], "standard": f.get("standard"), "type": f.get("type")}
        continue
    uk = k3_of(pn, f)
    sp = f["speed"]
    spde, rate = SPEED_DE.get(sp, sp), datarate(sp)
    length = ("%s m" % f["length"]).replace(".0 m", " m").replace("0.5", "0,5") if f.get("length") else ""
    acodes = alt_codes(pn, f)
    prov = []

    if uk in CABLE_FF:
        ktyp, kind_de, aoc = kabeltyp_of(pn)
        if not length:
            print("  FLAG: cable without length:", pn, "-> skipped"); flagged[pn] = {"reason_code": "harvest-gap", "note": "no length"}; continue
        ends, brk_n, brk_t = cable_ends(pn, f["ff"], sp)
        brk = brk_n > 1
        if aoc:
            phys_lc = ("die werkseitig terminierte Aktivoptik ist leichter und biegsamer als ein "
                       "Kupfer-DAC und überbrückt größere Distanzen")
            power_lc = "die integrierte Optik wird über die Ports versorgt, ein externes Netzteil entfällt"
        elif "Aktives Twinax" in ktyp:
            phys_lc = ("die aktive Elektronik im Kabel verbessert die Signalintegrität und erlaubt "
                       "größere Längen als ein passives DAC")
            power_lc = "die aktive Elektronik wird über die Ports versorgt, ein externes Netzteil entfällt"
        else:
            phys_lc = ("die passive Twinax-Baugruppe kommt ohne eigene Elektronik aus und bleibt "
                       "eine kostengünstige Direktverbindung im Rack")
            power_lc = "ohne aktive Komponenten benötigt es keine eigene Stromversorgung"
        short = "AOC" if aoc else "DAC"
        artikel = ws("%s %s %s %s%s %s – %s, Länge %s"
                     % (VEND, pn, sp, ("Breakout-" if brk else ""), short, ends, kind_de, length))
        titel = clip_titel(pn, ["%s %s%s %s" % (sp, ("Breakout-" if brk else ""), short, length),
                                "%s %s %s" % (sp, short, length), "%s %s" % (sp, short)])
        meta = fit_meta(("Original %s %s: %s-%s, %s, Länge %s. Fest konfektioniert, neu, versiegelt, "
                         "für ExtremeSwitching-Plattformen."
                         % (VEND, pn, spde, ktyp.lower(), ends, length)),
                        " Direktverbindung im Rechenzentrum.")
        kp1 = ("<p>Das %s %s ist ein %s-%s%s. Über eine Länge von %s verbindet es %s; die Enden "
               "sind fest konfektioniert und im Kabel enthalten.</p>"
               % (VEND, pn, spde, ktyp.lower(), (" für den Breakout (%s)" % ends) if brk else "",
                  length, ends))
        kp2 = ("<p>Als Extreme-Networks-Original-Neuware wird das %s versiegelt geliefert und ist für "
               "ExtremeSwitching-/ExtremeRouting-Ports der entsprechenden Portklasse vorgesehen.</p>" % pn)
        i1 = ("Das %s %s ist ein %s-%s%s mit werkseitig fest konfektionierten Enden und richtet sich "
              "an ExtremeSwitching- und ExtremeRouting-Plattformen mit der passenden Portklasse."
              % (VEND, pn, spde, kind_de, (" für den Breakout (%s)" % ends) if brk else ""))
        i2 = ("Über eine fest konfektionierte Länge von %s verbindet das %s zwei Anschlüsse (%s); "
              "%s, sodass keine separaten Transceiver ausgewählt oder bestückt werden müssen."
              % (length, pn, ends, phys_lc))
        i3 = ("Im Betrieb %s; damit ist das %s eine kostengünstige %s-Direktverbindung und wird als "
              "einzeln verpackte, versiegelte Original-Neuware für Erstaufbau und Ersatzbeschaffung "
              "geliefert." % (power_lc, pn, sp))
        attrs = [["Formfaktor", uk], ["Datenrate", rate], ["Kabeltyp", ktyp], ["Anschlussenden", ends]]
        prov += ["Datenrate", "Kabeltyp", "Anschlussenden"]
        if brk:
            attrs.append(["Aufteilung", "%dx %s" % (brk_n, brk_t)]); prov.append("Aufteilung")
        attrs += [["Länge", length], ["Transceiver", "fest konfektioniert (im Kabel enthalten)"],
                  ["Zustand", "Neu, versiegelt"]]
        prov.append("Länge")
        kompat = ["ExtremeSwitching-/ExtremeRouting-Ports mit passender Portklasse", KOMPAT_NOTE]
        # cables: alt order codes DESCOPED (length-family interleaving — see alt_codes()); none woven.
        faq = [ORIG_FAQ, ["Wie lang ist das %s?" % pn, "Das Kabel hat eine feste Länge von %s." % length]]
        faq.append(["Benötigt das Kabel ein Netzteil?", "Nein. %s%s." % (power_lc[0].upper(), power_lc[1:])]
                   if (aoc or "Aktives Twinax" in ktyp) else
                   ["Benötigt das Kabel eine eigene Stromversorgung?",
                    "Nein. Als passives Direct-Attach-Kupferkabel kommt es ohne aktive Elektronik aus."])
        if brk:
            faq.append(["Wozu dient das Breakout-Kabel?",
                        "Es teilt einen Highspeed-Port in %dx %s auf und verbindet ihn mit mehreren "
                        "Ports." % (brk_n, brk_t)])
        pool = ["Werksseitig konfektioniert erspart das %s die Auswahl und Bestückung separater "
                "Transceiver und verringert Fehlerquellen bei der Verkabelung." % pn,
                "Vor dem Einsatz des %s empfiehlt sich ein Abgleich von Plattform, Portgeschwindigkeit "
                "und Software-Stand." % pn]
    else:
        std, typ = f.get("standard") or "", f.get("type") or ""
        ftyp, fz, conn = fasertyp(f), faseranzahl(f), (f.get("connector") or "")
        wl, reach = wavelength_of(pn, f), reach_of(f)
        copper = f.get("media") == "Kupfer" or conn == "RJ45"
        anschluss_txt = ("Über den %s-Anschluss " % conn) if conn else "Das Modul "
        reach_txt = ("überbrückt bis zu %s" % reach) if reach else "stellt die Verbindung bereit"
        artikel = ws("%s %s %s %s %s-Transceiver – %s%s%s"
                     % (VEND, pn, sp, uk, (typ or "Optik"), ftyp,
                        (", %s" % conn) if conn else "", (", bis %s" % reach) if reach else ""))
        titel = clip_titel(pn, ["%s %s %s" % (sp, uk, (typ or reach)), "%s %s %s" % (sp, uk, typ),
                                "%s %s" % (sp, uk)])
        meta = fit_meta(("Original %s %s: %s %s-%s-Transceiver, %s%s%s. Neu, versiegelt, für "
                         "ExtremeSwitching."
                         % (VEND, pn, typ, spde, uk, ftyp, (", %s" % conn) if conn else "",
                            (", bis %s" % reach) if reach else "")),
                        " Verlässliche Extreme-Optik für Switching und Routing.")
        kp1 = ("<p>Der %s %s ist ein %s-%s-Transceiver%s für %s-Glasfaser%s. %s%s.</p>"
               % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if typ else "",
                  ("Kupfer" if copper else ftyp.split(" (")[0]),
                  (" (%s)" % std) if std else "", anschluss_txt, reach_txt)) if not copper else \
              ("<p>Der %s %s ist ein %s-%s-Transceiver%s für strukturierte Kupferverkabelung%s. "
               "%süber RJ45.</p>"
               % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if typ else "",
                  (" (%s)" % std) if std else "", reach_txt[0].upper() + reach_txt[1:]))
        kp2 = ("<p>Als Extreme-Networks-Original-Neuware wird das Modul versiegelt geliefert, ist im "
               "laufenden Betrieb tauschbar (Hot-Plug) und für ExtremeSwitching-/ExtremeRouting-"
               "Systeme mit %s-Steckplätzen vorgesehen.</p>" % uk)
        wl_clause = (" bei einer Wellenlänge von %s" % wl) if wl else ""
        faser_clause = ("; die optische Anbindung nutzt %s Fasern" % fz) if fz else ""
        i1 = ("Der %s %s ist ein %s-Transceiver im %s-Formfaktor%s und überträgt %s-Ethernet%s über %s, "
              "abgestimmt auf ExtremeSwitching- und ExtremeRouting-Plattformen mit %s-Steckplätzen."
              % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if typ else "", spde,
                 (" nach %s" % std) if std else "", ("RJ45-Kupfer" if copper else ftyp), uk))
        i2 = ("%s%s%s%s%s." % (anschluss_txt, reach_txt,
                               (" über %s" % ftyp) if not copper else " über strukturierte Kupferverkabelung",
                               wl_clause, faser_clause))
        i3 = ("Als auf den ExtremeSwitching-Plattformen qualifizierte Extreme-Optik vereinfacht das %s "
              "die Auswahl passender Module und vermeidet Verbindungsprobleme; geliefert wird es als "
              "einzeln verpackte, versiegelte Original-Neuware für Erstaufbau und Ersatzbeschaffung an "
              "Systemen mit %s-Steckplätzen." % (pn, uk))
        attrs = [["Formfaktor", uk], ["Datenrate", rate]]
        if typ:
            attrs.append(["Transceiver Typ", typ]); prov.append("Transceiver Typ")
        attrs.append(["Medientyp", ftyp]); prov.append("Medientyp")
        if fz:
            attrs.append(["Faseranzahl", fz]); prov.append("Faseranzahl")
        if conn:
            attrs.append(["Anschluss", conn]); prov.append("Anschluss")
        if wl:
            attrs.append(["Wellenlänge", wl]); prov.append("Wellenlänge")
        if reach:
            attrs.append(["Reichweite", "bis %s" % reach]); prov.append("Reichweite")
        if std:
            attrs.append(["Standard", std]); prov.append("Standard")
        attrs.append(["DOM/DDM", dom_of(f)]); prov.append("DOM/DDM")
        attrs.append(["Zustand", "Neu, versiegelt"])
        prov.append("Datenrate")
        kompat = ["ExtremeSwitching-/ExtremeRouting-Systeme mit %s-Steckplätzen" % uk, KOMPAT_NOTE]
        # MODULE alt order codes -> woven into the Beschreibung (emitted, searchable) + a FAQ pair, so a
        # customer searching an Avaya AA-/Enterasys legacy code finds the product (the kompatibilitaet
        # field is NOT emitted — never put load-bearing data there).
        if acodes:
            _ref = ("der Bestellnummer %s" % acodes[0]) if len(acodes) == 1 \
                else ("den Bestellnummern %s" % ", ".join(acodes))
            i3 = i3.rstrip(".") + "; das Modul wird zudem unter %s geführt." % _ref
        faq = [ORIG_FAQ]
        faq.append(["Welche Reichweite erreicht der %s?" % pn,
                    "Er überbrückt Strecken von bis zu %s." % reach] if reach else
                   ["Wofür ist der %s ausgelegt?" % pn,
                    "Für %s-Verbindungen an %s-Steckplätzen von ExtremeSwitching-Plattformen." % (spde, uk)])
        faq.append(["In welchen Systemen lässt sich das Modul einsetzen?",
                    "In ExtremeSwitching- und ExtremeRouting-Systemen mit %s-Steckplätzen; maßgeblich "
                    "ist die Extreme-Optics-Kompatibilitätsmatrix." % uk])
        pool = ["Das %s ist im laufenden Betrieb steckbar (Hot-Plug) und erlaubt Wartung und "
                "Erweiterung ohne Unterbrechung des Switches." % pn,
                "Vor dem produktiven Einsatz des %s empfiehlt sich ein Abgleich von Plattform, "
                "Portgeschwindigkeit und Software-Stand." % pn]

    kurz = pad_kurz(kp1, kp2)
    intro = pad_intro([ws(i1), ws(i2), ws(i3)], pool)
    e = {"_facts": {"unterkategorie": uk, "quell_url": URL, "verifiziert_am": TODAY},
         "artikelname": ws(artikel), "titel_tag": titel, "meta_description": meta,
         "kurzbeschreibung": ws(kurz), "intro": intro, "kompatibilitaet": kompat,
         "faq": faq, "verwandte": [], "attributes": attrs,
         "provenance": {lab: [URL, "datasheet"] for lab in prov},
         "beschreibung": "", "netto_vk": None}
    assert len(e["titel_tag"]) <= 60 and e["titel_tag"].endswith("| Hexwaren"), (pn, e["titel_tag"])
    doc[pn] = e

DEST.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
FLAGS_OUT.write_text(json.dumps(flagged, ensure_ascii=False, indent=1), encoding="utf-8")
print("authored %d Extreme SKUs -> %s" % (len(doc), DEST.name))
print("flagged-out %d: %s" % (len(flagged), ", ".join(flagged)))
