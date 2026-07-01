# -*- coding: utf-8 -*-
"""STEP-2 ArubaOS-Switch PHASE 2c: 5400R zl2 (current-gen modular flagship) — 11 chassis + 11 modules (10 line cards + J9827A mgmt).
REUSES the validated CX MODULAR-CHASSIS + MODULE Merkmal schema (commit 97d98a3) VERBATIM. 0 new Merkmal NAMES; NO new Modultyp value
(reuse Linecard/Management-Modul). Prose = ArubaOS-Switch (current-gen, AOS-S 16.11 RN-supported; ProVision-ASIC hardware). DISTINCT
from the legacy 5400zl v1 (Phase 2d) — separate E3. NO discrete fabric (forwarding integrated in the J9827A management module)->prose.
Grounded: cached 5400R QuickSpec c04293383 (chassis) + AOS-S 16.11 RN (modules, authoritative vs the QuickSpec column-scramble; agents,
findings-only). Per-chassis SwK is the 5400R's OWN figure (960/1920 Gbit/s), NOT the 6400's 2,8 Tbit/s, NOT port-math. Per-module SwK +
PoE budget un-published -> customer-safe (never ship the token). Hersteller=HP. Prices PHASE-1 ESTIMATE (flagged). $0 prose."""
import json, re, shutil, tempfile, csv, sys
from pathlib import Path
sys.path.insert(0, "_scratch")
from hexcat.config import load_rules, load_weights
from hexcat.stage3 import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat import constants as C
import scrub_uwg as S

