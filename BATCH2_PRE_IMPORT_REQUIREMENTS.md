# HPE/Aruba STEP-2 BATCH-2 — PRE-IMPORT REQUIREMENTS  (CX access tier)

**Planned scope:** CX 6000 (6) · 6100 (5) · 6200F (27) · 6200M (10) · 6300L (3) · 4100i (2) = **53 PIDs**.
**Authored + gate-clean this batch: 31 PIDs (5 bundles).  Deferred (flag-don't-fabricate): 22 PIDs — see §E.**
Reuses the proven batch-1 pipeline verbatim. Hersteller = **HP**. Grounded verbatim from the cached current
per-family datasheets, CITED. Prices = **Phase-1 ESTIMATE** (flagged). 0 new Merkmal NAMES.

**Gate:** all 5 emitted bundles `ok=True viol=0`. **validate_dir = 0** each. **Dedup:** whole switch tree
1095 SKUs, all unique (A-rev/B-rev/TAA twins distinct via PID-welding).

| Bundle | SKUs | Doc (cached, current) | Class token | Layer |
|---|---|---|---|---|
| Aruba CX 6000 Switches | 6 | a00112996enw | Managed Switch (L2) | L2 |
| Aruba CX 6100 Switches | 5 | a00106853enw | Managed Switch (L2) | L2 |
| Aruba CX 6200F Switches | 15 / 27 | a00097415enw | Managed Switch (L2) | L2 |
| Aruba CX 6300L Switches | 3 | a00085162enw | Managed Switch (L2) | L2 |
| Aruba CX 4100i Switches | 2 | a00117285enw | **Industrie-Switch** | L2 |

---

## A. Five E3 categories to create  (Netzwerk & Infrastruktur ▸ Switches ▸ …)
`Aruba CX 6000 Switches` · `Aruba CX 6100 Switches` · `Aruba CX 6200F Switches` · `Aruba CX 6300L Switches`
· `Aruba CX 4100i Switches`. (Added to `config/rules.yaml` allowlist, additions-only. **`Aruba CX 6200M
Switches` is NOT yet created** — that family is deferred, see §E.) Create these 5 JTL category nodes before import.

## B. PoE risk-test — PASS (no new Merkmal)
The existing `PoE` Merkmal again holds every value, incl. the 4100i's mixed-class industrial budgets
(`4× Class 6 60 W + 8× Class 4 30 W; PoE-Budget netzteilabhängig 50–360 W`). 0 STOP-and-ask. 0 new Merkmal NAMES.

## C. NEW MERKMAL VALUES NEEDED  (59 — add to live Wertlisten before import)
NAMES 100 % reused (locked 15 fixed-switch Merkmale). NEW **values** only; these are NOT in the Cisco bundles
NOR in batch-1's 63.

> ✅ **Switch-Typ · Layer · Portanzahl · Betriebstemperatur — 0 new** (reused: `Managed`, `L2`, `16/28/52`,
> and notably `-40 bis 70 °C` already exists from the Cisco IE industrial bundles).

### Bauform — 3 NEW:
- `19-Zoll-Rackmontage (1 HE, industrielles IP30-Modell); wandmontierbar`
- `DIN-Schienen-Montage (Hutschiene, IP30); 19-Zoll-Montage über Kit JL822A`
- `Kompakt (lüfterlos, halbe Breite); 19-Zoll-Montagekit`

### Switching-Kapazität — 1 NEW: `64 Gbit/s`  *(104/56/32/176/128/68/780/720/128 already present or added here)*
### Durchsatz — 5 NEW: `41,6 Mpps` · `45,1 Mpps` · `46 Mpps` · `77,3 Mpps` · `98,6 Mpps`
### Stacking — 2 NEW:
- `Ja (Aruba VSF, bis 8 Einheiten, über die 10G-SFP+-Uplinks)`
- `Ja (Aruba VSF-Front-Plane-Stacking, bis 10 Einheiten, 200 Gbit/s; stackt nicht mit 6300F/6300M)`
  *(`Nein` reused for 6000/6100/4100i.)*

### PoE — 5 NEW:
- `Ja (IEEE 802.3af/at Class 4, 30 W/Port, Budget 139 W)`
- `Ja (IEEE 802.3af/at Class 4, 30 W/Port, Budget 370 W)`
- `Ja (IEEE 802.3af/at Class 4, 30 W/Port, Budget 740 W)`
- `Ja (IEEE 802.3af/at/bt; 4× Class 6 60 W + 20× Class 4 30 W; Budget 240 W, internes 300-W-Netzteil)`
- `Ja (IEEE 802.3af/at/bt; 4× Class 6 60 W + 8× Class 4 30 W; PoE-Budget netzteilabhängig 50–360 W)`

### Port-Geschwindigkeit — 2 NEW:
- `10/100/1000 Mbit/s (RJ45, Access), 1 GbE (SFP-Uplink)`
- `10/100/1000 Mbit/s (RJ45, Access), 1/10 GbE (SFP+-Uplink)`

### Uplink-Ports — 3 NEW: `2× 1G-RJ45 + 2× SFP (1G)` · `2× 1G-RJ45 + 2× SFP+ (1/10G)` · `2× SFP+ (1/10G)`

### Port-Konfiguration — 16 NEW:
- `12× 1G-RJ45 (10/100/1000BASE-T, Class 4 PoE, 30 W) + 2× 1G-RJ45 + 2× SFP (1G) (Uplink)`
- `12× 1G-RJ45 (10/100/1000BASE-T, Class 4 PoE, 30 W) + 2× 1G-RJ45 + 2× SFP+ (1/10G) (Uplink)`
- `24× 10/100/1000BASE-T (Class 4 PoE, 30 W) + 4× SFP+ (1/10G) (Uplink)`
- `24× 10/100/1000BASE-T (ohne PoE) + 4× SFP+ (1/10G) (Uplink)`
- `24× 1G-RJ45 (10/100/1000BASE-T, Class 4 PoE, 30 W) + 4× SFP (1G) (Uplink)`
- `24× 1G-RJ45 (10/100/1000BASE-T, Class 4 PoE, 30 W) + 4× SFP+ (1/10G) (Uplink)`
- `24× 1G-RJ45 (10/100/1000BASE-T, ohne PoE) + 4× SFP (1G) (Uplink)`
- `24× 1G-RJ45 (10/100/1000BASE-T, ohne PoE) + 4× SFP+ (1/10G) (Uplink)`
- `48× 10/100/1000BASE-T (Class 4 PoE, 30 W) + 4× SFP+ (1/10G) (Uplink)`
- `48× 10/100/1000BASE-T (ohne PoE) + 4× SFP+ (1/10G) (Uplink)`
- `48× 1G-RJ45 (10/100/1000BASE-T, Class 4 PoE, 30 W) + 4× SFP (1G) (Uplink)`
- `48× 1G-RJ45 (10/100/1000BASE-T, Class 4 PoE, 30 W) + 4× SFP+ (1/10G) (Uplink)`
- `48× 1G-RJ45 (10/100/1000BASE-T, ohne PoE) + 4× SFP (1G) (Uplink)`
- `48× 1G-RJ45 (10/100/1000BASE-T, ohne PoE) + 4× SFP+ (1/10G) (Uplink)`
- `4× 100M/1G-RJ45 (Class 6 PoE, 60 W) + 20× 100M/1G-RJ45 (Class 4 PoE, 30 W) + 4× SFP+ (1/10G) (Uplink)`
- `4× 100M/1G-RJ45 (Class 6 PoE, 60 W) + 8× 100M/1G-RJ45 (Class 4 PoE, 30 W) + 2× SFP+ (1/10G) (Uplink)`

### Stromversorgung — 6 NEW:
- `Externe industrielle DIN-Rail-Netzteile JL819A/JL820A/JL821A (2 für Redundanz, separat); AC oder DC`
- `Internes Festnetzteil (nicht hot-swap, nicht feldaustauschbar)`
- `Internes Festnetzteil 65 W (nicht hot-swap, nicht feldaustauschbar)`
- `Internes Festnetzteil 165 W (nicht hot-swap, nicht feldaustauschbar)`
- `Internes Festnetzteil 300 W (240 W PoE-Budget; AC 100–240 V)`
- `Internes Festnetzteil 500 W (nicht hot-swap, nicht feldaustauschbar)`

### Kühlung — 2 NEW: `Feste Lüfter (nicht austauschbar)` · `Lüfterlos (passiv gekühlt, IP30)`

### Anwendung — 14 NEW: (per-SKU descriptive — see `output/.../Attributes.csv`; 6000/6100 entry-access ×4,
compact ×2, 6200F campus ×3, 6300L L2 ×3, 4100i industrial ×2)

