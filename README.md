# HexCat — Hexwaren Catalog Automation

HexCat generates **JTL-Ameise-ready CSV bundles** for the Hexwaren product catalog from
a structured per-SKU intake file. It is a pure, **offline, deterministic** file
transformer: no model calls, no network access. Given a filled intake CSV it emits a
byte-exact, fully-validated set of import files, and **never** writes a non-compliant
file — a failed validation check is a hard stop with an exact, located message.

> **Scope.** The deterministic core (pipeline stages 1, 7, 8) plus the **Phase 2 $0
> content flow** (German prose, SEO, FAQ authored by Claude Code in-session — the
> `worksheet` / `draft` commands). Phase 3 (datasheet fetch + spec extraction +
> verification) is **not** built here; see *Extension points* below.

> ## $0, no API key, no network
>
> **HexCat never makes a paid LLM API call.** There is no `anthropic` dependency and no
> `ANTHROPIC_API_KEY`. The German prose is written by **Claude Code in-session** (under
> your existing subscription), not by the tool. HexCat does the deterministic work:
> it turns a facts-only skeleton into a fill-in **worksheet**, merges your authored
> content back into a **draft** intake CSV, and **gates** that draft with the very same
> content rules the build enforces.

## Install

Requires Python 3.11+.

```bash
pip install -e .                 # everything: build / validate / worksheet / draft (offline)
# or run without installing:
PYTHONPATH=src python -m hexcat.cli --help
```

Dependencies: `pydantic`, `typer`, `rich`, `pyyaml` (and `pytest` for the test suite).
No API key, no network access — every command is fully offline and free to run.

## The $0 content flow

```
new-skeleton → fill facts → worksheet → (Claude Code fills the blocks in-session)
            → draft → validate --input → fix any violations → build
```

### `hexcat new-skeleton` — write a facts-only skeleton
```bash
hexcat new-skeleton --out my_batch_skeleton.csv [--profile transceiver]
```
Writes the wide intake header plus one **commented example row** with the five content
columns (`Kurzbeschreibung, Beschreibung, TitelTag, MetaDescription, FAQ`) left blank —
the input shape `worksheet` expects. Fill real fact rows below it (Vendor, Artikelname,
KategorieEbene3, the 14 attributes, NettoVK, Condition, SourceURLs).

### `hexcat worksheet` — turn a skeleton into a fill-in surface
```bash
hexcat worksheet --input my_batch_skeleton.csv --out my_batch_worksheet.md
```
Emits a Markdown worksheet: the rendered **voice guide** (positioning + banned language,
filled from `rules.yaml`), then one section per SKU showing its **verified facts**, the
**per-field rules** (budgets, the authenticity closer, FAQ format), and an empty
`BEGIN/END` block for each content field. Claude Code fills those blocks **in-session**
(no API, no cost). FAQ is authored one pair per line as `Frage? :: Antwort.`.
The facts stay authoritative in the skeleton — the worksheet only carries content.

### `hexcat draft` — merge authored content + facts into a draft intake CSV
```bash
hexcat draft --worksheet my_batch_worksheet.md --out my_batch_draft.csv \
             [--skeleton my_batch_skeleton.csv]
```
Reads the authored worksheet, re-reads the skeleton facts (path is embedded in the
worksheet header; override with `--skeleton`), and writes a **draft intake CSV** with the
five content columns filled. If any content block is empty it **errors without writing**,
naming each `{SKU}/{field}` — so a draft is only produced once every block is authored.
Next: `hexcat validate --input …`, then `hexcat build`.

### `hexcat new-intake` — write a blank intake template
```bash
hexcat new-intake --out my_batch_intake.csv [--profile transceiver]
```
Writes the wide intake header plus one **commented example row** (its `Artikelnummer`
starts with `#`, so it is skipped on build). Fill real rows below it.

### `hexcat build` — assemble + validate a bundle
```bash
hexcat build --input my_batch_intake.csv --batch "Cisco_Transceivers" \
             --category Transceivers --out ./out
```
Steps: validate intake → assemble the six files + verification log into a staging area →
run the full validation gate → on **PASS** promote files to `--out`; on **FAIL** move the
bundle to `--out/_quarantine`, write nothing compliant to `--out`, and exit non-zero.
Prints a concise supervisor report. (Phase 1 is files-only and stateless — there is **no
database**; dedup against the live catalog arrives with the Excel ledger in Phase 3.)

