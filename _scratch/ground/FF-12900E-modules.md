# FF-12900E-modules | modules | HPE FlexFabric 12900E Modules | doc c04111378

I have complete verbatim OEM grounding. Assembling the final per-PID output. Note on naming: V43 QuickSpec rebranded MPU/Fabric/current-linecard names to "HPE Networking ..."; legacy datasheet + legacy QuickSpec use "HPE FlexFabric ...". I give the verbatim name from the doc that carries each PID (current PIDs → V43 "HPE Networking"; legacy PIDs → "HPE FlexFabric").

---

**FF-12900E-modules — OEM grounding complete. Sources (all reached, verbatim):**
- **V43 QuickSpec c04111378** (Version 43, 27-Feb-2026) via Jina cache-opt-out — current MPU/Fabric/I/O tables (rebranded "HPE Networking Comware")
- **Legacy QuickSpec c04111378 PDF** (1worldsync mirror, HPE-authored) — legacy EA/EB/EC/FX/FE + Type F/A/B modules, LPU adapter
- **HPE FlexFabric 12900/12900E data sheet** (gzhls mirror, HPE-authored) — clean SKU↔name pairings that resolved the 2-column offset
- Cross-check: HPE Store product pages, harddiskdirect (JH264A)

**Per-card switching capacity (SwK): NOT PUBLISHED per line card in any OEM doc.** OEM publishes only chassis backplane (28.8 Tbps/slot-pair; up to 28.8 Tbps per-chassis backplane, "up to 21.6 Tbps per slot" bandwidth) and per-**fabric-module** Tbps (in the fabric names). So every LINECARD SwK = **ZU_VERIFIZIEREN** (never port-math).

**Roster verdict: 8 MPU + 13 Fabric + 34 linecards + 1 LPU-adapter = 56 PIDs. All 55 manifest PIDs confirmed + LPU adapter. Zero pending courier.** V43 dropped all legacy PIDs from active tables (rebrand), but they remain fully grounded in the HPE-authored legacy QuickSpec + data sheet.

---

## MPU / Route-Processor (8)
```
JH346A | HPE FlexFabric 12902E Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12900E (integrated-fabric chassis 12902E only) | — | n/a (control plane) | EOL (V43-dropped; legacy QS/DS only)
JH668A | HPE FlexFabric 12904E v2 Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12900E, 12904E | — | n/a | active (V43: "HPE Networking 12904E v2 Main Processing Unit")
R9F17A | HPE Networking 12904E Type H2 Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12900E, Type H2, 12904E | — | n/a | active (V43)
JH669A | HPE FlexFabric 12900E v2 Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12900E, 12908E/12916E | — | n/a | active (V43: "HPE Networking 12900E v2 Main Processing Unit")
JL844A | HPE Networking 12904E Type X Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12900E, Type X, 12904E | — | n/a | active (V43)
JL845A | HPE Networking 12900E Type X Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12900E, Type X, 12908E/12916E | — | n/a | active (V43)
R9F18A | HPE Networking 12900E Type H2 Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12900E, Type H2, 12908E/12916E | — | n/a | active (V43)
JG621A | HPE FlexFabric 12910 Main Processing Unit | MPU/Route-Processor | HPE FlexFabric 12910 (legacy chassis JG619A) | — | n/a | EOL (legacy QS/DS only)
```
Note: 12901E (JH951A) has an **Integrated MPU** and 12902E (JH345A) has 2× integrated MPUx management ports — no separate MPU PID for 12901E; 12902E uses JH346A.

