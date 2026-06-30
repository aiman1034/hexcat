# STEP 2 — CX 6400/8400 CHASSIS + MODULES · PHASE A: schema proposal + validation case (STOP for approval)

NEW-SCHEMA batch. The 15 fixed-switch Merkmale don't describe a modular chassis or a line card. **Outcome: the
Cisco modular-chassis + module schema already in the repo covers HPE → 0 new Merkmal NAMES.** One validation
case authored end-to-end (gate-clean); **full enumeration is HELD pending your approval + JTL creation.**

## STEP 0 — the Cisco precedent (audited in-repo; this is what I reuse VERBATIM)
- **Modular chassis** (e.g. Cisco_6500E / 4500E) — 10 Merkmale, drops all port-level ones:
  `Switch-Typ`(value `Modular-Chassis`) · `Layer` · `Steckplätze` · `Bauform`(value `19-Zoll-Rackmontage (X HE)`) ·
  `Switching-Kapazität` · `Stromversorgung` · `Kühlung` · `Unterstützte Supervisor-Engines` · `Redundanz` · `Anwendung`
  (+ `Zustand`). `_facts.unterkategorie = "Modularer Switch (Chassis)"`. (Operating temperature lives in PROSE, not a Merkmal.)
- **Modules** — `Modultyp` (established vocab: `Supervisor-Engine` · `Linecard` · `Port-Card` · `Fabric-Module`) +
  `Kompatible Serie` (multi-value); **line cards additionally reuse `Portanzahl` / `Port-Konfiguration` / `Switching-Kapazität`
  / `PoE`** (NOT `Port-Geschwindigkeit` — the gate enforces its absence on modules). `_facts.unterkategorie = "Switch-Modul"`.
- **Mapping (ratified, post-remap):** E1 `Netzwerk & Infrastruktur` / E2 **`Switches`** / E3 `Cisco <series> Switches` (chassis)
  resp. `Cisco <series> Modules` (modules). Both chassis-E3 and module-E3 sit in `kategorie_ebene_3_switch_allowed`.

## PROPOSED HPE SCHEMA — reuse → **0 new Merkmal NAMES**
- **CHASSIS** (E3 `Aruba CX 6400 Switches` / `Aruba CX 8400 Switches`): the 10 Merkmale above, verbatim names. New
  **VALUES** only — `Switch-Typ=Modular-Chassis` (reused value), the per-chassis HE Bauform, the system/per-slot
  `Switching-Kapazität`, `Steckplätze`/`Unterstützte Supervisor-Engines`/`Redundanz` strings. VSX, distributed-fabric, and
  management-plane detail → PROSE.
- **MODULES** (E3 `Aruba CX 6400 Modules` / `Aruba CX 8400 Modules`): `Modultyp` + `Kompatible Serie="Aruba CX 6400/8400"`
  + reused `Portanzahl`/`Port-Konfiguration`/`Switching-Kapazität`/`PoE` on line cards. **New `Modultyp` VALUE proposed:
  `Management-Modul`** (Aruba's term for the 6400/8400 control module; Cisco's equivalent value is `Supervisor-Engine`).
  Fabric modules (8400 only) reuse `Modultyp=Fabric-Module`.

**→ NEW Merkmal NAMES: 0.** Everything maps to an existing Cisco-established name. New work = Wertliste VALUES + prose only.

## ⚠️ TWO MAPPING DECISIONS FOR YOUR APPROVAL
1. **Module hauptkat.** You named `Switch-Module & Komponenten` — but that is the *pre-remap* E2. The **ratified, live**
   Cisco module mapping is **E2=`Switches`** + `_facts.unterkategorie="Switch-Modul"`, E3=`… Modules`. I followed the
   ratified precedent ("mirror exact / don't invent"). Confirm: keep **E2=Switches** (Cisco-consistent, what I built), or
   carve a distinct `Switch-Module & Komponenten` top-level.