Useful options:
- `--strict/--no-strict` — posture flag (default strict). Phase 1 always fails closed and
  never emits a non-compliant file regardless; warn-list items never block.

### `hexcat validate` — gate a draft, or re-check a bundle
```bash
hexcat validate --input my_batch_draft.csv    # content gate on a draft before build
hexcat validate --dir ./out                   # re-validate an already-produced bundle
```
Pass **exactly one** of `--input` or `--dir`.

- `--input` runs the **content gate** on a draft/intake CSV using the **same predicates**
  `build` enforces (`content_checks`): word/char budgets, exact `<p>` counts, banned-language
  hard-fail, Titel-Tag ≤ 60 + ` | Hexwaren` suffix, Meta 140–200, the Beschreibung
  authenticity closer, FAQ format + 3–10 pairs, plus advisory soft-spec flags. Unlike the
  build's fail-fast intake read, it collects **every** violation, each located as
  `{SKU, field, expected, got}`. A draft that passes here passes the build gate's content
  checks. Any leftover `[FLAG] ` marker in a content cell is a violation.
- `--dir` re-runs the full structural+content+audit gate against files on disk.

Exit 0 on pass, 1 on fail (each located violation printed; warnings/soft flags listed too).

## Intake schema (wide — one row per SKU)

Columns (see `examples/Cisco_Transceivers_intake.csv` for a filled, runnable example):

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
| 1 | `Hexwaren_{Category}_Main.csv` | UTF-8 **BOM** | `;` | 19 columns, exact order |
| 2 | `Hexwaren_{Category}_Attributes.csv` | UTF-8 **BOM** | `,` | long format; Attributgruppe `Transceivers & SFP Modul` (**no** final "e") |
| 3 | `Hexwaren_{Category}_PlatformFlag.csv` | UTF-8 **BOM** | `;` | `Überverkauf Plattform Hexwaren = TRUE` |
| 4 | `Hexwaren_{Category}_Prices.csv` | UTF-8 (no BOM) | `;` | `Artikelnummer;Netto-VK`, German decimals |
| 5 | `Hexwaren_Condition_{Batch}.csv` | UTF-8 **BOM** | `,` | separate from Attributes; default `new` |
| 6 | `Hexwaren_FAQ_{Batch}.csv` | UTF-8 **BOM** | `,` | FAQ cell always double-quoted — **NON-AUTHORITATIVE PLACEHOLDER** (see import guardrail) |
| 7 | `Verification_Log_{Batch}.csv` | UTF-8 BOM | `,` | one row per emitted attribute value — **INTERNAL, never imported** |

> **⚠ Import guardrail — FAQ go-live (applies to EVERY brand).** The `Hexwaren_FAQ_{Batch}.csv`
> hexcat emits is a **non-authoritative placeholder**: it satisfies the JTL byte-contract
> (`Q||A##Q||A`, 3–10 pairs, BOM) so the bundle is self-consistent, but its content is basic
> (3 short pairs, near-identical for same-spec siblings). The **authoritative, FAQ-Master-Guide-v1.3**
> FAQ (3–10 data-driven, 50–90-word, harvest-backed, ≥80% sibling-differentiated) is produced
> **separately in the "Hexwaren FAQ Production" project** — that is a distinct content stream, not
> hexcat's. **At import: load the live FAQ field from the FAQ Production v1.3 output, NEVER from this
> placeholder. Import only the 5 Ameise product files (Main, Attributes, PlatformFlag, Prices,
> Condition); the FAQ comes from the v1.3 stream; skip `Verification_Log` (internal).**

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
- `config/prompts/transceiver_content.txt` — the **voice guide** shown at the top of the
  worksheet. Budget/banned `{{TOKEN}}`s are filled from `rules.yaml` at runtime, so the
  guide can't drift from the gate. `GUIDE_VERSION` (in `generate/prompt.py`) stamps the
  worksheet header.
- `config/taxonomy/transceivers.yaml` — the operator-facing canonical transceiver taxonomy:
  the 22 sub-categories and the 14 ordered attributes (the `Sortiernummer` contract). On
  build, `config.verify_taxonomy()` fails loudly if this file drifts from the structural
  contract in `rules.yaml` / `constants.py`. A new **category** = a sibling taxonomy file.
