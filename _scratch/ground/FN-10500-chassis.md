# FN-10500-chassis | chassis | HPE FlexNetwork 10500 Switches | doc c04212581 + c03050623

I have everything needed. EOL is confirmed: the QuickSpecs doc (c04212581) is officially retired and base products are obsolete/no-longer-available-for-sale (HPE psnow retirement notice), with the TAA LPU line EoS Mar-2018. The roster is verified against the HPE QuickSpecs verbatim — all 8 PIDs confirmed, MPU PIDs identified (JC614A, JG496A, JH198A + TAA JG375A), and fabric slot / MPU slot counts stated separately from I/O slots.

Here is the grounded family block.

---

FAMILY: FN-10500-chassis — HPE FlexNetwork 10500 Switch Series

FAMILY-LEVEL FACTS (verbatim from HPE QuickSpecs c04212581, retrieved PDF; cross-checked H3C S10500 twin):
- Operating temperature: 0°C to 45°C (32°F to 113°F) — identical all 4 chassis. Storage/non-op: -40°C to 70°C. Op. humidity 10–95% noncondensing. Altitude up to 4 km.
- Layer: L2 switching + full L3 routing (IPv4/IPv6, MPLS, VPLS) + MPLS L2/L3 VPN. Enterprise campus core, Clos architecture.
- Comware: HPE Comware v7 (modular OS); some line cards also run Comware v5. IRF (virtualizes up to 4 chassis, single mgmt IP). MDC (Multitenant Device Context). ISSU requires IRF + R7169P01 or later.
- Supported MPU / Management Modules (chassis-agnostic, 2 slots each): **JC614A** (A10500 Main Processing Unit, CWv5), **JG496A** (10500 Type A MPU w/ Comware v7), **JH198A** (FlexNetwork 10500 Type D MPU w/ Comware v7), and TAA **JG375A** (10500 TAA Main Processing Unit). MPU slot placement: 10504 = slots 0&1; 10508/10508-V = slots 4&5; 10512 = slots 6&7.
- Redundancy (all models): redundant/load-sharing fabrics, management (MPU), fan assemblies, and power supplies; hitless stateful failover; all modules hot-swappable; passive (no-active-component) backplane. PSU redundancy: 10504 = 3+1; 10508/10508-V/10512 = 5+1.
- PSU options (family): JC610A 2500W AC / JC747A 2400W DC. Warranty: 1-year.
- EOL: **OBSOLETE / END OF SALE.** QuickSpecs c04212581 officially retired by HPE ("base products… now considered obsolete and… no longer available for sale"). Comware v7 TAA LPU line EoS announced 30-Nov-2017 (planned EoS 31-Mar-2018).
- Fabric slots = 4 dedicated switch-fabric slots on every chassis (distinct from I/O and MPU slots). Fabric modules: Type B or Type D (min 4, all same Type). System SwK depends on fabric Type installed (Type D > Type B).

PER-PID (all facts verbatim from HPE QuickSpecs c04212581; TAA variants share their base chassis spec):

JC613A | HPE FlexNetwork 10504 Switch Chassis | 4 I/O module slots + 4 switch-fabric slots + 2 MPU slots | up to 4.8 Tbps (Type D fabric) / 3.5 Tbps (Type B); throughput up to 2.9 Bpps Type D / 1.9 Bpps Type B (per-chassis Technical-Spec table) | 8U (43.99 × 65.99 × 35.31 cm) | 38.7 kg (chassis) / 83.07 kg full-config weight | 4 PSU slots, min 1 required, 3+1 redundancy, 2500W AC (JC610A) or 2400W DC (JC747A) | 1 fan tray slot (spare JC632A) | MPU: JC614A / JG496A / JH198A / TAA JG375A | redundant MPU + 4 fabric + PSU(3+1) + fan, all hot-swap | L2/L3 | OBSOLETE (doc retired)

JC612A | HPE FlexNetwork 10508 Switch Chassis | 8 I/O module slots + 4 switch-fabric slots + 2 MPU slots | up to 9.3 Tbps (Type D) / 4.2 Tbps (Type B); throughput up to 5.7 Bpps Type D / 1.9 Bpps Type B | 14U (43.99 × 65.99 × 62 cm) | 56.7 kg (chassis) / 129.43 kg full-config weight | 6 PSU slots, min 1 required, 5+1 redundancy, 2500W AC / 2400W DC | fan tray (spare JC633A) | MPU: JC614A / JG496A / JH198A / TAA JG375A | redundant MPU + 4 fabric + PSU(5+1) + fan, hot-swap | L2/L3 | OBSOLETE

JC611A | HPE FlexNetwork 10508-V Switch Chassis | 8 I/O module slots (vertical) + 4 switch-fabric slots + 2 MPU slots | up to 9.3 Tbps (Type D) / 4.2 Tbps (Type B); throughput up to 5.7 Bpps Type D / 1.9 Bpps Type B | 20U (43.99 × 65.99 × 88.6 cm) | 76.9 kg (chassis) / 150.28 kg full-config weight | 6 PSU slots, min 1 required, 5+1 redundancy, 2500W AC / 2400W DC | fan tray (spare JC634A) | MPU: JC614A / JG496A / JH198A / TAA JG375A | redundant MPU + 4 fabric + PSU(5+1) + fan, hot-swap | L2/L3 | OBSOLETE

