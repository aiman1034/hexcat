# BATCH — HPE Comware + SMB Switch Lines · PHASE 1 ENUMERATION MANIFEST

**Status:** Phase 1 = ENUMERATION ONLY. Nothing authored. `output/` and `config/` untouched.
**Purpose:** establish the *measured* denominator (verbatim OEM part numbers + counts + sources) for the
FlexFabric (Comware DC), FlexNetwork (Comware campus/core) and SMB (Instant On + OfficeConnect) lines, plus
the E3-naming / schema-fit / scope decisions the operator must rule on **before** any Phase-2 authoring.
**Method:** 5 parallel research agents, restricted to OEM docs (HPE QuickSpecs / datasheets / EoS lifecycle
notices / ordering guides), Jina proxy + HPE-hosted PDF mirrors for Akamai-blocked hosts. Reseller listings
were **not** used for any count. Every measured PID is transcribed verbatim from an OEM ordering table.
**Grounding notes:** `_scratch/comware_smb_phase1_grounding.md` (agent-by-agent detail).
**Hersteller for the whole batch = `HP`** (per MISSION §0). **No new Merkmal NAME is invented anywhere** —
where the existing schema does not cover an axis, it is **FLAGGED for operator approval**, not created.

---

## 0. HEADLINE DENOMINATOR (measured, OEM-grounded)

| Line | Sub-lane | Families | Distinct products | Measured PIDs (incl. bundles/TAA/regional) | Pending courier |
|---|---|---|---|---|---|
| **FlexFabric** | Fixed (DC ToR/leaf/spine) | 10 | **33** | **~55** | 0 |
| **FlexFabric** | Modular chassis | 4 (12900E · 7900 · 12500 · 11900) | 18 chassis | **18 chassis** | 0 |
| **FlexFabric** | Module pools | 4 pools | — | **~69 modules** | 7900 ~2-4 · **12500 full pool** |
| **FlexNetwork** | Fixed (campus) | 7 | **37 core** | **44** | 0 |
| **FlexNetwork** | Modular chassis | 2 (7500 · 10500) | 15 chassis | **15 chassis** | 0 |
| **FlexNetwork** | Module pools | 2 pools | — | **~92 unique** (95 pre-dedup, +1 PoE-DIMM) | 10500-TAA descriptors* |
| **SMB** | Aruba Instant On (current) | 4 | **25** | 28 (w/ 3 B-revs) | 0 |
| **SMB** | HPE OfficeConnect (legacy/EOL) | 6 | **31** | 32 (w/ JG708B) | 0 |
| **TOTAL** | | **35 families** | | **≈ 350–360 measured PIDs** | 3 blocked pools (below) |

\* only if the TAA lane is built. Core FlexNetwork counts are complete.

