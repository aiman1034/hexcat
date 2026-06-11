# HexCat — Hexwaren Catalog Automation (Phase 1)

HexCat generates **JTL-Ameise-ready CSV bundles** for the Hexwaren product catalog from
a structured per-SKU intake file. It is a pure, **offline, deterministic** file
transformer: no model calls, no network access. Given a filled intake CSV it emits a
byte-exact, fully-validated set of import files, and **never** writes a non-compliant
file — a failed validation check is a hard stop with an exact, located message.

> **Scope.** The deterministic core (pipeline stages 1, 7, 8) plus **Phase 2** content
> generation (German prose, SEO, FAQ via the Anthropic API — the `generate` command).
> Phase 3 (datasheet fetch + spec extraction + verification) is **not** built here; see
> *Extension points* below. The core build/validate path remains fully offline.

## Install

Requires Python 3.11+.

```bash
pip install -e .                 # core: build / validate / new-intake (offline)
pip install -e ".[generate]"     # + Phase 2 AI content generation (adds the anthropic SDK)
# or run without installing:
PYTHONPATH=src python -m hexcat.cli --help
```

Dependencies: `pydantic`, `typer`, `rich`, `pyyaml` (and `pytest` for the test suite).
The `generate` command additionally requires `anthropic` (the `[generate]` extra) and an
`ANTHROPIC_API_KEY` in the environment. The core build/validate path needs neither.

## Commands

### `hexcat generate` — draft content with the Anthropic API (Phase 2)
```bash
export ANTHROPIC_API_KEY=sk-...
hexcat generate --input my_batch_skeleton.csv --out my_batch_draft.csv \
                [--model claude-opus-4-8] [--max-retries 4] [--limit N] [--only SKU,SKU]
```
Reads a **facts-only skeleton** intake (the five content columns
`Kurzbeschreibung, Beschreibung, TitelTag, MetaDescription, FAQ` left blank; everything
else — Vendor, Artikelname, KategorieEbene3, the 14 attributes, NettoVK, Condition —
filled). For each SKU it drafts German prose/SEO/FAQ, then **self-checks the draft against
the exact same budget/banned rules the build gate enforces** (`content_checks`), re-prompting
with the unmet checks up to `--max-retries` times. It writes a **draft intake CSV** with the
content filled in. A SKU that still fails after the retries is written but **flagged** in the
report (and the build gate would quarantine it). This is the only command that makes network/
model calls. Workflow: `generate` → **human review/edit the draft** → `build`. See
`examples/Cisco_SampleBatch_skeleton.csv` for a runnable skeleton.

### `hexcat new-intake` — write a blank intake template
```bash
hexcat new-intake --out my_batch_intake.csv [--profile transceiver]
```
Writes the wide intake header plus one **commented example row** (its `Artikelnummer`
starts with `#`, so it is skipped on build). Fill real rows below it.

### `hexcat build` — assemble + validate a bundle
```bash
hexcat build --input my_batch_intake.csv --batch "Cisco_SampleBatch" \
             --category Transceivers --out ./out
```
Steps: validate intake → dedupe against the SQLite ledger → assemble the six files +
verification log into a staging area → run the full validation gate → on **PASS** promote
files to `--out` and record the ledger; on **FAIL** move the bundle to `--out/_quarantine`,
write nothing compliant to `--out`, and exit non-zero. Prints a concise supervisor report.

Useful options:
- `--rebuild` — re-emit SKUs already recorded in the ledger (default: dedupe/skip them).
- `--ledger <path>` — ledger DB location (default `hexcat_ledger.sqlite3`).
- `--strict/--no-strict` — posture flag (default strict). Phase 1 always fails closed and
  never emits a non-compliant file regardless; warn-list items never block.

### `hexcat validate` — re-check an existing bundle
```bash
hexcat validate --dir ./out
```
Re-runs the validation gate against an already-produced bundle (files on disk). Exit 0 on
pass, 1 on fail (with each located violation printed).

## Intake schema (wide — one row per SKU)

Columns (see `examples/Cisco_SampleBatch_intake.csv` for a filled, runnable example):

```
Artikelnummer, Vendor, KategorieEbene3, Artikelname, Kurzbeschreibung, Beschreibung,
TitelTag, MetaDescription, NettoVK, Artikelgewicht, Versandgewicht,
Formfaktor, Geschwindigkeit, TransceiverTyp, Faseranzahl, Fasertyp, Anschlusstyp,
Laenge, Kabeltyp, Wellenlaenge, Anwendung, Reichweite, DOMUnterstuetzung,
Betriebstemperatur, Standard, Condition, FAQ, SourceURLs
```

Notes:
- **NettoVK** — plain number (`120.50` or `120,50`); formatted to German locale (`120,50`)
  on output. Thousands separators are rejected (ambiguous).
- **Artikelgewicht / Versandgewicht** — optional. Provide **both** or **neither**; if
  blank they are derived from `config/weights.yaml` by `Formfaktor` (and flagged as
  placeholder in the report). `Versandgewicht > Artikelgewicht` is enforced.
- **The 14 attribute columns** (`Formfaktor` … `Standard`) are transposed wide→long into
  the Attributes file. **Empty cells are skipped** (no empty Wertliste rows); skipped
  attributes are listed in the report. Emitted attributes keep their canonical
  `Sortiernummer` (1-based position in the fixed 14).
