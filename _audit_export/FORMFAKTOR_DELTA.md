# Formfaktor sweep — delta (operator review; report-only, MSA/name-grounded, within-family)
_2026-06-17. Method CORRECTION: form factor is a PHYSICAL property — multiple FFs share a speed (10G: SFP+/XFP/XENPAK; 100G: QSFP28/SFP-DD/CPAK/CFP2). So checks are WITHIN-family (SFP↔SFP+↔SFP28↔SFP56↔SFP-DD by single-lane speed; QSFP+↔QSFP28↔QSFP56↔QSFP-DD↔QSFP-DD800) + Name. XFP/XENPAK/X2/CPAK/CFP/CFP2/CXP/GBIC/OSFP/coherent-QSFP-DD = valid distinct FFs, NOT flagged._

## CONFIRMED corrections (within-family, MSA-grounded)
| Brand | PN | Formfaktor old → new | Speed | Rule |
|---|---|---|---|---|
| HPE | S4B43A | QSFP-DD → **QSFP56** | 200G | MSA: 200G QSFP = QSFP56 |
| HPE | S2N63A | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Extreme | 10303 | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Extreme | MGBIC-BX40-D | SFP+ → **SFP** | 1G | MSA: 1G single-lane = SFP |
| Extreme | 10053H | SFP+ → **SFP** | 1G | MSA: 1G single-lane = SFP |
| Dell | DAC-SFP-25G-1M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | DAC-SFP-25G-2M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | DAC-SFP-25G-2.5M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | DAC-SFP-25G-3M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | DAC-SFP-25G-5M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | AOC-SFP-25G-2M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | AOC-SFP-25G-7M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | AOC-SFP-25G-10M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | AOC-SFP-25G-20M | SFP+ → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Dell | DAC-QSFP-100G-0.5M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | DAC-QSFP-100G-1M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | DAC-QSFP-100G-2M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | DAC-QSFP-100G-3M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | DAC-QSFP-100G-5M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | AOC-QSFP-100G-3M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | AOC-QSFP-100G-7M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | AOC-QSFP-100G-10M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Dell | AOC-QSFP-100G-30M | QSFP+ → **QSFP28** | 100G | MSA: 100G QSFP = QSFP28 |
| Arista | C-D800-D800-1M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | C-D800-D800-2M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-1M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-3M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-5M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-7M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-10M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-15M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-20M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-25M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | A-D800-D800-30M | QSFP-DD → **QSFP-DD800** | 800G | MSA: 800G QSFP = QSFP-DD800 |
| Arista | QDD-200G-2LR4 | QSFP-DD → **QSFP56** | 200G | MSA: 200G QSFP = QSFP56 |
| Arista | C-Z100-Z100-1M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Z100-Z100-2M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Z100-Z100-3M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Z100-Q100-1M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Z100-Q100-2M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Z100-Q100-3M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Y100-Y100-1M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Y100-Y100-2M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Y100-Y100-3M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Y100-Q100-1M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Y100-Q100-2M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-Y100-Q100-3M | SFP → **SFP-DD** | 100G | MSA: 100G single-lane = SFP-DD |
| Arista | C-S50-S50-1M | SFP → **SFP56** | 50G | MSA: 50G single-lane = SFP56 |
| Arista | C-S50-S50-2M | SFP → **SFP56** | 50G | MSA: 50G single-lane = SFP56 |
| Arista | C-S50-S50-3M | SFP → **SFP56** | 50G | MSA: 50G single-lane = SFP56 |
| Arista | CAB-S-S-25G-0.5M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | CAB-S-S-25G-1M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | CAB-S-S-25G-1.5M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | CAB-S-S-25G-2M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | CAB-S-S-25G-2.5M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | CAB-S-S-25G-3M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | CAB-S-S-25G-5M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-3M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-5M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-7M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-10M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-15M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-20M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-25M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | AOC-S-S-25G-30M | SFP → **SFP28** | 25G | MSA: 25G single-lane = SFP28 |
| Arista | CAB-SFP-SFP-0.5M | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Arista | CAB-SFP-SFP-1M | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Arista | CAB-SFP-SFP-1.5M | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Arista | CAB-SFP-SFP-2M | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Arista | CAB-SFP-SFP-2.5M | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Arista | CAB-SFP-SFP-3M | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Arista | CAB-SFP-SFP-5M | SFP → **SFP+** | 10G | MSA: 10G single-lane = SFP+ |
| Supermicro | AOC-TSR-FS | SFP+ → **SFP** | 1G | MSA: 1G single-lane = SFP |
| Supermicro | AOM-TSR-FS | SFP+ → **SFP** | 1G | MSA: 1G single-lane = SFP |

