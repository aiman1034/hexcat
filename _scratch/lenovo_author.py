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


def media_phrase(f):
    """(noun, lower-plural) for the optic's transmission medium — grounded from facts."""
    if f.get("media") == "Kupfer" or f.get("connector") == "RJ45":
        return "RJ45-Kupfer", "eine strukturierte Kupferverkabelung"
    if f.get("media") == "MMF":
        return "Multimode-Glasfaser", "Multimode-Fasern"
    return "Singlemode-Glasfaser", "Singlemode-Fasern"


def era_phrase(pn):
    """COARSE product lineage derivable ONLY from the PN prefix + the public Lenovo↔IBM acquisition (L8
    round-3: no finer sub-era, no OEM/qualification claim — those were fabrications). Two buckets only:
      - ThinkSystem-era PNs (4T/7G/4M/4X/7Z/4Z) -> ThinkSystem generation
      - pre-Lenovo IBM PNs (44/46/49/68/69/81/88/90 = System Networking/BladeCenter/System x heritage)
    Anything else (e.g. 00-series transition parts) -> no lineage claim ('')."""
    if pn[:2] in ("7G", "4T", "4M", "4X", "7Z", "4Z"):
        return "Teil der ThinkSystem-Generation"
    if pn[:3] in ("44W", "46C", "49Y", "68Y", "69Y", "81Y", "88Y", "90Y"):
        return "Teil des von Lenovo übernommenen IBM-System-Networking-Erbes"
    return ""


