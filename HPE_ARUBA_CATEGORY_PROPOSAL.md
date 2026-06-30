# HPE/Aruba Switches — Category Proposal (STEP 1, enumeration only)

**Date:** 2026-06-30 · **Status:** PROPOSAL — nothing created in JTL, no SKU authored. Locks scope/categories/branding **before** building.
**Hersteller (LOCKED):** `HP` — single manufacturer for all HP / HPE / Aruba; the sub-brand lives in the **E3 series name** (exactly the Cisco/Meraki pattern: Hersteller=Cisco, E3 carries Catalyst / Nexus / Meraki).

## Category structure (reuse the locked Cisco tree)
- **E1 = `Netzwerk & Infrastruktur`**
- **E2 = `Switches`** (every family, fixed + chassis + modules — identical to the Cisco switch lane)
- **E3 = the series name** (one E3 per family; the load-bearing class token that drives Attributgruppe + the chassis/module gate carve-out)

## Proposed E3 naming convention (pick ONE — justification below)
**CONVENTION: `E3 = "<OEM sub-brand> <series> Switches"`**, where `<OEM sub-brand>` is the family's **current OEM data-sheet brand**, used verbatim. The sub-brands already embed their own brand prefix (Aruba / HPE), so NO extra "HP" prefix is added (the `HP` Hersteller field carries the legal manufacturer — just as Cisco's catalog doesn't repeat "Cisco Systems Inc" in E3).