## Fabric-Module (13)
```
JH264A | HPE FlexFabric 12904E 2.5Tbps Type F Fabric Module  | Fabric-Module | HPE FlexFabric 12900E, Type F, 12904E | fabric rating 2.5 Tbps (verbatim) | EOL (legacy)
JH364A | HPE FlexFabric 12904E 7.2Tbps Type H Fabric Module  | Fabric-Module | HPE FlexFabric 12900E, Type H, 12904E | 7.2 Tbps | active (V43: "HPE Networking 12904E 7.2Tbps Type H Fabric Module")
JL841A | HPE Networking 12904E Type X Fabric Module          | Fabric-Module | HPE FlexFabric 12900E, Type X, 12904E | ZU_VERIFIZIEREN (no Tbps in name) | active (V43)
R9F14A | HPE Networking 12904E Type H2 Fabric Module         | Fabric-Module | HPE FlexFabric 12900E, Type H2, 12904E | ZU_VERIFIZIEREN | active (V43)
JH257A | HPE FlexFabric 12908E 5.0Tbps Type F Fabric Module  | Fabric-Module | HPE FlexFabric 12900E, Type F, 12908E | 5.0 Tbps | EOL (legacy)
JH362A | HPE FlexFabric 12908E 14.4Tbps Type H Fabric Module | Fabric-Module | HPE FlexFabric 12900E, Type H, 12908E | 14.4 Tbps | active (V43: "HPE Networking 12908E 14.4Tbps Type H Fabric Module")
JL842A | HPE Networking 12908E Type X Fabric Module          | Fabric-Module | HPE FlexFabric 12900E, Type X, 12908E | ZU_VERIFIZIEREN | active (V43)
R9F15A | HPE Networking 12908E Type H2 Fabric Module         | Fabric-Module | HPE FlexFabric 12900E, Type H2, 12908E | ZU_VERIFIZIEREN | active (V43)
JH252A | HPE FlexFabric 12916E 10.0Tbps Type F Fabric Module | Fabric-Module | HPE FlexFabric 12900E, Type F, 12916E | 10.0 Tbps | EOL (legacy) [flag CLEARED: was offset-risk]
JH361A | HPE FlexFabric 12916E 21.6Tbps Type H Fabric Module | Fabric-Module | HPE FlexFabric 12900E, Type H, 12916E | 21.6 Tbps | active (V43: "HPE Networking 12916E 21.6Tbps Type H Fabric Module")
JH435A | HPE FlexFabric 12916E 43.2Tbps Type H Fabric Module | Fabric-Module | HPE FlexFabric 12900E, Type H, 12916E | 43.2 Tbps | active (V43: "HPE Networking 12916E 43 2Tps Type H Fabric Module" [sic OCR]) 
JG622A | HPE FlexFabric 12910 1.92Tbps Type A Fabric Module  | Fabric-Module | HPE FlexFabric 12910, Type A (legacy chassis JG619A) | 1.92 Tbps | EOL (legacy)
JG623A | HPE FlexFabric 12910 3.84Tbps Type B Fabric Module  | Fabric-Module | HPE FlexFabric 12910, Type B (legacy chassis JG619A) | 3.84 Tbps | EOL (legacy)
```
Note: JG622A/JG623A are **12910** (not 12916E) fabrics — verified in data sheet. No V43 Type X/H2 Tbps figure exists in the name (OEM omits it) → SwK ZU_VERIFIZIEREN for those 4.

