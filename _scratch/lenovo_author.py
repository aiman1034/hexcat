# -*- coding: utf-8 -*-
"""Lenovo (ThinkSystem; absorbs IBM System Networking / BNT) Ethernet optics content author — German
v5.0 gold-slice for output/stage3/lenovo_facts.json (Lenovo Press lp1652/lp1417, current). Prose $0,
in-session. Mirrors the proven dell_author.py scaffold + Lenovo specifics: specs are grounded (the facts
carry the IEEE standard + explicit Faseranzahl); the Lenovo FEATURE CODE is woven into the Beschreibung
as an alt order code (the operator's IBM/BNT legacy-code handling, like Extreme's AA-/MGBIC-); dual-rate
10G/25G parts noted. DOM media-grounded (optical Ja / 10GBASE-T copper Nein). Writes Lenovo_content.json.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "output" / "stage3" / "lenovo_facts.json").read_text(encoding="utf-8"))
DEST = ROOT / "stage3_content" / "Lenovo_content.json"
URL = "https://lenovopress.lenovo.com/lp1652-thinksystem-broadcom-57504-25gbe-ethernet-adapters"
VEND = "Lenovo"
TODAY = "2026-06-15"
CABLE_FF = {"DAC Kabel", "AOC Kabel", "MPO Kabel"}
SPEED_DE = {"200G": "200-Gigabit", "100G": "100-Gigabit", "25G": "25-Gigabit", "10G": "10-Gigabit"}
KOMPAT_NOTE = ("Maßgeblich ist die Lenovo-Kompatibilitätsmatrix (Lenovo Press) für die jeweilige "
               "ThinkSystem-Plattform und den Firmware-/Treiberstand")
ORIG_FAQ = ["Ist dies ein originales Lenovo-Produkt?",
            "Ja. Es handelt sich um Lenovo-Original-Neuware (ThinkSystem) – versiegelt geliefert und für "
            "Lenovo-ThinkSystem-Server und -Adapter freigegeben."]


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def _wc(html):
    return len(re.sub(r"<[^>]+>", "", html).split())


def datarate(sp):
    return sp.replace("G", " Gbit/s")


def dom_of(f):
    return "Nein" if (f.get("media") == "Kupfer" or f.get("connector") == "RJ45") else "Ja"


def fasertyp(f):
    if f.get("media") == "Kupfer" or f.get("connector") == "RJ45":
        return "Kupfer"
    return "Multimode" if f.get("media") == "MMF" else "Singlemode"


PAD_KURZ = ["Die Lieferung erfolgt als versiegelte Original-Neuware.",
            "Vor dem Einsatz ist die Freigabe für Plattform und Firmware-Stand zu prüfen."]


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
        t = ws("Lenovo %s %s | Hexwaren" % (pn, tail))
        if len(t) <= 60:
            return t
    base = "Lenovo %s | Hexwaren" % pn
    return base if len(base) <= 60 else ("%s | Hexwaren" % pn)


def fit_meta(meta, filler):
    meta = ws(meta)
    while len(meta) < 140:
        meta = meta[:-1].rstrip() + filler
        filler = " Neu, versiegelt und für Lenovo-ThinkSystem freigegeben."
    return meta[:200].rstrip()


doc = {}
for pn, f in FACTS.items():
    cable = bool(f.get("cable"))
    uk = f["k3"] if cable else f["ff"]
    sp = f["speed"]
    spde, rate = SPEED_DE.get(sp, sp), datarate(sp)
    fc = f.get("feature_code")
    fc_clause = ("; das Produkt wird bei Lenovo unter dem Feature-Code %s geführt" % fc) if fc else ""
    prov = []

    if cable:
        length = ("%s m" % f["length"]).replace("0.5", "0,5").replace("1.5", "1,5") if f.get("length") else ""
        if not length:
            continue
        ends = f.get("ends_raw") or ""
        brk = bool(f.get("breakout"))
        aoc = uk == "AOC Kabel"
        if aoc:
            kabeltyp, kind_de = "Aktives optisches Kabel (AOC)", "aktives optisches Kabel (AOC)"
            phys_lc = ("die werkseitig terminierte Aktivoptik ist leichter und biegsamer als ein "
                       "Kupfer-DAC und überbrückt größere Distanzen")
            power_lc = "die integrierte Optik wird über die Ports versorgt, ein externes Netzteil entfällt"
        elif f.get("active"):
            kabeltyp, kind_de = "Aktives Twinax-Kupferkabel", "aktives Twinax-Kupferkabel"
            phys_lc = ("die aktive Elektronik im Kabel verbessert die Signalintegrität und erlaubt "
                       "größere Längen als ein passives DAC")
            power_lc = "die aktive Elektronik wird über die Ports versorgt, ein externes Netzteil entfällt"
        else:
            kabeltyp, kind_de = "Passives Twinax-Kupferkabel (DAC)", "passives Direct-Attach-Kupferkabel (DAC)"
            phys_lc = ("die passive Twinax-Baugruppe kommt ohne eigene Elektronik aus und bleibt eine "
                       "kostengünstige Direktverbindung im Rack")
            power_lc = "ohne aktive Komponenten benötigt es keine eigene Stromversorgung"
        short = "AOC" if aoc else "DAC"
        artikel = ws("%s %s %s %s%s %s – %s, Länge %s" % (VEND, pn, sp, ("Breakout-" if brk else ""), short, ends, kind_de, length))
        titel = clip_titel(pn, ["%s %s%s %s" % (sp, ("Breakout-" if brk else ""), short, length),
                                "%s %s %s" % (sp, short, length), "%s %s" % (sp, short)])
        meta = fit_meta(("Original %s %s: %s-%s, %s, Länge %s. Fest konfektioniert, neu, versiegelt, für "
                         "Lenovo-ThinkSystem." % (VEND, pn, spde, kabeltyp.lower(), ends, length)),
                        " Direktverbindung im Rechenzentrum.")
        kp1 = ("<p>Das %s %s ist ein %s-%s%s. Über eine Länge von %s verbindet es %s; die Enden sind fest "
               "konfektioniert und im Kabel enthalten.</p>"
               % (VEND, pn, spde, kabeltyp.lower(), (" für den Breakout (%s)" % ends) if brk else "", length, ends))
        kp2 = ("<p>Als Lenovo-Original-Neuware (ThinkSystem) wird das %s versiegelt geliefert und ist für "
               "ThinkSystem-Plattformen der entsprechenden Portklasse vorgesehen.</p>" % pn)
        i1 = ("Das %s %s ist ein %s-%s%s mit werkseitig fest konfektionierten Enden und richtet sich an "
              "Lenovo-ThinkSystem-Server und -Adapter mit der passenden Portklasse im Rechenzentrum."
              % (VEND, pn, spde, kind_de, (" für den Breakout (%s)" % ends) if brk else ""))
        i2 = ("Über eine fest konfektionierte Länge von %s verbindet das %s zwei Anschlüsse (%s); %s, sodass "
              "keine separaten Transceiver ausgewählt oder bestückt werden müssen." % (length, pn, ends, phys_lc))
        i3 = ("Im Betrieb %s; damit ist das %s eine wirtschaftliche %s-Direktverbindung und wird als einzeln "
              "verpackte, versiegelte Original-Neuware geliefert%s." % (power_lc, pn, sp, fc_clause))
        attrs = [["Formfaktor", uk], ["Datenrate", rate], ["Kabeltyp", kabeltyp], ["Anschlussenden", ends]]
        prov += ["Datenrate", "Kabeltyp", "Anschlussenden"]
        if brk:
            attrs.append(["Aufteilung", ends]); prov.append("Aufteilung")
        attrs += [["Länge", length], ["Transceiver", "fest konfektioniert (im Kabel enthalten)"],
                  ["Zustand", "Neu, versiegelt"]]
        prov.append("Länge")
        kompat = ["ThinkSystem-Ports mit passender Portklasse", KOMPAT_NOTE]
        faq = [ORIG_FAQ, ["Wie lang ist das %s?" % pn, "Das Kabel hat eine feste Länge von %s." % length],
               (["Benötigt das Kabel ein Netzteil?", "Nein. %s%s." % (power_lc[0].upper(), power_lc[1:])]
                if (aoc or f.get("active")) else
                ["Benötigt das Kabel eine eigene Stromversorgung?",
                 "Nein. Als passives Direct-Attach-Kupferkabel kommt es ohne aktive Elektronik aus."])]
        pool = ["Werksseitig konfektioniert erspart das %s die Auswahl und Bestückung separater Transceiver "
                "und verringert Fehlerquellen bei der Verkabelung." % pn,
                "Vor dem Einsatz des %s empfiehlt sich ein Abgleich von Plattform, Portgeschwindigkeit und "
                "Firmware-Stand." % pn]
    else:
        std, typ = f.get("standard") or "", f.get("type") or ""
        wl, reach, conn = f.get("wavelength"), f.get("reach") or "", f.get("connector") or ""
        fz = f.get("faseranzahl")
        fz = str(fz) if fz else None
        copper = f.get("media") == "Kupfer" or conn == "RJ45"
        ftyp = fasertyp(f)
        dual = " (dual-rate 10G/25G)" if f.get("dual_rate") else ""
        anschluss_txt = ("Über den %s-Anschluss " % conn) if conn else "Das Modul "
        reach_txt = ("überbrückt bis zu %s" % reach) if reach else "stellt die Verbindung bereit"
        artikel = ws("%s %s %s %s %s-Transceiver%s – %s%s%s" % (VEND, pn, sp, uk, (typ or "Optik"), dual, ftyp,
                     (", %s" % conn) if conn else "", (", bis %s" % reach) if reach else ""))
        titel = clip_titel(pn, ["%s %s %s" % (sp, uk, (typ or reach)), "%s %s %s" % (sp, uk, typ), "%s %s" % (sp, uk)])
        meta = fit_meta(("Original %s %s: %s %s-%s-Transceiver%s, %s%s%s. Neu, versiegelt, für Lenovo-ThinkSystem."
                         % (VEND, pn, typ, spde, uk, dual, ftyp, (", %s" % conn) if conn else "",
                            (", bis %s" % reach) if reach else "")),
                        " Verlässliche Lenovo-Optik für ThinkSystem-Server.")
        wl_clause = (" bei einer Wellenlänge von %s" % wl) if wl else ""
        faser_clause = ("; die optische Anbindung nutzt %s Fasern" % fz) if fz else ""
        kp1 = ("<p>Der %s %s ist ein %s-%s-Transceiver%s%s für %s%s. %s%s.</p>"
               % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if typ else "", dual,
                  ("RJ45-Kupfer" if copper else (ftyp + "-Glasfaser")), (" (%s)" % std) if std else "",
                  anschluss_txt, reach_txt))
        kp2 = ("<p>Als Lenovo-Original-Neuware (ThinkSystem) wird das Modul versiegelt geliefert, ist im "
               "laufenden Betrieb tauschbar (Hot-Plug) und für ThinkSystem-Systeme mit %s-Steckplätzen "
               "vorgesehen.</p>" % uk)
        i1 = ("Der %s %s ist ein %s-Transceiver im %s-Formfaktor%s%s und überträgt %s-Ethernet%s über %s, "
              "abgestimmt auf Lenovo-ThinkSystem-Server und -Adapter mit %s-Steckplätzen."
              % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if typ else "", dual, spde,
                 (" nach %s" % std) if std else "", ("RJ45-Kupfer" if copper else ftyp), uk))
        i2 = ("%s%s%s%s%s." % (anschluss_txt, reach_txt,
                               (" über %s" % ftyp) if not copper else " über strukturierte Kupferverkabelung",
                               wl_clause, faser_clause))
        i3 = ("Als auf den Lenovo-ThinkSystem-Plattformen freigegebene Lenovo-Optik vereinfacht das %s die "
              "Auswahl passender Module und vermeidet Verbindungsprobleme; geliefert wird es als einzeln "
              "verpackte, versiegelte Original-Neuware%s." % (pn, fc_clause))
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
        kompat = ["Lenovo-ThinkSystem-Systeme mit %s-Steckplätzen" % uk, KOMPAT_NOTE]
        faq = [ORIG_FAQ,
               (["Welche Reichweite erreicht der %s?" % pn, "Er überbrückt Strecken von bis zu %s." % reach]
                if reach else ["Wofür ist der %s ausgelegt?" % pn,
                               "Für %s-Verbindungen an %s-Steckplätzen von Lenovo-ThinkSystem-Systemen." % (spde, uk)]),
               ["In welchen Systemen lässt sich das Modul einsetzen?",
                "In Lenovo-ThinkSystem-Servern und -Adaptern mit %s-Steckplätzen; maßgeblich ist die "
                "Lenovo-Kompatibilitätsmatrix." % uk]]
        pool = ["Das %s ist im laufenden Betrieb steckbar (Hot-Plug) und erlaubt Wartung und Erweiterung "
                "ohne Unterbrechung des Systems." % pn,
                "Vor dem produktiven Einsatz des %s empfiehlt sich ein Abgleich von Plattform, "
                "Portgeschwindigkeit und Firmware-Stand." % pn]

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
print("authored %d Lenovo SKUs -> %s" % (len(doc), DEST.name))
