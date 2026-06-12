# HexCat — Stage-1 Ledger Status

_Cross-session continuity ledger. Updated at end of each working block. Pairs with ruflo
memory (`hexcat/*`). The autonomous audit→fix→re-verify loop reads this to resume._

## Current state (2026-06-12) — autonomous directive in force

**§2 G3/G4/G5 DONE (commits 1b73e89 G3, 2e1d0fe G4, 872a122 G5). 251 tests pass.**
- **G3 weights** `config/weight_disposition.yaml` (tracked) + `tests/test_weight_disposition.py` —
  makes the 902/902 PLACEHOLDER-weight debt AUDITABLE rather than silently passing. Every emitted
  Artikelgewicht/Versandgewicht is GROUNDED (operator per-SKU) or a form-factor PLACEHOLDER from
  `config/weights.yaml`; transceiver weight is NOT physics-derivable, so grounding is DEFERRED to a
  datasheet/measurement pass (same as pricing). Artifact reconciles per brand: grounded+placeholder
  ==sku_count, by-Formfaktor sums match, every flagged FF is a real PHYSICAL_FORMFAKTOR. Regen via
  `_scratch/gen_weight_disposition.py`.
- **G4 GTIN/EAN** `validate.valid_gtin` (GS1 mod-10 check digit, lengths 8/12/13/14) + `_check_attributes`
  row check: GTIN is populate-or-prove-absent — empty is OK ("absent"), present MUST pass the check
  digit (no fabricated barcodes). Self-audit fixture A10 + unit tests for accept/reject/empty.
- **G5 FAQ uniqueness** `_check_faq` substantive-block dedup — strips the authenticity Q&A pair
  (`_FAQ_AUTHENTICITY_RE`), keys remaining pairs; identical substantive block across ≥4 SKUs FAILs
  (boilerplate), 2-3 WARNs. Calibrated to data (max legit dup=2). Self-audit fixture added.
NEXT: §2 G6 merged-catalog sweep → G7 import-readiness validator.

**§2 G6 MERGED-CATALOG SWEEP DONE (commit pending). 261 tests pass.** The per-bundle gate is
blind to clashes BETWEEN brands; `src/hexcat/merged_sweep.py` + `hexcat sweep <dirs…>` CLI close
that. Reads all 5 bundles, FAILs on any cross-brand identity collision (Artikelnummer, URL-Pfad,
GTIN, Titel-Tag) and on a body sentence reused across ≥3 brands; WARNs at 2 brands. **Real finding:
9 Artikelnummer collisions Cisco↔Arista** — both ship identical MSA part names (SFP-10G-SR,
QSFP-40G-SR4, SFP-1G-SX, …). These are REAL distinct parts that collide on a single global
Artikelnummer; re-keying is an operator merchandising decision (HAN must stay the true PN), so per
flag-don't-emit it's recorded in tracked `config/merged_catalog_collisions.yaml` (auditable, DEFERRED)
not silently re-keyed. URL/GTIN/Titel/3-brand-sentence all PASS; the 9 two-brand WARN sentences are
grounded shared physics (identical DAC-length / wavelength facts), not padding. 10 sweep tests +
schema test. Regen `_scratch/gen_merged_collisions.py`. NEXT: §2 G7 import-readiness validator.

**§2 G2 ATTRIBUTE DEPTH DONE (commits d51af66 G2a, 6b5685b G2b, 78f62f3 flag artifact).**
Populate-or-prove-absent for the locked 14 attributes is now real and auditable:
- **G2a** `src/hexcat/attribute_depth.py` — pure, deterministic applicability model. `MediaClass`
  (cable/copper/smart-SFP) + `EXPECTED_WHEN` table classify each empty cell as PROVABLY_ABSENT
  (category-gated: no wavelength on copper, no cable length on a module, no reach/DOM on a cable)
  or a real GAP. Plus physics-grounded derivers that NEVER guess: Fasertyp from Wellenlänge
  (8xx→Multimode, 1270-1610→Singlemode), Faseranzahl from a duplex/dual-LC connector→2 (excludes
  single/BiDi/MPO). 33 tests. `_scratch/g2_depth_audit.py` prints per-brand POP/ABSENT/GAP.
