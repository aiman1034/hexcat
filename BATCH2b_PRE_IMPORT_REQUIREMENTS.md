# HPE/Aruba STEP-2 BATCH-2b — PRE-IMPORT REQUIREMENTS  (the 22 deferred 6200 PIDs, now authored)

Resolves the batch-2 cache gap. The auditor couriered the live-HPE grounding (**a00059762enw**), and I
mirror-fetched the same QuickSpecs to verify/complete it. **All 22 formerly-deferred PIDs are now authored
and gate-clean:**
- **NEW bundle Aruba CX 6200M (10):** R8Q67A R8Q68A R8Q69A R8Q70A R8Q71A + TAA R8V08A R8V09A R8V10A R8V11A R8V12A.
- **EXTENDED Aruba CX 6200F 15 → 27 (+12):** S0M81A–S0M85A (1G-SFP), S0G13A–S0G17A (1G-SFP TAA), R8Q72A (12-port compact), R8V13A (TAA).

**Gate:** all 6 access bundles `ok=True viol=0`. **validate_dir = 0**. **Dedup:** whole switch tree 1117 SKUs, all unique.
Running HPE/Aruba switch total: batch-1 30 + batch-2/2b 53 = **83 authored** (the full CX access + 6300 tiers).

---

## A. One E3 category to create: `Aruba CX 6200M Switches`  (Netzwerk & Infrastruktur ▸ Switches)
Added to `config/rules.yaml` allowlist (additions-only). Create the JTL node before import. (The other 5 CX-access
E3 categories were already listed in the batch-2 note.)

## B. ⚠️ SwK DISCREPANCY — couriered 6200F-1G figures were WRONG; corrected from the authoritative QuickSpecs
Per your instruction ("replace any couriered SwK that the table contradicts — flag discrepancies"): the courier
listed the **6200F 1G-SFP** variants as 24-port = 56 Gbit/s, 48-port = 104. The authoritative a00059762enw
"Model switching capacity" table says they are **128 / 176 Gbit/s** — identical to their 10G-SFP+ siblings (the
rated model switching capacity is the ASIC total; it is NOT derated by uplink type, and 1G ports do not halve it).
**I used the doc values (128/176), not the courier's 56/104.** Throughput likewise 95,2 / 130,9 Mpps (not 41,6/77,3).
The 6200M figures couriered (128/176) MATCHED the doc and were used as-is.

## C. The 3 formerly-ZU_VERIFIZIEREN cells — now grounded from a00059762enw
- **R8Q71A / R8V12A** (6200M 36×1G + 12×SmartRate SR5 Class6 PoE): **SwK = 272 Gbit/s** / 130,9 Mpps (the multigig
  ports push it well above the 24-port 128 the courier speculated), Max PoE 1.440 W, weight 6,31 kg. **48-port switch**
  (courier mislabelled it 24-port).
- **R8Q72A** (6200F 12-port compact): **SwK = 68 Gbit/s** / 45,1 Mpps, 12×1G Class4 PoE + 2×1G + 2×SFP+, PoE 139 W,
  **fanless**, weight 3,24 kg, 0–45 °C.
- **R8V13A** (6200F 48×1G PoE 740 W 4×SFP TAA): TAA twin of S0M85A → **SwK = 176 Gbit/s** (no standalone table;
  electrically identical to S0M85A).

**Source:** HPE origin (hpe.com/psnow) was Akamai-blocked from this host; the identical doc was obtained from a
verbatim-OEM mirror — `kickstartcomputers.com.au/.../a00059762enw-1.pdf` — and text-extracted. Provenance URLs in the
content cite the canonical `hpe.com/psnow/doc/a00059762enw`.

## D. Prose correction carried into the 6200F bundle (re-emit)
The shared VSF sentence had hardcoded "bis zu **zehn** Einheiten" while the grounded Stacking value for 6200F/6200M
is **8 members**. Fixed: the prose member count now derives from the Stacking attribute (6200F/M = "acht", 6300L =
"zehn"). The re-emitted 6200F bundle (now 27 SKUs) carries the correction.

