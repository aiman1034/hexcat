# -*- coding: utf-8 -*-
"""STEP-2 ArubaOS-Switch PHASE 2a: current Aruba FIXED families 2530/2540/2920/2930F/2930M/3810M (59 SKUs).
15 fixed-switch Merkmale (validated schema); 0 new Merkmal NAMES — ArubaOS specifics (Backplane/VSF stacking,
PoE Class 6/740W, ProVision OS) are new VALUES or prose. Grounded verbatim from the cached QuickSpecs Models
tables (per-model SwK/Durchsatz/PoE-budget read cell-by-cell, never port-math); stacking-Gbit/s + JL692A/693A
physicals flagged where un-groundable, rephrased customer-safe (never ship ZU_VERIFIZIEREN). Hersteller = HP.
Prices PHASE-1 ESTIMATE (flagged). $0 prose. Reuses the locked pipeline (reconcile->assemble->scrub->remap->gate)."""
import json, re, shutil, tempfile, csv, sys
from pathlib import Path
sys.path.insert(0, "_scratch")
from hexcat.config import load_rules, load_weights
from hexcat.stage3 import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat.validate import validate_dir
from hexcat.writers import write_csv
from hexcat import constants as C
import scrub_uwg as S

ROOT = Path("."); rules, weights = load_rules(), load_weights()
BRAND = "Aruba"; E1, E2 = "Netzwerk & Infrastruktur", "Switches"; VERIF = "2026-06-30"
def ws(s): return re.sub(r"\s+", " ", s).strip()
DOC = {"2530":"https://www.hpe.com/psnow/doc/4aa5-9518enw","2540":"https://www.hpe.com/psnow/doc/4aa6-7884enw",
       "2920":"https://www.hpe.com/psnow/doc/c04111401","2930F":"https://www.hpe.com/psnow/doc/c05052929",
       "2930M":"https://www.hpe.com/psnow/doc/a00004551enw","3810M":"https://www.hpe.com/psnow/doc/c04843019"}

# --- per-family defaults: Layer, Stacking value, Betriebstemperatur, Anwendung, feature-prose ---
STK={"2530":"Kein (Standalone; Single-IP-Virtual-Stacking bis 16 Einheiten für zentrales Management)",
     "2540":"Kein (eigenständiger Access-Switch)",
     "2920":"Backplane-Stacking (bis 4 Einheiten, 40 Gbit/s je Stacking-Port; optionales Stacking-Modul)",
     "2930F":"VSF (Virtual Switching Framework, bis 8 Einheiten)",
     "2930M":"Backplane-Stacking (VSF, Ring bis 10 Einheiten, 100 Gbit/s je Switch; optionales Stacking-Modul)",
     "3810M":"Backplane-Stacking (dediziertes Stacking-Modul, bis 336 Gbit/s)"}
ANW={"2530":"Fully-managed Layer-2-Campus-Access (ArubaOS-Switch) für Edge, Filialen und kleine Standorte",
     "2540":"Layer-2-/Basis-Layer-3-Campus-Access (ArubaOS-Switch) mit festen 10G-SFP+-Uplinks",
     "2920":"Layer-3-Campus-Access und -Aggregation (ArubaOS-Switch) mit Backplane-Stacking",
     "2930F":"Layer-3-Campus-Access (ArubaOS-Switch) mit VSF-Stacking",
     "2930M":"Layer-3-Campus-Access und -Aggregation (ArubaOS-Switch) mit VSF-Backplane-Stacking",
     "3810M":"Layer-3-Campus-Aggregation (ArubaOS-Switch) mit Backplane-Stacking und durchgängigem MACsec"}
FEAT={"L2":"Layer-2-Funktionen unter ArubaOS-Switch (ProVision-ASIC): VLANs, ACLs, QoS, LACP, Spanning Tree, IGMP-Snooping und statisches IPv4-Routing",
      "L3":"Layer-3-Routing (statisch, RIP, OSPF) unter ArubaOS-Switch, dazu VLANs, ACLs, QoS, LACP, Spanning Tree und Tunneled-Node",
      "L3ADV":"Layer-3-Routing (OSPF, BGP, IPv6, VRRP, PIM) unter ArubaOS-Switch mit durchgängigem MACsec, VLANs, ACLs, QoS und Robust-Stacking"}
