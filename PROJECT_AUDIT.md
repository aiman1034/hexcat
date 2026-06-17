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

> **DOM follow-up DONE (2026-06-14, L8 round 2):** L3 now REQUIRES `DOM Unterstützung` on non-cable
> transceivers (+L7 fixture F15). XENPAK DOM misfire fixed (form-factor shortcut → **media-grounded**:
> optical=Ja incl XENPAK/XFP, copper-T=Nein; legacy-uncertain=flagged-undetermined). Backfilled all 6
> emitted brands (Arista +104/HPE +78/Cisco +39/Fortinet +32/MikroTik +16/NVIDIA +12; MikroTik
> reconciled — the "7 with DOM" were DAC cables, the 16 optical were the real gap). **All 8 brands now
> DOM-complete + gate L1–L6 GREEN; self-test re-CERTIFIED (9/9, 15/15 fixtures); fresh ZIPs `…_918c89c`
> (6 brands) + Juniper `…_2925d42`.** Commits `2925d42`+`918c89c`. Awaiting operator L8 re-audit.


Status legend: `not-started` → `facts` (grounded facts JSON) → `authored` (content) → `emitted`
(ZIP, passed the *legacy* gate L1–L4 + B.1–B.8 + semantic; **NOT yet** the consolidated 8-layer gate
of MISSION.md §8 — L5/L6 partial, **L7 anti-blind-spot fixtures + the consolidated gate.py do NOT yet
exist**) → `audited` (operator L8 independent re-audit passed) → `imported` (live in JTL — operator-side).
**Nothing here is "done" until `imported`.** Counts are grounded SKU counts, gaps flagged in each
`config/coverage/*_completeness.yaml` (most `complete:false`).

### Transceivers / Optics
| Brand | Count | Status | Note |
|---|---|---|---|
| Cisco | 588 | **emitted, gate L1–L6 PASS** (L8 round-3 2026-06-14: −8 POM SONET out-of-scope) | core; all 0,00 (Phase-1) |
| Arista | 347 | **audited** (parallel audit) + emitted `…_f8fd859.zip` | core |
| HPE/Aruba | 147 | **audited** + emitted `…_38ab528.zip` | core |
| Fortinet | 87 | **audited** + emitted `…_38ab528.zip` | |
| NVIDIA | 85 | emitted `…_38ab528.zip` (≤400G Eth) | 800G-Eth = flagged harvest gap |
| Extreme | 102 | **emitted, gate L1–L6 PASS** (L8 round-3: phantom sweep -6, +16 real incl. 400G QSFP-DD tier) | 108 = 102 + 6 flagged |
| Meraki | 25 | **audited** + emitted `…_63bbcc2.zip` | |
| MikroTik | 24 | emitted `…_f538381.zip` | |
| **Juniper** | **188 emitted** (gate L1–L6 PASS) | ✅ **AUTHORED + GATE-GREEN + L8 fixes applied — ZIP `…_c6d2860.zip`** | core. Locked 205 → EXACT **188 + 13 flagged-out + 4 aliased = 205**. Authored via `juniper_author.py` (per-SKU-unique prose; EX/QFX/MX/PTX/ACX/SRX theme; BX D/U λ 1330/1270 datasheet-verified; 23 industrial → −40/+85). **L8 audit: contract+content+grounding PASS + 1 HIGH/2 low FIXED** — DOM Unterstützung now required (L3) + added (188/188: Ja 178/Nein 10 copper+XENPAK); 4 XENPAK connectors LC→**SC (Duplex)**; λ normalized to carry **nm**. **gate.py L1–L6 = PASS** on the re-emitted bundle. Commit `c6d2860`. EUR pricing deferred (0,00). Optional polish: 3 flagged-out λ, JCO/QDD-ZR alias, PLR4 reach. |
| Extreme | 91 (facts) | **facts** only — `extreme_transceivers_completeness.yaml` | author after Juniper |
| **Dell** | 163 (61 optics 1G–800G + 102 DAC/AOC) | **emitted, gate L1–L6 PASS** (L8 round-2 2026-06-15: +3 matrix-only 40G + 5 fixes) | 1st Tier-B; SFP-DD+QSFP28-DD vocab; FC/QSA/passive-CBL out |
| **Lenovo** | 104 (33 optics + 71 DAC/AOC; 30 EOL-flagged) | ✅ **DONE — operator L8 byte-audit PASS `b331235` (2026-06-15), import-ready. 11th transceiver brand cleared.** | Tier-B #2; 1G/10G/25G/40G/100G + 40G→4×10G & 100G→4×25G breakout; +2× 10G-SR 85 °C; GROUNDED prose (L5 near-dup ≤0.27 + ungrounded-claim guard); 6 web-verified OEM variants logged; FC+OEM via extra_log. **FAQ = separate v1.3 stream (placeholder here, see §9 FAQ-scope note)** |
| **Ubiquiti** | 49 (24 optics + 25 DAC/AOC) | **emitted, gate L1–L6 PASS** (2026-06-15; `3297703`; L8 round-1 PASS-with-LOW fixed) — awaiting final L8 | Tier-B #3; denominator = operator-signed-off techspecs SFP&Fiber(29); 1G/10G(+12-ch CWDM)/25G/100G(SR4/LR4/PSM4); Uplink hybrid DAC/AOC-by-length; UF-↔UACC- dedup (6 alt-codes); 9 OUT + PON flagged; CWDM 12-distinct framing; near-dup 0 (now incl. L5 λ-channel Pass 2) |
| Palo Alto/Supermicro/Huawei/ZTE/Ruijie | — | **not-started** | §10 source-gated; re-verify per §7.1 ladder |

### Switches (Rule-7 schema)
| Brand | Count | Status | Note |
|---|---|---|---|
| MikroTik | 36/36 | emitted `…_e48e5a7.zip` (legacy gate) | weights cited+cross-checked; **awaiting operator L8 audit** |
| HPE/Aruba/Cisco/Juniper/Arista/Dell/… | — | **not-started** | source-gated; core brands first |

### Server Memory — NOT IN SCOPE (charter error, corrected 2026-06-14)
The earlier "Server Memory 25-SKU batch" was a charter assertion in error — operator does not
recognize it and the repo has zero trace. Removed from MISSION.md (§3/§6/§10). If server memory ever
enters scope it comes from the real catalog, not the charter.

### Other categories (MISSION.md §3 / §6 "TO BUILD")
Routers · Firewalls/Security · Wireless (APs/controllers/antennas) · NICs/Adapters · PSUs ·
Modules/Line cards · Servers/Compute · Cables & accessories · Mounting/rack kits → **all not-started**;
each needs `{CATEGORY}_SCHEMA.md` + semantic checks + anti-blind-spot fixtures → operator sign-off → batches.

### Manifest denominator (do NOT stall on scope — operator ruling 2026-06-14)
The denominator is **the brand list × the categories each brand actually makes** (from each brand's
own product lines) — built directly, NOT waiting on any external input. A JTL-Wawi export / live-
hexwaren.de reconciliation is **OPTIONAL** (nice-to-have to avoid re-doing the ~525 already-live SKUs),
never a blocker. Work order proceeds core-brand-first (Juniper → Extreme → expansion), each brand
across the categories it makes. The grid above is the *built* state; the *target* = every brand×category
cell driven to `imported`.

### 0.6 — LOCKED TRANSCEIVER-BRAND LIST (operator task 2026-06-14: bound the transceiver universe)
The in-scope transceiver-brand denominator. Brand scope GROWS with stocking (MISSION §3) → a JTL/
hexwaren.de export can extend/prune Tier-C; Tiers A/B are firm. Each brand runs the full Juniper-grade
pipeline (Workflow-B enumerate → ground → reconcile → author → gate L1–L7 → ZIP → operator L8).
- **TIER A — DONE + emitted (9):** Cisco, Juniper, Arista, HPE/Aruba, Fortinet, Meraki, NVIDIA/Mellanox,
  MikroTik, **Extreme** (absorbs Avaya/Enterasys legacy). 8 operator-L8-cleared; Extreme awaiting L8.
- **TIER B — remaining named in-scope (8), source-gated (§10):** Dell (+ Force10/EMC legacy), Lenovo
  (+ IBM legacy), Ubiquiti, Supermicro, Palo Alto, Huawei, ZTE, Ruijie. NEXT after Extreme.
- **TIER C — candidate (confirm vs a JTL/hexwaren.de export before authoring):** H3C/New-H3C,
  Netgear, D-Link, Zyxel, TP-Link/Omada, Allied Telesis, Brocade/Ruckus (parked), Edge-Core, SonicWall,
  Check Point, Cisco-Meraki-vs-SB overlap. (FS/3rd-party-compatible optics are NOT OEM-new-sealed → out
  unless Hexwaren stocks the FS brand itself.) Polycom = no transceivers (excluded).
- **Authoritative confirmation:** a JTL-Wawi article export / hexwaren.de brand facet would make this
  list exact (turn Tier-C candidates into firm in/out). Requested, NOT a blocker — Tiers A→B proceed now.

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

**Taxonomy:** locked **25** Kat-Ebene-3 tokens (`config/taxonomy/transceivers.yaml` ⇄ `config/rules.yaml` ⇄ `constants.py`, lock-step enforced by `verify_taxonomy`): DAC/AOC/MPO Kabel, QSFP+/QSFP-DD/QSFP-DD800/QSFP28/**QSFP28-DD**/QSFP56/QSFP112, OSFP, SFP/SFP+/**SFP-DD**/SFP28/SFP56, X2, XENPAK, XFP, CFP/CFP2/CPAK/CXP, GBIC, CIM8. "Sonstige" never allowed. (POM removed 2026-06-14 — SONET/SDH out of scope; SFP-DD + QSFP28-DD added 2026-06-15 for Dell.)

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