JC748A | HPE FlexNetwork 10512 Switch Chassis | 12 I/O module slots + 4 switch-fabric slots + 2 MPU slots | up to 13.8 Tbps (Type D) / 6.0 Tbps (Type B); throughput up to 8.6 Bpps Type D / 2.9 Bpps Type B | 18U (44.0 × 66.0 × 79.7 cm) | 75.4 kg (chassis) / 172.8 kg full-config weight | 6 PSU slots, min 1 required, 5+1 redundancy, 2500W AC / 2400W DC | 2 fan trays (top JC758A + bottom JC773A) | MPU: JC614A / JG496A / JH198A / TAA JG375A | redundant MPU + 4 fabric + PSU(5+1) + fan, hot-swap | L2/L3 | OBSOLETE

JG820A | HPE FlexNetwork 10504 TAA Switch Chassis | 4 I/O + 4 switch-fabric + 2 MPU slots (= JC613A) | = JC613A (4.8 Tbps Type D / 3.5 Tbps Type B) | 8U | 38.7 kg / 83.07 kg full-config ZU_VERIFIZIEREN (TAA doc not separately published; assumed = base JC613A) | 4 PSU, 3+1 | 1 fan tray | MPU incl. TAA JG375A | as JC613A | L2/L3 | OBSOLETE (TAA EoS 31-Mar-2018)

JG821A | HPE FlexNetwork 10508 TAA Switch Chassis | 8 I/O + 4 switch-fabric + 2 MPU slots (= JC612A) | = JC612A (9.3 Tbps Type D / 4.2 Tbps Type B) | 14U | 56.7 kg / 129.43 kg full-config ZU_VERIFIZIEREN (= base JC612A) | 6 PSU, 5+1 | fan tray | MPU incl. TAA JG375A | as JC612A | L2/L3 | OBSOLETE (TAA EoS 31-Mar-2018)

JG822A | HPE FlexNetwork 10508-V TAA Switch Chassis | 8 I/O (vertical) + 4 switch-fabric + 2 MPU slots (= JC611A) | = JC611A (9.3 Tbps Type D / 4.2 Tbps Type B) | 20U | 76.9 kg / 150.28 kg full-config ZU_VERIFIZIEREN (= base JC611A) | 6 PSU, 5+1 | fan tray | MPU incl. TAA JG375A | as JC611A | L2/L3 | OBSOLETE (TAA EoS 31-Mar-2018)

JG823A | HPE FlexNetwork 10512 TAA Switch Chassis | 12 I/O + 4 switch-fabric + 2 MPU slots (= JC748A) | = JC748A (13.8 Tbps Type D / 6.0 Tbps Type B) | 18U | 75.4 kg / 172.8 kg full-config ZU_VERIFIZIEREN (= base JC748A) | 6 PSU, 5+1 | 2 fan trays | MPU incl. TAA JG375A | as JC748A | L2/L3 | OBSOLETE (TAA EoS 31-Mar-2018)

---

ROSTER VERIFICATION vs Phase-1 manifest:
- All 8 PIDs CONFIRMED present in HPE QuickSpecs c04212581. No additions, no removals.
- Manifest note "JC613A(10504, 4 I/O+2 MPU+4 fabric)" is EXACT-CORRECT per HPE Technical-Spec table (4 I/O + 2 MPU + 4 fabric). Same 2-MPU + 4-fabric pattern holds for all four chassis (manifest only annotated it on JC613A; now confirmed for all).
- Family SwK note in prior scratch ("more than 11 Tbps") is the marketing/overview headline (11.52 Tb/s line cards, 13.72 Tb/s fabric w/ Type D); the per-chassis SwK figures above are the authoritative system numbers from the per-chassis Technical Specifications table.

DATA CONFIDENCE:
- I/O/fabric/MPU slots, dimensions, RU height, both weights (chassis + full-config), operating temp, PSU count/redundancy, fan trays, MPU PIDs, layer, Comware = HPE-VERBATIM (QuickSpecs c04212581, full PDF extracted; H3C S10500 twin corroborates slot topology: 2 MPU + 4 fabric + N LPU).
- TAA (JGxxx) full-config weights flagged ZU_VERIFIZIEREN — HPE never published a separate TAA spec table; physically identical chassis to the JCxxx base, so inherited.
- Chassis weights all >50 kg for the full-config (and 10508/10508-V/10512 even bare) — consistent with the >50 kg chassis expectation. 10504 bare = 38.7 kg but full-config = 83.07 kg.

SOURCES: HPE QuickSpecs c04212581 (retired; full PDF recovered via edsystem.sk mirror + parsed locally); HPE PIR c03050623 (retired landing); H3C S10500 series page (Comware OEM twin, cross-check only); HPE Networking EoS portal (TAA EoS Nov-2017/Mar-2018). PDF cached at C:\Users\Vince\.claude\projects\D--Project\a57c90b8-6e03-408b-8338-39f4bfdc1b6b\tool-results\webfetch-1782962241580-txcelx.pdf. No family marked DENOMINATOR PENDING — all reachable via HPE-authored QuickSpecs.