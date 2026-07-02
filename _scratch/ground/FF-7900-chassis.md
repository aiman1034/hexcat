# FF-7900-chassis | chassis | HPE FlexFabric 7900 Switches | doc 4AA5-2359ENN (QuickSpec c04293387 RETIRED — use the data sheet)

The operating-temperature table on the HPE-authored manual won't render through the proxy (image/table-heavy pages), and I will not port the legacy 3Com S7900E value (wrong generation). I have enough verbatim OEM data to return the block. Here is the grounding.

---

**FAMILY: FF-7900-chassis — "HPE FlexFabric 7900 Switches"**

FAMILY-LEVEL:
- **Operating temp**: ZU_VERIFIZIEREN — HPE data sheet 4AA5-2359ENW + QuickSpec c04293387 both RETIRED/obsolete; HPE installation-manual Appendix A env-table (manualslib doc 1291069, pp.67-69) is image/table-only and did not render through r.jina.ai or WebFetch. Legacy 3Com/H3C S7900E twin lists 0–45°C but is a DIFFERENT (pre-Comware-v7, 2.4 Tbps) generation → NOT ported. Courier the HPE-authored env table.
- **EOL status**: OEM QuickSpec c04293387 + data sheet 4AA5-2359ENW officially RETIRED / "base products now considered obsolete" (confirmed on HPE psnow retirement notice). Products EOL/obsolete per HPE; exact EOSL date ZU_VERIFIZIEREN.
- **Comware / branding**: HPE Comware v7 (7900 is a Comware-v7 DC ToR/EoR chassis; H3C twin = S7900E). Verbatim SW version string ZU_VERIFIZIEREN (release-notes not reached).
- **Layer**: L2 + L3 (data-center, fully distributed L2/L3 switching; "Layer Supported: 3").
- **Roster VERIFIED**: 4 PIDs confirmed = JG682A (7904, 4 I/O), JG841A (7910, 10 I/O), JH122A (7904 TAA), JH123A (7910 TAA). No additions/removals — matches Phase-1 manifest. TAA = trade-agreement re-badges of the same chassis.

PER-PID (verbatim, from HPE installation manual doc 1291069 Appendix A + HPE-derived spec tables; the two chassis architectures differ — 7904 = fixed/built-in MPU, 7910 = removable Fabric/MPU combi modules):

```
JG682A | HPE FlexFabric 7904 Switch Chassis | 4 I/O (LPU) slots + 1 built-in/fixed MPU (slot 0, integrated switching fabric); NO separate fabric slot — fabric integrated in fixed MPU | 3.8 Tbps (system switching capacity; Bpps/Mpps ZU_VERIFIZIEREN) | 2 RU (88.1 mm; W 440 mm × D 720 mm) | complete-switch max 40 kg (bare chassis 15.5 kg) verbatim | 2× PSR1800-56A, AC, N+1 redundancy | 2 fan trays, airflow back-to-front OR front-to-back (variant) | MPU: fixed/built-in (MIPS64 dual-core @1.2 GHz, 4 GB DDR3), not a removable PID | redundancy: PSU N+1, fan 2-tray; MPU/fabric NON-redundant (single fixed MPU) | L2/L3 | EOL (QuickSpec RETIRED)
JG841A | HPE FlexFabric 7910 Switch Chassis | 10 I/O (LPU) slots + 2 Fabric/MPU-combi slots (slots 10 & 11) — fabric+MPU combined in one module; NO separate standalone MPU slot | 9.6 Tbps (system switching capacity; Bpps/Mpps ZU_VERIFIZIEREN) | 5 RU (220 mm; W 440 mm × D 760 mm) | complete-switch max 70 kg verbatim (bare-chassis kg ZU_VERIFIZIEREN) | 4× PSU, AC, N+1 redundancy | 4 fan trays, airflow back-to-front OR front-to-back (variant) | MPU/Fabric: JG842A "7.2Tb/s Fabric Main Processing Unit" (combined Fabric+MPU module) | redundancy: 2× Fabric/MPU dual (active-standby switchover), PSU N+1, fan 4-tray | L2/L3 | EOL (QuickSpec RETIRED)
JH122A | HPE FlexFabric 7904 TAA-compliant Switch Chassis | same as JG682A: 4 I/O (LPU) + 1 built-in/fixed MPU, integrated fabric | 3.8 Tbps (Bpps/Mpps ZU_VERIFIZIEREN) | 2 RU (88.1 mm; W 440 × D 720 mm) | complete-switch max 40 kg (chassis 15.5 kg) verbatim | 2× PSR1800-56A AC, N+1 | 2 fan trays, B2F or F2B | fixed built-in MPU | PSU N+1, fan 2-tray; MPU/fabric non-redundant | L2/L3 | EOL (RETIRED)
JH123A | HPE FlexFabric 7910 TAA-compliant Switch Chassis | same as JG841A: 10 I/O (LPU) + 2 Fabric/MPU-combi slots (10 & 11) | 9.6 Tbps (Bpps/Mpps ZU_VERIFIZIEREN) | 5 RU (220 mm; W 440 × D 760 mm) | complete-switch max 70 kg verbatim | 4× PSU AC, N+1 | 4 fan trays, B2F or F2B | JG842A Fabric/MPU-combi module | 2× Fabric/MPU dual (active-standby), PSU N+1, fan 4-tray | L2/L3 | EOL (RETIRED)
```

