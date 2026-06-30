# HPE/Aruba STEP-2 BATCH-4 — PRE-IMPORT REQUIREMENTS  (CX high-end DC tail)

Each family enumerated against the **FULL ordering guide** (the 8325 lesson). **37 switch SKUs authored + gate-clean;
CX 10040 (6) deferred to batch-4b (§E).** Hersteller = **HP**. Prices = Phase-1 ESTIMATE. **0 new Merkmal NAMES.**
All bundles `ok=True viol=0`; **validate_dir = 0**; whole switch tree **1197 SKUs, all unique**. Switch total: **163**.

| Bundle | SKUs | SwK | Notes |
|---|---|---|---|
| Aruba CX 8360 | 18 (12 bundles + 6 base) | per-model 4.8/2.4/1.76/1.2/2.4/0.88 Tbit/s | **AC-only** (no DC/TAA — 18 = floor, not an expansion) |
| Aruba CX 9300 | 3 | **25.6 Tbit/s** | 32× QSFP-DD 400G spine; AC-only |
| Aruba CX 9300S | 8 | 16 Tbit/s | 32×100G + 8×400G; AC + BtF-DC; encryption+PTP in prose |
| Aruba CX 10000 | 4 | 3.6 Tbit/s | DSS, AMD Pensando DPU (in prose) |
| Aruba CX 8325 (+S1D) | +4 → **24** | 6.4 Tbit/s | S1D09-12A = DC-PSU TAA twins of JL857-860A |
| ~~Aruba CX 10040~~ | ~~6~~ DEFERRED | 8 Tbit/s | §E — clean OEM doc uncacheable |

