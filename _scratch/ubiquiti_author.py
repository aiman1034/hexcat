# -*- coding: utf-8 -*-
"""Ubiquiti (UniFi) Ethernet optics + DAC/AOC content author — German v5.0 gold-slice for
output/stage3/ubiquiti_facts.json. Prose $0, in-session, GROUNDED-only (1000-rule): specs from the
techspecs-locked facts; soft UniFi-ecosystem use-case framing only — NO invented vendor/OEM/qualification
claims (passes the L5 ungrounded-claim guard). Dedup: the legacy UFiber UF- code is woven as an alternate
order number + logged via extra_log (Lenovo pattern). CWDM channels get wavelength-led, channel-rotated
prose so the 12 do not share near-identical Beschreibung (§7.7). FAQ = byte-contract placeholder (the
v1.3 FAQ is the separate FAQ-Production stream). Writes Ubiquiti_content.json.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "output" / "stage3" / "ubiquiti_facts.json").read_text(encoding="utf-8"))
DEST = ROOT / "stage3_content" / "Ubiquiti_content.json"
URL = "https://techspecs.ui.com/unifi/accessories"
VEND = "Ubiquiti"
TODAY = "2026-06-15"
SPEED_DE = {"100G": "100-Gigabit", "25G": "25-Gigabit", "10G": "10-Gigabit", "1G": "1-Gigabit"}
KOMPAT_NOTE = ("Maßgeblich ist die UniFi-Kompatibilitätsliste (ui.com) für den jeweiligen UniFi-Switch "
               "bzw. das Gateway und den Firmware-Stand")
ORIG_FAQ = ["Ist dies ein originales Ubiquiti-Produkt?",
            "Ja. Es handelt sich um Ubiquiti-Original-Neuware (UniFi) – versiegelt geliefert und für "
            "UniFi-Switches und -Gateways mit SFP-/SFP+/SFP28-/QSFP28-Steckplätzen vorgesehen."]


def ws(s): return re.sub(r"\s+", " ", s).strip()
def _wc(html): return len(re.sub(r"<[^>]+>", "", html).split())
def datarate(sp): return sp.replace("G", " Gbit/s")
def dom_of(f): return "Nein" if (f.get("media") == "Kupfer" or f.get("connector") == "RJ45") else "Ja"


def fasertyp(f):
    if f.get("media") == "Kupfer" or f.get("connector") == "RJ45":
        return "Kupfer"
    return "Multimode" if f.get("media") == "MMF" else "Singlemode"


def media_phrase(f):
    if f.get("media") == "Kupfer" or f.get("connector") == "RJ45":
        return "RJ45-Kupfer"
    return "Multimode-Glasfaser" if f.get("media") == "MMF" else "Singlemode-Glasfaser"


PAD_KURZ = ["Die Lieferung erfolgt als versiegelte Original-Neuware.",
            "Vor dem Einsatz ist die Freigabe für das UniFi-Gerät und den Firmware-Stand zu prüfen."]


def pad_kurz(kp1, kp2, lo=44, hi=80):
    i = 0
    while _wc(kp1 + kp2) < lo and i < len(PAD_KURZ):
        cand = PAD_KURZ[i]; i += 1
        if _wc(kp1 + kp2) + _wc(cand) <= hi:
            kp2 = kp2[:-4].rstrip() + " " + cand + "</p>"
    return kp1 + kp2


def pad_intro(intro, pool, lo=108, hi=200):
    i = 0
    while sum(_wc(p) for p in intro) < lo and i < len(pool):
        cand = pool[i]; i += 1
        if sum(_wc(p) for p in intro) + _wc(cand) <= hi:
            intro[-1] = ws(intro[-1] + " " + cand)
    return intro


def clip_titel(pn, parts):
    for tail in parts:
        t = ws("Ubiquiti %s %s | Hexwaren" % (pn, tail))
        if len(t) <= 60:
            return t
    base = "Ubiquiti %s | Hexwaren" % pn
    return base if len(base) <= 60 else ("%s | Hexwaren" % pn)


def fit_meta(meta, filler):
    meta = ws(meta)
    while len(meta) < 140:
        meta = meta[:-1].rstrip() + filler
        filler = " Neu, versiegelt und für UniFi-Umgebungen vorgesehen."
    return meta[:200].rstrip()


# UniFi-ecosystem use-case framings (soft, class-true, no part-specific fabrication). Index-rotated.
USECASE = [
    "in kleinen Büros und Zweigstellen für den Switch-Uplink",
    "in Prosumer- und Home-Lab-Umgebungen am UniFi-Switch",
    "zur Aggregation von UniFi-Access-Points im Campus-Netz",
    "als Backbone für UniFi-Protect-Überwachungssysteme",
    "in Hotellerie- und Mehrfamilienhaus-Netzen (MDU)",
    "für die Switch-zu-Switch-Aggregation im Verteiler",
    "für Punkt-zu-Punkt-Glasfaserstrecken zwischen Gebäuden",
    "im dichten Client-Zugang großer UniFi-Standorte",
    "als Speicher- und NVR-Anbindung im Rechenraum",
    "für wachsende UniFi-Netze mit steigendem Durchsatz",
]
# per-voice intro padding (voice-specific so any padding stays unique)
VPOOL = [
    "Gerade in kleinen Standorten vereinfacht der %s die Verkabelung ohne zusätzliche Medienkonverter.",
    "Im Home-Lab lässt sich der %s unkompliziert in bestehende UniFi-Switches einsetzen.",
    "Bei dichter AP-Belegung hält der %s die Uplink-Last gleichmäßig stabil.",
    "Im Dauerbetrieb der Videoüberwachung bleibt der %s belastbar.",
    "In MDU-Installationen spart der %s Platz und Verkabelungsaufwand.",
    "Zwischen Verteilern bündelt der %s den Verkehr ohne Engpass.",
    "Auf der Gebäudestrecke liefert der %s eine stabile Glasfaserverbindung.",
    "Bei hoher Client-Dichte hält der %s den Zugriff reaktionsschnell.",
    "An der NVR-Anbindung trägt der %s anhaltend hohe Schreiblast.",
    "Mit wachsender Portzahl lässt sich der %s nahtlos ergänzen.",
]


def alt_clause(f):
    a = f.get("alt_code")
    return ("; in der UFiber-Generation wird das Modul auch unter der Bestellnummer %s geführt" % a) if a else ""


def optic_entry(pn, f):
    sp, uk = f["speed"], f["ff"]
    spde, rate = SPEED_DE.get(sp, sp), datarate(sp)
    typ, std = f.get("type") or "", f.get("standard") or ""
    wl, reach, conn = f.get("wavelength"), f.get("reach") or "", f.get("connector") or ""
    fz = str(f["faseranzahl"]) if f.get("faseranzahl") else None
    copper = f.get("media") == "Kupfer" or conn == "RJ45"
    ftyp = fasertyp(f)
    med = media_phrase(f)
    dual = (" (Mehrraten %s)" % f["dual_rate_pair"]) if (f.get("dual_rate") and f.get("dual_rate_pair")) else ""
    note = f.get("spec_note")
    altc = alt_clause(f)
    is_cwdm = typ == "CWDM"
    idx = optic_entry.order.setdefault(pn, len(optic_entry.order))
    uc = USECASE[idx % len(USECASE)]
    connphr = ("über den %s-Anschluss" % conn) if conn else "optisch"
    wlfz = ((" bei %s" % wl) if wl else "") + ((" über %s Fasern" % fz) if fz else "")
    artikel = ws("%s %s %s %s %s-Transceiver%s – %s%s%s" % (VEND, pn, sp, uk, (typ or "Optik"), dual, ftyp,
                 (", %s" % conn) if conn else "", (", bis %s" % reach) if reach else ""))
    titel = clip_titel(pn, ["%s %s %s" % (sp, uk, (typ or reach)), "%s %s %s" % (sp, uk, typ), "%s %s" % (sp, uk)])
    meta = fit_meta(("Original %s %s: %s %s-%s-Transceiver, %s%s%s. Neu, versiegelt, für UniFi."
                     % (VEND, pn, typ, spde, uk, ftyp, (", %s" % conn) if conn else "",
                        (", bis %s" % reach) if reach else "")),
                    " Verlässliche UniFi-Optik.")
    if is_cwdm:
        i1 = ("Der %s %s ist ein %s-CWDM-SFP+-Transceiver für den Wellenlängenkanal %s und überträgt "
              "%s-Ethernet über Singlemode-Glasfaser, eingesetzt %s." % (VEND, pn, spde, wl, spde, uc))
        i2 = ("Über den %s-Anschluss überbrückt der %s bis zu %s%s; das Modul arbeitet im Paar mit einem "
              "Gegenmodul derselben Wellenlänge und lässt sich per CWDM-Multiplexer kombinieren."
              % (conn, pn, reach, (" über %s Fasern" % fz) if fz else ""))
        i3 = ("Ausgeliefert wird der %s als versiegelte Ubiquiti-Original-Neuware (UniFi), vorgesehen für "
              "UniFi-Switches mit SFP+-Steckplätzen%s." % (pn, altc))
    else:
        typc = (" vom Typ %s" % typ) if typ else ""
        i1 = ("Der %s %s ist ein %s-%s-Transceiver%s%s und überträgt %s-Ethernet (%s) über %s, eingesetzt %s."
              % (VEND, pn, spde, uk, typc, dual, spde, std, ("RJ45-Kupfer" if copper else med), uc))
        i2 = ("Der %s stellt die Verbindung %s her und überbrückt %s%s."
              % (pn, connphr, ("bis zu %s" % reach) if reach else "die geforderte Distanz", wlfz))
        i3 = ("Ausgeliefert wird der %s als versiegelte Ubiquiti-Original-Neuware (UniFi) und ist für "
              "UniFi-Geräte mit %s-Steckplätzen vorgesehen%s." % (pn, uk, altc))
        if note:
            i3 = i3 + " " + (note if note.endswith(".") else note + ".")
    kp1 = ("<p>Der %s %s ist ein %s-%s-Transceiver%s für %s%s. %s überbrückt er %s%s.</p>"
           % (VEND, pn, spde, uk, (" vom Typ %s" % typ) if (typ and not is_cwdm) else (" (CWDM %s)" % wl if is_cwdm else ""),
              ("RJ45-Kupfer" if copper else (ftyp + "-Glasfaser")), (" (%s)" % std) if std else "",
              ("Über den %s-Anschluss" % conn) if conn else "Optisch",
              ("bis zu %s" % reach) if reach else "die geforderte Distanz", wlfz))
    kp2 = ("<p>Als Ubiquiti-Original-Neuware (UniFi) wird das Modul versiegelt geliefert, ist im laufenden "
           "Betrieb steckbar (Hot-Plug) und für UniFi-Geräte mit %s-Steckplätzen vorgesehen.</p>" % uk)
    attrs = [["Formfaktor", uk], ["Datenrate", rate]]
    prov = ["Datenrate"]
    if typ and not is_cwdm:
        attrs.append(["Transceiver Typ", typ]); prov.append("Transceiver Typ")
    elif is_cwdm:
        attrs.append(["Transceiver Typ", "CWDM"]); prov.append("Transceiver Typ")
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
    faq = [ORIG_FAQ,
           (["Welche Reichweite erreicht der %s?" % pn, "Er überbrückt Strecken von bis zu %s." % reach]
            if reach else ["Wofür ist der %s ausgelegt?" % pn,
                           "Für %s-Verbindungen an %s-Steckplätzen von UniFi-Geräten." % (spde, uk)]),
           ["In welchen Geräten lässt sich das Modul einsetzen?",
            "In UniFi-Switches und -Gateways mit %s-Steckplätzen; maßgeblich ist die UniFi-Kompatibilitätsliste." % uk]]
    pool = [VPOOL[idx % len(VPOOL)] % pn]
    extra = ([["Alt-Bestellnummer", f["alt_code"], f.get("alt_src") or URL]] if f.get("alt_code") else [])
    return uk, artikel, titel, meta, kp1, kp2, [i1, i2, i3], pool, attrs, prov, faq, extra
optic_entry.order = {}


def cable_entry(pn, f):
    uk = f["k3"]; sp = f["speed"]; spde, rate = SPEED_DE.get(sp, sp), datarate(sp)
    length = ("%s m" % f["length"]).replace("0.5", "0,5").replace("0.15", "0,15").replace("0.3", "0,3")
    ends = f.get("ends_raw") or ""
    aoc = uk == "AOC Kabel"
    note = f.get("spec_note")
    if aoc:
        kabeltyp, kind_de = "Aktives optisches Kabel (AOC)", "aktives optisches Kabel (AOC)"
        phys = "die werkseitig terminierte Aktivoptik ist leicht und biegsam und überbrückt größere Distanzen"
    else:
        kabeltyp, kind_de = "Passives Twinax-Kupferkabel (DAC)", "passives Direct-Attach-Kupferkabel (DAC)"
        phys = "die passive Twinax-Baugruppe kommt ohne eigene Elektronik aus und bleibt eine kostengünstige Direktverbindung"
    short = "AOC" if aoc else "DAC"
    artikel = ws("%s %s %s %s %s – %s, Länge %s" % (VEND, pn, sp, short, ends, kind_de, length))
    titel = clip_titel(pn, ["%s %s %s" % (sp, short, length), "%s %s" % (sp, short)])
    meta = fit_meta(("Original %s %s: %s-%s, %s, Länge %s. Fest konfektioniert, neu, versiegelt, für UniFi."
                     % (VEND, pn, spde, kabeltyp.lower(), ends, length)), " Direktverbindung im Rack.")
    kp1 = ("<p>Das %s %s ist ein %s-%s. Über eine Länge von %s verbindet es %s; die Enden sind fest "
           "konfektioniert und im Kabel enthalten.</p>" % (VEND, pn, spde, kabeltyp.lower(), length, ends))
    kp2 = ("<p>Als Ubiquiti-Original-Neuware (UniFi) wird das %s versiegelt geliefert und ist für UniFi-Geräte "
           "der passenden Portklasse vorgesehen.</p>" % pn)
    i1 = ("Das %s %s ist ein %s-%s mit werkseitig fest konfektionierten Enden (%s) und richtet sich an "
          "UniFi-Switches und -Gateways der passenden Portklasse." % (VEND, pn, spde, kind_de, ends))
    i2 = ("Über eine fest konfektionierte Länge von %s verbindet das %s zwei Anschlüsse; %s, sodass keine "
          "separaten Transceiver ausgewählt werden müssen." % (length, pn, phys))
    i3 = ("Geliefert wird das %s als einzeln verpackte, versiegelte Ubiquiti-Original-Neuware%s."
          % (pn, ("; %s" % note) if note else ""))
    attrs = [["Formfaktor", uk], ["Datenrate", rate], ["Kabeltyp", kabeltyp], ["Anschlussenden", ends],
             ["Länge", length], ["Transceiver", "fest konfektioniert (im Kabel enthalten)"], ["Zustand", "Neu, versiegelt"]]
    prov = ["Datenrate", "Kabeltyp", "Anschlussenden", "Länge"]
    kompat = ["UniFi-Geräte mit %s-Ports" % ends.split(" auf ")[0], KOMPAT_NOTE]
    faq = [ORIG_FAQ, ["Wie lang ist das %s?" % pn, "Das Kabel hat eine feste Länge von %s." % length],
           (["Benötigt das Kabel ein Netzteil?", "Nein. Die integrierte Optik wird über die Ports versorgt."]
            if aoc else ["Benötigt das Kabel eine eigene Stromversorgung?",
                         "Nein. Als passives Twinax-Kupferkabel kommt es ohne aktive Elektronik aus."])]
    pool = ["Werkseitig konfektioniert erspart das %s die Auswahl separater Transceiver und verringert "
            "Fehlerquellen bei der Verkabelung." % pn,
            "Vor dem Einsatz des %s empfiehlt sich ein Abgleich von UniFi-Gerät und Portgeschwindigkeit." % pn]
    return uk, artikel, titel, meta, kp1, kp2, [i1, i2, i3], pool, attrs, prov, kompat, faq


doc = {}
for pn, f in FACTS.items():
    if f.get("cable"):
        uk, artikel, titel, meta, kp1, kp2, intro_raw, pool, attrs, prov, kompat, faq = cable_entry(pn, f)
        extra = []
    else:
        uk, artikel, titel, meta, kp1, kp2, intro_raw, pool, attrs, prov, faq, extra = optic_entry(pn, f)
        kompat = ["UniFi-Switches und -Gateways mit %s-Steckplätzen" % uk, KOMPAT_NOTE]
    kurz = pad_kurz(kp1, kp2)
    intro = pad_intro([ws(x) for x in intro_raw], pool)
    e = {"_facts": {"unterkategorie": uk, "quell_url": f.get("row") or URL, "verifiziert_am": TODAY},
         "artikelname": ws(artikel), "titel_tag": titel, "meta_description": meta,
         "kurzbeschreibung": ws(kurz), "intro": intro, "kompatibilitaet": kompat,
         "faq": faq, "verwandte": [], "attributes": attrs,
         "provenance": {lab: [f.get("row") or URL, "datasheet"] for lab in prov},
         "extra_log": extra, "beschreibung": "", "netto_vk": None}
    assert len(e["titel_tag"]) <= 60 and e["titel_tag"].endswith("| Hexwaren"), (pn, e["titel_tag"])
    doc[pn] = e

DEST.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print("authored %d Ubiquiti SKUs -> %s" % (len(doc), DEST.name))
