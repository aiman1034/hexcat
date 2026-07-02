# FF-11900-chassis | chassis | HPE FlexFabric 11900 Switches | doc c03801956 (Option Parts) + HPE Store

EOL is confirmed as an end-of-sale/legacy product (11900 series is discontinued). I have enough OEM-grounded facts. Here is the family block.

---

FAMILY: FF-11900-chassis — "HPE FlexFabric 11900 Switches"
OEM DOCS VERIFIED: Option Parts c03801956 (roster + PSU/fan/module PIDs, reachable via Jina proxy) + HPE-authored datasheet (product datasheet/brochure mirror + h20195 oid=5385041). Comware twin H3C S9500E cross-checkable but not needed — HPE facts obtained directly.

FAMILY-LEVEL:
- Software / Comware: HP Comware v7 (verbatim "HP Comware v7 software"; specific build not published in datasheet — ZU_VERIFIZIEREN if a version string is required)
- Operating temperature: 0 – 45 °C (verbatim, HPE datasheet mirror)
- Layer: Layer 2 and Layer 3 (verbatim)
- EOL: End-of-Sale / legacy — the FlexFabric 11900 series is discontinued (listed on HPE Networking End-of-Sale). Exact EOS/EOSL date not on the OEM datasheet; carried on HPE EoS index — ZU_VERIFIZIEREN for the precise date.
- Fabric-slot note (CRITICAL axis): chassis has SEPARATE dedicated switch-fabric slots and MPU slots distinct from I/O slots — NOT integrated.

ROSTER VERIFICATION: Phase-1 manifest confirmed. JG608A (11908-V) is the ONLY orderable chassis in this family — no bare "11908", JG608AR (refurb) excluded. No addition/removal. Modules (JG609A MPU, JG610A fabric, JG611A/612A/613A/614A/615A/JG918A I/O, JG616A/617A PSU, JG618A fan) belong to a separate "FF-11900-modules" lane, not chassis.

PER-PID:

JG608A | HP FlexFabric 11908-V Switch Chassis | 14 Steckplätze gesamt: 8 I/O + 4 Switch-Fabric + 2 MPU (verbatim "14-slot vertical chassis … 2 MPU slots, 4 switch fabric slots, 8 I/O slots") | 7.7 Tb/s switching capacity, 5.8 Bpps (5.76 Bpps) forwarding throughput (verbatim; NOT port-summed) | 20U vertical chassis; 439.9 mm (W) × 659.9 mm (D) × 886 mm (H) (verbatim) | 76.9 kg (169.53 lb) chassis config weight (verbatim; >50 kg as expected) | PSU: HP FF 11900 2500W AC PSU (JG616A) / HP FF 11900 2400W DC PSU (JG617A); min 1, max 6 PSU per enclosure → N+N / N+1 redundant; 100–120 / 200–240 V AC | Cooling: hot-swappable fan tray (spare = HP FF 11908-V Spare Fan Assy JG618A); side-to-side / front-to-back per module design | Supported MPU/Supervisor: HP FF 11900 Main Processing Unit JG609A (Dual-Core MIPS 1.2 GHz, 512 MB flash, 8 GB DDR2) — fabric via HP FF 11900 1.92Tbps Type D Fabric Module JG610A | Redundancy: dual MPU (2 slots, 1+1), 4 fabric modules, redundant hot-swap PSU (up to 6) + hot-swap fan tray; "fully redundant and hot-swappable components" (verbatim); IRF + TRILL | Layer 2/3 | EOL: End-of-Sale (series discontinued; exact date ZU_VERIFIZIEREN)

Pending courier: NONE for the chassis (all chassis facts OEM-grounded). Only open items are the exact Comware build string and the exact EOS/EOSL date, both flagged ZU_VERIFIZIEREN (not published on the datasheet; require HPE EoS notice PDF which is Akamai-gated).

Relevant file: D:\Project\hexcat\_scratch\comware_smb_phase1_grounding.md (prior enumeration — 11900 chassis line under "FLEXFABRIC ADDITIONS surfaced by Agent D").