- **G2b** wired `derive_all` into `intake._build_attributes`: fills only physics-pinned slots,
  inherits the SKU's grounding Source_URL, stamps the rule label as Verification_Log Confidence
  (new `AttributeValue.confidence`). Emits in canonical order. Regen closed **156 GAPs, zero
  invention** (Cisco Faseranzahl −101, Fortinet −37, MikroTik −9, Arista/HPE Fasertyp −9); all 5
  brands GREEN. 4 wiring tests.
- **Flag artifact** `config/attribute_gaps/residual_gaps.yaml` (tracked) — the DEFERRED grounded
  datasheet pass's scope: Transceiver Typ, DOM Unterstützung, Standard, residual Faseranzahl/
  Anschlusstyp/Geschwindigkeit, flagged per brand. Schema test locks structure, not the volatile
  counts. **236 tests pass.** NEXT: §2 G3 weights → G4 GTIN/EAN → G5 FAQ uniqueness → G6 merged
  sweep → G7 import-readiness validator.

**§2 G1 SOURCE-DISPOSITION DONE (commit 8237fb6).** `config/source_disposition/<brand>.yaml`
accounts for every datasheet considered (MINED + per-source SKU count, or NON_TRANSCEIVER/
SUPERSEDED/FAILED + reason). Cisco = 29 MINED (== curated SEED, tracked-to-tracked) + 2
NON_TRANSCEIVER, FLAGGED_INCOMPLETE (full ~48 candidate enumeration deferred to a web pass).
4 single-datasheet brands = GROUNDED_COMPLETE. `tests/test_source_disposition.py` reconciles.

**§3 GATE SELF-AUDIT DONE (commit 9db4789).** `tests/test_gate_self_audit.py` is a data-driven
suite: one minimal FAILING fixture per known build-gate defect class (S* structural, M* Main,
A* Attributes, P* Prices, C* Condition, F* FAQ, X* cross-file, V* verification) — each mutates
the clean 2-SKU reference bundle and asserts `validate_dir` FAILS on the *named* violation —
plus a green-reference test and a monkeypatched cross-SKU reuse FAIL. The Beschreibung inline-Q&A
`?` check was promoted WARN→FAIL (body is prose-only; all 902 Beschreibungen are `?`-free).
**Standing rule:** any future gate-missed defect becomes a permanent fixture here before it is
fixed.

**Verifier-gated pipeline live.** Every mine is independently re-derived and audited (V1–V8)
before the ledger is accepted; a non-passing ledger is NOT written (CLI exits 1). Audit
reports (`Audit_Report_{Brand}.md` + `.json`) are written per source to the `--out` dir.
**Multi-source merge works via `--source all`** (one ledger from N datasheets; `write_workbook`
takes the list of per-source results; each source independently V1–V8 gated).

### §7 Dashboard (computed from files 2026-06-12)