ROOT = Path("."); rules, weights = load_rules(), load_weights()
E1, E2 = "Netzwerk & Infrastruktur", "Switches"; VERIF = "2026-07-01"
DOC = "https://www.hpe.com/psnow/doc/c04293383"     # HPE Aruba 5400R zl2 QuickSpec (chassis; modules cross-checked vs AOS-S 16.11 RN)
KOMPAT = ["HPE Aruba Networking ArubaOS-Switch","Aruba Central","HP IMC (Intelligent Management Center)"]
def ws(s): return re.sub(r"\s+", " ", s).strip()
def mk(pid, unterkat, gw, price, artikel, titel, meta, kurz, intro, faq, attrs):
    versand=f"{float(gw.replace(',','.'))+2.0:.2f}".replace('.',',')
    prov={a[0]:[DOC,"datasheet"] for a in attrs if a[0]!="Zustand"}
    return {"_facts":{"unterkategorie":unterkat,"quell_url":DOC,"verifiziert_am":VERIF},
            "artikelname":ws(artikel),"titel_tag":titel,"meta_description":ws(meta),
            "artikelgewicht":gw,"versandgewicht":versand,"kurzbeschreibung":ws(kurz),
            "intro":[ws(p) for p in intro],"kompatibilitaet":KOMPAT,
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{price}.00"}

# =================================================================== CHASSIS
CH={"5406R":dict(slots=6,he=4,swk="960 Gbit/s (Routing/Switching; Switch-Fabric 1.015 Gbit/s), 571,4 Mpps Durchsatz",npsu=2,fan="J9831A"),
    "5412R":dict(slots=12,he=7,swk="1.920 Gbit/s (Routing/Switching; Switch-Fabric 2.030 Gbit/s), 1.142,8 Mpps Durchsatz",npsu=4,fan="J9832A")}
SUP="HPE Aruba Networking 5400R zl2 Management Module (J9827A), bis 2 redundant; Weiterleitung im Management-Modul integriert (kein diskretes Fabric-Modul)"
REDUN="Management-Modul (bis 2, redundant), Netzteil (N+1, Hot-Swap) und Hot-Swap-Lüftertray; VSF-Stacking chassisübergreifend"
def gen_chassis(pid, model, disp, kind, gw, price, desc):
    s=CH[model]; he=s["he"]; slots=s["slots"]; fab=s["swk"]
    steck=f"{slots} zl2-Modul-Steckplätze (Management-Modul mit integrierter Fabric)"
    strom=f"bis {s['npsu']} Hot-Swap-Netzteile (5400R 700 W oder 1100 W PoE+ zl2; redundant; separat bestellt, Chassis ohne Netzteil)"
    anw="Campus-Core/Aggregation (modularer Layer-3-Switch, ArubaOS-Switch)"
    kindde={"base":"Basissystem-Chassis","bundle":"vorkonfiguriertes Switch-Bundle"}[kind]
    wnote=(f"Das angegebene Artikelgewicht des {pid} ist ein Konfigurationsgewicht (Herstellerangabe für das ab Werk bestückte System)." if kind=="bundle"
           else f"Das angegebene Artikelgewicht des {pid} ist das Grundgewicht des Chassis (ohne Linecards und Netzteile).")
    artikel=f"HPE Aruba Networking {disp} {pid} modulares {kindde} ({steck}, {he} HE) – {desc}"
    titel=f"Aruba {disp} {pid} Chassis | Hexwaren"
    if len(titel)>60: titel=f"Aruba 5400R zl2 {pid} Chassis | Hexwaren"
    meta=f"Original HPE Aruba Networking {disp} ({pid}): modulares {he}-HE-Layer-3-Chassis der Aruba-5400R-zl2-Serie, {steck}, ArubaOS-Switch. {desc}. Neu und versiegelt."
    kurz=(f"<p>Der HPE Aruba Networking {disp} ({pid}) ist ein modulares Layer-3-Chassis der Aruba-5400R-zl2-Serie für Campus-Core und -Aggregation mit {steck}. "
          f"Der {pid} erreicht eine Switching-Kapazität von {fab.split('(')[0].strip()} und wird unter ArubaOS-Switch betrieben.</p>"
          f"<p>Der {pid} wird als {kindde} geliefert ({desc}); Management-Modul (J9827A) und Lüftertray sind enthalten, das Netzteil wird separat bestellt. Auslieferung als versiegelte Original-Neuware.</p>")
    intro=[f"Der HPE Aruba Networking {disp} ({pid}) ist ein modularer Layer-3-Switch (Chassis) der Aruba-5400R-zl2-Serie, ausgelegt für Campus-Core und -Aggregation und betrieben unter ArubaOS-Switch (ProVision-ASIC). Der {pid} wird als {kindde} geliefert: {desc}.",
           f"Mit {steck} erreicht der {pid} eine Switching-Kapazität von {fab}; die Weiterleitung ist im Management-Modul (J9827A) integriert, ein diskretes Fabric-Modul entfällt. Für Hochverfügbarkeit lassen sich im {pid} bis zu zwei Management-Module redundant betreiben (Nonstop-Switching).",
           f"Im 19-Zoll-Gehäuse ({he} HE) arbeitet der {pid} im Temperaturbereich 0 bis 45 °C; ein Hot-Swap-Lüftertray ({s['fan']}, Airflow front-to-back) und bis zu {s['npsu']} Hot-Swap-Netzteile (5400R 700 W oder 1100 W PoE+ zl2, separat bestellt) versorgen den {pid}. {wnote} Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch."]
    faq=[[f"Wie viele Steckplätze hat der {pid}?", f"Der {pid} bietet {steck}; das Management-Modul J9827A ist bereits enthalten."],
         [f"Wie hoch ist die Switching-Kapazität des {pid}?", f"Der {pid} erreicht {fab}."],
         [f"Hat der {pid} ein diskretes Fabric-Modul?", f"Nein. Beim {pid} ist die Switch-Fabric im Management-Modul (J9827A) integriert; ein separates Fabric-Modul entfällt. Für Redundanz lassen sich bis zu zwei Management-Module betreiben."],
         [f"Ist der {pid} ein originales HPE-Produkt?", f"Ja. Der {pid} ist HPE-Aruba-Networking-Original-Neuware der 5400R-zl2-Serie, versiegelt geliefert und für den Betrieb unter ArubaOS-Switch vorgesehen."]]
    attrs=[["Switch-Typ","Modular-Chassis"],["Layer","L3"],["Steckplätze",steck],
           ["Bauform",f"19-Zoll-Rackmontage ({he} HE)"],["Switching-Kapazität",fab],
           ["Stromversorgung",strom],["Kühlung",f"Lüftergekühlt (Hot-Swap-Lüftertray {s['fan']}, Airflow front-to-back)"],
           ["Unterstützte Supervisor-Engines",SUP],["Redundanz",REDUN],["Anwendung",anw],["Zustand","Neu, versiegelt"]]
    return mk(pid,"Modularer Switch (Chassis)",gw,price,artikel,titel,meta,kurz,intro,faq,attrs)

CHASSIS={}
for pid,model,disp,kind,gw,price,desc in [
 ("J9821A","5406R","5406R zl2 Switch","base","11,11",18000,"Leergehäuse mit sechs Modul-Steckplätzen, alle Steckplätze frei"),
 ("J9822A","5412R","5412R zl2 Switch","base","17,28",26000,"Leergehäuse mit zwölf Modul-Steckplätzen, alle Steckplätze frei"),
 ("J9823A","5406R","5406R-44G-PoE+/2SFP+ v2 zl2 Switch","bundle","12,75",24000,"44 Gigabit-PoE+-Ports und zwei 10-GbE-SFP+-Ports vorinstalliert, vier freie Steckplätze"),
 ("J9824A","5406R","5406R-44G-PoE+/4SFP v2 zl2 Switch","bundle","11,88",23000,"44 Gigabit-PoE+-Ports und vier SFP-Ports vorinstalliert, vier freie Steckplätze"),
 ("J9825A","5412R","5412R-92G-PoE+/2SFP+ v2 zl2 Switch","bundle","20,50",34000,"92 Gigabit-PoE+-Ports und zwei 10-GbE-SFP+-Ports vorinstalliert, acht freie Steckplätze"),
 ("J9826A","5412R","5412R-92G-PoE+/4SFP v2 zl2 Switch","bundle","20,50",35000,"92 Gigabit-PoE+-Ports und vier SFP-Ports vorinstalliert, acht freie Steckplätze"),
 ("J9868A","5406R","5406R-8XGT/8SFP+ v2 zl2 Switch","bundle","12,75",26000,"acht 10GBASE-T-Ports und acht 10-GbE-SFP+-Ports vorinstalliert, vier freie Steckplätze"),
 ("JL001A","5412R","5412R-92GT-PoE+/4SFP+ v3 zl2 Switch","bundle","20,50",36000,"92 Gigabit-PoE+-Ports und vier 10-GbE-SFP+-Ports vorinstalliert, acht freie Steckplätze"),
 ("JL002A","5406R","5406R-8-SmartRate-PoE+/8SFP+ v3 zl2 Switch","bundle","12,75",28000,"acht HPE-Smart-Rate-PoE+-Ports (1/2.5/5/10GBASE-T) und acht 10-GbE-SFP+-Ports vorinstalliert, vier freie Steckplätze"),
 ("JL003A","5406R","5406R-44GT-PoE+/4SFP+ v3 zl2 Switch","bundle","12,75",25000,"44 Gigabit-PoE+-Ports und vier 10-GbE-SFP+-Ports vorinstalliert, vier freie Steckplätze"),
 ("JL095A","5406R","5406R-16SFP+ v3 zl2 Switch","bundle","12,75",24000,"16 10-GbE-SFP+-Ports vorinstalliert, vier freie Steckplätze"),
]:
    CHASSIS[pid]=gen_chassis(pid,model,disp,kind,gw,price,desc)

# =================================================================== MODULES
SWK_MOD="Chassis-Fabric-vermittelt (modellspezifischer Wert nicht ausgewiesen)"
poe_at="Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port; Gesamt-PoE-Budget abhängig von der Netzteilbestückung des Chassis)"
SERIE="Aruba 5400R zl2"
def gen_line(pid, short, n, portkonfig, poe, price):
    poe_attr=[["PoE",poe]] if poe else []
    poe_k=(f" Die {pid} speist angeschlossene Endgeräte per Power over Ethernet." if poe else f" Die {pid} ist auf reine Daten-Anbindung ohne PoE ausgelegt.")
    poe_i=(f" Die {pid} versorgt angeschlossene Geräte per Power over Ethernet; das Gesamt-PoE-Budget hängt von der Netzteilbestückung des Chassis ab." if poe else f" Eine PoE-Einspeisung bietet die {pid} nicht.")
    kurz=(f"<p>Die HPE Aruba Networking 5400R zl2 {pid} ist eine Linecard mit {short} für die modularen Chassis der Aruba-5400R-zl2-Serie (5406R/5412R). Die {pid} stellt {portkonfig} bereit.{poe_k}</p>"
          f"<p>Die {pid} trägt einen karteneigenen Forwarding-ASIC mit MACsec-Verschlüsselung, ist im laufenden Betrieb steckbar (hot-swap) und belegt einen zl2-Modul-Steckplatz des Chassis. Sie wird als versiegelte Original-Neuware geliefert.</p>")
    intro=[f"Die HPE Aruba Networking 5400R zl2 {pid} ist eine Linecard mit {short} für die modularen Chassis der Aruba-5400R-zl2-Serie (5406R/5412R), betrieben unter ArubaOS-Switch und ausgelegt für Erweiterung und Ersatz im Chassis.",
           f"Mit {portkonfig} stellt die {pid} ihre Anschlüsse bereit; die Weiterleitung übernimmt der karteneigene Forwarding-ASIC der {pid} mit durchgängiger MACsec-Verschlüsselung, sodass die Karte unabhängig zur Gesamtkapazität des Chassis beiträgt.{poe_i}",
           f"Kompatibel ist die {pid} ausschließlich mit den Chassis der Serie Aruba 5400R zl2; sie benötigt ein kompatibles Chassis mit Management-Modul und ist kein eigenständiger Switch. Geliefert wird die {pid} als versiegelte Original-Neuware. Originales HP-Modul."]
    faq=[[f"Wofür wird die {pid} verwendet?", f"Die {pid} ist eine zl2-Linecard ({short}) für die modularen Aruba-5400R-zl2-Chassis (5406R/5412R)."],
         [f"In welche Chassis passt die {pid}?", f"Die {pid} ist ausschließlich mit der Serie Aruba 5400R zl2 kompatibel und belegt einen zl2-Modul-Steckplatz; sie ist nicht mit den älteren 5400zl-Chassis kompatibel."],
         ([f"Unterstützt die {pid} PoE?", f"Ja. Die {pid} speist angeschlossene Geräte per IEEE 802.3at PoE+ ein; das Gesamt-PoE-Budget hängt von der Netzteilbestückung des Chassis ab."] if poe else
          [f"Unterstützt die {pid} PoE?", f"Nein. Die {pid} ist eine zl2-Linecard ohne Power over Ethernet."]),
         [f"Ist die {pid} ungebraucht?", f"Ja. Hexwaren führt die {pid} ausschließlich als versiegelte Original-Neuware."]]
    attrs=[["Modultyp","Linecard"],["Kompatible Serie",SERIE],["Portanzahl",str(n)],["Port-Konfiguration",portkonfig]]+poe_attr+[["Switching-Kapazität",SWK_MOD],["Zustand","Neu, versiegelt"]]
    return mk(pid,"Switch-Modul",gw2(price),price,
        f"HPE Aruba Networking 5400R zl2 {pid} Linecard – {short} für 5406R/5412R",
        f"Aruba 5400R zl2 {pid} Linecard | Hexwaren",
        f"Original HPE Aruba Networking 5400R zl2 {pid}: Linecard ({short}, MACsec) für die modularen Chassis Aruba 5406R/5412R zl2, ArubaOS-Switch. Modul, Chassis separat. Neu und versiegelt.",
        kurz,intro,faq,attrs)
def gw2(price): return "3,50"
def gen_mgmt(pid):
    return mk(pid,"Switch-Modul","2,50",5000,
      f"HPE Aruba Networking 5400R zl2 {pid} Management-Modul (Control-Plane, bis 2 redundant)",
      f"Aruba 5400R zl2 {pid} Management-Modul | Hexwaren",
      f"Original HPE Aruba Networking 5400R zl2 {pid}: Management-Modul (Control-Plane mit integrierter Fabric) für die modularen Chassis Aruba 5406R/5412R zl2, redundant und hot-swap. Modul, Chassis separat. Neu und versiegelt.",
      f"<p>Das HPE Aruba Networking 5400R zl2 {pid} ist das Management-Modul (Control-Plane) für die modularen Chassis der Aruba-5400R-zl2-Serie (5406R/5412R). Das {pid} steuert Routing, Switching und das Management des gesamten Chassis unter ArubaOS-Switch und trägt die integrierte Switch-Fabric.</p>"
      f"<p>Das {pid} ist hot-swap-fähig und lässt sich für Hochverfügbarkeit bis zu zweifach redundant betreiben (Nonstop-Switching). Es wird als versiegelte Original-Neuware geliefert.</p>",
      [f"Das HPE Aruba Networking 5400R zl2 {pid} ist das zentrale Management-Modul für die modularen Aruba-5400R-zl2-Chassis (5406R/5412R) unter ArubaOS-Switch. Als Control-Plane-Modul übernimmt das {pid} Routing, Switching-Steuerung und das Chassis-Management und trägt die integrierte Switch-Fabric des Chassis.",
       f"Das {pid} ist hot-swap-fähig; werden zwei Module installiert, arbeiten sie redundant und ermöglichen Nonstop-Switching, sodass das Chassis bei einem Ausfall unterbrechungsarm weiterläuft. Ein diskretes Fabric-Modul entfällt, da die Weiterleitung im {pid} integriert ist.",
       f"Kompatibel ist das {pid} mit den Chassis der Serie Aruba 5400R zl2; es dient Erweiterung, Redundanz und Ersatz und ist kein eigenständiger Switch. Geliefert wird das {pid} als versiegelte Original-Neuware. Originales HP-Modul."],
      [[f"Wofür wird das {pid} verwendet?", f"Das {pid} ist das Management-Modul (Control-Plane mit integrierter Fabric) für die Aruba-5400R-zl2-Chassis und steuert Routing, Switching und Chassis-Management."],
       [f"In welche Chassis passt das {pid}?", f"Das {pid} ist mit den Chassis der Serie Aruba 5400R zl2 (5406R/5412R) kompatibel und belegt den Management-Modul-Schacht."],
       [f"Ist das {pid} ein eigenständiger Switch?", f"Nein. Das {pid} ist ein Management-Modul und benötigt ein kompatibles Aruba-5400R-zl2-Chassis sowie zl2-Linecards."],
       [f"Ist das {pid} ungebraucht?", f"Ja. Hexwaren führt das {pid} ausschließlich als versiegelte Original-Neuware."]],
      [["Modultyp","Management-Modul"],["Kompatible Serie",SERIE],["Zustand","Neu, versiegelt"]])

MODULES={}
for pid,short,n,pk,poe,price in [
 ("J9986A","24× Gig-T PoE+",24,"24× 10/100/1000 (RJ45, Class 4 PoE+, MACsec)",poe_at,7000),
 ("J9987A","24× Gig-T",24,"24× 10/100/1000 (RJ45, MACsec)",None,5500),
 ("J9988A","24× SFP (1G)",24,"24× SFP (1G Glasfaser, MACsec)",None,6000),
 ("J9989A","12× Gig-T PoE+ + 12× SFP",24,"12× 10/100/1000 (RJ45, Class 4 PoE+) + 12× SFP (1G, MACsec)",poe_at,7200),
 ("J9990A","20× Gig-T PoE+ + 4× SFP+",24,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× SFP+ (1/10G, MACsec)",poe_at,8000),
 ("J9991A","20× Gig-T PoE+ + 4× Smart Rate",24,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× HPE Smart Rate (1/2.5/5/10GBASE-T, Class 4 PoE+, MACsec)",poe_at,9500),
 ("J9992A","20× Gig-T PoE+ + 1× QSFP+",21,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 1× QSFP+ (40G, MACsec)",poe_at,8500),
 ("J9993A","8× 10-GbE SFP+",8,"8× SFP+ (1/10G, MACsec)",None,7500),
 ("J9995A","8× Smart Rate (10GBASE-T) PoE+",8,"8× HPE Smart Rate (1/2.5/5/10GBASE-T, Class 4 PoE+, MACsec)",poe_at,9000),
 ("J9996A","2× QSFP+ (40G)",2,"2× QSFP+ (40G, MACsec)",None,8800),
]:
    MODULES[pid]=gen_line(pid,short,n,pk,poe,price)
MODULES["J9827A"]=gen_mgmt("J9827A")

# =================================================================== build (PRE-remap gate)
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
    write=__import__("hexcat.writers",fromlist=["write_csv"]).write_csv
    write(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{cat}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in doc_map:
        vrows.append([pid,doc_map[pid]["netto_vk"].replace('.',','),"PHASE-1-SCHÄTZUNG — NICHT marktgegroundet (5400R-zl2-Chassis/-Modul). Tier-Tarif. Echte HPE-Marktpreis-Recherche folgt.","geschätzt-Tier (PLATZHALTER)","—"])
    write(vp,tuple(vrows[0]),vrows[1:],",",False)
    return out

if __name__=="__main__":
    fams={"ch":("Aruba_5400R_zl2_Switches",CHASSIS),"mod":("Aruba_5400R_zl2_Modules",MODULES)}
    only=sys.argv[1] if len(sys.argv)>1 else None
    for k,(cat,dm) in fams.items():
        if only and k!=only: continue
        build(cat,dm)
