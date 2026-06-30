# HPE/Aruba STEP-2 BATCH-1 — PRE-IMPORT REQUIREMENTS

**Scope:** Aruba CX 6300F (8 PIDs) + Aruba CX 6300M (22 PIDs) = **30 fixed switches**, authored to the
EXACT locked Cisco switch schema/pipeline. Hersteller = **HP**. Grounded verbatim from the cached current
6300 datasheet **a00085162ENW** (auditor-confirmed). Prices are **Phase-1 ESTIMATES** (see §E).

**Build output:** `output/switches/Aruba_CX_6300F_Switches/` + `output/switches/Aruba_CX_6300M_Switches/`
(full 8-file bundle each: Main · Attributes · PlatformFlag · Prices · Condition · FAQ · 2× Verification_Log).
**Gate:** both `ok=True viol=0`. **validate_dir = 0** both bundles. **Dedup:** 30/30 unique.

> ⚠️ **The operator must create the following in the live JTL tree BEFORE importing this batch.**
> Import does NOT auto-create E3 categories or Merkmal-Wertliste values; an un-created value imports blank.

---

## A. Two E3 categories to create  (Netzwerk & Infrastruktur ▸ Switches ▸ …)

| Kategorie Ebene 1 | Kategorie Ebene 2 | Kategorie Ebene 3 (NEW) |
|---|---|---|
| Netzwerk & Infrastruktur | Switches | **Aruba CX 6300F Switches** |
| Netzwerk & Infrastruktur | Switches | **Aruba CX 6300M Switches** |

Already added to `config/rules.yaml → kategorie_ebene_3_switch_allowed` (additions-only) so validate_dir
treats the bundles as switches. The **JTL category tree** still needs these two E3 nodes created by hand,
exactly as the Cisco series categories were.

---

## B. PoE risk-test — PASS (no new Merkmal)

The existing `PoE` Merkmal **cleanly holds a wattage budget** — the Cisco bundles already use the
`Ja (<Standard>, <W/Port>, Budget <N> W)` form (e.g. `Ja (Cisco UPOE+ 802.3bt Type 4, 90 W/Port, Budget 2.160 W)`).
The 6300M maps straight onto it (e.g. `Ja (IEEE 802.3af/at/bt Class 8, 90 W/Port, Budget 2.880 W)`).
**No new Merkmal NAME was created; 0 STOP-and-ask.** The split-class R8S91A (ports 1–12 Class 8 / 13–48
Class 6) also fits the single string. Per-port wattage + budget live in the attribute; the prose stays concise.

---

## C. NEW MERKMAL VALUES NEEDED  (63 total — add to the live Wertlisten before import)

Merkmal **NAMES** are 100 % reused (the locked 15 fixed-switch Merkmale). These are new **VALUES** only.
The 5 categorical Merkmale need **0** new values (all reuse the Cisco-populated lists); the per-SKU
descriptive Merkmale expose HPE-specific strings.

> ✅ Switch-Typ · Layer · Portanzahl · Bauform · Betriebstemperatur — **0 new** (fully reused: `Managed`,
> `L3`, `28`/`52`, `19-Zoll-Rackmontage (1 HE)`, `0 bis 45 °C`).

### Switching-Kapazität — 2 NEW value(s) to add:
- `720 Gbit/s`
- `780 Gbit/s`
  *(1760 / 448 / 496 Gbit/s already exist in the Cisco Wertliste — reused.)*

### Durchsatz — 7 NEW value(s) to add:
- `1310 Mpps`
- `334 Mpps`
- `369 Mpps`
- `476 Mpps`
- `535 Mpps`
- `580 Mpps`
- `654 Mpps`

### Stacking — 2 NEW value(s) to add:
- `Ja (Aruba VSF, bis 10 Einheiten, bis 400 Gbit/s, über die SFP56-Uplinks)`
- `Ja (Aruba VSF, bis 10 Einheiten; QSFP-zu-SFP56-DAC für das Stacking erforderlich)`

### PoE — 9 NEW value(s) to add:
- `Ja (IEEE 802.3af/at/bt Class 6, 60 W/Port, Budget 1.440 W)`
- `Ja (IEEE 802.3af/at/bt Class 6, 60 W/Port, Budget 2.880 W)`
- `Ja (IEEE 802.3af/at/bt Class 8, 90 W/Port, Budget 2.640 W)`
- `Ja (IEEE 802.3af/at/bt Class 8, 90 W/Port, Budget 2.880 W)`
- `Ja (IEEE 802.3af/at/bt; Ports 1–12 Class 8 90 W, Ports 13–48 Class 6 60 W; Budget 2.880 W)`
- `Ja (IEEE 802.3at/bt Class 4, 30 W/Port, Budget 1.440 W)`
- `Ja (IEEE 802.3at/bt Class 4, 30 W/Port, Budget 370 W)`
- `Ja (IEEE 802.3at/bt Class 4, 30 W/Port, Budget 720 W)`
- `Ja (IEEE 802.3at/bt Class 4, 30 W/Port, Budget 740 W)`
  *(`Nein` reused.)*