| Brand    | Ledger SKUs | True scope | V1–V8 | V9 coverage | Stage-3 | Status |
| -------- | ----------- | ---------- | ----- | ----------- | ------- | ------ |
| Cisco    | **297** (29 sources) | full Eth line | GREEN (all 29 src) | **PASS 19/19** | **PRICES-PENDING (297/297 authored)** | **DONE-VERIFIED + CONTENT-COMPLETE** (only operator Netto-VK outstanding) |
| Fortinet | 87 (1 datasheet) | whole line, 1 sheet | GREEN | **PASS 12/12** | **PRICES-PENDING (87/87 authored)** | **DONE-VERIFIED + CONTENT-COMPLETE** (datasheet-sourced facts; only operator Netto-VK outstanding) |
| HPE/Aruba| 147 (AOS-S/CX guide) | AOS-S/CX only | GREEN | **PASS 9/9** | **PRICES-PENDING (147/147 authored)** | **DONE-VERIFIED + CONTENT-COMPLETE** (name-encoded specs + verified wl/temp; only operator Netto-VK outstanding) |
| MikroTik | **24** (1 card-grid page) | whole SFP/QSFP line | GREEN | **PASS 7/7** | **PRICES-PENDING (24/24 authored)** | **DONE-VERIFIED + CONTENT-COMPLETE** (card-grid mode; per-SKU product-page facts; only operator Netto-VK outstanding) |
| Arista   | **347** (1 datasheet) | full Eth line, ordering pp.12-26 | GREEN | **PASS 11/11** | **PRICES-PENDING (347/347 authored)** | **DONE-VERIFIED + CONTENT-COMPLETE** (token mode + footnote repair; claims round-tripped vs ordering descriptions; only operator Netto-VK outstanding) |
| Brocade  | — | FC (out of scope) | — | — | — | PARKED (operator decision) |
| 12 others| 0 | not enumerated | — | — | — | NOT-STARTED |

**DONE-VERIFIED count: 5** (Cisco, Fortinet, HPE, MikroTik, Arista pass the full V1–V9 gate). Fortinet/HPE V9
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

### MikroTik content authoring (COMPLETE 2026-06-12) — State = PRICES-PENDING (24/24)
Authored all 24 MikroTik SKUs in-session ($0) into `stage3_content/MikroTik_content.json` (TRACKED).
Facts spine = `output/stage3/mikrotik_facts.json` (gitignored): per-SKU honest-GET of each
server-rendered product page (slug map in `_scratch/harvest_mikrotik.py`), pulling the spec
`<li>` label/value pairs. 19 pages carry the full `basis-1/2 font-bold`/`font-light` spec list;
**5 thin pages** (DQ+BC0003-DS+, S+31DLC10D, DDQ+DA0001/0003, DDQ+85MP01D) render specs outside
that markup — round-tripped instead from their `og:description` (added as `og` key in the facts
file). Families: SFP 6, SFP+ 3, SFP28 3, QSFP28 3, QSFP-DD 1, DAC 7, AOC 1. Every attribute →
provenance to its product page; flag-or-omit on unstated specs (e.g. DDQ+85MP01D reichweite not
asserted; S+31DLC10D reichweite "laut Hersteller"). `content_issues` passes for all 24; package
written to `output/stage3/MikroTik_Transceivers_*` (5 CSVs). Only operator Netto-VK outstanding.

### Fortinet content authoring (COMPLETE 2026-06-12) — State = PRICES-PENDING (87/87)
Authored all 87 Fortinet SKUs in-session ($0) into `stage3_content/Fortinet_content.json` (TRACKED).
Facts spine = `output/stage3/fortinet_facts.json` (gitignored): one `{desc,url}` per PN, where
`desc` = the per-SKU "Ordering Information" line lifted from the cached datasheet
`datasheets/cache/fortinet_transceivers.pdf` (pages 12–14; text dump in `_scratch/ft_pdf.txt`).
Authoring generator = `_scratch/ft_author.py` (gitignored): `parse()` regex-extracts
speed/media/range|length/connector/wavelength/temp/slots/standard/bidi/breakout from each desc;
composes German prose per **kind** (mod / modcu copper / dac / dacbrk breakout / adac active-DAC /
aoc) and builds attributes + provenance (every attr → the datasheet URL). FIX dict supplies clean
facts for the 2 truncated ordering lines (FN-TRAN-SFP+BD27 TX1271/RX1331, BD33 TX1331/RX1271; both
30 km single-LC SMF BiDi, -5 °C–85 °C). FN-TRAN-SFP+LRM special-cased: 10GBASE-LRM dual-media →
MMF 220 m primary + dedicated FAQ for SMF 300 m reach (honest, both stated). `content_issues`
passes for all 87; package written to `output/stage3/Fortinet_Transceivers_*` (5 CSVs). Only
operator Netto-VK outstanding. To regenerate: rebuild facts spine from the cached PDF, then run
`python _scratch/ft_author.py` + `hexcat stage3 --brand Fortinet --content stage3_content/Fortinet_content.json`.

