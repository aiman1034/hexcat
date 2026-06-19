# Phase-2 Correction Manifest — notes & reconciliation (v2, post-3-fixes)
_2026-06-17. Companion to `PHASE2_MANIFEST.csv` (the byte-diff spec). Report-only; nothing applied. HOLD Phase-2 until operator reviews this corrected manifest + the remaining [VERIFY] grounding is in._

## EXACT total: 140 definite corrections (124 + 16 [VERIFY]-resolved DOM)
| source_delta | rows | notes |
|---|---|---|
| DOM-temp | 28 | 13 pending (Cisco 7, HPE 4, **Juniper 2 omit**) + 15 applied-guard (Extreme 3, Fortinet 7, Dell 5) |
| other-11 | 11 | Faseranzahl 7, Länge 3, Kabeltyp 1 |
| FF-withinfamily | 70 | |
| FF-hostFF | 6 | 4× QSFP-DD + **2× SR10→omit** (FIX 2) |
| FF-DSFP | 9 | needs DSFP vocab add |
| VERIFY-DOM | 16 | [VERIFY]-resolved DOM Ja→Nein: Cisco MGB ×3 + Cisco CWDM/DWDM-1G ×10 + Juniper RX ×3 |
| **TOTAL** | **140** | **125 pending + 15 applied-guard** |

### [VERIFY] grounding resolved (2026-06-17) — web-verified vs official datasheets
**16 genuine DOM deltas added** (all Ja→Nein): Cisco MGBSX1/LX1/LH1 (SB DS c78-741408, DOM absent), Cisco CWDM-SFP-{1470,1490,1510,1530,1610} + DWDM-SFP-{3033,3112,3190,3268,6141} (1G; OEM DS silent → conservative, reversible), Juniper RX-10KM/550M/70KM-SFP (legacy E-series; OEM silent → conservative, reversible). **+2 Anschlusstyp** (Cisco B20U4/B20D4-I: "Duplex LC (bidirektional)" → "Single LC/PC (Single-Fiber BiDi)", matched to the GLC-BX Wertliste token; DS c78-736282 single-fibre; no paired Artikelname — connector not in name).
**CONFIRM-KEEPS (logged in Verification_Log, NO value change):**
- Cisco **B20U4/B20D4-I**: Faseranzahl=**1** (DS: single-fibre, 4 Tx via diplexer — current already 1, so a confirm-keep, NOT the "[was 2]" add), DOM=Ja, Betriebstemperatur=−40 °C Kaltstart/−20…85 °C Betrieb (industriell) — all 3 already correct.
- Cisco **ONS-SI-GE-SX/LX/EX/ZX** ×4: DOM=Ja + Betriebstemperatur=−40…85 °C — already correct (grounding confirmed, no delta).
**Updated per-brand:** Cisco B 14→**27** (+13 DOM), Cisco C 0→**2** (B20 Anschlusstyp, no paired name); Juniper B 2→**5** (+3 RX DOM). Other brands unchanged.

- **124 corrections / 121 unique (Brand,PN).** ⚠ **Key the byte-diff on (Brand,PN)** — `SFP-1G-SX` & `SFP-1G-LX` exist in BOTH Cisco and Dell. Genuine same-part double-corrections = 3 Arista parts (Formfaktor + Länge): C-Z100-Z100-3M, C-Y100-Y100-3M, C-S50-S50-3M.
- **applied-guard (15)**: already in emitted CSV + content JSON (verified synced) — must NOT regress. **pending (109)**: must change to new_value.

