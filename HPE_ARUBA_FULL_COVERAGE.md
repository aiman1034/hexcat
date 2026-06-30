# HPE/Aruba Switches — STEP 1c FULL-SCOPE Coverage (match-Cisco)

**Date:** 2026-06-30 · **Scope:** match Cisco exactly — NO EoL cutoff, INCLUDE fixed + chassis + modules; keep granularity (all orderable airflow/AC-DC/PoE/TAA/rev variants) + E3 convention. **Enumeration only — 0 SKU authored, 0 specs, 0 Merkmal, nothing in JTL.**

## NEW FULL-SCOPE DENOMINATOR = **533 orderable PIDs** across **72 E3 families**
(replaces the STEP-1b 224 and the STEP-1 ~352 figures). Manifest: `catalog_manifest/hpe_aruba_switches_FULL.csv` (one row per PID).

### Per-OEM-line subtotals
| OEM line | PIDs | Families |
|---|---|---|
| Aruba CX | 159 | 19 |
| ArubaOS-Switch (incl. ProVision/ProCurve) | 103 | 15 |
| Modules (line-card / fabric / mgmt / expansion) | 103 | 7 |
| SMB / Instant On / OfficeConnect | 85 | 13 |
| Comware-FlexFabric (DC) | 45 | 11 |
| Comware-FlexNetwork (campus/legacy) | 38 | 7 |
| **TOTAL** | **533** | **72** |
### By type: fixed-switch **392** · chassis **38** · module **103**.

## Per-family counts
**Aruba CX (19):** 6000 (6) · 6100 (5) · 6200F (27) · 6200M (10) · 6300F (8) · 6300L (3) · 6300M (22) · 4100i (2) · 6400 (7, chassis) · 8100 (12) · 8320 (3) · 8325 (6) · 8325H (8) · 8360 (18) · 8400 (2, chassis) · 9300 (3) · 9300S (8) · 10000 (4) · 10040 (5)
**ArubaOS-Switch (15):** 2530 (17) · 2540 (4) · 2920 (5) · 2930F (16) · 2930M (8) · 3810M (9) · 5400R zl2 (10, chassis) · HPE 2510 (3) · 2610 (5) · 2615 (1) · 2620 (5) · 2810 (2) · 2915 (1) · 3500 (8) · 3800 (9)
**Comware-FlexFabric (11):** 5700 (3) · 5800 (7) · 5900 (2) · 5930 (3, chassis) · 5940 (7, chassis) · 5945 (8) · 5950 (3) · 5980 (1) · 7900 (4, chassis) · 12900 (2, chassis) · 12900E (5, chassis)
**Comware-FlexNetwork (7):** 5120 SI (6) · 5130 EI (9) · 5130 HI (4) · 5500 EI (5) · 5500 HI (5) · 5510 HI (5) · 10500 (4, chassis)
**SMB (13):** Instant On 1430 (7) · 1830 (5) · 1930 (7) · 1960 (6) · OfficeConnect 1410 (9) · 1420 (9) · 1620 (3) · 1810 (7) · 1820 (6) · 1910/V1910 (5) · 1920 (9) · 1920S (7) · 1950 (5)
**Modules (7):** CX 6400 (19) · CX 8400 (6) · 5400R zl2 (11) · ArubaOS-Switch Expansion 2920/2930M/3810M (9) · FlexNetwork 10500 (45) · FlexFabric 5930/5940 (7) · FlexFabric 12900E (6)

## E3-convention OPEN decisions (sub-family granularity — operator to confirm)
The CX series split into F/M/L/H sub-lines. Proposed = **separate E3 per sub-line** (mirrors the Cisco 9300 vs 9300X / 6300F vs 6300M pattern): `Aruba CX 6200F` + `6200M`; `6300F` + `6300M` + `6300L`; `8325` + `8325H`. (The new-CX agent suggested merging F/M into one "Aruba CX 6200/6300/8325 Switches" E3 — your call. Manifest currently keeps them separate.)

## ZU_VERIFIZIEREN — auditor live-verification (origin reachable on auditor side)
**PID present but a detail needs a clean OEM source (21 rows):**
- **CX 6200F** JL724B / S0M81A / S0M86A / S0G13A — the S0M81A–S0M85A (4SFP/1G non-TAA) config↔PID 1:1 order (QuickSpecs 2-col drift); full 27-PID set vs live a00059762enw.
- **CX 8320** JL479A/JL579A/JL581A — exact EoS date (note-only now; included regardless).
- **FlexFabric 5940** JH390A/JH391A/JH394A/JH395A — exact EoS dates (note-only; all IN).
- **FlexNetwork 10500 Modules** JG916A/JH194A/JH195A/JH196A — PID present, description needs a clean QuickSpecs (cached QS columns corrupt; trusted clean datasheets for the rest).
- **FlexFabric 12900E Modules** JL845A/JL846A/JL847A/JH360A/JQ061A/JH953A — **PARTIAL** (6 store-confirmed of a larger Type-S/X/H/HB/HF set).

**Whole-family / coverage gaps flagged (NOT padded — real OEM tables needed):**
- **FlexFabric 12900E Modules** — full line-card/fabric/MPU ordering table NOT cached → recommend caching QuickSpecs **c04928717** before authoring this module family.
- **FlexFabric 7900 Modules** — the 7900 EA/EB/EC/EG I/O + fabric line cards were NOT enumerated (separate follow-up); chassis are in (4).
- **CX 8325H** — DC-power bundle existence unconfirmed (all 8 surfaced SKUs are AC); the 8 AC/airflow/TAA SKUs are pinned.
- **5400R zl2 Modules** — J9992A↔J9995A and J9987A↔J9996A description↔PID disambiguation (PID set certain).
- **HPE 2510** J9279A (2510G-24 sibling) + **HPE 2810** full ordering table — older ProCurve, confirm against a clean QuickSpecs.
- **HPE 1810 v2** J9802A/J9803A exact port/uplink rows.
- **New-sealed availability of the oldest ProCurve** (2510/2610/2615/2810/2915/3500/3800) in 2026 — real PIDs banked; whether Hexwaren stocks them new-sealed is a sourcing call. **3800** is enterprise-class (not SMB) — confirm it belongs in the ArubaOS-Switch lane.

## Method & honesty
- Carried forward every PID banked in STEP-1/1b (no regression); added the restored EOL families, the chassis (CX 6400/8400, 5400R zl2, FlexNetwork 10500), all module families, and the misses (6200M entirely; 6300L/8325H/10040; FlexFabric 5945/5950/5980/7900/12900; SMB 1430/1920S; ProCurve 2510/2610/2810/3800).
- **Every PID is verbatim from an OEM QuickSpecs/datasheet ordering table** (cached PDFs + verbatim-OEM CDN mirrors; hpe.com + arubanetworks.com origins Akamai-blocked from this host). **No PID was invented, padded, or guessed** — the agents explicitly rejected non-existent SKUs (e.g. FlexFabric 7902/7912 do not exist; 12900E is 5 chassis not 4; 5950/5980 single-count confirmed). Gaps are flagged ZU_VERIFIZIEREN, never filled.
- Excluded (same as Cisco): transceivers/DACs, bare accessories (PSU/fan/rack/stacking-cable), licenses, eval/NFR, refurb, CTO "--", pure-redundant bundles, and 1 firewall service blade (JG372A, borderline).
- **Recommend a residential-IP/authenticated confirmation pass** on the ZU_VERIFIZIEREN items + the 6200F/8325 bundle lists + the 12900E/7900 module tables before STEP-2 authoring.