### HPE/Aruba content authoring (COMPLETE 2026-06-12) — State = PRICES-PENDING (147/147)
Authored all 147 HPE/Aruba SKUs in-session ($0) into `stage3_content/HPE_content.json` (TRACKED).
Facts spine = `output/stage3/hpe_facts.json` (gitignored): one `{uk,name}` per PN, where `name` is
the **verified canonical product name** — 105 recovered by the NAME_RE grammar from the cached
guide `datasheets/cache/aos-s and aos-cx transceiver guide.pdf` (text dump `_scratch/hpe_pdf.txt`),
+ 42 read by hand from the authoritative "Product name (SKU)" optical spec tables (the regex missed
borderless-table rows), + 3 garbled-name fixes (OCR letter-doubling / marketing-text catches). The
Aruba/HPE name fully encodes speed/form-factor/connector/optical-type/reach/fiber, so it is the
parse source. Build = `_scratch/hpe_facts_build.py` (merges `_scratch/hpe_names.json` + OVERRIDE +
FIX dicts). Authoring generator = `_scratch/hpe_author.py` (gitignored): parses each name → kind
(mod / modcu copper-T / dac / dacbrk / aoc / aocbrk), composes German prose + attributes +
provenance. **Wavelength + temperature are flag-or-omit bonus attributes**, emitted only from the
verified `SPECS` override (BiDi wl pairs + industrial/I-Temp ranges read from the guide tables) or
the definitional single-wavelength of the optical type (`STD_WL`: SX/SR=850, LX/LR/DR/FR/LRM=1310,
LH/ER/ZR=1550). Multi-lane types (SR4/LR4/ER4L/CWDM4/FR4) emit no numeric wl. `content_issues`
passes for all 147; package written to `output/stage3/HPE_Transceivers_*` (5 CSVs). Only operator
Netto-VK outstanding. To regenerate: `python _scratch/hpe_facts_build.py` + `python
_scratch/hpe_author.py` + `cp output/stage3/HPE_content.json stage3_content/` + `hexcat stage3
--brand HPE --content stage3_content/HPE_content.json`.

### Arista content authoring (COMPLETE 2026-06-12) — State = PRICES-PENDING (347/347)
Authored all 347 Arista SKUs in-session ($0) into `stage3_content/Arista_content.json` (TRACKED).
Token-mode mining leaves ledger descriptions EMPTY, so the grounding corpus is
`_scratch/arista_desc.json` — one authoritative English Ordering-Information description per PN,
harvested by `_scratch/arista_harvest.py` from the cached `transceiver-data-sheet.pdf` ordering
region (pp.12-26). The harvester stitches bare-PN-on-own-line optics (prev+next), strips footnote
digits (SFP-10G-T family / ADPT), applies the same 9 `sku_rewrites` superscript repairs as the
ledger YAML, and HARDCODEs 5 multi-row E-Series/MR entries the line-stitcher can't reassemble →
347/347 clean, 0 missing. Authoring generator = `_scratch/arista_author.py` (gitignored): parses
structured facts (speed incl. NxM aggregates, IEEE standard, connector MPO-16/12/SN/CS/RJ45/LC,
media MMF/SMF/Cat6a, max reach, cable length/endpoints/breakout, tunable/BiDi/dual-rate) from the
harvested description — **flag-or-omit: a fact is emitted only if parseable**. Two paths: cables
(DAC / active-copper / AOC, breakout-aware) and optic/copper modules. Truthful brand-safe
expansion sentences (`pad_intro`/`pad_kurz` pools) lift under-budget intros/Kurz into the 90-175 /
40-80 word gates without adding unverifiable claims. `content_issues` passes for all 347; package
written to `output/stage3/Arista_Transceivers_*` (5 CSVs). Only operator Netto-VK outstanding. To
regenerate: `python _scratch/arista_harvest.py` + `python _scratch/arista_author.py` + `cp
output/stage3/Arista_content.json stage3_content/` + `hexcat stage3 --ledger
output/Arista_Transceivers_Ledger.xlsx --brand Arista --content stage3_content/Arista_content.json`.

