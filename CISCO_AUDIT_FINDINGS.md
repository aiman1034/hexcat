# Cisco Switch Catalog — Deep Find-Mistakes Audit (report-only)

**Date:** 2026-06-29 · **Auditor:** Claude Code (independent pass for L8 cross-verify) · **No fixes applied.**
**Method:** in-place reads of every Cisco bundle in `output/switches/` (no gate temp-copies; disk ~full).
Authoritative byte-contract read from `src/hexcat/writers.py` + `constants.py`; Merkmal set from
`constants.SWITCH_ATTRIBUTE_NAMES_ORDERED`.

---

## 1. SCOPE

**113 Cisco bundles, 995 SKUs** — reconciles exactly to the manifest's 995 built.

> ⚠️ The count only reconciles once you include `output/switches/Cisco/` (the Catalyst 9300 bundle, 40 SKUs,
> named at brand-level not `Cisco_9300`). A naïve `Cisco_*` family glob enumerates **112 bundles / 955 SKUs**
> and silently drops the 40 C9300. See **MAJOR-1**. Every emitted PID is in the manifest; no emitted-but-unlisted.

Class split: **fixed** 92 bundles · **modular chassis** 11 bundles (4500E, 6500E, 6807XL, C9610, Catalyst_9400,
Catalyst_9600, Nexus_7000, Nexus_7700, Nexus_9400, Nexus_9500, Nexus_9800) · **modules** 4 lanes (Cat4500E 22,
Cat6500 29, Cat6800X 2, Nexus7000 43) · **SAN/FC** 5 bundles (MDS_9700/MS/S/T/V, 13 SKUs).

---

## 2. PER-BUNDLE ROLLUP

**108/113 bundles structurally PASS** (`validate_dir` 0 errors across the whole tree; gate was green at build).
Issues are localized:
- **77 bundles** — Prices.csv bare-LF instead of CRLF (MINOR-1).
- **5 MDS bundles** (13 SKUs) — Ebene-2 `SAN & Fibre Channel` outside the sanctioned switch set (MAJOR-3).
- **1 bundle** (`Cisco/`) — brand-level naming (MAJOR-1).
- **5 chassis bundles** — Class-A schema vs the other 6 (MAJOR-2).
- Scattered MINOR Wertliste-fragmentation members across ~20 bundles (MINOR-2).

---

## 3. CATALOG ISSUES — SEVERITY-RANKED

### CRITICAL — none
No fabrication, no un-flagged placeholder, no dedup collision, no exclusion violation, no inferred/ZU_VERIFIZIEREN
PID shipped as a primary key, **no cross-field factual contradiction** (the 4948E class is the only one of its
kind and is fixed). Dedup: 0 PID collisions across all 113 bundles. Exclusion: 0 `-RF`/REMAN/refurb/license/
CarePack/NFR/eval/demo PIDs; `XFP10GER192IRRGDRF` absent. Price: all 995 priced, all German-decimal ungrouped.

### MAJOR

**MAJOR-1 — Catalyst 9300 bundle is named `output/switches/Cisco/` (brand-level), not `Cisco_9300/`.**
40 SKUs (C9300/C9300L/C9300LM/C9300X), all `Hexwaren_Cisco_Switches_*`. The data is correct and imports fine,
but the name breaks any `Cisco_<family>` glob — *this audit's first pass undercounted 955/112 until the bundle
was found via the manifest gap*. Same risk for the manifest top-scan and any per-family automation.
**Recommend:** rename dir to `Cisco_9300` (or `Cisco_Catalyst_9300`) + re-key its files, OR confirm intentional.

**MAJOR-2 — Modular-chassis class is modeled two different ways (known; operator flagged during the 9800 build).**
- **Class-A** (`Switch-Typ='Modular-Chassis'` + `Layer` + `Steckplätze`/`Unterstützte Supervisor-Engines`/`Redundanz`):
  `Cisco_4500E, Cisco_6500E, Cisco_6807XL, Cisco_Nexus_7000, Cisco_Nexus_7700` — **19 SKUs**.
- **Production** (`Switch-Typ='Managed'`, 7-attr, no Class-A Merkmale):
  `Cisco_Catalyst_9400, Cisco_Catalyst_9600, Cisco_C9610, Cisco_Nexus_9400, Cisco_Nexus_9500, Cisco_Nexus_9800` — **11 SKUs**.
