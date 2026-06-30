# HPE/Aruba STEP-2 BATCH-3 ADDENDUM — 8325 family re-enumeration  (a00059009ENW Rev.3 ordering guide)

The auditor pinned the live ordering guide. Result: **+14 in-scope switch SKUs added to the existing Aruba CX 8325
bundle** (6 → **20**). All re-emitted gate-clean. **validate_dir = 0**; whole switch tree **1160 SKUs, all unique**.
Running HPE/Aruba switch total: **126 authored**.

## What was added (grounded verbatim from the a00059009ENW Rev.3 ordering/spec tables)
**(1) 8325P-32C telco line — 10 PIDs** (5 non-TAA + 5 TAA), all into the 8325 bundle with display model "CX 8325P":
- `S4A51A` FtB-AC · `S4A52A` BtF-AC · `S4A49A` FtB-DC · `S4A50A` BtF-DC · `S4A48A` base-unit (switch-only)
- `S0G09A` FtB-AC (TAA) · `S0G10A` BtF-AC (TAA) · `S0G07A` FtB-DC (TAA) · `S0G08A` BtF-DC (TAA) · `S0G12A` base (TAA)

**(2) 8325 (non-P) DC-power bundles — 4 PIDs** (the courier named the 32C pair; the ordering guide also has the 48Y8C pair):
- `JL857A` 8325-48Y8C FtB-DC · `JL858A` 8325-48Y8C BtF-DC · `JL859A` 8325-32C FtB-DC · `JL860A` 8325-32C BtF-DC

## 8325P ≠ 8325-32C — encoded in PROSE, NOT a new Merkmal (operator-instructed)
The 8325P is electrically a 32C (same 32× 100G, 6,4 Tbit/s, VSX, 0–40 °C) but adds **telco precision timing** — woven
into the feature sentence + Anwendung: *PTP/IEEE 1588v2, SyncE (G.8262.1), Telecom Profiles G.8275.1/.2 Class C,
Boundary-Clock/GNSS, SMPTE; NEBS-Konformität; erweiterte Breakout-Flexibilität (bis 128× 10G/25G); 5G-RAN/Mobile-Backhaul/Edge*.
No new Merkmal NAME; the differentiation is prose, as instructed.

## Re-enumeration completeness findings (flag-don't-fabricate)
- **8325H DC-power: NONE** — confirmed three ways (ordering section has only "8325H AC options"; spec tables are all
  100–240 VAC; 8325H has FIXED PSUs so there is no DC-swap path). The 8 captured 8325H AC SKUs are the complete set.
- **8100: complete (12, AC-only)** — no DC PSU in the doc (only AC PSUs JL600A/JL712A); 4 port-configs × {FtB,BtF} + 4 spares.
- **8320: complete (3, FtB-AC only) per a00036440enw** — no BtF twin and no DC PSU exist in that datasheet. *(Low-confidence
  closure flag: that is the older 2022 sheet; ruling out a BtF 8320 in any other generation would need a secondary HPE source —
  not invented here.)*
- **S0G11A — DEFERRED / ZU_VERIFIZIEREN:** absent from a00059009ENW Rev.3 (S0G07/08/09/10/12 all present, 11 skipped). Likely a
  reserved/unlisted number — NOT encoded, NOT fabricated. (Not counted in the 8325 denominator.)
- **R9F tracking SKUs:** none appear in the 8325 datasheet — nothing to exclude for this family. (The 8100's R9W PIDs are
  normal sellable bundles, not R9F tracking SKUs.) Origin of the R9F list = ZU_VERIFIZIEREN (not this doc).
- **Base-unit SKUs** (JL635A/JL636A/S4A48A/S0G12A) are bare switch boards ("do not include PSU/fans") → modeled as base units
  (configurable airflow, PSU/fans separate), not as FtB/BtF/AC/DC variants.

## NEW MERKMAL VALUES NEEDED (9 — 0 new Merkmal NAMES)
Switch-Typ/Layer/PoE/SwK (6,4 Tbit/s)/Durchsatz (2.000 Mpps)/Bauform/Betriebstemperatur all reuse existing values.
### Stromversorgung — 4 NEW:
- `2 Hot-Swap-Netzteile, redundant (N+1) – AC (100–240 VAC), NEBS-konform`
- `2 Hot-Swap-Netzteile, redundant (N+1) – DC (-48 V), NEBS-konform`
- `2 feldaustauschbare Hot-Swap-Netzteile (N+1, im Bundle); DC (-48 V)`
- `Feldaustauschbare Hot-Swap-Netzteile (AC oder DC), separat bestellt (bis 2, N+1); NEBS-konform`
### Kühlung — 2 NEW: `6 Hot-Swap-Lüfter (N+1, Airflow front-to-back)` · `6 Hot-Swap-Lüfter (N+1, Airflow back-to-front)`
### Port-Geschwindigkeit — 1 NEW: `40/100 GbE (QSFP+/QSFP28); erweiterte Breakout-Flexibilität (bis 128 Ports 10G/25G)`
### Uplink-Ports — 1 NEW: `alle 32 Ports flexibel (40/100G-QSFP28; bis zu 128× 10G/25G per Breakout)`
### Anwendung — 1 NEW: the 8325P telco/5G-RAN string (PTP/SyncE/G.8275/NEBS) — see `output/.../Attributes.csv`

**TOTAL ADDENDUM NEW WERTLISTE VALUES = 9**

## ZU_VERIFIZIEREN (auditor may refine)
- **8325P artikelgewicht** = `10,87 kg` (the 32C sibling weight, same 1U/32×100G chassis; the doc's 8325P spec column was not
  separately weight-captured) — low-risk logistics estimate.
- **S0G11A** (absent from doc), **R9F list origin**, **8320 BtF closure** — as above.

## Footprint
- RE-EMITTED `output/switches/Aruba_CX_8325_Switches/` (6 → 20) + its `stage3_content/*.json`
- `config/coverage/gate_completeness.yaml` (8325 6→20) · `_scratch/aruba_cx_access_build.py` (driver: display-series
  decoupling + 8325P/8325-DC configs) · `PROJECT_AUDIT.md` · this note
- **0 new Merkmal NAMES · 0 src/ changes · 0 rules.yaml change** (E3 "Aruba CX 8325 Switches" already exists) · nothing in JTL.
