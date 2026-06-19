# Other-11 Close-Out — Datasheet Sample-Check Delta (operator L8 review input)
_Compiled 2026-06-17. Report-only. Nothing applied. The last gap of the correctness audit (the 7 attributes not covered by the DOM / temp / Formfaktor sweeps or the internal cross-consistency probe)._

## Why this pass exists
DOM, Betriebstemperatur, and Formfaktor **each** had systematic errors (3-for-3). By the operator's logic, the un-probed attributes could not be assumed clean. This pass cross-checks the 7 remaining attributes — **Standard, Reichweite, Anwendung, Länge, Kabeltyp, Faseranzahl, Transceiver Typ** — against each SKU's (datasheet-authored) PN/Name, the catalog's own internal convention, and the official datasheet, across all 13 brands. A representative cross-check, not all-SKU re-grounding.

## Result: 3 real findings (report-only), 4 clean
| Attribute | Verdict | Count | Grounding |
|---|---|---|---|
| **Faseranzahl** | **ERROR** | 7 (+2 [VERIFY]) | Catalog convention + Cisco datasheet + cross-brand proof |
| **Länge** | **ERROR** | 3 | PN suffix + 40 sibling parts |
| **Kabeltyp** | **ERROR** | 1 | Catalog convention (only empty in its category) |
| Transceiver Typ | clean | 0 | 76 flags = regex artifact (EX- prefix) |
| Reichweite | clean | 0 | 0 mismatches name↔attr |
| Standard | clean | 0 | 45 "mismatches" all breakout/dual-rate |
| Anwendung | clean | 0 | sensible category distribution |

---

## Finding 1 — Faseranzahl: dual-fiber SR-BiDi optics say 1, must be 2 (the real find)
**7 corrections + 2 [VERIFY].** Dual-fiber **SR-BiDi** transceivers carry `Anschlusstyp = "Duplex LC"` but `Faseranzahl = 1`. A duplex-LC BiDi link runs over **two strands** of MMF (two TX/RX channels, 832–918 nm, aggregated over a 2-strand duplex MMF) → Faseranzahl must be **2**.

**Triple-grounded:**
1. **Catalog's own convention** — every normal Duplex-LC optic = Faseranzahl 2 (138 Cisco parts); Simplex/Single-fiber = 1 (25 parts); MPO = 8/16/20/24. The SR-BiDi parts are the only Duplex-LC optics set to 1.
2. **Cisco official datasheet** (Cisco 40GBASE QSFP Modules, `data_sheet_c78-660083`): *"…enabling an aggregated 40 or 100-Gbps link over a **two-strand multimode fiber** connection"* + *"duplex LC connector interface … reuse of their existing 10 gigabit **duplex MMF** infrastructure."*
3. **Cross-brand proof** — **Lenovo 00YL631** (40G QSFP+ **SR-BiDi**, identical technology) correctly has Faseranzahl = **2**. Same optic, Cisco/Meraki say 1 → Cisco/Meraki is the outlier.

| Brand | PN | Anschlusstyp | Faseranzahl old → new |
|---|---|---|---|
| Cisco | QSFP-100G-SR1.2 | Duplex LC | 1 → **2** |
| Cisco | QSFP-40/100-SRBD | Duplex LC | 1 → **2** |
| Cisco | QSFP-40G-SR-BD | Duplex LC | 1 → **2** |
| Cisco | QSFP-40G-BD-RX | Duplex LC | 1 → **2** |
| Cisco | QDD-400G-BD | Duplex LC (UPC) | 1 → **2** |
| Cisco | QSFP-40-SR-BD | LC Duplex | 1 → **2** |
| Meraki | MA-QSFP-40G-SR-BD | Duplex LC | 1 → **2** |

**[VERIFY] (2 — do NOT apply):** Cisco **QSFP-100G-B20U4-I**, **QSFP-100G-B20D4-I** — Anschlusstyp "Duplex LC (bidirektional)" on a single-fiber B-series 100G-BiDi. If single-fiber (like its B40 siblings, which carry "LC" + 1), then Faseranzahl=1 is correct and the **connector label** is the defect; if dual-fiber, Faseranzahl=2. Needs the Cisco 100G-BiDi (B-series) datasheet — flagged, not guessed.