**TOTAL BATCH-2 NEW WERTLISTE VALUES = 59**

---

## D. Grounding findings (flag-don't-fabricate — per-family, doc-grounded)
- **CX 6000 / 6100 = NO VSF stacking** (`Stacking = Nein`, grounded — entry tier); L2 + static routing; internal
  FIXED PSU; 12-port models (R8N89A/JL679A) are **fanless/compact**. SwK 104/56/32 (6000), 176/128/68 (6100).
- **CX 6300L = Layer 2** (the licensed-L2 variant of the 6300M); hot-swap PSU/fans; **own VSF domain** (8-/10-member
  front-plane, 200 Gbps; does NOT stack with 6300F/6300M). SwK 780/780/720.
- **CX 4100i = industrial (IP30)**, `Industrie-Switch` class, DIN-rail (JL817A) / 19-in IP30 (JL818A), **fanless,
  −40…70 °C**, mixed-class PoE. SwK 64/128. (Reuses the existing `-40 bis 70 °C` Betriebstemperatur value.)
- **CX 6200F = FIXED-PSU L2** (the F-vs-M split, like 6300): internal fixed PSU (200/500/950 W), fixed fans, VSF
  8-member. SwK 128 (24p) / 176 (48p), throughput 95,2 / 130,9 Mpps — verbatim from the cached A-rev sheet.

