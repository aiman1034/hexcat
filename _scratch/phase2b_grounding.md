# ArubaOS-Switch Phase 2b — grounding matrix (44 PIDs). Hersteller=HP. QuickSpec tables = denominator, never port-math.

## E3 naming (per operator, grounded per-family from product name)
- ProCurve-era → "HP ProCurve <model> Switches": 2510/2610/2615/2620/2810/2910al/2915/3500/6600
- Post-ProCurve → "HP 3800 Switches" (never ProCurve-branded)
- 3500 MERGE = ONE E3 "HP ProCurve 3500 Switches" (all 8)

## Layer rule (LOCKED — consistent w/ Phase 2a: static-routing→L2, dynamic-protocol→L3)
- L2 (no routing OR static-only): 2510, 2610(static 16 routes), 2615(static), 2810
- L3 (dynamic RIP/OSPF/BGP): 2620(RIP), 2915(RIP), 2910al(RIP/OSPF), 3500(OSPF), 3800(OSPF/BGP), 6600(OSPF/BGP)
  (static-routing L2 models still MENTION statisches IPv4-Routing in prose, like 2530/2540)

## AGENT-1 DONE — 2510/2610/2810 (11) — src DA-12599 v8 / DA-13032 v7 / DA-12600 v11
### 2510 (4) — "HP ProCurve 2510 Switches" — L2, Stacking Kein, 0-45°C, internes PSU
- J9019B 2510-24 : 24×10/100 + 2×dual-pers(RJ45/SFP GbE)=26; SwK 8.8; 6.5 Mpps; PoE nein; FANLESS(0dB); 2.22 kg
- J9020A 2510-48 : 48×10/100 + 2×10/100/1000(RJ45) + 2×SFP=52; SwK 17.6; 13 Mpps; PoE nein; Lüfter; 2.74 kg
- J9279A 2510G-24: 20×10/100/1000 + 4×dual-pers=24; SwK 48; 35.7 Mpps; PoE nein; Lüfter; 3.27 kg
- J9280A 2510G-48: 44×10/100/1000 + 4×dual-pers=48; SwK 96; 71.4 Mpps; PoE nein; Lüfter; 3.90 kg
### 2610 (5) — "HP ProCurve 2610 Switches" — L2+static-L3(16 routes), Stacking Kein, 0-50°C, internes PSU (+opt. ext. RPS/EPS)
  uplink pattern = 2×10/100/1000(RJ45) + 2×SFP; FE access
- J9085A 2610-24     : 24×10/100 +2G+2SFP=28; SwK 12.8; 9.5 Mpps; PoE nein; FANLESS(0dB); 4.63 kg
- J9086A 2610-24/12PWR: 24×10/100(12 PoE) +2G+2SFP=28; 12.8; 9.5; PoE 802.3af Class3 15.4W Budget 124W@12P; Lüfter; 3.40 kg
- J9087A 2610-24-PWR : 24×10/100(alle PoE) +2G+2SFP=28; 12.8; 9.5; PoE 802.3af Class3 15.4W BUDGET=PSU/EPS-abh.(ZU_VERIF→customer-safe); Lüfter; 6.83 kg
- J9088A 2610-48     : 48×10/100 +2G+2SFP=52; SwK 17.6; 13.0 Mpps; PoE nein; Lüfter; 4.88 kg
- J9089A 2610-48-PWR : 48×10/100(alle PoE) +2G+2SFP=52; 17.6; 13.0; PoE 802.3af Class3 15.4W BUDGET=PSU/EPS-abh.(customer-safe); Lüfter; 7.58 kg
### 2810 (2) — "HP ProCurve 2810 Switches" — L2 pure, Stacking Kein, 0-45°C, internes PSU (+opt. ext. RPS)
- J9021A 2810-24G: 20×10/100/1000 + 4×dual-pers=24; SwK 48; 35.7 Mpps; PoE nein; Lüfter; 3.27 kg
- J9022A 2810-48G: 44×10/100/1000 + 4×dual-pers=48; SwK 96; 71.4 Mpps; PoE nein; Lüfter; 3.90 kg
NOTE J9280A naming trap: roster=2510G Gigabit(96G); a diff QuickSpec reused J9280A for an FE 2510-48G(17.6G) — if live shop lists FE, flag.