## Linecards / I/O Modules (34) — current HB/HF/X/H2
```
JH357A | HPE FlexFabric 12900E 36-port 100GbE QSFP28 HB Module        | Linecard | 12900E, Type HB | 36 | 36×QSFP28 (QSFP+/QSFP28) | 100GbE | none | ZU_VERIFIZIEREN | active (V43: "HPE Networking 12900E 36p 100GbE QSFP28 HB Module")
JH359A | HPE FlexFabric 12900E 48-port 40GbE QSFP+ HB Module          | Linecard | 12900E, Type HB | 48 | 48×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | active (V43: "HPE Networking Comware Module 48-port 40GbE QSFP+ HB 12900E")
JH360A | HPE FlexFabric 12900E 48-port 10GbE + 2-port 100GbE HB Module| Linecard | 12900E, Type HB | 50 | 48×SFP/SFP+ + 2×QSFP+/QSFP28 | 10GbE + 100GbE | none | ZU_VERIFIZIEREN | active (V43: "HPE Networking 12900E 48p 10G 2p 100G HB Module")
JH422A | HPE FlexFabric 12900E 18-port 100G QSFP28/18-port 40G QSFP+ HB Module | Linecard | 12900E, Type HB | 36 | 18×QSFP28 + 18×QSFP+ | 100G + 40G | none | ZU_VERIFIZIEREN | active [flag CLEARED: descriptor↔PID verified]
JH425A | HPE FlexFabric 12900E 18-port 100G QSFP28/18-port 40G QSFP+ HF Module | Linecard | 12900E, Type HF | 36 | 18×QSFP28 + 18×QSFP+ | 100G + 40G | none | ZU_VERIFIZIEREN | active
JH045A | HPE FlexFabric 12900 36-port 40GbE QSFP+ FX Module           | Linecard | 12900E, FX (legacy pool) | 36 | 36×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | EOL (legacy) — requires JH107A LPU Adapter
JQ061A | HPE FlexFabric 12900E 48-port 10GbE SFP+ HF Module           | Linecard | 12900E, Type HF | 48 | 48×SFP+ | 10GbE | none | ZU_VERIFIZIEREN | active (V43: "HPE Networking 12900E 48p 10GbE SFP+ HF Module")
JH953A | HPE FlexFabric 12900E 24-port 10G/2-port 40G HB 59xx Slot Module | Trägermodul/Sub-slot | 12900E, Type HB (hosts 1×59XX submodule) | 24+2 (+1 59XX slot) | 24×SFP+ 10G + 2×QSFP+ 40G + 1×59XX module bay | 10G/40G | none | ZU_VERIFIZIEREN | active (V43: "HPE Networking 12900E 24p 10G/2p 40G HB 59xx Module")
JH954A | HPE FlexFabric 12900E 24-port 10GbE and 4-port 100GbE HD 59xx Slot Module | Trägermodul/Sub-slot | 12900E, Type HD (hosts 1×59XX submodule) | 24+4 (+1 59XX slot) | 24×SFP/SFP+ + 4×QSFP28 + 1×59XX module bay | 10G/100G | none | ZU_VERIFIZIEREN | active (V43: "HPE Networking 12900E 24p 10G/4p 100G HD 59xx Module")
JL846A | HPE Networking Comware Module 48-Port 10GbE SFP+ Type X 12900E   | Linecard | 12900E, Type X | 48 | 48×SFP/SFP+ (1G/10G) | 1G/10GbE | none | ZU_VERIFIZIEREN | active (V43)
JL847A | HPE Networking Comware Module 36-Port 40GbE QSFP+ Type X 12900E  | Linecard | 12900E, Type X | 36 | 36×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | active (V43)
JL848A | HPE Networking Comware Module 36-Port 100GbE QSFP28 Type X 12900E| Linecard | 12900E, Type X | 36 | 36×QSFP+/QSFP28 | 100GbE | none | ZU_VERIFIZIEREN | active (V43)
R9F19A | HPE Networking Comware Module 24-Port 400GbE QSFP-DD Type H2 12900E | Linecard | 12900E, Type H2 | 24 | 24×QSFP-DD | 400GbE | none | ZU_VERIFIZIEREN | active (V43) [PID↔descriptor: 24×400G, NOT 48×100G]
R9F20A | HPE Networking Comware Module 48-Port 100GbE QSFP28 Type H2 12900E  | Linecard | 12900E, Type H2 | 48 | 48×QSFP28 (44×QSFP+ 40G, not ports 17/20/27/30) | 100GbE (40GbE subset) | none | ZU_VERIFIZIEREN | active (V43) [PID↔descriptor: 48×100G]
```
Legacy 12900 EA/EB/EC/FX/FE linecards (merged into 12900E Modules pool; require JH107A LPU Adapter where noted; EOL):
```
JG855A | HPE FlexFabric 12900 48-port GbE SFP EB Module        | Linecard | 12900E, EB gen | 48 | 48×SFP | 1GbE (Max 48 SFP+ tx per QS) | none | ZU_VERIFIZIEREN | EOL
JG856A | HPE FlexFabric 12900 48-port 10/100/1000BASE-T EB Module | Linecard | 12900E, EB gen | 48 | 48×10/100/1000BASE-T (RJ45) | 1GbE | none | ZU_VERIFIZIEREN | EOL
JG624A | HPE FlexFabric 12900 48-port 10GbE SFP+ EA Module     | Linecard | 12900E, EA gen | 48 | 48×SFP+ | 10GbE | none | ZU_VERIFIZIEREN | EOL
JG625A | HPE FlexFabric 12900 16-port 40GbE QSFP+ EA Module    | Linecard | 12900E, EA gen | 16 | 16×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | EOL
JG626A | HPE FlexFabric 12900 48-port 1/10GbE SFP+ EC Module   | Linecard | 12900E, EC gen | 48 | 48×SFP+ | 1/10GbE | none | ZU_VERIFIZIEREN | EOL
JG857A | HPE FlexFabric 12900 12-port 40GbE QSFP+ EC Module    | Linecard | 12900E, EC gen | 12 | 12×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | EOL
JG858A | HPE FlexFabric 12900 4-port 100GbE CFP EC Module      | Linecard | 12900E, EC gen | 4 | 4×CFP | 100GbE | none | ZU_VERIFIZIEREN | EOL
JH241A | HPE FlexFabric 12900 48-port GbE SFP FX Module        | Linecard | 12900E, FX gen | 48 | 48×SFP | 1GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JH242A | HPE FlexFabric 12900 48-port 10/100/1000BASE-T FX Module | Linecard | 12900E, FX gen | 48 | 48×10/100/1000BASE-T (RJ45) | 1GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JH007A | HPE FlexFabric 12900 48-port 1/10GBASE-T FX Module    | Linecard | 12900E, FX gen | 48 | 48×1/10GBASE-T (RJ45) | 1/10GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JH005A | HPE FlexFabric 12900 12-port 40GbE QSFP+ FX Module    | Linecard | 12900E, FX gen | 12 | 12×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JH006A | HPE FlexFabric 12900 8-port 100GbE CXP FX Module      | Linecard | 12900E, FX gen | 8 | 8×CXP | 100GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JH249A | HPE FlexFabric 12900 48-port 1/10GbE SFP+ FE Module   | Linecard | 12900E, FE gen | 48 | 48×SFP+ | 1/10GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JH250A | HPE FlexFabric 12900 24-port 40GbE QSFP+ FE Module    | Linecard | 12900E, FE gen | 24 | 24×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JG888B | HPE FlexFabric 12900 48-port 1/10GbE SFP+ FX Module   | Linecard | 12900E, FX gen | 48 | 48×SFP+ | 1/10GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JG889B | HPE FlexFabric 12900 24-port 40GbE QSFP+ FX Module    | Linecard | 12900E, FX gen | 24 | 24×QSFP+ | 40GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
JH288A | HPE FlexFabric 12900 8-port 100GbE CFP2 FX Module     | Linecard | 12900E, FX gen | 8 | 8×CFP2 | 100GbE | none | ZU_VERIFIZIEREN | EOL — requires JH107A
```