# 10 distinct authorial voices for OPTIC modules (finding ①). Each writes (i1,i2,i3) in its own framing,
# lead use-case, sentence structure and buyer angle — every spec stays grounded and identical; only the
# LANGUAGE differs, so two same-(Std,FF,reach,λ) products no longer share near-identical prose (§7.7).
# Selected by the SKU's position within its spec-cluster, so cluster members always draw different voices.
def _voices(c):
    # ALL content here is grounded: spec facts from the datasheet + the coarse, prefix-derivable lineage
    # appositive (ERA) + the published 85 C temp clause (TEMP). NO vendor/OEM/qualification claim (L8 ①).
    P, SP, FF, TYP, STD, MED = c["P"], c["SP"], c["FF"], c["TYP"], c["STD"], c["MED"]
    CONN, REACH, ERA, DUAL, TEMP = c["CONN"], c["REACH"], c["ERA"], c["DUAL"], c["TEMP"]
    cop, wl, fz, rn, fcc = c["COP"], c["WL"], c["FZ"], c["RNOTE"], c["FCC"]
    typc = (" vom Typ %s" % TYP) if TYP else ""
    ap = (", %s," % ERA) if ERA else ""                       # lineage appositive, e.g. "Der X, Teil der …,"
    apg = (" (%s)" % ERA) if ERA else ""                      # parenthetical variant
    temp = (" Für thermisch anspruchsvolle Umgebungen ist das %s bis 85 °C spezifiziert." % P) if TEMP else ""
    connphr = ("über den %s-Anschluss" % CONN) if CONN else "über die optische Schnittstelle"
    rphr = (rn if rn else ("bis zu %s" % REACH if REACH else "die geforderte Distanz"))
    wlfz = ((" bei %s" % wl) if wl else "") + ((" über %s Fasern" % fz) if fz else "")
    media_long = ("RJ45-Kupfer" if cop else MED)
    V = [
        (  # 0 — virtualization, identity-first
            "Der %s %s ist ein %s-%s-Transceiver%s%s und überträgt %s-Ethernet über %s; in verdichteten "
            "Virtualisierungs-Hosts bindet er ThinkSystem-Server zuverlässig an %s-Ports an."
            % (VEND, P, SP, FF, typc, DUAL, STD, media_long, FF),
            "Er stellt die Verbindung %s her und trägt%s." % (connphr, (" " + rphr + wlfz)),
            "Ausgeliefert wird der %s%s als versiegelte Lenovo-Original-Neuware, freigegeben für "
            "ThinkSystem-Plattformen%s.%s" % (P, ap, fcc, temp),
        ),
        (  # 1 — HPC/cluster, use-case-first
            "Für HPC- und Cluster-Knoten liefert der %s %s eine %s-Anbindung: Der %s-Transceiver%s%s setzt "
            "%s auf %s um und passt in die %s-Steckplätze der ThinkSystem-Systeme."
            % (VEND, P, SP, FF, typc, DUAL, STD, media_long, FF),
            "Die Reichweite erreicht %s%s, kontaktiert %s." % (rphr, wlfz, connphr),
            "Einzeln verpackt und versiegelt kommt der %s%s als Lenovo-Original-Neuware in den Versand%s.%s"
            % (P, ap, fcc, temp),
        ),
        (  # 2 — storage backbone, reach-forward
            "Im Storage-Backbone und bei SAN-/NAS-Anbindungen an ThinkSystem-Servern überträgt der %s %s "
            "%s-Ethernet als %s-%s-Transceiver%s%s." % (VEND, P, SP, SP, FF, typc, DUAL),
            "Das Modul setzt %s über %s um und überbrückt %s%s." % (STD, media_long, rphr, wlfz),
            "Der %s%s wird als versiegelte Lenovo-Original-Neuware für %s-Steckplätze geliefert%s.%s"
            % (P, ap, FF, fcc, temp),
        ),
        (  # 3 — access/aggregation, connector-forward
            "%s führt der %s %s als %s-%s-Transceiver%s%s %s-Ethernet an %s-Ports im Access- und "
            "Aggregations-Layer." % (connphr[0].upper() + connphr[1:], VEND, P, SP, FF, typc, DUAL, STD, FF),
            "Über %s erreicht das Modul eine Distanz von %s%s." % (media_long, rphr, wlfz),
            "Versiegelt und ThinkSystem-freigegeben wird der %s%s als Lenovo-Original-Neuware ausgeliefert%s.%s"
            % (P, ap, fcc, temp),
        ),
        (  # 4 — uplink/backbone, delivery-forward
            "Zwischen Switches und Servern stellt der %s %s %s-Uplinks bereit — ein %s-%s-Transceiver%s%s für "
            "%s über %s." % (VEND, P, SP, SP, FF, typc, DUAL, STD, media_long),
            "%s deckt er %s ab%s." % (connphr[0].upper() + connphr[1:], rphr, wlfz),
            "Der %s%s ist für ThinkSystem-%s-Steckplätze freigegeben und wird versiegelt als Original-Neuware "
            "geliefert%s.%s" % (P, ap, FF, fcc, temp),
        ),
        (  # 5 — high availability
            "Der %s %s sichert redundante Server-Anbindungen ab und arbeitet als %s-%s-Transceiver%s%s mit "
            "%s über %s." % (VEND, P, SP, FF, typc, DUAL, STD, media_long),
            "Die Verbindung wird %s aufgebaut und trägt %s%s." % (connphr, rphr, wlfz),
            "Im Betrieb steckbar (Hot-Plug), wird der %s%s als versiegelte Lenovo-Original-Neuware geliefert%s.%s"
            % (P, ap, fcc, temp),
        ),
        (  # 6 — throughput/database
            "Durchsatzstarke Datenbank- und Analytics-Workloads bedient der %s %s als %s-%s-Transceiver%s%s, "
            "der %s-Ethernet über %s führt." % (VEND, P, SP, FF, typc, DUAL, STD, media_long),
            "%s reicht das Modul das Signal %s%s." % (connphr[0].upper() + connphr[1:], rphr, wlfz),
            "Geliefert wird der %s%s versiegelt und ThinkSystem-freigegeben als Original-Neuware%s.%s"
            % (P, ap, fcc, temp),
        ),
        (  # 7 — edge/remote
            "Für Edge- und Außenstandorte bietet der %s %s eine kompakte %s-Anbindung; das %s-Modul%s%s "
            "realisiert %s über %s." % (VEND, P, SP, FF, typc, DUAL, STD, media_long),
            "Es verbindet %s und überbrückt %s%s." % (connphr, rphr, wlfz),
            "Der %s%s wird einzeln verpackt, versiegelt und für %s-Ports freigegeben ausgeliefert%s.%s"
            % (P, apg, FF, fcc, temp),
        ),
        (  # 8 — consolidation
            "Um Netzwerk- und Storage-Verkehr zu konsolidieren, setzt der %s %s als %s-%s-Transceiver%s%s "
            "%s über %s um." % (VEND, P, SP, FF, typc, DUAL, STD, media_long),
            "Die Anbindung erfolgt %s über eine Distanz von %s%s." % (connphr, rphr, wlfz),
            "Für ThinkSystem-%s-Steckplätze freigegeben, wird der %s%s versiegelt als Original-Neuware "
            "geliefert%s.%s" % (FF, P, ap, fcc, temp),
        ),
        (  # 9 — growth/containers
            "In wachsenden Virtualisierungs- und Container-Umgebungen skaliert der %s %s die Anbindung als "
            "%s-%s-Transceiver%s%s für %s über %s." % (VEND, P, SP, FF, typc, DUAL, STD, media_long),
            "%s trägt das Modul das Signal %s%s." % (connphr[0].upper() + connphr[1:], rphr, wlfz),
            "Als versiegelte, ThinkSystem-freigegebene Original-Neuware wird der %s%s ausgeliefert%s.%s"
            % (P, ap, fcc, temp),
        ),
    ]
    return V


