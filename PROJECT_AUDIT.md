# HexCat — Project Audit & Rolling Context

> **STANDING RULE (non-negotiable, every session until the operator says otherwise):**
> 1. **READ this file first** at the start of any work and **before every update** to anything in the project — it is the single source of truth so context is never lost.
> 2. **UPDATE this file as work proceeds and after every change** (data, code, config, brand completion, decisions).
> 3. **Always tell the operator** when you have **read** this file and when you have **edited** it.
>
> Last updated: 2026-06-14 · Maintained by Claude (Opus) under the Max subscription, $0.
>
> **READ [MISSION.md](MISSION.md) FIRST** (supreme charter). Run its §0 checklist at the start of
> every response. Mission = the WHOLE catalog (ALL categories × ALL brands × ALL SKUs) imported LIVE
> on hexwaren.de via JTL — never narrow it to what's already built.

---

## 0. MASTER CATALOG MANIFEST — the scoreboard (MISSION.md §3 Step 0)

Status legend: `not-started` → `facts` (grounded facts JSON) → `authored` (content) → `emitted`
(ZIP, passed the *legacy* gate L1–L4 + B.1–B.8 + semantic; **NOT yet** the consolidated 8-layer gate
of MISSION.md §8 — L5/L6 partial, **L7 anti-blind-spot fixtures + the consolidated gate.py do NOT yet
exist**) → `audited` (operator L8 independent re-audit passed) → `imported` (live in JTL — operator-side).
**Nothing here is "done" until `imported`.** Counts are grounded SKU counts, gaps flagged in each
`config/coverage/*_completeness.yaml` (most `complete:false`).

### Transceivers / Optics
| Brand | Count | Status | Note |
|---|---|---|---|
| Cisco | 596 | **audited** (op. audit 2026-06-13) + emitted `…_63bbcc2.zip` | core; priced 111 |
| Arista | 347 | **audited** (parallel audit) + emitted `…_f8fd859.zip` | core |
| HPE/Aruba | 147 | **audited** + emitted `…_38ab528.zip` | core |
| Fortinet | 87 | **audited** + emitted `…_38ab528.zip` | |
| NVIDIA | 85 | emitted `…_38ab528.zip` (≤400G Eth) | 800G-Eth = flagged harvest gap |
| Meraki | 25 | **audited** + emitted `…_63bbcc2.zip` | |
| MikroTik | 24 | emitted `…_f538381.zip` | |
| **Juniper** | 26+ | **UNBLOCKED, source cached — harvest next** | core; `datasheets/cache/juniper-optic-modules.pdf` text-parses 26 PNs (1G/SONET/10GE SFP); QSFP/100G+ set on JS `qualified-optics/*.html` (browser rung-c). **ACTIVE NEXT.** |
| Extreme | 91 (facts) | **facts** only — `extreme_transceivers_completeness.yaml` | author after Juniper |
| Dell/Lenovo/Palo Alto/Ubiquiti/Supermicro/Huawei/ZTE/Ruijie | — | **not-started** | §10 source-gated; re-verify per §7.1 ladder |

### Switches (Rule-7 schema)
| Brand | Count | Status | Note |
|---|---|---|---|
| MikroTik | 36/36 | emitted `…_e48e5a7.zip` (legacy gate) | weights cited+cross-checked; **awaiting operator L8 audit** |
| HPE/Aruba/Cisco/Juniper/Arista/Dell/… | — | **not-started** | source-gated; core brands first |