## CACHED families — grounded (me, from datasheets/cache/hpe-aruba/)

### 2615 (1) — "HP ProCurve 2615 Switches" — cache 2615.txt
- J9565A 2615-8-PoE: 8× 10/100 PoE(af) + 2× dual-personality(10/100/1000 o SFP) = 10 ports; L3(static);
  SwK 5.6 Gbps; 4.1 Mpps; PoE 802.3af 67W; compact(10×6.28×1.75in); internes PSU(100-240VAC); FANLESS(sibling-2915);
  Stacking Kein; 0-45°C; 1.66 kg (3.66 lb). TAA No.

### 2620 (5) — "HP ProCurve 2620 Switches" — cache 2620.txt — all L3(static+RIP IPv4/IPv6), 0-55°C, PoE 802.3af/at(30W PoE+)
  port pattern = N× 10/100 + 2× 10/100/1000(RJ45) + 2× SFP
- J9623A 2620-24    : 24FE+2G+2SFP=28; SwK 12.8; 9.5 Mpps; PoE 0W(non); FANLESS; 2.59 kg
- J9624A 2620-24-PPoE+: 28 (12 of 24 FE = PoE+); 12.8; 9.5; PoE 128W; Lüfter(variabel); 3.19 kg
- J9625A 2620-24-PoE+: 28 (24 FE PoE+); 12.8; 9.5; PoE 382W; Lüfter; 4.84 kg
- J9626A 2620-48    : 48FE+2G+2SFP=52; SwK 17.6; 13.0 Mpps; PoE 0W; Lüfter; 2.94 kg
- J9627A 2620-48-PoE+: 52 (48 FE PoE+); 17.6; 13.0; PoE 382W; Lüfter; 5.23 kg

### 2915 (1) — "HP ProCurve 2915 Switches" — cache 2915.txt
- J9562A 2915-8G-PoE: 8× 10/100/1000 PoE(af) + 2× dual-personality = 10 ports; L3(static+RIP);
  SwK 20 Gbps; 14.8 Mpps; PoE 802.3af 67W; compact; internes PSU; FANLESS(explicit); Stacking Kein; 0-45°C; 1.66 kg. TAA No.

### 3500 (8) — "HP ProCurve 3500 Switches" — cache 3500-3500yl.txt — AGENT ad64d45ab17103a69 (pending)
  8 PIDs: J9470A/J9471A/J9472A/J9473A (FE base+PoE) + J8692A/J8693A/J9310A/J9311A (yl Gigabit). L3(OSPF).
  Top model up to 153.6 Gbps crossbar / 111.5 Mpps (determine which). Single 10-GbE slot; meshed/virtual stacking.

## WEB-agent families (pending)
- ad3cc1ac0dff5c092: 2510(4: J9019B/J9020A/J9279A/J9280A) + 2610(5: J9085A/J9086A/J9087A/J9088A/J9089A) + 2810(2: J9021A/J9022A)
- aa7b22d48d2a6c844: 2910al(4: J9145A/J9146A/J9147A/J9148A) + 6600(5: J9263A/J9264A/J9265A/J9451A/J9452A)
- ab478916a59af2b19: 3800(9: J9573A/J9574A/J9575A/J9576A/J9584A/J9585A/J9586A/J9587A/J9588A) [E3 "HP 3800 Switches"]