- **Condition** — `new` / `used` / `refurbished`; blank defaults to `new`.
- **FAQ** — canonical `Question||Answer##Question||Answer` (Master-Guide v1.3), **or** a
  friendlier `Question :: Answer ;; Question :: Answer` which is normalized to canonical.
  3–10 pairs.
- **SourceURLs** — optional. If provided, used as the `Source_URL` for that SKU's
  attribute values in the Verification Log; if blank, values are marked `operator-provided`
  (Phase 1's "source" is the human; real datasheet verification arrives in Phase 3).

## Output contract (per batch: six files + one log)

| # | File | Encoding | Delim | Notes |
|---|------|----------|-------|-------|
| 1 | `Hexwaren_{Category}_v5_0_Main.csv` | UTF-8 **BOM** | `;` | 19 columns, exact order |
| 2 | `Hexwaren_{Category}_Attributes_v5_0.csv` | UTF-8 **BOM** | `,` | long format; Attributgruppe `Transceivers & SFP Modul` (**no** final "e") |
| 3 | `Hexwaren_{Category}_PlatformFlag.csv` | UTF-8 **BOM** | `;` | `Überverkauf Plattform Hexwaren = TRUE` |
| 4 | `Hexwaren_{Category}_Prices.csv` | UTF-8 (no BOM) | `;` | `Artikelnummer;Netto-VK`, German decimals |
| 5 | `Hexwaren_Condition_{Batch}.csv` | UTF-8 **BOM** | `,` | separate from Attributes; default `new` |
| 6 | `Hexwaren_FAQ_{Batch}_Batch_{N}.csv` | UTF-8 **BOM** | `,` | FAQ cell always double-quoted |
| 7 | `Verification_Log_{Batch}.csv` | UTF-8 BOM | `,` | one row per emitted attribute value |

Two category labels differ by exactly one character — both are intentional and preserved:
`Kategorie Ebene 2 = "Transceivers & SFP Module"` (with "e") vs. the Attributes
`Attributgruppe = "Transceivers & SFP Modul"` (no "e").

## The validation gate (18 checks)

Structural (headers/columns/order, delimiters, BOM, long format, FAQ quoting, cross-file
SKU-set identity), content (paragraph counts, word/char budgets, authenticity closer,
Titel-Tag suffix/length, locked `Kategorie Ebene 3` set, banned-language hard-fail list,
German-decimal prices, URL-Pfad/Hersteller/vendor consistency, condition values), and audit
(every attribute value has a Verification-Log row; weights numeric & `Versand > Artikel`).
Warn-list puffery (`Premium`, …) is flagged but does **not** fail the build.

Every failure reports `{file, SKU, field, expected, got}`.

## Config (single source of truth)

- `config/rules.yaml` — vendor→(Hersteller, slug) map, constants, the locked 22-item
  `Kategorie Ebene 3` set, word/char budgets, the authenticity closer, banned-language
  lists (hard-fail + warn), and the condition rule. Tweak values here, not in code.
- `config/weights.yaml` — per-form-factor `Artikelgewicht`/`Versandgewicht`. **All values
  are placeholders** (marked `# PLACEHOLDER — confirm`); confirm them before a live import.
  The report lists which emitted weights are still placeholders.

Structural column orders/headers (the byte-exact contract) live in
`src/hexcat/constants.py` — they are not operator-tweakable.

## Tests

```bash
pytest            # 71 tests: writers, intake, ledger, assembly, the gate, content checks, generation
```
The gate tests assemble the example bundle, then seed each contract violation (wrong column,
wide-vs-long attributes, dot-decimal price, missing BOM, `Sonstige`, `Module` vs `Modul`,
over-long Titel-Tag, banned phrase, missing closer, SKU missing from a file, missing
verification row) and assert a precise, located failure. The Phase 2 tests use an injected
**fake completer** (no network), cover the self-check/retry/flag paths, and assert end-to-end
that a generated draft flows through `read_intake → assemble → validate` and **passes the gate**.

## Phase 2 (built) — AI content generation

`hexcat generate` (module `generate.py`) is the only network/model path. It plugs into the
existing seams without rebuilding the deterministic core:
- It writes the five content columns into the wide intake rows **before** `read_intake`
  consumes them — exactly the `intake.py` seam — so generated content is gated identically.
- Its self-check and the build gate share **one** set of predicates (`content_checks.py`):
  there is no second copy of the budget/banned-phrase logic to drift.
- The model is injected via a `completer` callable, so generation is fully testable offline.
- Config-driven rules (`config/rules.yaml`) feed both the prompt and the gate, so new vendors,
  categories, or budget changes need no code edits. The model id is `--model`-overridable.

The **human-approval gate** is realized as the draft-file review step: `generate` never feeds
the deterministic build directly — the operator reviews/edits the draft, then runs `build`.

## Extension points (Phase 3 — not built here)

- **Verification Log** (`assemble._verification_rows`, `SourceURLs`) is the seam for
  **Phase 3**: replace the `operator-provided` source/confidence with real datasheet URLs
  and extraction confidence; the gate already requires a log row per attribute value.
- A spec-extraction + verification step (after datasheet fetch) slots upstream of `generate`,
  populating the facts skeleton from verified datasheet data instead of by hand.

The Phase 1 commands (`build`, `validate`, `new-intake`) make **no** network or model calls
and write only to `--out` and the ledger file.