## A. Five E3 categories (Netzwerk & Infrastruktur ▸ Switches ▸ …) — additions-only in rules.yaml
`Aruba CX 8360 / 9300 / 9300S / 10000 / 10040 Switches`. Create the JTL nodes (10040's node is pre-created for batch-4b).
(8325 unchanged — S1D09-12A go into the existing `Aruba CX 8325 Switches` bundle.)

## B. Capabilities encoded in PROSE, NOT Merkmale (the standing MACsec/DPU rule)
- **9300S:** line-rate MACsec/IPSec/VXLANsec encryption (6,4 / 4,8 Tbit/s) + PTP — woven into feat + Anwendung.
- **10000:** the **AMD Pensando DPU** / Distributed-Services (verteilte Stateful-Firewall, Ost-West-Segmentierung, NAT,
  Verschlüsselung, Telemetrie inline, 800 G über 2 DPUs) — woven into feat + Anwendung. No new Merkmal; VSX/L3 stay the Merkmale.

## C. NEW MERKMAL VALUES NEEDED (43 — 0 new Merkmal NAMES)
Switch-Typ (`Managed`), Layer (`L3`), Stacking (`VSX…`), PoE (`Nein`) all reuse existing values.
### Betriebstemperatur — 3 NEW: `0 bis 35 °C` · `0 bis 45 °C (Front-to-Back) bzw. 0 bis 35 °C (Back-to-Front)` · `0 bis 45 °C (Front-to-Back) bzw. 0 bis 40 °C (Back-to-Front)`
### Switching-Kapazität — 3 NEW: `1,2 Tbit/s` · `2,4 Tbit/s` · `16 Tbit/s`  *(25,6 / 6,4 / 4,8 / 1,76 / 0,88 Tbit/s already present — reused)*
### Durchsatz — 1 NEW: `5.000 Mpps`  *(2.000 Mpps reused; 8360/9300S = "Wire-Speed (… nicht ausgewiesen)" already present)*
### Port-Geschwindigkeit — 5 NEW · Uplink-Ports — 4 NEW · Port-Konfiguration — 9 NEW
  (25G/100G/200G/400G QSFP28/QSFP-DD DC configs + the homogeneous "alle N Ports flexibel" descriptors — see `output/.../Attributes.csv`)
### Stromversorgung — 6 NEW:
- `2 feldaustauschbare Hot-Swap-Netzteile (800 W AC, N+1, im Bundle)` (10000)
- `2 feldaustauschbare Hot-Swap-Netzteile (1500 W AC, N+1, im Bundle)` (9300)
- `2 feldaustauschbare Hot-Swap-Netzteile (1600 W AC, N+1, im Bundle)` (9300S-AC)
- `2 feldaustauschbare Hot-Swap-Netzteile (1600 W DC, -40/-75 V, N+1, im Bundle)` (9300S-DC)
- `Feldaustauschbare Hot-Swap-Netzteile (AC oder DC), separat bestellt (bis 2, N+1)` (9300S base)
- `Feldaustauschbare Hot-Swap-Netzteile, separat bestellt (bis 2, N+1); 1500 W AC` (9300 base)
### Kühlung — 3 NEW: `5 …Lüfter (Airflow back-to-front)` (8360-48Y6C BtF) · `6 …Hot-Swap-Lüfter (N+1, Airflow front-to-back / back-to-front)`
### Anwendung — 9 NEW: DC aggregation/spine/leaf strings incl. the 400G spine, the secure-DCI 9300S, and the DPU/DSS 10000 — see Attributes.

**TOTAL BATCH-4 NEW WERTLISTE VALUES = 43**

## D. Flag-don't-fabricate findings
- **8360 = AC-only** (all 4 PSU SKUs are AC; no DC/TAA bundle PIDs) → 18 SKUs = the floor, NOT a 8325-style expansion. Per-model SwK
  from the table; per-model Durchsatz absent (series 2.678/1.145 Mpps don't map per-model across the 0.88→4.8 Tbps spread) → wire-speed flagged.
- **9300-32D = 25.6 Tbit/s** (doc) — the manifest's 12.8 hint was a uni-directional misread; used the doc's 25.6.
- **9300 vs 9300S** are different ASICs: 9300-32D = uniform 32× QSFP-DD (400G spine, 25.6 Tbps); 9300S-32C8D = 32× 100G + 8× 400G
  (16 Tbps) + embedded line-rate encryption + PTP. **9300S DC ships Back-to-Front only** (no FtB-DC bundle).
- **8325 base/spare + S1D:** S1D09-12A confirmed as 8325-48Y8C/32C DC-PSU **TAA** bundles (QuickSpecs a00056519enw + HPE Store PID
  pages); the reseller "AC" tag on S1D10A/S1D12A was a mis-tag — used HPE-canonical DC.
- **R9F\* EXCLUDED** (integration-tracking SKUs, per operator) — none in scope.

## E. ⚠️ CX 10040 (6 PIDs) DEFERRED to batch-4b
S4R54A/S4R55A (32C6D FtB/BtF-AC), S4R56A/S4R57A (TAA), **S4R58A/S4R59A (FRU — incl. a TAA FRU not on the manifest)**. Grounded
*shape* (8 Tbit/s, 32× 100G QSFP28 + 6× 400G QSFP-DD + 2× 10G, 2U, 4× AMD Pensando Elba DPU, 3000 W AC, 0–40 °C, AC-only), but:
- The clean OEM QuickSpecs **a50004267enw is Akamai-blocked from this host** — only *reseller* mirrors (securewirelessworks + HPE
  Store titles) were reachable. Reseller specs have burned us before (6200F-1G SwK, S1D "AC" tags), so they are not authoritative.
- **Per-model weight and Durchsatz (Mpps) are un-groundable** from those sources (the "2.000 Mpps" appears carried over from the 10000).
- The **FRU SKUs (S4R58A/S4R59A)** are bare-chassis field-replacement units (no bundled PSU/fans) — recommend INCLUDE as switches but
  need operator sign-off.
**AUDITOR ACTION:** courier/cache the clean **a50004267enw** (residential IP) → batch-4b authors all 6 (the 10040 E3 node is already in rules.yaml).

## F. ZU_VERIFIZIEREN within the authored 37
- 8360 + 9300S per-model **Durchsatz (Mpps)** — not in the docs (wire-speed); a QuickSpecs Mpps would replace it.
- 8360 base-unit (JL717-722C), 9300/9300S base (R8Z96A/S0F96A/S0F95A) — switch-only, airflow configurable (PSU/fans separate).

## G. Pricing — Phase-1 ESTIMATE only (flagged `geschätzt-Tier (PLATZHALTER)` in VLog_Prices).

## H. Footprint
- NEW bundles `output/switches/Aruba_CX_{8360,9300,9300S,10000}_Switches/` + 4 `stage3_content/*.json` · RE-EMITTED `Aruba_CX_8325_Switches/` (+S1D, 20→24) + its content JSON
- `config/rules.yaml` (+5 E3) · `config/coverage/gate_completeness.yaml` (8325→24, +8360/9300/9300S/10000) · driver · PROJECT_AUDIT · this note
- **0 new Merkmal NAMES · 0 src/ changes · nothing created in JTL.**
