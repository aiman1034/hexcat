# HPE/Aruba STEP-2 BATCH-4 CORRECTION — auditor live-HPE re-verification (2026-06-30)

Three items from the auditor's live-HPE check of batch 4. **No new families.** All re-emitted gate-clean:
`ok=True viol=0`, **validate_dir = 0**, whole switch tree **1205 SKUs all unique**, **0 new Merkmal NAMES**.
HPE/Aruba switch total **169 → 171**.

## (1) ✅ CX 10000 Switching-Kapazität: 3,6 → 3,2 Tbit/s (all 4 SKUs) — FIXED
HPE's CURRENT published figure is **3,2 Tbps** bidirectional (a50004267enw QuickSpec + current a00119682enw datasheet + HPE Store
all agree). The 3,6 was the **port-sum**, not the published spec — the exact trap flag-don't-fabricate guards against.
- **Durchsatz confirmed = 2.000 Mpps** (this one IS published for the 10000, unlike the 10040's wire-speed).
- "3,2 Tbit/s" is a **REUSED** Wertliste value → **0 new value** for this fix.

## (2) ✅ CX 8360 per-model SwK — RE-VERIFIED, all 6 CORRECT (no change)
Re-checked against the **CURRENT a50002121ENW Rev.2 (©2025)** (the 2023 cache could have been stale, like the 10000):

| Model | Catalog | Current doc | Result |
|---|---|---|---|
| 8360-32Y4C | 2,4 Tbit/s | 2.4 Tbps | MATCH |
| 8360-16Y2C | 1,2 Tbit/s | 1.2 Tbps | MATCH |
| 8360-48Y6C | 4,8 Tbit/s | 4.8 Tbps | MATCH |
| 8360-48XT4C | 1,76 Tbit/s | 1.76 Tbps | MATCH |
| 8360-12C | 2,4 Tbit/s | 2.4 Tbps | MATCH |
| 8360-24XF2C | 0,88 Tbit/s | 880 Gbps | MATCH |

Both the 2023 cache and the 2025 doc report identical per-model "Switching capacity" table cells (read by JL part-number column,
NOT port-math). The 4,8 Tbps in web-search summaries is the **series-max headline** (= the 48Y6C top model) — correctly NOT applied
across all models. **The 10000 was the only stale value; the cache is otherwise current for the 8360.**

## (3) ✅ CX 9300 / 9300S RE-ENUMERATION (8325-precedent depth) — +2 to 9300S
Re-enumerated against the datasheet **a00125744ENW Rev.2 (2025)** + ordering-depth sources.
- **NET-NEW = 2 → 9300S now 10 (was 8):**
  - `S0F86A` — 9300S-32C8D **Front-to-Back, DC**, non-TAA
  - `S0F85A` — 9300S-32C8D **Front-to-Back, DC**, **TAA**
  - These are the **FtB-DC twins of the BtF-DC pair S0F87A/S0F88A** we already had — the exact 9300S analogue of the 8325 S1D09-12A
    finding: absent from the datasheet "Product SKUs" table but present in the OEM **AOS-CX Release Notes "Products Supported"** table.
    Internally consistent (the datasheet lists both a FtB-DC PSU S0F89A and a BtF-DC PSU S0F90A, so both DC airflows have bundles).
- **9300-32D = 3, confirmed complete** (R9A29A/R9A30A/R8Z96A) — **NO DC bundle, NO TAA bundle** (AC-only; triangulated datasheet +
  QuickSpec + RN). QuickSpec a50004291enw turned out to be the OLD 9300-only revision (V3, Nov-2022, predates 9300S).
- **EXCLUDED** (PSU/fan/accessory): 9300 fans R8Z99A/R9A00A + AC PSUs R8Z97A/R8Z98A; 9300S fans S0F93A/S0F94A + DC PSUs S0F89A/S0F90A
  + AC PSUs S0F91A/S0F92A; rack kits JL482C/JL483C/J9583B; feature-pack/Central/Fabric-Composer subscription SKUs. No R9F tracking SKU.

### ⚠️ ZU_VERIFIZIEREN on S0F85A/S0F86A (shipped on best grounding; auditor to confirm)
- **Bundle-title verbatim long-description** — the RN "Products Supported" table gives the canonical name; a00125744enw has no SKU
  row, and the buy.hpe.com per-PID pages for S0F85A/S0F86A did not surface in search (the BtF-DC S0F87A/S0F88A pages did).
- **FtB-DC Betriebstemperatur = 0–45 °C** — applied per the **FtB-airflow rule** (every FtB config = 0–45; every BtF = 0–40), NOT a
  per-doc 9300S-FtB-DC table cell. Confirm against the auditor's table.
- All other 9300S-FtB-DC specs are identical to the grounded BtF-DC pair except airflow (1600 W DC, 6 fans FtB, 16 Tbit/s, encryption+PTP in prose).

## Footprint
- RE-EMITTED `output/switches/Aruba_CX_10000_Switches/` (SwK fix) + `Aruba_CX_9300S_Switches/` (+S0F85A/S0F86A, 8→10) + their content JSON
- `config/coverage/gate_completeness.yaml` (9300S 8→10) · driver · PROJECT_AUDIT · this note
- **0 new Merkmal NAMES · 0 src/ changes · 0 rules.yaml change** (no new E3) · nothing created in JTL. Pricing Phase-1 ESTIMATE.