**CRITICAL slot-architecture note (per instruction):** The 7900 chassis do NOT have the 12900E-style "6 dedicated fabric slots." Fabric-slot vs MPU-slot breakdown verbatim:
- **7904 (JG682A/JH122A)**: fabric is INTEGRIERT in a single FIXED/built-in MPU (slot 0) — 0 removable fabric slots, 0 removable MPU slots, 4 I/O slots.
- **7910 (JG841A/JH123A)**: 2 slots (10 & 11) each hold a COMBINED Fabric+MPU module (JG842A) — the fabric and MPU roles are NOT on separate slots; 2 Fabric/MPU-combi slots + 10 I/O slots.

**Weight guardrail deviation (flagged):** These chassis are BELOW the ">50 kg" rule (7904 complete = 40 kg / 2RU; 7910 complete = 70 kg / 5RU). This is a genuine verbatim OEM config weight (HPE manual Table 11), NOT ZU_VERIFIZIEREN — the 7900 is a compact fixed-fabric DC chassis, so the >50 kg heuristic legitimately does not apply to the 7904.

**PENDING AUDITOR COURIER (2 items, HPE-authored source unreachable):**
1. Operating/storage temperature + humidity — HPE data sheet 4AA5-2359ENW (docname; ENN in prompt is wrong) & QuickSpec c04293387 both RETIRED; manual Appendix A env-table image-only. Do NOT port the 3Com S7900E 0–45°C (wrong generation).
2. Comware v7 exact version string + Bpps/Mpps forwarding rate.

URLs tried: `hpe.com/psnow/doc/4AA5-2359ENN` (404), `r.jina.ai/.../4AA5-2359ENN` (404), `h20195.www2.hpe.com/V2/Getdocument.aspx?docname=4AA5-2359ENW` (301→psnow Akamai-blocked), `r.jina.ai/https://psnow.ext.hpe.com/V2/Getdocument.aspx?docname=4AA5-2359ENW` (RETIRED notice, no body), `hpe.com/h20195/v2/GetPDF.aspx/c04293387.pdf` (timeout; via Jina = RETIRED notice), `support.hpe.com docDisplay c04932605` (template only), SHI eu/us (403).

**Sources that yielded verbatim numbers:** HPE FlexFabric 7900 Series Installation Manual (HPE-authored), manualslib doc 1291069 pp.62-66 (slots, weight, dimensions, RU, PSU count/redundancy, fan trays, airflow); switching-capacity 3.8/9.6 Tbps + JG842A "7.2Tb/s Fabric Main Processing Unit" cross-confirmed via HPE-derived spec tables. Legacy 3Com S7900E datasheet (senetic PDF) read but REJECTED as wrong-generation cross-check.