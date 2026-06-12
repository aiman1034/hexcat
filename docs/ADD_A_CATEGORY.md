# §4 — Category framework & the "add a category" runbook

HexCat's engine is **category-agnostic**. Everything that makes the current catalog *about
transceivers* lives in a small set of named **seams** (config files + a few code constants); the
whole pipeline around them — read → reconcile → build → assemble → validate → gate → price — is
generic. Adding a new product category (switches, NICs, optical line cards, …) means **supplying a
new profile of seams**, not rewriting the engine.

This document is the authoritative inventory of those seams and the step-by-step procedure. A guard
test (`tests/test_category_framework.py`) locks the inventory so it cannot silently drift.

---

## What is already generic (do NOT touch per category)

These are the byte-exact JTL-Ameise contract and the pipeline. They are identical for every
category and must stay unchanged:

| Concern | Where |
| --- | --- |
| The 7-file output contract (columns, delimiters, BOM, filenames) | `src/hexcat/constants.py` (MAIN/ATTRIBUTES/PLATFORMFLAG/PRICES/CONDITION/FAQ/VERIFICATION_LOG_*) |
| Reconcile → record → assemble → write | `stage3/`, `intake.build_record`, `assemble.assemble_bundle`, `writers.py` |
| Prose predicates (word/char budgets, `<p>` counts, closer, banned scan, sentence reuse) | `content_checks.py` |
| Build gate G1–G7 framework + cross-brand sweep + readiness + pricing | `validate.py`, `merged_sweep.py`, `import_readiness.py`, `pricing.py` |
| Verification-log provenance discipline (every attribute value backed by a row) | `assemble.py`, `validate._check_verification` |

The Condition/FAQ/Prices/PlatformFlag files carry **no** category-specific schema — they are reused
as-is.

---

## The category seams (what a new category must supply)

A category = the **attribute schema** + the **taxonomy** + the **applicability/derivation model** +
the **operator policy** (weights, prose budgets, banned words, closer, prompt). Each seam below is
marked **CONFIG** (add a sibling file / edit rules) or **CODE** (edit a constant / add a deriver).

1. **Taxonomy file — CONFIG.** Add `config/taxonomy/<category>.yaml` (sibling to
   `transceivers.yaml`): `category`, `kategorie_ebene_2`, `attributgruppe`, the
   `subcategories` (Kategorie Ebene 3 set), and the ordered `attributes`
   (`name` + `intake_field`). This is the operator-facing source of truth.

2. **Attribute schema — CODE.** `constants.py` mirrors the taxonomy's attribute tuple as
   `TRANSCEIVER_ATTRIBUTES` (the name encodes the category; generalise to a per-category tuple).
   Its order **is** the Sortiernummer contract. `config.verify_taxonomy()` fails loudly if the
   taxonomy file and this tuple drift — **edit both together.**

3. **Wide-intake columns — CODE.** `models.INTAKE_COLUMNS` must contain every `intake_field` the
   taxonomy references (plus the fixed identity/prose/price/weight columns). The build reads the
   wide intake by these names.

4. **Category vocabulary — CODE/CONFIG.** Transceivers lock two value vocabularies in
   `constants.py`: `PHYSICAL_FORMFAKTOR(_ORDERED)` (allowed `Formfaktor` values) and
   `CABLE_CATEGORIES` (sub-types whose prose floor relaxes / optics rules are waived). A new
   category supplies its own analogues (or empty sets if it has none). The Kategorie-Ebene-3 set
   itself lives in `rules.yaml: kategorie_ebene_3_allowed` and must equal the taxonomy
   `subcategories`.

5. **Applicability + derivation model — CODE.** `attribute_depth.py` is the transceiver physics
   model: `classify_media` + `EXPECTED_WHEN` decide PROVABLY_ABSENT vs GAP per empty cell, and the
   derivers (`derive_fasertyp`, `derive_faseranzahl`, …) fill ONLY physics-pinned slots, never
   guessing. A new category supplies its own applicability table + derivers (or a trivial
   "everything expected, nothing derivable" model). **Derivers must never invent a value** — same
   1000% rule.

6. **Completeness gate — CODE.** `validate._check_attributes` enforces a category-specific
   completeness rule (transceivers: a non-cable optical module MUST carry a `Wellenlänge`, with
   copper/Smart-SFP exemptions). A new category either reuses, replaces, or drops this rule.

7. **Weights — CONFIG.** `config/weights.yaml` (`defaults` + per-`form_factors` placeholder
   weights). Keys are the category's connectors/sub-types. Weights remain **flagged placeholders**
   (see `weight_disposition.yaml`) until grounded — never asserted.

8. **Prose policy — CONFIG.** `rules.yaml`: `budgets` (word/char/`<p>`/FAQ-pair ranges),
   `beschreibung_closer_prefix` (the authenticity closer), `banned_hard_fail` / `banned_warn`,
   `condition`. Tune per category; the predicates that read them are generic.

9. **Content prompt — CONFIG.** `config/prompts/<category>_content.txt` — the in-session authoring
   brief Claude uses (German prose written under Max, **$0**, never via a paid API).

---

## Procedure

1. **Write the taxonomy file** `config/taxonomy/<category>.yaml` (seam 1).
2. **Mirror the attribute tuple** into `constants.py` and **extend `INTAKE_COLUMNS`** (seams 2–3).
   Run `python -c "from hexcat.config import verify_taxonomy; verify_taxonomy('config/taxonomy/<category>.yaml')"` — it must pass.
3. **Set the Kategorie-Ebene-3 set** in `rules.yaml` to equal the taxonomy `subcategories`, and add
   the category vocabularies (seam 4).
4. **Add the applicability model + derivers** in `attribute_depth.py`, and adjust the completeness
   gate (seams 5–6). Keep derivers physics-grounded — flag, don't invent.
5. **Add weights, prose budgets, banned/closer, and the content prompt** (seams 7–9).
6. **Add tests** mirroring the transceiver suites for the new category: depth/derivers
   (`test_attribute_depth.py`), intake wiring (`test_intake.py`), the gate self-audit fixtures
   (`test_gate_self_audit.py` — one failing fixture per defect class), and extend the framework
   guard test for the new profile.
7. **Author + build + validate** a slice, then run the catalog-level gates:
   `hexcat validate --dir <bundle>`, `hexcat sweep <all bundles>`, `hexcat readiness <all bundles>`.
8. **Regenerate the flag artifacts** (`gen_source_disposition`, `gen_weight_disposition`,
   `gen_price_disposition`, residual-gaps, `gen_merged_collisions`) so the new category's deferred
   debt is auditable.

---

## Honest gaps (today)

The framework is **config-first but not yet 100% config-only**: seams 2, 3, 5, 6 are *code* edits
(`constants.py`, `models.py`, `attribute_depth.py`, `validate.py`) rather than pure config. That is
deliberate — the attribute tuple is the byte-exact Sortiernummer contract and the physics derivers
are real logic, both of which belong in tested code, not a YAML the operator could silently break.
A future refactor could lift seams 2–6 behind a `CategoryProfile` object selected by name; it is NOT
done now (no second category exists yet — building the abstraction before the second instance would
be speculative over-engineering). The guard test below ensures the *current* seams stay aligned so
that refactor, when a real second category arrives, starts from a consistent base.