### Server Memory (DDR4/DDR5)
| — | — | ⚠ **DISCREPANCY** | MISSION.md §3/§10 asserts a "25-SKU HPE/Cisco-UCS memory batch", but **the repo has ZERO memory evidence** (no content JSON, no completeness YAML, no DDR/DIMM reference). **NOT assuming it exists** (flag-don't-fabricate). **Needs operator clarification:** built elsewhere? planned? misremembered? If real → locate/import it + formalize `MEMORY_SCHEMA.md`. |

### Other categories (MISSION.md §3 / §6 "TO BUILD")
Routers · Firewalls/Security · Wireless (APs/controllers/antennas) · NICs/Adapters · PSUs ·
Modules/Line cards · Servers/Compute · Cables & accessories · Mounting/rack kits → **all not-started**;
each needs `{CATEGORY}_SCHEMA.md` + semantic checks + anti-blind-spot fixtures → operator sign-off → batches.

### ❗ SCOPE STILL UNKNOWN (blocks a TRUE manifest)
The **actual stocked PN universe** (which categories × brands × PNs Hexwaren stocks/plans) is **not
yet inventoried** — I have no JTL-Wawi or live-hexwaren.de access. The grid above is the *built* state,
NOT the *target* universe. **Operator input needed for Step 0 to be real:** a JTL-Wawi export (or
hexwaren.de category dump, or the sourcing scope) of stocked categories × brands × PNs. Until then,
"complete" cannot be measured against the true denominator — the work order proceeds core-brand-first
(Juniper → Extreme → expansion) on confirmed scope.

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
- **B.7 cable ⇒ cable Kat-3 token** — a DAC/AOC cable (identified by its Kabeltyp) must be classified under a CABLE Kat-Ebene-3 token (DAC/AOC Kabel), never a transceiver-module form factor (QSFP28/SFP+/…). Modules carry no Kabeltyp → low FP risk. (Added after HPE was found with 21 DACs + 3 AOCs under a module k3 — see §9.)
- **B.8 inline-template artifacts** — the author scaffolds left a visibly-broken slot. Scans **EVERY content field** (Kurzbeschreibung, Artikelname, **Beschreibung, Titel-Tag, Meta-Description, FAQ** — `audit_semantic` reads the raw content JSON so it sees the composed intro→Beschreibung + FAQ). Three sub-patterns (FAIL): (a) **unfilled slot** — `von .`, double-space gap after a value-preposition, `ein -X` leading empty token (**INDEFINITE article only** — a definite `die -L-Variante` / `das -I` legitimately discusses a PN suffix), `: .`, empty parens (also tightened so clause-ending nouns "…3 m Länge." and separable verbs "…teilt auf." are NOT flagged); (b) **adjacent duplicate token** in Artikelname/Titel (`DAC DAC`); (c) **doubled separator** in Artikelname/Titel (`, –`). (Added 2026-06-14; **widened to all fields after the parallel audit found B.8's Kurz-only coverage let `ein -X`/`von .` persist in Beschreibung+FAQ on HPE 5 / Fortinet 2 / NVIDIA 1** — see §9.) **Note on B.3:** the multi-wl regex uses `\b` guards so a parallel single-mode type (PLR4/PLR8 — one 1310 nm wavelength over parallel fibres) does NOT match its WDM cousin (LR4/LR8); validate.py was also aligned to audit_semantic.py (it had been missing LR8). **Note on B.6:** the coherent-type regex matches speed-gated `\d{3}G(?:BASE)?[- ]?ZR` so genuine coherent **100/400/800GBASE-ZR(P)** (legitimately C-band-tunable) pass, while grey direct-detect **10/40GBASE-ZR** (2-digit G) stay excluded — preserving the grey-ZR fix. (Refined when Arista's 400GBASE-ZR modules were false-flagged.)

Audit tool: **`_scratch/audit_semantic.py [Brand ...]`** — per-brand (defaults Cisco+Meraki); enumerates every instance of all **8** classes (ff_conn / faser / multi_wl / tunable_wl / dash / hersteller / cable_k3 / template).

---

## 5. Brand status

> **Verified-state-only:** this table records MEASURED facts (actual gate output, `audit_semantic.py`
> per-check counts, Rule-8 parity tallies) — never "done" assertions. If it isn't measured, it isn't
> stated as fact. Re-run to confirm: `python -m hexcat.cli stage3 …` (gate), `python _scratch/audit_semantic.py`
> (cross-checks), the §6 pricing run, and `python -m pytest -q`.

| Brand | Content SKUs | Measured gate | audit_semantic (8: ff/faser/multiwl/tunwl/dash/herst/cablek3/**template**) | Pricing | Notes |
|---|---|---|---|---|---|
| **Cisco** | 596 | **PASS 596/596, 0 violations** (2026-06-13, commit `63bbcc2`) | **0 / 0 / 0 / 0 / 0 / 0** | 111/596 priced (T1 7, FAMILY 98, T2-LIST 6; rest 0,00 debt) | Rule-8 parity: Anwendung/Geschwindigkeit/Betriebstemperatur(non-MPO) **0-missing**. Flagged (held, need a Cisco source): QDD-800G-VR8, SFP10G-USR, MGBBX1, ONS-QSFP-4X10-MER/MLR. 4 MGB* are Cisco SB. **Count traceable:** 594 pre-correction + 4 MGB − 2 exclusions (ONS-QDD-OLS EDFA, E1000-2-G line card) = 596 ✓. ZIP `output/Hexwaren_Cisco_stage3_63bbcc2.zip`. |
| **Meraki** | 25 (MA-* only) | **PASS 25/25, 0 violations** (2026-06-13, commit `63bbcc2`) | **0 / 0 / 0 / 0 / 0 / 0** | 0/25 (PENDING, no comp yet) | Rule-8 parity: required attrs **0-missing**. MGB* reassigned to Cisco SB. 2 MA-CBL-SPWR excluded (power cables). Rule-9 temp. ZIP `output/Hexwaren_Meraki_stage3_63bbcc2.zip`. |
| **Arista** | 347 | **PASS 347/347, 0 violations** (2026-06-14, commit `3fd1f61`) | **0×8** | deferred (no prices in datasheet; 0,00) | ✅ DONE. Completeness 347/347 (Arista Transceivers Data Sheet); token diff confirms no gap (13 extra = footnote/truncation/bare-form-factor artifacts). Fixed 42 reconcile connectors (Anschlussenden bare "QSFP"→QSFP56/QSFP28 by standard). 243 DAC/AOC Rule-9 commercial 0/70. 18×800G speeds grounded; 3 coherent 400GBASE-ZR drove B.6 ZR-speed-gate refinement. Rule-8 parity 0-missing (SFP-1G-T copper exempt). ZIP `output/Hexwaren_Arista_stage3_f8fd859.zip`. |
| **HPE/Aruba** | 147 | **PASS 147/147, 0 violations** (2026-06-13, commit `a34a86b`) | **0×8** (all incl B.7 cable_k3) | deferred (no grounded list; netto_vk 0,00) | ✅ DONE. Completeness: 147 of 147 standalone catalog transceivers (AOS-S/AOS-CX guide); independent full-guide token diff confirms the ~370 other PN-tokens are switches/EOL-revisions/aliases (R9F75A=JL309A)/cross-refs, no gap. Betriebstemperatur: 72 verbatim from the guide's per-module Rating + 61 Rule-9 commercial. **Fixed 21 DAC + 3 AOC mis-classified under module k3 → DAC/AOC Kabel (drove new B.7).** 5 speeds grounded. Rule-8 parity 0-missing. ZIP `output/Hexwaren_HPE_stage3_38ab528.zip`. |
| **Fortinet** | 87 | **PASS 87/87, 0 violations** (2026-06-14, commit `fb11cb4`) | **0×8** | deferred (datasheet has no prices; 0,00) | ✅ DONE. Completeness 87/87 (Fortinet Transceivers Data Sheet); token diff confirms no gap (11 extra tokens = shorthand/4-pack/"+"-truncations of captured SKUs). Fixed 5 reconcile-blocking connectors (3 QSFP-DD cables + 2 MPO breakouts). Betriebstemperatur 85 datasheet-verbatim (Fortinet publishes). FG-TRAN-CFP2-LR4 wavelength set; QSFP28 SR→SR4. Rule-8 parity 0-missing. ZIP `output/Hexwaren_Fortinet_stage3_38ab528.zip`. |
| **MikroTik** | 24 | **PASS 24/24, 0 violations** (2026-06-13, commit `f538381`) | **0 / 0 / 0 / 0 / 0 / 0** | 24/24 MSRP captured (grounded); EUR net DEFERRED to supplier feed | ✅ DONE. Completeness: captured 24 of 25 (official sfp-qsfp grid); XQ+CM0000-XS+ excluded (QSFP28→SFP28 port adapter). Betriebstemperatur: 8 published verbatim + 16 Rule-9 sibling-corroborated industrial (NOT commercial — MikroTik publishes -40 lows). DDQ+85MP01D=400G QSFP-DD SR8 (Faseranzahl 16, MPO-16). Rule-8 parity 0-missing. ZIP `output/Hexwaren_MikroTik_stage3_f538381.zip`. 14 non-blocking warnings (length-variant DAC prose reuse). |
| **MikroTik Switches** | **36 / 36** | **PASS 36/36, 0 violations** (2026-06-14, commit `e48e5a7`, ZIP `…_e48e5a7.zip`) | **0×8** + S.1-S.6 + weight guard | 36/36 MSRP; EUR deferred | ✅ **DONE 36/36** — 1st SWITCH brand (Rule-7). schema/combo/access/S.1-S.6/B.1-B.8/weight-guard all PASS; env-first L3 Managed(L3)/Smart/Industrie/DC; temp datasheet-verbatim. **Weights:** MikroTik doesn't publish them ($0-verified) → operator-approved distributor weights, every value cited + cross-checked in `datasheets/cache/mikrotik-switch-weights.yaml` (dateks.lv net+gross / mikrotik-store.eu / datagram.ae; templated-default detection; corrected /min disagreement flag; CSS610-8P & CRS328 overrides documented). All 6 once-blocked SKUs sourced in a best-effort 2nd pass (CRS804 4,02/CRS812 4,75 dateks+ms; CSS106-5G-1S 0,212 datasheet-net → guard floor lowered 0,30→0,15; CSS106-1G-4P/CRS318-OUT/CSS610-OUT via ms+web). Completeness 36 of 40 (4 non-switches excluded). |
| **NVIDIA** | 85 | **PASS 85/85, 0 violations** (2026-06-14, commit `148ed65`) | **0×8** | deferred (no list; 0,00) | ✅ DONE (1st FRESH brand). LinkX Ethernet ≤400G: DAC 26/DAC-SPLIT 6/AOC 28/AOC-SPLIT 13/XCVR 12. Authored via nvidia_facts.py → nvidia_author.py (adapted arista_author.py) → backfill. Lane-aware XCVR optics (1-lane serial=single λ; 4-lane WDM=LAN-WDM/CWDM4 set; MPO SR8/DR4). Rule-9 commercial 0-70. Rule-8 parity 0-missing. **Completeness `false`: 800G-Ethernet (Spectrum-X) is a flagged HARVEST GAP** (deprecated 800G list was XDR/IB). ZIP `output/Hexwaren_NVIDIA_stage3_38ab528.zip`. |

**Fresh brands not started:** Avaya/Extreme, Dell, Huawei, Juniper, Lenovo/IBM, Palo Alto, Ruijie, Supermicro, Ubiquiti, ZTE. (NVIDIA ≤400G DONE — 800G-Eth follow-up pending; Brocade parked; Polycom = no transceivers.)
**Switch category:** not started — needs its OWN gold-slice schema + taxonomy (Rule-7 approval before authoring); everything else (completeness, gate, Rule 8/9, byte contract, cross-checks, per-brand process) carries over.

**Test suite (measured):** 413 tests (28 files), all green — last run 2026-06-14 (commit `cef7c27`, incl B.8). Run: `PYTHONIOENCODING=utf-8 python -m pytest -q`. **All 6 brands (Cisco/Meraki/MikroTik/HPE/Fortinet/Arista) re-verified `audit_semantic = 0` across all 8 checks (incl B.8) on 2026-06-14.**

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
- **✅ ALL 4 EARLY BRANDS RE-VERIFIED** (MikroTik, HPE, Fortinet, Arista) + Cisco/Meraki audit-passed = **6 brands gold-parity-complete.**
- **Operator parallel audit PASSED (2026-06-14)** on MikroTik/HPE/Fortinet/Arista + Meraki re-check — byte contract, 7 checks, floors, schema, cross-file all reproduced at zero; judgment calls (Arista QSFP56/28-by-speed, HPE reclassified cables, MikroTik temps + adapter exclusion) verified correct. Flagged a new class: **inline-template artifacts** → added **B.8** (gate commit `cef7c27`): empty slot / adjacent dup token / doubled separator, with the regex tightened so legit clause-ending nouns & separable verbs don't FP. **Back-applied (brand commit `f8fd859`):** Fortinet 23 (DAC DAC collapse + 2 FG-TRAN inline slots), Arista 243 (', –' separator + 'ein -X' + capitalized lowercase cable terms), **HPE 5** ('ein -X' slots the manual audit missed — B.8 caught them). Re-emitted HPE/Fortinet/Arista ZIPs `…_f8fd859.zip`; Cisco/Meraki/MikroTik clean (untouched). **audit_semantic now 0×8 across all 6 brands**, 413 tests green.
- Next: **11 fresh brands** — Avaya/Extreme, Dell, Huawei, Juniper, Lenovo/IBM, NVIDIA/Mellanox, Palo Alto, Ruijie, Supermicro, Ubiquiti, ZTE (full per-brand process: harvest→completeness→author→gate→parity→audit **0×8**→price→commit→ZIP). Then switches (Rule-7 schema STOP).
- **CHECKPOINT 2026-06-14 #3 (context budget, after B.8 + NVIDIA foundation):** B.8 done + 6 brands at audit_semantic **0×8** + ZIPs re-emitted. **NVIDIA harvest + facts + completeness FINALIZED this session** (content authoring is the only remaining NVIDIA step). Stopping before authoring because a brand is only committable at all-GREEN — a partial authoring yields nothing durable while risking a half-built brand. Built + verified:
  - `_scratch/nvidia_harvest.py` → **85 Ethernet SKUs** (IB filtered, edge-case asserts pass); `_scratch/nvidia_facts.py` → `output/stage3/nvidia_facts.json` with grounded per-SKU specs (speed/ff/type/length/config). Breakdown: DAC 26 / DAC-SPLIT 6 / AOC 28 / AOC-SPLIT 13 / XCVR 12; 400G 16 / 200G 31 / 100G 30 / 25G 8; QSFP-DD 17 / QSFP56 32 / QSFP28 28 / SFP28 8.
  - **800G determination (operator-requested):** the staged 800G list is deprecated XDR/InfiniBand (0 Ethernet) → out of scope. BUT Spectrum-X (SN5600) is an 800G **Ethernet** platform, so 800G-Ethernet LinkX parts likely exist; no structured $0 list located this sweep (deeper crawl risked CAPTCHA, operator away). → **85 = the complete ≤400G Ethernet set; 800G-Ethernet flagged as a follow-up HARVEST GAP** (NOT claiming full universe). Logged in `config/coverage/nvidia_transceivers_completeness.yaml` (`complete: false`).
  - **RESUME POINT — author NVIDIA:** adapt `_scratch/arista_author.py` … (done — see next entry).
- **NVIDIA DONE (commit `148ed65`, measured) — 1st FRESH brand authored end-to-end:** `nvidia_facts.py` → `nvidia_author.py` (adapted arista_author.py: cable vs XCVR branch, pad floors, lane-aware `xcvr_optics`) → `backfill_brand`. **Gate PASS 85/85, audit_semantic 0×8, Rule-8 parity 0-missing, 413 tests.** Key authoring lessons (apply to the next 10 fresh brands): (a) the cross-SKU **boilerplate gate** fails any ≥6-word Beschreibung sentence shared by >25% of SKUs — so weave a per-SKU-unique token (PN, or length+ends) into EVERY intro sentence and merge generic phys/power as clauses (no standalone generic sentence); (b) **"neu und versiegelt" is a banned hard-fail** — use the comma form "Neu, versiegelt"; (c) **lane-aware wavelengths** — 1-lane serial = single λ (no LR4/FR4 token), ≥4-lane WDM = the standard SET (100G-LR4 LAN-WDM 1295–1309, CWDM4 1271–1331 for 100G-CWDM4/200G/400G-FR4), MPO parallel = single λ SR8/DR4; (d) add the brand to `config/rules.yaml` vendors. Completeness `false` — **800G-Ethernet (Spectrum-X) flagged harvest gap.** ZIP `…_148ed65.zip`.
- Next: 800G-Eth follow-up harvest (when a $0 parts list is locatable), then the remaining 10 fresh brands — same facts→author→backfill→gate→ZIP pattern; then **switches (Rule-7 schema STOP).**
- **CHECKPOINT 2026-06-14 #4 (after NVIDIA + fresh-brand source recon):** NVIDIA done (1st fresh brand, `148ed65`). The other 10 fresh brands have NO cached source — harvesting each needs locating + $0-fetching its enumeration, and **several sources are $0-BLOCKED** (external-dependency blocker like CAPTCHA): Supermicro + Dell support pages → **403**; Juniper transceiver list → **JS-gated HCT app** (apps.juniper.net/hct, no static HTML); Lenovo Press needs the correct doc URL (guessed `lp1380` is the wrong/withdrawn product). **FETCHABLE source FOUND + CACHED:** Extreme Networks Optics Solution Guide → `datasheets/cache/extreme-optics-solution-guide.pdf` (986 KB, 15 pp, has the SFP/SFP+/SFP28/SFP-DD/QSFP+/QSFP28 line + PNs like 100G-QSFP-ESR4) — plus the EXOS optics DB (optics.extremenetworks.com/EXOS) for full specs. **RESUME POINT — next fresh brand = Extreme:** parse the cached PDF (+ EXOS DB for reach/wavelength) → `extreme_facts.json` → author via the `nvidia_author.py` pattern (cable/XCVR branch, per-SKU-unique sentences, lane-aware wavelengths, comma-form meta, add `Extreme` to `config/rules.yaml` vendors) → backfill → gate → ZIP. For the $0-blocked brands (Supermicro/Dell/Juniper/Huawei/ZTE), the operator may need to provide a source PDF or solve the gate (same model as the CAPTCHA / supplier-feed dependencies). **Authoring lessons for all fresh brands are in the NVIDIA entry above.**
- **B.8 field-coverage blind spot FIXED (operator parallel audit, gate `8f55522` + back-apply `38ab528`):** B.8 had only scanned Kurzbeschreibung + Artikelname → the same `ein -X`/`von .` artifacts persisted UNDETECTED in **Beschreibung (composed from intro) + FAQ** (NVIDIA proved it — authored AFTER B.8 yet a FAQ `von .` slipped). Widened B.8 to **all fields** (Kurz/Artikelname/Beschreibung/Titel/Meta + FAQ cell); `audit_semantic` now scans the raw content JSON (intro→Beschreibung, FAQ). Re-run FAILED on HPE 5 / Fortinet 2 / NVIDIA 1 (proving coverage) → fixed: HPE intro `ein -Transceiver`→`ein Transceiver`; Fortinet intro hyphen + FAQ `Länge von .`→1m/5m; NVIDIA re-authored with PN-length fallback (FNM050→50 m) + FLAG guard. Also **refined the leading-empty pattern to INDEFINITE articles only** — a definite `die -L-Variante`/`das -I` legitimately discusses a PN suffix (caught + cleared 6 Cisco FAQ false-positives, so Cisco needed NO change). **All 7 brands now audit_semantic 0×8 across ALL fields; 413 tests.** Re-emitted HPE/Fortinet/NVIDIA ZIPs `…_38ab528.zip` (Arista/Cisco/Meraki/MikroTik unchanged, verified in-place). **Lesson for all future authoring: fill every slot; the gate now hard-fails empty slots in any field.**
- Next: resume at **Extreme** (cached PDF) → remaining fresh brands; then switches (Rule-7 STOP).
- **MikroTik Switches — operator switch audit (`e3b43aa`) defects fixed + back-applied to the gate (commit `33e3e8d`, measured):** the format gate + S.1-S.5 passed a batch that was NOT import-ready; the operator's grounding audit caught 3 real defects + a missing guard. **#2 combo ports dropped (4 SKUs):** `mikrotik_switch_author.py` PORT_KEYS missed "Ethernet Combo ports" / "Number of Combo 10G Ethernet/SFP+ ports" → re-mapped; Portanzahl/Port-Konfiguration re-derived (CRS106 5→6, CRS328-4C/CRS312-4C/CRS326-4C +4 combo). Added permanent **S.6** (gate): PN-encoded port groups — esp. combo "C" — must appear in Port-Konfiguration (catches the consistent-omission class S.3's sum can't see). **#3 access-speed read the 100M management port** (6 high-speed switches, incl a 100G DC switch, were emitting "100 Mbit/s"): rewrote Port-Geschwindigkeit to exclude a lone 10/100 mgmt port and take the dominant user-facing port (verified 100G/25G/10G). **#1 weight guard added** (gate): a switch `Artikelgewicht` ≤ the optics placeholder / under the 0,30 kg switch floor HARD-FAILS — **back-applied so every future switch brand is protected.** **#4** SWITCHES_SCHEMA_PROPOSAL.md S.5 wording reconciled to the code + S.6/weight-guard documented. CRS418 WiFi-6 variant differentiated. **Gate now isolates cleanly: 36 violations ALL `Artikelgewicht`, 0 non-weight (combo/access/S.1-S.6/B.1-B.8 all PASS); 413 tests green.** **BUT real MikroTik switch weights are NOT $0-reachable** — verified absent from the product page, specs page, manual page, and Confluence REST API; the spec widget is JS-rendered and the Playwright Chromium binary is not installed (browser fetch is the operator-gated/CAPTCHA-opt-in path). Per 1000%-grounding "flag don't fabricate," the placeholder is NOT shipped → **MikroTik switches HELD on weight-grounding** (see §10). Stale defective ZIP `…_e3b43aa.zip` removed; no clean re-emit until weights land.
- Next: resume at **Extreme** (transceivers, cached PDF) → remaining fresh brands. **MikroTik switches unblock = a weight source** (operator drops a weight list, or approves the browser/CAPTCHA fetch — §10).
- **Extreme UNBLOCKED + facts BUILT (2026-06-14, this session) — corrects the stale §10 "not groundable" note.** The cached `extreme-optics-solution-guide.pdf` was previously judged un-groundable, but that used pdfplumber `extract_text` (mangles the 3-column layout); **`extract_tables()` recovers 72 clean `Standard/Type | Description | Extreme SKUs` rows.** Built `_scratch/extreme_facts.py` → **`output/stage3/extreme_facts.json` = 91 grounded SKUs** (46 transceivers, 45 cables: 36 DAC/9 AOC, 14 breakouts) + `extreme_flags.txt` (8 flags, ALL legitimate — verified). **Grounding decisions** (in `config/coverage/extreme_transceivers_completeness.yaml`): one SKU per physical optic (artikelnummer = first descriptive Extreme PN; numeric + 35 legacy Avaya/Enterasys `AA-`/`MGBIC-` codes captured in `alt_pns`); cable rows split into per-length SKUs (length from PN suffix); cable TYPE from the PN (`DACP`=passiv/`DACA`=aktiv/`AOC`) not the row label; **lane-aware λ derived from the IEEE standard** (37/46 transceivers — 100G-LR4 LAN-WDM vs 40G-LR4 CWDM4 correctly distinguished; 9 BiDi/4WDM/SWDM4 left blank for EXOS-DB/backfill). **Source corruption handled flag-don't-fabricate:** PDF cell-shift put the `25GBASE-ER` PN in the `25G-DACP` row and the real `25G-DACP-*` PNs in the `25G-AOC` row — excluded the shifted cell, recovered the DACP length-PNs and **re-typed them DAC (passive)** from the PN; the numeric-only 25G-AOC + 100G-AOC-Breakout lengths excluded (length↔code unprovable); 3 source-duplicated DACA rows deduped; 3 `-1001` alternate-naming codes excluded. **RESUME — author Extreme:** adapt `_scratch/nvidia_author.py` (cable/XCVR branch, per-SKU-unique PN-woven sentences, fill-every-slot for B.8) to the **Extreme switching theme** (ExtremeSwitching/ExtremeRouting + the guide's "Extreme Optics Compatibility-Matrix" note; `alt_pns` → a "kompatible Bestellnummern" line), derive **Faseranzahl** (MPO 4-lane SR4/ESR4/PSM4=8, LC duplex=2, BiDi=1, RJ45/copper=none; SR10-CFP2 uncertain → omit), use the λ already in facts, **add `Extreme` to `config/rules.yaml` vendors** → `backfill_brand --brand Extreme` (Rule-9 commercial temp + Anwendung) → gate PASS → Rule-8 parity → `audit_semantic.py Extreme` 0×8 → price 0,00 → commit → ZIP. Then the remaining fresh brands stay §10-source-gated.
- **MikroTik switch WEIGHTS — operator-approved scoped browser fetch EXECUTED; conclusively NOT $0-reachable (2026-06-14).** Operator granted a one-time browser exception (mikrotik.com product pages only; opt-in stop otherwise stands). Installed Playwright Chromium and rendered all 36 product pages (no CAPTCHA, full JS render): **0/36 carry a Weight row** in the rendered spec widget (Dimensions present, weight absent — confirmed across old/PoE/DC/industrial/smart). Fetched + parsed all **63 linked `cdn.mikrotik.com` datasheet leaflet PDFs**: the word "weight" appears in **none** (their specs tables list Dimensions/temp/power only); dimensions PDFs are CAD drawings; `help.mikrotik.com` 404s. **The approval's premise — that the rendered widget carries weight — does not hold: MikroTik simply does not publish switch weight in any public $0 source.** Per the operator's contingency ("if it genuinely can't be read even via the browser, flag it — don't fabricate"), all 36 stay weight-blocked; weights NOT fabricated; guard correctly blocks. Probe data in `output/stage3/mikrotik_weight_probe.json`. **Unblock now requires a non-MikroTik source** (distributor/retail datasheet, a dropped weight list, or explicit approval to emit a marked-DERIVED weight) — see §10 WEIGHTS row. Injection path confirmed ready: per-SKU `Artikelgewicht`/`Versandgewicht` in the content JSON via a 1-line `entry_to_intake` change (backward-compatible; transceivers keep deriving from `weights.yaml`), `Versand>Artikel` enforced, guard floor lowerable to ~0,15 kg for light switches.
- **MikroTik switches WEIGHTED → gate GREEN 30/36; re-emitted (commit `ae90c7b`, ZIP `…_ae90c7b.zip`).** Operator approved a SCOPED grounding relaxation (this one manufacturer-unpublished attribute only): use distributor/retail published weight, every value cited + cross-checked. Harvested via httpx ($0, no browser): **dateks.lv** (net+gross, logistics-grade) > **mikrotik-store.eu** (dedicated store) > **datagram.ae**. Triangulated all 3; the cross-check caught real data-quality traps — **dateks templated-duplicate pairs** (CRS320=CRS326-24S=2.153; CRS504=CRS518=3.40) and **datagram's "3.5 kg" repeated across 5 switches** (a default) — both discarded via duplicate-detection. 4 material (>40%) disagreements noted for spot-check; **CSS610-8P-2S+IN override** (dateks 0.7 kg rejected as physically implausible — a PoE switch can't be lighter than its non-PoE sibling CSS610-8G @1.1; used mikrotik-store 2.21). Resolved **30/36**, cited per-SKU in `datasheets/cache/mikrotik-switch-weights.yaml` (Artikelgewicht=net, Versandgewicht=published-gross-or-DERIVED×1.20). `reconcile.py` `entry_to_intake` now reads per-SKU weights (backward-compatible). **GATE GREEN 30/30, 0 violations** (weight guard PASS — all ≥0,40 kg > 0,30 floor, so floor unchanged; combo/access/S.1-S.6/B.1-B.8 all PASS), audit_semantic **0×8**, `Versand>Artikel` holds, 413 tests. **6 SKUs weight-blocked** (no $0 distributor source across 5 distributors + search — flagged, NOT fabricated): CSS106-5G-1S, CSS106-1G-4P-1S, CRS318-1Fi-15Fr-2S-OUT, CRS804-4DDQ-hRM, CRS812-8DS-2DQ-2DDQ-RM, CSS610-1Gi-7R-2S+OUT. **Follow-ups:** (a) source the 6 (then re-derive lifts to 36/36); (b) formal Verification_Log weight-rows (the YAML is the citation record now — needs a `weight_source_url` on SkuRecord + `_verification_rows` emit). Operator gates + spot-checks weights vs the cited URLs.
- **MikroTik switches → 36/36 (commit `e48e5a7`, ZIP `…_e48e5a7.zip`) — operator follow-ups A+B done.** **(A) Provenance:** fixed the cross-check disagreement formula to `|a−b|/min(a,b)` (was `/chosen`, which under-counted) — now correctly fires on CRS328 (5,02 vs datagram 3,5) and CSS318 (2,2 vs ms 1,5); added explicit rationale on CRS328 (datagram 3,5 = templated default rejected — the gold-slice SKU's founding datapoint, now documented), CSS318 (dateks_net logistics-grade), CRS112 (PoE-anchor: kept 1,7, 0,8 too light), CSS610-8P (dateks 0,7 implausible → ms 2,21). YAML-only; the 30 values were unchanged (no re-emit needed for A). **(B) Best-effort 2nd pass sourced ALL 6 once-blocked SKUs** (broadened to balticnetworks + ServeTheHome teardowns + web search; cited + cross-checked): CRS804-4DDQ-hRM 4,02/4,4 (dateks net+gross, ms 3,9 ~3%), CRS812-8DS-2DQ-2DDQ-RM 4,75/5,1 (dateks, ms 5,4 ~7%; a '2,8' snippet outlier rejected), CSS106-5G-1S **0,212** (RB260GS datasheet-net → **guard floor lowered 0,30→0,15** in `validate.py` so a real light switch is admitted while the 0,05/0,20 placeholder still hard-fails), CSS106-1G-4P-1S 0,7 / CRS318-1Fi-15Fr-2S-OUT 2,4 / CSS610-1Gi-7R-2S+OUT 2,1 (mikrotik-store = web-search agree). **GATE GREEN 36/36, 0 violations; audit_semantic 0×8; 413 tests.** `flagged_no_distributor_weight: []`. **MikroTik switches fully DONE.** Outstanding switch follow-up = formal Verification_Log weight-rows only (YAML is the citation record).
- **MISSION CHARTER + MASTER MANIFEST (commit `9de02cf`) — operator course-correction against drift/scope-narrowing.** Saved `MISSION.md` verbatim (supreme charter; §0 checklist to run EVERY response; mission = WHOLE catalog × all brands → live on hexwaren.de via JTL, not just transceivers+switches). Wired `CLAUDE.md` to read it first. Bootstrapped the **MASTER MANIFEST (§0, the scoreboard)** grounded in actual repo state: 7 transceiver brands + MikroTik switches `emitted` (status honestly NOT "done" — the consolidated 8-layer gate + L7 anti-blind-spot fixtures don't exist yet; L8 operator audit + JTL import pending). **Server-Memory DISCREPANCY flagged:** the charter asserts a 25-SKU memory batch but the repo has ZERO evidence → needs operator clarification, NOT assumed. **True stocked PN universe unknown** (no JTL-Wawi/hexwaren.de access) → operator export needed for Step 0 to be real.
- **Juniper UNBLOCKED (core brand, was wrongly parked — failure #5) via the §7.1 ladder.** Re-verified the stale "JS-gated/blocked" label: rung (a) the QFX10000 doc page is prose (no PN table); rung (b) **`juniper-optic-modules.pdf` cached + text-parses 26 grounded PNs** (SFP 1G/SONET-OC3/12/48/10GE). The fuller QSFP/100G/400G set is on JS `qualified-optics/*.html` (browser rung-c, scoped-approved). **RESUME — Juniper transceivers:** parse the cached PDF text (text-mode, not extract_tables) → `juniper_transceivers_facts.json`; browser-fetch the qualified-optics JS pages for the QSFP/100G+ PNs; cross-check via the Juniper doc per-platform spec pages; author via the `nvidia_author.py` scaffold (add Juniper to `rules.yaml` vendors: hersteller/slug `juniper`); backfill → gate → completeness → ZIP → operator audit. THEN Extreme (facts already built, `d59eee8`), then expansion brands, then non-transceiver category schemas (§10.5).

---

## 10. SOURCE MANIFEST — operator action to unblock fresh brands ($0-harvest blockers)

The 10 remaining fresh brands have **no cached source** and their official transceiver enumerations
are not $0-fetchable in a cleanly-parseable form (the same external-dependency class as a CAPTCHA /
the supplier price-feed). Per brand: the source to use · why it's blocked · **exactly what file to
drop into `datasheets/cache/` to unblock authoring**. A good drop-in is a parts list / datasheet with
per-SKU: PN · speed · form factor · type/reach (SR/LR/FR4/…) · connector · wavelength · media · (cable) length.

| Brand | Source to use | Blocker (measured) | Drop into `datasheets/cache/` |
|---|---|---|---|
| ~~**Extreme** (+Avaya)~~ **UNBLOCKED** | Cached `extreme-optics-solution-guide.pdf` (15 pp) | **CORRECTED**: the "marketing-bled / not groundable" note used `extract_text` (mangles columns); `extract_tables()` recovers 72 clean rows → **groundable**. Facts BUILT (`extreme_facts.json`, 91 SKUs). No operator action needed to author. | *(optional)* EXOS DB CSV for the 9 blank-λ BiDi/4WDM parts + DDM — not blocking |
| **Dell** | Dell "Networking Optics & Cables" support KB / SFP datasheet | dell.com support → **403** on $0 GET | `dell-optics.{pdf,csv}` |
| **Supermicro** | supermicro.com networking accessories / transceiver datasheet | **403** on $0 GET | `supermicro-transceivers.{pdf,csv}` |
| **Juniper** | Juniper HCT `apps.juniper.net/hct` / optics datasheet | **JS-gated** single-page app — no static HTML enumeration | `juniper-optics.{csv,pdf}` (HCT export) |
| **Lenovo/IBM** | Lenovo Press "ThinkSystem Network Transceivers & Cables" guide | static + fetchable, but the **correct `lpNNNN` URL** wasn't found (guessed `lp1380` = wrong/withdrawn product) | the correct Lenovo Press doc URL, or `lenovo-transceivers.pdf` |
| **Huawei** | Huawei optical-module datasheets (`support.huawei.com`) | likely login/region-gated (untested $0) | `huawei-optical-modules.{pdf,csv}` |
| **ZTE** | ZTE optical-module datasheets | untested $0 (likely gated) | `zte-optics.{pdf,csv}` |
| **Ruijie** | Ruijie optical-transceiver datasheets | untested $0 | `ruijie-optics.{pdf,csv}` |
| **Palo Alto** | PAN-OS-compatible transceiver list (`docs.paloaltonetworks.com`) | untested $0 | `paloalto-transceivers.{pdf,csv}` |
| **Ubiquiti** | ui.com store (UF-*, UACC-* optics/DAC) | JS store, specs sparse | `ubiquiti-optics.{csv,pdf}` |
| **NVIDIA 800G-Eth** | NVIDIA LinkX **800G Ethernet** (Spectrum-X) parts list | no $0 static list located (the cached 800G list is XDR/InfiniBand) | `nvidia-800g-ethernet-parts.pdf` (same shape as the cached 400/200/100/25G list) |
| ~~**MikroTik switches — WEIGHTS**~~ **RESOLVED 36/36** | distributor/retail static HTML (dateks.lv / mikrotik-store.eu / datagram.ae) | **DONE** — all 36 weighted via operator-approved distributor weights, cited + cross-checked in `datasheets/cache/mikrotik-switch-weights.yaml` (gate GREEN, ZIP `…_e48e5a7.zip`); `flagged_no_distributor_weight: []`. The 6 once-blocked SKUs all sourced in a best-effort 2nd pass. *(historical: MikroTik itself does not publish switch weight —* **EXHAUSTIVELY VERIFIED 2026-06-14 with operator-approved browser fetch** (Playwright Chromium, no CAPTCHA, full JS render): rendered HTML spec widget **0/36** (32–44 spec rows each, Dimensions present, no Weight row); the 63 linked `cdn.mikrotik.com` datasheet leaflet PDFs contain the word "weight" **nowhere** (specs tables list Dimensions/temp/power but no weight); dimensions PDFs are drawings only; Confluence REST API + `help.mikrotik.com` none. The browser approval's premise (widget carries weight) does not hold. Per 1000%-grounding the placeholder is not shipped → the **weight guard hard-fails all 36**. | A weight source MikroTik itself doesn't provide: a **distributor/retail datasheet or the retail-box spec** listing per-SKU kg (a NEW grounding-source decision — outside the scoped mikrotik.com fetch), OR drop `mikrotik-switch-weights.{csv,yaml}` (PN → Artikelgewicht kg), OR operator explicitly approves emitting with a clearly-marked DERIVED/estimated weight (relaxes 1000%-grounding for this one attribute). Once a source lands, the batch re-emits clean immediately (all other work done; injection path = per-SKU `Artikelgewicht`/`Versandgewicht` in the content JSON). |

**SWITCH sources (same gating):** MikroTik switches are **DONE 30/36** (gate GREEN, ZIP emitted; weights
from cited distributor sources) — only 6 SKUs await a weight source (see the WEIGHTS row above). Every OTHER brand's switches
are source-gated like its transceivers — drop a switch parts list / datasheet into `datasheets/cache/`
as `<brand>-switches.{pdf,csv}` (per-SKU: management class · layer · port-config · PoE · Bauform · temp)
and the switch pipeline (schema + S.1-S.5 + all-fields B.8, all live) runs it via the MikroTik-switch
pattern (`mikrotik_switch_author.py`). Add a vendor entry to `config/rules.yaml` for any new brand.

**Process once a source is dropped in:** run the NVIDIA pattern — `<brand>_facts.py` (parse the cached
file) → author via the `nvidia_author.py` scaffold (cable/XCVR branch, per-SKU-unique sentences,
lane-aware wavelengths, comma-form meta, **fill every slot — widened B.8 hard-fails empty slots in any
field**) → add the brand to `config/rules.yaml` vendors → `backfill_brand` (Rule-9 commercial temp) →
gate PASS → Rule-8 parity → `audit_semantic.py <Brand>` 0×8 (all fields) → price 0,00 → commit → ZIP.

---

## 11. Switches — gold-slice schema ✅ SIGNED OFF + IMPLEMENTED (see status block at the end of this section)

Full schema in **`SWITCHES_SCHEMA_PROPOSAL.md`** (repo root). Surfaced + signed off 2026-06-14 (Rule 7).
The original proposal summary below is HISTORICAL — the **applied** schema (4 amendments) is in the
"SCHEMA SIGNED OFF + IMPLEMENTED + PROVEN" block further down. Original decisions (pre-amendment):
- **L2** `Switches` + **Attributgruppe** `Switche` (one-char-diff convention).
- **L3 locked set (6):** Unmanaged / Smart-Managed / Managed (L2) / Managed (L3) / Data-Center / Industrie.
- **15 switch attributes** (fixed order = Sortiernummer): Switch-Typ, Layer, Portanzahl,
  Port-Konfiguration, Geschwindigkeit, Uplink-Ports, PoE, Switching-Kapazität, Durchsatz,
  Formfaktor, Stromversorgung, Kühlung, Stacking, Betriebstemperatur (Rule 9), Anwendung.
- **4 new cross-checks S.1–S.4** (PoE↔PoE-port, L3↔Managed, Portanzahl↔Port-Konfiguration sum,
  Stacking↔class). Byte contract + 7 files + floors + B.1–B.8 + Rule 8/9 all carry over unchanged
  (no new Main columns). Worked example: MikroTik CRS328-24P-4S+RM.
- **Fresh brands** (Extreme + 9 others + NVIDIA 800G-Eth) remain HELD on the §10 SOURCE MANIFEST
  (operator drops sources into `datasheets/cache/`).

**✅ SCHEMA SIGNED OFF + IMPLEMENTED + PROVEN (2026-06-14).** Operator approved with 4 amendments —
APPLIED (Attributgruppe `Switch` not `Switche`; attr #5 `Port-Geschwindigkeit`; attr #10 `Bauform`;
L3 env-first precedence + new **S.5**) + the Switch-Typ note. **Implemented across the core pipeline,
backward-compatible — 413 tests green:**
- `constants.py` SWITCH_ATTRIBUTES (15) + `attributes_for_category()`; `rules.yaml` L2 `Switches` /
  Attributgruppe `Switch` / 6 L3 tokens; `config.py` loads them. (commit `d9b719d`)
- `models.py` +13 switch intake fields; `reconcile.py` (ATTR_ALIAS / `_CANON_TO_FIELD` / map_attributes
  Formfaktor-optional / entry_to_intake skips physical_formfaktor / `_closer` "Originaler {brand}-Switch");
  `intake.py` build_record category dispatch; `assemble.py` Attributgruppe; `validate.py` category-aware
  Kat-L2/L3 + attr-set + `_check_switch_sku` with S.1-S.5. (commit `810f3f9`)
- **End-to-end proof:** CRS328-24P-4S+RM → L2 `Switches` / L3 `Managed Switch (L3)`, **gate PASS, 0
  violations.** Worked example in `SWITCHES_SCHEMA_PROPOSAL.md` §6.
**MikroTik switch enumeration harvested (40 slugs, mikrotik.com/products/group/switches):** CRS106/112/
304/305/309/310/312/317/318/320/326/328/354/418/504/510/518/520/804/812, CSS318/326/610, RB260GS/GSP,
netPower-16P / netPower-Lite-7R. Completeness pass must EXCLUDE non-switches: fiberbox+, gperx6,
netfiber-9 (media converters), netpower-lite-ups (UPS).
**⏸ MikroTik Switches — 1st switch brand on the new schema; authored + verified EXCEPT weights; HELD on weight-grounding.** Harvested the
switches grid (40) via `_scratch/harvest_mikrotik_switches.py`, excluded 4 non-switches
(fiberbox+/gperx6/netfiber-9 media converters, netpower-lite-ups UPS), authored 36 via
`_scratch/mikrotik_switch_author.py`. env-first L3: Managed(L3) 20 / Smart-Managed 7 / Industrie 3 /
Data-Center 6. Betriebstemperatur datasheet-verbatim; Switching-Kapazität+Durchsatz omitted (not
published per-page — flag-don't-fabricate). **Naming convention set:** batch=category=`MikroTik_Switches`
→ every file category-tagged (`Hexwaren_Condition_MikroTik_Switches.csv` etc.), ZIP
`output/Hexwaren_MikroTik_Switches_stage3_<commit>.zip` — no collision with the transceiver bundle.
**Standing convention for all switch brands.** `audit_semantic.py <Brand>_Switches` strips the suffix
for vendor resolution. MSRP captured (`config/market_prices/mikrotik_switch_msrp.yaml`); EUR deferred.
**Operator switch audit (`e3b43aa`) → fixes (commit `33e3e8d`):** the first emit (`e3b43aa`) passed the
format gate + S.1-S.5 but was NOT import-ready — the operator's grounding audit caught: **#2** combo
ports dropped on 4 SKUs (fixed PORT_KEYS + added **S.6** gate cross-check); **#3** access-speed read the
100M management port on 6 high-speed switches (fixed to dominant user-facing port); **#1** weights were
the optics placeholder on all 36 (added a **weight guard** — `Artikelgewicht` ≤ placeholder / < 0,30 kg
floor HARD-FAILS — back-applied to protect every future switch brand); **#4** doc S.5 reconciled + WiFi-6
variant differentiated. **Gate now isolates to weight only: 36 `Artikelgewicht` violations, 0 non-weight
(combo/access/S.1-S.6/B.1-B.8 all PASS); 413 tests.** **Residual blocker:** real switch weights are NOT
$0-reachable (verified across product/specs/manual pages + Confluence REST API; JS-rendered widget, no
browser binary) → flag-don't-fabricate → **HELD until a weight source lands (§10 WEIGHTS row).** Stale
defective ZIP `…_e3b43aa.zip` removed.
**Next switch brands** await their datasheets in `datasheets/cache/` (same §10 manifest gating).
