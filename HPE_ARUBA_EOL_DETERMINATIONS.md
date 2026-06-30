# HPE/Aruba Switches — EOL Determinations (STEP 1b)

**Date:** 2026-06-30 · **Rule (locked decision 3):** EXCLUDE any family/PID with HPE **End-of-Sale BEFORE 2020-01-01**; KEEP current/shipping + EoS ≥ 2020-01-01. Marker = **End-of-Sale** (if only End-of-Support/Life is published, that is used and noted). Every date cited from OEM lifecycle / QuickSpecs / EoS-announcement PDFs (fetched via cached/mirror copies — hpe.com + arubanetworks.com origins Akamai-blocked from this host; the Aruba Hardware End-of-Sale master list, updated 2020-05-06, + dedicated EoS-announcement PDFs were the primary sources). Undated → **ZU_VERIFIZIEREN** (auditor confirms against live HPE).

## IN — End-of-Sale ≥ 2020 or current/shipping (30 families)
| Family | HPE End-of-Sale | Source | Note |
|---|---|---|---|
| Aruba CX 6000 / 6100 / 6300F / 6300M / 4100i | current (no EoS) | current QuickSpecs / 2025 install guides / live HPE Store | shipping |
| Aruba CX 6200F | A-rev **2024-07-31** (EoS, EoSL 2032); B-rev current | Aruba EoS announcement (announced 2023-05-17) | enumerated the CURRENT **B-rev** (20 PIDs); A-rev passes cutoff but superseded |
| Aruba CX 8100 / 8325 / 8360v2 / 9300 / 9300S / 10000 | current | Aruba datasheets ©2020–2025; not in 2020 EoS list as retiring | shipping |
| Aruba CX 8320 | **ZU_VERIFIZIEREN** (no dated EoS accessible; NOT listed retiring in 2020 OEM list) | Aruba HW EoS list 2020-05-06 | IN — no pre-2020 evidence (was still the *replacement* product in 2020) |
| Aruba 2530 (Gigabit only) | 24/48G **2021-10-31**, 8G **2021-05-31** | EOS_2530-Gigabit-{24-48,8}-port PDFs | PARTIAL — only the 6 Gigabit PIDs IN |
| Aruba 2540 | **2021-10-31** (announced 2021-04-30) | EOS_2540-Switches.pdf | IN |
| Aruba 2930F | current (8-port EoS 2023-09-30) | HPE airheads + EOS_2930F PDF | IN — mainstream line not migrating to CX |
| Aruba 2930M | current (no EoS) | HPE airheads roadmap; Service Express "Active" | IN |
| Aruba 3810M | **2025-01-31** (announced 2022-11-09, EoSL 2030) | Aruba 3810 EoS Announcement v5 | IN |
| HPE FlexFabric 5700 | **2020-02-03 / 2020-04-30** (by PID) | Aruba HW EoS master list | IN (EoS in 2020) |
| HPE FlexFabric 5900 | JG510A **2022-02-28**; JL864A current | EOS_HPE-FlexFabric-5900AF PDF | IN |
| HPE FlexFabric 5940 (fixed only) | JH396A **2020-03-31**; JH390A/JH391A current; JH394A/JH395A **ZU_VERIFIZIEREN** (orig-EoS 2019-10, superseded) | Aruba HW EoS master list | IN; modular JH397A/JH398A dropped (decision 4) |
| HPE FlexNetwork 5130 EI | 7 PIDs **2022-04-30**; JG938A/JG939A **2019-01-31** (OUT) | EOS_5510-HI-5130-EI PDF + master list | PARTIAL — 7 IN, 2 OUT |
| HPE FlexNetwork 5130 HI | **2022-06-30** | EOS_5130-HI PDF | IN |
| HPE FlexNetwork 5510 HI | **2022-04-30** | EOS_5510-HI-5130-EI PDF | IN |
| HPE OfficeConnect 1420 | current (no EoS yet; 1430 is the successor) | HPE/Aruba EoS doc 1405-1420; Service Express "Supported" | IN |
| HPE OfficeConnect 1820 | **2022-03-07** | HPE EoS announcement | IN |
| HPE OfficeConnect 1950 | **2020-02-29** (announced 2019-07-31) | HPE 1950 EoS notice | IN (just inside cutoff) |
| Aruba Instant On 1830 / 1930 / 1960 | current | instant-on.hpe.com lifecycle; Service Express | shipping |

