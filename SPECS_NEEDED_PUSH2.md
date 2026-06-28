# SPECS_NEEDED — Batch M-1 PUSH 2

Courier-blocked / decision-needed specs for the Catalyst 4500-E + Nexus 7000/7700 module lane.
Same loop as the 9 PUSH-1 weights: I hold the field, you courier/decide, I fill + (re)push.

---

## PUSH 2B — Nexus 7000/7700 modules (43 PIDs) — NOTHING BLOCKED
All 43 weights grounded verbatim (sups + fabric from Cisco datasheets; I/O linecards from the
Nexus 7000/7700 Hardware Installation Guide *Switch Specifications* appendices). No `<PEND>`.
Built + pushed this turn. **One encoding decision logged (not blocking)** — the M2 trio
Switching-Kapazität: I encoded the Cisco **product-bulletin per-module** figure (240/240/200 Gbit/s
for M224XP-23L / M206FQ-23L / M202CF-22L) rather than the datasheet's raw Switch-Fabric-Interface
number (550/230 Gbit/s), because the per-module figure is the module's actual switching capacity and
keeps the bundle consistent with the F-series. Both are Cisco-verbatim; the datasheet figure is in
each card's Verification_Log. Say the word if you prefer the datasheet representation.

---

## PUSH 2A — Catalyst 4500-E modules (22 PIDs) — RESOLVED & SHIPPED (scoped weight exception)

**Final operator decision (2026-06-28):** the 4500-E per-module weights are **NOT OEM-published anywhere**
(auditor confirmed exhaustively — Module Install Guide App-A = pinouts/environmental/power, chassis guides
carry chassis weight only, Sup9-E datasheet has no weight row) AND **no supplier/warehouse feed exists**
(BrokerBin off the table; the earlier "in the install guides / IP-blocked" framing is withdrawn). The 22
legacy EoS SKUs were deliberately **closed WITHOUT grounded weights** — an explicit, documented exception
to the nothing-guessed bar, scoped to these 22 only.

**Outcome:** EMPTY weights were tried first (preferred) but **fail the gate** (the emit defaults an empty
weight to the 0,05 optics-placeholder, tripping the switch-weight-floor). So per the operator's fallback,
the 22 shipped with **conservative ZU_VERIFIZIEREN placeholders** (Sup 7,00 / 48-port 6,00 / smaller 5,00
kg; over-estimated so shipping is never under-quoted; NOT measured, NOT sourced; VLog flagged). Only open
item: a physical-measurement weight follow-up. Built + pushed; see PROJECT_AUDIT §9.

---
### (historical) the 22 PIDs that needed a weight:

### The 22 PIDs needing a weight (artikelgewicht is a core Main-CSV field — can't ship blank):
**Supervisors (7):** WS-X45-SUP6-E, WS-X45-SUP6L-E, WS-X45-SUP7-E, WS-X45-SUP7L-E, WS-X45-SUP8-E,
WS-X45-SUP8L-E, WS-X45-SUP9-E
**Linecards (15):** WS-X4748-12X48U+E, WS-X4748-UPOE+E, WS-X4748-RJ45V+E, WS-X4748-RJ45-E,
WS-X4748-SFP-E, WS-X4712-SFP+E, WS-X4724-SFP-E, WS-X4712-SFP-E, WS-X4624-SFP-E, WS-X4612-SFP-E,
WS-X4640-CSFP-E, WS-X4648-RJ45-E, WS-X4648-RJ45V-E, WS-X4648-RJ45V+E, WS-X4606-X2-E

### Options for you (PUSH 2A):
1. **Courier a weight source** Cisco never web-published (a physical-scale sheet, the Cisco ordering
   tool's shipping weight clearly labelled as such, or a print install note you hold) → I ground + build.
2. **Ship 2A with all weights ZU_VERIFIZIEREN** — but unlike the C6880-X (where a chassis-derived
   ~2,72 kg estimate existed), here there is **no defensible estimate at all**, so this means shipping
   a placeholder artikelgewicht I'd have to invent → I do NOT recommend it (violates nothing-guessed).
3. **Hold 2A** until a weight source lands; PUSH 2B (Nexus) ships now and resolves one of the two
   catch-alls.

### Other PUSH 2A open items (independent of weights):
- **TAA `++` linecards:** Cisco's EoS notice c51-737185 lists `++=` *spare* PIDs for every E-series
  linecard, but I found no bare `…++` orderable PID in any Cisco doc. Per flag-don't-fabricate I would
  **exclude** the unconfirmed `++` variants unless you confirm they're separately orderable.
- **Classic (non-E) 4500 linecards** (WS-X4548-*, WS-X4448-*, etc.) are forward-compatible with the
  4500-E chassis but are branded "Catalyst 4500" not "4500-E" → excluded from the 4500-E set unless you
  want them banked under a "Catalyst 4500" Kompatible Serie.
