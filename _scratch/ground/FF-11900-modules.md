# FF-11900-modules | modules | HPE FlexFabric 11900 Modules | doc c03801956

The EOS PDF didn't extract, but I have full verbatim confirmation from the primary OEM Option-Parts doc (c03801956) plus the FlexNetwork Portfolio Guide (chassis-level SwK) and the h20195 product doc. All 8 module PIDs are confirmed. This family is fully grounded — 0 pending courier.

Grounding complete. All 8 roster module PIDs confirmed verbatim from OEM Option-Parts doc **c03801956** (cross-checked against the HP FlexNetwork Portfolio Guide PDF and h20195 product docs). The manifest's "~9" is corrected to **8 modules** (JG609A–JG615A + JG918A); JG616A/JG617A = PSUs, JG618A = fan, JG608A = chassis — correctly excluded from the module pool.

FAMILY: FF-11900-modules | E3: "HPE FlexFabric 11900 Modules" | OEM doc c03801956 | 8 PIDs | 0 pending courier

Per-PID lines:

**JG609A** | "HP FlexFabric 11900 Main Processing Unit" | MPU/Route-Processor | HPE FlexFabric 11900 (11908-V chassis JG608A) | n/a (supervisor, no data ports) | n/a | EOL (EOS July 2016)

**JG610A** | "HP FlexFabric 11908 1.92Tbps Type D Fabric Module" | Fabric-Module | HPE FlexFabric 11900, Type D (11908-V chassis) | n/a | **1.92 Tbps (Type D fabric module, verbatim)** | EOL

**JG611A** | "HP FlexFabric 11900 32-port 10GbE SFP+ SF Module" | Linecard | HPE FlexFabric 11900, "SF" module | Portanzahl 32 | Port-Konfiguration SFP+ | Port-Geschwindigkeit 10GbE | PoE: keine | Switching-Kapazität ZU_VERIFIZIEREN (chassis-level: bis 7.7 Tb/s; per-card fabric not stated verbatim in OEM doc) | EOL

**JG612A** | "HP FlexFabric 11900 48-port 10GbE SFP+ SF Module" | Linecard | HPE FlexFabric 11900, "SF" module | Portanzahl 48 | SFP+ | 10GbE | PoE: keine | SwK ZU_VERIFIZIEREN (per-card not verbatim) | EOL

**JG613A** | "HP FlexFabric 11900 4-port 40GbE QSFP+ SF Module" | Linecard | HPE FlexFabric 11900, "SF" module | Portanzahl 4 | QSFP+ | 40GbE | PoE: keine | SwK ZU_VERIFIZIEREN | EOL

**JG614A** | "HP FlexFabric 11900 8-port 40GbE QSFP+ SF Module" | Linecard | HPE FlexFabric 11900, "SF" module | Portanzahl 8 | QSFP+ | 40GbE | PoE: keine | SwK ZU_VERIFIZIEREN | EOL

**JG615A** | "HP FlexFabric 11900 24-port 1/10GBASE-T SF Module" | Linecard | HPE FlexFabric 11900, "SF" module | Portanzahl 24 | Port-Konfiguration RJ-45 (1/10GBASE-T copper) | Port-Geschwindigkeit 1/10GbE | PoE: keine | SwK ZU_VERIFIZIEREN | EOL

**JG918A** | "HP FlexFabric 11900 2-port 100GbE CFP SE Module" | Linecard | HPE FlexFabric 11900, "SE" module | Portanzahl 2 | Port-Konfiguration CFP | Port-Geschwindigkeit 100GbE | PoE: keine | SwK ZU_VERIFIZIEREN | EOL

Notes for the manifest:
- **Roster verified**: no additions, no removals. Roster "~9" → **exactly 8 modules**. All 8 confirmed in OEM doc.
- **No PoE** on any 11900 linecard (data-center aggregation series; OEM lists none).
- **Modultyp split**: 1 MPU (JG609A) + 1 Fabric (JG610A, verbatim 1.92 Tbps Type D) + 6 Linecards (JG611–615A, JG918A). Note the SF/SE suffix is part of the verbatim card name (SF = standard fabric-attach, SE = enhanced) — captured in Kompatible Serie as the module-type qualifier.
- **Per-card fabric SwK = ZU_VERIFIZIEREN** (per your NEVER-port-math rule): the OEM Option-Parts doc + Portfolio Guide give only the **chassis-level 7.7 Tb/s / 384×10GbE / 64×40GbE** figure, not per-linecard fabric throughput. The retired QuickSpec c04111418 (which would carry per-card numbers) is Akamai-blocked/retired. Do NOT derive per-card SwK from the 1.92 Tbps fabric or port counts.
- **Interop note (verbatim from HPE)**: 11900 modules are cross-compatible in the 10500 chassis from unified Comware release R7169 onward (11900 ≈ 10500 platform twin; h3c S9500E lineage) — useful for the "Kompatible Serie" field if operator wants 10500 listed as a co-compatible chassis.
- Chassis JG608A (11908-V) belongs to the separate **FlexFabric 11900 Switches** family, already noted in the manifest.

Relevant files:
- `D:\Project\hexcat\_scratch\comware_smb_phase1_grounding.md` (prior enumeration; the 11900 entry there is confirmed and can be upgraded from "~9 modules" to the 8-PID roster above)

Sources: [HP FlexFabric 11900 Option Parts (c03801956)](https://support.hpe.com/hpsc/doc/public/display?docId=emr_na-c03801956) · [HP FlexNetwork Portfolio Guide PDF](https://www.novastar.net/wp-content/uploads/HP-FLexNetwork-Portfolio-GuideOPT.pdf) · [JG615A product doc h20195 oid=5385062](https://h20195.www2.hpe.com/v2/default.aspx?cc=id&lc=en&oid=5385062) · [HP 11900 EOS table July 2016](https://support.hpe.com/docs/display/public/hpe-networking-eos/docs/products/eos/HP%2011900%20Switch%20Series%20-%20July%202016%20-%20External%20-%20Center%20Aligned%20Table.pdf)