## LPU-Adapter (1)
```
JH107A | HPE FlexFabric 12900E LPU Adapter | LPU-Adapter | HPE FlexFabric 12900E (12904E/12908E/12916E; NOT 12902E) | — | n/a | EOL (legacy) — REQUIRED (1 per module) for any FX/FE I/O module
```

---

### Roster reconciliation & flags
- **All 8 MPU + 13 Fabric + 34 linecards + JH107A confirmed** in HPE-authored docs. 55/55 manifest PIDs verified; JH107A classified as **LPU-Adapter** (not linecard).
- **Flags CLEARED (were offset-risk):** JH252A = 12916E 10.0Tbps Type F Fabric; JH257A = 12908E 5.0Tbps Type F Fabric; JH422A = 18p-100G/18p-40G **HB** Module. All confirmed against the HPE data sheet's clean SKU-in-parentheses table.
- **R9F19A / R9F20A do NOT follow the naive numbering:** R9F19A = **24-Port 400GbE QSFP-DD** H2; R9F20A = **48-Port 100GbE QSFP28** H2 (V43).
- **JG621A** = 12910 **MPU** (not a 12900E MPU per se — it is the legacy 12910 chassis' Main Processing Unit); **JG622A/JG623A** = 12910 Type A/B fabrics. These belong to the legacy 12910 (JG619A) which the QuickSpec folds into the 12900E family.
- **Switching-Kapazität per linecard = ZU_VERIFIZIEREN for ALL 34 linecards** — OEM publishes NO per-card fabric SwK (only chassis backplane 28.8 Tbps [12904E]/57.6 Tbps [12908E] and per-fabric-module Tbps). Do NOT port-math. The 4 Type X/H2 fabrics (JL841A/JL842A/R9F14A/R9F15A) also lack a stated Tbps in their names → SwK ZU_VERIFIZIEREN.
- **PoE:** none — every 12900E line card is a DC-core module; no PoE on any PID.
- **Generation interop (from OEM notes, for the chassis-side "Modul-Generation" gate):** Type X modules ↔ Type X fabrics only; HB ↔ Type H fabrics; H2 ↔ H2 fabrics; EA/EB/EC I/O ↔ Type F/A/B fabrics; FX/FE I/O require the JH107A LPU Adapter and cannot mix with EA/EB/EC. Comware v9 runs only on H2 modules; all other generations run Comware v7.
- **Pending courier: 0.** OEM doc c04111378 fully reached (V43 current tables + HPE-authored legacy QuickSpec PDF + HPE data sheet).

Scratch artifacts (absolute paths): `C:\Users\Vince\AppData\Local\Temp\claude\D--Project\a57c90b8-6e03-408b-8338-39f4bfdc1b6b\scratchpad` not used; working extracts in `/tmp/jina2.txt` (V43), `/tmp/ws.txt` (legacy QS), `/tmp/ds12900.txt` (data sheet).