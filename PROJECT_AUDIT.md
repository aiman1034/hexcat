# HexCat — Project Audit & Rolling Context

> **STANDING RULE (non-negotiable, every session until the operator says otherwise):**
> 1. **READ this file first** at the start of any work and **before every update** to anything in the project — it is the single source of truth so context is never lost.
> 2. **UPDATE this file as work proceeds and after every change** (data, code, config, brand completion, decisions).
> 3. **Always tell the operator** when you have **read** this file and when you have **edited** it.
>
> Last updated: 2026-06-13 · Maintained by Claude (Opus) under the Max subscription, $0.

---

## 1. Mission & hard rules

**What HexCat is:** an autonomous, **$0**, deterministic-Python, files-only engine that produces a network-transceiver catalog for **Hexwaren** (German B2B network-hardware reseller) as byte-exact **JTL-Ameise v5.0** CSV import bundles. German prose is written by Claude in-session under Max — never a paid LLM API call, never by the tool.

**Hard rules (never violate):**
- **ZERO-DOLLAR** — no paid API call, ever. Grounding via the local fetch bridge ($0) + Claude-in-session prose.
- **1000% grounding** — every value traces verbatim to an official manufacturer datasheet; NEVER fabricated/assumed. Derivations are explicitly tagged. **Flag, don't emit** on uncertainty.
- **Deterministic core; files-only; surgical edits** (never rebuild); **commit per batch/family**; recall/store **ruflo** (memory only).
- Commits end with `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`.
- Windows; run Python with `PYTHONIOENCODING=utf-8`; git-bash paths `/d/Project/hexcat`.

**The 9 standing rules** (full text in `STATUS.md`):
1–6. **Completeness** — union of ALL independent official enumerations (never one source, never harvest-vs-itself); EOL/EOS bulletins mandatory; mine each source to backend; verdict **computed** ("captured X of Y"), never asserted; every real PN included; legacy flagged never dropped; only genuine non-transceivers excluded with a verbatim reason.
7. **Taxonomy-approval gate** — never add/remove a Kat-Ebene-3 token autonomously; STOP and surface for operator yes/no.
8. **Gold-standard parity** — the gate bar must EQUAL the gold-slice schema; "gate-PASS" is necessary but never sufficient → run a Rule-8 parity re-verification (before→after tally) before declaring a brand complete; specs verbatim-verified (read→adversarial-verify); derived values tagged; verify per-SKU where a value varies by suffix.
9. **Class-derived Betriebstemperatur when unpublished** — if a manufacturer doesn't publish operating temp, derive from the optic's temperature CLASS (commercial → 0–70 °C; industrial-suffix -I/-RGD → ≈ -40..+85 °C), corroborated by publishing siblings, tagged `industry-standard-<class>`. Applies **ONLY** to Betriebstemperatur; every other part-specific spec (wavelength, reach, channel, datarate, connector) stays datasheet-verbatim and is **never derived**.

---

## 2. The gold-slice schema (the quality bar)

**Applicable attribute set** (locked 14 canonical attributes, `src/hexcat/constants.py` `TRANSCEIVER_ATTRIBUTES`; free vocab mapped via `ATTR_ALIAS` in `reconcile.py`):
Formfaktor · Geschwindigkeit · Transceiver Typ · Faseranzahl · Fasertyp · Anschlusstyp · Länge · Kabeltyp · Wellenlänge · Anwendung · Reichweite · DOM Unterstützung · Betriebstemperatur · Standard.
- **Anwendung** required on EVERY SKU (varied by reach/type, derived+tagged).
- **Geschwindigkeit** required on EVERY SKU.
- **Betriebstemperatur** required on every optical/active module **and DAC** (only `MPO Kabel` exempt).
- **Wellenlänge** required on optical modules (copper/Smart-SFP/cable exempt via `_WAVELENGTH_EXEMPT_RE`).
- **Faseranzahl** auto-derived lane-aware (see §4).

