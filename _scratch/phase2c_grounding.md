# ArubaOS-Switch Phase 2c — 5400R zl2 (current-gen modular). Hersteller=HP. Schema = CX chassis/module (commit 97d98a3) VERBATIM.
# 2 E3: "Aruba 5400R zl2 Switches" (11 chassis) + "Aruba 5400R zl2 Modules" (11 = 10 line cards + J9827A mgmt).
# 0 new Merkmal NAMES, NO new Modultyp value (reuse Linecard/Management-Modul). NO discrete fabric (integrated in mgmt module)→prose.
# OS = ArubaOS-Switch (current-gen, AOS-S 16.11 RN-supported; ProVision-ASIC hardware). DISTINCT from legacy 5400zl v1 (Phase 2d).

## CHASSIS DONE — "Aruba 5400R zl2 Switches" — 11 PIDs — src cached 5400Rzl2.txt (QuickSpec c04293383) + J9826A RN-only
### series: L3, ArubaOS-Switch (ProVision-ASIC), NO discrete fabric (fwd integrated in J9827A mgmt module),
###   included: 1× Mgmt Module J9827A + 1× Fan Tray (J9831A 5406R / J9832A 5412R); PSU "No PSU" = separate (700W J9829A / 1100W PoE+ zl2).
###   Kühlung="Lüftergekühlt (Lüftertray, front-to-back)"; temp→prose; PSU: bis 2 (5406R) / 4 (5412R) Hot-Swap-Netzteile redundant.
###   Redundanz: Netzteil(N+1)+Lüfter + VSF-Stacking (chassisübergreifend). SwK PER-CHASSIS (NOT 6400's 2,8 Tbit/s, NOT port-math):
### 5406R (6 slots, 4U): SwK "960 Gbit/s (Routing/Switching; Switch-Fabric 1.015 Gbit/s), 571,4 Mpps Durchsatz"
### 5412R (12 slots, 7U): SwK "1.920 Gbit/s (Routing/Switching; Switch-Fabric 2.030 Gbit/s), 1.142,8 Mpps Durchsatz"
### per-PID (model, slots, HE, weight kg, kind, pre-installed):
- J9821A 5406R zl2 Switch                : 6, 4U, 11,11; base (Leergehäuse, 6 offene Slots)
- J9822A 5412R zl2 Switch                : 12, 7U, 17,28; base (Leergehäuse, 12 offene Slots)
- J9823A 5406R-44G-PoE+/2SFP+ v2 zl2     : 6(4 offen), 4U, 12,75; bundle (44× GbE PoE+ + 2× SFP+ vorinstalliert)
- J9824A 5406R-44G-PoE+/4SFP v2 zl2      : 6(4 offen), 4U, 11,88; bundle (44× GbE PoE+ + 4× SFP vorinstalliert)
- J9825A 5412R-92G-PoE+/2SFP+ v2 zl2     : 12(8 offen), 7U, 20,50; bundle (92× GbE PoE+ + 2× SFP+ vorinstalliert)
- J9826A 5412R-92G-PoE+/4SFP v2 zl2      : 12(8 offen), 7U, 20,50(est, J9825A/JL001A-twin→flag); bundle (92× GbE PoE+ + 4× SFP; RN-only, seed missed)
- J9868A 5406R-8XGT/8SFP+ v2 zl2         : 6(4 offen), 4U, 12,75; bundle (8× 10GBASE-T + 8× SFP+ vorinstalliert)
- JL001A 5412R-92GT-PoE+/4SFP v3 zl2     : 12(8 offen), 7U, 20,50; bundle (92× GbE PoE+ + 4× SFP+ vorinstalliert)
- JL002A 5406R-8-SmartRate-PoE+/8SFP+ v3 : 6(4 offen), 4U, 12,75(est-sibling→flag); bundle (8× 1/2.5/5/10GBASE-T SmartRate PoE+ + 8× SFP+)
- JL003A 5406R-44GT-PoE+/4SFP v3 zl2     : 6(4 offen), 4U, 12,75; bundle (44× GbE PoE+ + 4× SFP+ vorinstalliert)
- JL095A 5406R-16SFP+ v3 zl2             : 6(4 offen), 4U, 12,75; bundle (16× SFP+ vorinstalliert)
### all <50kg (ceiling OK). GATE PRE-REMAP still required.

## MODULES DONE — "Aruba 5400R zl2 Modules" — 11 — src AOS-S 16.11 RN (authoritative) + QuickSpec c04293383 (3-source agree)
### ⚠️ CHASSIS UPDATE from module agent: J9827A supports up to 2 REDUNDANT mgmt modules (std 1/max 2) →
###   chassis Unterstützte Supervisor-Engines "…(J9827A), bis 2 redundant; Weiterleitung im Mgmt-Modul integriert (kein diskretes Fabric-Modul)";
###   chassis Redundanz "Management-Modul (bis 2, redundant), Netzteil (N+1, Hot-Swap) und Hot-Swap-Lüftertray; VSF chassisübergreifend".
### Global: Serie "Aruba 5400R zl2" ONLY; all MACsec v3 zl2, hot-swap. PoE = ALL 802.3at PoE+ 30W (NONE 802.3bt/Class6;
###   SmartRate ports = 802.3bz 2.5/5G). PoE budget chassis-PSU-dependent → customer-safe. Per-module SwK UN-PUBLISHED →
###   customer-safe "Chassis-Fabric-vermittelt (modellspezifischer Wert nicht ausgewiesen)". NO Port-Geschwindigkeit.
### LINE CARDS (10, Linecard) — 6 roster-guesses CORRECTED:
- J9986A: 24× 10/100/1000 (RJ45, Class 4 PoE+, MACsec); n=24; PoE+
- J9987A: 24× 10/100/1000 (RJ45, MACsec); n=24; no PoE
- J9988A: 24× SFP (1G Glasfaser, MACsec); n=24; no PoE          [CORR: not 20p PoE+/4SFP+]
- J9989A: 12× 10/100/1000 (RJ45, Class 4 PoE+) + 12× SFP (1G, MACsec) combo; n=24; PoE+
- J9990A: 20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× SFP+ (1/10G, MACsec); n=24; PoE+
- J9991A: 20× 10/100/1000 (RJ45, Class 4 PoE+) + 4× HPE Smart Rate (1/2.5/5/10GBASE-T, Class 4 PoE+, MACsec); n=24; PoE+  [CORR: not 24p 10GBASE-T]
- J9992A: 20× 10/100/1000 (RJ45, Class 4 PoE+) + 1× QSFP+ (40G, MACsec); n=21; PoE+   [CORR: not 24p 10GbE SFP+]
- J9993A: 8× SFP+ (1/10G, MACsec); n=8; no PoE
- J9995A: 8× HPE Smart Rate (1/2.5/5/10GBASE-T, Class 4 PoE+, MACsec); n=8; PoE+       [CORR: not 12p 10GbE SFP+]
- J9996A: 2× QSFP+ (40G, MACsec); n=2; no PoE                    [CORR: not 20p PoE+/4SFP+]
  (sequence skips J9994A — not a zl2 module)
### MGMT (1): J9827A Management-Modul, Serie "Aruba 5400R zl2"; 0 Daten-Ports (Konsole/OOB-Mgmt/AUX); bis 2 redundant, hot-swap.
