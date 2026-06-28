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

## PUSH 2A — Catalyst 4500-E modules (~22 PIDs) — WEIGHTS BLOCKED (decision needed)

**The blocker is a genuine OEM-source gap, not an unfetched courier.** A dedicated sub-agent
exhaustively checked, via Wayback + Cisco PDF mirrors:
- all 7 supervisor datasheets + their Installation & Configuration Notes (b-sup8e-note, b-sup8le-note,
  b-sup9e-note, 78_18337 Sup6-E, OL_19334 Sup6L-E),
- the Catalyst 4500 Series Line Cards Data Sheet (product_data_sheet0900aecd802109ea),
- the Catalyst 4500-E chassis + Module Installation Guide spec appendices.

**Cisco prints NO per-module weight (lb or kg) for ANY of these ~22 PIDs.** The E-generation moved
physical specs into the datasheets, and those list dimensions/temp/humidity/altitude/power/MTBF but
omit weight. The classic Module Installation Guide has only one generic 4.8 lb / 2.2 kg figure for
pre-E modules (does not apply). Reseller "weights" exist but are inconsistent shipping weights →
disallowed per the guardrails.

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