**Content floors:** Kurzbeschreibung 40–80 words (2× `<p>`); Beschreibung 90–175 words ending the authenticity closer `Originaler <Brand>-…`; Titel-Tag ≤60 chars ending ` | Hexwaren`; Meta-Description 140–200 chars; FAQ 3–10 pairs.

**Taxonomy:** locked **24** Kat-Ebene-3 tokens (`config/taxonomy/transceivers.yaml` ⇄ `config/rules.yaml`): DAC/AOC/MPO Kabel, QSFP+/QSFP-DD/QSFP-DD800/QSFP28/QSFP56/QSFP112, OSFP, SFP/SFP+/SFP28/SFP56, X2, XENPAK, XFP, CFP/CFP2/CPAK/CXP, GBIC, POM, CIM8. "Sonstige" never allowed.

**Byte contract (v5.0, 7 files):** Main (19-col `;` BOM CRLF), Attributes (8-col `,` BOM), PlatformFlag (`;`), Prices (`;` NO BOM, German decimal), Condition (7-col `,`), FAQ (`,`), Verification_Log (6-col `,`). Enforced by `validate_dir`; non-compliant → `_quarantine` (holds **only the rejected rows**, not a full copy).

---

## 3. Pipeline & architecture

```
harvest (official sources) → completeness union (captured X of Y) → author per family (in-session German, grounded)
   → reconcile (entry_to_intake → build_record; ATTR_ALIAS; derivers) → assemble_bundle (writers, byte contract)
   → validate_dir (the GATE: format + gold-slice completeness + 5 semantic cross-checks) → PASS→emit / FAIL→_quarantine
   → price (best-effort, comp + family-base + list; flag rest 0,00) → commit per batch → ruflo store
```

**Key modules (`src/hexcat/`, 7096 LoC):** `validate.py` (877, the gate), `cli.py` (672, `stage3` command), `stage3/reconcile.py` (294, intake mapping + `physical_formfaktor` + `ATTR_ALIAS`), `intake.py` (273, `build_record`/`_build_attributes`), `attribute_depth.py` (217, the lane-aware derivers), `assemble.py` (178, bundle writers + Verification_Log), `content_checks.py` (177, `word_count`/`plain_text`), `constants.py` (163, columns/tokens), `ledger/*` (harvest/mine/spec), `verify/*` (adversarial verify), `pricing.py`/`price_inputs.py`.
**`lib/` (2104 LoC):** `completeness.py` (reconcile_brand verdict), `local_fetch.py` (the $0 fetch bridge: cache→httpx→browser, CAPTCHA opt-in), `market_comp.py`/`price_model.py`/`price_run.py` (pricing engine), `harvest.py`, `deferred_queue.py`.

**CLI:** `python -m hexcat.cli stage3 --content stage3_content/<Brand>_content.json --brand <Brand> --out output/stage3_<Brand>`.

---

## 4. Permanent semantic cross-checks (in `validate.py`, all FAIL-level)