## E. NEW MERKMAL VALUES NEEDED  (17 — beyond Cisco ∪ batch-1 ∪ batch-2)
0 new Merkmal NAMES. New **values** only (the 6200M hot-swap PSU/fan + MACsec strings, the 6200F 1G-SFP + compact
port configs, the multigig Smart-Rate config). Categorical Merkmale (Switch-Typ/Layer/Bauform/Betriebstemperatur)
and Stacking/SwK/Durchsatz/Uplink reuse existing values.

### PoE — 2 NEW:
- `Ja (IEEE 802.3af/at Class 4, 30 W/Port, Budget bis 1.440 W netzteilabhängig)`
- `Ja (IEEE 802.3af/at/bt Class 6, 60 W/Port, Budget bis 1.440 W netzteilabhängig)`
### Port-Geschwindigkeit — 1 NEW:
- `10/100/1000 Mbit/s + 1/2.5/5 GbE Smart Rate (Access), 1/10 GbE (SFP+-Uplink)`
### Port-Konfiguration — 6 NEW:
- `12× 10/100/1000BASE-T (Class 4 PoE, 30 W) + 2× 1G-RJ45 + 2× SFP+ (1/10G) (Uplink)`
- `24× 10/100/1000BASE-T (Class 4 PoE, 30 W) + 4× SFP (1G) (Uplink)`
- `24× 10/100/1000BASE-T (ohne PoE) + 4× SFP (1G) (Uplink)`
- `36× 10/100/1000BASE-T (Class 6 PoE, 60 W) + 12× HPE Smart Rate 1/2.5/5G-BASE-T (Class 6 PoE, 60 W) + 4× SFP+ (1/10G) (Uplink)`
- `48× 10/100/1000BASE-T (Class 4 PoE, 30 W) + 4× SFP (1G) (Uplink)`
- `48× 10/100/1000BASE-T (ohne PoE) + 4× SFP (1G) (Uplink)`
### Stromversorgung — 1 NEW:
- `2 Hot-Swap-Netzteilslots (modular, N+1/N+N-Redundanz, mindestens 1 erforderlich, separat bestellt: JL085A 250 W / JL086A 680 W / JL087A 1050 W)`
### Kühlung — 1 NEW:
- `2 Hot-Swap-Lüftertray-Slots (1 inkl., je 2 Lüfter)`
### Anwendung — 6 NEW: (6200M ×4 incl. MACsec, 6200F-1G ×2 — see `output/.../Attributes.csv`)

**TOTAL BATCH-2b NEW WERTLISTE VALUES = 17**

## F. ZU_VERIFIZIEREN remaining (minor, auditor to confirm)
- **R8Q71A MACsec is partial on downlinks** (uplinks all; downlinks ports 37–48 only per the QuickSpec) — woven as a
  generic "MACsec-256" feature in the Anwendung; the port-range nuance is not a Merkmal.
- **6200M weights** (4,50–6,31 kg) — R8Q71A weight (6,31) is grounded; the other 6200M weights are sibling-consistent
  estimates (the QuickSpec section weights were not all captured) — low-risk logistics field, auditor may refine.

## G. Pricing — Phase-1 ESTIMATE only (flagged in VLog_Prices, as batch 1/2).

## H. Footprint
- NEW `output/switches/Aruba_CX_6200M_Switches/` (8-file bundle) + its `stage3_content/*.json`
- RE-EMITTED `output/switches/Aruba_CX_6200F_Switches/` (15 → 27) + its `stage3_content/*.json`
- `config/rules.yaml` (+1 E3 line) · `config/coverage/gate_completeness.yaml` (6200F 27/27 flags cleared, +6200M 10/10)
- `_scratch/aruba_cx_access_build.py` (driver) · `PROJECT_AUDIT.md` · this note
- **0 new Merkmal NAMES · 0 src/ changes · nothing created in JTL.**