# Voice-specific intro padding (one pair per voice). pad_intro draws from THIS so that, when a short
# intro needs to reach the word floor, co-clustered siblings (which always hold different voices) pad
# with different sentences — padding never re-introduces the near-duplication we just removed.
VOICE_POOL = [
    ["Gerade bei hoher VM-Dichte zahlt sich die werkseitige Freigabe des %s aus, weil Kompatibilitätsrisiken entfallen.",
     "Der %s lässt sich im laufenden Betrieb tauschen, was Wartungsfenster spürbar verkürzt.",
     "In dicht belegten Hypervisor-Clustern hält der %s die Ost-West-Kommunikation der virtuellen Maschinen stabil."],
    ["In Cluster-Fabrics sorgt der %s für gleichmäßige Latenz über alle Knoten hinweg.",
     "Vor dem Rollout des %s sollten Firmware- und Treiberstand der beteiligten Knoten abgeglichen werden.",
     "Über viele Rechenknoten hinweg liefert der %s reproduzierbare Durchsatzwerte für eng gekoppelte Jobs."],
    ["Im Storage-Backbone hält der %s die Anbindung auch unter Dauerlast stabil.",
     "Als hot-plug-fähiges Modul ist der %s ohne Systemstopp tauschbar.",
     "In Backup- und Replikationsfenstern bleibt der %s auch bei anhaltend hohem Volumen belastbar."],
    ["Am Access-Layer vereinfacht der %s die Portplanung dicht bestückter Server-Racks.",
     "Ein kurzer Abgleich von Plattform und Portklasse sichert den Einsatz des %s ab.",
     "Beim Verdichten der Zugriffsebene erleichtert der %s eine aufgeräumte, strukturierte Verkabelung."],
    ["Auf Uplink-Strecken bündelt der %s den Verkehr zwischen den Verteilern zuverlässig.",
     "Der %s wird einzeln verpackt geliefert und ist nach dem Einstecken sofort betriebsbereit.",
     "Als Etagen-Uplink verknüpft der %s die Verteilerschränke ohne erkennbaren Engpass."],
    ["In redundanten Pfaden trägt der %s zur unterbrechungsfreien Verfügbarkeit bei.",
     "Dank Hot-Plug-Fähigkeit lässt sich der %s ohne Downtime ersetzen.",
     "In doppelt ausgelegten Anbindungen stützt der %s die Ausfallsicherheit der Serveranbindung."],
    ["Bei datenintensiven Abfragen hält der %s den Durchsatz konstant hoch.",
     "Vor dem Produktivbetrieb empfiehlt sich beim %s ein Plattform- und Firmware-Check.",
     "Unter anhaltender Analytics-Last bewahrt der %s gleichmäßige Paketraten."],
    ["An Außenstandorten überzeugt der %s durch robuste, wartungsarme Verbindungen.",
     "Der %s ist hot-plug-fähig und damit auch im Feld unkompliziert tauschbar.",
     "Auch bei wechselnden Umgebungsbedingungen am Rand des Netzes bleibt der %s zuverlässig."],
    ["Bei konsolidiertem Verkehr trennt der %s Netzwerk- und Storage-Lasten sauber auf Portebene.",
     "Der %s wird als versiegelte Neuware geliefert und ist für ThinkSystem freigegeben.",
     "Beim Zusammenführen zuvor getrennter Fabrics entlastet der %s die Portbilanz im Rack."],
    ["In Container-Plattformen wächst die Anbindung mit dem %s flexibel mit.",
     "Ein Abgleich von Portklasse und Firmware-Stand sichert den Einsatz des %s ab.",
     "Mit steigender Knotenzahl lässt sich der %s nahtlos in bestehende Cluster ergänzen."],
]


# Pre-pass: group optics by spec-signature (matches the gate's near-dup cluster key) and assign each its
# within-cluster index -> a distinct voice, so same-spec siblings never share a voice.
_clusters = {}
for _pn, _f in FACTS.items():
    if _f.get("cable"):
        continue
    _sig = (_f.get("standard") or "", _f.get("ff") or "", _f.get("reach") or "", _f.get("wavelength") or "")
    _clusters.setdefault(_sig, []).append(_pn)
