# -*- coding: utf-8 -*-
"""STEP-2 ArubaOS-Switch PHASE 2b: legacy ProCurve/HP FIXED tail (44 SKUs, 10 families).
15 fixed-switch Merkmale; 0 new Merkmal NAMES. All EOL — grounded verbatim from the QuickSpecs Models/spec
tables (cached hpe-aruba/*.txt for 2615/2620/2915/3500; web-mirror QuickSpecs for 2510/2610/2810/2910al/3800/6600),
per-model SwK/Durchsatz/PoE-budget read cell-by-cell, never port-math. ProVision/ProCurve prose (NOT ArubaOS-Switch).
Un-published PoE budgets (2610-PWR, 2910al-PoE+, 3800-PoE+) rephrased customer-safe (never ship ZU_VERIFIZIEREN).
Hersteller = HP. E3 per operator: HP ProCurve <model> Switches (ProCurve era) + HP 3800 Switches (post-ProCurve).
Prices PHASE-1 ESTIMATE (flagged). $0 prose. Reuses the locked pipeline (reconcile->assemble->scrub->remap->gate)."""
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
BRAND = "Aruba"; E1, E2 = "Netzwerk & Infrastruktur", "Switches"; VERIF = "2026-07-01"
def ws(s): return re.sub(r"\s+", " ", s).strip()

# ---- per-family defaults: E3, Layer, Stacking, Betriebstemp, Anwendung, feat-key, QuickSpec doc ----
FAM = {
 "2510":  dict(e3="HP ProCurve 2510 Switches",  lyr="L2", feat="L2",  btemp="0 bis 45 °C",
   stk="Kein (Standalone; Single-IP-Virtual-Stacking-Verwaltung bis 16 Einheiten)",
   anw="Managed Layer-2-Fast-Ethernet-Edge-Access (ProVision) für Anschlussbereiche",
   doc="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c02485763"),
 "2610":  dict(e3="HP ProCurve 2610 Switches",  lyr="L2", feat="L2R", btemp="0 bis 50 °C",
   stk="Kein (Standalone; Single-IP-Virtual-Stacking-Verwaltung bis 16 Einheiten)",
   anw="Managed Layer-2-Edge-Access mit statischem IPv4-Routing (ProVision)",
   doc="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c01518375"),
 "2615":  dict(e3="HP ProCurve 2615 Switches",  lyr="L2", feat="L2R", btemp="0 bis 45 °C",
   stk="Kein (Standalone)",
   anw="Managed Layer-2-PoE-Edge-Access mit statischem Routing (ProVision)",
   doc="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c02051444"),
 "2620":  dict(e3="HP ProCurve 2620 Switches",  lyr="L3", feat="L3",  btemp="0 bis 55 °C",
   stk="Kein (Standalone)",
   anw="Managed Layer-3-Lite-Access (ProVision) mit statischem und RIP-Routing",
   doc="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c04003242"),
 "2810":  dict(e3="HP ProCurve 2810 Switches",  lyr="L2", feat="L2",  btemp="0 bis 45 °C",
   stk="Kein (Standalone; Single-IP-Virtual-Stacking-Verwaltung bis 16 Einheiten)",
   anw="Managed Layer-2-Gigabit-Access (ProVision) mit Dual-Personality-Uplinks",
   doc="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c02516905"),
 "2910al":dict(e3="HP ProCurve 2910al Switches",lyr="L3", feat="L3",  btemp="0 bis 55 °C",
   stk="Kein (Standalone; Single-IP-Virtual-Stacking-Verwaltung bis 16 Einheiten)",
   anw="Managed Layer-3-Lite-Campus-Access/-Aggregation (ProVision) mit optionalen 10-GbE-Uplinks",
   doc="https://www.hpe.com/psnow/doc/c01844343"),
 "2915":  dict(e3="HP ProCurve 2915 Switches",  lyr="L3", feat="L3",  btemp="0 bis 45 °C",
   stk="Kein (Standalone)",
   anw="Managed Layer-3-Lite-PoE-Access (ProVision) für kleine Standorte",
   doc="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c02051445"),
 "3500":  dict(e3="HP ProCurve 3500 Switches",  lyr="L3", feat="L3OSPF", btemp="0 bis 55 °C",
   stk="Kein (kein dedizierter Stacking-Bus; Ausfallsicherheit über HP-Switch-Meshing und Distributed Trunking)",
   anw="Managed Layer-3-Campus-Access/-Aggregation (ProVision) mit optionalem 10-GbE-Modul",
   doc="https://www.hpe.com/psnow/doc/c01813146"),
 "3800":  dict(e3="HP 3800 Switches",           lyr="L3", feat="L3BGP", btemp="0 bis 55 °C",
   stk="Meshed Stacking (dediziertes Stacking-Modul J9577A, bis 10 Einheiten, bis 336 Gbit/s)",
   anw="Managed Layer-3-Campus-Aggregation (HP Networking, ProVision) mit Meshed-Stacking",
   doc="https://www.hpe.com/psnow/doc/c04111485"),
 "6600":  dict(e3="HP ProCurve 6600 Switches",  lyr="L3", feat="L34",  btemp="5 bis 40 °C",
   stk="Kein (kein dedizierter Stacking-Bus; Ausfallsicherheit über HP-Switch-Meshing und Distributed Trunking)",
   anw="Managed Layer-3/4-Rechenzentrums-Server-Edge (ProVision) mit redundanten Hot-Swap-Netzteilen",
   doc="https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c01881713"),
}
FEAT={"L2":"Layer-2-Funktionen unter ProVision: VLANs, ACLs, QoS, LACP, Spanning Tree und IGMP-Snooping",
      "L2R":"Layer-2-Funktionen mit statischem IPv4-Routing unter ProVision: VLANs, ACLs, QoS, LACP und Spanning Tree",
      "L3":"Layer-3-Routing (statisch und RIP) unter ProVision, dazu VLANs, ACLs, QoS, LACP und Spanning Tree",
      "L3OSPF":"Layer-3-Routing (statisch, RIP; OSPF/BGP/IPv6 per Premium-Lizenz) unter ProVision, dazu VLANs, ACLs, QoS und Switch-Meshing",
      "L3BGP":"Layer-3-Routing (statisch, RIP, OSPF, BGP, IPv6) unter ProVision, dazu VLANs, ACLs, QoS, LACP und Meshed-Stacking",
      "L34":"Layer-3/4-Routing (statisch, RIP; OSPF/OSPFv3 per Premium-Lizenz) unter ProVision für den Rechenzentrums-Server-Edge"}