**Two ways to read the denominator (operator's catalog policy decides):**
- **Distinct-product basis** (model the switch/module once; airflow/FlexNetwork/CTO bundles + TAA + regional +
  B-revs = *variants*) — matches how the audited switch gate already handles airflow/TAA. This is the
  **recommended** basis. FlexFabric-fixed 33, FlexNetwork-fixed 37, SMB 56, plus the chassis/module pools.
- **Orderable-PID basis** (every bundle/TAA/regional SKU = its own catalog line) — the higher ~350–360.

---

## 1. FLEXFABRIC — FIXED (Comware DC ToR/leaf/spine) · Agent A · 0 pending courier

All fit the validated **15-Merkmal fixed-switch** set. IRF stacking = a Wertliste **VALUE**. **No new Merkmal NAME.**
Modeling levers already in the toolbox: the "N-slot" fixed switches with 0 fixed ports (JH179A / JH398A /
JH404A / JQ075A / JQ076A) use the **word-form lever** (Portanzahl reads the populated module config, not the
chassis) — same pattern as the Nexus-2000 FEX lane.

| Family | Class | Distinct | Verbatim PID roster | Measured | E3 (proposed) | Source |
|---|---|---|---|---|---|---|
| 5700 | Fixed ToR | 3 | JG894A · JG896A · JG898A | 3 | HPE FlexFabric 5700 Switches | QuickSpec c04347352 |
| 5710 | Fixed ToR | 4 | JL585A · JL586A · JL587A · JL689A | 4 | HPE FlexFabric 5710 Switches | QuickSpec a00045647enw |
| 5900 (AF+CP) | Fixed ToR | 4 | JC772A · JG336A · JG510A · JG838A(5900CP) **+ 6 airflow bundles** JG846A–JG851A | 10 | HPE FlexFabric 5900 Switches | QuickSpec c04111469 |
| 5920 | Fixed ToR | 1 | JG296A **+ TAA** JG555A | 2 | HPE FlexFabric 5920 Switches | QuickSpec c04111528 |
| 5930 | Fixed ToR | 3 | JG726A · JH178A · JH179A **+ 4 airflow** JH378A–JH381A **+ 2 module bundles** JH382A/JH383A | 9 | HPE FlexFabric 5930 Switches | QuickSpec c04111326 + EOS |
| 5940 | Fixed ToR | 7 | JH390A · JH391A · JH394A · JH395A · JH396A · JH397A · JH398A **+ 5 FlexNetwork** JH684A/685A/686A/691A/692A **+ 4 CTO** JQ041A–JQ044A | 16 | HPE FlexFabric 5940 Switches | QuickSpec c05158726 + EOS |
| 5945 | Fixed ToR | 4 | JQ074A · JQ075A · JQ076A · JQ077A (+ 4 TAA S3K87A–S3K90A, dedupe) | 4 | HPE FlexFabric 5945 Switches | QuickSpec a00047323enw |
| 5950 | Fixed ToR | 3 | JH321A · JH402A · JH404A | 3 | HPE FlexFabric 5950 Switches | QuickSpec c05051989 + c05175675 |
| 5960 | Fixed ToR | 3 | S4J82A · R9Y12A · R9Y13A | 3 | HPE FlexFabric 5960 Switches | QuickSpec a50007000enw |
| 5980 | Fixed ToR | 1 | JQ026A | 1 | HPE FlexFabric 5980 Switches | QuickSpec a00029144enw |
| **TOTAL** | | **33** | | **~55** | | dual-source, 0 courier |

**Confirmed negatives (do NOT enumerate):** 5990, 5970, 5701, 5712 — none exist (independent searches → zero
OEM hits). 5900CP is JG838A **inside** 5900, not a separate family. 5944 is a separate sibling of 5945 (not
requested; not merged).
**Additions the prompt omitted:** 5920 (exists — added). **5965** (S3U42A, 64×400G) exists as a **separate
series** "HPE Networking Comware 5965" (QuickSpec a50009252enw) — **flagged, not banked**: verify the full
models table before shipping. Operator decides whether 5965 enters this batch.

**New Wertliste VALUES this lane needs (values, NOT names):** convergence-port / FCoE (JG838A 5900CP); 25G/SFP28
(5945, 5950); 200G/QSFP56 + 400G/QSFP-DD (5960).

---

## 2. FLEXFABRIC — MODULAR chassis + module pools · Agents B & D · 12900E+7900 courier + 12500 pool blocked

### 2.1 Chassis (validated Modular-Chassis schema: Switch-Typ=Modular-Chassis / Steckplätze / Bauform / Switching-Kapazität / Stromversorgung / Kühlung / Unterstützte Supervisor-Engines / Redundanz / Anwendung; temp→prose)

| Family | Distinct | Verbatim chassis PID roster | Count | E3 (proposed) | Source |
|---|---|---|---|---|---|
| 12900E (+ legacy 12910) | 6 | JH951A=12901E · JH345A=12902E · JH262A=12904E · JH255A=12908E · JH103A=12916E **+ legacy** JG619A=12910-AC · JG632A=12910-TAA | 7 | HPE FlexFabric 12900E Switches | QuickSpec c04111378 (V43, 27-Feb-2026 + legacy PDF) |
| 7900 | 2 | JG682A=7904 · JG841A=7910 **+ TAA** JH122A · JH123A | 4 | HPE FlexFabric 7900 Switches | datasheet 4AA5-2359ENN (QS c04293387 **retired**) |
| 12500 | 3–6 | JC654A=12504-AC · JC655A=12504-DC · JF431C=12508-AC · JC652A=12508-DC · JF430C=12518-AC · JC653A=12518-DC | 6 | HPE FlexFabric 12500 Switches | QuickSpec c04111591 (chassis via HPE product pages) |
| 11900 | 1 | JG608A=11908-V *(only the -V ships; no bare 11908; JG608AR=refurb excluded)* | 1 | HPE FlexFabric 11900 Switches | Option-Parts c03801956 |
| **TOTAL** | | | **18 chassis** | | |

### 2.2 Module pools (Class-B module lane: Modultyp + Kompatible Serie; port Merkmale reused where applicable; PLURAL E3)

| Pool | Measured | Composition | E3 (proposed) | Source |
|---|---|---|---|---|
| 12900E Modules | **55** | 8 MPU + 13 Fabric + 34 Linecard/adapter (current HB/HF/X/H2 + legacy 12900 EA/EB/EC/FX) | HPE FlexFabric 12900E Modules | QuickSpec c04111378 |
| 7900 Modules | **5** meas. **+ ~2-4 courier** | JG842A/JH001A (combined Fabric+MPU) + linecards JG683B/JG845A/JH002A; **7904 MPU PID + post-2016 cards pending** | HPE FlexFabric 7900 Modules | datasheet 4AA5-2359ENN |
| 11900 Modules | **~9** | JG609A · JG610A · JG611A–JG615A · JG918A | HPE FlexFabric 11900 Modules | Option-Parts c03801956 |
| 12500 Modules | **PENDING COURIER** | chassis + sample MPU/LPU (JC072B / JC064B / JC065B) only; full LEB/LEC/REB line-card denominator blocked | HPE FlexFabric 12500 Modules | QuickSpec c04111591 (**Akamai-blocked**) |

**Verify-before-encode:** 12900E descriptor↔PID bindings **JH252A / JH257A / JH422A** were reconstructed from a
2-column PDF and are the ones most exposed to column-offset error — re-verify on a clean HPE source.

### 2.3 🚨 NEW-MERKMAL-NAME FLAGS — the load-bearing Phase-2 decision (operator must rule; nothing invented)

The Comware **modular** chassis expose **two axes the validated CX/zl (ProVision/ArubaOS-CX) chassis schema
does not model as first-class**. Per the directive I flag and stop — I do **not** invent:

1. **Fabric-slot count distinct from I/O-slot count.** 12904E/12908E/12916E have 6 *dedicated* fabric slots;
   12901E/12902E have *integrated* fabric (no fabric slot); 10500 has 4 fabric + 2 MPU slots separate from I/O.
   The current `Steckplätze` Merkmal models a single slot count. → **Candidate new Merkmal `Fabric-Steckplätze`**,
   OR fold into `Steckplätze` with a role qualifier (verbatim string e.g. "16 I/O + 2 MPU + 6 Fabric").
2. **Module generation / type interop gating.** MPU/fabric/linecards interoperate only within one generation
   (12900E: Type F / H / H2 / X / HB / HF; legacy 12900: EA / EB / EC / FX). This compatibility axis has no
   home in the current schema. → **Candidate new Merkmal `Modul-Generation`** on both chassis and modules.

**These two are the only genuine new-NAME candidates in the entire batch.** Everything else is a VALUE:

**New Modultyp VALUES (values, not names — device-class-modeling rule = new values are allowed, flagged here for
confirmation):** `MPU / Route-Processor` (supervisor-as-a-module — CX/zl integrate the supervisor, so no such
value exists); `Fabric/MPU (kombiniert)` (7900 + 7500 carry both roles in one PID); `Service-Modul` (VPN-Firewall
/ NetStream / Load-Balancing / Wired-WLAN cards); `Trägermodul / Sub-slot` (12900E JH953A/JH954A host 5930/5950
sub-modules; JH107A LPU-adapter).

**Excluded as bare accessories (noted, not banked):** transceivers, DAC/AOC cables, PSUs (e.g. JG840A), fan
trays (JG684A/JG839A/JG843A/JH448A/JH423A/JH424A), rack/mount kits. The 5930/5950 "59xx" sub-modules
(JH180A–JH184A / JH405A/JH406A/JH450A/JH957A) that plug the JH953A/JH954A carriers are their **own switch
families**, noted but not counted here.

---

## 3. FLEXNETWORK — FIXED (Comware campus) · Agent C · 0 pending courier

All fit the 15-Merkmal fixed-switch set. IRF = VALUE; TAA / dual-PSU / expansion-slot / combo-port / mGig = VALUES.
**No new Merkmal NAME.**

| Family | Distinct | Verbatim PID roster | Measured | E3 (proposed) | Source |
|---|---|---|---|---|---|
| 5120 v3 | 1 | S0F79A *(new/thin line, roster expanding)* | 1 | HPE FlexNetwork 5120 v3 Switches † | QuickSpec a50007006enw |
| 5130 EI | 9 | JG932A · JG933A · JG934A · JG936A · JG937A · JG938A · JG939A · JG940A · JG941A **+ 4 Brazil** JG975A–JG978A | 13 | HPE FlexNetwork 5130 EI Switches | QuickSpec c04394228 |
| 5130 HI | 4 | JH323A · JH324A · JH325A · JH326A | 4 | HPE FlexNetwork 5130 HI Switches | QuickSpec c04843026 |
| 5140 EI | 9 | JL823A–JL829A + R8J41A · R8J42A | 9 | HPE FlexNetwork 5140 EI Switches | QuickSpec a50002579enw |
| 5140 HI | 4 | R9L61A · R9L62A · R9L63A · R9L64A | 4 | HPE FlexNetwork 5140 HI Switches | HPE Store 1014653205 (QS a50006098enw 404) |
| 5510 HI | 5 | JH145A · JH146A · JH147A · JH148A · JH149A | 5 | HPE FlexNetwork 5510 HI Switches | QuickSpec c04843027 |
| 5520 HI | 5 | R8M25A · R8M26A · R8M27A · R8M28A · R8M29A **+ 3 TAA** S3K91A/S3K92A/S3K93A | 8 | HPE FlexNetwork 5520 HI Switches | QuickSpec a50002587enw |
| **TOTAL** | | **37 core** | | **44** | | 0 courier |

† **Branding flag:** HPE now labels 5120 v3 "**Networking Comware**", not FlexNetwork — operator picks the E3 label.
**mGig flag:** a 2.5/5 GbE "XGT" multi-gig **Port-Geschwindigkeit VALUE** must exist (5140 EI, 5520 HI).
**Excluded (EOL/wrong-line):** 5120 SI / 5120 EI-orig, 5500 / 5500-HI/EI (pre-FlexNetwork), 5560 / 5580 (don't
exist), 5710 / 5930 / 5940 / 5960 (= FlexFabric DC).

---

## 4. FLEXNETWORK — MODULAR chassis + module pools · Agent D · 10500-TAA descriptors only if TAA lane built

🚨 **Disambiguation (load-bearing):** only **7500 + 10500** are genuinely FlexNetwork-branded. 11900 / 12500 /
12900E are **FlexFabric** (§2). There is no FlexNetwork-branded 12900.

### 4.1 Chassis (validated Modular-Chassis schema)

| Family | Distinct | Verbatim chassis PID roster | Count | E3 (proposed) | Source |
|---|---|---|---|---|---|
| 7500 | 4 | JD242C=7502 · JD240C=7503 · JD239C=7506 · JD238C=7510 **+ 3 Fabric+MPU bundles** JH331A/JH332A/JH333A | 7 | HPE FlexNetwork 7500 Switches | QuickSpec c04111585 |
| 10500 | 4 | JC613A=10504 · JC612A=10508 · JC611A=10508-V · JC748A=10512 **+ 4 TAA** JG820A–JG823A | 8 | HPE FlexNetwork 10500 Switches | QuickSpec c04212581 + c03050623 |
| **TOTAL** | | | **15 chassis** | | |

### 4.2 Module pools (Class-B module lane; PLURAL E3)

| Pool | Measured | Composition | E3 (proposed) | Source |
|---|---|---|---|---|
| 7500 Modules | **50** (+1 PoE-DIMM JD192B = 51) | 7 MPU/Fabric-MPU + 5 fabric + 33 LPU + 5 service | HPE FlexNetwork 7500 Modules | QuickSpec c04111585 |
| 10500 Modules | **45** | 5 MPU + 7 fabric + 30 LPU + 3 service | HPE FlexNetwork 10500 Modules | QuickSpec c04212581 |

**Cross-family dedupe:** JG372A (VPN-Firewall), JG639A (Wired-WLAN), JD254A (NetStream) are cross-listed in both
pools → **1 canonical PID each**. Module total: 95 distinct → **92 unique** post-dedup (96 with the PoE-DIMM).
**Combined FlexNetwork chassis + modules ≈ 107 unique PIDs.**

**Schema:** rides the validated module lane. **No new Merkmal NAME.** New Modultyp VALUES (same set as §2.3):
`Fabric/MPU (kombiniert)` (7500 JH207A/JH208A/JH209A/JC666A/JC699A–JC701A); `Service-Modul`. 10500 MPUs = existing
`Management-Modul` value, 10500 fabric = existing `Fabric-Module` value → no new type needed for 10500.

---

## 5. SMB — Aruba Instant On + HPE OfficeConnect · Agent E · 0 pending courier

All 10 families fit the 15-Merkmal fixed-switch set. **No new Merkmal NAME.** The only modeling work is the
**Unmanaged cascade** (1430 + 1420 + 1405: Switch-Typ=Unmanaged ⇒ suppress L3/stacking/VLAN/mgmt Merkmale) — the
same empty-attribute-propagation path as the FEX non-counted-ports lane.

**Scope corrections (resolve prompt assumptions):** there is **no Aruba Instant On 1420** (the 1420 is
OfficeConnect only, replaced by Instant On 1430) and **no Instant On 1410/1410G**. Instant On unmanaged = **1430 only**.

### 5.1 Aruba Instant On — current, cloud-managed

| Family | Class | Distinct | Verbatim PID roster | E3 (proposed) | Source |
|---|---|---|---|---|---|
| 1960 | managed L2+ stackable | 5 | JL805A · JL806A · JL807A · JL808A · JL809A | Aruba Instant On 1960 Switches | DS a00118137enw |
| 1930 | managed L2+ | 7 (+3 B-rev) | JL680A–JL686A **+ B-revs** JL683B/JL684B/JL686B | Aruba Instant On 1930 Switches | DS a00098249enw |
| 1830 | smart-mgd L2 | 6 | JL810A · JL811A · JL812A · JL813A · JL814A · JL815A | Aruba Instant On 1830 Switches | DS a00119988enw |
| 1430 | **Unmanaged** | 7 | R8R44A · R8R45A · R8R46A · R8R47A · R8R48A · R8R49A · R8R50A | Aruba Instant On 1430 Switches | DS a00123902enw |
| **subtotal** | | **25** (28 w/ B-revs) | | | |

### 5.2 HPE OfficeConnect — legacy, **ALL EOL**

| Family | Class | Distinct | Verbatim PID roster | E3 (proposed) | Source |
|---|---|---|---|---|---|
| 1405 + 1420 | **Unmanaged** | 10 | JH407A/JH408A=1405v3 · JH327A/JH329A/JH328A/JH330A/JH016A/JH017A/JH018A/JH019A=1420 (+JG708B=11) | HPE OfficeConnect 1420 Switches (+1405) | EoS notice + QS c04609036 |
| 1620 | smart-mgd L2, copper-only | 3 | JG912A · JG913A · JG914A | HPE OfficeConnect 1620 Switches | DS 4AA5-5571ENW |
| 1820 | smart-mgd L2 | 6 | J9979A · J9982A · J9980A · J9983A · J9981A · J9984A | HPE OfficeConnect 1820 Switches | DS 4AA5-6352ENW |
| 1920S | smart-mgd L2+ static-L3 | 7 | JL380A · JL381A · JL382A · JL383A · JL384A · JL385A · JL386A | HPE OfficeConnect 1920S Switches | QS (HPE Support) |
| 1950 | smart web-mgd 10G | 5 | JG960A · JG961A · JG962A · JG963A · JH295A | HPE OfficeConnect 1950 Switches | QS c04545486 |
| **subtotal** | | **31** (32 w/ JG708B) | | | |

**SMB total: 56 base (25 Instant On + 31 OfficeConnect), ~60 with carried revs. 0 pending courier.**

### 🚩 SMB POSITIONING FLAG (operator scope decision)

These are genuinely **low-end SMB** and do **not** fit the "neu-versiegelt" (new-sealed *enterprise*) range the
audited gate was built for: (1) **Limited-Lifetime warranty**, not Foundation Care / enterprise support SKUs;
(2) **all OfficeConnect is EOL** (1405/1420 EoS Feb-2023; 1620 EoS 2019; 1820/1920S/1950 discontinued) — a
complete *historical* denominator, but not orderable-new; (3) **Instant On is cloud-portal/app-managed** (no
on-box enterprise CLI). **Recommendation:** shelve as two sub-ranges — Instant On (current, 25 orderable) vs
OfficeConnect (legacy/EOL, 31 reference-only). If only current product is wanted, the SMB denominator is **25**.

---

## 6. BLOCKED-DOC LIST — pending courier (Akamai/retired; could not ground from a live OEM ordering table)

| # | Item | Doc | What's blocked | Impact |
|---|---|---|---|---|
| 1 | FlexFabric **7900** module pool (current roster) | QuickSpec **c04293387** (RETIRED — obsolete-notice page only; psnow + h20195 Akamai-blocked) | 7904 MPU ordering PID + any post-2016 line cards (~2-4 PIDs) | small; chassis + 2016 module set already grounded from datasheet 4AA5-2359ENN |
| 2 | FlexFabric **12500** full module pool | QuickSpec **c04111591.pdf** (curl hung on Akamai; Jina → retired landing page) | full LEB/LEC/REB line-card denominator (~15-30 PIDs) | **largest gap**; 6 chassis + sample modules (JC072B/JC064B/JC065B) grounded |
| 3 | **10500 TAA** QuickSpecs | referenced via config-note in c04212581 only | JG820A–JG823A / JG375A full descriptors | only matters if the TAA lane is built; TAA chassis PIDs already confirmed |
| 4 | FlexFabric **5965** (S3U42A) | QuickSpec **a50009252enw** | full models table not read end-to-end | SKU existence confirmed via HPE Store; verify before shipping if 5965 is banked |
| 5 | 12900E descriptor↔PID re-verify | c04111378 (2-column PDF) | **JH252A / JH257A / JH422A** binding confidence | re-verify on a clean source before encoding |

**URLs tried (for #1/#2):** `hpe.com/psnow/doc/<id>`, `hpe.com/psnow/downloadDoc/…<id>.pdf`,
`h20195.www2.hpe.com/v2/getdocument.aspx?docname=<id>` — all blocked/timeout/notice-only. Recovery for every
*counted* family was via HPE-hosted PDF mirrors, HPE Support docDisplay, downloadDoc, or the EoS lifecycle docs.

---

## 7. SCHEMA VERDICT — one place, for the whole batch

| Axis | Verdict |
|---|---|
| Fixed switches (FlexFabric-fixed, FlexNetwork-fixed, all SMB) | ✅ existing 15-Merkmal set covers all. No new NAME. |
| Modular chassis (12900E/7900/12500/11900/7500/10500) | ⚠️ existing Modular-Chassis schema covers *most*, but see the **two new-NAME candidates** below. |
| Module pools (all 6) | ✅ existing Class-B module lane covers structure. Needs **new Modultyp VALUES** only (no new NAME). |
| IRF stacking | VALUE (Stacking Merkmal), not a NAME. |
| **NEW MERKMAL NAME — needs operator ruling** | (a) **`Fabric-Steckplätze`** (or fold into Steckplätze w/ role qualifier); (b) **`Modul-Generation`** (F/H/H2/X interop gating). These are the ONLY two new-NAME candidates in the batch. |
| New Wertliste VALUES (allowed per device-class-modeling rule; listed for confirmation) | Port/connector: CP-FCoE, 25G/SFP28, 200G/QSFP56, 400G/QSFP-DD, mGig 2.5/5G. Modultyp: MPU/Route-Processor, Fabric/MPU-kombiniert, Service-Modul, Trägermodul/Sub-slot. Unmanaged (SMB); 5-port count; "PoE+"↔"Class 4" normalization. |

---

## 8. OPEN DECISIONS FOR THE OPERATOR (before Phase 2)

1. **New Merkmal NAMES** (§7) — approve `Fabric-Steckplätze` + `Modul-Generation`, OR choose the fold-into-
   `Steckplätze` / verbatim-string alternative. **This gates all modular-chassis authoring.**
2. **New Modultyp + port VALUES** (§7) — confirm the Wertliste additions (values, not names).
3. **Scope: additions the prompt omitted** — include **5920**? include **5965** (separate series, verify
   a50009252enw first)? Both exist and are grounded/flagged.
4. **Scope: SMB** — include OfficeConnect (all EOL) as a legacy sub-range, or ship **Instant On only** (25)? Do
   these low-end/limited-warranty lines belong in the "neu-versiegelt" enterprise range at all? (§5 flag.)
5. **Legacy-within-family** — carry legacy 12910 under the 12900E E3, or split? Carry legacy 12900 (EA/EB/EC/FX)
   linecards in the 12900E module pool, or split a legacy pool?
6. **Variants basis** — model distinct product + variants (recommended, **33/37/56** basis), or one line per
   orderable PID (~350–360)? Applies to airflow/FlexNetwork/CTO bundles, TAA, regional (Brazil), B-revs.
7. **Branding** — 5120 v3 + 5710 + 5960 now carry "**HPE Networking Comware**" labels; keep "FlexFabric/
   FlexNetwork <n> Switches" E3s, or adopt the current "Networking Comware" branding?
8. **Courier the 3 blocked pools** (§6 #1/#2/#3) before authoring those families, or author the grounded
   families first and backfill the blocked module pools after courier?

---

## 9. NEXT (paused for operator review — no authoring until approved)

Phase 2 = author these families onto the switch gate. **Do not start** until decisions §8.1–§8.2 (the new-NAME +
new-VALUE rulings) are made, since they change the schema every modular family is authored against. Suggested
Phase-2 order once approved: FlexNetwork-fixed (37, cleanest, 0 courier) → FlexFabric-fixed (33) → SMB Instant On
(25) → modular chassis + module pools (after the schema ruling + courier on the 3 blocked pools).