## AGENT-3 DONE — 3800 (9) — "HP 3800 Switches" (NOT ProCurve) — src QuickSpec c04111485 via mirrors
### series: L3 full(OSPF/BGP/IPv6, ProVision), 1U, dual hot-swap PSU(X311 400W / X312 1000W-PoE), Lüfter front-to-back,
###   Stacking="Meshed Stacking (dediziertes Modul J9577A, bis 10 Einheiten, bis 336 Gbit/s)", 0-55°C.
###   CORRECTION: XG models = 10GBASE-T copper RJ45 (NOT CX4). PoE budget PSU-abhängig→customer-safe.
- J9573A 3800-24G-PoE+-2SFP+ : 24×G PoE+ + 2×SFP+ =26; SwK 88; 65.4 Mpps; PoE 802.3at(PSU-abh.,X312); PSU X312; 7.20 kg
- J9574A 3800-48G-PoE+-4SFP+ : 48×G PoE+ + 4×SFP+ =52; SwK 176; 130.9; PoE 802.3at(PSU-abh.); PSU X312; 7.64 kg
- J9575A 3800-24G-2SFP+      : 24×G + 2×SFP+ =26; SwK 88; 65.4; PoE nein; PSU X311; 7.21 kg
- J9576A 3800-48G-4SFP+      : 48×G + 4×SFP+ =52; SwK 176; 130.9; PoE nein; PSU X311; 7.50 kg(est)
- J9584A 3800-24SFP-2SFP+    : 24×SFP(1G fibre) + 2×SFP+ =26; SwK 88; 65.4; PoE nein; PSU X311; 7.26 kg
- J9585A 3800-24G-2XG        : 24×G + 2×10GBASE-T(RJ45) =26; SwK 88; 65.4; PoE nein; PSU X311; 7.17 kg
- J9586A 3800-48G-4XG        : 48×G + 4×10GBASE-T =52; SwK 176; 130.9; PoE nein; PSU X311; 7.70 kg(est)
- J9587A 3800-24G-PoE+-2XG   : 24×G PoE+ + 2×10GBASE-T =26; SwK 88; 65.4; PoE 802.3at(PSU-abh.); PSU X312; 7.40 kg(est)
- J9588A 3800-48G-PoE+-4XG   : 48×G PoE+ + 4×10GBASE-T =52; SwK 176; 130.9; PoE 802.3at(PSU-abh.); PSU X312; 7.80 kg
  port speed: SFP+ models "10/100/1000(RJ45),1/10GbE(SFP+)"; XG models "10/100/1000(RJ45),10GbE(10GBASE-T)"; J9584A "100/1000(SFP),1/10GbE(SFP+)"

## AGENT-4 DONE — 3500 (8) — "HP ProCurve 3500 Switches" (MERGE) — src cached c01813146
### series: L3 (static+RIP base; OSPF/BGP via Premium-Lizenz J8993A), 1U, internes AC-PSU(+opt. ext. EPS/RPS),
###   Kühlung="Lüftergekühlt"(yl acoustic 55+dB; per-model field war ZU_VERIF→customer-safe),
###   Stacking="Kein (kein Stacking-Bus; Resilienz via HP-Switch-Meshing + Distributed Trunking)", 0-55°C.
###   CORRECTION: 10-GbE-Modulschacht NUR auf yl-Modellen; FE-Modelle haben nur die 4 Dual-Personality-Uplinks.
### FE-base (10/100, up_modular=False, uplink=4×dual-personality):
- J9470A 3500-24     : acc 20×10/100; up 4×dual-pers(RJ45 10/100/1000 o SFP); =24; SwK 12; 8.9 Mpps; PoE nein; 5.40 kg
- J9471A 3500-24-PoE : acc 20×10/100(Class3 PoE); up 4×dual-pers(PoE o SFP); =24; SwK 12; 8.9; PoE 802.3af 398W; 6.00 kg
- J9472A 3500-48     : acc 44×10/100; up 4×dual-pers; =48; SwK 16.8; 12.5 Mpps; PoE nein; 6.10 kg
- J9473A 3500-48-PoE : acc 44×10/100(Class3 PoE); up 4×dual-pers(PoE o SFP); =48; SwK 16.8; 12.5; PoE 802.3af 398W; 6.80 kg
### yl-Gigabit (10/100/1000, up_modular=True, uplink=1 Modulschacht bis 4×10-GbE; dual-pers counted in acc):
- J8692A 3500-24G-PoE yl : acc 20×10/100/1000(Class3 PoE)+4×dual-pers(PoE o SFP)=24; SwK 101.8; 75.7 Mpps; PoE 802.3af 398W; 6.40 kg
- J8693A 3500-48G-PoE yl : acc 44×10/100/1000(Class3 PoE)+4×dual-pers=48; SwK 149.8; 111.5 Mpps; PoE 802.3af 398W; 7.30 kg
- J9310A 3500-24G-PoE+ yl: acc 20×10/100/1000(Class4 PoE+)+4×dual-pers(PoE+ o SFP)=24; SwK 101.8; 75.7; PoE 802.3at 398W; 6.29 kg
- J9311A 3500-48G-PoE+ yl: acc 44×10/100/1000(Class4 PoE+)+4×dual-pers=48; SwK 149.8; 111.5; PoE 802.3at 398W; 7.05 kg
  port speed: FE "10/100(Access),10/100/1000(Uplink)"; yl "10/100/1000(RJ45)".  Portanzahl excl. optional module.

