# Phase-1 DOM/Temp — Consolidated Delta (operator L8 review input)
_Compiled 2026-06-17. Report-only. Nothing re-authored. HOLD: provenance pass, Phase 2 (apply + Sortiernummer swap + prose re-author + re-emit), import, Palo Alto, Huawei._

## Review status
- **Operator-reviewed:** Cisco (7) + Juniper-DOM.
- **Autonomous sweep, PENDING this review (21):** Juniper-temp 2 · HPE 4 · Extreme 3 · Fortinet 7 · Dell 5.
- **Already APPLIED to bundles (15):** Fortinet 7 · Extreme 3 · Dell 5 (byte-minimal; Cisco/Juniper/HPE corrections recorded, NOT applied — await review + Phase 2).
- **All 13 brands audited.** 28 corrections; 7 brands = 0 value corrections.

## Section 1 — The 28 corrections
| Brand | PN | Attr | Old → New | Grounding (source / rule) | Applied |
|---|---|---|---|---|---|
| Cisco | GLC-LH-SM | DOM | Ja → **Nein** | Cisco GE-SFP DS **c78-366584**: non-D GLC has no DDM (only -MMD/-SMD) | no |
| Cisco | GLC-SX-MM | DOM | Ja → **Nein** | c78-366584 | no |
| Cisco | GLC-ZX-SM | DOM | Ja → **Nein** | c78-366584 | no |
| Cisco | SFP-GE-S | Betriebstemp | 0–70 → **-5…85 °C** | c78-366584: SFP-GE-* extended-temp (no -I suffix) | no |
| Cisco | SFP-GE-Z | Betriebstemp | 0–70 → **-5…85 °C** | c78-366584 | no |
| Cisco | SFP-1G-SX | Betriebstemp | 0–70 → **-5…85 °C** | c78-366584 | no |
| Cisco | SFP-1G-LH | Betriebstemp | 0–70 → **-5…85 °C** | c78-366584 | no |
| Juniper | EX-SFP-1GE-SX-ET | Betriebstemp | 0–70 → **extended → +85** (low bound [VERIFY]) | Juniper HCT: "1000Base-SX … Extended Temperature Range Optics" | no |
| Juniper | EX-SFP-1FE-FX-ET | Betriebstemp | 0–70 → **extended → +85** ([VERIFY]) | Juniper HCT: "100Base-FX … Extended Temp Range Optics" | no |
| HPE | J9142B | DOM | Ja → **Nein** | AOS-S/CX Transceiver Guide p.182 (BiDi): DDM = No (EOS Apr-2016) | no |
| HPE | J9143B | DOM | Ja → **Nein** | guide p.182 | no |
| HPE | JL745A | Betriebstemp | -40…85 → **0–70 °C** | guide p.164: "Commercial (0 to 70°C)" — TAA, not the I-Tmp twin | no |
| HPE | JL746A | Betriebstemp | -40…85 → **0–70 °C** | guide p.164 | no |
| Extreme | 10G-SR-SFP300M-ET | Betriebstemp | 0–70 → **0–85 °C** | Extreme High-Temp doc **GUID-E30872B1** (operator-confirmed 0-85) | **YES** |
| Extreme | 10G-LR-SFP10KM-ET | Betriebstemp | 0–70 → **OMITTED** ([VERIFY]) | -ET high-temp → +85; exact band not $0-verifiable + qualitative prose | **YES** |
| Extreme | 10G-ER-SFP40KM-ET | Betriebstemp | 0–70 → **OMITTED** ([VERIFY]) | ER/EW high-temp; exact band [VERIFY] + qualitative prose | **YES** |
| Fortinet | FN-TRAN-SFP+SR | Betriebstemp | -40…85 → **0–70 °C** | Fortinet Transceivers DS spec table p.5 (the -40…85 was the SRI twin) | **YES** |
| Fortinet | FN-TRAN-SFP+ER | Betriebstemp | -40…85 → **-5…70 °C** | DS spec p.5 | **YES** |
| Fortinet | FN-TRAN-SFP+LR | Betriebstemp | 0–70 → **0–85 °C** | DS spec p.5 (spec-table vs ordering blurb → default to spec) | **YES** |
| Fortinet | FN-TRAN-SFP2-SX | Betriebstemp | -40…70 → **-40…85 °C** | DS spec p.4 | **YES** |
| Fortinet | FN-TRAN-SFP2-LX | Betriebstemp | -40…70 → **-40…85 °C** | DS spec p.4 | **YES** |
| Fortinet | FN-TRAN-QSFP28-BIDI | Betriebstemp | 0–70 → **10–70 °C** | DS spec p.7 ("+10°C minimum") | **YES** |
| Fortinet | FG-TRAN-QSFP+SR-BIDI | DOM | Ja → **Nein** | DS BiDi table p.6: Digital Monitoring = No | **YES** |
| Dell | SFP-100M-FX | Betriebstemp | 0–70 → **0–85 °C** | Dell © 2026 Optics Spec Sheet, Notes "operates up to 85°C" | **YES** |
| Dell | SFP-1G-SX | Betriebstemp | 0–70 → **0–85 °C** | Dell © 2026 sheet, "operates up to 85°C" | **YES** |
| Dell | SFP-1G-LX | Betriebstemp | 0–70 → **0–85 °C** | Dell © 2026 sheet | **YES** |
| Dell | SFP-1G-T | Betriebstemp | 0–70 → **0–85 °C** | Dell © 2026 sheet | **YES** |
| Dell | QSFP-40G-BIDI | Betriebstemp | 0–70 → **10–70 °C** | Dell © 2026 sheet, "+10°C minimum operating temperature" | **YES** |

