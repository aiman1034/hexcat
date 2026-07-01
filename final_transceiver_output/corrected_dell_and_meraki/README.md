# Corrected Dell + Meraki content (2026-07-01)

Ready-to-import, corrected content. **`Dell/` = only the 24 AFFECTED part numbers** (not the
full 156-SKU Dell catalog) — re-importing it touches nothing else. **`Meraki/` = all 23**
(every Meraki transceiver changed). Byte-exact rows filtered from the full corrected bundles;
same CSV formats as the rest of `final_transceiver_output`. Roster, prices, and Beschreibung
are unchanged from the originals — only the fields listed below were touched.

## Dell/ — 24 affected part numbers (of 156), 3 corrections
Breakdown by reason:
- **SFP-DD form factor (3):** `S56DD-100G-FR / -LR / -SR1.2` — re-import to restore the SFP-DD
  category (undo the JTL rename to "SFP").
- **QSFP28-DD → QSFP-DD (16):** `Q28DD-200G-2SR4` (the E3-category product) + the 15 `Q28DD-*`
  DAC/AOC cables (their `Formfaktor` attribute) — re-import to fix the form factor.
- **`*` stripped (5):** `AEC-O112-800G-2M / -3M / -4M`, `400G-Q56DD-ZR+`, `800G-O112-2FR4` —
  corrected part numbers (the `*` was a Dell footnote, not part of the SKU).

The corrections themselves:
1. **SFP-DD kept as its own category.** SFP-DD is a real MSA form factor; the 3 modules
   `S56DD-100G-FR / -LR / -SR1.2` are genuine 100G SFP-DD (do NOT merge into "SFP" = 1G).
2. **`QSFP28-DD` → `QSFP-DD` everywhere.** "QSFP28-DD" is not a standard MSA name; the real
   double-density QSFP form factor is `QSFP-DD` (which the sheet already uses). Applied to the
   E3 category of `Q28DD-200G-2SR4`, the `Formfaktor` attribute + `Anschlusstyp` + prose of all
   `Q28DD-*` parts (they physically use the QSFP-DD connector). Part numbers (which literally
   contain "Q28DD") are unchanged. Not "QSFP28" (that's a different single-density 100G module).
3. **Trailing `*` stripped from 5 PIDs.** The `*` was a Dell datasheet footnote ("Supported in
   upcoming software release"), not part of the SKU. Corrected in every Dell file:
   `400G-Q56DD-ZR+`, `800G-O112-2FR4`, `AEC-O112-800G-2M / -3M / -4M`. URL-Pfad + Artikelnummer
   kept consistent.

## Meraki/ — Meraki is a Cisco brand (like Aruba is an HP brand)
- **Hersteller `Meraki` → `Cisco`** on all 23 transceivers.
- **URL slug `meraki/` → `cisco-meraki/`** (URL-Pfad `cisco-meraki/<sku>`), matching the Cisco
  Meraki switch line + the Aruba→`hpe-aruba` precedent. Titles/meta already read "Cisco Meraki".

## JTL re-import notes
- Dell: re-import the affected rows — the 1 QSFP28-DD product now lands in **QSFP-DD**; the 5
  `*`-suffixed SKUs now have clean part numbers.
- Meraki: URLs changed to `cisco-meraki/<sku>` + Hersteller Cisco — re-import or add redirects
  from the old `meraki/<sku>` URLs.
