# HPE/Aruba STEP-2 BATCH-4b — PRE-IMPORT REQUIREMENTS  (CX 10040, deferred from batch 4)

The auditor couriered the full authoritative ordering guide **a50004267enw** (the doc this host couldn't reach in batch 4).
**4 complete AC bundles authored + gate-clean; the 2 FRU held pending an operator policy decision (§D).**
`ok=True viol=0`; **validate_dir = 0**; whole switch tree **1201 SKUs, all unique**. **8 new Wertliste values, 0 new Merkmal NAMES.**

## A. Authored — Aruba CX 10040 (4) into the existing `Aruba CX 10040 Switches` E3 (already in rules.yaml)
- `S4R54A` 10040-32C6D FtB-AC · `S4R55A` BtF-AC · `S4R56A` FtB-AC **TAA** (twin of S4R54A) · `S4R57A` BtF-AC **TAA** (twin of S4R55A)
- (The `#B2B/#B2C/#B2E/#AC3` suffixes are power-cord options of the SAME PID — not separate SKUs; not encoded.)

Grounded verbatim from a50004267enw: L3 · Managed · **2U** (19-Zoll-Rackmontage 2 HE) · VSX · **8 Tbit/s** · Port-Konfiguration
`32× 100G-QSFP28 (Access) + 2× 10G-SFP+ (Management) + 6× 400G-QSFP-DD (Uplink)` (Portanzahl **40**) · 2× 3000 W AC hot-swap (N+1) ·
4 hot-swap Lüftertrays · 0–40 °C · PoE Nein.

## B. DSS / DPU — in PROSE, NOT a Merkmal (the standing DPU/MACsec pattern)
Woven into the feature sentence + Anwendung: *Distributed-Services-Switch mit vier AMD-Pensando-DPUs; 1,6 Tbit/s verteilte
Stateful-Services (Firewall, Segmentierung, NAT, Telemetrie inline); portflexible 4,8-Tbit/s-Verschlüsselungs-Engine (MACsec);
PTP-Boundary-Clock; VXLAN-EVPN/BGP; Leaf-Spine/ToR/EoR.* No new Merkmal; VSX/L3 remain the Merkmale.

## C. NEW MERKMAL VALUES NEEDED (8 — 0 new Merkmal NAMES)
Switch-Typ (`Managed`), Layer (`L3`), Stacking (`VSX…`), Betriebstemperatur (`0 bis 40 °C`), PoE (`Nein`), Bauform (`…2 HE`),
Durchsatz (`Wire-Speed…`) all reuse existing values.
- **Switching-Kapazität — 1 NEW:** `8 Tbit/s`
- **Stromversorgung — 1 NEW:** `2 feldaustauschbare Hot-Swap-Netzteile (3000 W AC, N+1, im Bundle)`
- **Kühlung — 2 NEW:** `4 feldaustauschbare Hot-Swap-Lüftertrays (N+1, Airflow front-to-back / back-to-front)`
- **Port-Geschwindigkeit / Uplink-Ports / Port-Konfiguration — 1 each:** the 100G/400G + management-SFP+ DSS strings (see Attributes).
- **Anwendung — 1 NEW:** the 10040 DSS/DPU string.

## D. ✅ OPERATOR DECISION — the 2 FRU (S4R58A / S4R59A): INCLUDE (resolved)
The operator chose **INCLUDE as sealed-switch FRU** (consistent with the base/spare units authored for 8325/8360/9300).
`S4R58A` + `S4R59A` (TAA) are now authored as **bare-chassis 10040-32C6D switch units** — configurable airflow, PSU/fans ordered
separately (prose: "Netzteile/Lüftertrays separat bestellt"); they carry the same 8 Tbit/s / wire-speed / weight-estimate
ZU_VERIFIZIEREN flags as the bundles. **CX 10040 is now 6/6** in `gate_completeness.yaml` (4 AC bundles + 2 FRU).

## E. ZU_VERIFIZIEREN (flagged, shipped on best grounding)
- **Artikelgewicht = 15,00 kg (ESTIMATE, 2U-class)** — the doc's Technical-Specs weight was not in the courier; flagged for the
  auditor to replace with the verbatim figure (the Phase-1 estimate, like the prices, is clearly marked).
- **Durchsatz** — wire-speed (no per-model Mpps published; the 10000's 2.000 Mpps was deliberately NOT carried over).
- **Kühlung fan count** — defaulted to **4** per the product name; the doc's BtF=6 is a likely typo carried from the 10000 (flagged).
- **2× 10G-SFP+** modeled as **Management** ports (mirrors the 9300-32D); confirm data-vs-mgmt if the auditor's table differs.

## F. Pricing — Phase-1 ESTIMATE only (flagged `geschätzt-Tier (PLATZHALTER)` in VLog_Prices).

## G. Footprint
- NEW `output/switches/Aruba_CX_10040_Switches/` + `stage3_content/Aruba_CX_10040_Switches_content.json`
- `config/coverage/gate_completeness.yaml` (+10040 4/4 + held-FRU comment) · driver · PROJECT_AUDIT · this note
- **0 new Merkmal NAMES · 0 src/ changes · 0 rules.yaml change** (E3 already present) · nothing created in JTL.