## The 3 fixes applied this round
**FIX 1 — Juniper -ET ×2 → OMIT (not hold at 0–70).** EX-SFP-1GE-SX-ET, EX-SFP-1FE-FX-ET: Juniper HCT documents "Extended Temperature Range Optics" → shipping 0–70 is a known-wrong claim. Handled exactly like the Extreme -ET: **Betriebstemperatur omitted** (old "0 bis 70 °C" → attribute removed); exact band stays [VERIFY] (flag-don't-fabricate) + qualitative prose. Moved OUT of [VERIFY]-held, INTO the manifest (+2 → DOM-temp 28).

**FIX 2 — FG-CABLE-SR10-SFP+ / -SFP+5 → OMIT Formfaktor (NOT CFP2, NOT SFP+).** The DS describes a **passive OM3 fan-out cable** ("100 GE CFP2 parallel breakout, MPO to 10×LC connectors, OM3") that *mates with* a separate 100GBASE-SR10 CFP2 module — not itself a CFP2 module. Already classified Kategorie "MPO Kabel" + Kabeltyp "OM3-Multimode-Glasfaser (MPO zu LC)". Passive fibre = no module FF → **Formfaktor row omitted** (operator default). ⚠ **Consistency caveat (checked, not fiat):** there is **no omit/empty precedent** — all **829 cable parts carry a populated Formfaktor (0 omit, 0 empty)**, and the only other "MPO Kabel" parts (FG-TRAN-QSFP-4XSFP/4SFP-5) are **active QSFP28 modules** (FF correct, not comparable). So omitting for these 2 is a **new emitter behaviour** (the emitter currently always writes Formfaktor for cables) — a small pipeline branch for passive-fibre cables. Also their Anschlusstyp is empty (→ the 36-part adjacent gap below; should read "MPO auf 10× LC").

**FIX 3 — Arista far-end Anschlusstyp mislabel → RESOLVED this round; FOLDS into Phase-2 (per operator sequencing).** Full detail + spec rows: `ANSCHLUSSTYP_DELTA.md` / `.csv`.
- **Cross-brand sized: ARISTA-ONLY = 94.** Cisco (48 breakouts), Dell (47), NVIDIA (6), Fortinet (12), HPE (26), Juniper (12) all label breakouts correctly → **0 mislabels** elsewhere.
- **Count corrected 85→94 via DS grounding:** the Arista-DS spot-check proved **Q400 = QSFP112** (Q=single-QSFP, D=QSFP-DD), which both fixed the far-end FF AND **unmasked A-D400-Q400 ×9** that a derivation bug had hidden as "straight." True total = 94.
- **Host FF correct in all 94 → manifest Formfaktor rows unaffected; far-end-only.** Same text in the Artikelname → each fix = Anschlusstyp + Artikelname pair.
- **All 94 DS-grounded** (16 distinct mappings, each a verbatim arista-DS line). **6 spot-checks (#3): `4x QSFP28`** (50GBASE-CR2 = 2×25G NRZ → QSFP28 token; not bare QSFP, not the inferred 4×SFP56).
- **+36 empty-Anschlusstyp fills FOLDED** (HPE 26 + Fortinet 10) — **all 36 derived** (the 2 former HPE DERIVE-FAILs resolved: their names state "Breakout-AOC zu 4x SFP28" → **QSFP28 auf 4x SFP28**). **Anschlusstyp spec total = 130** (`ANSCHLUSSTYP_DELTA.csv`).
- **(#1) Länge provenance:** the 3 Arista `-3M` rows get a Verification_Log DS-deviation note (DS p24 typos them "2 meter"; corrected to 3m — must NOT revert to DS-2m).
- **FIX 2 addendum:** SR10 gets a Verification_Log note (passive MPO fibre, no module FF) + an import sanity-check (omitted Formfaktor row vs Ameise).
- **Folded into the same per-brand re-emit** as the value corrections (no separate pass). **Full Phase-2 spec (LOCKED, post-[VERIFY]) = PHASE2_MANIFEST.csv (140 value) + ANSCHLUSSTYP_DELTA.csv (132 = 94 Arista mislabel + 36 fill + 2 Cisco B20) + paired Artikelname for the 94 Arista. Residual ungrounded = 0; [VERIFY] CLEARED.**

## Formfaktor count reconciliation: 73 → 85 (unchanged by the 3 fixes)
73 (operator-reviewed) + 12 net-new = 85: C-Z100-2S50 ×3 (SFP-DD) · C-Y100-2S50 ×3 (DSFP) · FN-CABLE-QSFPDD-2QSFP56 ×2 (QSFP-DD) · FN-CABLE-QSFPDD-8SFP56 ×2 (QSFP-DD) · FG-CABLE-SR10 ×2 (now →empty, was the SR10 line). 6 original C-Y100 reclassified SFP-DD→DSFP (no count change). FF = within 70 + host 6 + DSFP 9 = 85. C-Y100 ×9=DSFP / C-Z100 ×9=SFP-DD (host = Anschlusstyp left-of-"auf"), 9+9=18, clean.

## Fortinet [VERIFY] — both grounded from cached DS (`fortinet-transceivers.pdf`)
- FG-TRAN-QSFP-4XSFP / 4SFP-5 → **KEEP QSFP28** (DS p15 "40G/100G … breakout"; dual-rate, 100G-capable shell). No change.
- FG-CABLE-SR10-SFP+ / +5 → passive MPO cable → **Formfaktor empty** (see FIX 2). Not CFP2.

## Still [VERIFY] (operator's court — NOT in the 124; current value kept + flag)
| Item | Count | Disposition |
|---|---|---|
| Cisco B-series Faseranzahl (QSFP-100G-B20U4-I / B20D4-I) | 2 | single-fiber vs duplex label conflict; needs Cisco B-series DS |
| Cisco non-DWDM-XFP-C DOM/temp suspects → 4 family Qs | 26 | DWDM/CWDM 1G DOM · MGB DOM · ONS temp/DOM |
| Juniper RX- legacy DOM | 3 | DOM=Ja kept (uncontradicted) |
_(Juniper -ET ×2 left this list → now manifest omissions, FIX 1.)_

## Prose riders (NOT in the 124 attribute-value rows — fold into the 409-prose pass)
- HPE S4B43A — Artikelname "200G QSFP-DD SR4" → **QSFP56** (match Formfaktor).
- Arista D800 ×11 — name generic "QSFP-DD" → optional tighten "QSFP-DD800".
- Arista far-end ×94 (FIX 3) — name+Anschlusstyp far-end pair.

## Exact-string confirms (byte-diff sensitivity)
- Cisco SFP-1G-SX / -1G-LH: "(COM)" tag → "-5 bis 85 °C **(EXT)**" — confirm tag convention.
- HPE JL745A/JL746A: "-40 bis +85 °C" (with "+") → "0 bis 70 °C" — confirm sign convention.
- FG-CABLE-SR10 Formfaktor empty: confirm emit-form (empty cell vs omitted row).

## Out of this manifest's scope (separate Phase-2 workstreams)
Sortiernummer 3-transposition reorder · G3 strip · 409-SKU prose re-author · Arista far-end pass (FIX 3, 94). This manifest = the **attribute-value** correction spec only.
