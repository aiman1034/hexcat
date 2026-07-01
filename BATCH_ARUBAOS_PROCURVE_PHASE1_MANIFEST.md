# STEP 2 — ArubaOS-Switch + ProCurve · PHASE 1 MANIFEST (enumeration + classification only; NO authoring)

Enumerated the ArubaOS-Switch / ProVision line (current + legacy ProCurve) against the **ordering guide + AOS-Switch/
ProVision Release Notes "Products Supported" table** (the deep source — it surfaced RN-only variants the QuickSpecs drop),
via 3 enumeration agents; seed floor was `catalog_manifest/hpe_aruba_switches_FULL.csv` (114 PIDs / 17 families). Counts read
from OEM Models/RN tables, never port-math. **Hersteller = HP (locked). 0 authoring, 0 rules.yaml change, 0 bundle emitted.**

**True denominator ≈ 164 PIDs / ~19 families** (seed floor 114 → +~50 net-new). **0 new Merkmal NAMES needed** (the 15
fixed set + the validated chassis/module set cover the whole line; ArubaOS specifics = new VALUES / prose).

## (1) FULL FAMILY LIST — counts (true, ordering-guide) + FIXED/MODULAR classification

### A. FIXED switches (E3 "… Switches") — 16 families, **100 PIDs**
**Current Aruba (ArubaOS-Switch, 56):** 2530 **17** · 2540 **4** · 2920 **5** · 2930F **16** · 2930M **8** · 3810M **6 base** (+3 CTO — §4.2).
**Legacy ProCurve/ProVision (EOL, 44):** 2510 **4** · 2610 **5** · 2615 **1** · 2620 **5** · 2810 **2** · 2910al **4** · 2915 **1** · 3500 (+3500yl) **8** · 3800 **9** · 6600 **5**.
- 3810M / 3800 / 6600 are **STACKABLE FIXED** switches (backplane/meshed stacking, fixed ports) — **not** chassis. Confirmed.

### B. MODULAR CHASSIS (E3 "… Switches") — 3 families, **~21 chassis PIDs**
- **Aruba 5400R zl2** (current) — **11** (5406R/5412R × v2/v3; net-new +1 = **J9826A**, RN-only). No discrete fabric (integrated in mgmt).
- **HPE ProCurve 8200zl** (legacy) — **~6** (8206zl/8212zl + rev-B + bundles). **Only family with a discrete Fabric Module.**
- **HPE ProCurve 5400zl v1** (legacy) — **4** (5406zl/5412zl open + bundles).

### C. MODULES (E3 "… Modules", plural) — **~43 PIDs**
- **Aruba 5400R zl2 Modules** — **11** (10 zl2 line cards + J9827A Management Module).
- **ArubaOS-Switch Expansion Modules** — **9** (2920/2930M/3810M uplink + stacking modules: JL078A/079A/081A/083A/084A/325A/J9731-733A).
- **HPE ProCurve zl Modules** (shared 5400zl v1 + 8200zl) — **~23** = ~19 shared zl/v2-zl line cards + 8200zl Mgmt(J9092A)/**Fabric(J9093A)**/SSM(J9095A) + 5400zl Mgmt(J8726A). **Model ONCE** with `Kompatible Serie = {5400zl, 8200zl}` — the line-card pool is shared.

