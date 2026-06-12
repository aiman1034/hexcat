# HexCat — Stage-1 Ledger Status

_Cross-session continuity ledger. Updated at end of each working block. Pairs with ruflo
memory (`hexcat/*`). The autonomous audit→fix→re-verify loop reads this to resume._

## Current state (2026-06-12) — autonomous directive in force

**Verifier-gated pipeline live.** Every mine is independently re-derived and audited (V1–V8)
before the ledger is accepted; a non-passing ledger is NOT written (CLI exits 1). Audit
reports (`Audit_Report_{Brand}.md` + `.json`) are written per source to the `--out` dir.
**Multi-source merge works via `--source all`** (one ledger from N datasheets; `write_workbook`
takes the list of per-source results; each source independently V1–V8 gated).

### §7 Dashboard (computed from files 2026-06-12)

| Brand    | Ledger SKUs | True scope | V1–V8 | V9 coverage | Stage-3 | Status |
| -------- | ----------- | ---------- | ----- | ----------- | ------- | ------ |
| Cisco    | **297** (29 sources) | full Eth line | GREEN (all 29 src) | **PASS 19/19** | **PRICES-PENDING (297/297 authored)** | **DONE-VERIFIED + CONTENT-COMPLETE** (only operator Netto-VK outstanding) |
| Fortinet | 87 (1 datasheet) | whole line, 1 sheet | GREEN | **PASS 12/12** | NOT-STARTED | **DONE-VERIFIED** (V9 calibrated-complete; whole-line datasheet) |
| HPE/Aruba| 147 (AOS-S/CX guide) | AOS-S/CX only | GREEN | **PASS 9/9** | NOT-STARTED | **DONE-VERIFIED** (V9 calibrated to sourced line; FlexFabric/Comware = SKU-breadth gap, tracked) |
| MikroTik | **24** (1 card-grid page) | whole SFP/QSFP line | GREEN | **PASS 7/7** | NOT-STARTED | **DONE-VERIFIED** (HTML card-grid mode; 1 converter flagged-not-emitted; whole-line page) |
| Brocade  | — | FC (out of scope) | — | — | — | PARKED (operator decision) |
| 13 others| 0 | not enumerated | — | — | — | NOT-STARTED |

**DONE-VERIFIED count: 4** (Cisco, Fortinet, HPE, MikroTik pass the full V1–V9 gate). Fortinet/HPE V9
calibrated 2026-06-12: Fortinet expected=12 families (its own whole-line ordering datasheet is
self-complete → calibrated-COMPLETE); HPE expected=9 families (one per AOS-S/CX guide chapter +
DAC/AOC). HPE's FlexFabric/Comware line is a SKU-BREADTH gap *within* these same form factors
(V9 keys on form factor, not product line), so it is tracked in STATUS, not asserted as a missing
V9 family — closing it = mine the FlexFabric source as an ADDITIONAL merged source, not a coverage
edit. Coverage_Report_{Fortinet,HPE}.md written. V9 (catalog-coverage) is BUILT:
config-driven per-brand `coverage.expected_families`; runs on the MERGED ledger; each expected
locked-22 family must have ≥1 SKU else KNOWN-INCOMPLETE (names the gap) and DONE-VERIFIED is
blocked. `verify_ledger_spec` guards every coverage family is locked-22 AND reachable by a rule.
A spec with no coverage set → V9 FAILs as UNCALIBRATED (never silently certifies). Stage-3 state:
NOT-STARTED / GENERATED / PRICES-PENDING / IMPORT-READY (IMPORT-READY only when generated +
content-verified + prices filled).

### Stage-3 v5.0 package generator (BUILT) + Cisco content authoring (COMPLETE 2026-06-12)
The byte-exact JTL-Ameise package generator is built and matches the authoritative proof slice
(`Corrected 7 Part Numbers/Cisco_Audit_7SKUs_*.csv`): 5 CSVs (Main `_v5_0`, Attributes, Platform,
Prices [semicolon], Verification_Log), UTF-8 BOM + CRLF, csv-minimal quoting. Key facts learned
from the slice: the **Beschreibung is a composed HTML document**, not free prose — 3 intro `<p>`,
a `Technische Daten` `<ul>` (rendered FROM the verified attributes → single source of truth, never
drifts from Attributes.csv, Zustand excluded, empty GTIN li), an optional `Kompatibilität` `<ul>`
+ fixed TMG matrix note, the FAQ as `<p><strong>Q?</strong><br>A</p>` blocks, and a `Verwandte
Produkte` `<ul>` of slugged in-catalog links. `compose_beschreibung` builds this deterministically;
`content_issues` gates each SKU (kurz 2p/40-80w, intro 3p/90-175w, titel ≤60 ending `| Hexwaren`,
meta 140-200, FAQ 3-10 — NO Phase-2 closer; the slice carries authenticity in FAQ/meta).