POS={"2510":"Der {pid} bringt gemanagten Fast-Ethernet-Zugang in Anschlussräume und kleine Büros.",
     "2610":"Der {pid} kombiniert Fast-Ethernet-Zugang mit statischem IPv4-Routing am Netzwerkrand.",
     "2615":"Der {pid} versorgt als kompakter PoE-Switch Telefone, Kameras und Access Points am Edge.",
     "2620":"Der {pid} verbindet Fast-Ethernet-Zugang mit statischem und RIP-Routing für kleine Standorte.",
     "2810":"Der {pid} liefert gemanagten Gigabit-Zugang mit vier Dual-Personality-Uplinks.",
     "2910al":"Der {pid} skaliert den Gigabit-Zugang über optionale 10-GbE-Module bis in die Aggregation.",
     "2915":"Der {pid} bündelt Gigabit-PoE-Zugang und statisches/RIP-Routing im kompakten Gehäuse.",
     "3500":"Der {pid} vereint Layer-3-Routing mit einem optionalen 10-GbE-Modul für den Etagenverteiler.",
     "3800":"Der {pid} fügt sich per Meshed-Stacking zu einem ausfallsicheren Aggregations-Verbund zusammen.",
     "6600":"Der {pid} bedient mit redundanten Hot-Swap-Netzteilen den Server-Edge im Rechenzentrum."}
