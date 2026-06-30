# Cisco Switch Spec Grounding — B2/B3/B4/B5 (manifest)

**2026-06-30.** Official cisco.com datasheets fetched + cached to `datasheets/cache/cisco-switches/` (gitignored).
Result: **0 catalog edits** — every value is either datasheet-correct (confirmed verbatim) or unpinnable-from-Cisco
(kept per the "cannot be pinned → keep + log" rule). 19 SKUs · 20 SKU×attribute rows. validate_dir 0 · dedup 0.

| # | SKU | attribute | old → new | source (verbatim Cisco figure) |
|---|---|---|---|---|
| B2 | N9K-C9804 | Switching-Kapazität | `ZU_VERIFIZIEREN` → `ZU_VERIFIZIEREN` **(KEPT)** | Nexus 9800 DS `nexus9800-series-switches-ds.html` — **NO per-chassis system figure published** ("scale up to **230.4 Tbps**" series max; `115.2`/`57.6` **absent** from the doc; per-line-card **28.8 Tbps** 800G / **14.4 Tbps** 400G). 4-slot capacity is line-card-config-dependent (28.8×4=115.2 @800G, 14.4×4=57.6 @400G) → not cleanly derivable. |
| B3 | SX350X-24 | Durchsatz | `240 Mpps` → `240 Mpps` **(CONFIRMED)** | 350X DS `datasheet-c78-735986.html` — table "Capacity in Mpps (64-byte packets)" = **240.00** |
| B3 | SX350X-24F | Durchsatz | `240 Mpps` → `240 Mpps` **(CONFIRMED)** | 350X DS — **240.00** |
| B3 | SX550X-24 | Durchsatz | `240 Mpps` → `240 Mpps` **(CONFIRMED)** | 550X DS `datasheet-c78-735874.html` — Table 1 "Capacity in mpps" = **240.00** |
| B3 | SX550X-24F | Durchsatz | `240 Mpps` → `240 Mpps` **(CONFIRMED)** | 550X DS — **240.00** |
| B3 | SX550X-24FT | Durchsatz | `240 Mpps` → `240 Mpps` **(CONFIRMED)** | 550X DS — **240.00** |
| B4 | SG350X-8PMD | Switching-Kapazität | `80 Gbit/s` → `80 Gbit/s` **(CONFIRMED)** | 350X DS — "Switching capacity (Gbps)" = **80** |
| B4 | SG350X-8PMD | Durchsatz | `29,76 Mpps` → `29,76 Mpps` **(CONFIRMED)** | 350X DS — "Capacity in Mpps" = **29.76** |
| B5 | WS-C2960C-12PC-L | Switching-Kapazität | `6,4 Gbit/s` → `6,4 Gbit/s` **(KEPT, derived)** | 2960-C/3560-C DS `data_sheet_c78-639705.html` — **no per-model switching-capacity row**; Cisco prints flat **"Forwarding Bandwidth 10 Gbps"** per series + per-model mpps only |
| B5 | WS-C2960C-8PC-L | Switching-Kapazität | `5,6 Gbit/s` → `5,6 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C2960C-8TC-L | Switching-Kapazität | `5,6 Gbit/s` → `5,6 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C2960C-8TC-S | Switching-Kapazität | `5,6 Gbit/s` → `5,6 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C2960CG-8TC-L | Switching-Kapazität | `20 Gbit/s` → `20 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C2960CPD-8PT-L | Switching-Kapazität | `5,6 Gbit/s` → `5,6 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C2960CPD-8TT-L | Switching-Kapazität | `5,6 Gbit/s` → `5,6 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C3560C-12PC-S | Switching-Kapazität | `6,4 Gbit/s` → `6,4 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C3560C-8PC-S | Switching-Kapazität | `5,6 Gbit/s` → `5,6 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C3560CG-8PC-S | Switching-Kapazität | `20 Gbit/s` → `20 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C3560CG-8TC-S | Switching-Kapazität | `20 Gbit/s` → `20 Gbit/s` **(KEPT, derived)** | as above |
| B5 | WS-C3560CPD-8PT-S | Switching-Kapazität | `20 Gbit/s` → `20 Gbit/s` **(KEPT, derived)** | as above |

## Source URLs (one cited official cisco.com datasheet per item)
- **B2:** https://www.cisco.com/c/en/us/products/collateral/switches/nexus-9000-series-switches/nexus9800-series-switches-ds.html (C78-3007446; PDF cached, "230.4 Tbps" verified in-text, "115.2"/"57.6" absent).
- **B3+B4 (350X):** https://www.cisco.com/c/en/us/products/collateral/switches/350x-series-stackable-managed-switches/datasheet-c78-735986.html (240.00 / 80 / 29.76 verified).
- **B3 (550X):** https://www.cisco.com/c/en/us/products/collateral/switches/550x-series-stackable-managed-switches/datasheet-c78-735874.html (SX550X-24/-24F/-24FT = 240.00; SG550XG-24T sibling = 357.12).
- **B5 (2960-C/3560-C):** https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-2960-c-series-switches/data_sheet_c78-639705.html (one shared doc; "Forwarding Bandwidth 10 Gbps" per series; no per-model Gbps; per-model mpps 14.9/4.2/4.8).

## Secondary findings (flagged — NOT actioned, outside the named SKUs/attrs)
1. **N9K-C9808 (out of B2 scope):** the *existing* value `Bis zu 115,2 Tbit/s` is **not** in the current Nexus 9800 datasheet — the only system figure is the **230.4 Tbps** series max (800G), and per-chassis capacity is line-card-config-dependent. The "Bis zu 115,2" framing is likely wrong (115.2 = 4-slot@800G or 8-slot@400G, not an 8-slot max). **Recommend a separate re-ground of N9K-C9808** (and decide a config basis for both 9804 + 9808).
2. **B5 (operator decision):** Cisco publishes **no per-model switching capacity** for the 2960-C/3560-C — the catalog's 5,6/6,4/20 are internally derived (port×2). Cisco's only bandwidth figure is the flat **10 Gbps Forwarding Bandwidth** per series. Keep the derived per-model values, or switch all to Cisco's flat "10 Gbps"? (Kept for now per flag-don't-fabricate.)
3. **B3/B4 (note):** Cisco's own datasheets are conservative / internally inconsistent here — SX350X/550X-24 forwarding = 240.00 (below the 357.12 line-rate the SG550XG-24T sibling prints); SG350X-8PMD = 80 Gbps but 29.76 Mpps (omits the two 10G uplinks). The catalog **faithfully transcribes Cisco verbatim** — no "fix" applied to Cisco's numbers.