**Confirmed total: 74** (Dell 25G→SFP28 / 100G-QSFP→QSFP28; Arista 800G→QSFP-DD800 + 100G/50G→SFP-DD/SFP56; Extreme 1G/10G SFP↔SFP+; HPE 200G→QSFP56 + 25G→SFP28).

## AMBIGUOUS — breakout / splitter / coherent (FF is end-dependent; flag for review, NOT auto-corrected)
- **Cisco (11):** QDD-4X100G-FR-S, QDD-4X100G-LR-S, QDD-2X100-SR4-S, QDD-2X100-CWDM4-S, QDD-2X100-LR4-S, QSFP-2Q200-CU3M, DP01QSDD-ZF1, QDD-2Q200-CU1M …
- **Juniper (7):** QDD-2X400G-DR4-P, QDD-2X400G-FR4, QDD-2X400G-FR4-P, QDD-2X400G-LR4-10, QDD-2X400G-LR4-P, QDD-2X100G-CWDM4, QDD-2X100G-LR4
- **HPE (7):** S4B39A, S4B40A, R9B60A, R9B58A, R9B62A, R9B61A, R9B59A
- **Fortinet (4):** FG-CABLE-SR10-SFP+, FG-CABLE-SR10-SFP+5, FN-CABLE-QSFPDD-2QSFP56-L1, FN-CABLE-QSFPDD-2QSFP56-LB5
- **Dell (16):** DAC-Q56DD-4Q56-SFF-100G-1M, DAC-Q56DD-4Q56-SFF-100G-2M, DAC-Q56DD-4Q56-SFF-100G-3M, DAC-Q56DD-2Q56-SFF-200G-1M, DAC-Q56DD-2Q56-SFF-200G-2M, DAC-Q56DD-2Q56-SFF-200G-3M, DAC-Q56DD-2Q56-CMIS-200G-1M, DAC-Q56DD-2Q56-CMIS-200G-2M …
- **Arista (16):** CAB-D-2Q-200G-1M, CAB-D-2Q-200G-2M, CAB-D-2Q-200-2.5, CAB-D-4Q-200G-1M, CAB-D-4Q-200G-2M, CAB-D-4Q-200-2.5, CAB-D-8S-200G-1M, CAB-D-8S-200G-2M …
- **NVIDIA (3):** MCP7H60-W002R26, MCP7F60-W002R26, MCP7F60-W02AR26

**Ambiguous total: 64** — e.g. QDD-2X100/4X100 breakouts (module=QSFP-DD, ends=QSFP28), Dell Q56DD-2Q56 splitters, NVIDIA MCP7 splitters, Cisco DP01QSDD-ZF1 (coherent QSFP-DD @100G = valid).

---

## L8 review response (2026-06-17) — REJECT + re-screen + 64-disposition

### REJECT (1) — accepted
- **Arista QDD-200G-2LR4: QSFP-DD → QSFP56 is WRONG.** It is a 2×100GBASE-LR4 **breakout in a QSFP-DD shell**; the "200G QSFP = QSFP56" rule over-fired. **Reverts to QSFP-DD** (= current value → 0-change) and moves to the ambiguous/breakout bucket. (HPE S4B43A stays QSFP56 — native 200G, not a breakout.)

### RE-SCREEN of the confirmed bucket for the SAME failure mode (name implies a bigger physical shell than the speed-rule assigned) — **1 new instance found**
- **Arista C-Y100-* ×9 → physically DSFP, NOT SFP-DD (the speed-rule mislabel).** PN letter `Y` = DSFP; Anschlusstyp "DSFP auf DSFP"; Artikelname "100G DAC DSFP". The within-family rule mapped 100G-single-lane→SFP-DD, overriding the explicit DSFP. **DSFP ≠ SFP-DD** (distinct MSAs). Parts: C-Y100-Y100-1M/2M/3M, C-Y100-Q100-1M/2M/3M, C-Y100-2S50-1M/2M/3M.
  - **⚠ SCHEMA: `DSFP` is NOT in the locked `PHYSICAL_FORMFAKTOR` set** (0 parts use it). **DECIDED (operator 2026-06-17): ADD `DSFP` to the locked vocabulary** (`constants.py` PHYSICAL_FORMFAKTOR_ORDERED + `rules.yaml` + B.11 gate token) and set the 9 C-Y100-* parts = **DSFP**. **Staged for Phase 2 — NOT edited now** (adding the token without re-emitting the 9 parts in the same pass would split code↔data state — same rule as the Sortiernummer tuple-swap). Anschlusstyp ("DSFP auf DSFP") already correct.