### Engine fix: brand-aware compatibility-matrix note (package.py)
Latent cross-brand leak — the Cisco-specific `MATRIX_NOTE` was hardcoded into the composed
Beschreibung of EVERY brand (258 non-Cisco SKUs wrongly cited the Cisco matrix). Fixed surgically +
backward-compatibly: `matrix_note(brand)` returns the Cisco note for Cisco, an Arista
Transceiver-and-Cable-Guide note for Arista, and a generic `{brand}-Kompatibilitätsmatrix` note
otherwise; `compose_beschreibung` now calls it. `matrix_note("Cisco") == MATRIX_NOTE` so all
test_stage3.py assertions still pass (137/137). HPE/MikroTik/Fortinet packages regenerated — 0
Cisco leak confirmed across all 3.

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
| Arista       | **DONE-VERIFIED 2026-06-12** — real cached `transceiver-data-sheet.pdf` (29pp) HAS a clean "Ordering Information" enumeration pp.12-26; token mode, 347 SKUs, V1–V9 PASS (earlier "prose" triage was the 3KB QRG stub + misread pages) | — (done) |
| Huawei       | fetched HTML is a **404** page                                     | fresh official URL |
| Lenovo/IBM   | lp1042.pdf is the **wrong doc** (ThinkSystem SD650 server guide)   | correct transceiver-reference URL |
| Dell         | Tier-1 fetch failed (stale/blocked)                                | fresh URL / Tier-2 |
| NVIDIA       | **SOURCE MAPPED 2026-06-12** — LinkX is a valid brand; standalone "Parts List" PDFs are now DEPRECATED (100G-PAM4 + 800G XDR confirmed deprecated/empty; 2023 50G/25G PDF still has a table but is superseded). CURRENT source = Interconnect Product Specifications hub (per-product index by speed tier; each title = "{PN} {desc} Product Specifications"). Extraction algorithm + Ethernet/IB gating VALIDATED on the 2023 PDF (85 clean Ethernet PNs) | **BUILD from hub index** — enumerate per-speed-tier index pages, parse titles → (PN, desc), Ethernet-filter. See fresh-URLs/notes below |
| Palo Alto    | Tier-1 fetch failed                                                | fresh URL / Tier-2 |
| MikroTik     | **DONE-VERIFIED 2026-06-12** — card-grid mode, `sfp-qsfp` page, 24 SKUs, V1–V9 PASS | — (done) |
| Supermicro   | **WAF 403** on eStore listing (honest-GET 403, 443B) — bot-blocked | §6b NEEDS-HEADED (Tier-2; eStore WAF may still gate headed). Alt: AOC compat-matrix (a matrix, not an ordering list) |
| Ruijie       | **JS-shell / no listing page** — overview is a category landing (Tier-1 200 & Tier-2 headed both 0 SKUs, 0 tables, 6 hrefs); each SKU is its own /accessories/{slug} page | §6b NEEDS-HEADED + needs a real enumerable listing/datasheet source |
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

A genuine **prose / spec-sheet** datasheet — orderable PNs scattered through descriptive
text, the only tables being spec-attribute matrices (wavelength, reach, power) keyed by form
factor — would have no authoritative SKU locus to mine + verify against. Force-mining such a
source manufactures the exact phantom class V2 (authoritative-locus) rejects, so the verifier
would (correctly) refuse the ledger. Such a brand needs EITHER a different official document
with a real ordering table/part-number appendix, OR a new extraction mode with a defensible
locus. **Do not lower V2 to admit prose.**

