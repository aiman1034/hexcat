# HPE/Aruba STEP-2 BATCH-3 — PRE-IMPORT REQUIREMENTS  (CX data-center tier)

**Scope:** Aruba CX 8100 (12) · 8320 (3) · 8325 (6) · 8325H (8) = **29 fixed DC switches**, all authored + gate-clean
through the proven pipeline (extended with VSX/DC/L3 prose branches). Hersteller = **HP**. Prices = Phase-1 ESTIMATE.

**Gate:** all 4 bundles `ok=True viol=0`. **validate_dir = 0** each. **Dedup:** whole switch tree **1146 SKUs, all unique**
(FtB/BtF/TAA airflow variants distinct via PID-welding). Running HPE/Aruba switch total: **112 authored** (CX access +
6300 + DC aggregation tiers).

| Bundle | SKUs | Doc | SwK basis | Redundancy |
|---|---|---|---|---|
| Aruba CX 8100 | 12 | a00131340enw (cached, current) | **per-model** 1.28/1.36/1.76 Tbps | VSX |
| Aruba CX 8320 | 3 | a00036440enw (cached) | series-wide 2.5 Tbps | VSX |
| Aruba CX 8325 | 6 | a00059009enw (cached, current) | series-wide 6.4 Tbps | VSX |
| Aruba CX 8325H | 8 | a00059009enw (mirror — see §F) | **per-model** 2.16/4.0 Tbps | VSX |

---

## A. Four E3 categories to create  (Netzwerk & Infrastruktur ▸ Switches ▸ …)
`Aruba CX 8100 Switches` · `Aruba CX 8320 Switches` · `Aruba CX 8325 Switches` · `Aruba CX 8325H Switches`
(added to `config/rules.yaml`, additions-only). Create the 4 JTL nodes before import.

