# HPE/Aruba STEP-2 — FIXED-LINE COMPLETENESS SWEEP — PRE-IMPORT REQUIREMENTS (2026-06-30)

Re-enumerated all 17 fixed CX families against the **AOS-CX Release Notes "Products Supported" table** (the deepest SKU
source — it is what surfaced the 8325 S1D and the 9300S FtB-DC twins), cross-checked the QuickSpec/ordering guide, IGSG
install guides, and buy.hpe.com. **28 net-new in-scope switch SKUs authored**; 13 families confirmed complete; all gate-clean.

`ok=True viol=0`; **validate_dir = 0** on every touched bundle; whole switch tree **1233 SKUs, all unique**.
**21 new Wertliste VALUES, 0 new Merkmal NAMES, 0 new E3 (no rules.yaml change), 0 src/.**

## A. Per-family before → after (only 4 families gained SKUs)
| Family | Before | After | Net-new |
|---|---|---|---|
| Aruba CX 6000 | 6 | **22** | +16 |
| Aruba CX 6100 | 5 | **6** | +1 |
| Aruba CX 6300M | 22 | **30** | +8 |
| Aruba CX 6300L | 3 | **6** | +3 |
| 6200F · 6200M · 6300F · 8100 · 8320 · 8325 · 8325H · 8360 · 9300 · 9300S · 10000 · 10040 · 4100i | — | — | **0 (confirmed complete)** |

All four gaining families add to **existing E3 categories** — no new JTL category needed.

## B. The 28 net-new SKUs
**CX 6000 (+16):**
- **6 "B"-rev** (silicon refresh of the A-units, identical specs/caps/weights): R9Y03B, R8N85B, R8N86B, R8N87B, R8N88B, R8N89B
- **6 TAA twins** of the 48/24/12-port tiers: S4R20A, S4R24A, S4R25A, S4R26A, S4R27A, S4R21A
- **NEW 8-port tier (4):** S4R22A (8G non-PoE), S4R23A (8G Class-4 PoE 67 W), + TAA twins S4R28A, S4R29A

**CX 6100 (+1):** R9Y04A — 740-W-PoE twin of JL675A (370 W); cap 176 Gbit/s grounded.

**CX 6300M (+8):** the **S4P41A–S4P48A "2L 2Y" MACsec sub-family** (uplinks 2× SFP56 50G + 2× SFP28 25G), 4 configs × non-TAA/TAA,
incl. a **new 32-port density** (S4P41/42/45/46). Titles grounded from buy.hpe.com + the 6300 IGSG. MACsec is in the port/Anwendung
prose, not a Merkmal.

**CX 6300L (+3):** the TAA tier S2P49A, S2P50A, S2P51A — TAA twins of S3L75A/76A/77A.

## C. NEW WERTLISTE VALUES (21 — 0 new Merkmal NAMES)
- **Switching-Kapazität — 1 NEW:** `ZU_VERIFIZIEREN` (the 8-port 6000 tier + the 6300M S4P4x — see §D)
- **Durchsatz — 1 NEW:** `ZU_VERIFIZIEREN`
- **PoE — 3 NEW:** `…Class 4, 30 W/Port, Budget 67 W` · `…Class 8, 90 W/Port auf den 16 Smart-Rate-Ports, Budget ZU_VERIFIZIEREN` ·
  `…Class 8, 90 W/Port auf den 32 Smart-Rate-Ports, Budget ZU_VERIFIZIEREN`
- **Port-Konfiguration — 6 NEW:** the two 8-port 6000 strings + the four S4P4x strings (32+16 SR, 32 SR+8 LRM, 48 SFP, 24 SFP — all + 2×50G/2×25G)
- **Port-Geschwindigkeit — 3 NEW** · **Anwendung — 7 NEW** (the new 8-port, 6100-740W, and the four S4P4x/SFP application strings)
- (Uplink-Ports / Stromversorgung / Kühlung / Bauform / Betriebstemperatur — all reused.)

## D. ⚠️ ZU_VERIFIZIEREN (shipped on best grounding; auditor to confirm — flag-don't-fabricate, never port-math)
1. **CX 6000 8-port tier (S4R22A/23A/28A/29A) — Switching-Kapazität + Durchsatz** not published (new density, no sibling to
   analogize). Emitted as `ZU_VERIFIZIEREN` (graceful prose: "…herstellerseitig noch nicht ausgewiesen").
2. **CX 6300M S4P4x (S4P41-48A) — Switching-Kapazität + Durchsatz + PoE-Budget watts** not published per-model. Caps =
   `ZU_VERIFIZIEREN`; titles/ports/Class-8-tier grounded from buy.hpe.com.
3. **CX 6300L TAA (S2P49A/50A/51A) — exact verbatim EN bundle title** (the IGSG carries only an abbreviated form; specs taken
   from the confirmed non-TAA twin). German artikelname is built from the twin's config + the TAA tag.
4. **CX 6100 R9Y04A — internal PSU wattage** not published (cap + 740 W PoE budget are grounded) → generic PSU phrasing.

## E. Held / out-of-scope (with reason)
- **CX 8360 R9G\* "Attached Bundle" (12 PNs)** — physically identical to the JL…C bundles already in catalog (HPE's newer
  bundle-PN scheme). Held as `duplicate` per the "redundant dup bundles" exclude rule. (Reversible to PN-twins on request.)
- **S1T83A** — resolved: it is a **CX 6400 module** (line card), not a 6300M switch → belongs to the future CX 6400 chassis/module
  lane, correctly excluded here.

## F. Pricing — Phase-1 ESTIMATE only (flagged `geschätzt-Tier (PLATZHALTER)` in VLog_Prices) on all 28 new SKUs.

## G. Footprint
- RE-EMITTED `output/switches/Aruba_CX_{6000,6100,6300L,6300M}_Switches/` + their 4 `stage3_content/*.json`
- `config/coverage/gate_completeness.yaml` (6000→22, 6100→6, 6300L→6, 6300M→30) · 2 build drivers (scratch) · PROJECT_AUDIT · this note
- **0 new Merkmal NAMES · 0 new E3 / 0 rules.yaml change · 0 src/ change** · nothing created in JTL.
