# -*- coding: utf-8 -*-
"""STEP-2 ArubaOS-Switch PHASE 2d: LEGACY zl modular lane — 5400zl (6 chassis) + 8200zl (10 chassis) + shared zl
module pool (20). REUSES the validated CX MODULAR-CHASSIS + MODULE Merkmal schema (commit 97d98a3) VERBATIM:
  CHASSIS = Switch-Typ(Modular-Chassis)/Layer/Steckplätze/Bauform/Switching-Kapazität/Stromversorgung/Kühlung/
            Unterstützte Supervisor-Engines/Redundanz/Anwendung (temp->prose; unterkategorie "Modularer Switch (Chassis)")
  MODULE  = Modultyp/Kompatible Serie (+ reused Portanzahl/Port-Konfiguration/PoE/Switching-Kapazität on line cards; NO Port-Geschwindigkeit)
0 new Merkmal NAMES; exactly ONE new Modultyp VALUE = "System-Support-Modul" (J9095A). Prose = ProVision/ProCurve (NOT AOS-CX).
Grounded: 5400zl QuickSpec DA-12436 + zl module Install Guide 5998-4703 (agents, findings-only); 8200zl operator-couriered
(IGSG + 8212 datasheet). never port-math; per-module SwK + 8200zl per-chassis Gbit/s un-published -> customer-safe (never ship
the token); PoE budgets chassis-PSU-dependent -> customer-safe. Hersteller=HP. Prices PHASE-1 ESTIMATE (flagged). $0 prose."""
import json, re, shutil, tempfile, csv, sys
from pathlib import Path
sys.path.insert(0, "_scratch")
from hexcat.config import load_rules, load_weights
from hexcat.stage3 import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat.writers import write_csv
from hexcat import constants as C
import scrub_uwg as S