**Correctly excluded (Faseranzahl=1 is right):** all single-fiber BX/BiDi (`Single LC` / `Simplex` / `Einzelfaser`): Cisco SFP-10G-BX*, GLC-BX*, SFP-25G/50G-BX*, GLC-FE-100BX*, QSFP-100G-B40D/U-I, DP04CFP2-D15 (coherent single-fiber). QDD-400G-SR4.2-BD already correct (MPO-12, Faseranzahl 8). Juniper QDD-2X400G-FR4/LR4 already correct (Dual Duplex LC = 4 strands).

## Finding 2 — Länge: 3 Arista cable typos (2 m where PN + every sibling = 3 m)
| Brand | PN | Länge | Should be | Evidence |
|---|---|---|---|---|
| Arista | C-Z100-Z100-3M | 2 m | **3 m** | PN suffix `-3M`; all ~40 sibling `-3M` parts = 3 m |
| Arista | C-Y100-Y100-3M | 2 m | **3 m** | same |
| Arista | C-S50-S50-3M | 2 m | **3 m** | same |

The Arista DAC/AOC naming suffix `-<N>M` is the ordered length and is unambiguous; every other `-3M` part in the set correctly reads 3 m. These 3 are isolated typos. (Cisco QSFP-H40G-CU0-5M / SFP-H10GB-CU1-5M / CU2-5M were regex false positives — `CU0-5M`=0,5 m, `CU1-5M`=1,5 m, `CU2-5M`=2,5 m, all correct.)

## Finding 3 — Kabeltyp: 1 Cisco DAC with empty Kabeltyp
| Brand | PN | Kategorie 3 | Kabeltyp | Should be |
|---|---|---|---|---|
| Cisco | QSFP-2Q200-CU3M | DAC Kabel | **(empty)** | **Twinax-Kupfer, passiv, Breakout** |

It is the **only** part in the "DAC Kabel" category with an empty Kabeltyp (all 80+ siblings populated). Its name (2×QSFP breakout, CU = passive copper, 3M) and Transceiver-Typ ("Passives Direct-Attach-Kupferkabel (DAC)") fix the value. (Supermicro AOC-E10GSFPSR / AOC-TSR-FS were FPs — Supermicro's "AOC-" = **Add-On Card** product prefix, not Active Optical Cable; Cisco X2-10GB-CX4 / XENPAK-10GB-CX4 are X2/XENPAK **modules**, not the cable category → empty Kabeltyp is correct.)

---

## The 4 clean attributes (why their flags are not errors)
- **Transceiver Typ — clean.** 76 Juniper "mismatches" are an artifact of the crude PN-token regex colliding with Juniper's **`EX-`** product-line prefix (EX-SFP-…) and with descriptive German/standard type strings. The value distribution is entirely legitimate optical types (BiDi, 1000BASE-BX, DWDM, coherent, the BASE- standards, CWDM channels).
- **Reichweite — clean.** 0 name↔attribute reach mismatches across all brands.
- **Standard — clean.** 45 Standard-vs-Geschwindigkeit "speed mismatches" are all legitimate: breakout aggregates (Standard `4×10GBASE-LR` vs Geschwindigkeit `40 Gbit/s`; `2×400GBASE-FR4` vs `800 Gbit/s`), dual-rate coherent (`100G/200G`), and the `802.3z 1000BASE` regex reading "1000" against "1 Gbit/s". The data is correct (Standard = per-lane standard, Geschwindigkeit = aggregate).
- **Anwendung — clean.** Category distribution is sensible (Rechenzentrum ToR, Campus/Metro, Carrier/DWDM, Kupfer-Zugriff); breakout topology strings are consistent.

## Phase-2 staging (HELD — nothing applied)
Add to the Phase-2 delta: **Faseranzahl ×7** (+2 [VERIFY]), **Länge ×3**, **Kabeltyp ×1** = **~11 SKUs / 3 attributes**. Apply surgically or full-re-emit-with-regression-byte-diff only; every re-emitted bundle returns for operator byte-re-audit. The correctness audit is now complete across all 14 attributes.
