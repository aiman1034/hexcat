# Anschlusstyp delta — DS-grounded (FIX 3, final)
_2026-06-17. Report-only; folds into the same Phase-2 re-emit as the value manifest. Spec rows: `ANSCHLUSSTYP_DELTA.csv` (130 rows = 94 mislabel-corrections + 36 fills)._

## Cross-brand sizing
- **"X auf X" mislabel = ARISTA-ONLY, 94** (Cisco/Dell/NVIDIA/Fortinet/HPE/Juniper label breakouts correctly → 0).
- **Empty-Anschlusstyp on breakouts = HPE 26 + Fortinet 10 = 36** (a *missing*-not-*wrong* gap; FOLDED per operator).
- **Total Anschlusstyp spec = 130.** Host FF correct throughout → the value manifest's Formfaktor rows are unaffected.

## Part 1 — 94 Arista mislabels: EVERY distinct mapping DS-grounded (not sampled)
Source: `arista-transceiver-datasheet.pdf` (re-extracted, temp off the full C: drive). 16 distinct host×ratio→far-end rules, each with a verbatim DS line:
| Family | corrected Anschlusstyp | DS evidence | n |
|---|---|---|---|
| CAB-O-2Q-400G | OSFP auf 2x QSFP56 | p14 "OSFP to 2 x 200GBASE-CR4 QSFP" | 3 |
| CAB-O-2Q-200G | OSFP auf 2x QSFP28 | p14 "OSFP to 2 x 100GBASE-CR4 QSFP" | 3 |
| CAB-O-4Q-400G | OSFP auf 4x QSFP28 | p14 "OSFP to 4 x 100GBASE-CR2 QSFP" | 3 |
| **CAB-O-4Q-200G** | **OSFP auf 4x QSFP28** | p14 "OSFP to 4 x 50GBASE-CR2 **QSFP**" (50GBASE-CR2 = 2×25G NRZ → QSFP28 token) | 3 |
| CAB-O-8S-400G | OSFP auf 8x SFP56 | p14 "OSFP to 8 x 50GBASE-CR SFP" | 3 |
| CAB-O-8S-200G | OSFP auf 8x SFP28 | p14 "OSFP to 8 x 25GBASE-CR SFP" | 3 |
| CAB-D-2Q/4Q/8S | QSFP-DD auf … (mirror of OSFP) | p17 (identical wording, QSFP-DD host) | 19 |
| H-O400-4Q100 | OSFP auf 4x QSFP28 | p14 "OSFP to 4 x 100GBASE-CR4 QSFP" | 4 |
| H-D400-4Q100 | QSFP-DD auf 4x QSFP28 | p17 "QSFP-DD to 4 x 100GBASE-CR4 QSFP" | 4 |
| A-O400-Q400 | OSFP auf QSFP112 | p3 "400G OSFP … to 400G QSFP112" | 9 |
| A-D400-Q400 | QSFP-DD auf QSFP112 | p3 "400G QSFP-DD … to 400G QSFP112" | 9 |
| A-O400-2Q200 | OSFP auf 2x QSFP56 | p6/p15 "OSFP to 2x 200G QSFP56" | 9 |
| A-D400-2Q200 | QSFP-DD auf 2x QSFP56 | p18 "QSFP-DD to 2x200G QSFP56" | 9 |
| C-Z100-Q100 | SFP-DD auf QSFP28 | p24 "SFP-DD to QSFP" (100GBASE-CR2) | 3 |
| C-Z100-2S50 | SFP-DD auf 2x SFP56 | p24 "SFP-DD to 2x 50GBASE-CR SFP" | 3 |
| C-Y100-Q100 | DSFP auf QSFP28 | p24 "DSFP to QSFP" | 3 |
| C-Y100-2S50 | DSFP auf 2x SFP56 | p24 "DSFP to 2x 50GBASE-CR SFP" | 3 |
| | | **Total** | **94** |
Same text is wrong in the **Artikelname** → each fix is an Anschlusstyp + Artikelname pair.