Added after the operator's semantic-error audit (catch structurally-valid-but-WRONG values the byte gate AND adversarial-verify both passed):
- **B.1 Formfaktor ↔ Anschlusstyp** — an SFP-family Formfaktor cannot carry a QSFP/MPO/CXP connector.
- **B.2 Faseranzahl present** — every optical fibre-connector module must carry a fibre count (the lane-aware deriver fills it: single/BiDi→1, duplex→2, MPO parallel→2×lanes [SR4→8, SR8/VR8→16, SR10→20, 12×25G→24], ×N for N×100GBASE breakout).
- **B.3 multi-wavelength full set** — LR4/ER4/FR4/coherent carry the full wavelength SET (LAN-WDM 1271/1291/1311/1331; 100G 1295.56/1300.05/1304.58/1309.14; coherent C-band), never one centre value.
- **B.4 no "—" placeholders** — N/A attributes are OMITTED (emit-skip in `_build_attributes`), never emitted as "—".
- **B.5 Hersteller product-line guard** — a known PN family is assigned to its real Hersteller (MGB/MFE → Cisco), used as a guard, never as the assignment rule.
- **B.6 tunable wavelength ⇒ coherent/tunable part** — a "durchstimmbar"/tunable wavelength is only valid on a genuinely coherent/tunable part (kohär/coheren/DCO/ACO/400ZR/800ZR/DWDM/tunable). The INVERSE of B.3: catches a grey fixed optic (e.g. 10GBASE-ZR) wrongly given a C-band-tunable wavelength — which a single-value multi-λ check would NOT flag. (Added after this exact blind spot was found proving the back-fill on Cisco — see §9.)
- **B.7 cable ⇒ cable Kat-3 token** — a DAC/AOC cable (identified by its Kabeltyp) must be classified under a CABLE Kat-Ebene-3 token (DAC/AOC Kabel), never a transceiver-module form factor (QSFP28/SFP+/…). Modules carry no Kabeltyp → low FP risk. (Added after HPE was found with 21 DACs + 3 AOCs under a module k3 — see §9.) **Note on B.3:** the multi-wl regex uses `\b` guards so a parallel single-mode type (PLR4/PLR8 — one 1310 nm wavelength over parallel fibres) does NOT match its WDM cousin (LR4/LR8); validate.py was also aligned to audit_semantic.py (it had been missing LR8). **Note on B.6:** the coherent-type regex matches speed-gated `\d{3}G(?:BASE)?[- ]?ZR` so genuine coherent **100/400/800GBASE-ZR(P)** (legitimately C-band-tunable) pass, while grey direct-detect **10/40GBASE-ZR** (2-digit G) stay excluded — preserving the grey-ZR fix. (Refined when Arista's 400GBASE-ZR modules were false-flagged.)

Audit tool: **`_scratch/audit_semantic.py [Brand ...]`** — per-brand (defaults Cisco+Meraki); enumerates every instance of all **7** classes (ff_conn / faser / multi_wl / tunable_wl / dash / hersteller / cable_k3).

---

## 5. Brand status

> **Verified-state-only:** this table records MEASURED facts (actual gate output, `audit_semantic.py`
> per-check counts, Rule-8 parity tallies) — never "done" assertions. If it isn't measured, it isn't
> stated as fact. Re-run to confirm: `python -m hexcat.cli stage3 …` (gate), `python _scratch/audit_semantic.py`
> (cross-checks), the §6 pricing run, and `python -m pytest -q`.

| Brand | Content SKUs | Measured gate | audit_semantic (7: ff/faser/multiwl/tunwl/dash/herst/**cablek3**) | Pricing | Notes |
|---|---|---|---|---|---|
| **Cisco** | 596 | **PASS 596/596, 0 violations** (2026-06-13, commit `63bbcc2`) | **0 / 0 / 0 / 0 / 0 / 0** | 111/596 priced (T1 7, FAMILY 98, T2-LIST 6; rest 0,00 debt) | Rule-8 parity: Anwendung/Geschwindigkeit/Betriebstemperatur(non-MPO) **0-missing**. Flagged (held, need a Cisco source): QDD-800G-VR8, SFP10G-USR, MGBBX1, ONS-QSFP-4X10-MER/MLR. 4 MGB* are Cisco SB. **Count traceable:** 594 pre-correction + 4 MGB − 2 exclusions (ONS-QDD-OLS EDFA, E1000-2-G line card) = 596 ✓. ZIP `output/Hexwaren_Cisco_stage3_63bbcc2.zip`. |
| **Meraki** | 25 (MA-* only) | **PASS 25/25, 0 violations** (2026-06-13, commit `63bbcc2`) | **0 / 0 / 0 / 0 / 0 / 0** | 0/25 (PENDING, no comp yet) | Rule-8 parity: required attrs **0-missing**. MGB* reassigned to Cisco SB. 2 MA-CBL-SPWR excluded (power cables). Rule-9 temp. ZIP `output/Hexwaren_Meraki_stage3_63bbcc2.zip`. |
| **Arista** | 347 | **PASS 347/347, 0 violations** (2026-06-14, commit `3fd1f61`) | **0×7** | deferred (no prices in datasheet; 0,00) | ✅ DONE. Completeness 347/347 (Arista Transceivers Data Sheet); token diff confirms no gap (13 extra = footnote/truncation/bare-form-factor artifacts). Fixed 42 reconcile connectors (Anschlussenden bare "QSFP"→QSFP56/QSFP28 by standard). 243 DAC/AOC Rule-9 commercial 0/70. 18×800G speeds grounded; 3 coherent 400GBASE-ZR drove B.6 ZR-speed-gate refinement. Rule-8 parity 0-missing (SFP-1G-T copper exempt). ZIP `output/Hexwaren_Arista_stage3_3fd1f61.zip`. |
| **HPE/Aruba** | 147 | **PASS 147/147, 0 violations** (2026-06-13, commit `a34a86b`) | **0×7** (all incl B.7 cable_k3) | deferred (no grounded list; netto_vk 0,00) | ✅ DONE. Completeness: 147 of 147 standalone catalog transceivers (AOS-S/AOS-CX guide); independent full-guide token diff confirms the ~370 other PN-tokens are switches/EOL-revisions/aliases (R9F75A=JL309A)/cross-refs, no gap. Betriebstemperatur: 72 verbatim from the guide's per-module Rating + 61 Rule-9 commercial. **Fixed 21 DAC + 3 AOC mis-classified under module k3 → DAC/AOC Kabel (drove new B.7).** 5 speeds grounded. Rule-8 parity 0-missing. ZIP `output/Hexwaren_HPE_stage3_a34a86b.zip`. |
| **Fortinet** | 87 | **PASS 87/87, 0 violations** (2026-06-14, commit `fb11cb4`) | **0×7** | deferred (datasheet has no prices; 0,00) | ✅ DONE. Completeness 87/87 (Fortinet Transceivers Data Sheet); token diff confirms no gap (11 extra tokens = shorthand/4-pack/"+"-truncations of captured SKUs). Fixed 5 reconcile-blocking connectors (3 QSFP-DD cables + 2 MPO breakouts). Betriebstemperatur 85 datasheet-verbatim (Fortinet publishes). FG-TRAN-CFP2-LR4 wavelength set; QSFP28 SR→SR4. Rule-8 parity 0-missing. ZIP `output/Hexwaren_Fortinet_stage3_fb11cb4.zip`. |
| **MikroTik** | 24 | **PASS 24/24, 0 violations** (2026-06-13, commit `f538381`) | **0 / 0 / 0 / 0 / 0 / 0** | 24/24 MSRP captured (grounded); EUR net DEFERRED to supplier feed | ✅ DONE. Completeness: captured 24 of 25 (official sfp-qsfp grid); XQ+CM0000-XS+ excluded (QSFP28→SFP28 port adapter). Betriebstemperatur: 8 published verbatim + 16 Rule-9 sibling-corroborated industrial (NOT commercial — MikroTik publishes -40 lows). DDQ+85MP01D=400G QSFP-DD SR8 (Faseranzahl 16, MPO-16). Rule-8 parity 0-missing. ZIP `output/Hexwaren_MikroTik_stage3_f538381.zip`. 14 non-blocking warnings (length-variant DAC prose reuse). |

**Fresh brands not started:** Avaya/Extreme, Dell, Huawei, Juniper, Lenovo/IBM, NVIDIA/Mellanox, Palo Alto, Ruijie, Supermicro, Ubiquiti, ZTE. (Brocade parked; Polycom = no transceivers.)
**Switch category:** not started — needs its OWN gold-slice schema + taxonomy (Rule-7 approval before authoring); everything else (completeness, gate, Rule 8/9, byte contract, cross-checks, per-brand process) carries over.

**Test suite (measured):** 413 tests (28 files), all green — last run 2026-06-13 (commit `a34a86b`, incl B.7). Run: `PYTHONIOENCODING=utf-8 python -m pytest -q`. **All 4 done brands (Cisco/Meraki/MikroTik/HPE) re-verified `audit_semantic = 0` across all 7 checks (incl B.7) on 2026-06-13.**

**Tooling-validation gate (before scaling the back-fill across 4+11 brands):** Cisco + Meraki ZIPs (`output/Hexwaren_{Cisco,Meraki}_stage3_63bbcc2.zip`) + `audit_semantic.py` dump (`_out/audit_semantic_dump.txt`) for INDEPENDENT audit. Status (commit `63bbcc2`): audit_semantic.py = **0/0/0/0/0/0** on both; QSFP/SFP-substring trap verified handled; generalized `backfill_brand.py` proven **idempotent (dry-run 0/0/0)** on both. **One real blind spot was found+fixed during this validation** (grey-ZR wavelength corruption, see §9) and a **6th cross-check (B.6)** added to close it. **Still awaiting the operator's INDEPENDENT audit of the ZIPs; if it surfaces anything audit_semantic.py missed, fix the tool before scaling.** 4-brand commits HELD until confirmed.

---

## 6. Pricing state

Engine = `lib/price_run.resolve` (T1-MARKET comp > FAMILY-pool > T2-LIST/GPL > MODEL[back-test-gated] > FLAG 0,00). Orchestrator `_scratch/price_cisco.py`. Confirmed comp approach: broadened genuine-new-sealed market (exclude refurb/compatible *listings*, not sellers), authorized-preferred + secondary-fallback (tagged secondary-anchored), family-base for DWDM/CWDM channels, legacy flagged low-confidence, feature-model backstop only if leave-one-out MAPE ≤ 20% (currently DISABLED — 156% on heterogeneous anchors). **Pricing is best-effort, NOT a completion blocker** — the completion bar is gold-parity + coverage-complete DATA. Full pricing finished later via a supplier price-list ingest (operator will provide a feed). Comp data: `config/market_prices/market_observations.yaml` (sparse, 8 SKUs) + `list_prices.yaml`.

---

## 7. Key file map

- **Content (authored truth):** `stage3_content/<Brand>_content.json` (keyed by PN; per entry: `_facts`{unterkategorie,quell_url,verifiziert_am}, artikelname, titel_tag, meta_description, kurzbeschreibung, intro[3], faq, attributes[[name,value]], provenance{attr:[src,confidence]}, netto_vk).
- **Completeness/coverage:** `config/coverage/<brand>_transceivers_*.yaml` (completeness, disposition, union_triage), `config/coverage/enumerations/*.txt` (TMG matrix, EOL bulletins, ordering guide).
- **Grounded specs:** `config/attribute_gaps/betriebstemperatur_grounded.yaml` (per-family op-temp, source:line, confirmed).
- **Rules/taxonomy/pricing:** `config/rules.yaml`, `config/taxonomy/transceivers.yaml`, `config/pricing_policy.yaml`, `config/market_prices/*`.
- **Datasheet cache (gitignored):** `datasheets/cache/*.html|*.pdf` (fetched via the bridge).
- **Author/util scripts (gitignored `_scratch/`):** ~90 `author_*.py` + `backfill_499.py` + `audit_semantic.py` + `price_cisco.py`.
- **Emitted bundles (gitignored `output/`, `_out/`):** `output/stage3_<Brand>/Hexwaren_*.csv`.
- **STATUS.md** = the full rules charter; **CLAUDE.md** = session bootstrap (ruflo + this rule).

---

## 8. Pending work (roadmap — directive D)

1. **Re-verify the 4 early brands** — re-harvest for completeness → gold-parity back-fill (Anwendung, Betriebstemperatur per Rule 9, Faseranzahl auto, descriptions ≥90, fix Formfaktor/connector, multi-wavelength sets, drop "—") → strict gate PASS → Rule-8 parity → `audit_semantic.py` (all 5 = 0) → price best-effort → commit per family. **Diagnosed scope (2026-06-13):**
   - **MikroTik (24)** — no reconcile errors; gate FAIL 61: Beschreibung 23 (<90), Anwendung 21, Betriebstemperatur 16, Faseranzahl 1. Smallest/most tractable → do FIRST.
   - **HPE/Aruba (147)** — no reconcile errors; gate FAIL 398: Beschreibung 138, Betriebstemperatur 134, Anwendung 121, Geschwindigkeit 5. Pure attribute-depth regression.
   - **Fortinet (87)** — 5 reconcile failures (DAC/breakout `FG-TRAN-QSFP-4XSFP/4SFP`, `FN-CABLE-QSFPDD-DAC`: Formfaktor unresolved) + 82 OK then back-fill.
   - **Arista (347)** — 42 reconcile failures (`C-Q200-Q200-*` 200G DAC + similar: Formfaktor unresolved) + 305 OK then back-fill. Largest.
   - **PREREQUISITE — generalize `backfill_499.py`** to a `--content <path> --brand <B>` tool: Anwendung derive+tag (brand-agnostic `anwendung()`), **Betriebstemperatur via Rule 9 class-derivation** (commercial 0–70 °C / industrial-suffix -40..85 °C, tagged `industry-standard-<class>`) — NOT the Cisco grounded yaml — and the generic desc-extension. The reconcile-failure PNs (DAC/breakout) need their connector grounded so `physical_formfaktor` resolves (author the real `Anschluss`, e.g. QSFP56↔QSFP56 / QSFP↔4×SFP).
2. **Fresh brands** (11): Avaya/Extreme, Dell, Huawei, Juniper, Lenovo/IBM, NVIDIA/Mellanox, Palo Alto, Ruijie, Supermicro, Ubiquiti, ZTE — full per-brand process each.
3. **Switches:** propose switch gold-slice schema + taxonomy for Rule-7 approval, then author with the same machinery.

---

## 9. Session changelog (rolling — append every session)

- **2026-06-13** — Cisco taken to 596 transceivers (gate PASS, priced 111). Meraki authored (25 MA-*, PASS). Rules 8 & 9 locked. Parts 4–6 (pricing, Verification_Log real per-attr confidence, _quarantine rejected-rows-only) done. **Semantic-error correction A/B/C** (commit `2caf78a`): MGB→Cisco SB, Formfaktor↔connector, lane-aware Faseranzahl (137→0), multi-wavelength sets (25), "—" omitted (79→0), ONS-QSFP-4X10-MER/MLR flagged; 5 permanent gate cross-checks added; both brands re-gated PASS, 413 tests. **This PROJECT_AUDIT.md created** (commit `887932e`) + standing read-before-update rule wired into CLAUDE.md + ruflo/auto-memory. **Directive-D diagnosis run** on the 4 early brands (see §8 for per-brand scope: MikroTik 61 / HPE 398 / Fortinet 5 reconcile+ / Arista 42 reconcile+).
- **Tooling-validation proof (measured, commit `4467dd5`):** re-emitted Cisco + Meraki fresh → both gate **PASS** (596/596, 25/25, 0 violations); re-priced Cisco 111/596; `audit_semantic.py` = **0/0/0/0/0** on both; QSFP/SFP-substring trap verified handled; built fresh ZIPs (`output/Hexwaren_{Cisco,Meraki}_stage3_4467dd5.zip`) + dump (`_out/audit_semantic_dump.txt`) for INDEPENDENT audit. **4-brand commits HELD** until that audit confirms the tooling. §5 converted to verified-state-only.
- Generalized back-fill to **`_scratch/backfill_brand.py`** (`--content/--brand`, Rule-9 class-derived temp, generic Anwendung + desc-extension) and PROVED it on Cisco + Meraki.
- **Blind spot found + fixed during that proof (commit `63bbcc2`):** the A.4 multi-wavelength fix's coherent regex matched bare `ZR`, so it had **wrongly rewritten 9 grey 10GBASE-ZR optics to "C-Band durchstimmbar"** — which the gate AND `audit_semantic.py` both passed (the value was multi-valued, satisfying the multi_wl check) while being semantically wrong, and `anwendung()` then flipped them to DWDM. Restored the 9 to 1550 nm; sharpened `anwendung()` (dropped bare-"C-Band" DWDM trigger, blanket "ONS-" prefix, and "CWDM"/"CWDM4" lane-grid false matches → grey ZR=Weitverkehr, grey LR4=Campus/Metro, true coherent/tunable still DWDM); fixed `fix_multiwavelength.py`; added **B.6** (tunable wavelength ⇒ coherent/tunable part) to the gate + `audit_semantic.py`. Re-verified: Cisco/Meraki gate PASS, audit_semantic **0/0/0/0/0/0**, `backfill_brand --dry-run` idempotent, 413 tests; fresh ZIPs `…_63bbcc2.zip`. **This is exactly the operator's "prove before scaling" protocol working — caught a real corruption both prior tools missed.**
- **Operator independent audit PASSED (2026-06-13):** Cisco 596 + Meraki 25 confirmed clean, byte-perfect, ZR fix holds, all 5 Meraki fixes landed. Tooling validated → cleared to run the full remaining pipeline AUTONOMOUSLY (4 early brands → 11 fresh → switches), no per-brand check-ins; stop only on CAPTCHA / switches-schema (Rule 7) / low-context. Keep byte-contract + semantic cross-checks live per brand; per-brand ZIP audits are parallel (non-blocking).
- **MikroTik DONE (commit `f538381`, measured):** completeness re-enumerated the official sfp-qsfp grid (25 products) → caught 1 SKU the prior harvest missed (XQ+CM0000-XS+, excluded as a QSFP28→SFP28 port adapter); 24 transceivers taken to gold-parity. Betriebstemperatur grounded properly: 8 MikroTik-published verbatim + 16 Rule-9 class-derived from MikroTik's OWN publishing siblings (industrial −40 low, NOT the generic commercial 0–70 — the backfill default would have been wrong for this brand). DDQ+85MP01D 400G QSFP-DD SR8 Faseranzahl=16 from MPO-16+8ch. Gate PASS 24/24, audit_semantic 0/0/0/0/0/0, Rule-8 parity 0-missing, 413 tests. MSRP captured (`config/market_prices/mikrotik_msrp.yaml`); EUR net deferred (0.55 is Cisco-GPL-calibrated, under-prices budget brand). ZIP `…_f538381.zip`.
- **Pricing-artifact gotcha (learned):** a verification `regen.py <Brand>` re-emits the bundle from content WITHOUT the separate price step, so it clobbers an already-priced Prices CSV → `test_grounded_anchors_are_written_into_the_cisco_prices_csv` fails. Fix: re-run the brand's price step (`price_cisco.py`) after any verification regen of a priced brand. (Hit + fixed this turn; 413 green after re-pricing Cisco.)
- **HPE/Aruba DONE (gate commit `060cfb9` + brand commit `a34a86b`, measured):** 398 gate failures → 0. Betriebstemperatur grounded from the AOS-S/AOS-CX guide's per-module Temperature Rating — 72 verbatim (Commercial 0/70, Industrial −40/+85, Extended −5/85), 61 DAC/AOC/legacy → Rule-9 commercial 0/70. 5 missing speeds grounded (S3N90A/91A 400G, 845420/424-B21 100G, J9054C 100M). **New error class found + fixed: 21 DACs + 3 AOCs were classified under a module form-factor k3 → reclassified to DAC/AOC Kabel; added permanent cross-check B.7 (gate + audit) + cross-brand scan (0 elsewhere).** Also fixed a B.3 multi-wl `\b` false-positive on parallel PLR8/PLR4 (S4B35A) — a gate/audit divergence the dual-check caught. **Completeness re-confirmed by independent full-guide PN-token diff: 147 of 147 standalone transceivers; the ~370 extra tokens are switches/EOL-revisions/aliases/cross-refs (none a standalone transceiver) → no gap.** Gate PASS 147/147, audit_semantic 0×7, Rule-8 parity 0-missing, 413 tests. Pricing deferred (no grounded list). ZIP `…_a34a86b.zip`.
- **Fortinet DONE (commit `fb11cb4`, measured):** 5 reconcile-blocking connectors grounded (3× QSFP-DD 400GE cables → "2× QSFP-DD"; 2× MPO breakout FG-TRAN-QSFP-4XSFP/4SFP-5 → "MPO-12 (QSFP+/QSFP28) zu 4× LC", 40G/100G, lengths 1m/5m). Betriebstemperatur: Fortinet publishes per-module → 85 datasheet-verbatim + FN-TRAN-QSFP+BIDI verbatim 0/70 + FG-TRAN-QSFP+SR-BIDI Rule-9 commercial; 4 MPO exempt. Fixed FG-TRAN-CFP2-LR4 → full 100GBASE-LR4 LAN-WDM set; FN-TRAN-QSFP28 SR→SR4 (Faseranzahl 8); active-DAC SP-CABLE-ADASFP+ desc. **Completeness re-confirmed by token diff: 87/87, the 11 extra datasheet tokens are canonical-PN shorthand (FN-TRAN-1BD10→FN-TRAN-SFP-1BD10), 4-pack variants (FN-TRAN-EX→-4PACK), and "+"-truncations — no gap.** Gate PASS 87/87, audit_semantic 0×7, Rule-8 parity 0-missing, 413 tests. Pricing deferred. ZIP `…_fb11cb4.zip`.
- **Arista DONE (gate commit `951f819` + brand commit `3fd1f61`, measured):** 42 reconcile-blocking cables fixed (Anschlussenden bare "QSFP auf QSFP" → precise QSFP56/QSFP28 by interface standard, breakout ends from PN). 243 DAC/AOC Rule-9 commercial 0/70 (104 modules already 0/70). 18×800G AOC speeds grounded. spec_sentence gained an active-twinax-DAC branch (H-O400/H-D400 400G→4×100G breakouts) + SFP-1G-T copper clause. **3 coherent 400GBASE-ZR modules surfaced a B.6 refinement** (speed-gated GBASE-ZR; grey 10/40G still excluded). Completeness re-confirmed by token diff (347/347; 13 extra = footnote/truncation/form-factor artifacts). Gate PASS 347/347, audit_semantic 0×7, Rule-8 parity 0-missing, 413 tests. Pricing deferred. ZIP `…_3fd1f61.zip`.
- **✅ ALL 4 EARLY BRANDS RE-VERIFIED** (MikroTik, HPE, Fortinet, Arista) + Cisco/Meraki audit-passed = **6 brands gold-parity-complete, audit_semantic 0×7 each.**
- Next: **11 fresh brands** — Avaya/Extreme, Dell, Huawei, Juniper, Lenovo/IBM, NVIDIA/Mellanox, Palo Alto, Ruijie, Supermicro, Ubiquiti, ZTE (full per-brand process: harvest→completeness→author→gate→parity→audit 0×7→price→commit→ZIP). Then switches (Rule-7 schema STOP).
- **CHECKPOINT 2026-06-14 (context budget):** Stopped after completing the 4 early brands (operator's Phase-1 priority) — a clean milestone, everything committed + ZIP'd + verified. **Fresh brands are a from-scratch AUTHORING phase** (grounded German per SKU), the context-heavy part — deferred to the next session to avoid a half-built brand. **NVIDIA groundwork done this session:** `_scratch/nvidia_harvest.py` runs clean (Ethernet/InfiniBand filter, edge-case asserts pass) → **85 Ethernet SKUs** from the 400/200/100/25G LinkX Parts List; an 800G list (`_scratch/nvidia_parts_800g.txt`) is staged but not yet folded in. The other 10 fresh brands have no harvest yet. **Resume point:** start NVIDIA — fold in 800G, fetch per-SKU facts, author to the gold-slice via the author-scaffold + `backfill_brand` pattern, then gate/parity/audit/commit/ZIP like the 6 done brands.