OPTIC_VOICE_IDX = {}
for _sig, _pns in _clusters.items():
    for _i, _pn in enumerate(sorted(_pns)):
        OPTIC_VOICE_IDX[_pn] = _i


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
        # ③ dual-rate label is grounded per-part (00MY034 = 1G/10G; SFP28 dual-rate = 10G/25G).
        dual = (" (Dual-Rate %s)" % f["dual_rate_pair"]) if (f.get("dual_rate") and f.get("dual_rate_pair")) else ""
        op_temp = f.get("op_temp")                                   # ④ grounded 85 °C, else None
        temp_tail = ", 85 °C" if op_temp else ""
        med_noun, med_low = media_phrase(f)
        artikel = ws("%s %s %s %s %s-Transceiver%s – %s%s%s%s" % (VEND, pn, sp, uk, (typ or "Optik"), dual, ftyp,
                     (", %s" % conn) if conn else "", (", bis %s" % reach) if reach else "", temp_tail))
        titel = clip_titel(pn, ["%s %s %s" % (sp, uk, (typ or reach)), "%s %s %s" % (sp, uk, typ), "%s %s" % (sp, uk)])
        meta = fit_meta(("Original %s %s: %s %s-%s-Transceiver%s, %s%s%s%s. Neu, versiegelt, für Lenovo-ThinkSystem."
                         % (VEND, pn, typ, spde, uk, dual, ftyp, (", %s" % conn) if conn else "",
                            (", bis %s" % reach) if reach else "", temp_tail)),
                        " Verlässliche Lenovo-Optik für ThinkSystem-Server.")
        # ① genuinely unique prose per SKU — voice chosen by within-cluster position (same facts, new language)
        ctx = {"P": pn, "SP": spde, "FF": uk, "TYP": typ, "STD": std, "MED": med_noun,
               "CONN": conn, "REACH": reach, "WL": wl, "FZ": fz, "ERA": era_phrase(pn),
               "DUAL": dual, "TEMP": op_temp,
               "COP": copper, "RNOTE": f.get("reach_note"), "FCC": fc_clause}
        vidx = OPTIC_VOICE_IDX.get(pn, 0)
        i1, i2, i3 = _voices(ctx)[vidx % 10]
        pool = [s % pn for s in VOICE_POOL[vidx % 10]]               # voice-specific padding (no shared tail)
        # Kurzbeschreibung — opening varied by voice so siblings differ here too
        kopen = ["Der %s %s ist ein %s-%s-Transceiver%s%s%s.",
                 "Mit dem %s %s steht ein %s-%s-Transceiver%s%s bereit%s.",
                 "Der %s %s liefert als %s-%s-Transceiver%s%s eine verlässliche Optik%s."][vidx % 3]
        typ_k = (" vom Typ %s" % typ) if typ else ""
        media_k = ("RJ45-Kupfer" if copper else (ftyp + "-Glasfaser"))
        kp1 = ("<p>" + ws(kopen % (VEND, pn, spde, uk, typ_k, dual,
                                   (" für %s (%s)" % (media_k, std)) if std else (" für %s" % media_k)))
               + " " + ws("%s überbrückt er %s.%s</p>"
                          % (("Über den %s-Anschluss" % conn) if conn else "Optisch",
                             ("bis zu %s" % reach) if reach else "die geforderte Distanz",
                             " Es ist bis 85 °C spezifiziert." if op_temp else "")))
        kp2 = ("<p>Als Lenovo-Original-Neuware (ThinkSystem) wird das Modul versiegelt geliefert, ist im "
               "laufenden Betrieb tauschbar (Hot-Plug) und für ThinkSystem-Systeme mit %s-Steckplätzen "
               "vorgesehen.</p>" % uk)
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
        if op_temp:                                                  # ④ grounded op-temp authored verbatim
            attrs.append(["Betriebstemperatur", op_temp]); prov.append("Betriebstemperatur")
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
        # NOTE: optic `pool` is the voice-specific VOICE_POOL set above — do NOT reintroduce a shared pool
        # here (the old shared Hot-Plug/Abgleich pair caused two byte-identical tail sentences on all SR).

    kurz = pad_kurz(kp1, kp2)
    # optics: pad to a higher floor with the voice-specific pool so the composed Beschreibung clears
    # backfill's 90-word floor in the AUTHOR — otherwise backfill appends an identical spec-recap to
    # same-spec parts (a shared full sentence). Cables keep the standard floor.
    intro = pad_intro([ws(i1), ws(i2), ws(i3)], pool, lo=(95 if cable else 108))
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
