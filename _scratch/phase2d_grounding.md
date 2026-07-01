# ArubaOS-Switch Phase 2d — LEGACY zl modular lane. Hersteller=HP. Schema = CX chassis/module (commit 97d98a3) VERBATIM.
# 3 E3 (rules.yaml additions-only): "HP ProCurve 5400zl Switches" (chassis) · "HP ProCurve 8200zl Switches" (chassis) · "HP ProCurve zl Modules" (shared pool)
# 0 new Merkmal NAMES. Exactly ONE new Modultyp VALUE = "System-Support-Modul" (J9095A). Prose = ProVision/ProCurve (NOT AOS-CX).

## Schema reuse (from _scratch/aruba_cx_6400_build.py)
- CHASSIS unterkategorie="Modularer Switch (Chassis)"; 10 Merkmale = Switch-Typ(Modular-Chassis)/Layer/Steckplätze/Bauform/
  Switching-Kapazität/Stromversorgung/Kühlung/Unterstützte Supervisor-Engines/Redundanz/Anwendung (+Zustand). temp→prose.
  GATE PRE-REMAP (E3 stays "Modularer Switch (Chassis)" for the >50kg ceiling) then remap E1/E2/E3.
- MODULE unterkategorie="Switch-Modul"; Linecard=Modultyp/Kompatible Serie/Portanzahl/Port-Konfiguration/[PoE]/Switching-Kapazität
  (NO Port-Geschwindigkeit); Mgmt=Modultyp/Kompatible Serie; Fabric=Modultyp/Kompatible Serie/Switching-Kapazität.
- Kompatible Serie per card: shared="HP ProCurve 5400zl / 8200zl"; J8726A="HP ProCurve 5400zl"; 8200zl trio="HP ProCurve 8200zl".
- 5400zl = integrated forwarding (NO discrete fabric) → prose. 8200zl = ONLY zl chassis w/ DISCRETE fabric (J9093A) → prose.

## B) 8200zl CHASSIS — "HP ProCurve 8200zl Switches" — COURIERED (verbatim, operator) — 10 PIDs
### 8212zl (12-slot, 9U, 4 PSU slots, chassis 22,88 kg, up to 428 Mpps THROUGHPUT [NOT port-math a Gbit/s], 0-45°C,
###   max 288×10/100/1000 OR 48×10-GbE; DISCRETE fabric via J9093A):
- J8715A / J8715B = 8212zl Base System (A/B rev)
- J9091A / J9091B = 8212zl Replacement Chassis + Fan Tray (ships empty, spare) (A/B rev)
- J9639A = 8212-92G-PoE+/2XG-SFP+ v2 zl w/Premium (bundle)
- J9641A = 8212 v2 zl w/Premium (bundle)
### 8206zl (6-slot, 6U, base 17,36 kg, ~half 8212 port max = ~144×GbE OR ~24×10-GbE, 0-45°C):
- J9475A = 8206zl Base System
- J9477A = 8206zl Replacement Chassis (empty spare)
- J9638A = 8206-44G-PoE+/2XG-SFP+ v2 zl w/Premium (bundle)
- J9640A = 8206 v2 zl w/Premium (bundle)
### Per-chassis Gbit/s Switching-Kapazität NOT in snippets → customer-safe ("Wire-Speed / modellspezifischer Gbit/s-Wert nicht ausgewiesen; bis 428 Mpps Durchsatz").

## 8200zl trio MODULES (Serie {8200zl}) — COURIERED mapping (8212 datasheet authoritative; andovercg offset-by-one)
- J9092A = Management-Modul
- J9093A = Fabric-Module   (the ONLY discrete zl fabric)
- J9095A = System-Support-Modul  ← the ONE new Modultyp VALUE

## A) 5400zl CHASSIS — "HP ProCurve 5400zl Switches" — AGENT ac33f4c94a545bf06 (pending)
   OLDER gen (5406zl 6-slot + 5412zl 12-slot), DISTINCT from 5400R zl2. Integrated fwd (no discrete fabric)→prose.
   Seed: J8697A/J8698A/J8699A/J8700A + J9447A/J9448A (v2 Premium) + replacement/empty chassis. Enumerate exact roster.