## AGENT-2 DONE — 2910al(4) + 6600(5) — src ultima-computers 2910al QS / andovercg 6600 QS DA-13267
### 2910al (4) — "HP ProCurve 2910al Switches" — L3-lite(static+RIP, NOT OSPF), 0-55°C, Lüfter, internes PSU(+opt RPS)
###   Stacking="Kein (Standalone; Single-IP-Virtual-Stacking bis 16)"; uplink=4×dual-pers built-in + up_modular(2 Schächte, bis 4×10G via CX4/SFP+)
- J9145A 2910al-24G     : acc 20×10/100/1000 + 4×dual-pers=24; up=2 Modulschächte(bis 4×10-GbE); SwK 128; 95 Mpps; PoE nein; 4.95 kg
- J9146A 2910al-24G-PoE+: acc 20×10/100/1000(Class4 PoE+) + 4×dual-pers(PoE+)=24; up=module; SwK 128; 95; PoE 802.3at(Budget PSU-abh.→customer-safe); 5.60 kg
- J9147A 2910al-48G     : acc 44×10/100/1000 + 4×dual-pers=48; up=module; SwK 176; 131 Mpps; PoE nein; 5.08 kg
- J9148A 2910al-48G-PoE+: acc 44×10/100/1000(Class4 PoE+) + 4×dual-pers(PoE+)=48; up=module; SwK 176; 131; PoE 802.3at(Budget PSU-abh.→customer-safe); 5.88 kg
### 6600 (5) — "HP ProCurve 6600 Switches" — L3/L4 adv DC-server-edge(static+RIP+OSPF via Premium-Lizenz J9305A), ALL NON-PoE,
###   dual hot-swap PSU(1×J9269A), N+N Hot-Swap-Lüftertray, front-to-back reversibel, 1U.
###   Stacking="Kein (kein Stacking-Bus; Switch-Meshing + Distributed Trunking)". Temp 5-40°C (J9265A=0-40°C).
- J9263A 6600-24G     : acc 20×10/100/1000; up=4×dual-pers(RJ45 o SFP); =24; SwK 48; 35.7 Mpps; 5-40°C; 7.58 kg
- J9264A 6600-24G-4XG : acc 20×10/100/1000 + 4×dual-pers; up=4×SFP+(10G) FEST; =28; SwK 101.8; 75.7; 5-40°C; 7.80 kg
- J9265A 6600-24XG    : acc 24×SFP+(10G); up_modular(alle 24 als 10G-Uplink); =24; SwK 322.8; 240.2 Mpps; 0-40°C; 8.94 kg
- J9451A 6600-48G     : acc 44×10/100/1000; up=4×dual-pers; =48; SwK 96; 71.4; 5-40°C; 8.62 kg
- J9452A 6600-48G-4XG : acc 44×10/100/1000 + 4×dual-pers; up=4×SFP+(10G) FEST; =52; SwK 176; 130.9; 5-40°C; 8.62 kg
  6600 port speed: "10/100/1000(RJ45),1/10GbE(SFP+)" (24XG="10GbE(SFP+)"). CORRECTION vs Phase-1: 6600 NOT backplane-stack.

## Stacking values (new Wertliste, 0 new NAMES)
- Kein (2510/2610/2615/2620/2810/2915 access)
- "Meshed Stacking (bis 10 Einheiten, dediziertes Stacking-Modul)" — 3800
- 6600 / 2910al stacking form → from agents (6600 = backplane/ProVision; 2910al likely Kein or virtual)
