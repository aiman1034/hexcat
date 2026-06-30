# HPE/Aruba Switches — Merkmal-Fit (STEP 1)

**Date:** 2026-06-30 · Maps every spec the HPE/Aruba switch data sheets expose to the **EXISTING live switch Merkmal names** (the Cisco switch bundles use these). **No Merkmal is invented, renamed, or added.** Result: **every HPE/Aruba spec has an existing Merkmal home — 0 new Merkmal required.** Two feature edge-cases (MACsec, DPU services) are handled as **prose**, exactly as Cisco features are — not as Merkmale.

## Live Merkmal vocabulary (verbatim, from the Cisco switch bundles)
- **Fixed-switch gold-slice (15):** Switch-Typ · Layer · Portanzahl · Port-Konfiguration · Port-Geschwindigkeit · Uplink-Ports · PoE · Switching-Kapazität · Durchsatz · Stacking · Bauform · Stromversorgung · Kühlung · Anwendung · Betriebstemperatur
- **Modular-chassis adds (3):** Steckplätze · Unterstützte Supervisor-Engines · Redundanz
- **Module / Class-B (2):** Modultyp · Kompatible Serie

## Mapping — HPE/Aruba spec → existing Merkmal
| HPE/Aruba spec (as the OEM data sheet states it) | Existing Merkmal | Notes / value form (matches Cisco usage) |
|---|---|---|
| Managed / Layer-2 / Layer-3 / Modular chassis class | **Switch-Typ** | `Managed` for fixed; `Modular-Chassis` for the 4 chassis lines + the 5930/5940 slot-variants |
| L2 / L2+ / L3 (static, RIP, OSPF, BGP, EVPN/VXLAN) | **Layer** | `L2` or `L3` (same 2-value form as Cisco; routing depth → prose) |
| Port count (8/12/24/48 …) | **Portanzahl** | integer; chassis omit it (drives the chassis carve-out, same as Cisco) |
| Port mix / media (10/100/1000BASE-T, SFP, SFP+, SFP28, SFP56, QSFP+, QSFP28, QSFP-DD) | **Port-Konfiguration** | the access-port composition string |
| Port speed tier (1G / 10G / 25G / 40G / 100G / 400G) | **Port-Geschwindigkeit** | top access speed (FC-style guard N/A here) |
| Uplink ports (4×SFP+, 6×QSFP+, 2×100G …) | **Uplink-Ports** | the dedicated-uplink string |
| PoE / PoE+ / PoE++ (802.3af/at/bt), Class 4/6/8, budget W | **PoE** | budget W + standard/class, exactly as Cisco SMB/Catalyst PoE values |
| Switching capacity (Gbps / Tbps) | **Switching-Kapazität** | render Option-1 (≥2 Tbit/s → Tbit/s; else Gbit/s) — same rule as Cisco |
| Throughput / forwarding rate (Mpps / Bpps) | **Durchsatz** | Mpps value (Bpps for the big chassis) |
| Stacking — VSF / VSX / IRF / backplane-ring (member count + bandwidth) | **Stacking** | holds the stacking technology + member/bandwidth, same as Cisco StackWise values |
| Form factor / rack units / DIN-rail / fanless | **Bauform** | RU + chassis/desktop/DIN string |
| Power supplies (internal / dual hot-swap / external PSU, W) | **Stromversorgung** | PSU description, same form as Cisco |
| Cooling / airflow (front-to-back, reversible, fanless) | **Kühlung** | airflow string |
| Target use (campus access / aggregation / data-center / industrial) | **Anwendung** | `Campus`, `Data-Center`, `Industrial` … (same Wertliste as Cisco) |
| Operating temperature range (incl. industrial −40…+70 °C) | **Betriebstemperatur** | covers the CX 4100i / rugged ranges too |
| **Chassis:** line-card / module slot count (+ supervisor/fabric slots) | **Steckplätze** | e.g. `5` (CX 6405), `10` (CX 6410), `12` (5412R), `4/8/12` (10500) |
| **Chassis:** supported management / supervisor / fabric modules | **Unterstützte Supervisor-Engines** | the mgmt/fabric module PIDs (e.g. CX 6400 R0X31A; 8400 JL367A/JL368A; 10500 MPU) |
| **Chassis:** supervisor / PSU / fabric / fan redundancy + VSX HA | **Redundanz** | redundancy string, same form as the Cisco chassis |
| **Module:** line card / fabric / management / uplink-expansion type | **Modultyp** | the module class |
| **Module:** compatible host chassis / series | **Kompatible Serie** | e.g. `CX 6405 / 6410`, `5406R / 5412R zl2`, `FlexNetwork 10500` |

## Feature edge-cases → PROSE, not Merkmale (consistent with how Cisco features are handled)
- **MACsec** (on many CX / 5930 / 5940 / AOS-S modules): a security feature. The Cisco switch bundles carry **no MACsec Merkmal** → handle in Beschreibung/Anwendung prose. **No new Merkmal.**
- **DPU / distributed-services** (CX 10000 / 10040 — embedded AMD Pensando stateful firewall/NAT/encryption/telemetry): a platform capability, not a switch dimension. → prose (Beschreibung), classified as a Switch via Anwendung=`Data-Center`. **No new Merkmal** (flag for sign-off if the operator wants a dedicated services Merkmal — OPEN-DECISION #6).
- **Routing-protocol depth, OpenFlow, VXLAN/EVPN, IP/MPLS, IEC-61850/IEEE-1613 (industrial), IP30 rating, PTP/AVB:** all feature/standard detail → prose; none is a Cisco switch Merkmal, so none becomes one here.

## STOP-AND-ASK (specs with NO existing Merkmal home)
**NONE.** Every measurable hardware spec maps to an existing Merkmal above; every remaining item is a feature/standard that the Cisco lane already treats as prose. **Therefore STEP-2 needs no new/renamed Merkmal** — confirming the operator's hard guardrail is satisfiable. (The only sign-off item touching Merkmale is the optional DPU-services question, OPEN-DECISION #6 — and the default is "prose, no new Merkmal".)
