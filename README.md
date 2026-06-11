# HexCat — Hexwaren Catalog Automation (Phase 1)

HexCat generates **JTL-Ameise-ready CSV bundles** for the Hexwaren product catalog from
a structured per-SKU intake file. It is a pure, **offline, deterministic** file
transformer: no model calls, no network access. Given a filled intake CSV it emits a
byte-exact, fully-validated set of import files, and **never** writes a non-compliant
file — a failed validation check is a hard stop with an exact, located message.

> **Phase 1 scope.** This is the deterministic core only (pipeline stages 1, 7, 8 of the
> full design). Generative stages — datasheet spec extraction, German prose, SEO, FAQ
> authoring via the Anthropic API — are **not** built here. See *Extension points* below.

## Install

Requires Python 3.11+.

```bash
pip install -e .          # from the hexcat/ directory
# or run without installing:
PYTHONPATH=src python -m hexcat.cli --help
```

Dependencies: `pydantic`, `typer`, `rich`, `pyyaml` (and `pytest` for the test suite).

## Commands

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
pytest            # 50 tests: writers, intake, ledger, assembly, and the full gate
```
The gate tests assemble the example bundle, then seed each contract violation (wrong column,
wide-vs-long attributes, dot-decimal price, missing BOM, `Sonstige`, `Module` vs `Modul`,
over-long Titel-Tag, banned phrase, missing closer, SKU missing from a file, missing
verification row) and assert a precise, located failure.

## Extension points (Phase 2 / 3 — not built here)

The deterministic core is the foundation the generative phases plug into:
- **`intake.py`** is where a generative module would *write* the wide intake rows
  (Kurzbeschreibung/Beschreibung/Titel/Meta/FAQ) before `read_intake` consumes them.
  Phase 1 already validates that structure, so generated content is gated the same way.
- **Verification Log** (`assemble._verification_rows`, `SourceURLs`) is the seam for
  **Phase 3**: replace the `operator-provided` source/confidence with real datasheet URLs
  and extraction confidence; the gate already requires a log row per attribute value.
- A **human-approval gate** (settled decision: after spec verification / stage 4, before
  prose is written) slots between a future spec-extraction step and `intake.build_record`.
- Config-driven rules mean new vendors, categories, or budget changes need no code edits.

Phase 1 makes **no** network or model calls and writes only to `--out` and the ledger file.