**Why this (vs the operator's mixed examples):** HP's portfolio has **two living sub-brands** (Aruba and HPE) plus EOL ProCurve — unlike Cisco's single "Cisco" prefix. Forcing a uniform "HP …" prefix would produce un-searchable names ("HP Aruba CX 6300"); using each line's real OEM family name keeps every E3 self-identifying and matches how a B2B buyer searches. This mirrors Cisco/Meraki (sub-brand in E3) while respecting that HP's sub-brands are themselves brands. **Ratification is OPEN-DECISION #1.**

Brand mapping applied:
| OEM line | E3 prefix | Rationale |
|---|---|---|
| AOS-CX | `Aruba CX <series>` | OEM brands the whole line "Aruba CX" / "HPE Aruba Networking CX" |
| ArubaOS-Switch (Aruba-era) | `Aruba <series>` | 2530/2540/2920/2930F/2930M/3810M/5400R zl2 ship as "Aruba" |
| ArubaOS-Switch (EOL ProCurve) | `HPE <series>` | 2615/2620/2915/3500 physically branded "HP" → normalize to current owner "HPE" |
| Comware DC | `HPE FlexFabric <series>` | OEM family name |
| Comware campus/legacy | `HPE FlexNetwork <series>` | OEM family name |
| SMB managed/unmanaged | `HPE <series>` | OfficeConnect branding dropped by OEM; V1910 → "HPE 1910" |
| SMB cloud | `Aruba Instant On <series>` | OEM family name |

## Per-family E3 proposal (49 switch families + 5 module families)

### Aruba CX (15) — E2 Switches
`Aruba CX 6000 Switches` · `Aruba CX 6100 Switches` · `Aruba CX 6200F Switches` · `Aruba CX 6300F Switches` · `Aruba CX 6300M Switches` · **`Aruba CX 6400 Switches`** (modular) · `Aruba CX 4100i Switches` · `Aruba CX 8100 Switches` · `Aruba CX 8320 Switches` · `Aruba CX 8325 Switches` · `Aruba CX 8360 Switches` · **`Aruba CX 8400 Switches`** (modular) · `Aruba CX 9300 Switches` · `Aruba CX 9300S Switches` · `Aruba CX 10000 Switches`

### ArubaOS-Switch (11)
`Aruba 2530 Switches` · `Aruba 2540 Switches` · `HPE 2615 Switches` · `HPE 2620 Switches` · `HPE 2915 Switches` · `Aruba 2920 Switches` · `Aruba 2930F Switches` · `Aruba 2930M Switches` · `HPE 3500 Switches` · `Aruba 3810M Switches` · **`Aruba 5400R zl2 Switches`** (modular)

### HPE FlexFabric (Comware, 5)
`HPE FlexFabric 5700 Switches` · `HPE FlexFabric 5800 Switches` · `HPE FlexFabric 5900 Switches` · `HPE FlexFabric 5930 Switches` (mixed: 2 modular slot-variants) · `HPE FlexFabric 5940 Switches` (mixed: 2 modular slot-variants)

### HPE FlexNetwork (7)
`HPE FlexNetwork 5130 EI Switches` · `HPE FlexNetwork 5130 HI Switches` · `HPE FlexNetwork 5120 SI Switches` · `HPE FlexNetwork 5500 EI Switches` · `HPE FlexNetwork 5500 HI Switches` · `HPE FlexNetwork 5510 HI Switches` · **`HPE FlexNetwork 10500 Switches`** (modular)

### SMB / Instant On (11)
`HPE 1410 Switches` · `HPE 1420 Switches` · `HPE 1620 Switches` · `HPE 1810 Switches` · `HPE 1820 Switches` · `Aruba Instant On 1830 Switches` · `HPE 1910 Switches` · `HPE 1920 Switches` · `Aruba Instant On 1930 Switches` · `HPE 1950 Switches` · `Aruba Instant On 1960 Switches`

### Switch Modules (5) — parallel to the Cisco "…Modules" lane
`Aruba CX 6400 Modules` · `Aruba CX 8400 Modules` · `Aruba 5400R zl2 Modules` · `Aruba 2930M/3810M/2920 Modules` · `HPE FlexNetwork 10500 Modules`
*(module E3s drive the Class-B module gate — Modultyp/Kompatible Serie — not the fixed-switch Attributgruppe.)*

## Modular-chassis families (need the existing Modular-Chassis attribute set — Steckplätze / Unterstützte Supervisor-Engines / Redundanz)
**True line-card chassis (4):** `Aruba CX 6400` (6405/6410), `Aruba CX 8400` (8-slot), `Aruba 5400R zl2` (5406R/5412R), `HPE FlexNetwork 10500` (10504/08/12).
**Mixed families (some modular slot-variants):** `HPE FlexFabric 5930` (JH178A/JH179A), `HPE FlexFabric 5940` (JH397A/JH398A) — these carry both fixed and 2-/4-slot modular SKUs **inside one family**, so the chassis attr set applies per-SKU, not per-family (handle like the Cisco 5930/5940-style mixed bundles).
All other families are fixed (Switch-Typ = Managed / Layer-2/3 fixed).

---

## 4. OPEN-DECISIONS — sign-off needed before STEP-2 authoring

1. **E3 branding convention (ratify):** approve `"<OEM sub-brand> <series> Switches"` (no extra HP prefix; sub-brand verbatim from OEM)? Sub-question: EOL ProCurve lines (2615/2620/2915/3500) — label **`HPE 2620`** (normalize to current owner, proposed) or **`HP 2620`** (match the physical product silk-screen)?
2. **Base-vs-bundle counting (CX):** CX ships as airflow (FtB/BtF) × AC/DC × **TAA** *bundles* of the same hardware. The manifest counts **base switches** (e.g. 8360 = 6 base, not 18 bundles). Confirm: catalog one SKU per **base switch**, or one per **orderable bundle PID**? (This changes the denominator materially — esp. 6300M's TAA set and the CX 83xx airflow bundles.)
3. **EOL / legacy scope:** in or out? — ProCurve EOL (2615, 2620, 2915, 3500); FlexFabric EOSL (5700, 5800, 5930) + 5900CP/AF EOL (ZU_VERIFIZIEREN); FlexNetwork EoS (5500 EI/HI); SMB EOL (1410, 1620, 1810, 1820, 1910, 1920). The current-and-shipping core is CX + Instant On (1830/1930/1960) + 2540/2930F/2930M/3810M/5400R + 5940 + 5130/5510 HI.
4. **Module families in scope?** Confirm the 5 Module families (~70 SKUs) are STEP-2 in-scope (parallel to the Cisco "…Modules" lane). Sub-items: (a) **port-adding stacking modules** JL325A/JL084A/J9733A — in-scope (they add ports) or treat as accessory? (b) CX 6400 **v1 (A/B)** line cards — author the superseded generation, or v2 "C"/"S" only? (c) **CX 8360 has NO modules** (fixed) — exclude. (d) **5930 expansion modules + 12900 line cards** — separate follow-up enumeration passes (not done here).
5. **New CX candidates (not in the seed) — add to scope?** `CX 10040` (2025 DSS, 8 Tbps, 10000-successor), `CX 8325H` (half-width), `CX 6200M` (modular-uplink), `CX 6300L` (3-model L2 sub-line S3L75A/76A/77A), `CX 6000/6100/6200` newer revs.
6. **DSS positioning (CX 10000/10040):** classify as a Switch (it runs AOS-CX L2/L3) — confirmed in-scope as a switch — but note the embedded AMD Pensando DPU (stateful firewall/NAT/encryption) is a **feature handled in prose**, not a Merkmal (see Merkmal-Fit). OK?
7. **TAA twins:** include separately (e.g. 5700 JG895A/JG897A, 6300 S0G##A) or fold into the base PID? Affects count.
8. **ZU_VERIFIZIEREN items to resolve at author time:** 2930F phantom "740W non-TAA" name (no PID); 8325 full bundle count; 5400R zl2 40G-QSFP+ v3 module PID + JL745 binding; 10500 exact line-card count; SMB per-family verbatim PID lists (in cache `ENUMERATION_STEP1.md`, not all surfaced to the manifest); 1810 v1/v2 split; 1920S successor in scope.
9. **Source-fetch caveat:** hpe.com + arubanetworks.com origins are **Akamai-blocked from this host**; all counts were measured from **byte-verbatim OEM PDFs** (verified by embedded doc# + copyright) served via CDN mirrors + the prior cache, **not** a live origin fetch. router-switch counts were used only as a cross-reference, never as truth. Recommend a residential-IP / authenticated confirmation pass on the live counts before STEP-2.
