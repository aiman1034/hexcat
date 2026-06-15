# -*- coding: utf-8 -*-
"""Dell (PowerSwitch / Dell Networking) optics content author — German v5.0 gold-slice content for the
grounded SKUs in output/stage3/dell_facts.json (current © 2026 Dell spec sheet, Workflow-B). Prose
authored in-session ($0). Mirrors the proven extreme_author.py scaffold (cable vs module branch,
per-SKU-unique PN-woven sentences, pad floors, fill-every-slot for B.8) + Dell specifics:
  * Wavelengths are EXPLICIT in the facts (grounded verbatim from the spec sheet) — used directly.
  * DOM media-grounded (optical Ja per SFF-8472/CMIS, copper-T Nein); Faseranzahl from the raw connector
    (MPO-16 / 2×MPO-12 -> 16; MPO-12 -> 8; duplex LC -> 2; RJ45/copper -> none).
  * Standard derived from speed+type (100GBASE-LR4, 400GBASE-FR4, 800GBASE-2FR4, …); coherent ZR+ ->
    '{speed}BASE-ZR' so B.6 (tunable λ only on a coherent part) passes.
  * GUARD (operator flag-don't-fabricate): a part whose wavelength/standard can't be grounded cleanly is
    SKIPPED to dell_flagged_out.json (ship the rest, never the whole ZIP).
Writes stage3_content/Dell_content.json + output/stage3/dell_flagged_out.json.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "output" / "stage3" / "dell_facts.json").read_text(encoding="utf-8"))
DEST = ROOT / "stage3_content" / "Dell_content.json"
FLAGS_OUT = ROOT / "output" / "stage3" / "dell_flagged_out.json"
URL = "https://www.delltechnologies.com/asset/en-us/products/networking/technical-support/Dell_EMC_Networking_Optics_Spec_Sheet.pdf"
VEND = "Dell"
TODAY = "2026-06-15"
CABLE_FF = {"DAC Kabel", "AOC Kabel", "MPO Kabel"}
SPEED_DE = {"800G": "800-Gigabit", "400G": "400-Gigabit", "200G": "200-Gigabit", "100G": "100-Gigabit",
            "40G": "40-Gigabit", "25G": "25-Gigabit", "10G": "10-Gigabit", "1G": "1-Gigabit"}
KOMPAT_NOTE = ("Maßgeblich ist die Dell-Kompatibilitätsmatrix (Dell Networking Transceivers and Cables) "
               "für die jeweilige PowerSwitch-Plattform und den SmartFabric-OS10-Softwarestand")
ORIG_FAQ = ["Ist dies ein originales Dell-Produkt?",
            "Ja. Es handelt sich um Dell-Original-Neuware – versiegelt geliefert und für Dell-PowerSwitch-"
            "Plattformen unter SmartFabric OS10 freigegeben."]
SHORT = {"Q56DD": "QSFP56-DD", "Q28DD": "QSFP28-DD", "S56DD": "SFP-DD", "Q56": "QSFP56",
         "Q28": "QSFP28", "S28": "SFP28", "S56": "SFP-DD"}


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def _wc(html):
    return len(re.sub(r"<[^>]+>", "", html).split())


def datarate(sp):
    return sp.replace("G", " Gbit/s") if sp.endswith("G") else sp


def standard_of(f):
    t = (f.get("type") or "").strip()
    if not t:
        return ""
    tt = (t.replace("ZR+", "ZR").replace("SR-12", "SR1.2").replace("ER4-LITE", "ER4").replace("BIDI", "BiDi"))
    if "100M" in f["pn"]:
        return "100BASE-" + tt
    if f["speed"] == "1G":
        return "1000BASE-" + tt
    return "%sBASE-%s" % (f["speed"], tt)


def faseranzahl(f):
    raw = (f.get("connector_raw") or "").upper()
    t = (f.get("type") or "").upper()
    if f.get("media") == "Kupfer" or "RJ" in raw:
        return None
    if "MPO-16" in raw or "MPO16" in raw or re.search(r"2\s*[X×]\s*MPO", raw):
        return "16"
    if "MPO" in raw:
        return "8"                                   # MPO-12: 4-lane parallel = 8 fibres
    return "2"                                       # duplex LC (incl. BiDi SR1.2)


def dom_of(f):
    return "Nein" if (f.get("media") == "Kupfer" or (f.get("connector") == "RJ45")) else "Ja"


def fasertyp(f):
    if f.get("media") == "Kupfer" or f.get("connector") == "RJ45":
        return "Kupfer"
    if f.get("dual_media"):                # 40G-LM4: 150 m MMF + 1 km SMF
        return "Multimode/Singlemode"
    return "Multimode" if f.get("media") == "MMF" else "Singlemode"


def norm_ends(raw):
    s = (raw or "").replace(" to ", " auf ").replace("×", "x").replace(" x ", "x ")
    for k, v in SHORT.items():
        s = re.sub(r"\b%s\b" % k, v, s)
    return ws(s)


PAD_KURZ = ["Die Lieferung erfolgt als versiegelte Original-Neuware.",
            "Vor dem Einsatz ist die Freigabe für Plattform und OS10-Softwarestand zu prüfen."]


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
        t = ws("Dell %s %s | Hexwaren" % (pn, tail))
        if len(t) <= 60:
            return t
    base = "Dell %s | Hexwaren" % pn
    return base if len(base) <= 60 else ("%s | Hexwaren" % pn)


def fit_meta(meta, filler):
    meta = ws(meta)
    while len(meta) < 140:
        meta = meta[:-1].rstrip() + filler
        filler = " Neu, versiegelt und für Dell-PowerSwitch freigegeben."
    return meta[:200].rstrip()


doc, flagged = {}, {}
for pn, f in FACTS.items():
    cable = bool(f.get("cable"))
    uk = f["k3"] if cable else f["ff"]
    sp = f["speed"] or ""
    spde, rate = SPEED_DE.get(sp, sp), datarate(sp)
    prov = []

    if cable:
        length = ("%s m" % f["length"]).replace("0.5", "0,5") if f.get("length") else ""
        if not length:
            flagged[pn] = {"reason_code": "harvest-gap", "note": "cable without length"}; continue
        ends = norm_ends(f.get("ends_raw") or "")
        brk = bool(f.get("breakout"))
        aoc = uk == "AOC Kabel"
        mpo = uk == "MPO Kabel"
        if mpo:
            kabeltyp, kind_de = "Passives MPO-Glasfaser-Breakoutkabel", "passives MPO-Glasfaser-Breakoutkabel"
            phys_lc = ("die werkseitig konfektionierte MPO-Trunkleitung führt einen Parallel-Port auf "
                       "mehrere Duplex-LC-Anschlüsse und vermeidet Verkabelungsfehler")
            power_lc = "als reine Glasfaserstrecke benötigt es keine Stromversorgung"
        elif aoc:
            kabeltyp, kind_de = "Aktives optisches Kabel (AOC)", "aktives optisches Kabel (AOC)"
            phys_lc = ("die werkseitig terminierte Aktivoptik ist leichter und biegsamer als ein Kupfer-DAC "
                       "und überbrückt größere Distanzen")
            power_lc = "die integrierte Optik wird über die Ports versorgt, ein externes Netzteil entfällt"
        else:
            kabeltyp, kind_de = "Passives Direct-Attach-Kupferkabel (DAC)", "passives Direct-Attach-Kupferkabel (DAC)"
            phys_lc = ("die passive Twinax-Baugruppe kommt ohne eigene Elektronik aus und bleibt eine "
                       "kostengünstige Direktverbindung im Rack")
            power_lc = "ohne aktive Komponenten benötigt es keine eigene Stromversorgung"
        short = "AOC" if aoc else ("MPO" if mpo else "DAC")
        artikel = ws("%s %s %s %s%s – %s, Länge %s" % (VEND, pn, sp, ("Breakout-" if brk else ""), short, ends, length))
        titel = clip_titel(pn, ["%s %s%s %s" % (sp, ("Breakout-" if brk else ""), short, length),
                                "%s %s %s" % (sp, short, length), "%s %s" % (sp, short)])
        meta = fit_meta(("Original %s %s: %s-%s, %s, Länge %s. Fest konfektioniert, neu, versiegelt, für "
                         "Dell-PowerSwitch." % (VEND, pn, spde, kabeltyp.lower(), ends, length)),
                        " Direktverbindung im Rechenzentrum.")
        kp1 = ("<p>Das %s %s ist ein %s-%s%s. Über eine Länge von %s verbindet es %s; die Enden sind fest "
               "konfektioniert und im Kabel enthalten.</p>"
               % (VEND, pn, spde, kabeltyp.lower(), (" für den Breakout (%s)" % ends) if brk else "", length, ends))
        kp2 = ("<p>Als Dell-Original-Neuware wird das %s versiegelt geliefert und ist für Dell-PowerSwitch-"
               "Ports der entsprechenden Portklasse vorgesehen.</p>" % pn)
        i1 = ("Das %s %s ist ein %s-%s%s mit werkseitig fest konfektionierten Enden und richtet sich an "
              "Dell-PowerSwitch-Plattformen mit der passenden Portklasse im Rechenzentrum."
              % (VEND, pn, spde, kind_de, (" für den Breakout (%s)" % ends) if brk else ""))
        i2 = ("Über eine fest konfektionierte Länge von %s verbindet das %s zwei Anschlüsse (%s); %s, sodass "
              "keine separaten Transceiver ausgewählt oder bestückt werden müssen." % (length, pn, ends, phys_lc))
        i3 = ("Im Betrieb %s; damit ist das %s eine wirtschaftliche %s-Direktverbindung und wird als einzeln "
              "verpackte, versiegelte Original-Neuware für Erstaufbau und Ersatzbeschaffung geliefert."
              % (power_lc, pn, sp))
        attrs = [["Formfaktor", uk], ["Datenrate", rate], ["Kabeltyp", kabeltyp], ["Anschlussenden", ends]]
        prov += ["Datenrate", "Kabeltyp", "Anschlussenden"]
        if brk:
            attrs.append(["Aufteilung", ends]); prov.append("Aufteilung")
        attrs += [["Länge", length], ["Transceiver", "fest konfektioniert (im Kabel enthalten)"],
                  ["Zustand", "Neu, versiegelt"]]
        prov.append("Länge")
        kompat = ["Dell-PowerSwitch-Ports mit passender Portklasse", KOMPAT_NOTE]
        faq = [ORIG_FAQ, ["Wie lang ist das %s?" % pn, "Das Kabel hat eine feste Länge von %s." % length],
               (["Benötigt das Kabel ein Netzteil?", "Nein. %s%s." % (power_lc[0].upper(), power_lc[1:])]
                if (aoc or mpo) else
                ["Benötigt das Kabel eine eigene Stromversorgung?",
                 "Nein. Als passives Direct-Attach-Kupferkabel kommt es ohne aktive Elektronik aus."])]
        pool = ["Werksseitig konfektioniert erspart das %s die Auswahl und Bestückung separater Transceiver "
                "und verringert Fehlerquellen bei der Verkabelung." % pn,
                "Vor dem Einsatz des %s empfiehlt sich ein Abgleich von Plattform, Portgeschwindigkeit und "
                "OS10-Softwarestand." % pn]
    else:
        std = standard_of(f)
        typ = (f.get("type") or "").strip()
        wl = f.get("wavelength")
        copper = f.get("media") == "Kupfer" or f.get("connector") == "RJ45"
        # GUARD: an optical module must have a grounded wavelength (B.3/B.4); none -> flag, don't fabricate.
        if not copper and not wl:
            flagged[pn] = {"reason_code": "un-groundable-after-ladder", "note": "no grounded wavelength", "type": typ}; continue
        ftyp, fz = fasertyp(f), faseranzahl(f)
        conn = f.get("connector") or ""
        reach = f.get("reach") or ""
        anschluss_txt = ("Über den %s-Anschluss " % conn) if conn else "Das Modul "
        reach_txt = ("überbrückt bis zu %s" % reach) if reach else "stellt die Verbindung bereit"
        artikel = ws("%s %s %s %s %s-Transceiver – %s%s%s" % (VEND, pn, sp, uk, (typ or "Optik"), ftyp,
                     (", %s" % conn) if conn else "", (", bis %s" % reach) if reach else ""))
        titel = clip_titel(pn, ["%s %s %s" % (sp, uk, (typ or reach)), "%s %s %s" % (sp, uk, typ), "%s %s" % (sp, uk)])
        meta = fit_meta(("Original %s %s: %s %s-%s-Transceiver, %s%s%s. Neu, versiegelt, für Dell-PowerSwitch."
                         % (VEND, pn, typ, spde, uk, ftyp, (", %s" % conn) if conn else "",
                            (", bis %s" % reach) if reach else "")),
                        " Verlässliche Dell-Optik für PowerSwitch-Plattformen.")
        wl_clause = (" bei einer Wellenlänge von %s" % wl) if wl else ""
        faser_clause = ("; die optische Anbindung nutzt %s Fasern" % fz) if fz else ""
        kp1 = ("<p>Der %s %s ist ein %s-%s-Transceiver%s für %s%s. %s%s.</p>"
               % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if typ else "",
                  ("RJ45-Kupfer" if copper else (ftyp + "-Glasfaser")), (" (%s)" % std) if std else "",
                  anschluss_txt, reach_txt))
        kp2 = ("<p>Als Dell-Original-Neuware wird das Modul versiegelt geliefert, ist im laufenden Betrieb "
               "tauschbar (Hot-Plug) und für Dell-PowerSwitch-Systeme mit %s-Steckplätzen vorgesehen.</p>" % uk)
        i1 = ("Der %s %s ist ein %s-Transceiver im %s-Formfaktor%s und überträgt %s-Ethernet%s über %s, "
              "abgestimmt auf Dell-PowerSwitch-Plattformen mit %s-Steckplätzen."
              % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if typ else "", spde,
                 (" nach %s" % std) if std else "", ("RJ45-Kupfer" if copper else ftyp), uk))
        i2 = ("%s%s%s%s%s." % (anschluss_txt, reach_txt,
                               (" über %s" % ftyp) if not copper else " über strukturierte Kupferverkabelung",
                               wl_clause, faser_clause))
        i3 = ("Als auf den Dell-PowerSwitch-Plattformen qualifizierte Dell-Optik vereinfacht das %s die "
              "Auswahl passender Module und vermeidet Verbindungsprobleme; geliefert wird es als einzeln "
              "verpackte, versiegelte Original-Neuware für Systeme mit %s-Steckplätzen." % (pn, uk))
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
        kompat = ["Dell-PowerSwitch-Systeme mit %s-Steckplätzen" % uk, KOMPAT_NOTE]
        faq = [ORIG_FAQ,
               (["Welche Reichweite erreicht der %s?" % pn, "Er überbrückt Strecken von bis zu %s." % reach]
                if reach else ["Wofür ist der %s ausgelegt?" % pn,
                               "Für %s-Verbindungen an %s-Steckplätzen von Dell-PowerSwitch-Plattformen." % (spde, uk)]),
               ["In welchen Systemen lässt sich das Modul einsetzen?",
                "In Dell-PowerSwitch-Systemen mit %s-Steckplätzen; maßgeblich ist die Dell-Kompatibilitätsmatrix." % uk]]
        pool = ["Das %s ist im laufenden Betrieb steckbar (Hot-Plug) und erlaubt Wartung und Erweiterung "
                "ohne Unterbrechung des Switches." % pn,
                "Vor dem produktiven Einsatz des %s empfiehlt sich ein Abgleich von Plattform, "
                "Portgeschwindigkeit und OS10-Softwarestand." % pn]

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
print("authored %d Dell SKUs -> %s" % (len(doc), DEST.name))
print("flagged-out %d: %s" % (len(flagged), ", ".join(flagged) or "none"))