### The 6 spot-checks RESOLVED — inference overturned by the DS
CAB-O-4Q-200G ×3 + CAB-D-4Q-200G ×3 are **`4x QSFP28`, NOT `4x SFP56`** (DS p14/p17 explicitly "4 x 50GBASE-CR2 **QSFP**"). My earlier "4×SFP56" was inferred from per-lane 50G; the DS puts the 50G in a **QSFP**, not an SFP. Far-end token = **QSFP28** (50GBASE-CR2 = 2×25G NRZ lanes → the QSFP28 generation, matching the catalog's specific-token convention; not a bare "QSFP"). Shipped value would have been wrong — grounding caught it.

### Bonus DS finding — the Länge "2m" was a transcribed DS typo
DS p24 literally prints `C-Z100-Z100-3M … 2 meter` AND `…-2M … 2meter` (two "2 meter" rows → internal collision). So the emitted 2m on the three `-3M` parts faithfully copied an **Arista DS typo**; the value-manifest 2m→3m correction is right and now has its origin explained.

## Part 2 — 36 empty-Anschlusstyp fills (HPE 26 + Fortinet 10), FOLDED
Derived from the topology-bearing names ("400G Breakout-AOC zu 4x QSFP…") + host = the part's Formfaktor + MSA. **All 36 derived (0 DERIVE-FAIL after the HPE names resolved them).**
- HPE: R9B48-52A →"QSFP-DD auf 4x QSFP28"; R9B53-57A →"QSFP-DD auf 2x QSFP56"; R9B58-62A →"QSFP-DD auf 2x QSFP28"; S4B41/42A →"QSFP-DD auf 8x SFP56"; S4B39/40A →"QSFP-DD auf 8x SFP28"; R6F24-26A →"QSFP56 auf 2x QSFP28"; 845416-B21 →"QSFP28 auf 4x SFP28"; 721064-B21 →"QSFP+ auf 4x SFP+".
- Fortinet: FN-CABLE-QSFP+7-4PACK →"QSFP+ auf 4x SFP+"; FN-CABLE-QSFP28-4SFP28-* →"QSFP28 auf 4x SFP28"; FN-CABLE-QSFPDD-2QSFP56-* →"QSFP-DD auf 2x QSFP56"; FN-CABLE-QSFPDD-8SFP56-* →"QSFP-DD auf 8x SFP56"; FG-CABLE-SR10-SFP+/+5 →"MPO auf 10x LC (für 100GBASE-SR10 CFP2)".
- **2 former DERIVE-FAIL → RESOLVED:** HPE **845420-B21, 845424-B21** → **"QSFP28 auf 4x SFP28"**. Their own Artikelnamen state "Breakout-AOC zu 4x SFP28" (AOC 7m/15m siblings of 845416-B21, the 100G DAC); the earlier fail was only a missing speed-*prefix* in my regex — the topology is stated outright, host=Formfaktor QSFP28 (confirmed). Not in the cached HPE DS (grep empty), but name-grounded like the other 34 fills — not a guess.
- **Cross-dependency handled:** the 6 fills that are ALSO value-corrections use the *corrected* host FF — FN-CABLE-QSFPDD ×4 → host QSFP-DD (not the QSFP56/SFP56 being fixed); FG-CABLE-SR10 ×2 → "MPO auf 10x LC" (Formfaktor omitted per FIX 2).

## FIX 2 addendum — SR10 Verification_Log note
For FG-CABLE-SR10-SFP+/+5, log in Verification_Log: *"Passives OM3-MPO-zu-10×LC-Glasfaser-Fanout (mating mit separatem 100GBASE-SR10 CFP2-Modul); kein Modul-Formfaktor → Formfaktor-Zeile entfernt."* Import sanity-check: confirm an omitted Formfaktor row doesn't trip Ameise (no precedent — 829/829 cables currently populate it).

## Full Phase-2 spec (one re-emit per brand, all corrections together)
- `PHASE2_MANIFEST.csv` — **124** value corrections
- `ANSCHLUSSTYP_DELTA.csv` — **130** Anschlusstyp (94 Arista mislabel + 36 fill) + paired Artikelname for the 94
- **Residual ungrounded: 0 — spec fully locked.** (The 2 HPE were filled from their own names; the 6 spot-checks are QSFP28; the Länge typo has DS-deviation provenance.)