**Workflow:** `hexcat stage3-template` emits the JSON content sidecar (one entry/SKU: `_facts` with
source URL = the author's spine, blank prose, derivable attrs pre-seeded). Author fills it IN-SESSION
($0, datasheet round-tripped, every spec → provenance, flag-or-omit unverifiable). `hexcat stage3
--content <sidecar>` ingests it → composes Beschreibung, lifts state. **Canonical authored sidecar =
`stage3_content/Cisco_content.json` (TRACKED; `output/` is gitignored runtime).** Datasheets cached
locally in `datasheets/cache/` → authoring is fully offline/$0. 297 SKUs map to 29 cached datasheets.

**Progress: 297/297 authored — COMPLETE (commit 156b944). State = PRICES-PENDING.** All 19 families
authored in-session ($0, datasheet round-tripped, flag-or-omit): X2 (8), CPAK, SFP, SFP+, SFP28,
SFP56, QSFP+, QSFP28, QSFP56, QSFP112, QSFP-DD, QSFP-DD800, OSFP, XFP, CFP, CFP2, CXP, DAC, AOC, plus
7 singletons (DWDM-XFP-C, CFP2-100G-ER4, DP01QSDD-ZF1, DP04QSDD-HE0, DP04CFP2-D15, DWDM-SFP-6141,
SFP-10G-OLT20-X). Content gate (`content_issues`) passes for all 297. Only operator-supplied Netto-VK
remains before IMPORT-READY. Notable flag-don't-emit calls: CFP-100G-SR10 DOM "Nein (laut Datenblatt)";
DP01QSDD-ZF1 modulation QPSK per line-mode (datasheet "16QAM" column treated as typo); DWDM-SFP-6141
DOM not asserted; coherent DCOs assert only datasheet-stated power/temp/connector.

### Cisco corrected: 35 → 297 (root cause = single-datasheet trust)
The old 35 was ONLY the 10G SFP+ datasheet (`c78-455693`). Enumerated **48** Cisco transceiver
sources from the seed; **29** mine cleanly into **297 distinct SKUs** spanning 19 locked-22
families: SFP 60, DAC 59, AOC 39, SFP+ 21, QSFP28 19, QSFP-DD 17, CPAK 12, QSFP+ 12, SFP28 10,
XFP 9, SFP56 8, X2 8, CFP 6, OSFP 5, QSFP56 3, QSFP112 3, CFP2 2, CXP 2, QSFP-DD800 2.
Curated seed = `Cisco_Transceivers_SEED.xlsx` (drops 2 non-transceiver datasheets: the M12
fibre-patch-cable sheet and the PON-ONT sheet). Build: `--seed Cisco_Transceivers_SEED.xlsx
--source all --spec config/ledger/cisco_transceivers.yaml`.

### NEW bug class fixed → regression test
7. **Single-datasheet undercount + form-factor misclassification** — the Cisco spec defaulted
   every PN to "SFP+ (10G)". Now multi-family classify rules (PN-prefix, grounded in the 297-PN
   corpus) map each family to its locked-22 token; `test_classify_multi_family` freezes 27 cases.
8. **Flag-don't-emit `exclude`** — new spec block (`exclude:` list, `spec.is_excluded()`) drops
   non-transceiver tokens (CVR converter adapters, licenses/RTUs) from BOTH the emitted ledger
   AND the verifier's authoritative set (symmetric → V7/V8 stay honest). `test_exclude_flags_
   non_transceivers`. Applied in engine.run_source (→ flagged) + verify_ledger (token filter).

Fortinet true count is **87** (not the old mis-mined 90). DR4 and DR4+ both present (distinct).

### Bug classes fixed (each → permanent regression fixture/test)

1. **Description-bleed phantoms** — column x-band extraction isolates the authoritative SKU
   column from Description prose. (Fortinet: 4 FN-TRAN-1B{U,D}{10,40} phantoms gone.)
2. **Trailing-`+` stripping** — PN/SKU regex preserves a trailing `+`; whole-token verbatim
   check. DR4 vs DR4+ stay distinct; ADASFP+ / SR10-SFP+ no longer mangled.
3. **DAC/AOC/MPO misclassification** — one universal rule
   `classify_cable_from_description()` (spec.py), description-derived, identical across ALL
   brands. `resolve_unterkategorie()` precedence: description-cable → section hint → PN rules.
4. **Pack-of-four Notiz** — `_pack_notiz()` flags `-4PACK` / "pack of four".
5. **Unified taxonomy** — DAC Kabel / AOC Kabel / MPO Kabel are `UNIVERSAL_CABLE_CATEGORIES`,
   emittable by any brand (verify_ledger_spec whitelists them).
6. **Genericized brand labels** — workbook.py/cli.py no longer hardcode "Cisco".

### Verifier (src/hexcat/verify/)
- `extract.py` — independent 2nd-method re-derivation (column / section / HTML paths).
- `checks.py` — V1 verbatim · V2 authoritative-locus provenance · V3 no silent collision ·
  V4 separator integrity (`and st not in emitted_set` guards the both-forms-emitted case) ·
  V5 classification · V6 switch exclusion · V7 completeness (symmetric diff) · V8 count honesty.
- `verifier.py` — orchestrates V1–V8, `verify_source_result()` bridges engine→verifier,
  `write_audit_report()`.
- **Calibrated:** all-green on clean Cisco (true negative) AND flags exactly the listed
  Fortinet defects on the pre-fix mine (true positive). Does not cry wolf.

### Tests: **137 passing** (incl. V9 calibration for Cisco/Fortinet/HPE/MikroTik + 5 new
card-grid tests: V5 active-optics→AOC, `mine_html_cards` full 25-card enumeration, engine
classify+converter-exclude (24, exact family split), card 2nd-path V1–V8 all-green with locus
`card` authoritative, MikroTik spec coverage calibrated). Frozen on synthetic tokens + committed
fixtures (`sample_ordering_columns.pdf`, cached `datasheets/cache/sfp-qsfp.html`).

### CLI
`python -m hexcat.cli ledger --seed <seed.xlsx> --source <id|all> --spec
config/ledger/<brand>_transceivers.yaml --out output/<Brand>_Ledger.xlsx --no-network`
(new `--spec` option selects the per-brand mining spec; default = Cisco pilot.)

## Remaining-brand triage (2026-06-12 fetch probe)

Probed all 12 non-Juniper remaining brands Tier-1 (network IS up — 404s prove reachability).
**Every recorded seed URL in `inputs/brand_sources.xlsx` is stale, wrong, JS-gated, or FC-only.**
No remaining brand can be cleanly auto-mined into the locked-22 Ethernet taxonomy yet.

| Brand        | Source status from cached/probed fetch                            | Action needed |
| ------------ | ----------------------------------------------------------------- | ------------- |
| Brocade      | VALID PDF but **Fibre-Channel** "Transceiver Support Matrix" — wide multi-col Gen5/6/7/8, XBR-*/57-* PNs | **PARKED — OUT OF SCOPE this pass** (operator decision 2026-06-12). FC ≠ Ethernet protocol/domain; do NOT map XBR-/57- onto Ethernet form-factor buckets (an FC SFP+ is not a 10GBASE-SR SFP+ → wrong specs) and do NOT alter locked-22. If FC is later confirmed in-scope, build as a SEPARATE batch with dedicated FC Unterkategorien + FC-specific spec/voice templates. Not deleted; revisit on explicit go-ahead. |
| Ubiquiti     | JS-shell (accessories.html: 1.6KB rendered text, 107 UACC-* only in script JSON) | §6b NEEDS-HEADED (Tier-2 render) |
| Juniper      | hCaptcha-gated Next.js SPA                                          | §6b NEEDS-HEADED |
| Arista       | fetched 3KB stub — corrupt, "No /Root object" (error page as .pdf) | fresh official QRG URL |
| Huawei       | fetched HTML is a **404** page                                     | fresh official URL |
| Lenovo/IBM   | lp1042.pdf is the **wrong doc** (ThinkSystem SD650 server guide)   | correct transceiver-reference URL |
| Dell         | Tier-1 fetch failed (stale/blocked)                                | fresh URL / Tier-2 |
| NVIDIA       | Tier-1 fetch failed                                                | fresh URL / Tier-2 |
| Palo Alto    | Tier-1 fetch failed                                                | fresh URL / Tier-2 |
| MikroTik     | **DONE-VERIFIED 2026-06-12** — card-grid mode, `sfp-qsfp` page, 24 SKUs, V1–V9 PASS | — (done) |
| Supermicro   | Tier-1 fetch failed                                                | fresh URL / Tier-2 |
| Ruijie       | Tier-1 fetch failed                                                | fresh URL / Tier-2 |
| Avaya/Extreme| Tier-1 fetch failed (JS-grid per notes)                            | §6b NEEDS-HEADED |

## Extraction-mode boundary (learned 2026-06-12, Arista)

The deterministic miner needs an **authoritative SKU locus** to mine + verify against. It
currently supports exactly **three** source shapes:
- **token+column** — a two-column SKU/Description "Ordering Information" table (Cisco HTML,
  Fortinet PDF).
- **section** — form-factor chapters with `<noun> (SKU)` callouts (HPE PDF).
- **card** (BUILT 2026-06-12) — an HTML product-card GRID with no `<table>`: each product is a
  `div[wire:key^="product-"]` card whose authoritative SKU is the deep-link title
  `<a title="{prefix}{CODE}">` and whose blurb is a line-clamped `<p>` (feeds V5). Config:
  `mine.html.mode: card` + `card_title_prefix` + `desc_class_contains`. Miner `mine_html_cards`
  (DOM walk); independent 2nd path `extract_authoritative_html_cards` (regex over `wire:key`
  chunks → locus **`card`**, added to the shared `AUTHORITATIVE_LOCI`). Proven on MikroTik
  `sfp-qsfp` (24 emitted + 1 converter flagged; V1–V9 PASS).

It does **NOT** support **prose / spec-sheet** datasheets where orderable PNs are scattered
through descriptive text and the only tables are spec-attribute matrices (wavelength, reach,
power) keyed by form factor. Confirmed on Arista's official `Transceiver-Data-Sheet.pdf`
(29 pp, 24 tables, ~6 PN tokens in any table; PNs live in prose). Force-mining such a source
would manufacture the exact phantom class V2 (authoritative-locus) is built to reject — so the
verifier would (correctly) refuse the ledger. These brands need EITHER a different official
document with a real ordering table/part-number appendix, OR a new extraction mode with a
defensible locus. **Do not lower V2 to admit prose.**

Probable bucket for the remaining brands (to confirm per-brand next pass):
- prose spec-sheet → needs ordering-guide source or new mode: Arista (confirmed), likely
  NVIDIA, Dell, Palo Alto, Huawei.
- HTML **product-card grid** (no <table>, PNs in card markup) → card-extraction mode now BUILT:
  MikroTik **DONE** (24 SKUs); apply same mode to Supermicro, Ruijie (likely same shape).
- NEEDS-HEADED: Ubiquiti, Juniper, Avaya/Extreme.

### Fresh official URLs found 2026-06-12 (so next pass skips the search)
- MikroTik (current group page; old /group/optical-modules now 404):
  `https://mikrotik.com/products/group/sfp-qsfp` — server-rendered card grid, ~10 SFP PNs
  visible (S+RJ10, S-31DLC20D, S+31DLC10D, S+85DLC03D, S-3553LC20D, …), 0 tables.
- Arista data sheet (fetched OK, but prose — see boundary above):
  `https://www.arista.com/assets/data/pdf/Datasheets/Transceiver-Data-Sheet.pdf`;
  also the compatibility guide `https://www.arista.com/assets/data/pdf/Transceiver-Guide.pdf`
  (untried — may be more table-structured).
- Palo Alto datasheet landing (not a direct PDF):
  `https://www.paloaltonetworks.com/resources/datasheets/key-specs-for-paloalto-interface-transceivers`

## Next steps
- **Source acquisition is the gate**, not spec authoring. Next autonomous pass: for the
  stale-URL brands (Arista, Huawei, Lenovo, Dell, NVIDIA, Palo Alto, MikroTik, Supermicro,
  Ruijie) find the *current* official transceiver datasheet URL (web search ok — still
  "official manufacturer source"), re-fetch (Tier-2 render where JS-gated), then author a
  per-brand spec → mine → verify-gate PASS → ledger+audit → full suite green.
- **Escalated to human (§6):** (b) NEEDS-HEADED: Ubiquiti, Juniper, Avaya/Extreme;
  (c) Brocade Fibre-Channel optics — RESOLVED 2026-06-12: PARKED out-of-scope, do not map
  onto Ethernet taxonomy, revisit only on explicit go-ahead with dedicated FC categories.
- Loop now targets the other 17 brands (Brocade parked).
- Invariant for every new brand: a fix for brand N must not regress 1…N-1 (full suite green).