### Port-Geschwindigkeit — 7 NEW value(s) to add:
- `1 GbE (10/100/1000BASE-T, Access), bis 50 GbE (SFP56-Uplink)`
- `1/10 GbE (SFP+, Access), bis 50 GbE (SFP-Uplink)`
- `1/10 GbE (SFP+, Access), bis 50 GbE (SFP56-Uplink)`
- `100M/1/2.5/5 GbE (Smart Rate, Access), bis 50 GbE (SFP-Uplink)`
- `100M/1/2.5/5 GbE (Smart Rate, Access), bis 50 GbE (SFP56-Uplink)`
- `100M/1/2.5/5/10 GbE (Smart Rate, Access), bis 100 GbE (QSFP28-Uplink)`
- `100M/1/2.5/5/10 GbE (Smart Rate, Access), bis 50 GbE (SFP-Uplink)`

### Uplink-Ports — 4 NEW value(s) to add:
- `2× SFP56 (50G) + 2× SFP+ (1/10G LRM)`
- `2× SFP56 (50G) + 2× SFP28 (25G)`
- `4× QSFP28 (10/25/40/100G, MACsec)`
- `4× SFP56 (1/10/25/50G)`

### Port-Konfiguration — 12 NEW value(s) to add:
- `24× 1/10G-SFP+ (LRM, MACsec) + 2× SFP56 (50G) + 2× SFP28 (25G) (Uplink)`
- `24× 1/10G-SFP+ + 4× SFP56 (1/10/25/50G) (Uplink)`
- `24× 10/100/1000BASE-T (Class 4 PoE, 30 W) + 4× SFP56 (1/10/25/50G) (Uplink)`
- `24× 10/100/1000BASE-T (ohne PoE) + 4× SFP56 (1/10/25/50G) (Uplink)`
- `24× HPE Smart Rate 100M/1/2.5/5/10G-BASE-T (Class 6 PoE, 60 W, MACsec) + 2× SFP56 (50G) + 2× SFP28 (25G) (Uplink)`
- `24× HPE Smart Rate 100M/1/2.5/5G-BASE-T (Class 6 PoE, 60 W) + 4× SFP56 (1/10/25/50G) (Uplink)`
- `48× 10/100/1000BASE-T (Class 4 PoE, 30 W) + 4× SFP56 (1/10/25/50G) (Uplink)`
- `48× 10/100/1000BASE-T (ohne PoE) + 4× SFP56 (1/10/25/50G) (Uplink)`
- `48× HPE Smart Rate 100M/1/2.5/5/10G-BASE-T (Class 8 PoE, 90 W, MACsec) + 4× QSFP28 (10/25/40/100G, MACsec) (Uplink)`
- `48× HPE Smart Rate 100M/1/2.5/5G-BASE-T (Class 6 PoE, 60 W) + 4× SFP56 (1/10/25/50G) (Uplink)`
- `48× HPE Smart Rate 100M/1/2.5/5G-BASE-T (Class 8 PoE, 90 W, MACsec) + 2× SFP56 (50G) + 2× SFP28 (25G) (Uplink)`
- `48× HPE Smart Rate 100M/1/2.5/5G-BASE-T PoE, MACsec (Ports 1–12 Class 8/90 W, Ports 13–48 Class 6/60 W) + 2× SFP56 (50G) + 2× SFP+ (1/10G LRM) (Uplink)`

### Stromversorgung — 4 NEW value(s) to add:
- `2 Hot-Swap-Netzteilschächte (mindestens 1 erforderlich, separat bestellt)`
- `Internes Festnetzteil 200 W (nicht hot-swap, nicht feldaustauschbar)`
- `Internes Festnetzteil 950 W (nicht hot-swap, nicht feldaustauschbar)`
- `Power-to-Port-Bundle: 1× JL760A-Netzteil vorinstalliert (2 Hot-Swap-Schächte, zweites optional separat)`

### Kühlung — 4 NEW value(s) to add:
- `2 feldaustauschbare Hot-Swap-Lüftereinschübe (back-to-front, Power-to-Port), je 2 Lüfter`
- `2 feldaustauschbare Hot-Swap-Lüftereinschübe (front-to-back), je 2 Lüfter`
- `3 feldaustauschbare Hot-Swap-Lüftereinschübe (front-to-back), je 2 Lüfter`
- `Feste Lüfter (nicht austauschbar), Airflow front-to-back`