## OUT — End-of-Sale BEFORE 2020-01-01 (15 families)
| Family | HPE End-of-Sale | Source |
|---|---|---|
| Aruba 2615 | 2018-10-31 (announced 2018-03-31) | Aruba 2615 EoS PDF (Mar 2018) |
| HP 2620 | 2018-10-31 (PoE+) / 2019-06-30 (non-PoE) | Aruba HW EoS master list |
| HP 2915 | 2018-03-31 (J9562A) | EOS_2915-2920 PDF |
| Aruba 2920 | 2018-03-31 … 2018-11-30 (by model) | EOS_2915-2920 PDF |
| Aruba 3500 / 3500yl | 2014-06-30 (announced 2013-12-11) | HP 3500/6200 EoS PDF |
| HPE FlexFabric 5800 | 2018 (JC100B 2018-01-31; rest pre-2018) | Aruba HW EoS master list |
| HPE FlexFabric 5930 | JG726A **2018-11-30** (EoSL 2022-10-31 ≠ EoS) | Aruba HW EoS master list |
| HPE FlexNetwork 5120 SI | 2018-10-31 (announced 2018-03-31) | HPE 5120 SI EoS notice |
| HPE FlexNetwork 5500 EI | pre-2020 (legacy; not in current EoS tracking) | platform-era (H3C/HP A-series transition ~2017–18) |
| HPE FlexNetwork 5500 HI | 2018-03-31 (JG542A) + legacy | Aruba HW EoS master list |
| HPE OfficeConnect 1410 | 2016-03-31 | HP 1410 EoS notice (Feb 2016) |
| HPE OfficeConnect 1620 | 2019-10-31 (announced 2019-07-31) | HPE 1620 EoS PDF |
| HPE OfficeConnect 1810 v1 (1810G/V1810) | 2015-04-01 | HP 1810G EoS notice |
| HP V1910 | 2015-03-31 | HP 1910 EoS notice |
| HPE OfficeConnect 1920 | 2017-03-31 (last order 2017-05-15) | HPE 1920 EoS PDF (Mar 2017) |

## ZU_VERIFIZIEREN (undated / unverifiable — auditor to confirm; default lean as noted)
- **Aruba 2530 Fast-Ethernet** (J9778A–J9783A) + **JL070A** — no published EoS date found; family pattern (oldest 2530 variants) → **lean OUT**. (2530 10G-uplink J9853A–J9856A confirmed OUT, EoS 2017-09-30.)
- **HPE OfficeConnect 1810 v2** (J9800A/J9801A, Fast-Ethernet) — undated; ancient FE line (© ≤2016) → **lean OUT**.
- **Aruba CX 8320** — no dated EoS accessible; not retiring in the 2020 OEM list → **IN** (no pre-2020 evidence).
- **HPE FlexFabric 5940 JH390A/JH391A** (current, exact EoS undated) + **JH394A/JH395A** (orig-EoS 2019-10, superseded by the QSFP28 versions, EoS-date blank) — all **IN**, only the precise EoS date unverified.
- **Aruba CX 6200F B-rev PID list** — sourced from the EoS-announcement replacement table, not the live datasheet (a00059762enw 403'd) → confirm the 20 B-rev PIDs at author time.
- **Aruba CX 8325 JL857A / DC / TAA bundles** — named in prior notes but NOT present in cached datasheet a00059009enw (only 4 AC bundles + 2 base) → confirm against a newer 8325 QuickSpecs.

**Net:** 30 families IN (224 PIDs) · 15 families OUT (EoS < 2020) · 4 modular-chassis + 5 module families dropped per decision 4 · 5930/5940 modular slot-variants dropped.