## (2) PROPOSED E3 NAMES (+ ProCurve decision FLAGGED)
Mirroring the ratified brand+line precedent ("Cisco **Catalyst** 9300 Switches" / "Aruba **CX** 6300M Switches"):
- **Current Aruba:** `Aruba 2530/2540/2920/2930F/2930M/3810M Switches` · `Aruba 5400R zl2 Switches` + `Aruba 5400R zl2 Modules` · `Aruba OS-Switch Expansion Modules`.
- **Legacy ProCurve:** proposed `HPE ProCurve <model> Switches` (2510/2610/2615/2620/2810/2910al/2915/3500/3800/6600, 8200zl, 5400zl) + `HPE ProCurve zl Modules`.
- **⚠️ OPEN DECISION (yours):** legacy prefix — **`HPE ProCurve <model>`** (recommended; ProCurve = the line, mirrors "Cisco Catalyst") vs **`HPE <model>`** (seed's flatter form) vs fold under **`Aruba …`** (misleading — these were never Aruba-branded). Hersteller stays HP either way. I did NOT invent — pick one and I apply it in Phase 2.

## (3) NEW WERTLISTE VALUE CANDIDATES (grouped by Merkmal — 0 new NAMES)
- **Stacking:** `Backplane-Stacking (…Gbit/s)` — NEW value (2920/2930M/3810M; distinct from CX VSX/VSF) · `VSF (bis 8/10 Einheiten)` (2930F/2540 — reuse CX value) · `Meshed Stacking` (3800) · `Kein` (2530/2610…).
- **PoE:** `Class 6 (IEEE 802.3bt, 60 W/Port)` (2930M R0M67A/68A — reuse from CX 6300) · `740-W-Budget`-tier phrasing (2930F JL557-559, 2920 J9836A) — new VALUE.
- **Modultyp:** reuse `Linecard`/`Management-Modul`/`Fabric-Module`; NEW value `System-Support-Modul` (8200zl J9095A).
- **Kompatible Serie / Unterstützte Supervisor-Engines / Bauform (HE) / Anwendung:** per-family new VALUES (ProVision/AOS-Switch OS context, 4U/7U zl chassis, the shared-pool Kompatible Serie).
- **Port-Konfiguration / Portanzahl:** new VALUE `12` + `2G/2SFP+` combo (2930F JL693A — the only 12-port).

## (4) OPEN DECISIONS / SOURCE CONFLICTS / SEED DEFECTS (for your call)
**Seed-manifest data defects (catalog_manifest/hpe_aruba_switches_FULL.csv — corrections, NOT yet applied):**
1. **JL311A / JL312A are NOT switches** (rows 204-205 mislabel them as "2930F 740W" switches) — they are the 2930F **8-port Cable Guard** + **Power Shelf** (accessories). The real 740W switches are **JL557A/JL558A** (48G 740W non-TAA) + JL559A (TAA). Rows 206-207 also mislabel JL557A/JL558A as "24G TAA."
2. **2910al** (J9145-48A, 4) and **6600** (J9263-65A/J9451-52A, 5) families **entirely missing** from the seed — add.
3. **2510** missing **J9279A** (2510G-24) → should be 4 PIDs, not 3.
4. **5400R zl2** missing **J9826A** (5412R-92G-PoE+/4SFP v2, RN-only) → 11 chassis, not 10.
5. The c04293383 5400R QuickSpec has a **column-scramble** mislabeling module PIDs (e.g. J9991A as a transceiver) — the AOS-S 16.11 RN "Products Supported" table is authoritative; module descriptions taken from there.

**Classification/scope decisions:**
- **3810M CTO bundles** JL428A/JL429A/JL430A = "switch + module + PSU" config kits → per the CTO exclude rule, 3810M base = **6**; if you carry pre-configured bundles, +3. **Your call.**
- **3500 + 3500yl → MERGE** (one OEM QuickSpec c01813146 lists all 8; non-PoE + PoE-L3 tiers of one series). Recommend one E3 `HPE ProCurve 3500 Switches` (8 PIDs).
- **Shared zl module pool** (5400zl v1 ↔ 8200zl) — model ONCE as `HPE ProCurve zl Modules` (Kompatible Serie = both), not per-chassis (avoids ~19-card duplication).
- **8200zl discrete Fabric Module** (J9093A) — the only chassis with a separate fabric SKU; its "Unterstützte Fabric-Module" prose applies only here (5400R zl2 + 5400zl v1 = integrated).

**Source-quality flags (for a clean confirmation pass before Phase-2 authoring):**
- **8200zl** chassis/module set corroborated via **reseller listings + a 2012 ordering-guide mirror** (HPE 8200zl QuickSpecs was unreachable/Akamai-blocked). Chassis PIDs confirmed across ≥3 resellers; recommend a clean OEM-QuickSpec confirmation before authoring.
- **The oldest ProCurve** (2510/2610/2615/2810/2915) predate AOS-Switch 16.x — dropped from modern RN "Products Supported" lists (K/KA/KB ProVision firmware era); QuickSpecs Models tables are the denominator. New-sealed *availability* in 2026 is a sourcing call (real PIDs banked regardless).

## STOP — for review
No authoring, no rules.yaml, no bundle emitted. Awaiting your decisions on: (a) the **ProCurve E3 naming**, (b) **3810M CTO bundles** keep/exclude, (c) the **shared-zl-module** single-bundle approach, and (d) whether to **apply the 5 seed-manifest corrections** now. Then Phase 2 authors per family — fixed families on the 15-Merkmal set, the zl chassis/modules on the validated CX chassis/module schema.