- **HPE S4B43A — name rider.** Formfaktor QSFP56 is correct (operator-confirmed), but the **Artikelname reads "200G QSFP-DD SR4"** → the prose must be fixed QSFP-DD→QSFP56 in Phase 2 (Formfaktor and name must agree).
- **No other downgrades.** D800 ×11 (QSFP-DD800 = the 800G grade of the QSFP-DD shell; correction stands; names optionally tighten "QSFP-DD"→"QSFP-DD800"). QSFP-4X10G-LR-S (Cisco), JNP-QSFP-4X10GE-IR/LR + QSFP-4X10GE-LR-25 (Juniper), FG-TRAN-QSFP-4XSFP/4SFP-5 (Fortinet) = QSFP+/QSFP28 transceivers with an MPO **fibre** breakout; the module IS the QSFP host → current value correct (the "→SFP" flags were "SFP" matching inside "QSFP").

### 64-AMBIGUOUS — host-FF disposition applied (Formfaktor = host/switch-port end; breakout topology stays in Anschlusstyp)
Screened all 693 breakout/splitter/coherent parts. **Result = 4 parts change value (operator's "expect few" confirmed); the rest already carry the correct host FF.**
| Brand | PN | Formfaktor old → new | Why |
|---|---|---|---|
| Fortinet | FN-CABLE-QSFPDD-2QSFP56-L1 | QSFP56 → **QSFP-DD** | PN/host = 400G QSFP-DD; QSFP56 was the 2× fan-out end |
| Fortinet | FN-CABLE-QSFPDD-2QSFP56-LB5 | QSFP56 → **QSFP-DD** | "" |
| Fortinet | FN-CABLE-QSFPDD-8SFP56-L1 | SFP56 → **QSFP-DD** | host = 400G QSFP-DD; SFP56 was the 8× fan-out end |
| Fortinet | FN-CABLE-QSFPDD-8SFP56-LB5 | SFP56 → **QSFP-DD** | "" |

**Unchanged (already host FF):** QDD-2X100/4X100 → QSFP-DD · Dell Q56DD-2Q56/4Q56 → QSFP-DD · Dell Q28DD-* → QSFP28-DD · NVIDIA MCP7* → QSFP-DD/QSFP56 · Arista CAB-D-2Q/4Q/8S → QSFP-DD · Juniper QDD-2X400G/2X100G → QSFP-DD · HPE S4B39A/S4B40A (200G breakout) → QSFP-DD · Cisco coherent DP01QSDD-ZF1 → QSFP-DD · Extreme 20G-DACP-SFP-DD2SFP → SFP-DD.

**Residual [VERIFY] (not auto-changed — speed/shell ambiguous):** Fortinet FG-TRAN-QSFP-4XSFP / FG-TRAN-QSFP-4SFP-5 (host QSFP+ vs QSFP28 depends on 40G vs 100G — needs Fortinet DS); Fortinet FG-CABLE-SR10-SFP+ / FG-CABLE-SR10-SFP+5 (100G SR10/CXP-class host FF — current SFP+; doesn't fit the QSFP-DD/OSFP disposition).

### Revised confirmed Formfaktor set for Phase 2
**85 changes**: **70 within-family** (original 74 − QDD-200G-2LR4 − 6 C-Y100 + 3 newly-found C-Z100-2S50) **+ 6 host-FF disposition** (4× Fortinet QSFP-DD cables + 2× FG-CABLE-SR10) **+ 9 DSFP** (C-Y100-*, operator-decided ADD-to-vocab 2026-06-17). **Plus rider:** S4B43A name fix (QSFP-DD→QSFP56), D800 ×11 optional name-tighten. Both Fortinet families grounded from the cached DS: FG-TRAN-QSFP-4XSFP/4SFP-5 = dual-rate 40G/100G → **KEEP QSFP28** (no change); FG-CABLE-SR10-SFP+/+5 = passive OM3 MPO-zu-10×LC fan-out mating a separate SR10 **CFP2 module** → **NOT a CFP2 module itself → Formfaktor EMPTY** (operator FIX 2; already Kategorie/Kabeltyp = MPO Kabel/OM3). Frozen into `PHASE2_MANIFEST.csv` (v2, 124 total incl. Juniper-ET omits). Separate deferred item: Arista far-end Anschlusstyp mislabel ×94 (host FF correct; far-end needs Arista-DS grounding).

## Excluded as VALID (not errors): XFP/XENPAK/X2 (10G), CPAK/CFP/CFP2 (100G), CXP, GBIC, OSFP, coherent QSFP-DD — distinct MSA form factors that legitimately share a speed with SFP+/QSFP28.