## B. The headline new Merkmal VALUE — `VSX` (Stacking), 0 new Merkmal NAMES
The DC tier's redundancy is **VSX (Virtual Switching Extension)** — a 2-node active-active HA pair, NOT the access
tier's N-member VSF stacking. It is grounded into the existing **`Stacking`** Merkmal as a new VALUE (no new name).
The prose was given a dedicated VSX branch ("…lassen sich zwei <PID> per Aruba VSX zu einem aktiv-aktiven Paar
koppeln") so it does NOT misdescribe VSX as VSF stacking.

## C. NEW MERKMAL VALUES NEEDED  (51 — add to live Wertlisten before import)
0 new Merkmal NAMES. Switch-Typ (`Managed`), Layer (`L3`), PoE (`Nein`) all reuse existing values.

### Bauform — 1 NEW: `19-Zoll-Rackmontage (1 HE, halbe Breite)`  *(the half-width 8325H)*
### Betriebstemperatur — 1 NEW: `0 bis 40 °C (bei Front-to-Back-Konfiguration bis 45 °C)`
  *(`0 bis 40 °C` and `0 bis 45 °C` already exist — reused; this combined value is for the airflow-agnostic base/spares.)*
### Stacking — 1 NEW:
- `VSX (Aruba Virtual Switching Extension) – 2-Node-Hochverfügbarkeit, aktiv-aktiv mit synchronisiertem Forwarding-Zustand (MC-LAG)`
### Switching-Kapazität — 4 NEW: `1,28 Tbit/s` · `1,36 Tbit/s` · `1,76 Tbit/s` · `4 Tbit/s`
  *(2,16 / 2,5 / 6,4 Tbit/s already present — reused.)*
### Durchsatz — 4 NEW: `1.309 Mpps` · `1.905 Mpps` · `2.000 Mpps` · `Wire-Speed (modellspezifischer Mpps-Wert nicht im Datenblatt ausgewiesen)`
### Port-Geschwindigkeit — 8 NEW · Uplink-Ports — 6 NEW · Port-Konfiguration — 9 NEW
  (per-SKU 25G/100G DC configs incl. the homogeneous "alle N Ports flexibel" uplink descriptors — see `output/.../Attributes.csv`)
### Stromversorgung — 3 NEW:
- `2 feldaustauschbare Hot-Swap-Netzteile (N+1, im Bundle); AC 100–240 V`
- `2 fest verbaute Netzteile (1+1-Redundanz), 100–240 VAC, max. 500 W`  *(8325H = fixed, not hot-swap)*
- `Feldaustauschbare Hot-Swap-Netzteile, separat bestellt (bis 2, N+1); AC`  *(base/spares)*
### Kühlung — 9 NEW: (3/4/5/6-fan hot-swap or fixed, per airflow + the separate-order base variant)
### Anwendung — 5 NEW: (DC aggregation / spine-leaf-ToR strings, incl. the half-width 8325H + the 10GBASE-T 8100)

**TOTAL BATCH-3 NEW WERTLISTE VALUES = 51**

---

## D. Flag-don't-fabricate findings (grounded per family; the doc won where the brief differed)
- **Switching capacity granularity differs by family.** The cached docs state SwK **per-model** for 8100 (1.28/1.36/1.76
  Tbps) and 8325H (2.16/4.0 Tbps) — used per-model. But **8320 (2.5 Tbps) and 8325 (6.4 Tbps) state a single series-wide
  figure** (no per-model column) — so both 8325 models carry 6.4 Tbps as the doc states; I did NOT invent a lower 48Y8C
  value. Flagged as series-wide.
- **Durchsatz (Mpps):** 8100 = `1.309 Mpps`, 8320 = `1.905 Mpps`, 8325 = `2.000 Mpps` — all **series-wide max** (no
  per-model Mpps row). **8325H has NO Mpps figure at all** (the doc's 2.000 Mpps is attributed to the 8325-32C, a
  different model) → shipped as `Wire-Speed (… nicht ausgewiesen)`, flagged.
- **8320 has NO EVPN/VXLAN** in its datasheet (only BGP/OSPF/VRF) → its feature prose omits EVPN/VXLAN (the 8100/8325/8325H
  DO list BGP-EVPN/VXLAN and say so). Per-family feat override, not a blanket claim.
- **Operating temperature is airflow-dependent:** Front-to-Back = `0 bis 45 °C`, Back-to-Front = `0 bis 40 °C` (8100 +
  8325H); 8320/8325 = `0 bis 40 °C` across the board. Grounded per PID by airflow.
- **8325H = FIXED PSU + fans** (2× 1+1, 4× N+1 — not hot-swap), **half-width 1U**; the 8325 (full-width) is hot-swap.
- **Base-/spare PIDs** (8100 R9W94A–97A; 8325 JL635A/JL636A) are switch-only (PSU/fans ordered separately) → airflow is
  **configurable**; their Stromversorgung/Kühlung say "separat bestellt" and the temp carries the configurable note.
- **PoE = Nein** on every DC model (verified per doc).

## E. ZU_VERIFIZIEREN remaining (auditor may refine; shipped on best grounding)
- 8325H **Durchsatz** (Mpps) — no per-model figure in the doc (wire-speed); a couriered/QuickSpecs Mpps would replace it.
- 8100/8325 **base-spare weights** — the doc gives only the full-config bundle weight; the spare ships with the
  bundle weight as the nearest grounded figure.

## F. Source provenance (cache-currency check done, per the 6200 lesson)
8100/8320/8325 grounded from the **cached current** datasheets (a00131340 / a00036440 / a00059009enw — doc-ids + VSX
confirmed in-doc). **8325H:** its dedicated doc a00142954enw was unobtainable (HPE/Akamai timeouts, mirror cert/403),
but the **current combined 8325/8325H series datasheet (a00059009enw)** — which contains the full verbatim 8325H
technical-spec tables — was obtained from a verbatim-OEM mirror and used; provenance cites the canonical
`hpe.com/psnow/doc/a00059009enw`.

## G. Pricing — Phase-1 ESTIMATE only (flagged `geschätzt-Tier (PLATZHALTER)` in VLog_Prices).

## H. Footprint
- 4 NEW bundles `output/switches/Aruba_CX_{8100,8320,8325,8325H}_Switches/` + their 4 `stage3_content/*.json`
- `config/rules.yaml` (+4 E3) · `config/coverage/gate_completeness.yaml` (+4 records, all complete)
- `_scratch/aruba_cx_access_build.py` (driver, extended with VSX/DC branches) · `PROJECT_AUDIT.md` · this note
- **0 new Merkmal NAMES · 0 src/ changes · nothing created in JTL.**
