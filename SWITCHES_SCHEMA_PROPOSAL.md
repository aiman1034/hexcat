# Switches — Gold-Slice Schema (Rule-7, ✅ SIGNED OFF 2026-06-14 — LOCKED)

> **Status: APPROVED with 4 amendments (applied below) + 1 confirmed note. LOCKED — authoring may
> proceed (MikroTik switches first), no further sign-off needed unless an amendment proves infeasible.**
> Designed as a faithful analog of the locked transceiver gold-slice so the 7-file JTL-Ameise v5.0
> byte contract, the gate, pricing, the semantic cross-checks, Rule 8/9, and the per-brand pipeline
> all carry over unchanged.
>
> **Sign-off amendments (operator, 2026-06-14):** (1) Attributgruppe = `Switch` (real word, not the
> non-word `Switche`); (2) attribute #5 = `Port-Geschwindigkeit` (not `Geschwindigkeit` — keep it off
> the transceiver Merkmal/Wertliste); (3) L3 stays 6 tokens but with a documented **environment-first
> precedence** + new check **S.5** (single-L3-token determinism); (4) attribute #10 = `Bauform` (not
> `Formfaktor` — off the transceiver Merkmal); (5) confirmed: Switch-Typ (#1) = management class is
> distinct/additive given the environment-first L3 precedence (see §4 note).

---

## 1. What CARRIES OVER unchanged (no decision needed)

- **Byte contract — all 7 files, identical.** Main (19-col `;` BOM CRLF), Attributes (8-col `,` BOM),
  PlatformFlag, Prices (`;` no-BOM, German decimal), Condition, FAQ, Verification_Log. **No new Main
  columns** — switches populate the SAME 19 Main columns; only the Kat-L2/L3 *values* and the
  Attributes *set* differ. The contract generalises with zero schema edits.
- **Content floors:** Kurzbeschreibung 40–80 words / 2×`<p>`; Beschreibung 90–175 / 3×`<p>` ending the
  authenticity closer `Originaler {Hersteller}-…`; Titel-Tag ≤60 chars ending ` | Hexwaren`;
  Meta-Description 140–200 chars; FAQ 3–10 pairs.
- **Banned-language list, Condition template ("Neu, versiegelt"), Verkaufseinheit "Stk",
  Versandklasse, Überverkauf flags** — all identical.
- **Kategorie Ebene 1:** `Netzwerk & Infrastruktur` (shared parent — unchanged).
- **Rule 8 (gold parity), Rule 9 (class-derived Betriebstemperatur), the 8 semantic cross-checks
  B.1–B.8, pricing engine (best-effort, flag 0,00), commit-per-family, per-brand ZIP** — all carry over.
- **Artikelgewicht/Versandgewicht** — switches have a real shipping weight (heavier than optics);
  populated per datasheet as today.

---

## 2. [DECISION] Kategorie Ebene 2 + Attributgruppe

Transceivers use L2 `Transceivers & SFP Module` and Attributgruppe `Transceivers & SFP Modul`
(intentionally **one character** different — JTL needs the group name ≠ the category name).

**LOCKED:**
- **Kategorie Ebene 2:** `Switches`
- **Attributgruppe:** `Switch` (the singular — a real word, and the Modul convention is "singular of
  the last noun": Module→Modul, Switches→**Switch**. Still distinct from the L2 `Switches`. Renders
  as the product-page spec-header so it must be a real word — `Switche` rejected.)

---

## 3. [DECISION] Kategorie Ebene 3 — the locked switch token set

Transceivers lock 24 L3 tokens (form factors). Switches navigate best by **management class** (the
dominant B2B filter); deployment role (access/aggregation/core/DC/industrial) lives in the
`Anwendung` attribute, exactly as transceiver reach/use-case does. **Proposed locked L3 set (6):**

| L3 token | Definition |
|---|---|
| `Unmanaged Switch` | Plug-and-play, no configuration interface |
| `Smart-Managed Switch` | Web-smart / lightly managed (VLAN/QoS via web UI, no full CLI) |
| `Managed Switch (L2)` | Fully managed, Layer-2 (CLI/SNMP, STP/VLAN/LACP) |
| `Managed Switch (L3)` | Fully managed with Layer-3 routing (static/dynamic) |
| `Data-Center-Switch` | ToR/spine/leaf, high-density 25/100/400G, low-latency |
| `Industrie-Switch` | DIN-rail / hardened, extended temperature, often fanless |

Rules carried over: closed set, **"Sonstige" never allowed**; "Stackable"/"PoE"/port-speed are
**attributes**, not L3 tokens. Must stay in lock-step with a new `config/taxonomy/switches.yaml` ⇄
`config/rules.yaml`.

**LOCKED — single-token precedence (amendment 3; wording reconciled to the implemented gate 2026-06-14):**
the 6 tokens mix two axes (environment vs management class), so a managed-L3 DC switch or an industrial
managed switch could match two. **Every SKU resolves to exactly ONE token by this precedence:
ENVIRONMENT/DEPLOYMENT first, then management class** →
(1) `Industrie-Switch` — **DIN-rail/Hutschiene OR outdoor/hardened** (extended operating-temperature
ALONE is NOT sufficient: e.g. CRS504-4XQ-IN is −40/+70 °C but a desktop 100 G unit → Data-Center; the
identical-temp CRS504-4XQ-**OUT** is outdoor → Industrie) →
(2) `Data-Center-Switch` — high-density **≥25 G** (SFP28/QSFP28/QSFP-DD), ToR/spine →
else by management class (3) `Managed Switch (L3)` → (4) `Managed Switch (L2)` → (5) `Smart-Managed
Switch` → (6) `Unmanaged Switch`. Enforced by **S.5** (single-L3 determinism; DIN-rail/Hutschiene ⇒
Industrie) + **S.6** (PN-encoded port groups must appear in Port-Konfiguration — catches consistent
omissions like dropped combo "C" groups). Management class is still stated explicitly on every SKU via
the `Switch-Typ` attribute (so it isn't lost when the token is an environment one).

---

## 4. [DECISION] The switch attribute set (fixed order = Sortiernummer)

Analog of the 14 transceiver attributes. **15 proposed**, fixed order (Sortiernummer = 1-based index).
"Req" = required on every SKU (gate-enforced like transceiver Anwendung/Geschwindigkeit); "Exp" =
expected where applicable (attribute-depth model decides GAP vs PROVABLY_ABSENT).

| # | Attributname | Req/Exp | Example value | Notes |
|---|---|---|---|---|
| 1 | `Switch-Typ` | Req | `Managed` / `Smart-Managed` / `Unmanaged` | management class — additive (see note below) |
| 2 | `Layer` | Req | `L2` / `L2+` / `L3` | switching layer |
| 3 | `Portanzahl` | Req | `28` | total physical ports |
| 4 | `Port-Konfiguration` | Req | `24× 1GbE RJ45 (PoE), 4× 10G SFP+` | the defining spec (analog of Formfaktor) |
| 5 | `Port-Geschwindigkeit` | Req | `1 GbE` (access-port class) | **amendment 2** — distinct Merkmal, NOT transceiver `Geschwindigkeit` (incompatible Wertliste); multi-rate listed |
| 6 | `Uplink-Ports` | Exp | `4× SFP+ (10G)` | when dedicated uplinks exist |
| 7 | `PoE` | Req | `PoE+ (802.3at), 450 W Budget` / `Nein` | always present; `Nein` if none |
| 8 | `Switching-Kapazität` | Exp | `128 Gbit/s` | non-blocking fabric capacity |
| 9 | `Durchsatz` | Exp | `95,2 Mpps` | forwarding rate |
| 10 | `Bauform` | Req | `19-Zoll-Rackmontage (1 HE)` / `Desktop` / `Hutschiene` | **amendment 4** — switch housing form; NOT transceiver `Formfaktor` Merkmal |
| 11 | `Stromversorgung` | Exp | `intern` / `extern (Netzteil)` / `redundant (2× PSU)` | |
| 12 | `Kühlung` | Exp | `lüfterlos` / `aktiver Lüfter` | |
| 13 | `Stacking` | Exp | `Ja (bis 8 Einheiten)` / `Nein` | |
| 14 | `Betriebstemperatur` | Exp | `0 bis 45 °C` | **Rule 9** applies (class-derive if unpublished; industrial-suffix → wider) |
| 15 | `Anwendung` | Req | `Access-Layer` / `Aggregation/Core` / `Rechenzentrum` / `Industrie` / `SOHO/Desktop` | derived+tagged (analog of transceiver Anwendung) |

**Switch-specific semantic cross-checks to add (analog of B.1–B.8), for the gate + audit:**
- **S.1** `PoE`-Budget present ⇒ at least one PoE port present in `Port-Konfiguration` (no PoE budget on a non-PoE switch).
- **S.2** `Layer = L3` ⇒ `Switch-Typ = Managed` (no L3 routing on an unmanaged/smart switch).
- **S.3** `Portanzahl` equals the sum of ports parsed from `Port-Konfiguration` (count integrity).
- **S.4** `Stacking = Ja` only on `Managed`/`Data-Center` tokens.
- **S.5 (amendment 3)** single-L3-token determinism — DIN-rail/Hutschiene ⇒ `Industrie-Switch`
  (the implemented env-first key case); a SKU may not carry a token a higher-precedence rule overrides.
- **S.6 (post-audit)** PN-encoded port groups ⇒ Port-Konfiguration — for vendors whose PN encodes ports
  (MikroTik), every port group in the PN (esp. combo "C" groups) must appear in Port-Konfiguration.
  Catches the consistent-omission class S.3's sum check can miss.
- **Weight guard (post-audit)** — a switch `Artikelgewicht` at/below the transceiver optics placeholder
  (~0,05 kg) or under the switch floor (0,30 kg) HARD-FAILS; switches carry a real per-datasheet weight.
- B.4 (no "—" placeholders) and B.8 (inline-template artifacts, all fields) apply unchanged.

**Note on #1 `Switch-Typ` (amendment 5, confirmed distinct):** holds the **management class** (Managed/
Smart-Managed/Unmanaged) on EVERY SKU. NOT redundant with L3: under the env-first precedence, an
`Industrie-`/`Data-Center-Switch` token states the environment while `Switch-Typ` still states the
management level the token omits. For the four management-class tokens it deliberately restates L3 —
the same intentional pattern as the transceiver `Formfaktor` attribute ↔ its L3 token. `Layer` (#2) is
orthogonal (L2/L2+/L3).

---

## 5. Condition / FAQ deltas

- **Condition:** none — switches are sold new/sealed; same template.
- **FAQ:** structure unchanged (3–10 pairs). Content differs (PoE budget, management interface,
  stacking, rack mounting) — handled by authoring, not schema. The authenticity FAQ pair carries over.

---

## 6. Worked gold-slice SKU (example — demonstrates the schema; NOT committed)

**MikroTik CRS328-24P-4S+RM** — grounded specs to be re-verified against the MikroTik datasheet at
authoring time; shown here only to validate the schema end-to-end.

```
Artikelnummer:  CRS328-24P-4S+RM
Artikelname:    MikroTik CRS328-24P-4S+RM Managed PoE-Switch – 24× Gigabit RJ45 (PoE+), 4× 10G SFP+, 1 HE
Kategorie L1:   Netzwerk & Infrastruktur
Kategorie L2:   Switches
Kategorie L3:   Managed Switch (L3)
Titel-Tag:      MikroTik CRS328-24P-4S+RM 24-Port PoE+ Switch | Hexwaren        (<=60)
Meta-Desc:      Original MikroTik CRS328-24P-4S+RM: Managed 24× Gigabit-PoE+-Switch mit 4× 10G SFP+,
                500-W-PoE-Budget, 19-Zoll-Rackmontage. Dual-Boot RouterOS/SwOS.        (140–200)
Kurzbeschreibung (2× <p>, 40–80 W):
  <p>Der MikroTik CRS328-24P-4S+RM ist ein gemanagter Gigabit-Switch mit 24 RJ45-Ports inklusive
  PoE-Out (802.3af/at) und vier 10-Gigabit-SFP+-Uplinks. Mit Dual-Boot zwischen RouterOS und SwOS
  eignet er sich für L2- wie L3-Aufgaben im Access- und Aggregations-Layer.</p>
  <p>Im 19-Zoll-Gehäuse (1 HE) liefert er ein PoE-Budget von 500 W und versorgt damit Access Points,
  IP-Kameras und Telefone direkt über das Netzwerkkabel.</p>
Beschreibung (3× <p>, 90–175 W): … endend mit "Originaler MikroTik-…" (authenticity closer).
Attributes (Attributgruppe = Switch; Sortiernummer in []):
  [1]  Switch-Typ           = Managed
  [2]  Layer                = L3 (RouterOS) / L2 (SwOS)
  [3]  Portanzahl           = 28
  [4]  Port-Konfiguration   = 24× 10/100/1000 RJ45 (PoE-Out 802.3af/at), 4× 10G SFP+
  [5]  Port-Geschwindigkeit = 1 GbE (Access) / 10 GbE (Uplink)
  [6]  Uplink-Ports         = 4× SFP+ (10G)
  [7]  PoE                  = PoE+ (802.3af/at), 500 W Budget
  [8]  Switching-Kapazität  = 68 Gbit/s
  [9]  Durchsatz            = 50,5 Mpps
  [10] Bauform              = 19-Zoll-Rackmontage (1 HE)
  [L3-token: Managed Switch (L3) — env-first precedence: not Industrie/DC → management class]
  [11] Stromversorgung     = intern (Einbaunetzteil)
  [12] Kühlung             = aktiver Lüfter
  [13] Stacking            = Nein
  [14] Betriebstemperatur  = -40 bis +60 °C   (datasheet-verbatim where published; else Rule 9)
  [15] Anwendung           = Access-/Aggregations-Layer
FAQ (3–10): authenticity pair + "Wie hoch ist das PoE-Budget?" + "Unterstützt der Switch Layer-3-Routing?" …
Zustand: Neu, versiegelt   |   netto_vk: (best-effort / 0,00 flagged)
```

---

## 7. Post-approval work (ONLY after sign-off)

1. Add `Switches` L2 + the 6 L3 tokens to `config/rules.yaml` + new `config/taxonomy/switches.yaml`.
2. Add `attributgruppe_switch` + a `SWITCH_ATTRIBUTES` tuple (constants.py) with the 15 attributes.
3. Teach `validate.py` the category-aware attribute set (switch vs transceiver) + add S.1–S.4.
4. A switch attribute-depth table (EXPECTED_WHEN analog) + `Anwendung`/`Betriebstemperatur` derivers.
5. Then harvest → author → gate → parity → audit → price → commit per family, brand by brand.

**Until sign-off: HALT. No switch authoring, no taxonomy/code edits.**