RACK="19-Zoll-Rackmontage (1 HE)"; COMPACT="Kompakt (1 HE, halbe Breite)"
KF="Lüfterlos (passiv gekühlt)"; KL="Lüftergekühlt"; KFB="Lüftergekühlt (Airflow front-to-back)"
K66="Lüftergekühlt (N+N-Hot-Swap-Lüftertray, front-to-back reversibel)"
PSU_INT="Internes Festnetzteil"; PSU_2610="Internes Festnetzteil (optional externe RPS-/EPS-Absicherung über HP 600)"
PSU_2810="Internes Festnetzteil (optional externe RPS über HP 600)"; PSU_2910="Internes Netzteil (optional externe RPS über HP ProCurve 620)"
PSU_3500="Internes AC-Netzteil (optional externe EPS/RPS über HP 620/630)"
PSU_3800="2 Hot-Swap-Netzteilschächte (X311 400 W oder X312 1000 W; ein Netzteil enthalten, redundant erweiterbar)"
PSU_6600="2 Hot-Swap-Netzteilschächte (1× J9269A enthalten, lastverteilt redundant)"
SPD_FE="10/100 Mbit/s (RJ45, Access), 10/100/1000 Mbit/s (Uplink)"
SPD_G="10/100/1000 Mbit/s (RJ45)"; SPD_G_SFP="10/100/1000 Mbit/s (RJ45), 1 GbE (SFP)"
SPD_G_SFPP="10/100/1000 Mbit/s (RJ45), 1/10 GbE (SFP+)"; SPD_G_XG="10/100/1000 Mbit/s (RJ45), 10 GbE (10GBASE-T, RJ45)"
SPD_SFP_SFPP="100/1000 Mbit/s (SFP), 1/10 GbE (SFP+)"; SPD_10G="10 GbE (SFP+)"
U_DUAL2="2× Dual-Personality-Ports (RJ45 10/100/1000 oder SFP 1G)"; U_DUAL4="4× Dual-Personality-Ports (RJ45 10/100/1000 oder SFP 1G)"
U_FE="2× 10/100/1000 (RJ45) + 2× SFP (1G)"
poe_af=lambda w:f"Ja (IEEE 802.3af Class 3, 15,4 W/Port, Budget {w} W)"
poe_at=lambda w:f"Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port, Budget {w} W)"
poe_af12="Ja (IEEE 802.3af Class 3, 15,4 W/Port, Budget 124 W an bis zu 12 Ports)"
poe_af_eps="Ja (IEEE 802.3af Class 3, 15,4 W/Port; Gesamt-PoE-Budget abhängig von interner Speisung bzw. externem EPS)"
poe_at_psu="Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port; Gesamt-PoE-Budget abhängig von der Netzteilbestückung)"
poe_at_x312="Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port; Gesamt-PoE-Budget abhängig von der Netzteilbestückung mit X312-1000-W-Netzteil)"

def P(fam,model,n,acc,up,upmod,spd,poe,swk,mpps,bauform,strom,kueh,price,gw,**kw):
    d=dict(fam=fam,model=model,n=n,acc=acc,up=up,up_modular=upmod,spd=spd,poe=poe,swk=swk,mpps=mpps,
           bauform=bauform,strom=strom,kueh=kueh,price=price,gw=gw); d.update(kw); return d