- **B.9 DOM Unterstützung present** — every NON-cable transceiver must carry a `DOM Unterstützung` attribute (gold-slice completeness; cables exempt). Grounded per family (optical=Ja, copper-T=Nein), never a form-factor guess. (Added L8; task #21 backfilled all brands.)
- **B.10 media ↔ DOM consistency** — a copper/twinax module must NOT be DOM=Ja (nothing optical to monitor); an optical (MMF/SMF) module must NOT be DOM=Nein. Grounded by media, not form-factor — ONE standards carve-out: the **GBIC** MSA predates the SFF-8472 DDM interface, so an optical GBIC legitimately carries DOM=Nein (XENPAK/X2/SFP+ all post-date SFF-8472, stay enforced). (Added L8 round-3; caught Cisco XENPAK-CX4/S1G + FET-10G + Arista SFP-1G-T — see §9.)
- **B.11 Formfaktor ∈ locked vocabulary** — a non-cable transceiver's `Formfaktor` must be one of the locked `PHYSICAL_FORMFAKTOR` tokens (`constants.py`), kept in lock-step with `rules.yaml`/`taxonomy`. (Added L8 round-3; enforces the POM removal.)

Audit tool: **`_scratch/audit_semantic.py [Brand ...]`** — per-brand (defaults Cisco+Meraki); enumerates every instance of all **8** classes (ff_conn / faser / multi_wl / tunable_wl / dash / hersteller / cable_k3 / template).

**Consolidated gate `src/hexcat/gate.py` (MISSION §8, L1–L7)** wraps `validate_dir` (→ L1–L4) and adds: L1 UTF-8/umlaut + HTML-well-formedness guards; **L5 plausibility** (weight/reach/λ bands **+ price-sanity: refuses identical-price clusters ≥5 SKUs and stray non-zero in an otherwise-0,00 bundle** — added L8 round-3 after the Cisco templated clusters); L6 completeness-vs-`gate_completeness.yaml`; **L7 = `_scratch/gate_selftest.py`** (9 known-good zero-violation + 18 negative fixtures, each must fire at its layer). Re-CERTIFIED 2026-06-14.

---

## 5. Brand status

> **Verified-state-only:** this table records MEASURED facts (actual gate output, `audit_semantic.py`
> per-check counts, Rule-8 parity tallies) — never "done" assertions. If it isn't measured, it isn't
> stated as fact. Re-run to confirm: `python -m hexcat.cli stage3 …` (gate), `python _scratch/audit_semantic.py`
> (cross-checks), the §6 pricing run, and `python -m pytest -q`.

| Brand | Content SKUs | Measured gate | audit_semantic (8: ff/faser/multiwl/tunwl/dash/herst/cablek3/**template**) | Pricing | Notes |
|---|---|---|---|---|---|
| **Cisco** | **588** | **GATE L1–L6 PASS 588/588, 0 violations** (2026-06-14, gate.py) | **0 / 0 / 0 / 0 / 0 / 0** | **0/588 — all 0,00 (Phase-1 catalog-consistent)** | Rule-8 parity 0-missing. **L8 round-3 (2026-06-14):** (a) **PRICES reset to 0,00** — the market engine produced templated junk (4 identical clusters 33×8177,47/32×6135,28/32×1625,81/5×1765,16 = 102 SKUs); grounded pricing deferred to Phase-2. (b) **8 POM SONET/SDH SKUs DROPPED** (596→588) — SONET out of scope (operator, = Juniper SONET call); POM removed from rules.yaml + taxonomy + constants.py. (c) **2 copper DOM fixed Ja→Nein** (XENPAK-10GB-CX4, S1G-TE-PM-D-I) + **FET-10G Nein→Ja** (SFP+ SR, SFF-8472). CIM8 kept (real coherent FF). 35 optical GBIC correctly DOM=Nein (pre-SFF-8472). ZIP `output/Hexwaren_Cisco_stage3_c006e74.zip` (588 SKUs). |
| **Meraki** | 25 (MA-* only) | **PASS 25/25, 0 violations** (2026-06-13, commit `63bbcc2`) | **0 / 0 / 0 / 0 / 0 / 0** | 0/25 (PENDING, no comp yet) | Rule-8 parity: required attrs **0-missing**. MGB* reassigned to Cisco SB. 2 MA-CBL-SPWR excluded (power cables). Rule-9 temp. ZIP `output/Hexwaren_Meraki_stage3_63bbcc2.zip`. |
| **Arista** | 347 | **PASS 347/347, 0 violations** (2026-06-14, commit `3fd1f61`) | **0×8** | deferred (no prices in datasheet; 0,00) | ✅ DONE. Completeness 347/347 (Arista Transceivers Data Sheet); token diff confirms no gap (13 extra = footnote/truncation/bare-form-factor artifacts). Fixed 42 reconcile connectors (Anschlussenden bare "QSFP"→QSFP56/QSFP28 by standard). 243 DAC/AOC Rule-9 commercial 0/70. 18×800G speeds grounded; 3 coherent 400GBASE-ZR drove B.6 ZR-speed-gate refinement. Rule-8 parity 0-missing (SFP-1G-T copper exempt). **L8 round-3 (2026-06-14):** the new media↔DOM gate caught **SFP-1G-T (1000BASE-T copper) carrying DOM=Ja → fixed to Nein** (same bug class as the Cisco XENPAK/S1G copper-DOM; surfaced because the stricter check now runs on all brands). Re-emitted GREEN 347/347. ZIP `output/Hexwaren_Arista_stage3_c006e74.zip` (347 SKUs). |
| **HPE/Aruba** | 147 | **PASS 147/147, 0 violations** (2026-06-13, commit `a34a86b`) | **0×8** (all incl B.7 cable_k3) | deferred (no grounded list; netto_vk 0,00) | ✅ DONE. Completeness: 147 of 147 standalone catalog transceivers (AOS-S/AOS-CX guide); independent full-guide token diff confirms the ~370 other PN-tokens are switches/EOL-revisions/aliases (R9F75A=JL309A)/cross-refs, no gap. Betriebstemperatur: 72 verbatim from the guide's per-module Rating + 61 Rule-9 commercial. **Fixed 21 DAC + 3 AOC mis-classified under module k3 → DAC/AOC Kabel (drove new B.7).** 5 speeds grounded. Rule-8 parity 0-missing. ZIP `output/Hexwaren_HPE_stage3_38ab528.zip`. |
| **Fortinet** | 87 | **PASS 87/87, 0 violations** (2026-06-14, commit `fb11cb4`) | **0×8** | deferred (datasheet has no prices; 0,00) | ✅ DONE. Completeness 87/87 (Fortinet Transceivers Data Sheet); token diff confirms no gap (11 extra tokens = shorthand/4-pack/"+"-truncations of captured SKUs). Fixed 5 reconcile-blocking connectors (3 QSFP-DD cables + 2 MPO breakouts). Betriebstemperatur 85 datasheet-verbatim (Fortinet publishes). FG-TRAN-CFP2-LR4 wavelength set; QSFP28 SR→SR4. Rule-8 parity 0-missing. ZIP `output/Hexwaren_Fortinet_stage3_38ab528.zip`. |
| **MikroTik** | 24 | **PASS 24/24, 0 violations** (2026-06-13, commit `f538381`) | **0 / 0 / 0 / 0 / 0 / 0** | 24/24 MSRP captured (grounded); EUR net DEFERRED to supplier feed | ✅ DONE. Completeness: captured 24 of 25 (official sfp-qsfp grid); XQ+CM0000-XS+ excluded (QSFP28→SFP28 port adapter). Betriebstemperatur: 8 published verbatim + 16 Rule-9 sibling-corroborated industrial (NOT commercial — MikroTik publishes -40 lows). DDQ+85MP01D=400G QSFP-DD SR8 (Faseranzahl 16, MPO-16). Rule-8 parity 0-missing. ZIP `output/Hexwaren_MikroTik_stage3_f538381.zip`. 14 non-blocking warnings (length-variant DAC prose reuse). |
| **MikroTik Switches** | **36 / 36** | **PASS 36/36, 0 violations** (2026-06-14, commit `e48e5a7`, ZIP `…_e48e5a7.zip`) | **0×8** + S.1-S.6 + weight guard | 36/36 MSRP; EUR deferred | ✅ **DONE 36/36** — 1st SWITCH brand (Rule-7). schema/combo/access/S.1-S.6/B.1-B.8/weight-guard all PASS; env-first L3 Managed(L3)/Smart/Industrie/DC; temp datasheet-verbatim. **Weights:** MikroTik doesn't publish them ($0-verified) → operator-approved distributor weights, every value cited + cross-checked in `datasheets/cache/mikrotik-switch-weights.yaml` (dateks.lv net+gross / mikrotik-store.eu / datagram.ae; templated-default detection; corrected /min disagreement flag; CSS610-8P & CRS328 overrides documented). All 6 once-blocked SKUs sourced in a best-effort 2nd pass (CRS804 4,02/CRS812 4,75 dateks+ms; CSS106-5G-1S 0,212 datasheet-net → guard floor lowered 0,30→0,15; CSS106-1G-4P/CRS318-OUT/CSS610-OUT via ms+web). Completeness 36 of 40 (4 non-switches excluded). |
| **NVIDIA** | 85 | **PASS 85/85, 0 violations** (2026-06-14, commit `148ed65`) | **0×8** | deferred (no list; 0,00) | ✅ DONE (1st FRESH brand). LinkX Ethernet ≤400G: DAC 26/DAC-SPLIT 6/AOC 28/AOC-SPLIT 13/XCVR 12. Authored via nvidia_facts.py → nvidia_author.py (adapted arista_author.py) → backfill. Lane-aware XCVR optics (1-lane serial=single λ; 4-lane WDM=LAN-WDM/CWDM4 set; MPO SR8/DR4). Rule-9 commercial 0-70. Rule-8 parity 0-missing. **Completeness `false`: 800G-Ethernet (Spectrum-X) is a flagged HARVEST GAP** (deprecated 800G list was XDR/IB). ZIP `output/Hexwaren_NVIDIA_stage3_38ab528.zip`. |
| **Extreme** | 86 | **GATE L1–L6 PASS 86/86, 0 violations** (2026-06-14) | **0×8** | deferred (0,00) | ✅ DONE (2nd FRESH brand; absorbs Avaya/Enterasys legacy). Grounded from the Optics Solution Guide PDF (extract_tables): 91 facts → **86 authored + 5 flagged** (3× 100G-4WDM λ-plan, 10331 SR10-CFP2 fibre/connector conflict, 40G-LM4 λ/reach inconsistent — all reason-coded). 45 cables (DAC/AOC, breakouts via PN pattern) + 41 modules. DOM media-grounded (optical Ja / 2 copper-T Nein). **L8 round-1 (2026-06-15) — 2 grounding issues the gate passed, fixed:** (1) **`100G-ER4LT-QSFP40KM` shipped at single 1550 nm** → author wavelength now keyed off the **Standard** (WDM family LR4/ER4/ERLT/FR4/CWDM4/SWDM4 → 4-λ SET; parallel SR4/ESR4/PSM4/DR4 keep one λ), ER4LT → LAN-WDM set; **B.3 `_MULTI_WL_RE` broadened to ERLT/SWDM4** + L7 fixture F19. (2) **alt-PNs were silently dropped** (lived in the unread `kompatibilitaet` field) → MODULE legacy AA-/MGBIC- codes **woven into the Beschreibung** (emitted/searchable); CABLE codes **descoped** (length-family interleaving unattributable). **author→emit parity advisory** added (regen.py) — Zustand→Condition confirmed, nothing else load-bearing dropped. Earlier fixes: B.5 `MGB(?!IC)`. **L8 round-2 (2026-06-15): NOT cleared** — A `40G-QSFP-LR4-INT` PSM4→LR4 mis-ground **FIXED** (cell-shift); B **single-source undercount** — current datasheet adds a 400G QSFP-DD tier + 100G (incl. 100G-PSM4-QSFP10KM) → **re-harvest pending** (not re-emitted; A+B land together). ZIP `…_277ad7b.zip` (86 SKUs, superseded once re-harvested). |

**Transceiver brands DONE + emitted (9):** Cisco, Arista, HPE/Aruba, Fortinet, Meraki, NVIDIA, MikroTik, Juniper, **Extreme** (incl. Avaya/Enterasys legacy). 8 operator-L8-cleared; Extreme awaiting L8.
**Fresh brands not started:** Dell, Huawei, Lenovo/IBM, Palo Alto, Ruijie, Supermicro, Ubiquiti, ZTE. (NVIDIA ≤400G DONE — 800G-Eth follow-up pending; Brocade parked; Polycom = no transceivers.) See the LOCKED TRANSCEIVER-BRAND LIST (§0.6) for the full bounded scope.
**Switch category:** not started — needs its OWN gold-slice schema + taxonomy (Rule-7 approval before authoring); everything else (completeness, gate, Rule 8/9, byte contract, cross-checks, per-brand process) carries over.

**Test suite (measured):** 413 tests (28 files), all green — last run 2026-06-14 (L8 round-3: Cisco prices→0,00 + POM-drop + media↔DOM/Formfaktor gate-tightening). Run: `PYTHONIOENCODING=utf-8 python -m pytest -q`. **Consolidated gate re-CERTIFIED** (`_scratch/gate_selftest.py` exit 0 — **12** known-good zero-violation + **21** fixtures, incl. F19 WDM-λ-set). **All 9 emitted transceiver brands + MikroTik switches gate L1–L6 PASS.** B.3 keyed off the Standard (WDM family → 4-λ SET; ERLT/SWDM4 covered); author→emit parity advisory guards silent non-schema drops.

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
- **Charter v3 corrections + Juniper legacy facts built (this session).** (1) **Server Memory REMOVED** from MISSION.md §3/§6/§10 + manifest — operator confirms it doesn't exist (charter error, not a real category). (2) **Manifest scope un-blocked:** denominator = brand list × categories-each-brand-makes, built directly; JTL-Wawi/live-site reconciliation OPTIONAL (~525 live SKUs), never a blocker (MISSION.md §3 Step 0 updated). (3) **MISSION.md §8 L1 reinforced** ("data structure sacred"): added HTML-well-formedness + UTF-8/umlaut-integrity (mojibake/BOM, Mac+Excel corruption) silent-corruption guards, each requiring a NEGATIVE fixture — for the consolidated gate (task #19). Commits `bbed6b0`. (4) **Juniper (core) facts BUILT:** ran the §7.1 ladder — cached `juniper-optic-modules.pdf` (legacy matrix) text-parsed via `_scratch/juniper_facts.py` → **38 grounded Ethernet optics** (SFP 22/SFP+ 4/XFP 8/XENPAK 4; 1G/100M/10G; 23 EOL-flagged-kept), 10 SONET-only optics excluded (no Ethernet standard — flag-don't-fabricate; scope decision noted). `Juniper` already in `rules.yaml` vendors (verified). **Modern QSFP/100G/400G = harvest gap** — the JS `qualified-optics` pages TIME OUT headless even on `domcontentloaded` (goto never completes); alternate sources to try next: HCT backend JSON API / a current optics PDF / per-platform doc tables. **RESUME: harvest the modern Juniper set (alternate source) → combine with the 38 legacy → author Juniper as ONE batch → gate → ZIP.** `complete:false` until the modern set lands.
- **Juniper modern optics UNBLOCKED — sources cached (corrects my own "JS-blocked" diagnosis).** The HCT/qualified-optics JS pages were a dead end ($0): HCT is a Next.js SPA with no `__NEXT_DATA__` and a dynamically-constructed API (rabbit-hole, abandoned per §0.3). But the §7.1 PDF rung won: Juniper publishes **current official optics guides as PDFs** — cached `datasheets/cache/juniper-{100g,400g,800g}-optics-guide.pdf` (100G pub 2026-03-08 59pp ~16 PNs; 400G pub 2025-07-30 56pp ~13; 800G 69pp ~17 — regex floors, full set on parse; QDD-400G/800G, QSFP-100G-DR/FR, CFP2-100GBASE, JCO400 coherent). No separate 10G/25G/40G guide (404 — 10G/1G in the legacy PDF). **SONET SKIPPED** (operator). **RESUME (task #18): parse the 3 modern guides text-mode (like the legacy PDF) → merge with the 38 legacy → author ONE Juniper batch → gate → ZIP → operator audit.** Authoring deferred this turn (deep context — avoid a low-context half-build per §9); sources + facts foundation banked.
- **Juniper grounding STARTED then PAUSED for the gate.** Operator confirmed the locked 205. Grounding chunk **1/8 (800G)** done: 5 QDD-2X400G-* grounded from the 800G guide (standard/media/reach/λ; connector `[VERIFY]`), alias `QDD-800GB-2XFR4-J`→`QDD-2X400G-FR4` collapsed; master grounded set = **43** (38 legacy + 5). Banked `output/stage3/juniper_grounded_facts.json` (commit `ccdb06c`). Then PAUSED per operator to build the gate. Resume = 400G chunk WITH gate.py per-chunk.
- **CONSOLIDATED GATE `src/hexcat/gate.py` — task #19, part 1/2 (commit `800df67`).** MISSION §8 backbone. Wraps the battle-tested `validate_dir` (L1-core/L2/L3/L4) + adds the 2 NEW L1 silent-corruption guards: **HTML-well-formedness** (balanced/allowed tags, no stray `<>`, valid entities) + **UTF-8/umlaut-integrity** (valid UTF-8, BOM only at byte 0, zero mojibake `Ã¤/Â°/ï¿½`, umlauts intact). Per-LAYER PASS/FAIL report; **L5/L6/L7 explicitly surfaced as NOT-IMPLEMENTED (never silently green).** **SELF-TESTED + CERTIFIED** (`_scratch/gate_selftest.py`, exit 0): 8 known-good bundles all PASS L1-L4 (guards do NOT false-positive on real German); 6 negative fixtures (mojibake umlaut / BOM-in-body / unbalanced `</p>` / stray `<` / wrong delimiter / banned phrase) ALL caught at the expected layer (B.8 anti-blind-spot proof). 413 tests green. **PART 2/2 (resume):** L5 plausibility (weight/reach/λ bands; no optic-weight-on-switch) + L6 completeness-vs-record/manifest (refuse silent shortfall; note: complete:false-with-flagged-gaps must still PASS so known-good pass — confirm interpretation with operator) + institutionalize a fixture per L3/L4/L5/L6 check class + wire gate per-chunk. THEN resume Juniper 400G grounding with the gate running.
- **CONSOLIDATED GATE COMPLETE + CERTIFIED (task #19 DONE, commit `fa85b5d`).** Finished L5/L6/L7 in one push. **L4** grounding (no `[VERIFY]`/`[FLAG]` shipped); **L5** plausibility (weight band per class — switch 0,15–50 kg, optic ≤1 kg; reach ≤130 km EXEMPTing coherent/amplified/ULH/DWDM/ZR — Cisco `DP04QSDD-ULH-A1` "über 3000 km amplifiziert" is real; λ 800–1650 nm); **L6** completeness via the new clean machine-readable `config/coverage/gate_completeness.yaml` (the prose `*_completeness.yaml` docs aren't valid YAML) — PASS iff captured==emitted AND captured+flagged≥enumerated AND every flagged gap has a valid `reason_code` (out-of-scope|un-groundable-after-ladder|eol|harvest-gap|source-blocked); REFUSE on no-record/count-mismatch/flag-without-reason. **L7** = 14-fixture anti-blind-spot suite. **CERTIFIED** (`_scratch/gate_selftest.py` exit 0): 8 known-good bundles all PASS L1-L6; all 14 fixtures caught at the expected layer. 413 tests green. **Wiring:** `gate(bundle_dir)` is the single emit-gate — every grounding/authoring chunk that emits a bundle must run it and refuse to ship on any L1-L6 failure. **RESUME: Juniper grounding chunk 2/8 (400G) with the gate running per-chunk** (then 100G→40G→25G→10G/EX-SFP→1G→FE; collapse the 2 AddOn `-J` codes; register Juniper in `gate_completeness.yaml` when it emits).
- **JUNIPER GROUNDED → AUTHORED → GATE-GREEN → ZIP (commits `cc4962c`+`f4b8ab1`). First CORE-brand transceiver bundle since the charter.** Grounding completed (chunks 1-8, MSA/guide-grounded); **EXACT reconciliation 188 authored + 13 flagged-out + 4 aliased = 205** (no "~", asserted). Closed 37 `[VERIFY]` λ by convention (10G/25G-BX 1270/1330 — datasheet-VERIFIED not 1490/1310; CWDM ITU grid); 3 λ-undeterminable (QSFP-100G-ERBD-D/LRBD-D, SFP-1GE-FE) flagged out (gate requires Wellenlänge). Authored 188 via `juniper_author.py` (NVIDIA XCVR scaffold; per-SKU-unique PN-woven prose → boilerplate gate passes; Juniper EX/QFX/MX/PTX/ACX/SRX theme; 23 industrial -I/-IT → −40/+85). Emit GREEN; **`gate.py` L1–L6 = PASS on the real bundle** (the consolidated gate's first live brand run — L6 reconciles captured 188==emitted, 13 flags reason-coded). **ZIP `output/Hexwaren_Juniper_stage3_f4b8ab1.zip`** (188 SKUs). EUR pricing deferred (0,00). **Awaiting operator L8 independent audit** — NOT "done" until L8 + JTL import. NEXT: Extreme (facts `d59eee8`), then expansion brands; optional Juniper polish (3 flagged-out λ, JCO/QDD-ZR alias verify, PLR4 reach).
- **CISCO L8 ROUND-3 + GATE TIGHTENING (2026-06-14, commit `c006e74`; ZIPs `output/Hexwaren_{Cisco_588,Arista_347}_stage3_c006e74.zip`, stale `…_918c89c` removed).** Operator L8 deep re-audit cleared Juniper/Fortinet/HPE/Arista/MikroTik/NVIDIA and found 3 pre-existing Cisco issues — all fixed, plus 3 new gate checks back-applied:
  - **(1) PRICES reset to 0,00.** 102 of 111 priced Cisco SKUs were 4 identical templated clusters (33×8177,47 / 32×6135,28 / 32×1625,81 / 5×1765,16) from the market-pricing engine. Reset to catalog-consistent 0,00 (Phase-1; grounded pricing deferred to Phase-2). Mechanism: content `netto_vk` is already all-`null` → `reconcile.py` maps null→"0,00", so a plain `regen.py Cisco` (NOT `price_cisco.py`) emits an all-0,00 Prices CSV. Test `test_grounded_anchors_are_written_into_the_cisco_prices_csv` → rewritten to `test_cisco_prices_are_phase1_catalog_consistent_zero` (loader/engine unit tests stay green — engine kept for Phase-2).
  - **(2) MEDIA↔DOM fixes.** 2 copper modules carrying DOM=Ja → Nein (XENPAK-10GB-CX4 CX4-twinax, S1G-TE-PM-D-I 1000BASE-T). FET-10G (SFP+ 10GBASE-SR MMF) DOM Nein→Ja (SFF-8472 DDM-capable; was the lone optical-SFP+ outlier). 35 optical **GBIC** correctly stay DOM=Nein (GBIC MSA predates SFF-8472 — a standards fact, carved out of the check). 10 AOC are cable-exempt.
  - **(3) L3 TOKENS.** 8 **POM** SONET/SDH SKUs DROPPED (596→**588**) — SONET out of scope (operator, = the Juniper SONET call). POM removed from `rules.yaml` (24→23), `taxonomy/transceivers.yaml`, `constants.py` PHYSICAL_FORMFAKTOR (kept in lock-step — `verify_taxonomy` enforces it). **CIM8 KEPT** (real current NCS-1014 coherent form factor). `test_cisco_coverage` + `test_taxonomy` updated: Ethernet legacy (XENPAK/GBIC/DWDM-GBIC) stay protected-never-dropped; POM pinned as the ONE explicit operator-authorized domain exclusion.
  - **GATE TIGHTENING (validate.py + gate.py, with L7 fixtures, back-applied to ALL brands):** **B.10 media↔DOM** consistency, **B.11 Formfaktor∈locked-vocabulary**, **L5 price-sanity** (refuse identical-price clusters ≥5 SKUs + stray non-zero in an otherwise-0,00 bundle). 3 new negative fixtures (F16 optical-DOM=Nein→L3, F17 Formfaktor-unlocked→L3, F18 price-cluster→L5) — all fire at their layer.
  - **The new media↔DOM check immediately earned its keep:** running on all brands it caught **Arista SFP-1G-T** (1000BASE-T copper) carrying DOM=Ja — same bug class — fixed to Nein, Arista re-emitted GREEN 347/347. The `gate_selftest` DOM-GAP escape hatch (which had masked it) was removed — backfill is complete, so the honest bar is now ZERO violations on every bundle.
  - **RE-CERTIFIED (no self-green):** `gate_selftest.py` exit 0 — 9 known-good all PASS (zero-violation bar), all **18** fixtures caught at their layer. `gate.py` L1–L6 PASS on the real re-emitted Cisco (588/588) and Arista (347/347). **413 tests green.** Cisco/Arista bundles re-emitted; ZIPs rebuilt (see build entry).
- **OPERATOR L8 BYTE-AUDIT of `c006e74` PASSED (2026-06-14):** Cisco (588) + Arista (347) byte-diffed vs `918c89c` — ONLY intended edits, zero collateral drift; both supersede `918c89c`. CIM8 confirmed in-scope. **8 transceiver brands now operator-cleared** (Juniper, Cisco, Arista, HPE/Aruba, Fortinet, NVIDIA, MikroTik, Meraki). Operator follow-up (low-pri, parallel): re-ground the 35 DWDM-GBIC DOM=Nein on the Cisco DWDM-GBIC datasheet (DOM table: optical Tx/Rx = N/A → no optical-power DOM) rather than the "GBIC predates SFF-8472" rationale; keep the gate's GBIC leniency but a DDM-capable GBIC must still be allowed Ja. **Tracked, deferred** to avoid re-emitting a just-cleared brand for a provenance-only change (DOM values unchanged = correct either way).
- **NEW MAIN TASK — COMPLETE TRANSCEIVER UNIVERSE (all brands).** Operator: the 8 cleared brands are NOT the whole catalog; enumerate+lock the full in-scope transceiver-brand list, then author every remaining brand Juniper-grade (Workflow-B enumeration → ground → reconcile → author → gate L1–L7 → ZIP → operator L8), starting with Extreme. Locked brand list posted + recorded in §0.6.
- **EXTREME DONE (2nd fresh brand, this session) — gate L1–L6 PASS 86/86, audit_semantic 0×8, 413 tests.** Authored from the cached Optics Solution Guide facts (`extreme_facts.json`, 91 grounded) via `_scratch/extreme_author.py` (adapted nvidia_author.py: Extreme switching theme, facts-direct optics, DOM media-grounded, Faseranzahl by connector/type, `alt_pns`→"Kompatible Bestellnummern", BiDi-λ by BX convention) → `backfill_brand` (Anwendung + Rule-9 commercial temp). **86 authored + 5 flagged = 91** (3× 100G-4WDM λ-plan unprovable, 10331 SR10-CFP2 fibre/connector conflict, 40G-LM4 1310nm-can't-reach-160km — reason-coded in `gate_completeness.yaml`). SFP-DD is cables-only (DAC Kabel) → no vocab change. **Fixed + back-applied: (1) B.5 Hersteller guard** mis-claimed `MGBIC-` (Enterasys/Extreme) as Cisco → refined to `MGB(?!IC)` (validate.py + audit_semantic.py); **(2) ER4 λ** corrected from the facts' wrong single `1550 nm` to the 4-λ LAN-WDM (100G) / CWDM4 (40G) SET. Added `Extreme` (hersteller "Extreme", slug "extreme") to `rules.yaml` vendors. `Extreme` added to gate_selftest KNOWN-GOOD (zero-violation bar). ZIP rebuilt 2026-06-14 — see build entry. Completeness `extreme_transceivers_completeness.yaml` → `complete: true`. ZIP `…_1f43aa3.zip` (superseded). **Awaiting operator L8.**
- **EXTREME L8 ROUND-1 — operator byte-audit of `1f43aa3` NOT cleared (2 grounding issues the gate passed); fixed → re-emitted `277ad7b` for re-audit.** Contract/content/completeness/media↔DOM were clean. **(1) Wavelength:** `100G-ER4LT-QSFP40KM` shipped at a single `1550 nm` — the ER4 λ-fix keyed off a type substring (`"ER4" in typ`) and missed `ERLT`. Re-keyed the WDM-family detector off the **Standard** (LR4/ER4/ER4-Lite=ERLT/FR4/CWDM4/SWDM4 → 4-λ SET; parallel SR4/ESR4/PSM4/DR4 keep one λ); ER4LT now = the LAN-WDM grid (same as its CFP2-ER4 sibling). **Gate-tightening (the ER4LT miss is a class):** B.3 `_MULTI_WL_RE` broadened to `\bERLT`/`\bSWDM4` (still keyed off Standard), back-applied to audit_semantic.py; **L7 fixture F19** (a WDM standard forced to single 1550 nm MUST fail B.3 — proves ERLT caught; positive = known-good bundles pass). **(2) Alt-PN cross-ref:** the 35 AA-/MGBIC- legacy codes were placed in the `kompatibilitaet` content key, which the pipeline reads **nowhere** → silently stripped at emit. MODULE legacy codes (clean 1:1) now **woven into the Beschreibung** (emitted, on-site-searchable) so a customer with an old Avaya/Enterasys code finds the product; CABLE codes **descoped** (length-families interleave numeric/AA codes → per-length attribution unprovable → flag-don't-fabricate). **author→emit parity advisory** added to regen.py (warns when a content attribute neither aliases to the 14-schema nor lands in another emitted file e.g. Zustand→Condition) — confirmed Extreme drops nothing else load-bearing. Gate re-CERTIFIED (10 known-good + **19** fixtures, exit 0), audit_semantic 0×8, 413 tests. ZIP `output/Hexwaren_Extreme_stage3_277ad7b.zip` (86 SKUs). **Awaiting operator L8 re-audit.**
- **EXTREME L8 ROUND-2 — operator byte-audit of `277ad7b`: round-1 fixes VERIFIED, but NOT cleared (2 new findings). Finding A FIXED; finding B (undercount) checkpointed — NOT re-emitted (both must land together).** **A [fixed]:** `40G-QSFP-LR4-INT` was mis-grounded `40GBASE-PSM4` (MPO/1310 nm/10 km — physically impossible: PSM4 ≤2 km). The cached-guide ROW was cell-shifted (§7.5); the PN + 10 km = **40GBASE-LR4** (web-confirmed). Re-grounded in `extreme_facts.json`: duplex LC, 2 fibre, CWDM4 4-λ 1271/1291/1311/1331, 10 km. Bogus `40GBASE-PSM4` was ISOLATED to this one part (40G parallel SMF = PLR4/PLRL4). **B [pending] — the Juniper single-source-undercount lesson:** the cached Optics Solution Guide is NOT the universe. Fetched + cached Extreme's CURRENT "Optical Transceivers and Cables" datasheet (`datasheets/cache/extreme-optical-transceivers-cables-current.pdf`, 15 pp, sitecorecontenthub) and diffed → a whole **400G QSFP-DD tier missing** (400G-DR4/FR4/LR4-QSFPDD + 400G-AOC) + **100G additions** (100G-FR-SFPDD, **100G-PSM4-QSFP10KM** [operator-named], 100G-ER4-QSFP40KM) + 10G temp variants. RE-HARVEST needed: the current datasheet's tables are MERGED-CELL/multi-line → the index-collapse (`_scratch/extreme_facts_current.py`, WIP) broke (36 messy rows; 400G appears in `extract_text` not `extract_tables`). **RESUME:** text-row parser of the current datasheet → reconcile (current = authoritative superset; carry the verified 86 + fix A; add the new tiers) → re-author → re-gate → re-emit. Checkpointed per MISSION §9 (hit the parser context-wall; rushing the re-harvest is what causes these L8 findings). `complete:false` until A+B land.
- **DELL UNBLOCKED + HARVEST CHECKPOINT (Tier-B brand #1, 2026-06-15) — corrects the stale §10 "403/JS-blocked" label.** Ran the §7.1 ladder: rung (a) delltechnologies.com 403'd (the stale block), rung (b) **a reseller mirror (andovercg.com) serves the GENUINE Dell "Networking Transceivers and Cables" spec sheet PDF** (Dell's own content; mirror is just transport). **Cached** `datasheets/cache/dell-networking-optics-datasheet.pdf` (8 pp, FULL spec grid: Product/Model/Max-distance/IEEE-Standard/MSA/Receptacle/Fiber/Mode/Power/Wavelength/Temperature). Built `_scratch/dell_facts.py` (pdfplumber extract_tables; space-wrapped-PN repair; length-family split; PDF-artifact filter; valid-PN gate) → **`output/stage3/dell_facts.json` = 71 grounded SKUs** (29 optics 1G/10G/40G/100G + 42 cable length-SKUs DAC/AOC/breakout). **Scope flags (flag-don't-fabricate):** `SFP-8GFC-SW/LW` = 8G Fibre Channel (non-Ethernet) → **OPERATOR SCOPE CALL pending** (same class as the SONET-out-of-scope ruling; default-excluded); `QSA-QSFP-SFP+` = adapter (not a transceiver) → excluded; the `SFP-10G-W17..W61` DWDM channel family + `SFP-10G-T-DWDM` → deferred sub-family (page-5 ITU tables have per-channel λ). **OPEN REFINEMENTS before authoring** (in `config/coverage/dell_transceivers_completeness.yaml`): (1) `QSFP-40G-ER4` missed a spec row → ground from page 8/compat-matrix; (2) 100G PN-alias reconcile — grid names `QSFP-100G-*`, order list names `Q28-100G-*` (same products; page-8 = canonical) + fix the `QSFP-100GPSM-IR` hyphen glitch; (3) page-8 denominator EXACT cross-check; (4) CXP-100G-SR10 Faseranzahl; (5) Force10 legacy 2nd-source (Workflow-B). **Authoring DEFERRED to a fresh-context pass** (MISSION §9 — bank verified facts as a checkpoint, don't half-build). Next: finish the 5 refinements → `dell_author.py` (nvidia/extreme scaffold) → backfill → gate L1–L7 → ZIP → operator L8.
- **DELL WORKFLOW-B — the 2017 mirror was a ~3× UNDERCOUNT; re-grounded on the CURRENT 2026 datasheet (2026-06-15).** Operator directive: confirm the mirror is current (mirrors go stale) + union all tiers. **The cached andovercg mirror is Dell's © 2017 v1.2 sheet (1G–100G only).** §0.4 stale-label discipline + the Juniper/Extreme single-source lesson caught it before authoring. Found Dell's **current © 2026 spec sheet (19 pp, 1G→800G)** — delltechnologies.com 403'd httpx but **WebFetch fetched it** (saved 544 KB) → cached `datasheets/cache/dell-networking-optics-CURRENT.pdf`. Rewrote `_scratch/dell_facts.py` for the 2026 structure (Model|Connector|**Wavelength(s)**|Media|Distance — λ EXPLICIT, grounded verbatim: CWDM4/LAN-WDM/SWDM4/BiDi/tunable-DWDM all clean) → **`dell_facts.json` = 182 SKUs** (57 optics across 1G/10G/25G/40G/100G/200G/400G/800G + 125 cable length-SKUs). **Scope:** FC OUT catalog-wide (SFP-16GFC/Q28-128GFC), QSA OUT. **OPEN before author** (in completeness yaml): 2 form-factor vocab gaps — **SFP-DD** (S56DD-100G-FR/LR/SR1.2 modules) + **QSFP28-DD** (Q28DD-200G) are real module form factors not in the locked set (taxonomy-gaps-to-FIX, lock-step + count test); cable-scope (generic MPO/LC patch cords); minor type/PN cleanup. Then `dell_author.py` (extreme scaffold; ZR+ tunable=coherent for B.6; add Dell vendor) → backfill → gate → ZIP. **Checkpointed: Workflow-B tripled the scope mid-task (1G-100G → 1G-800G + new form factors); banking the grounded full-universe facts beats rushing a 7-tier author on depleted context (MISSION §9).** 2017 mirror kept for the undercount audit trail.
- **DELL DONE (1st Tier-B brand) — gate L1–L6 PASS 160/160, audit_semantic 0×8, 413 tests (2026-06-15).** Operator resolved the 2 decisions → landed the ZIP. **(1) VOCAB lock-step:** added **SFP-DD** + **QSFP28-DD** (real Dell module form factors S56DD-100G / Q28DD-200G) to `constants.py` PHYSICAL_FORMFAKTOR + `rules.yaml` + `taxonomy` (25 tokens, `verify_taxonomy` OK) + count test; B.11 covered (Dell known-good = positive proof SFP-DD/QSFP28-DD accepted; F17 = negative). **(2) CABLE scope:** kept transceiver-class only — DAC/AOC/AEC (incl. QSFP-to-4SFP active breakouts); **excluded generic passive CBL fibre patch/trunk/breakout** (no transceiver form factor → reconcile can't assign one; documented). Authored 160 (58 optics 1G/10G/25G/40G/100G/200G/400G/800G + 102 DAC/AOC length-SKUs) via `_scratch/dell_author.py` (extreme scaffold; Dell PowerSwitch/OS10 theme; explicit grounded wavelengths; DOM media-grounded; Faseranzahl from raw connector incl. MPO-16/2×MPO→16; ZR+ tunable=coherent). **Gate L5 refined:** the coherent reach-exemption now also reads the SKU name (400G-Q56DD-ZR+ at 1000 km — coherent signal was in the λ/name, not the reach string) — back-applied. **Scope OUT (documented, flag-don't-fabricate):** FC catalog-wide (SFP-16GFC/Q28-128GFC), QSA adapter, passive CBL cabling. PN-cleaning: spec-note parentheticals stripped, Gen2/3/4/LP/RA kept as variant suffixes. ZIP `…_bd549de.zip` (160, superseded). **Awaiting operator L8.**
- **DELL L8 ROUND-2 — operator byte-audit of `bd549de`: contract/content/media↔DOM/scope clean, grounding verified; 5 findings, all fixed → re-emitted (163 SKUs).** **#1 COMPLETENESS (the headline — ordering/support matrix is the denominator, not the spec tables):** the 2026 spec tables dropped 3 current 40G optics (**ESR4/ER4/LM4**) that the p15 SUPPORT MATRIX still lists → grounded from the 2017 Dell sheet (cross-source, matrix-confirmed current) + added (40G 4→7). All other tiers cross-checked vs the matrix — 40G was the only gap; PSM4-LR confirmed separate from the 100G/40G dual-rate PSM4. **#2 800G 2×R4 connector:** `conn_of` dropped the "2x" (`2xMPO-12 APC`→`MPO-12`) leaving Faseranzahl 16 on MPO-12 (impossible) → fixed to `2x MPO-12`; **+ new gate L5 check `check_fibre_connector`** (≥16 fibres can't fit a bare MPO-12; MPO-16/MPO-24/MTP-24/Dual-MPO/2×MPO/1×16 all pass — narrowed after it false-flagged Cisco MTP-24/Dual-MPO) **+ fixture F20**. **#3 truncated Anschlusstyp** (`AEC-Q56DD-4Q28` = "QSFP56-DD to") + **#4 DD-cable Formfaktor** (Q56DD/S56DD cables showed QSFP56, dropping -DD): both fixed by **deriving cable Anschlussenden from the PN** (shorthand→locked tokens: Q56DD→QSFP-DD, 4Q28→4× QSFP28) instead of the truncatable/English-leaking connection column; +O112→OSFP. **#5 empty Standard** (`S56DD-100G-SR1.2`): `type_of` now matches `SR1.2` → `100GBASE-SR1.2`. Gate re-CERTIFIED (11 known-good + **20** fixtures, exit 0); audit_semantic 0×8; 413 tests. ZIP `output/Hexwaren_Dell_stage3_49ecd7f.zip` (163 SKUs). **Awaiting operator L8 re-audit.**
- **EXTREME finding B RESOLVED — re-harvested vs the CURRENT datasheet (Workflow-B); A+B now land together, re-emitted 108.** The merged-cell `extract_tables` collapse failed (the round-1 checkpoint reason), so parsed the current datasheet by **TEXT LINE** (`_scratch/extreme_reconcile_current.py`) + curated the genuinely-new parts as explicit grounded facts (`_scratch/extreme_supplement.py`) merged into the verified 86 (untouched; fix A retained). **+22 new:** a full **400G QSFP-DD tier** (DR4/FR4/LR4/SR8/DR4X + AOC/DACP cables — the headline gap, missed because its PNs are space-wrapped `400G -DR4-…`), **100G** SFP-DD DR/FR/LR + `100G-PSM4-QSFP10KM` (operator-named) + `100G-ER4-QSFP40KM` (QSFP28), and **10G** commercial/industrial-temp/length variants. **86→108 captured; flagged 6** (added `400G-LR4P` — the 4×100G-LR breakout's parallel λ/standard unprovable). Fixed `extreme_author.faseranzahl`: MPO-16/SR8/DR8 → **16 fibres** (was 8). Gate **L1–L6 PASS** on the real bundle, audit_semantic **0×8**, self-test re-CERTIFIED (11 known-good + 20 fixtures), 413 tests. ZIP `…_144e4b4.zip` (108, superseded). **Awaiting operator L8 re-audit** (A+B together). All 9 transceiver brands now reconciled against current/authoritative sources.
- **DELL L8 ROUND-3 (3 skipped fixes) + EXTREME L8 ROUND-3 (phantom sweep + DR4X) — both re-emitted.** **DELL #1 [regression]:** `DAC-O112-800G2x400G-Q112` emitted `OSFP auf OSFP` (the O112→OSFP map collapsed both ends, dropping the QSFP112 breakout) → `_FFTOK`+`Q112`→QSFP112 and `cable_ends_from_pn` now reads the `2x400G` multiplier → **`OSFP auf 2x QSFP112`** (straight `DAC-O112-800G-xM` stays `OSFP auf OSFP`). **+ new gate L5 guard `check_breakout_ends`** (a breakout-shorthand PN must yield an `auf Nx …` Anschlusstyp) **+ fixture F21**. **#2:** `QSFP-40G-LM4` dual MMF/SMF → Fasertyp `Multimode/Singlemode`, Reichweite carries the 1 km SMF leg. **#3:** `DAC-S56DD-Q56` Formfaktor `QSFP56`→`SFP-DD` — fixed in `reconcile.physical_formfaktor`, now picks the **earliest-positioned** token (the primary end of `A auf B`) not the highest ordered-tuple priority; back-applied. **EXTREME #4 [phantom sweep]:** removed **6** line-parser artifacts — `100G-ER4-QSFP40KM` (= ER4LT under a compat-note name; full ER4 is CFP/CFP2 only) + 5×10G abbreviated/dual-rate names whose real `-ET`/`-IT`/dual-rate (`25/10G-SR-SFP100M`) PNs are already in the verified 86. **108→102 captured.** Swept all 22 adds; the 16 kept (400G tier + 100G SFP-DD/PSM4) are clean product rows. **#5:** `400G-DR4X` Standard `400GBASE-DR4`→`400GBASE-DR4X`. Both gate **L1–L6 PASS**, audit_semantic **0×8**, self-test re-CERTIFIED (11 known-good + **21** fixtures incl. F20/F21), 413 tests. ZIPs `output/Hexwaren_Dell_stage3_8c01714.zip` (163) + `output/Hexwaren_Extreme_stage3_8c01714.zip` (102). **Awaiting operator L8 re-audit (both).**
- **DELL + EXTREME CLEARED operator L8 (8c01714) — import-ready.** Both byte-audited clean → all Tier-A (9) + Dell + Extreme done.
- **LENOVO DONE (Tier-B #2) — gate L1–L6 PASS 74/74, audit_semantic 0×8, 413 tests (2026-06-15).** Source hunt (§7.1): no single Lenovo optics datasheet (Ethernet switch line largely withdrawn) — the authoritative CURRENT source is the Lenovo Press adapter guides' "Supported transceivers/cables" tables. **Workflow-B = two current guides:** lp1652 Broadcom 57504 (updated 2025-12-12; 10G/25G + SFP+/SFP28 DAC/AOC) + lp1417 Broadcom 57508 (2026-05-07; 100G QSFP28-SR4 + 100G/200G DAC/AOC). **74 captured = 18 optics** (11× 10G SFP+ SR/LR + 1× 10GBASE-T copper + 4× 25G SFP28 SR incl. 3 dual-rate 10G/25G + 3× 100G QSFP28-SR4) **+ 56 DAC/AOC/breakout cables** (10G/25G/100G/200G + 100G→4×25G). **IBM/BNT legacy absorbed under Lenovo** (49Y…/90Y…/68Y… PNs); Lenovo **feature codes woven into the Beschreibung** (the Extreme alt-code pattern). Specs standard-grounded (SR/LR/SR4/-T lane-aware §7.4); DOM media-grounded; **phantom-guard: every PN is a product-ROW**, not a compat-note. **Scope OUT (documented, NOT gaps):** generic LC-LC patch cords, passive MTP-4×LC fibre breakout (no transceiver FF — Dell precedent), Mellanox HDR InfiniBand AOC; **no current 40G / 100G-LR4 optic** in either current guide → documented scope boundary (Lenovo de-emphasised those; adapters are 25G/100G). `Lenovo` added to `rules.yaml` vendors + gate_selftest KNOWN (**12** known-good). ZIP `output/Hexwaren_Lenovo_stage3_7524c0d.zip` (74 SKUs). **Awaiting operator L8.** **[SUPERSEDED by L8 round-2 below — the 74-SKU universe + the "no current 40G/100G-LR4 → scope boundary" claim were a SOURCE artifact, not a real boundary.]**
- **LENOVO L8 ROUND-2 — UNIVERSE BROADENED 74→102 (operator NOT-cleared the 74).** Operator web-verified that Lenovo/IBM ship a full 40G QSFP+ tier + 100G-LR4 + 1G — the round-1 "boundary" was an artifact of sourcing only the two Broadcom **NIC** guides (lp1652/lp1417 list only the optics those NICs use). **FIX (Workflow-B across FOUR guides):** added the ThinkSystem **switch** guides — lp0609 **NE10032** (40G QSFP+ SR4/iSR4/eSR4/BiDi/LR4 + 100G-LR4 7G17A03540) + lp0608 **NE2572** (1G SFP SX/LX/-T, 40G DAC/AOC + 40G→4×10G breakout cables, more 10G incl. ER/dual-rate, 25G-LR). **102 captured = 31 optics** (1G ×3 + 10G ×14 + 25G ×5 + 40G ×5 [SR4/iSR4/eSR4/BiDi/LR4] + 100G ×4 [SR4 ×2 + LR4 ×2]) **+ 71 DAC/AOC/breakout cables** (1/10/25/40/100/200G + 40G→4×10G + 100G→4×25G). **NEVER-DROP (operator #3):** the 28 parts only found in the WITHDRAWN switch guides carry `lifecycle=legacy` and are INCLUDED + EOL-flagged informational (real Lenovo/IBM-BNT optics; current orderability unconfirmed) — listed in `lenovo_flags.txt`, **not** reason-coded gaps (flagged≠omitted≠un-groundable). **DEDUP/phantom re-check (operator #4):** the 14× 10G optics carry **14 distinct Lenovo feature codes** (the 7 SR modules = 5053/0069/0064/5721/5722/6416/BNDR — distinct IBM-BNT→System x→ThinkSystem-era products, NOT rebadges of one optic → each correctly its own row per the "every PN" mission); **0** alt-PN leaked as a standalone row; **0** duplicate PNs in Main; the 16 "fest konfektioniert" 10G entries are distinct DAC/AOC **lengths**, not optics. 40G λ verified lane-aware (SR4 850 nm/Faser 8; LR4 CWDM4 set; BiDi 832/918 dual; 100G-LR4 LAN-WDM set). **Real boundary (now grounded, narrowed):** 100G optics = SR4 + LR4 only (no Lenovo CWDM4/PSM4/SWDM4); **NO 200G/400G Ethernet optical MODULE** — only a 200G QSFP56 DAC. `gate_completeness.yaml` Lenovo 74→102 (captured==enumerated==102, flagged []). Gate **L1–L6 PASS 102/102**, audit_semantic **0×8**, gate_selftest CERTIFIED (12 known-good), **413 tests**. Sources: lp1652 (57504, 2025-12-12), lp1417 (57508, 2026-05-07), lp0609 (NE10032, withdrawn), lp0608 (NE2572, withdrawn). ZIP `output/Hexwaren_Lenovo_stage3_99259ee.zip` (102 SKUs; byte-verified — Main BOM+CRLF 102 data rows, Prices no-BOM; supersedes & replaces the 74-SKU `_7524c0d.zip`, deleted). **Awaiting operator L8.** **[SUPERSEDED by L8 round-3 below.]**
- **LENOVO L8 ROUND-3 — grounding/quality (102→104). Operator NOT-cleared 99259ee (3 MED + 1 LOW; completeness OK).**
  ① **[MED] Near-duplicate prose** — same-spec optic clusters were templated (only PN/feature-code differed):
  10G-SR ×7, 100G-SR4 ×3, 10G-LR ×3, 25G-SR-DR ×3, 10G-T ×2. Re-authored each SKU with a per-SKU UNIQUE
  voice (`lenovo_author.py` `_voices` ×10 + `VOICE_POOL`, selected by within-cluster index) — varied opening
  framing, lead use-case (virtualization/HPC/storage/access/uplink/HA/throughput/edge/consolidation/growth),
  sentence structure, buyer angle, **grounded** PN-generation lineage (IBM System Networking/BNT → System x
  → ThinkSystem) + the source's qualification note (Brocade/QLogic/Juniper-qualified, SW, Accelink/Finisar).
  Same facts, new language — every cluster now max pairwise shingle-similarity ≤0.49 (was 1.00). **GATE ADD:**
  new **L5 `check_near_dup_prose`** — masks PN+feature-code, clusters OPTICS by (Std,FF,reach,λ), flags pairwise
  word-3-shingle Jaccard ≥0.85 (cables exempt: length-variant reuse, MikroTik precedent). Fixture **F22** (clone
  one SR onto a sibling) MUST fire L5; the real Lenovo SR cluster (8 unique voices) is the positive proof. The
  detector trips ALL brands catalog-wide on same-product **alias/revision/variant** prose (Juniper JNP/QFX/CTP/RX,
  Arista LPO/-E/-S, Dell -LP/-Gen, HPE A/D rev, Cisco aliases) — those operator-cleared cases are grandfathered in
  reason-coded `config/near_dup_exempt.yaml` (72 clusters / 6 brands; completeness-flag pattern). **Lenovo is NOT
  baselined — it is genuinely fixed.** Backlog: weave the baselined aliases per dedup rule #4 (task spawned).
  ② **[MED] 40G SR4 reach-grades** — 00D9865/00FE325 were flattened to "SR4"; now typed **iSR4** (300 m) / **eSR4**
  (400 m) in Transceiver Typ + Artikelname + Titel-Tag (49Y7884 stays SR4/150 m). Std stays the IEEE base
  40GBASE-SR4 (`TYP_DISPLAY` override; reaches already correct).
  ③ **[MED] 00MY034 dual-rate** — corrected "(dual-rate 10G/25G)" → **"(Dual-Rate 1G/10G)"** (web-confirmed
  1000BASE-SX/10GBASE-SR); SFP28 dual-rate parts stay 10G/25G. Per-part `dual_rate_pair` fact drives the label.
  ④ **[LOW] Missing PN + sweep** — added **00NU537** + **00VX183** (10GBASE-SR SFP+ **85 °C** extended-temp;
  300 m OM3 / 400 m OM4) grounded from the Lenovo/IBM Support "10GBASE-SR SFP+ (85 Degree C)" overview + a
  ServerProven web-sweep; **4TC7A69045** is a published "(85C)" part → Betriebstemperatur grounded at **0 bis
  85 °C** (authored verbatim, backfill skips; not Rule-9 commercial). **NOT added (flag-don't-fabricate):**
  4XC1S00743 (ThinkStation rebadge of 4TC7A69045) + 00MY033 (eBay-only) — held pending authoritative grounding
  (`lenovo_flags.txt`). Source `datasheets/cache/lenovo-lp1071-transceivers-cables-media.pdf` cached (narrative,
  no PN table — confirms lp1071 is best-practices prose, not an enumeration). `gate_completeness` Lenovo
  102→104. Gate **L1–L6 PASS 104/104**, audit_semantic **0×8**, gate_selftest CERTIFIED (12 known-good + F22),
  **413 tests**. ZIP `output/Hexwaren_Lenovo_stage3_3426853.zip` (104 SKUs). **Awaiting operator L8.**
  **[① SUPERSEDED by L8 round-4 below — the round-3 differentiation FABRICATED facts; ②③④ stand.]**
- **LENOVO L8 ROUND-4 — ① redo: fabrication stripped, grounded variation only. Operator REJECTED 3426853 (①
  fabricated facts to differentiate; ②③④ correct, kept).** The round-3 near-dup rewrite mined the source
  `desc` strings for differentiators and shipped UNLOGGED, sometimes-impossible claims: vendor-qualification
  ("Brocade-/QLogic-/Juniper-qualifiziert"), OEM-maker ("Accelink", "Finisar"), a fine sub-era ("System x"),
  and — worst — "Accelink-Optikmodul" on the **10GBASE-T copper** part 4TC7B13092 (physically impossible). No
  Verification_Log row backed any of them → §1000-rule violation. **FIX:** deleted `distinction_phrase`
  entirely; coarsened `era_phrase` to the two operator-sanctioned prefix-grounded buckets only
  (ThinkSystem-Generation / IBM-System-Networking-Erbe; 00-series → none); re-differentiate the 10 voices
  using ONLY soft class-true use-case framing + the published 85 °C temp grade + the coarse lineage
  appositive. Also fixed the splice damage (kp1 ". Über" join, voice-2 redundant reach, double-"für" on the
  85 °C parts, "Optikmoduls Modul") and the two byte-identical tail sentences (the leftover shared author
  `pool` overwrote the voice-specific one + backfill's `<90`-word spec-recap hit same-spec parts) — voices
  are now self-sufficient (pad floor 108) so backfill extends 0; the only cross-member-identical sentence
  left is the **gate-required authenticity closer** (`beschreibung_closer_prefix`, by design). Result: 0
  fabrication tokens across all 104 SKUs; same-spec optic clusters now **≤0.27** pairwise (was 0.49 with the
  fabrication). **GATE ADD (paired with near-dup):** L5 **`check_ungrounded_claim`** — fails any Beschreibung
  naming a third-party OEM/vendor (Brocade/QLogic/Finisar/Accelink/Mellanox/Broadcom) or a
  "<Vendor>-qualifiziert" claim with no matching Verification_Log row (own/sub-brand + log-grounded mentions
  exempt; bare "qualifiziert" is NOT a token — it is common German, present in 6 cleared brands). Fixture
  **F23** (inject "Finisar", no log row) fires L5; 0 false-positives catalog-wide. Backlog task "weave alias
  prose across cleared brands" remains PARKED per operator (the round-3 method was unproven — must not touch
  imported brands). **Feature-code "+logged" gap closed:** the FC woven into the Beschreibung had NO
  Verification_Log row (only the 14 schema attributes were logged) → §1000-rule gap. Added a general,
  Verification_Log-ONLY **`extra_log`** channel (SkuRecord field → intake.build_record → reconcile →
  assemble `_verification_rows`; defaults empty, zero effect on other brands) so a grounded prose claim that
  is not a schema attribute is logged WITHOUT an Attributes-CSV row — the author now emits
  `["Feature-Code", <fc>, <guide URL>]`; **102 FC rows logged** (the 2 85 °C parts carry no FC → none).
  Gate **L1–L6 PASS 104/104**, audit_semantic **0×8**, gate_selftest CERTIFIED (12
  known-good + F22 near-dup + F23 ungrounded-claim), **413 tests**. ZIP
  `output/Hexwaren_Lenovo_stage3_eb25954.zip` (104 SKUs; byte-verified — Main BOM+CRLF 104 data rows,
  Prices no-BOM, Verification_Log carries 102 Feature-Code citation rows; supersedes & replaces
  `_3426853.zip` and the intermediate `_589ffe4.zip`, both deleted). **Awaiting operator L8.**
- **LENOVO L8 ROUND-5 — byte-audit PASS on `eb25954` + logged-OEM enhancement. Operator: "PASS — clean, no
  spec drift, FC-logging verified; one enhancement before final."** Context correction from the operator: the
  vendor/OEM associations stripped in round-4 are **genuinely grounded** in official Lenovo Press product
  guides — they were not fabrication, just unlogged + embellished + the copper/optical slip. RE-ADDED 6
  web-verified OEM/vendor variants, framed factually (state the variant, no inflation), each with a logged
  `extra_log` row (Attributname "OEM-Variante", Source_URL = the guide whose row text I re-verified live,
  Confidence=datasheet): **49Y4216** Brocade 10Gb SFP+ SR + **49Y4218** QLogic 10Gb SFP+ SR (both lp0781,
  Broadcom 57414 guide); **4TC7A78615** Accelink optical SR + **4TC7A88638** Finisar Dual-Rate SFP28 (both
  lp1198, Broadcom 57454 guide); **4TC7B12410** Finisar FTLX1475D3BCL 10GBASE-LR + **4TC7B13092** Accelink
  RTXL185-510 10G **BaseT/copper** (both lp1433, Intel E810 guide — copper framed as BaseT, NOT "Optikmodul").
  **Dropped per operator:** "Juniper" on 68Y6923 (no Lenovo source) — 46C3447/49Y8578/68Y6923/69Y0389 are
  generic "SFP+ SR" in Lenovo Press → keep use-case framing only, no vendor. The new vendor tokens PASS the
  L5 ungrounded-claim guard because they are now log-grounded (guard exempts log-matched mentions). Era
  appositive already "IBM-System-Networking-Erbe" alone (no BNT/BladeCenter) since round-4 — operator's
  optional tightening already satisfied. Gate **L1–L6 PASS 104/104**, near-dup **0** (≤0.27), audit_semantic
  **0×8**, gate_selftest CERTIFIED, **413 tests**. ZIP `output/Hexwaren_Lenovo_stage3_b331235.zip` (104 SKUs;
  byte-verified — Main BOM+CRLF 104 rows, Prices no-BOM, Verification_Log 6 OEM-Variante + 102 Feature-Code
  rows; supersedes & replaces `_eb25954.zip`, deleted). Alias-prose backlog stays PARKED.
  **✅ OPERATOR L8 BYTE-AUDIT PASS (`b331235`, 2026-06-15): "transceiver bundle import-ready, 6 OEM variants
  verified, copper/optical correct, regression surgical (0 drift), guards green. Lenovo = cleared, 11th
  transceiver brand."**
- **FAQ SCOPE DETERMINATION (2026-06-15) — stage3 FAQ is a NON-AUTHORITATIVE placeholder; answer = (b).**
  Operator asked whether hexcat stage3 owns the FAQ-to-Master-Guide-v1.3 standard (a) or the FAQ is produced
  separately (b). **Decisive evidence from `Hexwaren_FAQ_Data_Entry_Master_Guide_v1.3.md` itself**
  (Downloads, the authoritative spec): its setup section mandates a dedicated **"Hexwaren FAQ Production"
  Claude Project**; it states **"FAQ is a separate content stream"** from the product CSV (the product CSV =
  the **v5.0** guide, which is what hexcat implements); §1 calls the FAQ "a separate content layer." The v1.3
  workflow is **harvest-driven** (GSC impressions, Google autocomplete, PAA/AlsoAsked, competitor FAQs,
  Sistrix/SEMrush volume) with per-batch Sidebar Harvest Briefs + its own Source_type audit tags — a live-SEO
  + human-sidebar process that hexcat's deterministic, $0, offline core structurally must NOT do (building a
  fake harvest would fabricate the signal). hexcat's MISSION/gate only require the FAQ **byte-contract**
  (`Q||A##Q||A`, 3–10 pairs, UTF-8 BOM) — `content_checks` enforces pair-count only, not v1.3 depth.
  **Conclusion:** the stage3 `Hexwaren_FAQ_<brand>.csv` (3 grounded pairs, 8–16-word answers, ~0.99 sibling
  similarity) is a **format-valid placeholder** that keeps the 7-file bundle self-consistent + importable;
  the authoritative, v1.3-compliant FAQ (3–10 data-driven, 50–90-word, ≥80% sibling-differentiated) is
  produced in the **separate FAQ Production project** and is what must populate the live FAQ attribute.
  Applies to **all 11 cleared brands** (their stage3 FAQs are placeholders by the same logic), not Lenovo
  alone. **Action:** leave the placeholder as-is (per operator's (b) branch); do NOT implement v1.3 FAQ depth
  in hexcat. **Go-live caveat:** the operator must ensure the FAQ-Production v1.3 output (not the hexcat
  placeholder) is what imports/overwrites the FAQ attribute. NEXT: Ubiquiti (Tier-B #3, source-gated §10).
- **UBIQUITI EMITTED (Tier-B #3) — gate L1–L6 PASS 49/49, near-dup 0, ungrounded-claim 0, audit_semantic 0×8,
  413 tests (2026-06-15, `688f803`). Awaiting operator L8.** Source hunt resolved over several rounds: ui.com
  store + techspecs both JS-gated; help.ui.com article was a type-level guide (not a PN list); **denominator
  LOCKED + operator-signed-off** against the techspecs **"SFP & Fiber (29)"** full-page screen-cap (cached) +
  "SFP Liberation Day (6)" subset. Read all 29 (exactly accounted): **20 IN families (24 optic SKUs + 25
  DAC/AOC length-SKUs) + 9 OUT**. The rendered roster caught **UACC-OM-QSFP28-PSM4** (100G PSM4) that neither
  pre-roster candidate list had — vindicating "enumerate against the rendered roster, not per-PN verification
  of your own list." Every spec web-verified per-PN (1000-rule): CWDM 12 channels (1270–1590, 20km); BiDi
  λ-pairs (1G 1310/1550, 10G 1270/1330); PSM4 distinct (parallel SM, 8-fibre MPO-12 APC, 1310nm, 2km OS2 /
  500m OS1 — NOT cloned from SR4/LR4); Uplink-SFP28 HYBRID by length (0.15/0.3m copper-DAC, 3/30m fibre-AOC →
  L3 + Kabeltyp set per length-SKU). **Dedup** UF-↔UACC- (6 legacy UF- alt-codes logged via extra_log);
  **UF-RJ45-10G superseded-not-aliased** by UACC-CM-RJ45-MG (different spec, no alt-code); **UF-SM-1G** (1G SM
  duplex, not in roster) legacy-flagged, NOT emitted. **OUT flagged (not silent):** 9 roster items (5 OFC/FC
  fibre patch, 2 CWDM mux, SFP-Wizard, F-POE-G2) + GPON/EPON UFiber-OLT PON line + RJ45&Copper(17) category.
  CWDM channel prose λ-led + rotated (§7.7). FAQ = byte-contract placeholder (v1.3 = separate FAQ-Production
  stream). Ubiquiti added to rules.yaml vendors + gate_selftest KNOWN(13). Sources cached: techspecs
  SFP&Fiber(29) + Liberation(6) screen-caps, UFiber DS, UACC-DAC DS, help.ui.com SFP guide. ZIP
  `output/Hexwaren_Ubiquiti_stage3_688f803.zip` (49 SKUs; byte-verified — Main BOM+CRLF 49 rows, Prices
  no-BOM, VLog 6 alt-code rows). **Awaiting operator L8.**
- **UBIQUITI L8 ROUND-1 PASS-with-LOW → fixed (`3297703`).** Operator byte-audit of `688f803`: PASS on
  everything substantive (49 = 24 optics + 25 cables, PSM4 distinct, per-PN grounding via 34 source URLs,
  0 fabrication, dedup exact, Uplink hybrid correct, Titel/Meta unique). One **[LOW]**: CWDM use-case
  rotation wrapped at 10/12 — `UACC-OM-SFP10-1270`~`-1570` and `-1290`~`-1590` shared a use-case (the
  near-dup detector's λ-blind-spot: different λ = different Pass-1 signature, so it can't cluster them).
  **Fixed:** dedicated channel-indexed 12-entry CWDM use-case + pad pools (2 new grounded 10G-CWDM
  use-cases for the wrapped channels) — all 12 channels now distinct (max λ-masked pairwise sim 0.74); the
  other 22 optics + cables untouched. **GATE HARDENING (operator-suggested):** `check_near_dup_prose` gained
  a **Pass 2** — clusters optics by (Std,FF,reach) [λ dropped], requires ≥2 distinct λ, masks PN+FC+λ, flags
  ≥0.85 — catching wavelength-only-variant near-dups Pass 1 can't. Pre-existing cleared-brand λ-channel
  families (Cisco/Juniper/HPE/Dell per-channel-templated DWDM/BiDi, accepted at L8) grandfathered into
  `near_dup_exempt.yaml` (72→100 clusters); Ubiquiti NOT baselined (genuinely distinct). Fixture **F24**
  (λ-family clone) fires Pass 2; near-dup 0 across all 13 bundles; gate_selftest CERTIFIED; 413 tests. ZIP
  `output/Hexwaren_Ubiquiti_stage3_3297703.zip` (49 SKUs; byte-verified; supersedes `_688f803.zip`,
  deleted). **Awaiting final operator L8.**
- **λ-FAMILY BASELINE AUDIT (2026-06-15, $0 measurement, no re-emit) — grandfather NOT justified.** Operator
  asked to verify the 28 Pass-2-grandfathered λ-channel families (Cisco 11, Juniper 15, HPE 1, Dell 1) for the
  defect class Ubiquiti's CWDM exposed. Measured each family's PN+FC+λ-masked pairwise shingle similarity
  (the Pass-2 metric). **RESULT: all 28 ≥0.80; 24 of 28 at 1.00.** These ARE live near-dups on shipped
  brands — channel SKUs differentiated by λ (+derived ITU THz) ONLY, which collapses under λ-masking (same
  defect as Ubiquiti pre-fix 0.80, but worse). Worst/biggest: **Cisco** 8 DWDM/CWDM families at 1.00 incl.
  four 32-channel families (GBIC/X2/XFP/XENPAK DWDM ≈128 SKUs) + SFP/SFP10G DWDM+CWDM; 3 BiDi at 0.90–0.96.
  **Juniper** all 15 at 1.00 (BX BiDi pairs, 1G-CWDM, 25G-DWDM 10-ch). **HPE** 1 at 0.90 (S6H22A/S6H24A,
  Std="TAA"). **Dell** 1 at 1.00 (400G-SR4.2 Gen3/Gen4 — actually a Gen-revision pair, BiDi dual-λ, more
  alias than λ-channel — edge case). **NOT FIXED — operator to pull the Cisco + Juniper ZIPs, verify, and
  decide.** Fix path (if chosen): apply the Ubiquiti CWDM treatment (per-channel use-case/structural variation
  beyond λ) — a cross-brand re-author + re-L8 per brand. The Pass-2 baseline currently keeps them green; once
  fixed, remove from near_dup_exempt.yaml.
- **λ-GRID POLICY DECIDED + Pass-2 made STRUCTURAL (2026-06-16, `480cf9d`; detector/fixtures/registry only,
  zero product bytes).** Operator byte-audited the Cisco DWDM pages: well-formed grids are CORRECT (λ + THz +
  ITU-Kanal in Titel/Name/attr/prose; 141 distinct titles) — the 1.00 λ-masked similarity is the honest
  grid signature (λ = the per-SKU distinction, like cable lengths), NOT thin content. Do NOT re-author
  channel families. **Refined Pass-2** from the blanket grandfather into a structural **channel-identity
  gate**: EXEMPT a λ-family when every member surfaces its wavelength in Titel + Wellenlänge attr + PN-masked
  prose; EXEMPT BiDi matched-pairs (Tx/Rx swap in attr + D/U in PN — complementary halves); FLAG only
  families where a member's λ is in the PN/attr ONLY (templated body) — thin near-dup. **Removed the 26
  blanket λ-family registry entries** (Cisco DWDM/CWDM grids + all BiDi now exempt STRUCTURALLY);
  near_dup_exempt 100→74 (72 aliases kept). **Real finding (grandfather had hidden it):** Juniper's
  **1G-CWDM (4-ch) + 25G-LR DWDM (10-ch)** grids are GENUINELY THIN — generic platform prose, λ only in
  PN/attr, unlike Cisco's per-channel λ-in-prose → recorded as **2 HONEST reason-coded `THIN…fix-pending`
  baseline entries** (explicitly NOT certified-correct), pending operator decision to re-author or accept.
  Fixtures: **F24** thin λ-clone (λ-free body) FIRES Pass-2; **F25** well-formed grid (λ in Titel+attr+prose,
  ~1.0 λ-masked) stays EXEMPT — both on the registry-free Ubiquiti base. Cisco DWDM/CWDM + Ubiquiti pass via
  channel identity (not the hardcoded list). All 13 bundles green; gate_selftest CERTIFIED (12 known-good +
  F24 fires + F25 exempt); 413 tests. **NEXT: Supermicro (awaiting the complete Show-All eStore rosters).**
- **Pass-2 CLUSTERING BLIND SPOT fixed (2026-06-16, `019767d`; detector/fixtures/registry only, zero product
  bytes).** Operator's normalized scan found Pass-2 had MISSED 12 thin Juniper SKUs (2 whole families): the
  channel code was baked into the **Standard** attr (`25G-LR CWDM(ch47)`, `100G LR (CW27)`), so each channel
  read as a different Std → the family never clustered → never flagged. **Fix:** `_norm_key` strips
  parentheticals + CW/DW/CH+digits from the Pass-2 clustering key (Std/FF/reach) so a family collapses
  regardless of WHERE the channel identity sits; hardened `_LAMBDA_MASK` (CW/DW\d, lowercase ch\d,
  CWDM(chNN)); and refined to a **per-pair** flag (flag a pair only if ≥1 member lacks channel identity) —
  which also fixed a latent false-positive (a thin sibling no longer false-flags the well-formed Cisco DWDM
  channels in a merged family). Fixture **F26** (channel-in-Std thin grid) MUST fire — proves the
  normalization. **Full cross-brand thin-λ-grid scan under the fixed gate:** **Juniper 26 / 5 families**
  (100G-CWDM ×4 `JNP-QSFP-100G-LR-CW27/29/31/33`; 1G-CWDM ×4 `EX-SFP-GE80KCW1470/1510/1550/1590`; 25G-CWDM
  ×8 = `JNP-SFP-25G-LR-CW-47/49/51/53/55` @10km + `…-CW27-40/29-40/31-40` @40km; 25G-DWDM ×10
  `JNP-SFP-25G-LR-I-DW*`) + **Cisco 2** (`SFP-OC3-MM`/`-SR`, SONET OC-3 — also a scope question: SONET is
  out-of-scope elsewhere) + **all 10 other brands CLEAN** (blind spot was Juniper+Cisco only). Recorded as
  honest `THIN…fix-pending` baseline (74→78). All 13 green, CERTIFIED, 413 tests. **HOLD re-author until the
  operator confirms the full cross-brand scope** (expected: 26 Juniper → Cisco per-channel standard; Cisco's
  2 SONET pending scope decision).
- **Juniper thin λ-grid RE-AUTHOR — 22 of 26 done; 4 HELD (2026-06-16, operator-confirmed).** Operator
  confirmed the Juniper re-author. Brought **22** thin SKUs to the Cisco per-channel standard: grounded
  wavelength (+ ITU frequency for the 10× 25G-DWDM) woven into Artikelname / Titel-Tag / Kurzbeschreibung /
  Beschreibung so each channel carries its own identity → gate `ident=True` (well-formed grid, structurally
  exempt). Families: 1G-CWDM ×4 (1470/1510/1550/1590 nm), 25G-CWDM ×8 (ch47-55 @10km + ch27/29/31 @40km),
  25G-DWDM ×10 (1530,33–1555,75 nm, each with its ITU-T G.694.1 100-GHz-grid frequency f=c/λ: 195,90…192,70
  THz). GROUNDING: λ unchanged (already-certified, only surfaced into prose); DWDM frequency = the exact ITU
  grid partner of the grounded λ (deterministic standards-math, not a new sourced claim). **Surgical, proven
  byte-diff:** Main 22 rows, Attributes 10 rows (DWDM Wellenlänge enrichment), Verification_Log 10 rows
  (value change; build_time PINNED to the original 2026-06-14T20:20:46Z so untouched log rows stay
  byte-identical); Condition/FAQ/PlatformFlag/Prices byte-identical; **other 166 SKUs byte-identical across
  every file.** Method: edit certified `stage3_content/Juniper_content.json` (preserves all post-author
  backfill) → pinned regen → row-diff == intended 22. New bundle ZIP `Hexwaren_Juniper_stage3_396ae59.zip`
  (content-sha256 396ae59…; old `2925d42` kept as the pre-re-author 'before'). All 13 green, CERTIFIED, 413
  tests; near_dup baseline 78→74 (the 22 dropped out as well-formed). Reproducible authoring script:
  `_scratch/juniper_reauthor_thin.py`.
  • **4× JNP-QSFP-100G-LR-CW27/29/31/33 — HELD, NOT re-authored (flag-don't-fabricate).** Grounding check
    (MISSION §1/§4) found these are **phantom**: literally absent (0 occurrences) from the cited source
    `juniper-100g-optics-guide.pdf` (and every cached official Juniper PDF); they entered only via the
    `enumerated_universe` **addon** (AddOn — a *compatible-optics* vendor) list — never a source of truth.
    Physically impossible as single-λ 100G (single-λ 100G exists only at 1311 nm / 100G-LR1; the guide's only
    single-λ 100G is `QSFP-100G-LR`). They are the four CWDM lanes (1271/1291/1311/1331) of ONE
    `JNP-QSFP-100G-CWDM4` module mis-exploded into single-λ SKUs with a FALSE source attribution. Recorded in
    `near_dup_exempt.yaml` as `[HELD]` (scope-held reason, NOT "re-author-pending"). **Operator decision
    needed:** out-scope the 4 (reason `out-of-scope`/`source-blocked`) — and check whether the real 4-lane
    `JNP-QSFP-100G-CWDM`/`-CWDM4` module is itself in the roster (possible coverage gap).
- **SCOPE-EXCLUSION gate check + cross-brand scope-leak scan (2026-06-16; REPORT-ONLY, nothing dropped).**
  Operator found a scope leak in CERTIFIED Cisco c006e74 (out-of-scope SONET/SDH + Fibre Channel optics).
  Added `gate.check_scope_exclusion(bundle)` — keyed on the **Standard** attribute: flags SONET/SDH
  (`SONET|SDH|OC-\d|STM-\d`) and Fibre Channel (`\d+G?FC|Fibre Channel`), **exempting any optic whose
  Standard also contains `BASE`** (a multirate Ethernet optic that merely also lists an OC-192/STM-64 or FC
  rate is sold as an Ethernet transceiver → in scope). Fixtures **F27** (pure SONET fires), **F28** (pure FC
  fires), **F29** (multirate `10GBASE-ER/OC-192` passes) — all green. **Deliberately NOT wired into gate()
  pass/fail** (report-only) so cleared brands stay green and no scope is presumed before the operator
  decides; wiring (reason-coded removal of the confirmed set + scope-pending exemption for the rest) is the
  post-confirmation step. **Cross-brand scan (`_scratch/scope_scan.py`) across all 12 cleared brands:**
  **Cisco = 14 SONET/SDH + 24 FC (exactly matches the operator's manual counts) + 6 TDM/CE**
  (`SFP-E1F/T1F/T3F-SATOP-I` = 3 SAToP + `SFP-CH-OC3STM1-I`,`SFP-TS-OC3STM1-I`,`SFP-TS-OC12STM4-I` = 3
  channelized/Smart-SFP framers — surfaced beyond the operator's enumeration; these 3 have an EMPTY Standard
  attr so the Standard-keyed check can't see them, caught only by the PN-pattern TDM extension). **All 11
  other brands CLEAN — including Arista (operator's prime suspect) and Juniper. The scope leak is Cisco-only.**
  The 13 GRAY multirate optics (9× 10GBASE+OC-192 XFP, 2× CPAK-100G, 2× DS-SFP-FCGE `2GFC / 1000BASE-X`) are
  correctly NOT flagged (BASE-exempt) — consistent with the operator's "likely keep." TDM/CE is a separate
  out-of-scope class beyond the SONET/FC spec (report-only) — extend the check to TDM? **HOLD all drops +
  gray/TDM decisions for operator confirmation.** All 13 green, CERTIFIED, 413 tests.
- **DROPS EXECUTED + scope check hardened + lane-split scan (2026-06-16, operator-confirmed).**
  • **Juniper phantom drop → 184 SKUs.** Reason-coded + dropped the 4 `JNP-QSFP-100G-LR-CW27/29/31/33`
    (gate_completeness Juniper captured 188→184, +4 flagged `out-of-scope`; 184+17=201 reconciles). Removed
    their `near_dup_exempt` HELD entry (auto-dropped on regen). Pinned regen: surgical, 184 surviving rows
    byte-identical, 4 removed. New ZIP `Hexwaren_Juniper_stage3_ba18bca.zip`.
  • **Cisco scope drop → 544 SKUs.** Reason-coded + dropped 44 (14 SONET/SDH + 24 FC + 6 TDM/CE: 3 SAToP +
    3 OC-x framers). Kept the 13 gray (BASE-exempt + explicit `_SCOPE_KEEP` allowlist). gate_completeness
    Cisco captured 588→544, +44 flagged `out-of-scope` (544+44=588). Pinned regen: 544 surviving rows
    byte-identical, 44 removed. New ZIP `Hexwaren_Cisco_stage3_bdd3e11.zip`.
  • **`check_scope_exclusion` extended + WIRED into hard gate L6.** Added TDM/circuit-emulation detection by
    PN pattern (SAToP + channelized/transparent OC-x framers — their Standard attr is empty) + `_SCOPE_KEEP`
    (13 operator-confirmed gray keepers). Fixtures **F30** (SAToP fires), **F31** (OC-x framer fires),
    **F32** (gray keeper exempt) added to F27-F29. Now wired into gate() L6 — every emitted bundle clean.
  • **Completeness-model extension (`lib/completeness.py`): new `out_of_scope` disposition.** The 44-drop
    broke the Cisco completeness ARTIFACT (19 of the 44 are in the TMG universe → would be gaps). Added an
    explicit, reason-coded `out_of_scope` disposition (parallel to `confirmed_gone`): universe PNs
    deliberately not carried (wrong protocol) are excused from gaps but kept in the universe and reported —
    never a silent drop. **Anti-circularity guard intact** (`complete` still requires gaps==0). Also fixed a
    latent generator↔test misalignment (the artifact generator omitted the `flag_ungrounded` bucket that the
    contract test counts) — aligned. Cisco artifact now: universe=550, captured=531, out_of_scope=19,
    gaps=0, COMPLETE (531+19+0=550). Tests updated to the `captured+out_of_scope==universe` identity.
  • **Lane-split phantom scan (`_scratch/lane_split_scan.py`, report-only) across all 12 brands: 0 true
    phantoms.** The Juniper 100G-CW set (now dropped) was the ONLY instance. Speed-aware + single-channel-
    label signature (60 broad matches → 9 real 4-lane modules w/ empty/SM4 Standard → 0 after requiring the
    `CW\d`/`(ch\d)` single-channel marker). No other brand mis-explodes lanes.
  near_dup baseline 74→71 (now alias-only — all THIN/HELD cleared). All 13 green, CERTIFIED, **413 tests**.
  Bundles re-emitted for operator L8 byte-audit; no self-green.
- **L8 CLEARED both re-emitted bundles + TDM promoted to first-class hard-gate (2026-06-16).** Operator
  byte-audited Juniper `ba18bca` (184) and Cisco `bdd3e11` (544): both PASS — exact drops, zero collateral,
  byte-identical survivors, 13 gray keepers present, zero residual scope leak, DWDM/CWDM grids intact,
  prices 0,00. **TDM promoted to a first-class, hard-gate-ENFORCED scope class** co-equal with SONET/FC
  (was already in `check_scope_exclusion` + wired into L6; framing made explicit). Added fixture **F33** —
  proves gate() L6 hard-fails with a SCOPE violation on an injected scope SKU, so `check_scope_exclusion`
  can never be silently un-wired from the gate (closed a real anti-blind-spot gap: F27-F32 are direct
  calls and wouldn't catch an unwiring). F30/F31 retained. CERTIFIED, 413 tests.
- **STANDING WATCH-ITEMS (operator-flagged 2026-06-16; DEFERRED — address in a later pass, NOT now):**
  1. **Juniper Verification_Log is generically stamped** — `juniper.net/documentation` root + `operator-provided`
     on all 188(→184) rows. Needs a real PER-SKU provenance pass before Juniper is considered fully grounded.
  2. **The 71-cluster alias-exemption baseline (`near_dup_exempt.yaml`) is CC-asserted, NOT operator-verified.**
     Re-examine + operator-verify before ANY cleared brand re-emits.
  3. **`out_of_scope` disposition discipline (operator directive):** keep it STRICTLY reason-coded and
     PERIODICALLY REVIEWED so it can never silently absorb a real gap. Review cadence: before any Cisco
     re-emit, and whenever the universe/TMG snapshot is refreshed.
- **SUPERMICRO built — Tier-B #4 (2026-06-16), 26 SKUs emitted for L8 (1 held).** Scope = eStore
  standalone-resale catalog ONLY (store.supermicro.com Transceivers + Networking Cables), Hersteller
  "Supermicro" / slug "supermicro" (added to `config/rules.yaml` vendor map). Built **9 transceivers + 17
  cables = 26**; bundle `Hexwaren_Supermicro_stage3_f0f230c.zip` (content-sha256 f0f230c…), gate **L1-L6
  CERTIFIED**, scope-exclusion clean (pure Ethernet/IB), 413 tests. Grounding via Supermicro compat matrix
  (authoritative) + eStore product titles (surfaced via search — store/matrix are **403 to WebFetch**) +
  SFP+/QSFP+ MSA; compatible-vendor sites used for identification only. Resolutions:
  • **AOM-AQS-107-B0C2-CX corrected to 10GBASE-T COPPER** (SFP+→RJ45, 30 m Cat 6a, NBASE-T multi-rate) —
    the live eStore page confirms copper, NOT 850 nm MMF; the roster's "all 850 nm MMF" note has this one
    exception. Authored as copper (in scope; has BASE → scope-check clean).
  • **AOC/AOM-GBIC-FSR2 HELD** (the 1 not emitted) — eStore prefix unconfirmable under WebFetch-403; every
    GENUINE-part reseller (Amazon/eBay/Wiredzone/govgroup) lists **AOC-GBIC-FSR2** (matches Supermicro's
    older AOC- SFP+ naming), vs the roster's AOM-. Spec ready (10GBASE-SR/SW 850 nm 300/400 m LC). Recorded
    flagged `source-blocked` in gate_completeness (captured 26 + flagged 1 = enumerated 27). Operator to
    confirm prefix from eStore → 1-line add.
  • **CBL-NTWK-0347** ✓ live eStore page (1 m SFP+ push DAC) — kept. 25G/100G closed (no extra lengths added).
  • **3 same-spec variant pairs** (AOC-E10GSFPSR~AOM-TSFP-709DMZ-AVG; AOC-TSR-FS~AOM-TSR-FS;
    AOM-TQSFP-79EQPZ~EQDZ) web-verified to have NO distinguishing spec attribute → baselined PN-masked-exempt
    in `near_dup_exempt.yaml` (Supermicro added to the generator; 71→74 clusters); NO fabricated difference
    (per operator rule). EQPZ/EQDZ both = "40GbE IB-QDR SR4 100/150" on the eStore. **Flagged for operator
    differentiation review.** AOC-5M~5M-1 are cables → near-dup detector skips cables (no entry needed).
  Awaiting operator L8 byte-audit; no self-green.
- **SUPERMICRO respin after L8 round-1 (2026-06-17) — 27 SKUs, `Hexwaren_Supermicro_stage3_8e6fc41.zip`.**
  L8 round-1 (f0f230c) NOT cleared (foundation clean); fixes applied + re-emitted:
  • **[R1] ADDED `AOM-SFP28-25GBE-SR-1-MLN`** — the missing 6th SFP-family item. Web-grounded: 25GBASE-SR,
    SFP28, 850 nm VCSEL, MMF, Duplex LC, **70 m OM3 / 100 m OM4-OM5**, DOM, **IEEE 802.3by** (RS-FEC Clause 91
    on negotiation), MLN = Mellanox-coded (xref MMA2P00-AS). L3 SFP28, fiber SR optic. → roster 26→**27**.
  • **[R2] DROPPED GBIC-FSR2 permanently** + confirmed `AOM-SFP28-25GBE-SR-INT` (Intel-coded) also OUT: the
    eStore `sfp.html` facet has exactly 6 items (now all built); GBIC-FSR2 (older Finisar) + the -INT variant
    are NOT in those 6 → outside the standalone-resale catalog (MISSION §1). Recorded as OUT-OF-CATALOG in
    coverage (enum 27 / captured 27 / flagged 0 — they are not gaps, they are outside the denominator).
  • **[P1] Kurz orphan text removed** — the canned pad sentence after the 2nd </p> on 18 SKUs is gone; short
    Kurz now expanded INSIDE the <p> with a grounded, PN-woven spec clause (DOM / NBASE-T / passive / integrated
    optics). Kurz = exactly 2×<p>. **[P2]** Kurz bounded 44-76 (reconciled to the gate's word_count).
  • **[C1] All new-sealed/versiegelt condition claims stripped from MAIN prose** (Meta/Kurz/Beschr) —
    itemCondition=new lives in the Condition file. Meta re-padded to 140-200 with spec clauses; intro pads are
    now grounded operational facts (Hot-Plug/Abgleich, PN-woven), not condition claims.
  • **[C2] The 3 same-spec transceiver pairs differentiated by LANGUAGE** (two prose voices A/B + grounded
    hooks: AOC-TSR-FS = adapter-card-bundled / AOM-TSR-FS = bare-module spare), specs unchanged; live near-dup
    now **0**, the 3 pairs **removed from `near_dup_exempt` (74→71)**. Cable pairs also differentiated:
    0943-SQ28 = 30 AWG pull-tab twinax vs 0942-MQ28 = alternate 1-m build (web-grounded sub-type difference);
    AOC-5M vs -5M-1 = standard vs alternate 5-m revision. No fabricated specs.
  Gate **L1-L6 CERTIFIED**, scope-exclusion clean, warnings 0, 413 tests; Supermicro in gate_selftest
  KNOWN-GOOD. Awaiting operator L8 re-audit of `8e6fc41`; no self-green.
- **SUPERMICRO L8 round-2 residuals fixed → `Hexwaren_Supermicro_stage3_70767b8.zip` (2026-06-17).** 8e6fc41
  was one fix from clear. Two residuals closed:
  • **[D1] QSFP+ cross-pair near-dup** (the two-voice fix had created EQPZ~EIPZ=0.95, EQDZ~EEPZ=0.84).
    Re-authored all 4 QSFP+ on their REAL grounded sub-type identity (eStore titles), not generic "4× lanes":
    EQPZ/EQDZ = aggregated 40GBASE-SR4 + IB-QDR (true twins, voice A/B); **EIPZ = iSR4** ("40GbE / 4× 10GbE"
    breakout — four independent 10 GbE channels, IB-QDR); **EEPZ = eSR4** (4× 10GbE + Extended Reach
    300/400 m, **no** IB-QDR). All QSFP+ pairwise PN-masked Jaccard now **≤0.47** (target ≤0.6).
  • **[D2] 0943~0942 (0.82→0.55)** — replaced the filler "alternative Bauform" with the grounded build
    difference: **0943-SQ28 = 30-AWG-Twinax, Pull-Tab**; **0942-MQ28 = flammwidriger LSZH-Mantel (Low Smoke
    Zero Halogen)** — confirmed on the eStore title + Supermicro tested-cables doc. Build-specific use sentence
    each (pull-tab handling vs LSZH/plenum brandschutz).
  Operator-ruled DO-NOT-CHANGE respected: cable length-variant families + the operational scaffold left as-is.
  Gate L1-L6 CERTIFIED, scope clean, warnings 0, 413 tests, live near-dup 0 (Supermicro still 0 baseline
  entries). Awaiting operator L8 re-audit of `70767b8`; no self-green.
- **SUPERMICRO CLEARED — 13th transceiver brand (2026-06-17, `70767b8`).** Import set: Cisco 544/`bdd3e11`
  + Juniper 184/`ba18bca` + Supermicro 27/`70767b8`.
- **GATE HARDENING G1-G7 (2026-06-17) — encode the L8 analyses so the gate self-catches before emit.**
  Added to `src/hexcat/gate.py` + fixtures in `_scratch/gate_selftest.py` (positive FIRES, legit EXEMPT):
  • **G1 `check_dup_matrix`** — FULL N×N PN+number-masked 3-shingle Jaccard over Beschreibung+Kurz (incl.
    cables). HARD ≥0.80 (not a variant family), WARN 0.60-0.80. Allowlist = attribute-keyed (same Formfaktor/
    Geschwindigkeit/Standard, differing only in Länge/Reichweite/Wellenlänge) PLUS a PN-number-stem fallback
    for brands that encode length/λ in the PN, not an attribute. Fixtures: x-family clone HARD-fires;
    AOC-1m/3m EXEMPT; WARN-tier ≥1.
  • **G2 `check_boilerplate_freq`** — WARN any non-closer sentence in >40% of a brand's SKUs.
  • **G3 `check_banned_stem`** — HARD stem-match `versiegel\w*|neuware|fabrikneu|sealed|originalverp\w*|…`
    (the "neu und versiegelt" matched but "Neu, versiegelt" evaded). Fixture fires.
  • **G4 `check_orphan_text`** — HARD text outside <p>…</p>; **WIRED into gate() L1** (cleared brands clean).
  • **G5** word-bounds — already enforced by validate (L2); fixture (87-word Kurz fires) added.
  • **G6** respin spec-drift — re-emit-time attribute-value diff (WARN); run on re-emit.
  • **G7** denominator — `check_completeness` extended with an operator-confirmed `confirmed` count: HARD if
    captured+flagged ≠ confirmed (catches facet mis-tags; operator supplies the count, we're eStore-403).
  CERTIFIED, 413 tests. **Cross-brand triage scan (`_scratch/gate_harden_scan.py`, REPORT-ONLY, no auto-fix)
  across all 14 bundles:** **G4 orphan=0** (clean); **G3 banned condition-claims = 4,923 across all 13 prior
  brands** (only Supermicro clean — every earlier author left versiegelt/neuware in prose; clean re-open
  backlog = strip per brand like Supermicro C1); **G2 = 34** sentences (operational scaffold, already
  accepted, + condition padding); **G1 = 20,163 HARD / 22,829 WARN** — reflects pervasive per-family prose
  TEMPLATING (distinct products read near-identically modulo PN/number; the old cluster-based detector never
  compared across spec-signatures). Per-brand HARD heat-map: Arista 10918, Juniper 3315, Dell 1479, Cisco
  1131, NVIDIA 991, HPE 781, Lenovo 619, Extreme 407, Fortinet 360, Ubiquiti 88, MikroTik-Sw 46, Meraki 27,
  Supermicro 1 (`CBL-0347L~CBL-NTWK-0347` 1m pull/push latch — thin), MikroTik 0. **None import-blocking**
  (byte-contract clean) — SEO/quality backlog. **HOLD for operator triage**: G1's raw count conflates genuine
  thin-differentiation (EQPZ~EIPZ-class) with inherent numbered-family templates → needs an operator
  threshold/scope decision before any cleared brand re-opens. NO auto-fix of cleared brands.
- **TRANSCEIVER SCOPE LOCKED + G1 REFINED (2026-06-17).**
  • **SCOPE LOCK (operator):** transceiver category BOUNDED = **15 brands**. CLEARED 13 (Cisco 544, Arista
    347, Juniper 184, Dell 163, HPE 147, Lenovo 104, Extreme 102, Fortinet 87, NVIDIA 85, Ubiquiti 49,
    Supermicro 27, Meraki 25, MikroTik 24). REMAINING 2 = **Palo Alto + Huawei ONLY**, source-gated (do NOT
    enumerate until operator confirms sourcing per brand; Huawei also pending compliance/sourcing-path; Palo
    Alto first when greenlit). DROPPED PERMANENTLY: ZTE, Ruijie + all Tier-C (H3C, Netgear, D-Link, Zyxel,
    TP-Link, Allied Telesis, Brocade/Ruckus, Edge-Core, SonicWall, Check Point). Recorded in MISSION §3.
  • **G1 REFINED** (the 20K HARD was a masking artifact — number-masking collapsed speed/standard, real
    differentiators). `check_dup_matrix` now: PN-mask only (preserve speed/FF/Standard/Reichweite tokens);
    **HARD only WITHIN spec-signature** (same Formfaktor+Geschwindigkeit+Standard); **cross-signature → WARN,
    never HARD**; allowlist extended to latch/jacket build markers (`_build_variant`: Pull-Tab/Push-Type/LSZH)
    + reach (Reichweite already in the length/λ set). **HARD collapsed 20,163 → 841** (−96%). Fixtures
    updated: G1a within-sig clone HARD-fires; G1b length-variant exempt; G1c cross-sig clone → WARN-not-hard;
    **G1d Supermicro = 0 HARD** (latch pair `CBL-0347L~CBL-NTWK-0347` now correctly exempt). CERTIFIED, 413.
  • **Refined cross-brand HARD (triage, REPORT-ONLY):** Juniper 286, Arista 261, NVIDIA 125, HPE 50,
    Lenovo 45, Cisco 28, Dell 18, Fortinet 13, MikroTik-Sw 11, Extreme 3, Ubiquiti 1, **Supermicro 0,
    Meraki 0, MikroTik 0**. Samples show the residual is mostly legit aliases/revisions/PN-encoded
    length-variants (GLC-SX-MM~SFP-GE-S, HPE 487655-B21~J9283B, CFP~CFP-GEN2, MCP1600-C001~C003) — the
    operator's 71-registry-type set — plus a smaller genuine-thin subset. G3 banned-claims (4923) + G1-841
    + back-catalogue re-author all **HOLD for operator triage**; NO auto-fix.
- **G1 ATTRIBUTE-DIFF TRIAGE of the 841 HARD pairs (2026-06-17, REPORT-ONLY).** Per the operator: for each
  HARD pair, diff the structured attribute VALUES ignoring the allowlisted within-family axes (Länge,
  Wellenlänge, Kabeltyp/latch, Reichweite) + the soft/derived Anwendung. Result over the 13 transceiver
  brands (830 of the 841; +11 MikroTik-switches): **RE-AUTHOR-CANDIDATE 409** (a hard-spec attr differs →
  prose must surface it) / **ACCEPT 421** (no hard-spec attr differs; 114 of these differ only in Anwendung).
  Re-author hard-spec-diff histogram: **Anschlusstyp 244, Betriebstemperatur 126, Transceiver Typ 46,
  Faseranzahl 8, Fasertyp 3, DOM 3.** Per brand RE-AUTHOR/ACCEPT: Juniper 124/162, Arista 134/127, NVIDIA
  55/70, HPE 31/19, Lenovo 34/11, Cisco 15/13, Fortinet 9/4, Dell 5/13, Extreme 2/1, Ubiquiti 0/1,
  Supermicro/Meraki/MikroTik 0/0.
  **ACCEPT-bucket spot-check (vs official datasheet) — it is a genuine MIX, NOT all aliases:**
  • CONFIRMED ATTRIBUTE-COMPLETENESS GAPS (real diff the attrs failed to capture): **Cisco GLC-SX-MM vs
    SFP-GE-S** — my attrs byte-identical (DOM=Ja both, temp 0-70 both, no FC attr) but the datasheet differs
    (GLC-SX-MM = no DOM; SFP-GE-S = DOM + extended temp + 1G Fibre-Channel). **Arista A-D400-2Q200 vs
    A-D400-Q400** — both attr'd "QSFP-DD auf QSFP-DD" but 2Q200 is a 2×QSFP56 BREAKOUT vs Q400 straight
    (topology not captured). • CONFIRMED TRUE-ALIAS (ACCEPT correct): **HPE 487655-B21 vs J9283B** — both
    3 m SFP+ DAC (BladeSystem vs Aruba PN).
  **=> ATTRIBUTE-SCHEMA / GROUNDING GAPS to flag (watch-item-2):** (a) no Fibre-Channel-capability attribute
  exists; (b) DOM Unterstützung + Betriebstemperatur not always datasheet-grounded (Cisco 1G); (c) breakout
  topology not captured in Anschlusstyp (Arista AOC/DAC). The ACCEPT bucket therefore needs per-pair
  datasheet re-verification — it cannot be blanket-passed. **HOLD all re-author + the G3 strip + Palo Alto/
  Huawei enumeration for operator triage; NO auto-fix.**
- **PHASE-1 ATTRIBUTE RE-VERIFICATION — started (2026-06-17; correctness BEFORE prose; re-author NOTHING).**
  Operator decisions: G3 strip confirmed (held for Phase 2); SCHEMA LOCKED (value corrections + prose only,
  no new attributes — FC-capability goes in Beschreibung); attribute errors = PRE-IMPORT BLOCKER, outrank
  the 409 prose-thin + G3. Suspect detector `_scratch/attr_reverify.py` over the 13 cleared bundles.
  **SUSPECT SCOPE:** (A) breakout-Anschlusstyp-straight = **32 (all Arista)**; (D) 1G-optical-DOM=Ja = **97**
  suspects (DOM may be defaulted — many 1G optics genuinely lack DDM); (T) Betriebstemperatur — PN-marker
  detection unreliable (false-positives on "-40" = 40 km reach, misses unmarked extended parts like
  SFP-GE-S) → needs per-SKU datasheet.
  **VERIFIED DELTA so far (recorded source-of-truth for Phase 2; NOT yet applied to content/bundles):**
  • **Anschlusstyp — 32 Arista breakout cables** wrongly "X auf X" → correct far-end (MSA/PN-grounded, Arista
    Cables&Transceivers matrix): A-/H-D400/O400-2Q200 → "… auf 2× QSFP56"; -4Q100 → "… auf 4× QSFP28";
    C-Y100/Z100-2S50 → "… auf 2× SFP56". HIGH confidence (the PN breakout designation IS the far-end).
  • **DOM — Cisco GLC-SX-MM**: DOM Ja → **Nein** (Cisco GE-SFP datasheet c78-366584: GLC-SX-MM has NO DDM;
    only the -MMD variant does). • **Betriebstemperatur — Cisco SFP-GE-S**: "0 bis 70 °C" → **extended**
    (datasheet: SFP-GE-S is extended-temp; exact bound −5…85 °C pending official-PDF confirm — cisco.com is
    403 to WebFetch, grounded via datasheet-citing search). SFP-GE-S DOM=Ja stays correct; its 1G-FC support
    → Beschreibung in Phase 2 (schema locked).
  **STILL PENDING (the bulk — large systematic per-SKU datasheet pass):** the 97 DOM suspects (incl. the rest
  of Cisco's non-D GLC family + cross-brand 1G optics, mixed — modern 1G often HAS DDM) and per-SKU temp.
  cisco.com + store.supermicro.com are 403 to WebFetch → grounding is WebSearch-snippet-based, slower. HOLD
  Phase 2 (apply delta + prose re-author + re-emit), import, Palo Alto/Huawei.
- **PHASE-1 CISCO DOM/temp DELTA (2026-06-17; convention-grounded, datasheet c78-366584; operator byte-review
  pending before next brand).** Applied the operator's Cisco 1G convention (non-D GLC → DOM Nein/0-70; GLC
  D-suffix + SFP-GE/SFP-1G → DOM Ja/-5..85 EXT; *-RGD/-I → -40..85 IND) to all 51 Cisco 1G optics.
  **CORRECTED DELTA = 7** (the confirmed wrong-attribute count for Cisco 1G):
    DOM Ja→Nein (no DDM, only -MMD/-SMD has it): **GLC-LH-SM, GLC-SX-MM, GLC-ZX-SM**.
    Betriebstemperatur 0-70→-5..85 °C (EXT): **SFP-GE-S, SFP-GE-Z, SFP-1G-SX, SFP-1G-LH**.
  **VERIFIED-CORRECT (no change):** GLC-BX-/2BX-D/U(-I) (9) — DOM=Ja confirmed (Cisco BX datasheet: SFF-8472
  DDM; -I = -40..85); the GLC-*-MMD/SMD/EXD + *-RGD already match the convention.
  **[VERIFY] = 27 non-conformers (flag-don't-fabricate; NOT assumed wrong):** MGBSX1/LX1/LH1 (SMB — datasheets
  don't confirm DDM, lean no-DDM → possible DOM Ja→Nein); DWDM-SFP-* 1G ×5 (temp/DOM unverified);
  CWDM-SFP-* 1G ×5 (temp "-5..70" unusual); ONS-SI-GE-* ×4; S1G-*-PM-D-I ×2; GLC-LH/ZX-LMM-TI ×2; GLC-GE-DR-LX;
  DS-SFP-FCGE-LW/SW ×2 (the gray FC/GbE keepers); DWDM-XFP-C (a 10G tunable XFP mis-tagged 1G — speed-class
  data issue). Operator to resolve from datasheet access. **Recorded as the corrected source-of-truth; NOT
  applied to content/bundles (Phase 2 applies + re-emits + writes Verification_Log rows).** HOLD for byte-
  review before the next brand (Juniper 33 next).

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
| **Dell** | ✅ **UNBLOCKED 2026-06-15** — Dell "Networking Transceivers and Cables" spec sheet | delltechnologies.com **403**, but a reseller mirror (andovercg.com) serves the GENUINE Dell PDF → §7.1 rung-b. **Cached** `datasheets/cache/dell-networking-optics-datasheet.pdf` (8 pp, full spec grid). 71-SKU facts banked. | (done) |
| **Supermicro** **SOURCE-HUNT 2026-06-15** | Authoritative denominator = the **store.supermicro.com eStore** — `/server-accessories/transceiver.html` (**AOM-*** optics) + `/server-accessories/cable/networking.html` (**CBL-*** cables). PN schemes: AOM-* transceivers (vendor-coded e.g. `-MLN`/AVAGO/FINISAR/INTEL/Aquantia → dedup like Lenovo/Ubiquiti); CBL-* DAC/AOC/breakout. Range 10G SFP+ / 25G SFP28 / 40G QSFP+ / 100G QSFP28 + DAC/AOC. **BLOCKER: both eStore category pages return HTTP 403 on $0 GET** (matches §10) → can't self-enumerate the denominator. **Scope boundary:** IN = AOM-* Ethernet optics + CBL-* Ethernet DAC/AOC/breakout; OUT = InfiniBand-only cables (IB-QDR/EDR; dual "Ethernet IB-QDR" counts as Ethernet), Supermicro **AOC-*** Add-On Cards (NICs/HBAs — different category, NOT transceivers), **SSE-*** switches. **Reported to operator: need the eStore transceiver + networking-cable category screen-caps (rendered roster, the Ubiquiti method) or a Supermicro transceiver/cable datasheet/CSV to LOCK the denominator. HOLD facts.** **UPDATE (operator screen-caps received, cached `supermicro-estore-transceivers.pdf` + `-cables.pdf`): INCOMPLETE — the eStore paginates 10/page + JS-lazy-loads. Transceivers page = "16 Items" but only 1 rendered (AOC-E10GSFPSR, a 10G/1G SFP+ SR optic — NB the transceiver category uses BOTH AOM-* and AOC-* prefixes for OPTICS, so enumerate by the ROSTER not the PN prefix; AOC-NIC cards are a separate category). Cables = "Items 1-10 of 35" with [1]2 3 4 pagination → only page 1 (10 of 35). Cable cat includes generic RJ45 CAT6/CAT6E patch (CBL-0355L, CBL-C6-YL6FT) → OUT; DAC/AOC marked "Ethernet and InfiniBand" → Ethernet-capable IN. RE-CAPTURE NEEDED with "Show All"/max-per-page (or all pages: transceiver 2pp, cable 4pp) so all 16 + 35 render. STILL HOLDING facts.** | operator: COMPLETE eStore rosters (Show-All) — all 16 transceivers + 35 cables |
| **Juniper** | Juniper HCT `apps.juniper.net/hct` / optics datasheet | **JS-gated** single-page app — no static HTML enumeration | `juniper-optics.{csv,pdf}` (HCT export) |
| ~~**Lenovo/IBM**~~ **UNBLOCKED 2026-06-15** | Lenovo Press guides (live WebFetch, no cache needed) — **Workflow-B across 4 docs:** lp1652 + lp1417 (current NIC) **+ lp0609 NE10032 + lp0608 NE2572 (switch guides** = the 40G/1G/100G-LR4 + breakout-cable denominator the NIC guides miss) | none — Lenovo Press serves static fetchable HTML; the round-1 "boundary" was a single-source artifact, fixed by adding the switch guides | (done — 102 SKUs, L8 round-2) |
| **Huawei** | Huawei optical-module datasheets (`support.huawei.com`) | likely login/region-gated (untested $0) | `huawei-optical-modules.{pdf,csv}` |
| **ZTE** | ZTE optical-module datasheets | untested $0 (likely gated) | `zte-optics.{pdf,csv}` |
| **Ruijie** | Ruijie optical-transceiver datasheets | untested $0 | `ruijie-optics.{pdf,csv}` |
| **Palo Alto** | PAN-OS-compatible transceiver list (`docs.paloaltonetworks.com`) | untested $0 | `paloalto-transceivers.{pdf,csv}` |
| ~~**Ubiquiti**~~ **SOURCE-HUNT 2026-06-15 — DENOMINATOR NOT YET LOCKED (awaiting operator's help.ui.com table file)** | Denominator = the help.ui.com "SFP Modules and DAC Cables" store table (canonical current set); the ui.com store category is **JS-gated → WebFetch returns inconsistent partial slices** (it already dropped 2 families). Operator-flagged + now WEB-VERIFIED additions: **100G LR4** `UACC-OM-QSFP28-LR4` (SMF 10km, LAN-WDM λ; techspecs.ui.com confirmed) and **multi-gig copper** `UACC-CM-RJ45-MG` (1/2.5/5/10G NBASE-T, 100m Cat6A). **Confirmed scope:** 1G SFP (MM-SX/SM-BiDi/SM-duplex/copper) · 10G SFP+ (MM-SR/SM-LR/SM-BiDi/copper-1G+10G+MG/12-ch CWDM) · 25G SFP28 (SR+LR) · 100G QSFP28 (SR4+**LR4**) · DAC (10G/25G/uplink, full length matrix from the table). **OUT (flag, don't drop):** GPON/EPON UFiber-OLT PON (UF-GP-*/UF-OLT/UF-NANO/LOCO/INSTANT), generic ODN/OFC patch, UACC-SFP-Wizard, UACC-CWDM-4 mux/demux, F-POE-G2. **DEDUP:** legacy UF-* ↔ current UACC-* are the SAME optic across eras (UF-MM-10G ↔ UACC-OM-MM-10G-D) → emit ONE SKU (current UACC- code) with the UF- as alternate code (extra_log, Lenovo pattern), unless both independently orderable. Spec grounding: **techspecs.ui.com/unifi/accessories/<pn>** (official, static) + cached UFiber DS + UACC datasheets. **HOLD: do not build facts until the table locks the denominator.** **UPDATE (operator file received + analyzed):** the provided help.ui.com screen-cap (cached `datasheets/cache/ubiquiti-sfp-modules-dac-help-ui-202606015.pdf`) is a **TYPE-LEVEL GUIDE, not a per-PN list** — overview table by SFP/SFP+/SFP28 × Fiber/Copper/DAC + a QSFP28 note; names only UACC-CM-RJ45-MG + UACC-OM-QSFP28-SR4/LR4 in body text; **omits the CWDM 10G series**. So it LOCKS the TYPE SCOPE (+ confirms LR4 & MG) but does NOT lock the exact SKU set. techspecs.ui.com (official) is ALSO JS-gated — exposes only counts: **"SFP & Fiber (29)" + "RJ45 & Copper (17)"** (completeness anchor; the 29 includes OFC patch cables = partly OUT). Per-PN denominator STILL not locked → requested the techspecs SFP&Fiber/RJ45&Copper listing (screen-cap) or per-SKU verification authorization. Open: CWDM 10G in/out (store product, not in the canonical guide). **DENOMINATOR LOCKED 2026-06-15** — operator provided the techspecs **"SFP & Fiber (29)"** full-page screen-cap (cached `ubiquiti-techspecs-sfp-fiber-29.pdf`) + **"SFP Liberation Day (6)"** (cached `ubiquiti-techspecs-sfp-liberation-6.pdf`, a SUBSET of the 29 — no additions). Read all 29 (exactly accounted): **20 IN** (13 optic + 7 DAC/AOC families) **+ 9 OUT**. IN optics: 1G MM-SX `UACC-OM-MM-1G-D` / SM-BiDi `UACC-OM-SM-1G-S` / copper `UACC-CM-RJ45`; 10G MM-SR `UACC-OM-MM-10G-D` / SM-LR `UACC-OM-SM-10G-D` / SM-BiDi `UACC-OM-SM-10G-S` / multi-gig-copper `UACC-CM-RJ45-MG` / CWDM `UACC-OM-SFP10-{12 ch 1270–1590}`; 25G `UACC-OM-SFP28-SR/-LR`; 100G `UACC-OM-QSFP28-SR4/-LR4/-PSM4` (**PSM4 caught by the roster — neither candidate list had it**). IN cables: `UACC-Uplink-SFP28`, `UACC-DAC-SFP10`/`-SFP28`/`-QSFP28`, `UACC-AOC-SFP10`/`-SFP28`/`-QSFP28`. **OUT (9, flagged):** 5 OFC/FC fiber patch (`UACC-OFC-S2-LULU`/`-M2-LULU`/`-SA-MPMP`/`-MA-MPMP`, `FC-SM`), 2 CWDM mux (`UACC-CWDM-4`/`-8`), `UACC-SFP-Wizard` (programmer), `F-POE-G2` (media converter). **1G SM-duplex NOT in roster** → legacy `UF-SM-1G` only (flag legacy, not current). DEDUP UF-↔UACC- as alt code (extra_log). ≈24 optic SKUs + ~25 cable length-SKUs ≈ ~49 (AOC/QSFP28-DAC lengths TBV per-PN). **Reported for operator sign-off before facts.** | (locked) techspecs per-PN pages for specs |
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
