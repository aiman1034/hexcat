# STEP 2 — CX 6400/8400 PHASE B — PRE-IMPORT REQUIREMENTS (2026-06-30)

Authored the remaining **32 SKUs** against the LOCKED Phase-A schema (commit 97d98a3) — reused verbatim, no
re-proposal. All gate-clean (`ok=True viol=0`), **validate_dir = 0** on all 4 bundles, whole switch tree
**1270 SKUs, all unique**. **29 new Wertliste VALUES, 0 new Merkmal NAMES.** Phase-1 estimate prices, flagged.

## A. Per-family before → after
| Bundle (E3) | Before | After | Net-new |
|---|---|---|---|
| Aruba CX 6400 Switches (chassis) | 1 | **11** | +10 |
| Aruba CX 6400 Modules | 4 | **19** | +15 |
| Aruba CX 8400 Switches (chassis) | 0 | **1** | +1 |
| Aruba CX 8400 Modules | 0 | **6** | +6 |

**CX 6400 chassis (+10):** bare R0X24A/C (6405) + R0X25A/C (6410); switch bundles R0X26A/C (6405) + R0X27A (6410);
pre-config bundles R0X29A (96G PoE+4SFP56), R0X30A (48SFP++8SFP56), JL741A (6410 96G PoE). v1/v2 carried-both.
**CX 6400 modules (+15):** line cards R0X38B/C, R0X39B/C, R0X40B/C, R0X41C, R0X42A/C, R0X43A/C, R0X44C, R0X45C,
S0E48A, **S1T83A** (the sweep's loose end — a 6400 v2 Class-8-PoE line card). No fabric SKU (6400 forwarding is distributed).
**CX 8400 (+7, EOL/EoS-2019, retained):** chassis JL375A; mgmt JL368A; **fabric JL367A** (`Modultyp=Fabric-Module`,
7,2 Tbit/s — the 8400 is a 3-tier design with a separate fabric, unlike the 6400); line cards JL363A/JL365A/JL366A/JL687A.

## B. NEW WERTLISTE VALUES (29 — 0 new Merkmal NAMES)
- **Modultyp:** `Management-Modul` (approved Phase A), `Fabric-Module` reused, `Linecard` reused.
- **Kompatible Serie — 1 NEW:** `Aruba CX 8400` (`Aruba CX 6400` already from Phase A).
- **Bauform — 1 NEW:** `19-Zoll-Rackmontage (8 HE)` (7/12 HE from Phase A/existing).
- **Steckplätze — 2 NEW** (6405 5+2, 8400 8+2 → 6410 10+2 from Phase A).
- **Switching-Kapazität — 3 NEW:** `14 Tbit/s` (6405), `7,2 Tbit/s (Fabric-Modul…)`, the 8400 system flag.
- **Unterstützte Supervisor-Engines / Redundanz — 1 each NEW** (8400 mgmt strings).
- **Stromversorgung — 2 · Kühlung — 5 · Port-Konfiguration — 11 · PoE — 2 NEW** (the per-chassis/per-card strings; see Attributes.csv).

## C. ⚠️ ZU_VERIFIZIEREN — flagged, awaiting your couriered datasheet tables (flag-don't-fabricate, never port-math)
1. **Per-component weights** — every line card + the mgmt/fabric modules + the chassis carry **flagged ESTIMATE** artikelgewicht
   (the IGSG/QuickSpec weight tables didn't render through the proxy). Fill from your courier.
2. **Per-card Switching-Kapazität** — not published per line card → `ZU_VERIFIZIEREN` on all 17 line cards.
3. **Per-card PoE budget watts** — Class (4/6/8) grounded from the titles; the absolute card budget is PSU-/config-dependent → `ZU_VERIFIZIEREN`.
4. **CX 6405 PSU + fan-tray counts** — grounded for the 6410 (4/4); the 6405 counts weren't in the brief → `ZU_VERIFIZIEREN` in the strings.
5. **CX 8400 system switching capacity** — `ZU_VERIFIZIEREN` (fabric-module-dependent; JL367A = 7,2 Tbit/s per module, grounded).
6. **6410 height = 12 HE** (QuickSpec; the IGSG said 13U — confirm against your courier).

## D. Footprint
- RE-EMITTED `output/switches/Aruba_CX_6400_{Switches,Modules}/` (grown to 11/19) + NEW `Aruba_CX_8400_{Switches,Modules}/` + 4 content JSON
- `config/rules.yaml` (+2 8400 E3) · `config/coverage/gate_completeness.yaml` (4 records → full scope) · driver · PROJECT_AUDIT · this note
- **0 new Merkmal NAMES · 0 src/ change** (chassis >50 kg handled by gating pre-remap, the Cisco order) · nothing created in JTL.

## E. JTL — create these 4 E3 (mirror the Cisco chassis/Modules pattern) + the 29 new Wertliste values
`Netzwerk & Infrastruktur ▸ Switches ▸` **Aruba CX 6400 Switches · Aruba CX 6400 Modules · Aruba CX 8400 Switches · Aruba CX 8400 Modules**.
