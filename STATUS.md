# HexCat — Stage-1 Ledger Status

_Cross-session continuity ledger. Updated at end of each working block. Pairs with ruflo
memory (`hexcat/*`). The autonomous audit→fix→re-verify loop reads this to resume._

## Current state (2026-06-12)

**Verifier-gated pipeline live.** Every mine is independently re-derived and audited (V1–V8)
before the ledger is accepted; a non-passing ledger is NOT written (CLI exits 1). Audit
reports (`Audit_Report_{Brand}.md` + `.json`) are written per source to the `--out` dir.

### Production ledgers — all GREEN (8/8 checks PASS)

| Brand    | Source (cache key)                         | Distinct SKUs | Notable taxonomy |
| -------- | ------------------------------------------ | ------------- | ---------------- |
| Cisco    | `c78-455693` (HTML)                         | 35            | DAC 9, AOC 6, SFP+ 20 |
| Fortinet | `fortinet_transceivers` (PDF, token+column) | 87            | DAC 28, MPO 4, AOC 1, 4× pack-of-four flagged |
| HPE/Aruba| `aos-s%20…transceiver%20guide` (PDF, section)| 147          | AOC 36, DAC 9 |

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

### Tests: **111 passing** (99 prior + 12 new regression tests covering every bug class +
V1–V8, frozen on synthetic tokens + a committed column-layout fixture
`tests/fixtures/sample_ordering_columns.pdf`).

### CLI
`python -m hexcat.cli ledger --seed <seed.xlsx> --source <id|all> --spec
config/ledger/<brand>_transceivers.yaml --out output/<Brand>_Ledger.xlsx --no-network`
(new `--spec` option selects the per-brand mining spec; default = Cisco pilot.)

## Next steps
- Extend the loop to the remaining 15 brands. Per `inputs/brand_sources.xlsx`:
  CLEAN (mineable now): MikroTik, Supermicro, Ruijie, Avaya/Extreme (Tier-2 render).
  NEEDS-PDF (have official PDF/URL, need a spec): Arista, Dell, Huawei, Lenovo/IBM,
  NVIDIA/Mellanox, Palo Alto, Ubiquiti, Brocade.
  BLOCKED-NEEDS-HEADED: Juniper (hCaptcha-gated SPA).
- Each new brand: author spec → fetch (cache) → mine → verify-gate must pass → write ledger +
  audit report → re-run FULL suite green (a fix for brand N must not regress 1…N-1).