Same device class → two JTL attribute shapes (`Modular-Chassis` appears as a Switch-Typ Wertliste value; Steckplätze/
Redundanz/Supervisor-Engines exist on only 19 SKUs). Catalog-wide normalization is a separate operator decision.

**MAJOR-3 — MDS (SAN/Fibre-Channel) uses an Ebene-2 outside the sanctioned switch set.**
13 SKUs across MDS_9700/MS/S/T/V carry **Ebene-2 = `SAN & Fibre Channel`** (allowed set is
{Switches, Transceiver & Kabel, Switch-Module & Komponenten}). It is a *coherent* separate class — fixed FC switches
(E3 `Fibre-Channel-Switch`) use the switch schema **minus Layer** (correct: FC has no Ethernet L2/L3), and the
MDS_9700 directors (E3 `Fibre-Channel-Director`) use the **chassis 7-attr pattern**. Decisions needed:
(a) confirm `SAN & Fibre Channel` is an intended live JTL category (then add it to the audit's allowed set);
(b) confirm the FC directors should keep E3 `Fibre-Channel-Director` rather than `Modularer Switch (Chassis)`.

**MAJOR-4 — Switch weight-provenance traceability gap (532/995).** *(Operator-HELD: traceability/process, not a
correctness defect.)* The central weight configs (`grounded_weights.yaml`, `weight_disposition.yaml`) are
**transceiver-only** (Formfaktor buckets); **switch** weights are authored into the content/Main and echoed to the
per-SKU VLog for only **463/995** SKUs — **532/995 carry no per-SKU weight source in the deliverable**, so an auditor
cannot verify them from the emitted artifacts alone.
> **RETRACTED — the C9500-Y4C "sibling-graft" was a FALSE POSITIVE.** The L8 courier fetched the **live Catalyst 9500
> Hardware Installation Guide → Technical Specifications, Table 3**: `C9500-48Y4C` = 21.96 lb (**9,96 kg**),
> `C9500-24Y4C` = 20.99 lb (**9,52 kg**) — Cisco publishes both and they **match the catalog exactly**. No graft; the
> weights are correct + grounded. (My verify agent 403'd to direct fetch and used a Wayback snapshot that omitted the
> HIG physical-spec table, hence its "no Y4C weight published" conclusion.) Provenance now recorded in the VLog (FIX 3).
The systematic 532/995 gap remains as a process question for the operator (per-SKU VLog row vs a central
`grounded_weights`-style record for switch weights) — **not** evidence of wrong values.

### MINOR

**MINOR-1 — Prices.csv line-ending is inconsistent: 77 bundles bare-LF, 36 CRLF (of 113).**
The locked contract (`writers.write_csv`, `LINE_TERMINATOR="\r\n"`) is **CRLF for every file**; the 77 LF Prices were
written by ad-hoc price emitters (`\n`). The gate reads via `splitlines()` so it is line-ending-agnostic (that's why
the split passed); Ameise on Windows tolerates both → **not import-breaking**, but off-contract and internally
inconsistent. `Verification_Log_*_Prices.csv` are uniformly CRLF. **Recommend:** re-emit all Prices via
`writers.write_csv`. *(NB: the directive's "Prices … LF" wording conflicts with the `writers.py` CRLF contract —
worth reconciling which is canonical; either way the output should be uniform.)*

**MINOR-2 — Wertliste fragmentation (same value, trivial variant → two JTL entries).**
- **PoE & Stacking** — an en-dash (`0x2013`) is dropped to a double-space in one variant: `Ja – PoE+ …` vs `Ja  PoE+ …`
  (e.g. MS120 vs 3560C); `Ja – Cisco StackWise Plus …` (3750E vs 3750X). Invisible-char fragmentation.
- **Betriebstemperatur** — `-40 bis +70 °C` (MS130R) vs `-40 bis 70 °C` (IE1000/IE2000, ×27) — the `+`.
- **Port-Geschwindigkeit** — `1G/2,5G (Uplink 10G)` (×4) vs `1G/2.5G (Uplink 10G)` (IE9300) — comma vs dot (German-decimal).
- **Port-Konfiguration** — `16/24/32/40 10G SFP+` (Cisco_4500X, space) vs `… 10G-SFP+` (modules/9500, hyphen).
- **Uplink-Ports** — `2 40G QSFP` (6800X) vs `2 40G-QSFP+`; `4× 10G-SFP+ (oder 4× 1G-SFP)` vs `… oder …` (paren) within Cat4500E_Modules.
- **Switching-Kapazität** — Cisco_350 systematic trailing `,0` (`20,0`/`56,0`/`104,0`/`62,0` vs the integer used everywhere else); Nexus9200 `6,0 Tbit/s` vs `6 Tbit/s`.
- **Switching-Kapazität representation** — the *same* value as Tbit vs grouped-Gbit vs ungrouped-Gbit: `1,28 Tbit/s` / `1.280 Gbit/s` / `1280 Gbit/s`; `1,44 Tbit/s` / `1.440 Gbit/s`; `0,64 Tbit/s` / `640 Gbit/s`. Inconsistent unit choice AND dot-thousands-grouping.
- **⚠️ HIGH-PRIORITY — C9300X capacity uses an ambiguous 3-decimal German form:** `C9300X-48HX`/`-48TX` = `1,760 Tbit/s`,
  `C9300X-12Y` = `1,000 Tbit/s`, `C9300X-24Y` = `2,000 Tbit/s`. Under strict German comma-decimal these equal 1.76 / 1.0 /
  2.0 Tbit/s (= 1760 / 1000 / 2000 Gbit/s — values **confirmed correct** by the re-fetch), but `1,000 Tbit/s` / `2,000 Tbit/s`
  read as 1000×/2000× to anyone not applying German parsing, and the 3-decimal form breaks the catalog's 2-decimal norm
  (`1,28`/`25,6`/`115,2 Tbit/s`). Render as `1,76`/`1`/`2 Tbit/s` or `1760`/`1000`/`2000 Gbit/s`. (Borderline MAJOR — customer-facing misread risk.)
- **Durchsatz** — trailing 2-decimal vs 1-decimal: `11,90` vs `11,9`; `238,10` vs `238,1` (Cisco_1200/1300).

**MINOR-3 — `oder` alternatives inside Merkmal values (review vs S.3 discipline).** Gate passed all. Strongest:
Cat4500E_Modules **Uplink-Ports** `… (oder 4× 1G-SFP)` (alternative configs in a Merkmal). More defensible:
combo/unified-port descriptions in Port-Konfiguration/Port-Geschwindigkeit (Nexus 5500/5600, IE3000 — "Kupfer oder
SFP", "Ethernet/FCoE oder FC", "40G nativ oder Breakout") and `AC oder DC` in Stromversorgung. Confirm whether the
operator's no-alternatives-in-a-Merkmal rule applies here.

**MINOR-4 — VLog internal column quirk (cosmetic; VLog not imported).** For `extra_log`/note rows (EoL, Gewicht, PID,
Korrektur, …) the note text lands in the `Source_URL` column and the URL in `Confidence`; `Attributname` repeats the
PID. Consistent across all bundles (switch + module). Provenance/Merkmal rows are normal (URL in Source_URL).

**MINOR-5 — 536 VLog rows cite only `web.archive.org`.** Archived OEM (Cisco) pages — acceptable per the
datasheet-cache rule, but Wayback links rot; consider snapshotting the PDFs.

**MINOR-6 — high-cardinality "Wertliste" Merkmale.** Anwendung 498, Port-Konfiguration 396, Switching-Kapazität 165,
Durchsatz 160, Stromversorgung 132, Kühlung 120, PoE 107 distinct values — typed `Datentyp=Wertliste` but effectively
free-text → very large JTL Wertlisten. (The directive's specific check, Freitext-where-Wertliste, is **clean**: 0.)

---

## 4. FALSE POSITIVES — investigated and cleared (so the cross-pass knows what was checked)

| Candidate | Count | Why it is NOT a defect |
|---|---|---|
| Anwendung capacity ≠ Switching-Kapazität | 58 | The Anwendung figure is **stacking bandwidth** ("physisches Stacking (480 Gbit/s)", "StackWise Plus (64 Gbit/s Stack-Ring)") — a distinct metric that **matches the Stacking Merkmal**. 0 real switching-capacity contradictions; 0 Wire-Speed (4948E) patterns. |
| Prose Mpps ≠ Durchsatz | 5 | Distinct labeled metrics: N3432D-S "7.200 Ingress / 10.000 Egress"; N5500 "Layer 3 … 240 Mpps" optional daughter-card vs the system L2 rate (which matches the Merkmal). |
| MDS "missing Layer" | 13 | Correct — Fibre Channel has no Ethernet L2/L3 Layer. |
| "No cisco.com source" | 73 | All **Meraki MS\***, correctly sourced to **documentation.meraki.com** (official Meraki manufacturer site). |
| Cat4500E 22 placeholder weights | 22 | Placeholders (7,00/6,00/5,00 kg) but **ZU_VERIFIZIEREN-flagged** (22× in VLog + "konservativer Platzhalter" + "physischer Messung"). NOT un-flagged. |

Also verified clean: **VLog internal contradictions = 0** (the 4948E stale-line class); **dedup = 0**; **exclusion = 0**;
**empty Source_URL rows = 0**; **Datentyp Freitext-where-Wertliste = 0**; **near-dupe (casing/space/punct) under strict
normalizer beyond the MINOR-2 list = 0**.

### Recently-corrected items — re-verified end-to-end (in-data)
- **4948E** (4 SKUs): Switching-Kapazität 176 Gbit/s · Durchsatz 131 Mpps · 8,62 kg · "176 Gbit/s" in Anwendung · airflow S/E = Front-to-Back, F-S/F-E = Back-to-Front. ✅
- **Cat4500E modules** (22): placeholder weights, every one ZU_VERIFIZIEREN-flagged. ✅
- **Nexus 7000 M2 trio**: N7K-M224XP-23L 240, N7K-M206FQ-23L 240, N7K-M202CF-22L 200 Gbit/s. ✅
- **Nexus 9800**: N9K-C9808 16 HE / 115,2 Tbit/s / 73,00 kg / bis 40 °C; N9K-C9804 10 HE / Switching-Kapazität ZU_VERIFIZIEREN / 56,36 kg / bis 40 °C. ✅

---

## 5. INDEPENDENT RE-FETCH (5-SKU cross-section) + COURIER-NEEDED
All 5 cisco.com datasheets 403'd to automated fetch; verified via **Wayback snapshots of the identical Cisco docs**
(no reseller figures). **22 of 24 values CONFIRMED.** Two flags:
- **C9300X-48HX switching capacity** — value CONFIRMED (Cisco: 1,760 **Gbps** = 1760 Gbit/s); the catalog's `1,760 Tbit/s`
  *rendering* is the MINOR-2 ambiguity above, not a value error.
- **C9500-48Y4C weight** — my agent reported UNVERIFIED, but the **L8 courier RESOLVED it as CONFIRMED**: the HIG
  Technical-Specs Table 3 publishes 48Y4C = 9,96 kg / 24Y4C = 9,52 kg, matching the catalog. The agent's miss was a
  Wayback-snapshot artifact (no HIG physical-spec table in that snapshot). No defect.
- Fully CONFIRMED: N9K-C9332D-GX2B (25,6 Tbit/s · 4,17 Bpps · 12,70 kg · 32×400G · 1 RU); N9K-C9808 (73 kg unloaded · 16 RU ·
  8 slots · 115,2 Tbit/s · NX-OS); WS-C3750X-48P-S (160 Gbit/s · 101,2 Mpps · 7,50 kg · StackWise Plus 64 Gbit/s).

**COURIER-NEEDED** — none open. The 2 Y4C weights were couriered from the Catalyst 9500 HIG (Table 3) and **confirmed
correct**; their VLog provenance is added in FIX 3.

---

## 6. COUNTS
- SKUs audited: **995** (113 bundles). Manifest reconciled: 995 = 995.
- **CRITICAL 0 · MAJOR 3 actionable** (bundle naming · chassis-schema split · MDS category) **+ 1 HELD traceability gap**
  (weight-provenance 532/995 — no correctness defect) **· MINOR ~7** · false-positive classes cleared: 5 + the C9500-Y4C
  graft (courier-retracted) · re-fetch confirmed 24/24 after courier.
- Structural: 0 dedup · 0 exclusion · 0 unpriced · 0 price-format · 0 forbidden-Merkmal-on-module · 0 missing-Merkmal (fixed) · 0 cross-field factual contradiction.
- The 180 raw P1 hits = 154 Prices-LF (77 bundles ×2) + 26 MDS (13 ×2). Nothing else.
- Open verification: **none** (both Y4C weights couriered + confirmed).