LYR={"2530":"L2","2540":"L2","2920":"L3","2930F":"L3","2930M":"L3","3810M":"L3"}
BTEMP_DEF={"2530":"0 bis 45 °C","2540":"0 bis 45 °C","2920":"0 bis 55 °C","2930F":"0 bis 45 °C","2930M":"0 bis 55 °C","3810M":"0 bis 45 °C"}
RACK="19-Zoll-Rackmontage (1 HE)"; COMPACT="Kompakt (1 HE, halbe Breite, lüfterlos)"
PSU_INT="Internes Festnetzteil (nicht hot-swap)"; PSU_EXT="Externes Netzteil (Steckernetzteil / EPS-Shelf, separat)"
PSU_DUAL="2 Hot-Swap-Netzteilschächte (mindestens 1 erforderlich, redundant, separat bestellt)"
KUEHL_FANLESS="Lüfterlos (passiv gekühlt)"; KUEHL_FAN="Lüftergekühlt"; KUEHL_F2B="Lüftergekühlt (Airflow front-to-back)"
SPD_G="10/100/1000 Mbit/s (RJ45)"; SPD_G_SFPP="10/100/1000 Mbit/s (RJ45), 1/10 GbE (SFP+)"
SPD_FE="10/100 Mbit/s (RJ45, Access), 10/100/1000 Mbit/s (Uplink)"; SPD_SR="100M/1/2.5/5/10 GbE (HPE Smart Rate)"

# uplink strings
U_4SFPP="4× SFP+ (1/10G)"; U_2SFPP="2× SFP+ (1/10G)"; U_4SFP="4× SFP (1G)"
U_DUAL="2× Dual-Personality-Ports (RJ45 10/100/1000 oder SFP 1G)"
U_FE="2× 10/100/1000BASE-T (RJ45) + 2× SFP (1G)"
U_693="2× 10/100/1000BASE-T (RJ45) + 2× SFP+ (1/10G)"
U_MOD_2920="bis 4× 10 GbE über 2 Modulschächte (optionale SFP+- oder 10GBASE-T-Module, separat)"
U_MOD_2930M="1 Uplink-Modulschacht (optional 4× SFP+ 10G, 40G-QSFP+ oder 4× HPE Smart Rate, separat)"
U_MOD_3810="1 Modulschacht (optional 4× SFP+ 10G, 40G-QSFP+ oder 4× HPE Smart Rate, separat)"
U_MOD_3810_2="2 Modulschächte (optional bis 8× SFP+ 10G oder 2× 40G-QSFP+, separat)"

# ------------------------------------------------------------------ per-PID specs
# fields: fam, n, acc, up, up_modular, spd, poe, swk, mpps, bauform, strom, kueh, taa, price [, btemp]
def P(fam,n,acc,up,up_modular,spd,poe,swk,mpps,bauform,strom,kueh,taa,price,**kw):
    d=dict(fam=fam,n=n,acc=acc,up=up,up_modular=up_modular,spd=spd,poe=poe,swk=swk,mpps=mpps,
           bauform=bauform,strom=strom,kueh=kueh,taa=taa,price=price); d.update(kw); return d
PoE4=lambda w:f"Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port, Budget {w} W)"
PoE6=lambda w:f"Ja (IEEE 802.3bt Class 6, 60 W/Port, Budget {w} W)"