ROOT = Path("."); rules, weights = load_rules(), load_weights()
E1, E2 = "Netzwerk & Infrastruktur", "Switches"; VERIF = "2026-07-01"
DOC_CH5400="https://www.ultima-computers.co.uk/documents/PDF/HP_ProCurve/5400zl_series/HP_Procurve_5400zl_Series_Switch_QuickSpecs.pdf"
DOC_CH8200="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c02051709"   # HP 8200zl QuickSpec (IGSG + 8212 datasheet, couriered)
DOC_MOD="https://andovercg.com/datasheets/hpe-5400zl-Switch-modules.pdf"              # zl module Install Guide 5998-4703
KOMPAT=["HP ProVision-Firmware","HP PCM+ (ProCurve Manager Plus)","HP IMC (Intelligent Management Center)"]
def ws(s): return re.sub(r"\s+", " ", s).strip()
def mk(pid, unterkat, doc, gw, price, artikel, titel, meta, kurz, intro, faq, attrs):
    versand = f"{float(gw.replace(',','.'))+2.0:.2f}".replace('.',',')
    prov = {a[0]:[doc,"datasheet"] for a in attrs if a[0]!="Zustand"}
    return {"_facts":{"unterkategorie":unterkat,"quell_url":doc,"verifiziert_am":VERIF},
            "artikelname":ws(artikel),"titel_tag":titel,"meta_description":ws(meta),
            "artikelgewicht":gw,"versandgewicht":versand,"kurzbeschreibung":ws(kurz),
            "intro":[ws(p) for p in intro],"kompatibilitaet":KOMPAT,
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{price}.00"}

# =================================================================== CHASSIS
ZLCH={
 "5406zl":dict(gen="5400zl",slots=6,he=4,swk="322,8 Gbit/s (System-Switching-Kapazität, 240,2 Mpps Durchsatz)",portmax="144× 10/100/1000 oder 24× 10-GbE",temp="0 bis 55 °C (mit 10-GbE-Modulen J8706A/J8707A 0 bis 40 °C)"),
 "5412zl":dict(gen="5400zl",slots=12,he=7,swk="645,6 Gbit/s (System-Switching-Kapazität, 480,3 Mpps Durchsatz)",portmax="288× 10/100/1000 oder 48× 10-GbE",temp="0 bis 55 °C (mit 10-GbE-Modulen J8706A/J8707A 0 bis 40 °C)"),
 "8206zl":dict(gen="8200zl",slots=6,he=6,swk="Fabric-vermittelt (System-Switching-Kapazität modellspezifisch nicht ausgewiesen)",portmax="144× 10/100/1000 oder 24× 10-GbE",temp="0 bis 45 °C"),
 "8212zl":dict(gen="8200zl",slots=12,he=9,swk="Fabric-vermittelt (System-Switching-Kapazität modellspezifisch nicht ausgewiesen; bis 428 Mpps Durchsatz)",portmax="288× 10/100/1000 oder 48× 10-GbE",temp="0 bis 45 °C"),
}
STROM_5400="bis {n} Hot-Swap-zl-Netzteilschächte (J8712A 875 W / J9306A 1500 W PoE+; redundant und hot-swap; separat bestellt)"
STROM_8200="Hot-Swap-zl-Netzteilschächte (J8712A 875 W / J9306A 1500 W PoE+; N+1-Redundanz, hot-swap; separat bestellt)"

def gen_chassis(pid, model, kind, gw, price, desc, npsu):
    s=ZLCH[model]; gen=s["gen"]; he=s["he"]; slots=s["slots"]; fab=s["swk"]; temp=s["temp"]
    is8200 = gen=="8200zl"
    steck = (f"{slots} Linecard-Steckplätze + dedizierte Management-, Fabric- und System-Support-Modul-Schächte" if is8200
             else f"{slots} zl-Modul-Steckplätze (Management-Modul mit integrierter Fabric)")
    strom = (STROM_8200 if is8200 else STROM_5400.format(n=npsu))
    sup = ("HP ProCurve 8200zl Management Module (J9092A) mit diskretem Fabric-Modul (J9093A) und System-Support-Modul (J9095A), redundant" if is8200
           else "HP ProCurve 5400zl Management Module (J8726A); Switch-Fabric im Management-Modul/Backplane integriert (kein diskretes Fabric-Modul)")
    redun = ("Redundante Fabric-, Management-, Netzteil- und Lüfter-Ebene" if is8200
             else "Netzteil-Redundanz (Hot-Swap) und Lüftertray; Management-/Fabric-Funktion im Management-Modul")
    anw = (f"Campus-Core/Rechenzentrums-Aggregation (modularer Layer-3-Switch, ProVision)" if is8200
           else "Campus-Core/Aggregation (modularer Layer-3-Switch, ProVision)")
    fab_prose = ("die Weiterleitung erfolgt über das diskrete Fabric-Modul (J9093A), die zentrale Switching-Fabric des Chassis; ein Management-Modul (J9092A) und ein System-Support-Modul (J9095A) ergänzen Steuerung und Systemdienste" if is8200
                 else "die Weiterleitung ist im Management-Modul und der Backplane integriert, ein diskretes Fabric-Modul entfällt")
    wnote = (f"Das angegebene Artikelgewicht des {pid} ist ein Konfigurationsgewicht (Herstellerangabe für das ab Werk bestückte System)." if kind=="bundle"
             else f"Das angegebene Artikelgewicht des {pid} ist das Grundgewicht des Chassis (ohne Module und Netzteile).")
    modelname=f"HP ProCurve {model.replace('zl','zl').replace('54','54').replace('82','82')}"  # e.g. 5406zl
    disp=f"HP ProCurve {model}"
    kindde={"base":"Basissystem-Chassis","replacement":"Ersatz-/Leergehäuse","bundle":"vorkonfiguriertes Switch-Bundle"}[kind]
    artikel=f"{disp} {pid} modulares {kindde} ({steck}, {he} HE) – {desc}"
    titel=f"HP ProCurve {model} {pid} Chassis | Hexwaren"
    meta=(f"Original {disp} {pid}: modulares {he}-HE-Layer-3-Chassis der ProCurve-{gen}-Serie, {steck}, ProVision. {desc}. Neu und versiegelt.")
    kurz=(f"<p>Der {disp} {pid} ist ein modulares Layer-3-Chassis der ProCurve-{gen}-Serie für Campus-Core und -Aggregation mit {steck}. "
          f"Der {pid} nimmt bis zu {s['portmax']} auf und wird unter dem HP-ProVision-Betriebssystem betrieben.</p>"
          f"<p>Der {pid} wird als {kindde} geliefert ({desc}) und trägt die zl-Modul- und zl-Netzteil-Familie; Auslieferung als versiegelte Original-Neuware.</p>")
    intro=[f"Der {disp} {pid} ist ein modularer Layer-3-Switch (Chassis) der HP-ProCurve-{gen}-Serie, ausgelegt für Campus-Core und -Aggregation und betrieben unter dem HP-ProVision-Betriebssystem. Der {pid} wird als {kindde} geliefert: {desc}.",
           f"Mit {steck} nimmt der {pid} bis zu {s['portmax']} auf; {fab_prose}. Die System-Switching-Kapazität des {pid} ist mit „{fab.split('(')[0].strip()}“ ausgewiesen.",
           f"Im 19-Zoll-Gehäuse ({he} HE) arbeitet der {pid} im Temperaturbereich {temp}; ein Lüftertray (Airflow front-to-back) und Hot-Swap-zl-Netzteile (J8712A 875 W / J9306A 1500 W PoE+, separat bestellt) versorgen den {pid}. {wnote} Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch."]
    faq=[[f"Wie viele Steckplätze hat der {pid}?", f"Der {pid} bietet {steck} und nimmt bis zu {s['portmax']} auf."],
         [f"Hat der {pid} ein diskretes Fabric-Modul?", (f"Ja. Der {pid} der 8200zl-Serie nutzt ein diskretes Fabric-Modul (J9093A) als zentrale Switching-Fabric – als einzige zl-Chassis-Serie." if is8200 else f"Nein. Beim {pid} ist die Switch-Fabric im Management-Modul und der Backplane integriert; ein separates Fabric-Modul entfällt.")],
         [f"Welche Module passen in den {pid}?", (f"Der {pid} nimmt die gemeinsamen HP-ProCurve-zl-Linecards sowie das 8200zl-Management-, -Fabric- und -System-Support-Modul auf." if is8200 else f"Der {pid} nimmt die gemeinsamen HP-ProCurve-zl-Linecards sowie das 5400zl-Management-Modul (J8726A) auf.")],
         [f"Ist der {pid} ein originales HPE-Produkt?", f"Ja. Der {pid} ist HP-Original-Neuware der ProCurve-{gen}-Serie, versiegelt geliefert und für den Betrieb unter dem HP-ProVision-Betriebssystem vorgesehen."]]
    attrs=[["Switch-Typ","Modular-Chassis"],["Layer","L3"],["Steckplätze",steck],
           ["Bauform",f"19-Zoll-Rackmontage ({he} HE)"],["Switching-Kapazität",fab],
           ["Stromversorgung",strom],["Kühlung","Lüftergekühlt (Lüftertray, Airflow front-to-back)"],
           ["Unterstützte Supervisor-Engines",sup],["Redundanz",redun],["Anwendung",anw],["Zustand","Neu, versiegelt"]]
    return mk(pid,"Modularer Switch (Chassis)",(DOC_CH8200 if is8200 else DOC_CH5400),gw,price,artikel,titel,meta,kurz,intro,faq,attrs)

CHASSIS={}
# 5400zl (6) — model, kind, gw, price, desc, npsu
for pid,model,kind,gw,price,desc,npsu in [
 ("J8697A","5406zl","base","10,68",6000,"Leergehäuse ohne Netzteile",2),
 ("J8698A","5412zl","base","15,85",9000,"Leergehäuse ohne Netzteile",4),
 ("J8699A","5406zl","bundle","15,54",9000,"vorkonfiguriert mit zwei 24-Port-Gig-T-PoE-zl-Modulen (J8702A) und einem 875-W-zl-Netzteil, 48 Gigabit-Ports vorinstalliert, vier offene Steckplätze",2),
 ("J8700A","5412zl","bundle","26,31",14000,"vorkonfiguriert mit vier 24-Port-Gig-T-PoE-zl-Modulen (J8702A) und zwei 875-W-zl-Netzteilen, 96 Gigabit-Ports vorinstalliert, acht offene Steckplätze",4),
 ("J9447A","5406zl","bundle","15,83",11000,"vorkonfiguriert mit J9307A- und J9308A-PoE+-Modul und 1500-W-PoE+-zl-Netzteil (J9306A), 44 Gigabit-PoE+-Ports und vier SFP-Slots, vier offene Steckplätze",2),
 ("J9448A","5412zl","bundle","26,39",17000,"vorkonfiguriert mit drei J9307A- und einem J9308A-PoE+-Modul und zwei 1500-W-PoE+-zl-Netzteilen, 92 Gigabit-PoE+-Ports und vier SFP-Slots, acht offene Steckplätze",4),
]:
    CHASSIS[pid]=gen_chassis(pid,model,kind,gw,price,desc,npsu)
CHASSIS_8200={}
for pid,model,kind,gw,price,desc,npsu in [
 ("J8715A","8212zl","base","22,88",12000,"Basissystem mit zwölf Modul-Steckplätzen",4),
 ("J8715B","8212zl","base","22,88",12200,"Basissystem mit zwölf Modul-Steckplätzen (Revision B)",4),
 ("J9091A","8212zl","replacement","22,88",9000,"Ersatzgehäuse mit Lüftertray (ohne Module, Ersatzteil)",4),
 ("J9091B","8212zl","replacement","22,88",9200,"Ersatzgehäuse mit Lüftertray (ohne Module, Ersatzteil, Revision B)",4),
 ("J9639A","8212zl","bundle","30,00",20000,"v2-zl-Bundle mit Premium-Software, 92 Gigabit-PoE+-Ports und zwei 10-GbE-SFP+-Ports vorinstalliert",4),
 ("J9641A","8212zl","bundle","24,00",16000,"v2-zl-Bundle mit Premium-Software (Chassis mit Premium-Lizenz, ohne vorinstallierte Linecards)",4),
 ("J9475A","8206zl","base","17,36",9000,"Basissystem mit sechs Modul-Steckplätzen",4),
 ("J9477A","8206zl","replacement","17,36",7000,"Ersatzgehäuse (ohne Module, Ersatzteil)",4),
 ("J9638A","8206zl","bundle","23,00",15000,"v2-zl-Bundle mit Premium-Software, 44 Gigabit-PoE+-Ports und zwei 10-GbE-SFP+-Ports vorinstalliert",4),
 ("J9640A","8206zl","bundle","19,00",12000,"v2-zl-Bundle mit Premium-Software (Chassis mit Premium-Lizenz, ohne vorinstallierte Linecards)",4),
]:
    CHASSIS_8200[pid]=gen_chassis(pid,model,kind,gw,price,desc,npsu)

# =================================================================== MODULES
SWK_MOD="Chassis-Backplane-vermittelt (modellspezifischer Wert nicht ausgewiesen)"
poe_af="Ja (IEEE 802.3af Class 3, 15,4 W/Port; Gesamt-PoE-Budget abhängig von der Netzteilbestückung des Chassis)"
poe_at="Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port; Gesamt-PoE-Budget abhängig von der Netzteilbestückung des Chassis)"
SERIE_SHARED="HP ProCurve 5400zl / 8200zl"
def gen_line(pid, ver, short, n, portkonfig, poe, price=7000):
    poe_attr=[["PoE",poe]] if poe else []
    poe_k=(f" Die {pid} speist angeschlossene Endgeräte per Power over Ethernet." if poe else f" Die {pid} ist auf reine Daten-Anbindung ohne PoE ausgelegt.")
    poe_i=(f" Die {pid} versorgt angeschlossene Geräte per Power over Ethernet; das Gesamt-PoE-Budget hängt von der Netzteilbestückung des Chassis ab." if poe else f" Eine PoE-Einspeisung bietet die {pid} nicht.")
    kurz=(f"<p>Die {pid} ist eine HP-ProCurve-zl-Linecard ({ver}) mit {short} für die modularen Chassis der HP-ProCurve-5400zl- und 8200zl-Serie. Die {pid} stellt {portkonfig} bereit.{poe_k}</p>"
          f"<p>Die {pid} trägt einen karteneigenen Forwarding-ASIC, ist im laufenden Betrieb steckbar (hot-swap) und belegt einen zl-Modul-Steckplatz des Chassis. Sie wird als versiegelte Original-Neuware geliefert.</p>")
    intro=[f"Die {pid} ist eine HP-ProCurve-zl-Linecard ({ver}) mit {short} für die modularen Chassis der HP-ProCurve-5400zl- und 8200zl-Serie, betrieben unter dem HP-ProVision-Betriebssystem und ausgelegt für Erweiterung und Ersatz im Chassis.",
           f"Mit {portkonfig} stellt die {pid} ihre Anschlüsse bereit; die Weiterleitung übernimmt der karteneigene Forwarding-ASIC der {pid}, sodass die Karte unabhängig zur Gesamtkapazität des Chassis beiträgt.{poe_i}",
           f"Kompatibel ist die {pid} mit den Chassis der Serien HP ProCurve 5400zl und 8200zl; sie benötigt ein kompatibles Chassis mit Management-Modul und ist kein eigenständiger Switch. Geliefert wird die {pid} als versiegelte Original-Neuware. Originales HP-Modul."]
    faq=[[f"Wofür wird die {pid} verwendet?", f"Die {pid} ist eine zl-Linecard ({short}) für die modularen HP-ProCurve-5400zl- und 8200zl-Chassis."],
         [f"In welche Chassis passt die {pid}?", f"Die {pid} ist mit den Serien HP ProCurve 5400zl und 8200zl kompatibel und belegt einen zl-Modul-Steckplatz."],
         ([f"Unterstützt die {pid} PoE?", f"Ja. Die {pid} speist angeschlossene Geräte per Power over Ethernet ein; das Gesamt-PoE-Budget hängt von der Netzteilbestückung des Chassis ab."] if poe else
          [f"Unterstützt die {pid} PoE?", f"Nein. Die {pid} ist eine zl-Linecard ohne Power over Ethernet."]),
         [f"Ist die {pid} ungebraucht?", f"Ja. Hexwaren führt die {pid} ausschließlich als versiegelte Original-Neuware."]]
    attrs=[["Modultyp","Linecard"],["Kompatible Serie",SERIE_SHARED],["Portanzahl",str(n)],["Port-Konfiguration",portkonfig]]+poe_attr+[["Switching-Kapazität",SWK_MOD],["Zustand","Neu, versiegelt"]]
    return mk(pid,"Switch-Modul",DOC_MOD,"3,50",price,
        f"HP ProCurve zl {pid} Linecard ({ver}) – {short} für 5400zl/8200zl",
        f"HP ProCurve zl {pid} Linecard | Hexwaren",
        f"Original HP ProCurve zl {pid}: Linecard ({short}) für die modularen Chassis HP ProCurve 5400zl und 8200zl, ProVision. Modul, Chassis separat. Neu und versiegelt.",
        kurz,intro,faq,attrs)
def gen_mgmt(pid, serie, sershort):
    return mk(pid,"Switch-Modul",DOC_MOD,"2,50",3500,
      f"HP ProCurve zl {pid} Management-Modul für {serie} (Control-Plane)",
      f"HP ProCurve zl {pid} Management-Modul | Hexwaren",
      f"Original HP ProCurve zl {pid}: Management-Modul (Control-Plane) für die modularen Chassis {serie}, ProVision. Modul, Chassis separat. Neu und versiegelt.",
      f"<p>Das {pid} ist das Management-Modul (Control-Plane) für die modularen Chassis der Serie {serie}. Das {pid} steuert Routing, Switching und das Management des gesamten Chassis unter dem HP-ProVision-Betriebssystem.</p>"
      f"<p>Das {pid} trägt den Steuerprozessor und den Compact-Flash-Speicher des Chassis, ist hot-swap-fähig und lässt sich für Hochverfügbarkeit redundant betreiben. Es wird als versiegelte Original-Neuware geliefert.</p>",
      [f"Das {pid} ist das zentrale Management-Modul für die modularen {serie}-Chassis unter dem HP-ProVision-Betriebssystem. Als Control-Plane-Modul übernimmt das {pid} Routing, Switching-Steuerung und das Chassis-Management.",
       f"Das {pid} trägt den Steuerprozessor sowie den Compact-Flash-Speicher für die Firmware-Images des Chassis; die Weiterleitungsleistung selbst liegt auf den zl-Linecards. Ohne Management-Modul ist das {sershort}-Chassis nicht betriebsfähig. Das {pid} ist hot-swap-fähig und im laufenden Betrieb tauschbar.",
       f"Kompatibel ist das {pid} mit den Chassis der Serie {serie}; es dient Erweiterung, Ersatz und Aufrüstung bestehender {sershort}-Installationen und ist kein eigenständiger Switch. Geliefert wird das {pid} als versiegelte Original-Neuware. Originales HP-Modul."],
      [[f"Wofür wird das {pid} verwendet?", f"Das {pid} ist das Management-Modul (Control-Plane) für die {serie}-Chassis und steuert Routing, Switching und Chassis-Management."],
       [f"In welche Chassis passt das {pid}?", f"Das {pid} ist mit den Chassis der Serie {serie} kompatibel und belegt den Management-Modul-Schacht."],
       [f"Ist das {pid} ein eigenständiger Switch?", f"Nein. Das {pid} ist ein Management-Modul und benötigt ein kompatibles {sershort}-Chassis sowie zl-Linecards."],
       [f"Ist das {pid} ungebraucht?", f"Ja. Hexwaren führt das {pid} ausschließlich als versiegelte Original-Neuware."]],
      [["Modultyp","Management-Modul"],["Kompatible Serie",serie],["Zustand","Neu, versiegelt"]])
def gen_fabric(pid):
    serie="HP ProCurve 8200zl"
    return mk(pid,"Switch-Modul",DOC_MOD,"3,00",6000,
      f"HP ProCurve zl {pid} Fabric-Modul für {serie} (zentrale Switching-Fabric)",
      f"HP ProCurve zl {pid} Fabric-Modul | Hexwaren",
      f"Original HP ProCurve zl {pid}: Fabric-Modul für das modulare Chassis {serie}, hot-swap und redundant. Modul, Chassis separat. Neu und versiegelt.",
      f"<p>Das {pid} ist das diskrete Fabric-Modul für das modulare Chassis der Serie {serie}. Das {pid} bildet die zentrale Switching-Fabric des Chassis, über die der gesamte Datenverkehr zwischen den zl-Linecards vermittelt wird – die 8200zl-Serie ist die einzige zl-Chassis-Serie mit diskretem Fabric-Modul.</p>"
      f"<p>Mehrere Fabric-Module arbeiten lastverteilt und redundant; das {pid} ist hot-swap-fähig und wird als versiegelte Original-Neuware geliefert.</p>",
      [f"Das {pid} ist das diskrete Fabric-Modul für das modulare {serie}-Chassis unter dem HP-ProVision-Betriebssystem, ausgelegt als zentrale Switching-Fabric des Chassis.",
       f"Das {pid} vermittelt den gesamten Datenverkehr zwischen den zl-Linecards des Chassis; mehrere Fabric-Module arbeiten lastverteilt und redundant, sodass das Chassis beim Ausfall eines einzelnen Moduls unterbrechungsarm weiterläuft. Das {pid} ist hot-swap-fähig und im laufenden Betrieb tauschbar. Die 8200zl-Serie ist die einzige zl-Serie mit diskretem Fabric-Modul.",
       f"Kompatibel ist das {pid} mit dem Chassis der Serie {serie}; es dient Erweiterung, Redundanz und Ersatz und ist kein eigenständiger Switch. Geliefert wird das {pid} als versiegelte Original-Neuware. Originales HP-Modul."],
      [[f"Wofür wird das {pid} verwendet?", f"Das {pid} ist das diskrete Fabric-Modul und bildet die zentrale Switching-Fabric des {serie}-Chassis."],
       [f"In welches Chassis passt das {pid}?", f"Das {pid} ist mit dem Chassis der Serie {serie} kompatibel und belegt den Fabric-Modul-Schacht."],
       [f"Ist das {pid} ein eigenständiger Switch?", f"Nein. Das {pid} ist ein Fabric-Modul und benötigt ein kompatibles {serie}-Chassis."],
       [f"Ist das {pid} ungebraucht?", f"Ja. Hexwaren führt das {pid} ausschließlich als versiegelte Original-Neuware."]],
      [["Modultyp","Fabric-Module"],["Kompatible Serie",serie],["Switching-Kapazität","Zentrale Chassis-Fabric (Bandbreite modellspezifisch nicht ausgewiesen)"],["Zustand","Neu, versiegelt"]])
def gen_ssm(pid):
    serie="HP ProCurve 8200zl"
    return mk(pid,"Switch-Modul",DOC_MOD,"2,50",4500,
      f"HP ProCurve zl {pid} System-Support-Modul für {serie}",
      f"HP ProCurve zl {pid} System-Support-Modul | Hexwaren",
      f"Original HP ProCurve zl {pid}: System-Support-Modul für die modularen Chassis der 8200zl-Serie (8206zl/8212zl), ProVision. Modul, Chassis separat. Neu und versiegelt.",
      f"<p>Das {pid} ist das System-Support-Modul für das modulare Chassis der Serie {serie}. Das {pid} ergänzt Management- und Fabric-Modul um zentrale Systemdienste des Chassis und ist eine Besonderheit der 8200zl-Serie.</p>"
      f"<p>Das {pid} ist hot-swap-fähig, im laufenden Betrieb tauschbar und belegt einen dedizierten Modul-Schacht des 8200zl-Chassis. Es wird als versiegelte Original-Neuware geliefert.</p>",
      [f"Das {pid} ist das System-Support-Modul für das modulare {serie}-Chassis unter dem HP-ProVision-Betriebssystem. Es ergänzt Management- und Fabric-Modul um zentrale Systemdienste des Chassis und ist eine Besonderheit der 8200zl-Serie.",
       f"Als System-Support-Modul übernimmt das {pid} unterstützende Systemfunktionen des 8200zl-Chassis, die über die reine Weiterleitung der zl-Linecards hinausgehen; die eigentliche Forwarding-Leistung liegt auf den Linecards und dem diskreten Fabric-Modul (J9093A). Das {pid} ist hot-swap-fähig und im laufenden Betrieb tauschbar.",
       f"Kompatibel ist das {pid} mit dem Chassis der Serie {serie}; es dient Erweiterung, Redundanz und Ersatz bestehender 8200zl-Installationen und ist kein eigenständiger Switch. Geliefert wird das {pid} als versiegelte Original-Neuware. Originales HP-Modul."],
      [[f"Wofür wird das {pid} verwendet?", f"Das {pid} ist das System-Support-Modul des {serie}-Chassis und stellt zentrale Systemdienste bereit."],
       [f"In welches Chassis passt das {pid}?", f"Das {pid} ist mit dem Chassis der Serie {serie} kompatibel und belegt den System-Support-Modul-Schacht."],
       [f"Ist das {pid} ein eigenständiger Switch?", f"Nein. Das {pid} ist ein System-Support-Modul und benötigt ein kompatibles {serie}-Chassis."],
       [f"Ist das {pid} ungebraucht?", f"Ja. Hexwaren führt das {pid} ausschließlich als versiegelte Original-Neuware."]],
      [["Modultyp","System-Support-Modul"],["Kompatible Serie",serie],["Zustand","Neu, versiegelt"]])

MODULES={}
for pid,ver,short,n,pk,poe,price in [
 ("J9534A","v2","24× Gig-T PoE+",24,"24× 10/100/1000 (RJ45, Class 4 PoE+)",poe_at,6500),
 ("J9535A","v2","20× Gig-T PoE+ + 4× SFP",24,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× SFP (1G)",poe_at,6800),
 ("J9536A","v2","20× Gig-T PoE+ + 2× SFP+",22,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 2× SFP+ (10G)",poe_at,7500),
 ("J9537A","v2","24× SFP (1G)",24,"24× SFP (1G Glasfaser)",None,5500),
 ("J9538A","v2","8× 10-GbE SFP+",8,"8× SFP+ (10G)",None,8200),
 ("J9546A","v2","8× 10GBASE-T",8,"8× 10GBASE-T (RJ45, 10 GbE)",None,7000),
 ("J9547A","v2","24× 10/100 PoE+",24,"24× 10/100 (RJ45, Class 4 PoE+)",poe_at,5800),
 ("J9550A","v2","24× Gig-T",24,"24× 10/100/1000 (RJ45)",None,4500),
 ("J8702A","v1","24× Gig-T PoE",24,"24× 10/100/1000 (RJ45, Class 3 PoE)",poe_af,4800),
 ("J8705A","v1","20× Gig-T PoE + 4× SFP",24,"20× 10/100/1000 (RJ45, Class 3 PoE) + 4× SFP (1G)",poe_af,5200),
 ("J8706A","v1","24× SFP (1G)",24,"24× SFP (1G Glasfaser)",None,5000),
 ("J8707A","v1","4× 10-GbE X2",4,"4× 10-GbE X2",None,6600),
 ("J8708A","v1","4× 10-GbE CX4",4,"4× 10-GbE CX4",None,6100),
 ("J9307A","v1","24× Gig-T PoE+",24,"24× 10/100/1000 (RJ45, Class 4 PoE+)",poe_at,6300),
 ("J9308A","v1","20× Gig-T PoE+ + 4× SFP",24,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× SFP (1G)",poe_at,6700),
 ("J9309A","v1","4× 10-GbE SFP+",4,"4× SFP+ (10G)",None,6900),
]:
    MODULES[pid]=gen_line(pid,ver,short,n,pk,poe,price)
MODULES["J8726A"]=gen_mgmt("J8726A","HP ProCurve 5400zl","5400zl")
MODULES["J9092A"]=gen_mgmt("J9092A","HP ProCurve 8200zl","8200zl")
MODULES["J9093A"]=gen_fabric("J9093A")
MODULES["J9095A"]=gen_ssm("J9095A")

# =================================================================== build (PRE-remap gate; Cisco/CX chassis order)
def build(cat, doc_map):
    cpath=ROOT/"stage3_content"/f"{cat}_content.json"; cpath.write_text(json.dumps(doc_map,ensure_ascii=False,indent=1),encoding="utf-8")
    recs=reconcile_content(cpath,brand="Aruba",rules=rules,weights=weights)
    out=ROOT/"output"/"switches"/cat
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    assemble_bundle(recs,rules,batch=cat,category=cat,out_dir=out)
    S.process_main(out/f"Hexwaren_{cat}_Main.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    S.process_faq(out/f"Hexwaren_FAQ_{cat}.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/cat; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {cat} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:8]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:110])
    e3=cat.replace("_"," "); mp=out/f"Hexwaren_{cat}_Main.csv"
    rows=list(csv.reader(mp.read_bytes().decode("utf-8-sig").splitlines(),delimiter=";")); H=rows[0]
    i1,i2,i3=H.index("Kategorie Ebene 1"),H.index("Kategorie Ebene 2"),H.index("Kategorie Ebene 3"); data=[]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        r[i1],r[i2],r[i3]=E1,E2,e3; data.append(r)
    write_csv(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{cat}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in doc_map:
        vrows.append([pid,doc_map[pid]["netto_vk"].replace('.',','),"PHASE-1-SCHÄTZUNG — NICHT marktgegroundet (EOL-zl-Chassis/-Modul). Tier-Tarif. Echte HPE-Marktpreis-Recherche folgt.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    return out

if __name__=="__main__":
    fams={"5400":("HP_ProCurve_5400zl_Switches",CHASSIS),"8200":("HP_ProCurve_8200zl_Switches",CHASSIS_8200),"mod":("HP_ProCurve_zl_Modules",MODULES)}
    only=sys.argv[1] if len(sys.argv)>1 else None
    for k,(cat,dm) in fams.items():
        if only and k!=only: continue
        build(cat,dm)