## A) 5400zl CHASSIS DONE — "HP ProCurve 5400zl Switches" — 6 PIDs — src QuickSpec DA-12436 v9
### series: L3, ProVision, INTEGRATED fabric + INTEGRATED management (no discrete fabric, no separate supervisor SKU in v1),
###   Kühlung="Lüftergekühlt (Lüftertray, front-to-back)", temp 0-55°C (0-40°C mit J8706A/J8707A-Modulen)→prose.
###   zl-PSU: J8712A 875 W / J9306A 1500 W PoE+ (Hot-Swap, redundant, separat). SwK PUBLISHED (no customer-safe needed).
### 5406zl (6 slots, 4U, 2 PSU-Schächte): SwK 322,8 Gbit/s (Fabric 345,6), 240,2 Mpps, max 144×GbE OR 24×10G
- J8697A 5406zl Intelligent Edge : Leergehäuse (ohne PSU); 10,68 kg bare
- J8699A 5406zl-48G Intelligent Edge : v1-Bundle (2× J8702A + 1× J8712A 875W); 48 GbE vorinstalliert, 4 offene Slots; 15,54 kg
- J9447A 5406-44G-PoE+/4SFP zl : v1-PoE+-Bundle (J9307A + J9308A + J9306A 1500W); 44× RJ45 PoE+ + 4 SFP, 4 offene Slots; 15,83 kg
### 5412zl (12 slots, 7U, 4 PSU-Schächte): SwK 645,6 Gbit/s (Fabric 691,2), 480,3 Mpps, max 288×GbE OR 48×10G
- J8698A 5412zl Intelligent Edge : Leergehäuse (ohne PSU); 15,85 kg bare
- J8700A 5412zl-96G Intelligent Edge : v1-Bundle (4× J8702A + 2× J8712A); 96 GbE, 8 offene Slots; 26,31 kg
- J9448A 5412-92G-PoE+/4SFP zl : v1-PoE+-Bundle (3× J9307A + J9308A + 2× J9306A); 92× RJ45 PoE+ + 4 SFP, 8 offene Slots; 26,39 kg
### FLAGS: rack 5406zl=4U (not 7U); J9447A/J9448A = base-SW PoE+ bundles NOT "with Premium" (real Premium J9532A/J9533A/
###   J9539A/J9540A = separate family, NOT in v1 QuickSpec → OUT-OF-SCOPE, not authored). All 6 well under 50kg ceiling.
###   J8726A mgmt module absent from v1 QuickSpec (mgmt integrated) → Agent B to resolve.

## C) zl MODULE POOL DONE — "HP ProCurve zl Modules" — 20 modules — src Install Guide 5998-4703 + QuickSpecs
### ⚠️ per-module Switching-Kapazität NOT published for ANY zl card → customer-safe "Chassis-Backplane-vermittelt (modellspezifischer Wert nicht ausgewiesen)". NO Port-Geschwindigkeit. Kompatible Serie: linecards="HP ProCurve 5400zl / 8200zl".
### PoE budget chassis-PSU-dependent → customer-safe "…abhängig von der Netzteilbestückung des Chassis". af=802.3af Class3, at=802.3at Class4 PoE+.
### v2 LINE CARDS (8, Linecard):
- J9534A: 24× 10/100/1000 (RJ45, at PoE+); n=24
- J9535A: 20× 10/100/1000 (RJ45, at PoE+) + 4× SFP (1G); n=24
- J9536A: 20× 10/100/1000 (RJ45, at PoE+) + 2× SFP+ (10G); n=22
- J9537A: 24× SFP (1G Glasfaser); n=24; no PoE
- J9538A: 8× SFP+ (10G); n=8; no PoE
- J9546A: 8× 10GBASE-T (RJ45, 10 GbE); n=8; no PoE   [CORR: not 24-port PoE+/2SFP+]
- J9547A: 24× 10/100 (RJ45, at PoE+); n=24            [10/100 only, no Gig]
- J9550A: 24× 10/100/1000 (RJ45); n=24; no PoE
### v1 LINE CARDS (8, Linecard):
- J8702A: 24× 10/100/1000 (RJ45, af PoE); n=24
- J8705A: 20× 10/100/1000 (RJ45, af PoE) + 4× SFP (1G); n=24
- J8706A: 24× SFP (1G Glasfaser); n=24; no PoE
- J8707A: 4× 10-GbE X2; n=4; no PoE                   [CORR: X2 not CX4]
- J8708A: 4× 10-GbE CX4; n=4; no PoE
- J9307A: 24× 10/100/1000 (RJ45, at PoE+); n=24       [in J9447A/J9448A bundles]
- J9308A: 20× 10/100/1000 (RJ45, at PoE+) + 4× SFP (1G); n=24  [CORR: not 2×10G]
- J9309A: 4× SFP+ (10G); n=4; no PoE
### MANAGEMENT / FABRIC / SSM (4):
- J8726A: Management-Modul, Serie {5400zl} only (0 Daten-Ports)
- J9092A: Management-Modul, Serie {8200zl}
- J9093A: Fabric-Module, Serie {8200zl} (the ONLY discrete zl fabric; bandwidth un-published→customer-safe)
- J9095A: System-Support-Modul, Serie {8200zl}  ← the ONE new Modultyp VALUE
### EXCLUDED (not on operator list / not fully spec'd): J9548A/J9549A/J9637A v2 cards, J9478A; PSUs/fan-trays. Available-if-wanted.
### Total zl Modules = 16 linecards + 4 mgmt/fabric/SSM = 20.