SPECS={
 # ===== 2530 (17) — L2 =====
 "J9772A":P("2530",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFP,False,SPD_G,PoE4(382),"104 Gbit/s","77,3 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1150,gw="4,72"),
 "J9773A":P("2530",28,"24× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFP,False,SPD_G,PoE4(195),"56 Gbit/s","41,6 Mpps",RACK,PSU_INT,KUEHL_FAN,False,850,gw="3,95"),
 "J9774A":P("2530",10,"8× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_DUAL,False,SPD_G,PoE4(67),"20 Gbit/s","14,8 Mpps",COMPACT,PSU_EXT,KUEHL_FANLESS,False,480,gw="1,00"),
 "J9775A":P("2530",52,"48× 10/100/1000BASE-T (ohne PoE)",U_4SFP,False,SPD_G,"Nein","104 Gbit/s","77,3 Mpps",RACK,PSU_INT,KUEHL_FAN,False,800,gw="3,08"),
 "J9776A":P("2530",28,"24× 10/100/1000BASE-T (ohne PoE)",U_4SFP,False,SPD_G,"Nein","56 Gbit/s","41,6 Mpps",RACK,PSU_INT,KUEHL_FANLESS,False,560,gw="2,77"),
 "J9777A":P("2530",10,"8× 10/100/1000BASE-T (ohne PoE)",U_DUAL,False,SPD_G,"Nein","20 Gbit/s","14,8 Mpps",COMPACT,PSU_EXT,KUEHL_FANLESS,False,360,gw="0,91"),
 "J9778A":P("2530",52,"48× 10/100BASE-T (Class 4 PoE+, 30 W)",U_FE,False,SPD_FE,PoE4(382),"17,6 Gbit/s","13 Mpps",RACK,PSU_INT,KUEHL_FANLESS,False,900,gw="4,58"),
 "J9779A":P("2530",28,"24× 10/100BASE-T (Class 4 PoE+, 30 W)",U_FE,False,SPD_FE,PoE4(195),"12,8 Gbit/s","9,5 Mpps",RACK,PSU_INT,KUEHL_FANLESS,False,680,gw="3,81"),
 "J9780A":P("2530",10,"8× 10/100BASE-T (Class 4 PoE+, 30 W)",U_DUAL,False,SPD_FE,PoE4(67),"5,6 Gbit/s","4,1 Mpps",COMPACT,PSU_EXT,KUEHL_FANLESS,False,420,gw="0,91"),
 "J9781A":P("2530",52,"48× 10/100BASE-T (ohne PoE)",U_FE,False,SPD_FE,"Nein","17,6 Gbit/s","13 Mpps",RACK,PSU_INT,KUEHL_FANLESS,False,620,gw="2,86"),
 "J9782A":P("2530",28,"24× 10/100BASE-T (ohne PoE)",U_FE,False,SPD_FE,"Nein","12,8 Gbit/s","9,5 Mpps",RACK,PSU_INT,KUEHL_FANLESS,False,480,gw="2,59"),
 "J9783A":P("2530",10,"8× 10/100BASE-T (ohne PoE)",U_DUAL,False,SPD_FE,"Nein","5,6 Gbit/s","4,1 Mpps",COMPACT,PSU_EXT,KUEHL_FANLESS,False,320,gw="0,82"),
 "JL070A":P("2530",10,"8× 10/100BASE-T (Class 4 PoE+, 30 W)",U_DUAL,False,SPD_FE,PoE4(67),"5,6 Gbit/s","4,1 Mpps","Kompakt (1 HE, halbe Breite, lüfterlos, internes Netzteil)",PSU_INT,KUEHL_FANLESS,False,520,gw="2,11"),
 "J9853A":P("2530",50,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_2SFPP,False,SPD_G_SFPP,PoE4(382),"136 Gbit/s","101 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1350,gw="4,72"),
 "J9854A":P("2530",26,"24× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_2SFPP,False,SPD_G_SFPP,PoE4(195),"88 Gbit/s","65,4 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1050,gw="3,90"),
 "J9855A":P("2530",50,"48× 10/100/1000BASE-T (ohne PoE)",U_2SFPP,False,SPD_G_SFPP,"Nein","136 Gbit/s","101 Mpps",RACK,PSU_INT,KUEHL_FANLESS,False,1000,gw="3,08"),
 "J9856A":P("2530",26,"24× 10/100/1000BASE-T (ohne PoE)",U_2SFPP,False,SPD_G_SFPP,"Nein","88 Gbit/s","65,4 Mpps",RACK,PSU_INT,KUEHL_FANLESS,False,760,gw="2,81"),
 # ===== 2540 (4) — L2/L3-lite, 4× SFP+ built-in =====
 "JL354A":P("2540",28,"24× 10/100/1000BASE-T (ohne PoE)",U_4SFPP,False,SPD_G_SFPP,"Nein","128 Gbit/s","95,2 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1100,gw="2,41"),
 "JL355A":P("2540",52,"48× 10/100/1000BASE-T (ohne PoE)",U_4SFPP,False,SPD_G_SFPP,"Nein","176 Gbit/s","112 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1500,gw="3,10"),
 "JL356A":P("2540",28,"24× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(370),"128 Gbit/s","95,2 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1450,gw="3,90"),
 "JL357A":P("2540",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(370),"176 Gbit/s","112 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1850,gw="4,46"),
 # ===== 2920 (5) — L3-basic, modular uplinks =====
 "J9726A":P("2920",24,"20× 10/100/1000BASE-T + 4× Dual-Personality (RJ45 oder SFP, 1G)",U_MOD_2920,True,SPD_G,"Nein","128 Gbit/s","95,2 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1400,gw="5,25"),
 "J9727A":P("2920",24,"20× 10/100/1000BASE-T (Class 4 PoE+, 30 W) + 4× Dual-Personality (RJ45 oder SFP, 1G, PoE+)",U_MOD_2920,True,SPD_G,PoE4(370),"128 Gbit/s","95,2 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1750,gw="5,46"),
 "J9728A":P("2920",48,"44× 10/100/1000BASE-T + 4× Dual-Personality (RJ45 oder SFP, 1G)",U_MOD_2920,True,SPD_G,"Nein","176 Gbit/s","130,9 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1900,gw="5,42"),
 "J9729A":P("2920",48,"44× 10/100/1000BASE-T (Class 4 PoE+, 30 W) + 4× Dual-Personality (RJ45 oder SFP, 1G, PoE+)",U_MOD_2920,True,SPD_G,PoE4(370),"176 Gbit/s","130,9 Mpps",RACK,PSU_INT,KUEHL_FAN,False,2300,gw="5,70"),
 "J9836A":P("2920",48,"44× 10/100/1000BASE-T (Class 4 PoE+, 30 W) + 4× Dual-Personality (RJ45 oder SFP, 1G, PoE+)",U_MOD_2920,True,SPD_G,PoE4(740),"176 Gbit/s","130,9 Mpps",RACK,PSU_INT,KUEHL_FAN,False,2600,gw="5,83"),
 # ===== 2930M (8) — L3, modular uplinks, dual hot-swap PSU =====
 "JL319A":P("2930M",24,"20× 10/100/1000BASE-T + 4× Combo (10/100/1000BASE-T oder SFP)",U_MOD_2930M,True,SPD_G,"Nein","128 Gbit/s","95,2 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,2100,gw="4,45"),
 "JL320A":P("2930M",24,"20× 10/100/1000BASE-T (Class 4 PoE+, 30 W) + 4× Combo (10/100/1000BASE-T PoE+ oder SFP)",U_MOD_2930M,True,SPD_G,PoE4(840),"128 Gbit/s","95,2 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,2600,gw="4,50"),
 "JL321A":P("2930M",48,"44× 10/100/1000BASE-T + 4× Combo (10/100/1000BASE-T oder SFP)",U_MOD_2930M,True,SPD_G,"Nein","176 Gbit/s","112 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,2600,gw="4,60"),
 "JL322A":P("2930M",48,"44× 10/100/1000BASE-T (Class 4 PoE+, 30 W) + 4× Combo (10/100/1000BASE-T PoE+ oder SFP)",U_MOD_2930M,True,SPD_G,PoE4(1440),"176 Gbit/s","112 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,3200,gw="4,65"),
 "JL323A":P("2930M",48,"36× 10/100/1000BASE-T (Class 4 PoE+, 30 W) + 4× Combo (10/100/1000BASE-T PoE+ oder SFP) + 8× HPE Smart Rate (100M/1/2.5/5/10G, Class 4 PoE+, 30 W)",U_MOD_2930M,True,SPD_SR,PoE4(1440),"320 Gbit/s","112 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,3800,gw="4,45"),
 "JL324A":P("2930M",24,"24× HPE Smart Rate 100M/1/2.5/5G-BASE-T (Class 4 PoE+, 30 W)",U_MOD_2930M,True,"100M/1/2.5/5 GbE (HPE Smart Rate)",PoE4(840),"320 Gbit/s","112 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,3400,gw="4,50",btemp="0 bis 45 °C"),
 "R0M67A":P("2930M",48,"36× 10/100/1000BASE-T (Class 6 PoE, 60 W) + 4× Combo (10/100/1000BASE-T Class 6 oder SFP) + 8× HPE Smart Rate (100M/1/2.5/5/10G, Class 6 PoE, 60 W)",U_MOD_2930M,True,SPD_SR,PoE6(1440),"320 Gbit/s","112 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,4200,gw="4,49"),
 "R0M68A":P("2930M",24,"24× HPE Smart Rate 100M/1/2.5/5G-BASE-T (Class 6 PoE, 60 W)",U_MOD_2930M,True,"100M/1/2.5/5 GbE (HPE Smart Rate)",PoE6(1440),"320 Gbit/s","112 Mpps",RACK,PSU_DUAL,KUEHL_F2B,False,3800,gw="4,52",btemp="0 bis 45 °C"),
 # ===== 2930F (16, corrected) — L3, VSF; fixed uplinks =====
 "JL253A":P("2930F",28,"24× 10/100/1000BASE-T (ohne PoE)",U_4SFPP,False,SPD_G_SFPP,"Nein","128 Gbit/s","95,2 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1500,gw="2,41"),
 "JL254A":P("2930F",52,"48× 10/100/1000BASE-T (ohne PoE)",U_4SFPP,False,SPD_G_SFPP,"Nein","176 Gbit/s","112 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1900,gw="3,10"),
 "JL255A":P("2930F",28,"24× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(370),"128 Gbit/s","95,2 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1950,gw="3,90"),
 "JL256A":P("2930F",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(370),"176 Gbit/s","112 Mpps",RACK,PSU_INT,KUEHL_FAN,False,2400,gw="4,46"),
 "JL258A":P("2930F",10,"8× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_2SFPP,False,SPD_G_SFPP,PoE4(125),"56 Gbit/s","41,7 Mpps",COMPACT,PSU_INT,KUEHL_FANLESS,False,1100,gw="2,00"),
 "JL259A":P("2930F",28,"24× 10/100/1000BASE-T (ohne PoE)",U_4SFP,False,SPD_G,"Nein","56 Gbit/s","41,7 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1350,gw="2,41"),
 "JL260A":P("2930F",52,"48× 10/100/1000BASE-T (ohne PoE)",U_4SFP,False,SPD_G,"Nein","104 Gbit/s","77,4 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1700,gw="3,10"),
 "JL261A":P("2930F",28,"24× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFP,False,SPD_G,PoE4(370),"56 Gbit/s","41,7 Mpps",RACK,PSU_INT,KUEHL_FAN,False,1800,gw="3,90"),
 "JL262A":P("2930F",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFP,False,SPD_G,PoE4(370),"104 Gbit/s","77,4 Mpps",RACK,PSU_INT,KUEHL_FAN,False,2200,gw="4,46"),
 "JL263A":P("2930F",28,"24× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(370),"128 Gbit/s","95,2 Mpps",RACK,PSU_INT,KUEHL_FAN,False,2050,gw="3,90"),
 "JL264A":P("2930F",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(370),"176 Gbit/s","112 Mpps",RACK,PSU_INT,KUEHL_FAN,False,2500,gw="4,46"),
 "JL557A":P("2930F",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFP,False,SPD_G,PoE4(740),"104 Gbit/s","77,4 Mpps",RACK,"Internes Festnetzteil 980 W (80 PLUS Gold, nicht hot-swap)",KUEHL_FAN,False,2700,gw="4,79"),
 "JL558A":P("2930F",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(740),"176 Gbit/s","112 Mpps",RACK,"Internes Festnetzteil 980 W (80 PLUS Gold, nicht hot-swap)",KUEHL_FAN,False,2900,gw="4,79"),
 "JL559A":P("2930F",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_4SFPP,False,SPD_G_SFPP,PoE4(740),"176 Gbit/s","112 Mpps",RACK,"Internes Festnetzteil 980 W (80 PLUS Gold, nicht hot-swap)",KUEHL_FAN,True,3050,gw="4,79"),
 "JL692A":P("2930F",10,"8× 10/100/1000BASE-T (Class 4 PoE+, 30 W)",U_2SFPP,False,SPD_G_SFPP,PoE4(125),"56 Gbit/s","41,7 Mpps",COMPACT,PSU_INT,KUEHL_FANLESS,True,1250,gw="2,00"),
 "JL693A":P("2930F",16,"12× 10/100/1000BASE-T (Class 4 PoE+, 30 W) + 2× 10/100/1000BASE-T (ohne PoE)",U_2SFPP,False,SPD_G_SFPP,PoE4(139),"68 Gbit/s","41,7 Mpps","Kompakt (1 HE, halbe Breite)",PSU_INT,KUEHL_FAN,False,1400,gw="2,20"),
 # ===== 3810M (9 = 6 base + 3 CTO) — L3-advanced, modular uplinks, dual hot-swap PSU, MACsec =====
 "JL071A":P("3810M",24,"24× 10/100/1000BASE-T (MACsec)",U_MOD_3810,True,SPD_G,"Nein","160 Gbit/s","95,2 Mpps",RACK,PSU_DUAL,"Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,3200,gw="5,79",feat="L3ADV"),
 "JL072A":P("3810M",48,"48× 10/100/1000BASE-T (MACsec)",U_MOD_3810,True,SPD_G,"Nein","320 Gbit/s","190,5 Mpps",RACK,PSU_DUAL,"Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,3900,gw="5,99",feat="L3ADV"),
 "JL073A":P("3810M",24,"24× 10/100/1000BASE-T (Class 4 PoE+, 30 W, MACsec)",U_MOD_3810,True,SPD_G,PoE4(840),"160 Gbit/s","95,2 Mpps",RACK,PSU_DUAL,"Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,3900,gw="5,91",feat="L3ADV"),
 "JL074A":P("3810M",48,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W, MACsec)",U_MOD_3810,True,SPD_G,PoE4(1440),"320 Gbit/s","190,5 Mpps",RACK,PSU_DUAL,"Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,4700,gw="6,18",feat="L3ADV"),
 "JL075A":P("3810M",16,"16× SFP+ (1/10G, MACsec)",U_MOD_3810_2,True,"1/10 GbE (SFP+)","Nein","480 Gbit/s","285,7 Mpps",RACK,PSU_DUAL,"Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,5200,gw="6,02",feat="L3ADV"),
 "JL076A":P("3810M",48,"40× 10/100/1000BASE-T (Class 4 PoE+, 30 W, MACsec) + 8× HPE Smart Rate (100M/1/2.5/5/10G, Class 4 PoE+, 30 W, MACsec)",U_MOD_3810,True,SPD_SR,PoE4(1440),"480 Gbit/s","273,8 Mpps",RACK,PSU_DUAL,"Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,5500,gw="6,17",feat="L3ADV"),
 "JL428A":P("3810M",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W, MACsec)","4× SFP+ (1/10G, über enthaltenes JL083A-Modul)",False,SPD_G,PoE4(680),"320 Gbit/s","190,5 Mpps",RACK,"2 Hot-Swap-Netzteilschächte (1× X372 680 W AC enthalten, redundant erweiterbar)","Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,5000,gw="6,18",feat="L3ADV"),
 "JL429A":P("3810M",52,"48× 10/100/1000BASE-T (Class 4 PoE+, 30 W, MACsec)","4× SFP+ (1/10G, über enthaltenes JL083A-Modul)",False,SPD_G,PoE4(1050),"320 Gbit/s","190,5 Mpps",RACK,"2 Hot-Swap-Netzteilschächte (1× X372 1.050 W AC enthalten, redundant erweiterbar)","Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,5400,gw="6,18",feat="L3ADV"),
 "JL430A":P("3810M",24,"16× SFP+ (1/10G, fest, MACsec)","8× SFP+ (1/10G, über zwei enthaltene JL083A-Module)",False,"1/10 GbE (SFP+)","Nein","480 Gbit/s","285,7 Mpps",RACK,"2 Hot-Swap-Netzteilschächte (1× X371 250 W AC enthalten, redundant erweiterbar)","Lüftergekühlt (austauschbarer Lüftereinschub JL088A, front-to-side/rear)",False,5600,gw="6,02",feat="L3ADV"),
}

# ------------------------------------------------------------------ author one SKU
def clip(series,pid):
    for t in (f"HPE Aruba {series} {pid} Switch | Hexwaren", f"Aruba {series} {pid} Switch | Hexwaren", f"Aruba {series} {pid} | Hexwaren"):
        if len(t)<=60: return t
    return f"{pid} | Hexwaren"
def fitmeta(m):
    m=ws(m)
    while len(m)<140: m=m[:-1].rstrip()+" Neu und versiegelt."
    return m[:200].rstrip()
def author(pid):
    b=SPECS[pid]; fam=b['fam']; lyr=LYR[fam]; lyr_de="Layer-3" if lyr=="L3" else "Layer-2"
    poe_yes=b['poe']!="Nein"; taa=b['taa']; stack=STK[fam]; btemp=b.get('btemp') or BTEMP_DEF[fam]
    feat=FEAT[b.get('feat') or lyr]; up=b['up']
    portkonfig = b['acc'] if b['up_modular'] else f"{b['acc']} + {up} (Uplink)"
    upattr = up
    taa_tag=" (TAA, Trade Agreements Act)" if taa else ""
    artikel=ws(f"HPE Aruba Networking {fam} {pid} Managed Switch ({lyr}) – {b['acc']}{('' if b['up_modular'] else ' + '+up)}, {b['bauform'].split(';')[0].split('(')[0].strip()}{taa_tag}")
    titel=clip(fam,pid)
    poe_meta=(f"PoE-Budget {b['poe'].split('Budget ')[-1].rstrip(')')}" if poe_yes else "ohne PoE")
    meta=fitmeta(f"Original HPE Aruba Networking {fam} {pid}: gemanagter {lyr_de}-Switch mit {b['acc']}, Switching-Kapazität {b['swk']}, {poe_meta}, ArubaOS-Switch.")
    # kurz
    poe_k=(f" Über Power over Ethernet versorgt der {pid} angeschlossene Endgeräte direkt per Netzwerkkabel." if poe_yes else "")
    pos={"2530":f"Der {pid} bedient als kompakter Layer-2-Edge-Switch Anschlussräume, Filialen und kleinere Standorte.",
         "2540":f"Der {pid} bindet den Etagen-Access über feste 10-Gigabit-SFP+-Uplinks an den Verteiler an.",
         "2920":f"Der {pid} fasst als stapelfähiger Aggregations-Switch mehrere Etagenverteiler zu einer Einheit zusammen.",
         "2930F":f"Der {pid} bündelt per Virtual Switching Framework mehrere Geräte zu einem gemeinsam verwalteten Verbund.",
         "2930M":f"Der {pid} skaliert mit modularen Uplinks und VSF-Stapelung vom Access bis in die Aggregation.",
         "3810M":f"Der {pid} liefert mit Backplane-Stapelung und durchgängigem MACsec chassisähnliche Ausfallsicherheit."}[fam]
    if "Smart Rate" in b['acc']: pshort=f"{b['n']} Ports inklusive HPE-Smart-Rate-Multi-Gigabit-Ports"
    elif poe_yes: pshort=f"{b['n']} Ports mit PoE+"
    else: pshort=f"{b['n']} Ports"
    kp1=(f"<p>Der HPE Aruba Networking {fam} {pid} ist ein gemanagter {lyr_de}-Switch der Aruba-{fam}-Serie mit {pshort}, betrieben unter ArubaOS-Switch. "
         f"{pos}</p>")
    kp2=(f"<p>Der {pid} liefert eine Switching-Kapazität von {b['swk']} und bindet per {up} an das Netz an.{poe_k} "
         f"Er wird als versiegelte Original-Neuware geliefert.</p>")
    kurz=kp1+kp2
    # intro
    poe_i=(f" Der {pid} versorgt Access Points, IP-Telefone und Kameras per Power over Ethernet direkt über das Netzwerkkabel." if poe_yes
           else f" Der {pid} ist ein Modell ohne PoE und konzentriert sich auf reine Datenanbindung.")
    role={"2530":"den Layer-2-Campus-Access","2540":"den Campus-Access mit 10G-Uplinks","2920":"den Layer-3-Campus-Access","2930F":"den Layer-3-Campus-Access","2930M":"den Layer-3-Campus-Access und die Aggregation","3810M":"die Layer-3-Campus-Aggregation"}[fam]
    i1=(f"Der HPE Aruba Networking {fam} {pid} ist ein gemanagter {lyr_de}-Switch aus der Aruba-{fam}-Familie mit {b['acc']}, "
        f"ausgelegt für {role} und betrieben unter ArubaOS-Switch (ProVision).")
    stk_de={"2530":f"Der {pid} wird als eigenständiger Switch betrieben; über Single-IP-Virtual-Stacking lassen sich bis zu 16 Einheiten zentral verwalten.",
            "2540":f"Der {pid} wird als eigenständiger Access-Switch mit festen 10G-SFP+-Uplinks betrieben.",
            "2920":f"Über ein optionales Stacking-Modul lassen sich bis zu vier {pid} per Backplane-Stacking (40 Gbit/s je Stacking-Port) zu einem logischen Switch zusammenfassen.",
            "2930F":f"Per VSF (Virtual Switching Framework) lassen sich bis zu acht {pid} zu einem logischen Switch zusammenfassen.",
            "2930M":f"Per VSF-Backplane-Stacking (Ring bis zehn Einheiten, 100 Gbit/s je Switch) lassen sich mehrere {pid} zu einem logischen Switch zusammenfassen.",
            "3810M":f"Über ein dediziertes Stacking-Modul lassen sich mehrere {pid} per Backplane-Stacking (bis 336 Gbit/s) zu einem stapelbaren Switch mit chassisähnlicher Ausfallsicherheit zusammenfassen."}[fam]
    i2=(f"Mit {b['n']} Ports erreicht der {pid} eine Switching-Kapazität von {b['swk']} bei einer Weiterleitungsrate von {b['mpps']}.{poe_i} {stk_de}")
    i3=(f"Im Formfaktor {b['bauform'].split(';')[0]} arbeitet der {pid} im Temperaturbereich {btemp}; Kühlung und Stromversorgung des {pid} "
        f"übernehmen {b['kueh']} sowie {b['strom']}. Unter ArubaOS-Switch bietet der {pid} {feat}. "
        f"Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch.")
    intro=[ws(i1),ws(i2),ws(i3)]
    # faq
    faq=[["Ist dies ein originales HPE-Produkt?", f"Ja. Der {pid} ist HPE-Aruba-Networking-Original-Neuware der Aruba-{fam}-Serie – versiegelt geliefert und für den Betrieb unter ArubaOS-Switch vorgesehen."],
         [f"Wie viele Ports hat der {pid}?", f"Der {pid} bietet insgesamt {b['n']} Ports: {portkonfig}."]]
    if poe_yes: faq.append([f"Wie hoch ist das PoE-Budget des {pid}?", f"Der {pid} stellt {b['poe']} bereit und versorgt angeschlossene Geräte direkt über das Netzwerkkabel."])
    else: faq.append([f"Unterstützt der {pid} PoE?", f"Nein. Der {pid} ist ein Modell ohne Power over Ethernet und für reine Datenanbindung ausgelegt."])
    if fam=="2530" or fam=="2540":
        faq.append([f"Lässt sich der {pid} stapeln (Stacking)?", f"Der {pid} unterstützt {stack} und wird ansonsten als eigenständiger Access-Switch betrieben."])
    else:
        faq.append([f"Lässt sich der {pid} stapeln (Stacking)?", f"Ja. Der {pid} unterstützt {stack} und lässt sich so zu einem logischen Switch zusammenfassen."])
    attrs=[["Switch-Typ","Managed"],["Layer",lyr],["Portanzahl",str(b['n'])],["Port-Konfiguration",portkonfig],
           ["Port-Geschwindigkeit",b['spd']],["Uplink-Ports",upattr],["PoE",b['poe']],["Switching-Kapazität",b['swk']],
           ["Durchsatz",b['mpps']],["Bauform",b['bauform']],["Stromversorgung",b['strom']],["Kühlung",b['kueh']],
           ["Stacking",stack],["Betriebstemperatur",btemp],["Anwendung",ANW[fam]],["Zustand","Neu, versiegelt"]]
    doc=DOC[fam]; prov={a[0]:[doc,"datasheet"] for a in attrs if a[0]!="Zustand"}
    versand=f"{float(b['gw'].replace(',','.'))+2.0:.2f}".replace('.',',')
    return {"_facts":{"unterkategorie":"Managed Switch ("+lyr+")","quell_url":doc,"verifiziert_am":VERIF},
            "artikelname":artikel,"titel_tag":titel,"meta_description":meta,"artikelgewicht":b['gw'],"versandgewicht":versand,
            "kurzbeschreibung":ws(kurz),"intro":intro,"kompatibilitaet":["HPE Aruba Networking ArubaOS-Switch","Aruba Central","Aruba AirWave"],
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{b['price']}.00"}

# ------------------------------------------------------------------ build a bundle
def build(cat, pids):
    doc={pid:author(pid) for pid in pids}
    cpath=ROOT/"stage3_content"/f"{cat}_content.json"; cpath.write_text(json.dumps(doc,ensure_ascii=False,indent=1),encoding="utf-8")
    recs=reconcile_content(cpath,brand=BRAND,rules=rules,weights=weights)
    out=ROOT/"output"/"switches"/cat
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    assemble_bundle(recs,rules,batch=cat,category=cat,out_dir=out)
    S.process_main(out/f"Hexwaren_{cat}_Main.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    S.process_faq(out/f"Hexwaren_FAQ_{cat}.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    e3=cat.replace("_"," "); mp=out/f"Hexwaren_{cat}_Main.csv"
    rows=list(csv.reader(mp.read_bytes().decode("utf-8-sig").splitlines(),delimiter=";")); H=rows[0]
    i1,i2,i3=H.index("Kategorie Ebene 1"),H.index("Kategorie Ebene 2"),H.index("Kategorie Ebene 3"); data=[]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        r[i1],r[i2],r[i3]=E1,E2,e3; data.append(r)
    write_csv(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{cat}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in pids:
        vrows.append([pid,f"{SPECS[pid]['price']},00","PHASE-1-SCHÄTZUNG — NICHT marktgegroundet. Tarif nach Konfigurations-Tier. Echte HPE-Marktpreis-Recherche folgt.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/cat; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {cat} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:8]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:100])
    return out

if __name__=="__main__":
    import sys as _s
    fams={"2530":"Aruba_2530_Switches","2540":"Aruba_2540_Switches","2920":"Aruba_2920_Switches",
          "2930F":"Aruba_2930F_Switches","2930M":"Aruba_2930M_Switches","3810M":"Aruba_3810M_Switches"}
    only=_s.argv[1] if len(_s.argv)>1 else None
    for fam,cat in fams.items():
        if only and fam!=only: continue
        build(cat,[p for p,s in SPECS.items() if s['fam']==fam])
