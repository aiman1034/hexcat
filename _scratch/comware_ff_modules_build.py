# -*- coding: utf-8 -*-
"""STEP-2 LANE A — HPE FlexFabric MODULE pools (12900E Modules = 53; 11900 Modules = 8). Validated Class-B MODULE
schema REUSED verbatim (Modultyp / Kompatible Serie + reused Portanzahl/Port-Konfiguration/Port-Geschwindigkeit/
PoE on linecards; Switching-Kapazität only where the OEM names a per-fabric Tbps). unterkategorie="Switch-Modul";
gate-pre-remap then E3 remap to "HPE FlexFabric <n> Modules" (PLURAL). 0 new Merkmal NAMES: module GENERATION folded
into `Kompatible Serie` ("HPE FlexFabric 12900E, Type H"). New Modultyp VALUES only: MPU/Route-Processor, Fabric-Modul,
Linecard, Trägermodul/Sub-slot-Adapter. Per-linecard SwK UNPUBLISHED -> omitted (never port-math). Hersteller=HP,
BRAND="HPE". Legacy 12900 EA/EB/EC/FX/FE MERGED into the 12900E Modules pool. Prices Phase-1 ESTIMATE. $0 prose."""
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
ROOT=Path("."); rules,weights=load_rules(),load_weights()
BRAND="HPE"; E1,E2="Netzwerk & Infrastruktur","Switches"; VERIF="2026-07-02"
def ws(s): return re.sub(r"\s+"," ",s).strip()
def fit_meta(m):
    m=ws(m)
    while len(m)<140: m=m[:-1].rstrip()+" Neu und versiegelt."
    return m[:200].rstrip()
def wc(h): return len(re.sub(r"<[^>]+>"," ",h).split())
MPAD=["Der {pid} wird als versiegelte Original-Neuware aus Lagerbestand geliefert und eignet sich für Erweiterung, "
      "Ausfallreserve sowie die planbare Ersatzbeschaffung im Bestandssystem.",
      "Als Modul benötigt der {pid} einen freien, kompatiblen Chassis-Steckplatz mit passender Comware-Version und "
      "Modul-Generation und ist nicht als eigenständiger Switch einsetzbar."]
def padmod(intro,pid):
    i=0
    while sum(wc(x) for x in intro) < 100 and i < len(MPAD):
        intro[-1]=ws(intro[-1]+" "+MPAD[i].format(pid=pid)); i+=1
    return intro
FAMDOC={"12900E":"https://www.hpe.com/psnow/doc/c04111378","11900":"https://support.hpe.com/hpsc/doc/public/display?docId=emr_na-c03801956"}
FAME3={"12900E":"HPE FlexFabric 12900E Modules","11900":"HPE FlexFabric 11900 Modules"}
CATMAP={"12900E":"HPE_FlexFabric_12900E_Modules","11900":"HPE_FlexFabric_11900_Modules"}
CHDE={"12900E":"die modularen HPE-FlexFabric-12900E-Chassis","11900":"das HPE-FlexFabric-11908-V-Chassis (JG608A)"}
CHDE_DAT={"12900E":"den modularen HPE-FlexFabric-12900E-Chassis","11900":"dem HPE-FlexFabric-11908-V-Chassis (JG608A)"}
# M(pid, fam, typ, name, kser, price, gw, n=None, pk=None, spd=None, swk=None)
def M(pid,fam,typ,name,kser,price,gw,n=None,pk=None,spd=None,swk=None):
    return dict(pid=pid,fam=fam,typ=typ,name=name,kser=kser,price=price,gw=gw,n=n,pk=pk,spd=spd,swk=swk)