## E. ⚠️ DEFERRED — 22 PIDs NOT authored (CACHE GAP — auditor action needed)
> ✅ **RESOLVED in BATCH 2b** (auditor couriered a00059762enw): all 22 are now authored — 6200M (10) as a new bundle,
> 6200F extended 15→27. See `BATCH2b_PRE_IMPORT_REQUIREMENTS.md`. (Note: the couriered 6200F-1G SwK 56/104 was corrected
> to the doc's authoritative 128/176.) The text below is the historical batch-2 state.
**Root cause:** the cached `datasheets/cache/hpe-aruba/6200F.pdf` is the **wrong/older doc — `a00097415enw`
(2022, 6200F-only A-rev, only JL724A–728A)**, NOT the `a00059762enw` the manifest assumed. The current combined
**6200F+6200M** datasheet (B-rev, S-prefix, 1G-SFP variants, compact, AND the entire 6200M) is **not cached
anywhere** (verified across the cache dir + Downloads). Per flag-don't-fabricate the agents refused to invent
specs; these are flagged, not filled:

- **CX 6200F (12):** S0M81A–S0M85A, S0G13A–S0G17A (the **4× SFP / 1G-uplink** variants — different uplink → different
  switching capacity, so the SFP+ base numbers must NOT be copied), R8V13A (TAA 1G-SFP), R8Q72A (12-port compact —
  absent). Recorded in `gate_completeness.yaml` as `flagged` with `reason_code: harvest-gap` (15 captured / 27 enumerated).
- **CX 6200M (10):** R8Q67A–R8Q71A + R8V08A–R8V12A — the entire family. **No bundle emitted** (hot-swap modular PSU,
  higher PoE, Class-6 multigig on R8Q71A — none groundable from the cached 6200F-only A-rev sheet).

**To complete:** cache the current **`a00059762enw`** (combined 6200F + 6200M QuickSpecs/datasheet) → I author the
22 in a follow-up (batch 2b) through the same pipeline. The 6200F bundle then extends 15 → 27 and a 6200M bundle is added.

## F. ZU_VERIFIZIEREN within the authored 31 (auditor to confirm; specs shipped on best grounding)
- **4100i Stacking = Nein** — the datasheet has no VSF/stacking section for the industrial line; grounded by absence.
- **6200F B-rev (JL724B–728B)** — specs inherited from the A-rev (datasheet publishes no separate B-rev table; A/B is a
  hardware revision of the same model). **6200F TAA twins (S0M86A–S0M90A)** — specs inherited from their base PID
  (TAA = sourcing-only delta, same hardware) — consistent with batch-1 TAA handling.

## G. Pricing — Phase-1 ESTIMATE only (NOT grounded)
Tier-based placeholder Netto-VK; `Verification_Log_*_Prices.csv` flags `Methode = "geschätzt-Tier (PLATZHALTER)"`.
Real HPE market-price research is a separate later phase.

## H. Footprint (this batch changed ONLY:)
- 5 bundles `output/switches/Aruba_CX_{6000,6100,6200F,6300L,4100i}_Switches/` + their 5 `stage3_content/*.json`
- `config/rules.yaml` — 5 additions-only allowlist lines
- `config/coverage/gate_completeness.yaml` — 5 records (incl. 6200F 15/27 + 12 harvest-gap flags)
- `_scratch/aruba_cx_access_build.py` (build driver) · `PROJECT_AUDIT.md` · this note
- **0 new Merkmal NAMES · 0 src/ changes · nothing created in JTL.**