SPECS={
 # ===== 2510 (4) — L2 =====
 "J9019B":P("2510","ProCurve 2510-24",26,"24× 10/100 (RJ45)",U_DUAL2,False,SPD_FE,"Nein","8,8 Gbit/s","6,5 Mpps",RACK,PSU_INT,KF,180,"2,22"),
 "J9020A":P("2510","ProCurve 2510-48",52,"48× 10/100 (RJ45)",U_FE,False,SPD_FE,"Nein","17,6 Gbit/s","13 Mpps",RACK,PSU_INT,KL,280,"2,74"),
 "J9279A":P("2510","ProCurve 2510G-24",24,"20× 10/100/1000 (RJ45)",U_DUAL4,False,SPD_G_SFP,"Nein","48 Gbit/s","35,7 Mpps",RACK,PSU_INT,KL,320,"3,27"),
 "J9280A":P("2510","ProCurve 2510G-48",48,"44× 10/100/1000 (RJ45)",U_DUAL4,False,SPD_G_SFP,"Nein","96 Gbit/s","71,4 Mpps",RACK,PSU_INT,KL,480,"3,90"),
 # ===== 2610 (5) — L2 + static routing, 0-50°C, 2×GbE + 2×SFP uplink =====
 "J9085A":P("2610","ProCurve 2610-24",28,"24× 10/100 (RJ45)",U_FE,False,SPD_FE,"Nein","12,8 Gbit/s","9,5 Mpps",RACK,PSU_2610,KF,240,"4,63"),
 "J9086A":P("2610","ProCurve 2610-24/12PWR",28,"12× 10/100 (RJ45, Class 3 PoE) + 12× 10/100 (RJ45)",U_FE,False,SPD_FE,poe_af12,"12,8 Gbit/s","9,5 Mpps",RACK,PSU_2610,KL,340,"3,40"),
 "J9087A":P("2610","ProCurve 2610-24-PWR",28,"24× 10/100 (RJ45, Class 3 PoE)",U_FE,False,SPD_FE,poe_af_eps,"12,8 Gbit/s","9,5 Mpps",RACK,PSU_2610,KL,420,"6,83"),
 "J9088A":P("2610","ProCurve 2610-48",52,"48× 10/100 (RJ45)",U_FE,False,SPD_FE,"Nein","17,6 Gbit/s","13 Mpps",RACK,PSU_2610,KL,360,"4,88"),
 "J9089A":P("2610","ProCurve 2610-48-PWR",52,"48× 10/100 (RJ45, Class 3 PoE)",U_FE,False,SPD_FE,poe_af_eps,"17,6 Gbit/s","13 Mpps",RACK,PSU_2610,KL,560,"7,58"),
 # ===== 2615 (1) — L2 + static, compact PoE FE =====
 "J9565A":P("2615","ProCurve 2615-8-PoE",10,"8× 10/100 (RJ45, Class 3 PoE)",U_DUAL2,False,SPD_FE,poe_af(67),"5,6 Gbit/s","4,1 Mpps",COMPACT,PSU_INT,KF,250,"1,66"),
 # ===== 2620 (5) — L3 (static+RIP), 0-55°C, N×FE + 2×GbE + 2×SFP =====
 "J9623A":P("2620","ProCurve 2620-24",28,"24× 10/100 (RJ45)",U_FE,False,SPD_FE,"Nein","12,8 Gbit/s","9,5 Mpps",RACK,PSU_INT,KF,240,"2,59"),
 "J9624A":P("2620","ProCurve 2620-24-PPoE+",28,"12× 10/100 (RJ45, Class 4 PoE+) + 12× 10/100 (RJ45)",U_FE,False,SPD_FE,poe_at(128),"12,8 Gbit/s","9,5 Mpps",RACK,PSU_INT,KL,320,"3,19"),
 "J9625A":P("2620","ProCurve 2620-24-PoE+",28,"24× 10/100 (RJ45, Class 4 PoE+)",U_FE,False,SPD_FE,poe_at(382),"12,8 Gbit/s","9,5 Mpps",RACK,PSU_INT,KL,420,"4,84"),
 "J9626A":P("2620","ProCurve 2620-48",52,"48× 10/100 (RJ45)",U_FE,False,SPD_FE,"Nein","17,6 Gbit/s","13 Mpps",RACK,PSU_INT,KL,340,"2,94"),
 "J9627A":P("2620","ProCurve 2620-48-PoE+",52,"48× 10/100 (RJ45, Class 4 PoE+)",U_FE,False,SPD_FE,poe_at(382),"17,6 Gbit/s","13 Mpps",RACK,PSU_INT,KL,540,"5,23"),
 # ===== 2810 (2) — L2 Gigabit =====
 "J9021A":P("2810","ProCurve 2810-24G",24,"20× 10/100/1000 (RJ45)",U_DUAL4,False,SPD_G_SFP,"Nein","48 Gbit/s","35,7 Mpps",RACK,PSU_2810,KL,340,"3,27"),
 "J9022A":P("2810","ProCurve 2810-48G",48,"44× 10/100/1000 (RJ45)",U_DUAL4,False,SPD_G_SFP,"Nein","96 Gbit/s","71,4 Mpps",RACK,PSU_2810,KL,480,"3,90"),
 # ===== 2915 (1) — L3-lite compact PoE Gigabit =====
 "J9562A":P("2915","ProCurve 2915-8G-PoE",10,"8× 10/100/1000 (RJ45, Class 3 PoE)",U_DUAL2,False,SPD_G_SFP,poe_af(67),"20 Gbit/s","14,8 Mpps",COMPACT,PSU_INT,KF,350,"1,66"),
 # ===== 2910al (4) — L3-lite, 4×dual-personality + module uplinks =====
 "J9145A":P("2910al","ProCurve 2910al-24G",24,"20× 10/100/1000 (RJ45) + 4× Dual-Personality (RJ45 oder SFP 1G)","2 Modulschächte (optional bis 4× 10-GbE über CX4-/SFP+-Module, separat)",True,SPD_G_SFP,"Nein","128 Gbit/s","95 Mpps",RACK,PSU_2910,KL,560,"4,95"),
 "J9146A":P("2910al","ProCurve 2910al-24G-PoE+",24,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× Dual-Personality (RJ45 PoE+ oder SFP 1G)","2 Modulschächte (optional bis 4× 10-GbE über CX4-/SFP+-Module, separat)",True,SPD_G_SFP,poe_at_psu,"128 Gbit/s","95 Mpps",RACK,PSU_2910,KL,760,"5,60"),
 "J9147A":P("2910al","ProCurve 2910al-48G",48,"44× 10/100/1000 (RJ45) + 4× Dual-Personality (RJ45 oder SFP 1G)","2 Modulschächte (optional bis 4× 10-GbE über CX4-/SFP+-Module, separat)",True,SPD_G_SFP,"Nein","176 Gbit/s","131 Mpps",RACK,PSU_2910,KL,760,"5,08"),
 "J9148A":P("2910al","ProCurve 2910al-48G-PoE+",48,"44× 10/100/1000 (RJ45, Class 4 PoE+) + 4× Dual-Personality (RJ45 PoE+ oder SFP 1G)","2 Modulschächte (optional bis 4× 10-GbE über CX4-/SFP+-Module, separat)",True,SPD_G_SFP,poe_at_psu,"176 Gbit/s","131 Mpps",RACK,PSU_2910,KL,980,"5,88"),
 # ===== 3500 (8) — L3, FE-base + yl Gigabit; yl have module slot =====
 "J9470A":P("3500","ProCurve 3500-24",24,"20× 10/100 (RJ45)",U_DUAL4,False,SPD_FE,"Nein","12 Gbit/s","8,9 Mpps",RACK,PSU_3500,KL,420,"5,40"),
 "J9471A":P("3500","ProCurve 3500-24-PoE",24,"20× 10/100 (RJ45, Class 3 PoE)",U_DUAL4,False,SPD_FE,poe_af(398),"12 Gbit/s","8,9 Mpps",RACK,PSU_3500,KL,560,"6,00"),
 "J9472A":P("3500","ProCurve 3500-48",48,"44× 10/100 (RJ45)",U_DUAL4,False,SPD_FE,"Nein","16,8 Gbit/s","12,5 Mpps",RACK,PSU_3500,KL,560,"6,10"),
 "J9473A":P("3500","ProCurve 3500-48-PoE",48,"44× 10/100 (RJ45, Class 3 PoE)",U_DUAL4,False,SPD_FE,poe_af(398),"16,8 Gbit/s","12,5 Mpps",RACK,PSU_3500,KL,720,"6,80"),
 "J8692A":P("3500","ProCurve 3500-24G-PoE yl",24,"20× 10/100/1000 (RJ45, Class 3 PoE) + 4× Dual-Personality (RJ45 PoE oder SFP 1G)","1 Modulschacht (optional bis 4× 10-GbE, separat)",True,SPD_G_SFP,poe_af(398),"101,8 Gbit/s","75,7 Mpps",RACK,PSU_3500,KL,900,"6,40"),
 "J8693A":P("3500","ProCurve 3500-48G-PoE yl",48,"44× 10/100/1000 (RJ45, Class 3 PoE) + 4× Dual-Personality (RJ45 PoE oder SFP 1G)","1 Modulschacht (optional bis 4× 10-GbE, separat)",True,SPD_G_SFP,poe_af(398),"149,8 Gbit/s","111,5 Mpps",RACK,PSU_3500,KL,1200,"7,30"),
 "J9310A":P("3500","ProCurve 3500-24G-PoE+ yl",24,"20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× Dual-Personality (RJ45 PoE+ oder SFP 1G)","1 Modulschacht (optional bis 4× 10-GbE, separat)",True,SPD_G_SFP,poe_at(398),"101,8 Gbit/s","75,7 Mpps",RACK,PSU_3500,KL,1050,"6,29"),
 "J9311A":P("3500","ProCurve 3500-48G-PoE+ yl",48,"44× 10/100/1000 (RJ45, Class 4 PoE+) + 4× Dual-Personality (RJ45 PoE+ oder SFP 1G)","1 Modulschacht (optional bis 4× 10-GbE, separat)",True,SPD_G_SFP,poe_at(398),"149,8 Gbit/s","111,5 Mpps",RACK,PSU_3500,KL,1350,"7,05"),
 # ===== 3800 (9) — L3 full, meshed-stacking, dual PSU, front-to-back =====
 "J9573A":P("3800","3800-24G-PoE+-2SFP+",26,"24× 10/100/1000 (RJ45, Class 4 PoE+)","2× SFP+ (1/10G)",False,SPD_G_SFPP,poe_at_x312,"88 Gbit/s","65,4 Mpps",RACK,PSU_3800,KFB,900,"7,20"),
 "J9574A":P("3800","3800-48G-PoE+-4SFP+",52,"48× 10/100/1000 (RJ45, Class 4 PoE+)","4× SFP+ (1/10G)",False,SPD_G_SFPP,poe_at_x312,"176 Gbit/s","130,9 Mpps",RACK,PSU_3800,KFB,1200,"7,64"),
 "J9575A":P("3800","3800-24G-2SFP+",26,"24× 10/100/1000 (RJ45)","2× SFP+ (1/10G)",False,SPD_G_SFPP,"Nein","88 Gbit/s","65,4 Mpps",RACK,PSU_3800,KFB,780,"7,21"),
 "J9576A":P("3800","3800-48G-4SFP+",52,"48× 10/100/1000 (RJ45)","4× SFP+ (1/10G)",False,SPD_G_SFPP,"Nein","176 Gbit/s","130,9 Mpps",RACK,PSU_3800,KFB,1050,"7,50"),
 "J9584A":P("3800","3800-24SFP-2SFP+",26,"24× SFP (1G Glasfaser)","2× SFP+ (1/10G)",False,SPD_SFP_SFPP,"Nein","88 Gbit/s","65,4 Mpps",RACK,PSU_3800,KFB,1100,"7,26"),
 "J9585A":P("3800","3800-24G-2XG",26,"24× 10/100/1000 (RJ45)","2× 10GBASE-T (RJ45, 10 GbE)",False,SPD_G_XG,"Nein","88 Gbit/s","65,4 Mpps",RACK,PSU_3800,KFB,900,"7,17"),
 "J9586A":P("3800","3800-48G-4XG",52,"48× 10/100/1000 (RJ45)","4× 10GBASE-T (RJ45, 10 GbE)",False,SPD_G_XG,"Nein","176 Gbit/s","130,9 Mpps",RACK,PSU_3800,KFB,1250,"7,70"),
 "J9587A":P("3800","3800-24G-PoE+-2XG",26,"24× 10/100/1000 (RJ45, Class 4 PoE+)","2× 10GBASE-T (RJ45, 10 GbE)",False,SPD_G_XG,poe_at_x312,"88 Gbit/s","65,4 Mpps",RACK,PSU_3800,KFB,1050,"7,40"),
 "J9588A":P("3800","3800-48G-PoE+-4XG",52,"48× 10/100/1000 (RJ45, Class 4 PoE+)","4× 10GBASE-T (RJ45, 10 GbE)",False,SPD_G_XG,poe_at_x312,"176 Gbit/s","130,9 Mpps",RACK,PSU_3800,KFB,1400,"7,80"),
 # ===== 6600 (5) — L3/4 DC server-edge, all non-PoE, dual hot-swap PSU, 5-40°C =====
 "J9263A":P("6600","ProCurve 6600-24G",24,"20× 10/100/1000 (RJ45)","4× Dual-Personality (RJ45 10/100/1000 oder SFP 1G)",False,SPD_G_SFP,"Nein","48 Gbit/s","35,7 Mpps",RACK,PSU_6600,K66,900,"7,58"),
 "J9264A":P("6600","ProCurve 6600-24G-4XG",28,"20× 10/100/1000 (RJ45) + 4× Dual-Personality (RJ45 10/100/1000 oder SFP 1G)","4× SFP+ (10 GbE)",False,SPD_G_SFPP,"Nein","101,8 Gbit/s","75,7 Mpps",RACK,PSU_6600,K66,1400,"7,80"),
 "J9265A":P("6600","ProCurve 6600-24XG",24,"24× SFP+ (10 GbE)","Alle 24 Ports als 10-GbE-SFP+-Uplinks nutzbar",True,SPD_10G,"Nein","322,8 Gbit/s","240,2 Mpps",RACK,PSU_6600,K66,2500,"8,94",btemp="0 bis 40 °C"),
 "J9451A":P("6600","ProCurve 6600-48G",48,"44× 10/100/1000 (RJ45)","4× Dual-Personality (RJ45 10/100/1000 oder SFP 1G)",False,SPD_G_SFP,"Nein","96 Gbit/s","71,4 Mpps",RACK,PSU_6600,K66,1300,"8,62"),
 "J9452A":P("6600","ProCurve 6600-48G-4XG",52,"44× 10/100/1000 (RJ45) + 4× Dual-Personality (RJ45 10/100/1000 oder SFP 1G)","4× SFP+ (10 GbE)",False,SPD_G_SFPP,"Nein","176 Gbit/s","130,9 Mpps",RACK,PSU_6600,K66,1900,"8,62"),
}

# ------------------------------------------------------------------ author one SKU
def clip(model,pid):
    for t in (f"HP {model} Switch | Hexwaren", f"HP {model} | Hexwaren", f"{model} ({pid}) | Hexwaren"):
        if len(t)<=60: return t
    return f"{pid} | Hexwaren"
def fitmeta(m):
    m=ws(m)
    while len(m)<140: m=m[:-1].rstrip()+" Neu und versiegelt."
    return m[:200].rstrip()
def author(pid):
    b=SPECS[pid]; fam=b['fam']; f=FAM[fam]; lyr=f['lyr']; lyr_de="Layer-3" if lyr=="L3" else "Layer-2"
    poe_yes=b['poe']!="Nein"; stack=f['stk']; btemp=b.get('btemp') or f['btemp']; feat=FEAT[f['feat']]
    model=b['model']; up=b['up']
    portkonfig = b['acc'] if b['up_modular'] else f"{b['acc']} + {up} (Uplink)"
    artikel=ws(f"HP {model} {pid} Managed Switch ({lyr}) – {b['acc']}{('' if b['up_modular'] else ' + '+up)}, {b['bauform'].split('(')[0].strip()}")
    titel=clip(model,pid)
    poe_meta=(f"PoE {b['poe'].split('Budget ')[-1].rstrip(')') if 'Budget ' in b['poe'] else 'nach IEEE 802.3af/at'}" if poe_yes else "ohne PoE")
    meta=fitmeta(f"Original HP {model} ({pid}): gemanagter {lyr_de}-Switch mit {b['acc']}, Switching-Kapazität {b['swk']}, {poe_meta}, ProVision-Betriebssystem.")
    # kurz
    if poe_yes: pshort=f"{b['n']} Ports mit PoE"
    else: pshort=f"{b['n']} Ports"
    pos=POS[fam].format(pid=pid)
    kp1=(f"<p>Der HP {model} ({pid}) ist ein gemanagter {lyr_de}-Switch mit {pshort}, betrieben unter dem HP-ProVision-Betriebssystem. "
         f"{pos}</p>")
    poe_k=(f" Über Power over Ethernet versorgt der {pid} angeschlossene Endgeräte direkt per Netzwerkkabel." if poe_yes else "")
    kp2=(f"<p>Der {pid} liefert eine Switching-Kapazität von {b['swk']} und bindet per {up} an das Netz an.{poe_k} "
         f"Er wird als versiegelte Original-Neuware geliefert.</p>")
    kurz=kp1+kp2
    # intro
    poe_i=(f" Der {pid} versorgt IP-Telefone, WLAN-Access-Points und Kameras per Power over Ethernet direkt über das Netzwerkkabel." if poe_yes
           else f" Der {pid} ist ein Modell ohne PoE und konzentriert sich auf reine Datenanbindung.")
    role={"2510":"den Fast-Ethernet-Edge-Access","2610":"den Edge-Access mit statischem Routing","2615":"den kompakten PoE-Edge-Access",
          "2620":"den Access mit statischem und RIP-Routing","2810":"den Gigabit-Access","2910al":"den Gigabit-Access und die Aggregation",
          "2915":"den kompakten Gigabit-PoE-Access","3500":"den Layer-3-Access und die Aggregation","3800":"die Layer-3-Aggregation",
          "6600":"den Layer-3/4-Server-Edge im Rechenzentrum"}[fam]
    i1=(f"Der HP {model} ({pid}) ist ein gemanagter {lyr_de}-Switch der HP-{fam}-Serie mit {b['acc']}, "
        f"ausgelegt für {role} und betrieben unter dem HP-ProVision-Betriebssystem.")
    stk_de={"2510":f"Der {pid} arbeitet eigenständig; über Single-IP-Virtual-Stacking lassen sich bis zu 16 Einheiten zentral verwalten.",
            "2610":f"Der {pid} arbeitet eigenständig; per Single-IP-Virtual-Stacking lassen sich bis zu 16 Einheiten zentral verwalten.",
            "2615":f"Der {pid} wird als eigenständiger Edge-Switch betrieben.",
            "2620":f"Der {pid} wird als eigenständiger Access-Switch betrieben.",
            "2810":f"Der {pid} arbeitet eigenständig; per Single-IP-Virtual-Stacking lassen sich bis zu 16 Einheiten zentral verwalten.",
            "2910al":f"Der {pid} wird eigenständig verwaltet; über Single-IP-Virtual-Stacking lassen sich bis zu 16 Einheiten zusammenfassen, optionale Module ergänzen bis zu vier 10-GbE-Uplinks.",
            "2915":f"Der {pid} wird als eigenständiger Edge-Switch betrieben.",
            "3500":f"Der {pid} wird eigenständig verwaltet; Ausfallsicherheit entsteht über HP-Switch-Meshing und Distributed Trunking, ein optionales Modul ergänzt bis zu vier 10-GbE-Ports.",
            "3800":f"Über das dedizierte Stacking-Modul J9577A lassen sich bis zu zehn {pid} per Meshed-Stacking (bis 336 Gbit/s) zu einem logischen Switch zusammenfassen.",
            "6600":f"Der {pid} wird eigenständig verwaltet; Ausfallsicherheit entsteht über redundante Hot-Swap-Netzteile, ein Hot-Swap-Lüftertray sowie HP-Switch-Meshing und Distributed Trunking."}[fam]
    i2=(f"Mit {b['n']} Ports erreicht der {pid} eine Switching-Kapazität von {b['swk']} bei einer Weiterleitungsrate von {b['mpps']}.{poe_i} {stk_de}")
    i3=(f"Im Formfaktor {b['bauform']} arbeitet der {pid} im Temperaturbereich {btemp}; Kühlung und Stromversorgung des {pid} "
        f"übernehmen {b['kueh']} sowie {b['strom']}. Unter ProVision bietet der {pid} {feat}. "
        f"Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch.")
    intro=[ws(i1),ws(i2),ws(i3)]
    faq=[["Ist dies ein originales HP-Produkt?", f"Ja. Der {pid} ist HP-Original-Neuware ({model}) – versiegelt geliefert und für den Betrieb unter dem HP-ProVision-Betriebssystem vorgesehen."],
         [f"Wie viele Ports hat der {pid}?", f"Der {pid} bietet insgesamt {b['n']} Ports: {portkonfig}."]]
    if poe_yes: faq.append([f"Unterstützt der {pid} PoE?", f"Ja. Der {pid} stellt {b['poe']} bereit und versorgt angeschlossene Geräte direkt über das Netzwerkkabel."])
    else: faq.append([f"Unterstützt der {pid} PoE?", f"Nein. Der {pid} ist ein Modell ohne Power over Ethernet und für reine Datenanbindung ausgelegt."])
    faq.append([f"Lässt sich der {pid} stapeln (Stacking)?",
                (f"Der {pid} unterstützt {stack}." if fam=="3800" else f"Der {pid} nutzt kein dediziertes Stacking; er wird eigenständig verwaltet ({stack}).")])
    attrs=[["Switch-Typ","Managed"],["Layer",lyr],["Portanzahl",str(b['n'])],["Port-Konfiguration",portkonfig],
           ["Port-Geschwindigkeit",b['spd']],["Uplink-Ports",up],["PoE",b['poe']],["Switching-Kapazität",b['swk']],
           ["Durchsatz",b['mpps']],["Bauform",b['bauform']],["Stromversorgung",b['strom']],["Kühlung",b['kueh']],
           ["Stacking",stack],["Betriebstemperatur",btemp],["Anwendung",f['anw']],["Zustand","Neu, versiegelt"]]
    doc=f['doc']; prov={a[0]:[doc,"datasheet"] for a in attrs if a[0]!="Zustand"}
    versand=f"{float(b['gw'].replace(',','.'))+2.0:.2f}".replace('.',',')
    return {"_facts":{"unterkategorie":"Managed Switch ("+lyr+")","quell_url":doc,"verifiziert_am":VERIF},
            "artikelname":artikel,"titel_tag":titel,"meta_description":meta,"artikelgewicht":b['gw'],"versandgewicht":versand,
            "kurzbeschreibung":ws(kurz),"intro":intro,"kompatibilitaet":["HP ProVision-Firmware","HP PCM+ (ProCurve Manager Plus)","HP IMC (Intelligent Management Center)"],
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{b['price']}.00"}

# ------------------------------------------------------------------ build a bundle
def build(cat, pids):
    from hexcat.validate import validate_dir
    doc={pid:author(pid) for pid in pids}
    cpath=ROOT/"stage3_content"/f"{cat}_content.json"; cpath.write_text(json.dumps(doc,ensure_ascii=False,indent=1),encoding="utf-8")
    recs=reconcile_content(cpath,brand=BRAND,rules=rules,weights=weights)
    out=ROOT/"output"/"switches"/cat
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    assemble_bundle(recs,rules,batch=cat,category=cat,out_dir=out)
    S.process_main(out/f"Hexwaren_{cat}_Main.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    S.process_faq(out/f"Hexwaren_FAQ_{cat}.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    e3=FAM[SPECS[pids[0]]['fam']]['e3']; mp=out/f"Hexwaren_{cat}_Main.csv"
    rows=list(csv.reader(mp.read_bytes().decode("utf-8-sig").splitlines(),delimiter=";")); H=rows[0]
    i1,i2,i3=H.index("Kategorie Ebene 1"),H.index("Kategorie Ebene 2"),H.index("Kategorie Ebene 3"); data=[]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        r[i1],r[i2],r[i3]=E1,E2,e3; data.append(r)
    write_csv(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{cat}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in pids:
        vrows.append([pid,f"{SPECS[pid]['price']},00","PHASE-1-SCHÄTZUNG — NICHT marktgegroundet (EOL-Modell). Tarif nach Konfigurations-Tier. Echte HPE-Marktpreis-Recherche folgt.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/cat; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {cat} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:8]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:110])
    return out

if __name__=="__main__":
    fams={"2510":"HP_ProCurve_2510_Switches","2610":"HP_ProCurve_2610_Switches","2615":"HP_ProCurve_2615_Switches",
          "2620":"HP_ProCurve_2620_Switches","2810":"HP_ProCurve_2810_Switches","2910al":"HP_ProCurve_2910al_Switches",
          "2915":"HP_ProCurve_2915_Switches","3500":"HP_ProCurve_3500_Switches","3800":"HP_3800_Switches","6600":"HP_ProCurve_6600_Switches"}
    only=sys.argv[1] if len(sys.argv)>1 else None
    for fam,cat in fams.items():
        if only and fam!=only: continue
        build(cat,[p for p,s in SPECS.items() if s['fam']==fam])