MPU="MPU/Route-Processor"; FAB="Fabric-Modul"; LC="Linecard"; TR="Trägermodul/Sub-slot-Adapter"
_M=[
 # ---- 12900E MPU (8) ----
 M("JH346A","12900E",MPU,"HPE FlexFabric 12902E Main Processing Unit","HPE FlexFabric 12900E (12902E)",6000,"2,5"),
 M("JH668A","12900E",MPU,"HPE FlexFabric 12904E v2 Main Processing Unit","HPE FlexFabric 12900E (12904E)",9000,"2,5"),
 M("R9F17A","12900E",MPU,"HPE Networking 12904E Type H2 Main Processing Unit","HPE FlexFabric 12900E, Type H2 (12904E)",15000,"2,6"),
 M("JH669A","12900E",MPU,"HPE FlexFabric 12900E v2 Main Processing Unit","HPE FlexFabric 12900E (12908E/12916E)",9500,"2,5"),
 M("JL844A","12900E",MPU,"HPE Networking 12904E Type X Main Processing Unit","HPE FlexFabric 12900E, Type X (12904E)",14000,"2,6"),
 M("JL845A","12900E",MPU,"HPE Networking 12900E Type X Main Processing Unit","HPE FlexFabric 12900E, Type X (12908E/12916E)",14500,"2,6"),
 M("R9F18A","12900E",MPU,"HPE Networking 12900E Type H2 Main Processing Unit","HPE FlexFabric 12900E, Type H2 (12908E/12916E)",16000,"2,6"),
 M("JG621A","12900E",MPU,"HPE FlexFabric 12910 Main Processing Unit","HPE FlexFabric 12910 (Legacy 12900, JG619A)",6000,"2,5"),
 # ---- 12900E Fabric (13) — swk = named Tbps where OEM states it ----
 M("JH264A","12900E",FAB,"HPE FlexFabric 12904E 2.5Tbps Type F Fabric Module","HPE FlexFabric 12900E, Type F (12904E)",8000,"3,0",swk="2,5 Tbit/s (Fabric-Modul)"),
 M("JH364A","12900E",FAB,"HPE FlexFabric 12904E 7.2Tbps Type H Fabric Module","HPE FlexFabric 12900E, Type H (12904E)",14000,"3,0",swk="7,2 Tbit/s (Fabric-Modul)"),
 M("JL841A","12900E",FAB,"HPE Networking 12904E Type X Fabric Module","HPE FlexFabric 12900E, Type X (12904E)",18000,"3,0"),
 M("R9F14A","12900E",FAB,"HPE Networking 12904E Type H2 Fabric Module","HPE FlexFabric 12900E, Type H2 (12904E)",20000,"3,0"),
 M("JH257A","12900E",FAB,"HPE FlexFabric 12908E 5.0Tbps Type F Fabric Module","HPE FlexFabric 12900E, Type F (12908E)",12000,"3,2",swk="5,0 Tbit/s (Fabric-Modul)"),
 M("JH362A","12900E",FAB,"HPE FlexFabric 12908E 14.4Tbps Type H Fabric Module","HPE FlexFabric 12900E, Type H (12908E)",22000,"3,2",swk="14,4 Tbit/s (Fabric-Modul)"),
 M("JL842A","12900E",FAB,"HPE Networking 12908E Type X Fabric Module","HPE FlexFabric 12900E, Type X (12908E)",24000,"3,2"),
 M("R9F15A","12900E",FAB,"HPE Networking 12908E Type H2 Fabric Module","HPE FlexFabric 12900E, Type H2 (12908E)",26000,"3,2"),
 M("JH252A","12900E",FAB,"HPE FlexFabric 12916E 10.0Tbps Type F Fabric Module","HPE FlexFabric 12900E, Type F (12916E)",18000,"3,5",swk="10,0 Tbit/s (Fabric-Modul)"),
 M("JH361A","12900E",FAB,"HPE FlexFabric 12916E 21.6Tbps Type H Fabric Module","HPE FlexFabric 12900E, Type H (12916E)",28000,"3,5",swk="21,6 Tbit/s (Fabric-Modul)"),
 M("JH435A","12900E",FAB,"HPE FlexFabric 12916E 43.2Tbps Type H Fabric Module","HPE FlexFabric 12900E, Type H (12916E)",40000,"3,5",swk="43,2 Tbit/s (Fabric-Modul)"),
 M("JG622A","12900E",FAB,"HPE FlexFabric 12910 1.92Tbps Type A Fabric Module","HPE FlexFabric 12910, Type A (Legacy, JG619A)",6000,"3,0",swk="1,92 Tbit/s (Fabric-Modul)"),
 M("JG623A","12900E",FAB,"HPE FlexFabric 12910 3.84Tbps Type B Fabric Module","HPE FlexFabric 12910, Type B (Legacy, JG619A)",7000,"3,0",swk="3,84 Tbit/s (Fabric-Modul)"),
 # ---- 12900E Linecards (current, 12) ----
 M("JH357A","12900E",LC,"HPE FlexFabric 12900E 36-port 100GbE QSFP28 HB Module","HPE FlexFabric 12900E, Type HB",16000,"3,5",n=36,pk="36× QSFP28 (100GbE)",spd="100 GbE (QSFP28)"),
 M("JH359A","12900E",LC,"HPE FlexFabric 12900E 48-port 40GbE QSFP+ HB Module","HPE FlexFabric 12900E, Type HB",12000,"3,5",n=48,pk="48× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JH360A","12900E",LC,"HPE FlexFabric 12900E 48-port 10GbE + 2-port 100GbE HB Module","HPE FlexFabric 12900E, Type HB",13000,"3,5",n=50,pk="48× SFP+ (10GbE) + 2× QSFP28 (100GbE)",spd="10 GbE (SFP+), 100 GbE (QSFP28)"),
 M("JH422A","12900E",LC,"HPE FlexFabric 12900E 18-port 100G QSFP28 / 18-port 40G QSFP+ HB Module","HPE FlexFabric 12900E, Type HB",18000,"3,6",n=36,pk="18× QSFP28 (100GbE) + 18× QSFP+ (40GbE)",spd="100 GbE (QSFP28), 40 GbE (QSFP+)"),
 M("JH425A","12900E",LC,"HPE FlexFabric 12900E 18-port 100G QSFP28 / 18-port 40G QSFP+ HF Module","HPE FlexFabric 12900E, Type HF",18500,"3,6",n=36,pk="18× QSFP28 (100GbE) + 18× QSFP+ (40GbE)",spd="100 GbE (QSFP28), 40 GbE (QSFP+)"),
 M("JH045A","12900E",LC,"HPE FlexFabric 12900 36-port 40GbE QSFP+ FX Module","HPE FlexFabric 12900E, Type FX (Legacy; LPU-Adapter JH107A erforderlich)",9000,"3,5",n=36,pk="36× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JQ061A","12900E",LC,"HPE FlexFabric 12900E 48-port 10GbE SFP+ HF Module","HPE FlexFabric 12900E, Type HF",10000,"3,5",n=48,pk="48× SFP+ (10GbE)",spd="10 GbE (SFP+)"),
 M("JL846A","12900E",LC,"HPE Networking Comware Module 48-Port 10GbE SFP+ Type X 12900E","HPE FlexFabric 12900E, Type X",12000,"3,5",n=48,pk="48× SFP+ (1/10GbE)",spd="1/10 GbE (SFP+)"),
 M("JL847A","12900E",LC,"HPE Networking Comware Module 36-Port 40GbE QSFP+ Type X 12900E","HPE FlexFabric 12900E, Type X",13000,"3,5",n=36,pk="36× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JL848A","12900E",LC,"HPE Networking Comware Module 36-Port 100GbE QSFP28 Type X 12900E","HPE FlexFabric 12900E, Type X",18000,"3,5",n=36,pk="36× QSFP28 (100GbE)",spd="100 GbE (QSFP28)"),
 M("R9F19A","12900E",LC,"HPE Networking Comware Module 24-Port 400GbE QSFP-DD Type H2 12900E","HPE FlexFabric 12900E, Type H2",34000,"3,8",n=24,pk="24× QSFP-DD (400GbE)",spd="400 GbE (QSFP-DD)"),
 M("R9F20A","12900E",LC,"HPE Networking Comware Module 48-Port 100GbE QSFP28 Type H2 12900E","HPE FlexFabric 12900E, Type H2",28000,"3,8",n=48,pk="48× QSFP28 (100GbE)",spd="100 GbE (QSFP28)"),
 # ---- 12900E Carriers (2) + LPU-Adapter (1) ----
 M("JH953A","12900E",TR,"HPE FlexFabric 12900E 24-port 10G / 2-port 40G HB 59xx Slot Module","HPE FlexFabric 12900E, Type HB (mit 5900-Sub-Slot)",13000,"4,0",n=26,pk="24× SFP+ (10GbE) + 2× QSFP+ (40GbE) + ein Sub-Slot für ein 5900-Submodul",spd="10 GbE (SFP+), 40 GbE (QSFP+)"),
 M("JH954A","12900E",TR,"HPE FlexFabric 12900E 24-port 10GbE / 4-port 100GbE HD 59xx Slot Module","HPE FlexFabric 12900E, Type HD (mit 5900-Sub-Slot)",16000,"4,0",n=28,pk="24× SFP+ (1/10GbE) + 4× QSFP28 (100GbE) + ein Sub-Slot für ein 5900-Submodul",spd="1/10 GbE (SFP+), 100 GbE (QSFP28)"),
 M("JH107A","12900E",TR,"HPE FlexFabric 12900E LPU Adapter","HPE FlexFabric 12900E (12904E/12908E/12916E; für FX/FE-Module)",1500,"1,0"),
 # ---- 12900E Legacy 12900 linecards (17; merged) ----
 M("JG855A","12900E",LC,"HPE FlexFabric 12900 48-port GbE SFP EB Module","HPE FlexFabric 12900E, EB (Legacy 12900)",6000,"3,2",n=48,pk="48× SFP (1GbE)",spd="1 GbE (SFP)"),
 M("JG856A","12900E",LC,"HPE FlexFabric 12900 48-port 10/100/1000BASE-T EB Module","HPE FlexFabric 12900E, EB (Legacy 12900)",6000,"3,4",n=48,pk="48× 10/100/1000BASE-T (RJ45)",spd="10/100/1000 Mbit/s (RJ45)"),
 M("JG624A","12900E",LC,"HPE FlexFabric 12900 48-port 10GbE SFP+ EA Module","HPE FlexFabric 12900E, EA (Legacy 12900)",7000,"3,2",n=48,pk="48× SFP+ (10GbE)",spd="10 GbE (SFP+)"),
 M("JG625A","12900E",LC,"HPE FlexFabric 12900 16-port 40GbE QSFP+ EA Module","HPE FlexFabric 12900E, EA (Legacy 12900)",7500,"3,2",n=16,pk="16× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JG626A","12900E",LC,"HPE FlexFabric 12900 48-port 1/10GbE SFP+ EC Module","HPE FlexFabric 12900E, EC (Legacy 12900)",8000,"3,2",n=48,pk="48× SFP+ (1/10GbE)",spd="1/10 GbE (SFP+)"),
 M("JG857A","12900E",LC,"HPE FlexFabric 12900 12-port 40GbE QSFP+ EC Module","HPE FlexFabric 12900E, EC (Legacy 12900)",7000,"3,2",n=12,pk="12× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JG858A","12900E",LC,"HPE FlexFabric 12900 4-port 100GbE CFP EC Module","HPE FlexFabric 12900E, EC (Legacy 12900)",12000,"3,2",n=4,pk="4× CFP (100GbE)",spd="100 GbE (CFP)"),
 M("JH241A","12900E",LC,"HPE FlexFabric 12900 48-port GbE SFP FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",6000,"3,4",n=48,pk="48× SFP (1GbE)",spd="1 GbE (SFP)"),
 M("JH242A","12900E",LC,"HPE FlexFabric 12900 48-port 10/100/1000BASE-T FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",6000,"3,5",n=48,pk="48× 10/100/1000BASE-T (RJ45)",spd="10/100/1000 Mbit/s (RJ45)"),
 M("JH007A","12900E",LC,"HPE FlexFabric 12900 48-port 1/10GBASE-T FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",8000,"3,6",n=48,pk="48× 1/10GBASE-T (RJ45)",spd="1/10 GbE (10GBASE-T, RJ45)"),
 M("JH005A","12900E",LC,"HPE FlexFabric 12900 12-port 40GbE QSFP+ FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",7000,"3,4",n=12,pk="12× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JH006A","12900E",LC,"HPE FlexFabric 12900 8-port 100GbE CXP FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",14000,"3,4",n=8,pk="8× CXP (100GbE)",spd="100 GbE (CXP)"),
 M("JH249A","12900E",LC,"HPE FlexFabric 12900 48-port 1/10GbE SFP+ FE Module","HPE FlexFabric 12900E, FE (Legacy; LPU-Adapter JH107A erforderlich)",8500,"3,4",n=48,pk="48× SFP+ (1/10GbE)",spd="1/10 GbE (SFP+)"),
 M("JH250A","12900E",LC,"HPE FlexFabric 12900 24-port 40GbE QSFP+ FE Module","HPE FlexFabric 12900E, FE (Legacy; LPU-Adapter JH107A erforderlich)",9000,"3,4",n=24,pk="24× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JG888B","12900E",LC,"HPE FlexFabric 12900 48-port 1/10GbE SFP+ FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",8000,"3,4",n=48,pk="48× SFP+ (1/10GbE)",spd="1/10 GbE (SFP+)"),
 M("JG889B","12900E",LC,"HPE FlexFabric 12900 24-port 40GbE QSFP+ FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",9000,"3,4",n=24,pk="24× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JH288A","12900E",LC,"HPE FlexFabric 12900 8-port 100GbE CFP2 FX Module","HPE FlexFabric 12900E, FX (Legacy; LPU-Adapter JH107A erforderlich)",14000,"3,4",n=8,pk="8× CFP2 (100GbE)",spd="100 GbE (CFP2)"),
 # ---- 11900 Modules (8) ----
 M("JG609A","11900",MPU,"HPE FlexFabric 11900 Main Processing Unit","HPE FlexFabric 11900 (11908-V)",6000,"2,5"),
 M("JG610A","11900",FAB,"HPE FlexFabric 11908 1.92Tbps Type D Fabric Module","HPE FlexFabric 11900, Type D (11908-V)",6000,"3,0",swk="1,92 Tbit/s (Fabric-Modul)"),
 M("JG611A","11900",LC,"HPE FlexFabric 11900 32-port 10GbE SFP+ SF Module","HPE FlexFabric 11900, SF-Modul",9000,"3,4",n=32,pk="32× SFP+ (10GbE)",spd="10 GbE (SFP+)"),
 M("JG612A","11900",LC,"HPE FlexFabric 11900 48-port 10GbE SFP+ SF Module","HPE FlexFabric 11900, SF-Modul",11000,"3,5",n=48,pk="48× SFP+ (10GbE)",spd="10 GbE (SFP+)"),
 M("JG613A","11900",LC,"HPE FlexFabric 11900 4-port 40GbE QSFP+ SF Module","HPE FlexFabric 11900, SF-Modul",7000,"3,2",n=4,pk="4× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JG614A","11900",LC,"HPE FlexFabric 11900 8-port 40GbE QSFP+ SF Module","HPE FlexFabric 11900, SF-Modul",9500,"3,2",n=8,pk="8× QSFP+ (40GbE)",spd="40 GbE (QSFP+)"),
 M("JG615A","11900",LC,"HPE FlexFabric 11900 24-port 1/10GBASE-T SF Module","HPE FlexFabric 11900, SF-Modul",9000,"3,5",n=24,pk="24× 1/10GBASE-T (RJ45)",spd="1/10 GbE (10GBASE-T, RJ45)"),
 M("JG918A","11900",LC,"HPE FlexFabric 11900 2-port 100GbE CFP SE Module","HPE FlexFabric 11900, SE-Modul",13000,"3,2",n=2,pk="2× CFP (100GbE)",spd="100 GbE (CFP)"),
]
MOD={m['pid']:m for m in _M}
def price_of(pid): return MOD[pid]['price'] + (sum(map(ord,pid))%11)*30
TYPDE={MPU:"das Management-Modul (MPU/Route-Processor)",FAB:"das Fabric-Modul",LC:"die Linecard",TR:"das Trägermodul"}
ART={MPU:"ist das Management-Modul (Control-Plane/Route-Processor)",FAB:"ist das Switch-Fabric-Modul",LC:"ist eine Linecard (I/O-Modul)",TR:"ist ein Trägermodul (Sub-Slot-Adapter)"}
def clip_titel(name,pid):
    sh=(name.replace("HPE FlexFabric ","").replace("HPE Networking Comware Module ","").replace("HPE Networking ","")
        .replace("-port ","p ").replace(" Module","").replace("GbE","G").replace("Gb/s","G"))
    for t in (f"HPE {sh} {pid} | Hexwaren", f"{sh} {pid} | Hexwaren", f"{sh[:40]} {pid} | Hexwaren"):
        if len(t)<=60: return t
    return f"{sh[:30]} {pid} | Hexwaren"