### Anwendung — 12 NEW value(s) to add:
- `Aggregations- und Server-Access (1/10G-SFP+), Layer 3 unter AOS-CX, VSF-Stacking, 50G-SFP56-Uplinks`
- `Campus-Access (Layer 3, AOS-CX) mit Gigabit-PoE+ für Access Points, IP-Telefone und Kameras; Dynamic Segmentation, VSF-Stacking`
- `Campus-Access (Layer 3, AOS-CX) mit PoE-Versorgung für Access Points, IP-Telefone und Kameras; Dynamic Segmentation, VSF-Stacking über die SFP56-Uplinks`
- `Campus-Access (Layer 3, AOS-CX) ohne PoE für Arbeitsplatz-Anbindung und Uplink-Verdichtung; Dynamic Segmentation, VSF-Stacking über die SFP56-Uplinks`
- `Campus-Access für Wi-Fi-6/6E-Access-Points (10G Smart Rate, Class-6-PoE, MACsec) mit 50G/25G-Uplinks, Layer 3 AOS-CX, VSF-Stacking`
- `Campus-Access für Wi-Fi-6/6E-Access-Points (Multigigabit Smart Rate, Class-6-PoE), Layer 3 unter AOS-CX, Dynamic Segmentation, VSF-Stacking`
- `Campus-Access für Wi-Fi-6/6E-Access-Points (Smart Rate, Class-8-PoE 90 W, MACsec) mit 50G/25G-Uplinks, Layer 3 AOS-CX, VSF-Stacking`
- `Campus-Access mit gemischten PoE-Klassen (High-Power-Uplink-APs + Standard-APs), MACsec und 50G/10G-LRM-Uplinks, Layer 3 AOS-CX, VSF-Stacking`
- `Campus-Access/Aggregation (Layer 3, AOS-CX) ohne PoE für Arbeitsplätze und Uplink-Verdichtung; Dynamic Segmentation, VSF-Stacking`
- `Glasfaser-Aggregation/Server-Access (1/10G-SFP+ mit LRM und MACsec) mit 50G/25G-Uplinks, Layer 3 AOS-CX, VSF-Stacking`
- `High-Density-Campus-Aggregation/Access mit 10G-Smart-Rate, 100G-QSFP28-Uplinks und durchgängigem MACsec; PTP/AVB, Class-8-PoE, AOS-CX, VSF-Stacking`
- `Rechenzentrums-ToR/OOBM-Bundle: 1GbE-Server- und Management-Anbindung mit Back-to-Front-Airflow (Power-to-Port), Layer 3 unter AOS-CX, VSF-Stacking`

**TOTAL NEW WERTLISTE VALUES = 63**

---

## D. Grounding corrections surfaced (flag-don't-fabricate — the brief was wrong, the doc is authoritative)

Two grounding passes over the cached datasheet corrected the build brief — these are now baked into the SKUs:
1. **6300F (JL665A–JL668A + TAA twins) ≠ 6300M chassis.** The 6300F has an **internal FIXED power supply**
   (950 W on PoE models, 200 W on non-PoE), **fixed (non-replaceable) fans**, and a **PoE budget of 740 W /
   370 W** — NOT the 2640/2880 W hot-swap-PSU/fan-tray design of the 6300M. SwK/throughput = 496/448 Gbit/s ·
   369/334 Mpps (not the cover-page family max).
2. **JL762A / S0G02A = 48-port 1GbE NON-PoE Power-to-Port (back-to-front) ToR/OOBM bundle** — the brief
   labelled them "SmartRate Class6 PoE"; the doc shows plain 10/100/1000 BaseT, **no PoE row**. Grounded to doc.
3. **JL658A / S0G03A = 880 Gbit/s · 654 Mpps** (24p SFP+), not the brief's 720/535 (that is R8S91A).
4. **R8S92A = no PoE** (SFP+ LRM access). TAA twins inherit base-PID specs verbatim ([TAA] sourcing-only delta).

No value was invented; every per-PID number is verbatim from a00085162ENW or carried from its base PID.

---

## E. Pricing — Phase-1 ESTIMATE only (NOT grounded)

`Hexwaren_<bundle>_Prices.csv` carries tier-based **placeholder** Netto-VK (by port-count / PoE / speed).
`Verification_Log_<bundle>_Prices.csv` flags every row `Methode = "geschätzt-Tier (PLATZHALTER)"` with the
note that **real HPE market-price research is a separate later phase** (analogous to the Cisco Phase-2 run).
Do NOT treat these as grounded sell prices.

---

## F. Footprint (this batch changed ONLY:)
- `output/switches/Aruba_CX_6300F_Switches/` + `output/switches/Aruba_CX_6300M_Switches/` (the 2 bundles)
- `stage3_content/Aruba_CX_6300F_Switches_content.json` + `..6300M..` (authored sidecars)
- `config/rules.yaml` — **2 additions-only** allowlist lines (the 2 E3 series)
- `config/coverage/gate_completeness.yaml` — 2 completeness records (8 / 22)
- `_scratch/aruba_cx_6300_build.py` (the author+build driver) · `PROJECT_AUDIT.md`
- **0 new Merkmal NAMES · 0 changes to src/ · nothing created in JTL** (this note lists what the operator creates).