**Source URLs:** Cisco c78-366584 (cached); Juniper apps.juniper.net/hct; HPE AOS-S/AOS-CX Transceiver Guide (cached `hpe-aruba-transceivers.pdf`); Extreme documentation.extremenetworks.com/pluggable/GUID-E30872B1; Fortinet fortinet.com `Fortinet_Transceivers.pdf` (cached); Dell delltechnologies.com `Dell_EMC_Networking_Optics_Spec_Sheet.pdf` © 2026 (cached).

## Section 2 — [VERIFY] set (flag-don't-fabricate; resolve or omit before import)
| Group | Count | Detail |
|---|---|---|
| Cisco non-DWDM-XFP-C suspects | 26 | MGBSX1/LX1/LH1 (SMB, DDM unconfirmed); DWDM-SFP-* ×5; CWDM-SFP-* ×5; ONS-SI-GE-* ×4; S1G-*-PM-D-I ×2; GLC-LH/ZX-LMM-TI ×2; GLC-GE-DR-LX; DS-SFP-FCGE-LW/SW ×2 |
| Juniper RX- legacy | 3 | RX-10KM-SFP, RX-550M-SFP, RX-70KM-SFP — HCT page exists but JS-rendered; DOM=Ja kept (uncontradicted) |
| Juniper -ET exact band | 2 | EX-SFP-1GE-SX-ET, EX-SFP-1FE-FX-ET — extended → +85 confirmed; low bound (-5 vs 0) not $0-confirmable |
| Extreme -ET exact band | 2 | 10G-LR-SFP10KM-ET, 10G-ER-SFP40KM-ET — high-temp → +85; attribute OMITTED + qualitative prose pending exact band |
| Supermicro temp | 27 | Rule-9 [VERIFY] — eStore PDFs image-based (0/27 PN), store.supermicro.com 403; 0-70 commercial default, no suspects |
| Meraki temp | 25 | Rule-9 [VERIFY] — vendor genuinely omits operating temp (doc page + product pages confirmed); 0-70 commercial default |

_(NVIDIA temp was [VERIFY] → now GROUNDED 0-70 via networking-docs.nvidia.com; Dell's 127 newer parts → resolved to 0-70 by the © 2026 blanket statement. Both cleared.)_

## Section 3 — Sortiernummer (Phase-2 staged, NOT applied)
`constants.TRANSCEIVER_ATTRIBUTES` has **3 adjacent transpositions** vs the live-JTL 14-sequence: (Faseranzahl↔Fasertyp), (Kabeltyp↔Wellenlänge), (Anwendung↔Reichweite). One deterministic tuple-swap + re-emit fixes all 13 brands. **Held for the Phase-2 re-emit** (editing the tuple without re-emitting would split code↔data state).

## Section 4 — Provenance / writer fix (applied)
- **Standing policy (code-enforced, all brands):** optical DOM=Ja → "inference: SFF-8472 family-standard" (never a datasheet/page ground the source lacks). Confidence taxonomy = {datasheet, inference, physical, Rule-9-default}; every Source_URL must contain that attribute's value.
- **Provenance corrected (values byte-identical, surgical):** Ubiquiti (temp→ui.com / Rule-9; DOM→inference/physical; CWDM URLs→family page), Arista (DOM→inference; was already honest otherwise), Meraki (temp→Rule-9-default; DOM→inference/physical). 413 tests pass.
- **LESSON:** older-built brands need SURGICAL log edits for provenance (a full re-emit drifts values via code-drift); only recently-built Ubiquiti re-emitted cleanly.

## Section 5 — Deferred (operator decision)
- **Formfaktor-correctness pass** (after temp/DOM review): Arista C-* DACs Formfaktor=SFP → SFP-DD/SFP56 (21 parts; prose already says SFP-DD/SFP56) + check other brands' cable/module form factors.

## Section 6 — 0-correction brands (7) + grounding level
| Brand | Temp grounding | DOM |
|---|---|---|
| Lenovo | 3×85C = published "85 Degree C" variants (grounded); 101 standard = **Rule-9 default** (not datasheet) | copper Nein; optical Ja=inference |
| Ubiquiti | optical/AOC/Uplink/DAC = ui.com techspecs 0-70 (datasheet); 2 copper + 2 1G = Rule-9 | inference / physical |
| Arista | 104 modules = datasheet 0-70; 243 cables = Rule-9 (DS omits cable temp) | inference / physical |
| Meraki | **Rule-9 [VERIFY]** — vendor omits operating temp | inference / physical |
| MikroTik | per-part mikrotik.com (datasheet), varied; spot-check confirmed | inference / physical |
| NVIDIA | 0-70 grounded (networking-docs.nvidia.com; all-commercial, no -HT) | inference |
| Supermicro | **Rule-9 [VERIFY]** — eStore image-source + store 403 | inference / physical |