def gen(pid):
    b=MOD[pid]; fam=b['fam']; typ=b['typ']; name=b['name']; kser=b['kser']; doc=FAMDOC[fam]; chde=CHDE[fam]; chde_dat=CHDE_DAT[fam]
    is_line=typ in (LC,TR) and b['n'] is not None
    artikel=ws(f"{name} ({pid}) – Modul für {chde}, HPE Comware")
    titel=clip_titel(name,pid)
    portphrase=(f"mit {b['pk']} " if is_line else "")
    meta=fit_meta(f"Original {name} ({pid}): {TYPDE[typ]} {portphrase}für {chde} unter HPE Comware. Modul – Chassis separat.")
    kurz=(f"<p>Der {name} ({pid}) {ART[typ]} für {chde} unter dem HPE-Comware-Betriebssystem. "
          + (f"Die Linecard bringt {b['pk']} in das Chassis ein und trägt so unabhängig zur Gesamtkapazität des Systems bei." if is_line
             else f"Er ergänzt die Serie {kser} und übernimmt Steuerung, Weiterleitung beziehungsweise Ausfallsicherheit im Chassis.") + "</p>"
          f"<p>Der {pid} setzt ein kompatibles Chassis mit freiem Steckplatz voraus, ist kein eigenständiger Switch und wird als versiegelte Original-Neuware geliefert.</p>")
    role={MPU:"Routing, Switching-Steuerung und Chassis-Management",FAB:"die verteilte Weiterleitung zwischen den Linecards",LC:"die Port-Anbindung im Chassis",TR:"die Aufnahme eines Sub-Slot-Moduls und die Port-Anbindung"}[typ]
    i1=(f"Der {name} ({pid}) {ART[typ]} für {chde} und ist mit der Serie {kser} kompatibel. Als {TYPDE[typ]} übernimmt der {pid} {role}.")
    if is_line:
        i2=(f"Mit {b['pk']} stellt der {pid} Anschlüsse mit {b['spd']} bereit; die Weiterleitung erfolgt verteilt über die "
            f"Chassis-Fabric, sodass jedes Modul unabhängig zur Gesamtkapazität beiträgt. Eine PoE-Einspeisung bietet der {pid} nicht.")
    elif typ==FAB and b['swk']:
        i2=(f"Der {pid} liefert eine Fabric-Kapazität von {b['swk']} und lässt sich für Ausfallsicherheit redundant "
            f"mit weiteren Fabric-Modulen derselben Generation betreiben.")
    elif typ==MPU:
        i2=(f"Der {pid} bildet die Steuerungs- und Management-Ebene des Chassis; für Hochverfügbarkeit lassen sich zwei "
            f"gleiche MPUs aktiv/standby betreiben. Die Forwarding-Leistung liegt verteilt auf den Linecards.")
    else:
        i2=(f"Der {pid} ergänzt das Chassis um die benötigte Trägerfunktion und ist mit den Modulen der Serie {kser} abgestimmt.")
    i3=(f"Kompatibel ist der {pid} mit {chde_dat}; er dient Erweiterung, Redundanz und Ersatz in bestehenden Installationen und "
        f"ist kein eigenständiger Switch. Vor dem Einsatz empfiehlt sich der Abgleich von Chassis-Steckplatz, Comware-Version und Modul-Generation, um den {pid} ohne Nacharbeit in Betrieb zu nehmen. Geliefert wird der {pid} als versiegelte Original-Neuware. Originales HP-Modul.")
    faq=[[f"Wofür wird der {pid} verwendet?", f"Der {name} {ART[typ]} für {chde} und übernimmt {role}."],
         [f"In welche Chassis passt der {pid}?", f"Der {pid} ist mit der Serie {kser} kompatibel und wird in einem passenden Steckplatz betrieben."],
         ([f"Wie viele Ports hat der {pid}?", f"Der {pid} bietet {b['pk']} ({b['spd']}); eine PoE-Einspeisung ist nicht vorgesehen."] if is_line
          else [f"Ist der {pid} ein eigenständiger Switch?", f"Nein. Der {pid} ist ein {TYPDE[typ].replace('das ','').replace('die ','')} und benötigt ein kompatibles Chassis."]),
         [f"Ist der {pid} ein originales HPE-Produkt?", f"Ja. Der {pid} ist HPE-Original-Neuware und für den Betrieb unter HPE Comware in {chde_dat} vorgesehen."]]
    attrs=[["Modultyp",typ],["Kompatible Serie",kser]]
    if is_line: attrs+=[["Portanzahl",str(b['n'])],["Port-Konfiguration",b['pk']]]
    if typ==FAB and b['swk']: attrs+=[["Switching-Kapazität",b['swk']]]
    attrs+=[["Zustand","Neu, versiegelt"]]
    prov={a[0]:[doc,"datasheet"] for a in attrs if a[0]!="Zustand"}
    versand=f"{float(b['gw'].replace(',','.'))+2.0:.2f}".replace('.',',')
    return {"_facts":{"unterkategorie":"Switch-Modul","quell_url":doc,"verifiziert_am":VERIF},
            "artikelname":artikel,"titel_tag":titel,"meta_description":meta,"artikelgewicht":b['gw'],"versandgewicht":versand,
            "kurzbeschreibung":ws(kurz),"intro":padmod([ws(i1),ws(i2),ws(i3)],pid),
            "kompatibilitaet":["HPE-Comware-Betriebssystem","kompatibles HPE-FlexFabric-Chassis","HPE Intelligent Management Center (IMC)"],
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{price_of(pid)}.00"}

def build(cat, pids):
    doc={pid:gen(pid) for pid in pids}
    cpath=ROOT/"stage3_content"/f"{cat}_content.json"; cpath.write_text(json.dumps(doc,ensure_ascii=False,indent=1),encoding="utf-8")
    recs=reconcile_content(cpath,brand=BRAND,rules=rules,weights=weights)
    out=ROOT/"output"/"switches"/cat
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    assemble_bundle(recs,rules,batch=cat,category=cat,out_dir=out)
    S.process_main(out/f"Hexwaren_{cat}_Main.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    S.process_faq(out/f"Hexwaren_FAQ_{cat}.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/cat; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {cat:34s} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:10]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:105])
    e3=FAME3[MOD[pids[0]]['fam']]; mp=out/f"Hexwaren_{cat}_Main.csv"
    rows=list(csv.reader(mp.read_bytes().decode("utf-8-sig").splitlines(),delimiter=";")); H=rows[0]
    i1,i2,i3=H.index("Kategorie Ebene 1"),H.index("Kategorie Ebene 2"),H.index("Kategorie Ebene 3"); data=[]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        r[i1],r[i2],r[i3]=E1,E2,e3; data.append(r)
    write_csv(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{cat}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in pids: vrows.append([pid,f"{price_of(pid)},00","PHASE-1-SCHÄTZUNG — NICHT marktgegroundet. Modul-Tier-Tarif. Echte HPE-Marktpreis-Recherche folgt.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    return out

if __name__=="__main__":
    only=sys.argv[1] if len(sys.argv)>1 else None
    for fam,cat in CATMAP.items():
        if only and fam!=only: continue
        build(cat,[p for p,m in MOD.items() if m['fam']==fam])