2. **"Module" → "Modules".** I used **`Modules`** (plural): it matches the Cisco precedent (`Cisco … Modules`) AND the gate
   keys Class-B module bundles on a `_Modules` suffix (singular `Module` falls through to the transceiver namespace). If you
   want singular, that needs a gate change — not recommended.

## SCOPE (enumerated; NOT authored beyond the validation case)
| Platform | Chassis | Modules | Notes |
|---|---|---|---|
| **CX 6400** | 11 (4 bare 6405/6410 v1+v2 + 7 switch bundles) | 19 (1 mgmt + 18 line cards; **incl. S1T83A**) | no separate fabric SKU (distributed forwarding) |
| **CX 8400** | 1 (JL375A, 8-slot, ships as chassis+fan bundle) | 6 (1 mgmt + 1 fabric JL367A + 4 line cards) | EOL (EoS 2019), retained per keep-the-tail |
| **TOTAL** | **12** | **25** | full future enumeration = **37 SKUs** |

## VALIDATION CASE — authored end-to-end (5 SKUs, gate-clean, validate_dir=0)
**Chassis bundle `Aruba CX 6400 Switches` (1):** `R0X27C` Aruba CX 6410 v2 — 28 Tbit/s system capacity, 10 Linecard- +
2 Management-Steckplätze, 12 HE, 4× hot-swap PSU (N+1/N+N), 4 fan trays, 0–45 °C (prose). GROUNDED from QuickSpec a00073541enw.
**Module bundle `Aruba CX 6400 Modules` (4):**
- `R0X31A` Management Module (`Modultyp=Management-Modul`) — control plane, redundant active/standby (prose).
- `R0X44A` Linecard 48× SFP28 (1/10/25G).
- `R0X45A` Linecard 12× QSFP28 (40/100G).
- `R0X41A` Linecard 48× Smart Rate Class-6 PoE + 4× SFP56 (exercises card-level PoE).

### ⚠️ ZU_VERIFIZIEREN in the validation case (flag-don't-fabricate, never port-math)
- **Per-component weights** (mgmt module + each line card): the IGSG weight table (p.95) didn't render through the proxy →
  artikelgewicht are **flagged ESTIMATES** (mgmt 2,50; SFP/QSFP cards 3,50; PoE card 4,50 kg). Chassis 53,50 kg is GROUNDED.
- **Per-card Switching-Kapazität** — not published per line card (the cards carry an 8/32 MB packet buffer, in prose) → `ZU_VERIFIZIEREN`.
- **R0X41A PoE budget** — Class 6 (60 W/Port) is grounded; the absolute card budget is PSU-/config-dependent → `ZU_VERIFIZIEREN`.
- **6410 height** — QuickSpec says **12U** (used), the IGSG says 13U → flagged doc conflict; QuickSpec ordering value authoritative.

## STOP — what I need before authoring the remaining 32 SKUs
1. Approve the **chassis + module Merkmal sets** (0 new NAMES) and the new VALUES (esp. `Modultyp=Management-Modul`).
2. Decide the **two mapping questions** above (E2=Switches? · plural `Modules`?).
3. Create in JTL: E3 `Aruba CX 6400 Switches` / `Aruba CX 6400 Modules` (+ the 8400 pair) and the new Wertliste VALUES.
Then I enumerate + author the full 12 chassis + 25 modules (6400 + 8400) batch-by-batch.

## Footprint
- NEW `output/switches/Aruba_CX_6400_{Switches,Modules}/` + 2 `stage3_content/*.json` · driver `_scratch/aruba_cx_6400_build.py`
- `config/rules.yaml` (+2 E3) · `config/coverage/gate_completeness.yaml` (+2 records, validation subset) · PROJECT_AUDIT · this note
- **0 new Merkmal NAMES · 0 src/ change** (chassis weight handled by gating pre-remap, the Cisco order) · nothing created in JTL.
  Pricing Phase-1 ESTIMATE, flagged.
