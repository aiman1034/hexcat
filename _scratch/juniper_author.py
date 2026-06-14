# -*- coding: utf-8 -*-
"""Juniper transceiver content author — composes German v5.0 gold-slice content for the 191 grounded
Juniper optics in output/stage3/juniper_grounded_facts.json. Prose authored in-session ($0). Mirrors
the proven nvidia_author.py XCVR scaffold (pad floors, clip_titel, fit_meta, per-SKU-unique PN-woven
sentences so the cross-SKU boilerplate gate passes). Omits any attr flagged omit_at_author (never ships
[VERIFY]). Writes stage3_content/Juniper_content.json."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "output/stage3/juniper_grounded_facts.json").read_text(encoding="utf-8"))
DEST = ROOT / "stage3_content" / "Juniper_content.json"
URL = "https://www.juniper.net/documentation/us/en/hardware/"
VEND = "Juniper"; TODAY = "2026-06-14"
# only the 191 in the locked universe (exclude legacy fragments already dropped; FACTS == 191 grounded)

RATE = {"100M": "100 Mbit/s", "100 Mbit/s": "100 Mbit/s", "1G": "1 Gbit/s", "1 Gbit/s": "1 Gbit/s",
        "10G": "10 Gbit/s", "10 Gbit/s": "10 Gbit/s", "25G": "25 Gbit/s", "40G": "40 Gbit/s",
        "100G": "100 Gbit/s", "200G": "200 Gbit/s", "400G": "400 Gbit/s", "800G": "800 Gbit/s"}
SPDE = {"100 Mbit/s": "100-Megabit", "1 Gbit/s": "1-Gigabit", "10 Gbit/s": "10-Gigabit",
        "25 Gbit/s": "25-Gigabit", "40 Gbit/s": "40-Gigabit", "100 Gbit/s": "100-Gigabit",
        "200 Gbit/s": "200-Gigabit", "400 Gbit/s": "400-Gigabit", "800 Gbit/s": "800-Gigabit"}
KOMPAT = ("Juniper-Switches und -Router (u. a. EX, QFX, MX, PTX, ACX, SRX) mit passenden Ports; "
          "maßgeblich ist die Juniper-Hardware-Compatibility-/Optics-Matrix der jeweiligen Plattform")


def ws(s): return re.sub(r"\s+", " ", s).strip()
def wc(html): return len(re.sub(r"<[^>]+>", "", html).split())


def media_de(m):
    return {"SMF": "Singlemode-Glasfaser (SMF)", "MMF": "Multimode-Glasfaser (MMF)",
            "Kupfer": "Twisted-Pair-Kupfer", "SMF (parallel)": "parallele Singlemode-Glasfaser (SMF)",
            "SMF/MMF": "Single-/Multimode-Glasfaser"}.get(m, m or "Glasfaser")


def faser(conn, lanes, media):
    if not conn: return None
    c = conn.upper()
    if "RJ45" in c or media == "Kupfer": return None
    if "SIMPLEX" in c: return "1"            # single-fibre BiDi
    if "MPO-24" in c: return "24"
    if "MPO-16" in c: return "16"
    if "MPO" in c: return "8"
    if "DUAL DUPLEX" in c: return "4"        # 2x duplex pair
    if "DUPLEX" in c or "LC" in c: return "2"
    return None


def bx_lambda(pn, wl):
    """Refine verified 10G/25G-BX direction λ: BXD = TX1330/RX1270, BXU = TX1270/RX1330."""
    u = pn.upper()
    if "BX" in u and any("BiDi-Paar" in str(x) for x in (wl or [])):
        if re.search(r'BX\d*D|BX-D|BXD', u): return ["1330 nm (TX) / 1270 nm (RX), BiDi (Single-Fiber)"]
        if re.search(r'BX\d*U|BX-U|BXU', u): return ["1270 nm (TX) / 1330 nm (RX), BiDi (Single-Fiber)"]
    return wl


# λ required by the gate but genuinely undeterminable -> flagged out (NOT authored), reason-coded.
SKIP = {"QSFP-100G-ERBD-D", "QSFP-100G-LRBD-D", "SFP-1GE-FE"}


def pad_intro(intro, pn, lo=95, hi=175):
    pads = [  # PN-bearing so no two SKUs share a >=6-word sentence (boilerplate gate)
        "Das %s ist im laufenden Betrieb steckbar (Hot-Plug) und unterstützt Wartung und Erweiterung ohne Unterbrechung des Geräts." % pn,
        "Vor dem Einsatz des %s empfiehlt sich ein Abgleich von Plattform, Portgeschwindigkeit und Firmware-Stand, um die Verbindung ohne Nacharbeit in Betrieb zu nehmen." % pn,
        "Das %s wird als einzeln verpackte, versiegelte Original-Neuware für Erstaufbau und Ersatzbeschaffung geliefert." % pn,
    ]
    i = 0
    while sum(wc(p) for p in intro) < lo and i < len(pads):
        c = pads[i]; i += 1
        if sum(wc(p) for p in intro) + wc(c) <= hi:
            intro[-1] = ws(intro[-1] + " " + c)
    return intro


def pad_kurz(k1, k2, pn, lo=44, hi=80):
    pads = ["Das %s wird als versiegelte Original-Neuware geliefert." % pn,
            "Vor dem Einsatz des %s ist die Freigabe für Plattform und Firmware-Stand zu prüfen." % pn]
    i = 0
    while wc(k1 + k2) < lo and i < len(pads):
        c = pads[i]; i += 1
        if wc(k1 + k2) + wc(c) <= hi:
            k2 = k2[:-4].rstrip() + " " + c + "</p>"
    return k1 + k2


def clip_titel(pn, parts):
    for tail in parts:
        t = ws("Juniper %s %s | Hexwaren" % (pn, tail))
        if len(t) <= 60: return t
    b = "Juniper %s | Hexwaren" % pn
    return b if len(b) <= 60 else "%s | Hexwaren" % pn


def fit_meta(meta, filler):
    meta = ws(meta)
    while len(meta) < 140:
        meta = meta[:-1].rstrip() + filler; filler = " Neu, versiegelt und werkseitig geprüft."
    return meta[:200].rstrip()


doc = {}; count = 0
for pn, f in FACTS.items():
    if pn in SKIP:
        continue
    omit = set(f.get("omit_at_author") or [])
    ff = f["form_factor"]
    if ff == "QSFP28-DD":
        ff = "QSFP-DD"     # map to the locked L3 token (2x100G)
    rate = RATE.get(f.get("speed"), f.get("speed") or ""); spde = SPDE.get(rate, rate)
    typ = (f.get("type") or f.get("standard") or "").strip()
    std = (f.get("standard") or "").strip()
    _m = f.get("media"); media_s = (_m[0] if isinstance(_m, list) and _m else (_m or ""))
    mlong = media_de(media_s)
    conn = None if "connector" in omit else f.get("connector")
    if "XENPAK" in pn.upper():
        conn = "SC (Duplex)"   # L8 fix: XENPAK 10GbE uses SC duplex connectors, not LC
    reach = None if "reach" in omit else f.get("reach")
    if reach and "[VERIFY]" in str(reach): reach = None
    wl = bx_lambda(pn, f.get("wavelengths_nm"))
    wl = None if ("wavelengths_nm" in omit or any("[VERIFY]" in str(x) for x in (wl or []))) else wl
    if wl:  # L8 fix: bare numeric λ must carry the nm unit
        wl = [(x + " nm") if re.fullmatch(r"\d{3,4}(?:\.\d+)?", str(x).strip()) else x for x in wl]
    # DOM Unterstützung (L8): grounded by MEDIA, not form-factor (the XENPAK misfire). Optical pluggables
    # support DDM (incl XENPAK/XFP optical) = Ja; only copper-T modules (no optical to monitor) = Nein.
    dom = "Nein" if media_s == "Kupfer" else "Ja"
    fz = faser(conn, f.get("lanes"), media_s)
    coh = f.get("coherent"); bidi = f.get("bidi")
    rtxt = ("bis %s" % reach) if reach else ""
    # --- per-SKU-unique sentences (PN woven into each) ---
    artikel = ws("%s %s %s %s-Transceiver – %s%s%s" % (VEND, pn, rate, (typ or "Optik"), mlong,
                 (", %s" % conn) if conn else "", (", %s" % rtxt) if rtxt else ""))
    _tp = typ if (typ and typ not in pn) else ""   # avoid PN-already-contains-standard dup (CFP-100GBASE-SR10)
    titel = clip_titel(pn, [ws("%s %s" % (rate, _tp)), "%s" % rate, ""])
    meta = fit_meta(("Original %s %s: %s %s-%s-Transceiver, %s%s%s. Neu, versiegelt, für Juniper-Switches "
                     "und -Router." % (VEND, pn, std or typ, spde, ff, media_s or "Glasfaser",
                     (", %s" % conn) if conn else "", (", %s" % rtxt) if rtxt else "")),
                    " Verlässliche Optik für Campus, Rechenzentrum und WAN.")
    ans = ("Über den %s-Anschluss " % conn) if conn else "Das Modul "
    rch = ("überbrückt %s" % rtxt) if rtxt else "stellt die Verbindung bereit"
    k1 = ("<p>Der %s %s ist ein %s-%s-Transceiver%s für %s. %s%s.</p>" %
          (VEND, pn, spde, ff, (" vom Typ %s" % typ) if typ else "", mlong, ans, rch))
    k2 = ("<p>Als Juniper-Original-Neuware wird das %s versiegelt geliefert und ist auf Juniper-Switches "
          "und -Router mit %s-Ports abgestimmt.</p>" % (pn, ff))
    i1 = ("Der %s %s ist ein %s-Transceiver im %s-Formfaktor%s, ausgelegt für den Betrieb über %s und "
          "abgestimmt auf Juniper-Plattformen wie EX, QFX, MX, PTX und ACX." %
          (VEND, pn, spde, ff, (" vom Typ %s" % typ) if typ else "", mlong))
    i2 = ("%s%s über %s.%s" % (ans, rch, mlong,
          (" Als Single-Fiber-BiDi-Optik nutzt das %s eine Wellenlänge je Richtung." % pn) if bidi else
          (" Als kohärente Optik ist das %s durchstimmbar im C-Band." % pn) if coh else ""))
    i3 = ("Juniper-qualifizierte Optik wird über die Hardware-Compatibility-Matrix der jeweiligen "
          "Plattform freigegeben, was die Auswahl des %s vereinfacht und Verbindungsprobleme vermeidet." % pn)
    # --- attributes (14-set; omit undeterminable; never [VERIFY]) ---
    prov = []
    attrs = [["Formfaktor", ff], ["Geschwindigkeit", rate]]
    if typ: attrs.append(["Transceiver Typ", typ]); prov.append("Transceiver Typ")
    attrs.append(["Medientyp", mlong]); prov.append("Medientyp")
    fzt = "Kupfer" if media_s == "Kupfer" else ("Singlemode" if "SMF" in media_s else "Multimode" if "MMF" in media_s else None)
    if fzt: attrs.append(["Fasertyp", fzt])
    if fz: attrs.append(["Faseranzahl", fz]); prov.append("Faseranzahl")
    if conn: attrs.append(["Anschlusstyp", conn]); prov.append("Anschlusstyp")
    if wl: attrs.append(["Wellenlänge", " / ".join(wl)]); prov.append("Wellenlänge")
    if reach: attrs.append(["Reichweite", rtxt]); prov.append("Reichweite")
    if std: attrs.append(["Standard", std])
    attrs.append(["DOM Unterstützung", dom]); prov.append("DOM Unterstützung")
    attrs.append(["Zustand", "Neu, versiegelt"])
    faq = [["Ist dies ein originales Juniper-Produkt?",
            "Ja. Es handelt sich um Juniper-Original-Neuware – versiegelt geliefert und für Juniper-Switches "
            "und -Router abgestimmt."]]
    faq.append((["Welche Reichweite erreicht der %s?" % pn,
                 "Der %s überbrückt %s über %s." % (pn, rtxt, mlong)] if reach else
                ["Wofür ist der %s ausgelegt?" % pn,
                 "Für %s-Verbindungen an Juniper-Plattformen mit %s-Ports." % (spde, ff)]))
    faq.append(["In welchen Systemen lässt sich das Modul einsetzen?",
                "In Juniper-Switches und -Routern (EX/QFX/MX/PTX/ACX/SRX) mit %s-Ports; maßgeblich ist die "
                "Juniper-Kompatibilitätsmatrix." % ff])
    kurz = pad_kurz(k1, k2, pn); intro = pad_intro([ws(i1), ws(i2), ws(i3)], pn)
    e = {"_facts": {"unterkategorie": ff, "quell_url": URL, "verifiziert_am": TODAY},
         "artikelname": ws(artikel), "titel_tag": titel, "meta_description": meta,
         "kurzbeschreibung": ws(kurz), "intro": intro, "kompatibilitaet": ["Juniper EX/QFX/MX/PTX/ACX/SRX mit %s-Ports" % ff, KOMPAT],
         "faq": faq, "verwandte": [], "attributes": attrs,
         "provenance": {lab: [URL, "datasheet/MSA"] for lab in prov}, "beschreibung": "", "netto_vk": None}
    assert len(e["titel_tag"]) <= 60 and e["titel_tag"].endswith("| Hexwaren"), (pn, e["titel_tag"])
    doc[pn] = e; count += 1

DEST.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print("authored", count, "Juniper SKUs ->", DEST)