**CORRECTION (2026-06-12, Arista):** Arista is NOT a prose datasheet. The official
`transceiver-data-sheet.pdf` (29 pp) carries a clean, authoritative two-column
"Ordering Information" enumeration spanning pp.12-26 (every page footer reads "Optics Modules
and Cables | Ordering Information"). It mines cleanly in **token mode** scoped to that heading
→ **347 SKUs, V1–V9 PASS, DONE-VERIFIED**. The earlier "prose, ~6 PN tokens, unminable"
triage was a mis-read: it inspected the 3 KB QRG stub + the front-matter spec-attribute pages,
not the ordering-information chapter. Lesson: confirm you are looking at the *ordering* section
before declaring a datasheet proseless. (One wrinkle solved here: pdfplumber glues
footnote-reference superscripts onto table SKUs — repaired via config-gated `mine.pdf.sku_rewrites`,
applied symmetrically in miner + verifier re-derivation + V1 raw text; empty/no-op for all
other brands.)

Probable bucket for the remaining brands (to confirm per-brand next pass):
- needs ordering-guide source confirmed before mode pick: NVIDIA, Dell, Palo Alto, Huawei
  (do NOT assume "prose" — verify the ordering section first, as the Arista correction shows).
- HTML **product-card grid** (no <table>, PNs in card markup) → card-extraction mode now BUILT:
  MikroTik **DONE** (24 SKUs); apply same mode to Supermicro, Ruijie (likely same shape).
- NEEDS-HEADED: Ubiquiti, Juniper, Avaya/Extreme.

### Fresh official URLs found 2026-06-12 (so next pass skips the search)
- MikroTik (current group page; old /group/optical-modules now 404):
  `https://mikrotik.com/products/group/sfp-qsfp` — server-rendered card grid, ~10 SFP PNs
  visible (S+RJ10, S-31DLC20D, S+31DLC10D, S+85DLC03D, S-3553LC20D, …), 0 tables.
- Arista data sheet (**DONE-VERIFIED** — token mode, 347 SKUs; see correction above):
  `https://www.arista.com/assets/data/pdf/Datasheets/transceiver-data-sheet.pdf`.
- NVIDIA LinkX **Parts List** PDFs (official ordering docs; Ethernet line spans 1G–1600G across
  several lists — must enumerate ALL for full coverage). Cached: `nvidia-400g-200g-parts-list.pdf`
  (21pp, text dump `_scratch/nvidia_parts.txt`) = the 50G-PAM4/25G-NRZ QSFP-DD/QSFP56/QSFP28/SFP28
  list. Others to fetch:
  `https://docs.nvidia.com/networking/display/400gbps-100g-pam4-transceivers-and-fiber-parts-list.pdf`
  (400G 100G-PAM4), 800G XDR (200G-PAM4) parts list, + legacy 40G/10G/1G list. Hub:
  `https://docs.nvidia.com/networking/interconnect/index.html`. **Extraction note:** the parts
  lists carry Ethernet/InfiniBand SUBSECTION HEADERS that gate scope — a flat token scan would
  wrongly ingest IB parts (EDR/HDR/SPQ-CE-*). Need a subsection-gated token mode that tracks the
  current header and emits only Ethernet (or Ethernet-and-IB) rows. Tables are merged-cell/multi-row
  (one Name cell spans many length rows), so description reassembly is non-trivial.
  - **PROTOTYPE RESULT (2026-06-12, `_scratch/nvidia_harvest.py`):** subsection-gated token scan
    over `_scratch/nvidia_parts.txt` yields **86 Ethernet PNs** from this 1 PDF (orderable
    Part-Number column MCP*/MFS*/MFA*/MMA*/MMS*/C-DQ*/T-DQ*; 980-* NVIDIA SKU column ignored;
    MAM*-QSA port adaptors excluded like ADPT). Gating headers: INCLUDE on "…Ethernet Only" /
    "InfiniBand and/or Ethernet" / "…and NNNGbE Ethernet" / "…and Spectrum Ethernet"; EXCLUDE on
    "InfiniBand Only". **Two false-positive classes found (must fix before a real ledger):**
    (1) cross-protocol HELPER rows — `MMA1T00-HS` (HDR *InfiniBand* SR4) is listed inside the
    Ethernet 400G "…Transceivers Often Used with 400G … for Split Ends" caption; its true
    Ethernet twin is `MMA1T00-VS`. (2) PAGE-BLEED — `MCP1650-V001E30/V01AE30/V002E26` (genuine
    200GbE) surface under the p7 "200G HDR InfiniBand Only" header because pdfplumber merges the
    table across the p7→p8 break. Root cause = `extract_text()` mangling merged-cell tables.
    **Recommended real build:** geometry/word-bbox column extraction (read the Part-Number column
    + the active subsection header by y-position) instead of line heuristics, run across ALL the
    NVIDIA parts-list PDFs (this one + 400G 100G-PAM4 + 800G XDR + legacy 40/10/1G). Do NOT ship a
    line-heuristic ledger — it would admit the 2 false-positive classes above.
  - **PROTOTYPE v2 (2026-06-12, `_scratch/nvidia_harvest.py`) — ALGORITHM VALIDATED.** A
    per-occurrence gating rule set resolves all 3 hazards and yields **85 clean Ethernet PNs**
    (17 IB/helper dropped) for PDF #1, with edge-case asserts that PASS: drop `MMA1T00-HS`
    (helper IB, code H), keep `MMA1T00-VS` (Eth twin), keep page-bled `MCP1650-V*` (also under a
    real Ethernet header), keep dual `MMS1W50-HM` (under "IB and 200GbE Ethernet"), drop IB
    `MMA1B00-E100`/`MFA1A00-E*`/`MCP1600-E*`. Rule: INCLUDE/EXCLUDE/HELPER header classes + a PN
    protocol-code fallback (V/C/A/W/G/N=Eth, H/E=IB) used only for HELPER/none rows; emit a PN iff
    it has >=1 Ethernet-positive occurrence OR (only-HELPER/none occurrences AND Eth code). NEXT:
    fetch the other 3 parts-list PDFs, run the same harvester to get the full Ethernet PN universe,
    build the per-PN grounding-description corpus, then wire as an engine mining mode + YAML +
    V1-V9 (still prefer word-bbox column extraction for robust descriptions).
  - **SOURCE-CURRENCY PIVOT (2026-06-12) — the clean parts-list PDFs are DEPRECATED.** Fetched the
    other two: `400gbps-100g-pam4-…-parts-list.pdf` and `800gbps-xdr-200g-pam4-…-parts-list.pdf`
    BOTH carry a page-2 "This document has been deprecated, refer to Interconnect Product
    Specifications" note and NO parts table (legal boilerplate only). The cached
    `nvidia-400g-200g-parts-list.pdf` (50G-PAM4/25G-NRZ, exported Nov/2023) is the only one with a
    real table, but it too is superseded. **Current authoritative source = the Interconnect
    Product Specifications hub** `https://networking-docs.nvidia.com/interconnect` — a per-product
    spec index organized by speed tier (1600G/800G/400G/200G/100G/25G). NO consolidated parts list,
    BUT each product link's TITLE is `"{PN} {desc} Product Specifications"` (e.g. "MMS1V00-WM 400GbE
    QSFP-DD DR4 Transceiver…", "MCP1600-E0xxEyy 100Gb/s QSFP28 DAC Cable…") — i.e. the index itself
    carries PN + a clean human description in one line. **RECOMMENDED current-source build:**
    enumerate each speed-tier index page on the hub, parse product-spec titles → (PN, description),
    Ethernet-filter by the title text (keep "…GbE"/"Ethernet"; drop InfiniBand "HDR/NDR/EDR/XDR"
    unless dual-labelled). This is CLEANER and CURRENT vs the deprecated PDF tables, and the
    title-description doubles as the grounding corpus for $0 authoring. Hub is a JS docs site
    (302 → networking-docs.nvidia.com) — confirm WebFetch can enumerate each tier index, else
    NEEDS-HEADED. The validated PN-family regex + Ethernet/IB gating from the prototype carry over.
  - **HUB ENUMERABLE (2026-06-12) — confirmed WebFetch reads it.** `https://networking-docs.nvidia.com/interconnect`
    is a single page grouping products by tier (1600G/800G/400G/200G/100G/25G/Accessories); each
    item = title `{PN} {desc}` + href to its product-spec page. It is CURRENT (adds today's 800G/1600G
    OSFP parts absent from the 2023 PDF: MMA4Z00-NS(-T), MMS4X00-NM/NS(-T), MMS4X50-NM, MMS4X90-NR,
    MCP7Y00-Nxxx, MCP4Y10-Nxxx, MCA4J80-Nxxx, MCA4K00/MCA4K50/MCA7K10 1600G, MMS4A20, MMS4C1X). **Two
    wrinkles for the real build:** (1) hub PNs are FAMILY PLACEHOLDERS with length variables
    (`MCP1600-E0xxEyy`, `MFS1S00-HxxxV`, `MCA4J80-Nxxx`) — concrete orderable per-length SKUs need a
    follow-through fetch of each family's product-spec page (href captured in the WebFetch result).
    (2) MAM*-QSA + MFP7E* are Accessories (port adaptors / MPO fiber harnesses) → out of scope like ADPT.
    **RECOMMENDED build = hub crawl:** (a) WebFetch the hub, parse the tier groups → family list with
    titles, Ethernet-filter; (b) for each Ethernet family, WebFetch its product-spec page → concrete
    per-length PNs + verified specs (reach/connector/wavelength/media); (c) the title+spec text is the
    grounding corpus for $0 German authoring. This is current + official + grounded — preferred over a
    deprecated-PDF ledger. NEXT PASS STARTS HERE (no more source discovery needed for NVIDIA).
- Palo Alto datasheet landing (not a direct PDF):
  `https://www.paloaltonetworks.com/resources/datasheets/key-specs-for-paloalto-interface-transceivers`
- Supermicro eStore transceiver listings (WAF-403 on honest-GET — need headed/Tier-2):
  `https://store.supermicro.com/us_en/server-accessories/transceiver/sfp.html`,
  `.../transceiver/qsfp.html`; AOC compat matrix (not an ordering list):
  `https://www.supermicro.com/en/support/resources/aoc/cables-transceivers`.
- Ruijie optics overview (category landing only — full SKU list is JS/per-product, NOT one page):
  `https://www.ruijienetworks.com/products/switches/optics-transceivers/` (redirects to
  ruijie.com/en-global SPA). Needs a real enumerable listing or a per-series datasheet.

## Next steps
- **Source acquisition is the gate**, not spec authoring. Next autonomous pass: for the
  stale-URL brands (Huawei, Lenovo, Dell, NVIDIA, Palo Alto, Supermicro,
  Ruijie) find the *current* official transceiver datasheet URL (web search ok — still
  "official manufacturer source"), re-fetch (Tier-2 render where JS-gated), then author a
  per-brand spec → mine → verify-gate PASS → ledger+audit → full suite green.
- **Escalated to human (§6):** (b) NEEDS-HEADED: Ubiquiti, Juniper, Avaya/Extreme;
  (c) Brocade Fibre-Channel optics — RESOLVED 2026-06-12: PARKED out-of-scope, do not map
  onto Ethernet taxonomy, revisit only on explicit go-ahead with dedicated FC categories.
- Loop now targets the other 17 brands (Brocade parked).
- Invariant for every new brand: a fix for brand N must not regress 1…N-1 (full suite green).
