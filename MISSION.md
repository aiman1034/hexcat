═══════════════════════════════════════════════════════════════════════
HEXCAT — MISSION, METHODS & VERIFICATION CHARTER  (v3 — full catalog)
═══════════════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────────────
§0 — RUN THIS AT THE START OF EVERY RESPONSE (before any action)
───────────────────────────────────────────────────────────────────────
1. MISSION FOCUS — Am I working toward best-ideal-data for the FULL catalog
   (ALL categories × ALL brands) → imported live on hexwaren.de? Or have I
   narrowed to one category/brand and forgotten the rest? (Failure #1/#2)
2. ANCHOR — What does PROJECT_AUDIT.md + the MASTER MANIFEST say is the
   active task and the next concrete step? State it in one line.
3. PRIORITY — Is my planned action the highest-priority mission work (core
   brands/categories first), or a rabbit-hole? Is a CORE brand sitting parked
   that I should do first? (Failure #5)
4. STALE-LABEL — Am I about to trust a "blocked"/"not groundable" note
   without re-verifying it? Re-verify first. (Failure #4)
5. GROUNDING — Am I about to write ANY uncited/fabricated value? STOP — flag
   the gap (complete:false) instead. Fabrication is the worst failure.
6. VERIFICATION — Am I about to self-declare "green" without the full 8-layer
   gate AND the operator's independent audit? STOP — that is NOT done.
   (Failure #3)
If any check fails, correct course BEFORE acting. Re-state the mission focus +
active task, then proceed.

───────────────────────────────────────────────────────────────────────
§1 — THE MISSION & THE END GOAL
───────────────────────────────────────────────────────────────────────
END GOAL: every part number in Hexwaren's catalog — EVERY CATEGORY × EVERY
BRAND × EVERY SKU — imported and LIVE on hexwaren.de through JTL (and onward
to eBay.de via eazyAuction + Google Merchant). The deliverable is not "nice
CSVs" — it is product data that imports cleanly into JTL-Wawi and goes live.

Data must be: (1) 100% datasheet-GROUNDED, (2) byte-exact to the locked
schemas so Ameise imports without error, (3) COMPLETE (every SKU; gaps
flagged, never faked), (4) correct German B2B voice. "Best ideal data" = a
reseller customer AND a manufacturer engineer both find nothing wrong, AND it
imports into JTL first try.

Hexwaren = German B2B reseller of NEW-SEALED ORIGINAL hardware. Refurb/
compatible sellers are NEVER competitors and never a source of truth.

DEFINITION OF DONE (per SKU): grounded → authored → passes the full 8-layer
gate (§8) → completeness record exists → bundle emitted → operator audit
clean → Ameise-import-ready. Until a SKU is import-ready AND accounted for in
the master manifest, it is NOT done.

───────────────────────────────────────────────────────────────────────
§2 — THE DATA FLOW / IMPORT PATH
───────────────────────────────────────────────────────────────────────
hexcat → 7-file Ameise CSV bundle → 5-step Ameise import into JTL-Wawi →
JTL-Shop (hexwaren.de) LIVE → eBay.de (eazyAuction) + Google Merchant.
File → import step: 1 Main→article master · 2 Attributes→Wertliste · 3
PlatformFlag→platform TRUE · 4 Prices→Netto-VK · 5 Condition→new · 6 FAQ→FAQ+
schema · 7 Verification_Log→INTERNAL (not imported). Any byte that breaks
Ameise (delimiter/BOM/decimal/column count/order/UTF-8) = failed import =
mission failure. The gate (§8 L1) guarantees clean import.

───────────────────────────────────────────────────────────────────────
§3 — SCOPE: ALL CATEGORIES × ALL BRANDS  (do NOT narrow this)
───────────────────────────────────────────────────────────────────────
CATEGORIES — confirmed worked: Transceivers/Optics (+ DAC/AOC/MPO cables),
  Switches. Expected across the catalog (CONFIRM via each brand's actual
  product lines, don't assume): Routers, Firewalls/Security, Wireless
  (APs/WLAN controllers/antennas), NICs/Adapters, Power supplies, Modules/
  Line cards, Servers/Compute, Cables & accessories, Mounting/rack kits.
BRANDS — core FIRST: HP/HPE/Aruba, Cisco, Juniper, Arista. Then the full
  stocked set (touched: Meraki, Fortinet, NVIDIA, MikroTik; expansion: Dell,
  Lenovo, Palo Alto, Ubiquiti, Supermicro; off-core/optional: Huawei, ZTE,
  Ruijie). Brand scope GROWS with stocking — inventory it, don't hard-code.

*** STEP 0 — BUILD THE MASTER CATALOG MANIFEST (do NOT stall on scope) ***
The DENOMINATOR = the brand list (HPE/Cisco/Juniper/Arista core + the
expansion brands) × the categories EACH brand actually makes (from the
brand's own product lines). Build the manifest from THAT — it does NOT wait on
any external input. A JTL-Wawi export / live-hexwaren.de reconciliation is
OPTIONAL (a nice-to-have to avoid re-doing the ~525 already-live SKUs), NEVER
a blocker. Record as the MASTER MANIFEST in PROJECT_AUDIT (category × brand →
status: not-started/facts/authored/emitted/audited/imported). Mission = 100%
of the manifest reaches "imported". This manifest is the scoreboard.

───────────────────────────────────────────────────────────────────────
§4 — THE GROUNDING LAW (1000% rule — SUPREME, overrides everything)
───────────────────────────────────────────────────────────────────────
Every spec + prose claim web-verified against the OFFICIAL MANUFACTURER
datasheet BEFORE writing. No pattern-matching. No invented specs.
  • No authoritative source → tag [VERIFY] or OMIT. Never guess.
  • FLAG-DON'T-FABRICATE is absolute: gaps flagged (complete:false), NEVER
    filled. A faked value is the worst possible failure here.
  • Every grounded fact citable (datasheet URL / cited cache YAML); every
    batch carries a Verification_Log.
  • Manufacturer-unpublished-attribute exception (e.g. switch weights, §7.6):
    a distributor-published value, cited + cross-checked, allowed ONLY for an
    attribute the manufacturer genuinely doesn't publish — NOT a general
    license for third-party data.

───────────────────────────────────────────────────────────────────────
§5 — THE RECORD FILES (so you NEVER forget / re-do work)
───────────────────────────────────────────────────────────────────────
READ-FIRST: MISSION.md (this) · PROJECT_AUDIT.md (master state §4/§5 tables,
  §9 changelog, §10 SOURCE MANIFEST, §11 status + the MASTER MANIFEST; READ
  FIRST, FLAG when edited) · CLAUDE.md.
SCHEMAS: SWITCHES_SCHEMA_PROPOSAL.md · the transceiver schema doc · (per new
  category: {CATEGORY}_SCHEMA.md, signed off before its first batch).
GATE: validate.py + consolidated gate.py · anti-blind-spot fixtures dir.
PIPELINE: constants.py, rules.yaml, config.py, models.py, reconcile.py,
  intake.py, assemble.py.
CACHE — datasheets/cache/: {brand}_{category}_facts.json ·
  {brand}_{category}_completeness.yaml · cited provenance YAMLs (e.g.
  mikrotik-switch-weights.yaml).
AUTHORS: {brand}_{category}_author.py / _facts.py.
OUTPUT: output/Hexwaren_{Brand}[_{Category}]_stage3_{commit}.zip (all 7 files
  category-tagged so a brand's categories never collide).
RULE: before declaring anything missing/blocked, CHECK THESE FILES.

───────────────────────────────────────────────────────────────────────
§6 — THE SCHEMA FRAMEWORK (category-agnostic core + per-category schemas)
───────────────────────────────────────────────────────────────────────
CATEGORY-AGNOSTIC (identical every category): 7-file contract; Main 19-col
exact order [Artikelnummer;Artikelname;Kurzbeschreibung;Beschreibung;
URL-Pfad;Artikelgewicht;Versandgewicht;HAN;Hersteller;Versandklasse;
Verkaufseinheit;Titel-Tag (SEO);Meta-Description (SEO);Kategorie Ebene 1;
Kategorie Ebene 2;Kategorie Ebene 3;Überverkauf Plattform Hexwaren;
Bestandsführung aktiv;Überverkäufe möglich] (UTF-8 BOM, ';', CRLF;
HAN=Artikelnummer; URL={slug}/{sku-lower}; last 3 = TRUE/Y/Y); Attributes
8-col LONG [Artikelnummer,GTIN,Attributgruppe,Attributname,Attributwert,
Sortiernummer,Datentyp (sonst automatisch ermittelt),Attributart] (BOM, ',',
every row Wertliste/Attribut); PlatformFlag=TRUE; Prices ';' no-BOM
"Artikelnummer;Netto-VK" German-decimal best-effort-0,00; Condition template;
FAQ "Q||A ## Q||A" 3–10; Verification_Log. Content floors: Kurz 2×<p>/40–80w;
Beschr 3×<p>/90–175w ending gender-inflected "Originaler/Originales {Brand}-
{noun}"; Titel ≤60 "| Hexwaren"; Meta 140–200. German B2B voice, no marketing/
puffery. Banned hard-fail: ["sofort lieferbar/verfügbar","Versand am selben
Werktag","ab Lager Deutschland","B2B-Versand aus Deutschland","Rechnungskauf",
"neu und versiegelt","voller Herstellergarantie"]. Brand→Hersteller/slug:
HP/HPE/Aruba→HP/hpe-aruba; Cisco→cisco; Juniper→juniper; Arista→arista;
+lower-cased brand.

PER-CATEGORY (each defines its own, same rigor): Attributgruppe · Kat L2 · Kat
L3 set · attribute set + fixed Sortiernummer order · required attributes ·
category SEMANTIC checks. Built:
 ▸ TRANSCEIVERS — Attributgruppe "Transceivers & SFP Modul" (NO final e); L1
   Netzwerk & Infrastruktur / L2 "Transceivers & SFP Module" (WITH e) / L3 =
   locked form-factor set (RECONCILE 22-vs-24 to authoritative). 14 attrs:
   Formfaktor, Geschwindigkeit, Transceiver Typ, Faseranzahl, Fasertyp,
   Anschlusstyp, Länge, Kabeltyp, Wellenlänge, Anwendung, Reichweite, DOM
   Unterstützung, Betriebstemperatur, Standard.
 ▸ SWITCHES (Rule-7) — Attributgruppe "Switch"; L2 "Switches"; L3 = 6 tokens
   (Unmanaged Switch | Smart-Managed Switch | Managed Switch (L2) | Managed
   Switch (L3) | Data-Center-Switch | Industrie-Switch). 15 attrs: Switch-Typ,
   Layer, Portanzahl, Port-Konfiguration, Port-Geschwindigkeit, Uplink-Ports,
   PoE, Switching-Kapazität, Durchsatz, Bauform, Stromversorgung, Kühlung,
   Stacking, Betriebstemperatur, Anwendung (8/9 Exp allowed-absent,
   Sortiernummer GAPS preserved). Required-8: Switch-Typ, Layer, Portanzahl,
   Port-Konfiguration, Port-Geschwindigkeit, PoE, Bauform, Anwendung.
   Bauform=housing not Formfaktor; Port-Geschwindigkeit from dominant user
   port not mgmt. Checks S.1–S.6.
 ▸ TO BUILD (each: {CATEGORY}_SCHEMA.md → operator sign-off → first batch):
   Routers, Firewalls/Security, Wireless (APs/controllers/antennas), NICs/
   Adapters, PSUs, Modules/Line cards, Servers/Compute, Cables/Accessories.
   NEVER author a new category without its locked schema + semantic checks +
   anti-blind-spot fixtures.

───────────────────────────────────────────────────────────────────────
§7 — THE METHODS / PLAYBOOK (apply across categories)
───────────────────────────────────────────────────────────────────────
7.1 SOURCE-REVERIFICATION LADDER (never trust a stale "blocked" label): a) $0
   httpx, use extract_tables NOT extract_text (hid Extreme's rows); b) miss →
   web search + alternates (manufacturer PDFs, per-SKU datasheets, distributor
   spec pages, hardware/compat guides — unblocked Juniper via optic-modules
   PDF + MikroTik weights via distributors); c) fallback → scoped browser
   (PUBLIC manufacturer/distributor pages, no auth); d) only then → flag
   blocked with the SPECIFIC reason + unblock input.
7.2 HARVEST: enumerate ALL SKUs per brand×category. Workflow A (odd SKUs at
   batch end), Workflow B (AFTER batch, re-search missed SKUs). EOL/EOS = flag
   informational, NEVER drop.
7.3 FACTS PARSER (deterministic → facts JSON): repair space-wrapped PNs; split
   length-families (1 row→N SKUs); capture multi-PN/alt codes (numeric/legacy/
   Avaya-AA/MGBIC); derive Faseranzahl.
7.4 LANE-AWARE WAVELENGTHS (optics): λ from IEEE standard, lane-aware —
   100G-LR4 LAN-WDM ≠ 40G-LR4 CWDM4; SR 850nm; LR/PSM4 1310; -T copper.
7.5 SOURCE-CORRUPTION GUARD (flag-don't-fabricate): shifted cells (type from
   PN not row), cable-type-from-PN, numeric-only ambiguous lengths → flag/
   exclude.
7.6 SWITCH-SPECIFIC: combo "C" groups → Port-Konfiguration + Portanzahl (S.6);
   env-first L3 (Industrie=DIN-rail/outdoor; Data-Center=≥25G; extended-temp
   alone insufficient; else mgmt class). WEIGHTS (mfr-unpublished): distributor
   cited → triangulate ≥2–3 (dateks net+gross › dedicated store › distributor);
   DETECT templated defaults (value repeated across unrelated SKUs=placeholder,
   discard); PHYSICAL-REASONING override (PoE ≥ non-PoE sibling); disagreement
   flag |a−b|/min(a,b)>0.40; Versand>Artikel (published gross else ×1.20
   DERIVED+marked); per-weight citation; floor 0.15kg.
7.7 SEO: Titel ≤60 "| Hexwaren"; Meta 140–200; FAQPage schema; depth where
   competitors thin; DWDM/CWDM channel SKUs must NOT share near-identical
   Beschreibung.
7.8 COMPLETENESS RECORD per brand×category: grounded count, gaps flagged
   (complete:false), citation per source.
GENERALIZE: a new technique → build it as tool + gate check + fixtures +
document here.

───────────────────────────────────────────────────────────────────────
§8 — THE VERIFICATION REGIME (STRICT, MULTI-LAYER — *** THE BACKBONE ***)
───────────────────────────────────────────────────────────────────────
NOT done until it passes EVERY layer. The gate is the ONLY path to a ZIP — NO
emit unless 0 violations across ALL layers. The gate PRINTS a per-layer PASS/
FAIL report every run. Multiple INDEPENDENT methods must agree before a value
is trusted — a single source is a hypothesis, not a fact.
  L1 CONTRACT — DATA STRUCTURE IS SACRED. Byte-exact schema (files/columns/
     order/delimiter Main ';' Attributes ','/UTF-8 BOM/CRLF/German decimals/
     Attributgruppe/category tokens/Sortiernummer-gaps preserved/cross-file SKU
     parity). HARD-FAIL any deviation — NO ZIP emits unless byte-exact (a
     structural break costs the operator an eternity to fix). L1 ALSO includes
     two silent-corruption guards, EACH with its own NEGATIVE fixture it MUST
     flag + a POSITIVE it passes:
       • HTML WELL-FORMEDNESS — every Kurz/Beschr/FAQ HTML parses (balanced
         tags, valid entities); malformed HTML → hard-fail.
       • UTF-8 / UMLAUT INTEGRITY — file decodes as valid UTF-8 WITH BOM; ZERO
         mojibake (scan for Ã/Â/ï¿½ and the replacement char); ä/ö/ü/ß intact.
         Known risk: Mac+Excel corrupts the BOM + umlauts — the gate MUST catch
         it. These silent modes must be IMPOSSIBLE to emit. Guarantees Ameise import.
  L2 CONTENT — floors; banned-phrase hard-fail; B.1–B.8. B.8 = inline-
     template-artifact linter scanning EVERY content field incl Beschreibung +
     FAQ (a field-coverage gap here caused a false-green; ALL fields,
     permanently).
  L3 SEMANTIC — per-category checks (transceiver consistency; switch S.1–S.6;
     each new category defines its own).
  L4 GROUNDING — every spec + value CITED; any uncited claim fails; [VERIFY]/
     omit otherwise.
  L5 PLAUSIBILITY — physical sanity (weight bands by class; port counts vs PN;
     λ vs standard; memory platform-compat); cross-source triangulation with
     the /min disagreement flag; templated-default + corruption detection.
  L6 COMPLETENESS — every SKU per brand×category accounted (Workflow-B); gaps
     EXPLICITLY flagged; count reconciles to the completeness record AND the
     master manifest.
  L7 ANTI-BLIND-SPOT (the verifier verifies ITSELF) — for EVERY check, a
     NEGATIVE fixture it MUST flag + a POSITIVE it must pass. A check blind to
     a field/case FAILS its own fixture in CI. (B.8 once passed its own output
     while blind to 2/3 fields.) A check with no negative fixture is untrusted.
  L8 INDEPENDENT RE-AUDIT — the operator (separate QA) re-runs an INDEPENDENT
     validator on the emitted ZIP + spot-checks grounding vs FRESH sources.
     Self-reported "green" is NEVER trusted alone. Hand off clean self-
     contained bundles + completeness records.
When two methods disagree, the data is NOT done. Cite everything. Verify again
when in doubt.

───────────────────────────────────────────────────────────────────────
§9 — OPERATING RULES
───────────────────────────────────────────────────────────────────────
- AUTONOMOUS GRIND: don't stop on source-blocks — run the §7.1 ladder, unblock
  what's reachable, flag what's genuinely blocked, CONTINUE. Don't idle.
- CHECKPOINT if you'd run low mid-task — sharp resume point in PROJECT_AUDIT
  §9. A half-built brand commits NOTHING. Bank verified facts as checkpoints.
- NEW ERROR CLASS → fix tool + add gate check + its fixtures + BACK-APPLY to
  all brands/categories. Every fix permanent.
- READ PROJECT_AUDIT.md + MISSION.md FIRST every session; FLAG when you edit
  PROJECT_AUDIT.md. Non-negotiable.
- $0 LAW: generation through Claude Code (Max), NEVER paid API credits.
- Browser scoped-approved for PUBLIC manufacturer/distributor source pages,
  all brands (no auth, flag-don't-fabricate). Not a blanket lift.
- Operator runs Ameise import + independently audits ZIPs (L8).

───────────────────────────────────────────────────────────────────────
§10 — CURRENT STATE & WORK ORDER
───────────────────────────────────────────────────────────────────────
DONE (emitted; awaiting consolidated-gate + operator L8 audit): Transceivers —
  Cisco 596, Arista 347, HPE 147, Fortinet 87, NVIDIA 85, Meraki 25, MikroTik
  24. Switches — MikroTik 36/36.
EXECUTE IN ORDER:
  0) MASTER MANIFEST — inventory ALL categories × brands × PNs (§3 Step 0).
  1) SOURCE-REVERIFICATION + COMPLETENESS SWEEP across the manifest. Juniper
     FIRST (core; source confirmed: juniper.net optic-modules PDF + per-SKU
     datasheets).
  2) BUILD THE CONSOLIDATED 8-LAYER GATE (§8) + anti-blind-spot fixtures,
     self-tested vs known-good batches AND every negative fixture.
  3) AUTHOR unblocked brands through the gate (core first; Juniper → Extreme →
     expansion; across categories) → ZIPs → operator audit → Ameise import.
  4) Workflow-B completeness pass over already-authored brands.
  5) BUILD REMAINING CATEGORY SCHEMAS (routers, firewalls, wireless, NICs,
     PSUs, modules, servers, cables) — each {CATEGORY}_SCHEMA.md + checks +
     fixtures → then batches.

───────────────────────────────────────────────────────────────────────
§11 — ANTI-DRIFT (your known failure patterns — guard against each)
───────────────────────────────────────────────────────────────────────
Mission = BEST IDEAL DATA for ALL CATEGORIES × ALL BRANDS × ALL SKUs, IMPORTED
LIVE on hexwaren.de via JTL. The whole catalog. Guard against YOUR patterns:
  #1 SCOPE-NARROWING → don't shrink to what's already built; the manifest is
     the scope.
  #2 DRIFT → don't rabbit-hole on one SKU while a core brand/category sits
     unbuilt; re-run §0 each response.
  #3 SELF-GREEN → never declare done without all 8 layers AND the operator's
     audit.
  #4 STALE LABELS → re-verify every "blocked" note (the ladder).
  #5 PARKED CORE BRANDS → core (HPE/Cisco/Juniper/Arista) FIRST, every
     category.
  #6 FABRICATION → never fake to "finish"; flag the gap.
Per SKU: ground → author → gate(8) → completeness → ZIP → audit → import. The
master manifest is the scoreboard; JTL import is the finish line; multi-method
verification is the backbone. Nothing is "done" until grounded, gated, and
imported.
═══════════════════════════════════════════════════════════════════════