- `config/weights.yaml` — per-form-factor `Artikelgewicht`/`Versandgewicht`. **All values
  are placeholders** (marked `# PLACEHOLDER — confirm`); confirm them before a live import.
  The report lists which emitted weights are still placeholders.

Structural column orders/headers (the byte-exact contract) live in
`src/hexcat/constants.py` — they are not operator-tweakable.

## Tests

```bash
pytest            # 77 tests: writers, intake, taxonomy, assembly, the gate, content checks, the $0 flow
```
The gate tests assemble the example bundle, then seed each contract violation (wrong column,
wide-vs-long attributes, dot-decimal price, missing BOM, `Sonstige`, `Module` vs `Modul`,
over-long Titel-Tag, banned phrase, missing closer, SKU missing from a file, missing
verification row) and assert a precise, located failure. The Phase 2 tests cover the **$0
flow** (no network, no mocking): the worksheet round-trip (block-per-field, embedded
skeleton header, FAQ `::`→friendly-cell conversion), the **draft** merge + empty-block
error, the **content validator** including a **seeded-bad draft** (over-long Beschreibung,
banned phrase, over-long Titel-Tag, malformed FAQ) asserting each field is flagged and
located, the missing-closer and **[FLAG]**-marker checks, the **soft spec** flag, and an
**end-to-end** assertion that worksheet → author → draft → `validate_draft` → `read_intake`
→ assemble → `validate_dir` **passes the gate** (validate-pass ⇒ build-pass).

## Phase 2 (built) — the $0 content flow

Generation is performed by **Claude Code in-session**, not by the tool — there is **no
network/model path** in HexCat. The `generate/` package does the deterministic work:
- `generate/prompt.py` — renders the voice guide (`config/prompts/transceiver_content.txt`)
  with live rule values; owns `GUIDE_VERSION` (stamped into the worksheet header).
- `generate/worksheet.py` — `write_worksheet` (skeleton → fill-in Markdown) and
  `read_worksheet` (authored Markdown → `{SKU: {field: text}}`), via deterministic
  `<!-- HEXCAT:BEGIN/END … -->` block markers.
- `generate/engine.py` — facts-only skeleton intake (`read_skeleton`), the `merge_fields`
  fold into a wide intake row, the advisory soft spec check, and the draft + skeleton writers.

The design guarantees:
- It writes the five content columns into the wide intake rows **before** `read_intake`
  consumes them — exactly the `intake.py` seam — so authored content is gated identically.
- The draft content gate (`validate.validate_draft`) and the build gate share **one** set of
  predicates (`content_checks.py`): there is no second copy of the budget/banned-phrase logic
  to drift. A draft that passes `validate --input` passes the build gate's content checks.
- Facts stay authoritative in the skeleton CSV (referenced by path in the worksheet header),
  so they never round-trip through fragile Markdown parsing — `draft` re-reads them via
  `read_skeleton` and only parses the content blocks from the worksheet.

The **human-approval gate** is the draft-file review step: `draft` never feeds the
deterministic build directly — the operator reviews/edits the draft, runs `validate --input`,
then `build`.

## Extension points (Phases 3-4 — not built here)

- **Verification Log** (`assemble._verification_rows`, `SourceURLs`) is the seam for
  **Phase 3**: replace the `operator-provided` source/confidence with real datasheet URLs
  and extraction confidence; the gate already requires a log row per attribute value.
- A spec-extraction + verification step (after datasheet fetch) slots upstream of the
  worksheet flow, populating the facts skeleton from verified datasheet data instead of by hand.
- **`src/hexcat/ledger/`** (empty package, docstring) — Phase 3 builds the **Excel** 5-sheet
  ledger (Fortschritt / Neue Artikel / Quellen-Tracker / PN-Korrekturen / Familien-Audit)
  with `openpyxl`. Files-only, **no database**. Dedup against the live catalog lives here.
- **`src/hexcat/adapters/base.py`** (`BrandAdapter`) — Phase 4 per-vendor Stage 1 logic
  (`discover_datasheets` / `mine_part_numbers` / `hygiene_rules` / `taxonomy_map`).
  Onboarding brand #2-18 is meant to be config (adapter + taxonomy map), not engine changes.

The Phase 1 commands (`build`, `validate`, `new-intake`) make **no** network or model calls,
use **no** database, and write only to `--out`.
