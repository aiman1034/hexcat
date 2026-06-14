# Switches — Gold-Slice Schema PROPOSAL (Rule-7, PENDING operator sign-off)

> **Status: PROPOSAL ONLY. Nothing authored, no code/taxonomy changed.** Per Rule 7 (taxonomy-approval
> gate) this is surfaced for the operator's yes/no before any switch SKU is authored. Designed as a
> faithful analog of the locked transceiver gold-slice so the 7-file JTL-Ameise v5.0 byte contract,
> the gate, pricing, the 8 semantic cross-checks, Rule 8/9, and the per-brand pipeline all carry over
> unchanged. Decisions needing your sign-off are marked **[DECISION]**.

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

**Proposed for switches:**
- **Kategorie Ebene 2:** `Switches`
- **Attributgruppe:** `Switche` (one char different — drop the final `s`, mirroring `Module`→`Modul`).

*(Alternative if you prefer a more descriptive L2: `Netzwerk-Switches` / Attributgruppe
`Netzwerk-Switche`. Your call — the one-char rule is the only hard constraint.)*

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

Rules carried over: closed set, **"Sonstige" never allowed**; a switch maps to exactly one token;
"Stackable"/"PoE"/port-speed are **attributes**, not L3 tokens (no overlap). Must stay in lock-step
with a new `config/taxonomy/switches.yaml` ⇄ `config/rules.yaml` (post-approval).

---

## 4. [DECISION] The switch attribute set (fixed order = Sortiernummer)

Analog of the 14 transceiver attributes. **15 proposed**, fixed order (Sortiernummer = 1-based index).
"Req" = required on every SKU (gate-enforced like transceiver Anwendung/Geschwindigkeit); "Exp" =
expected where applicable (attribute-depth model decides GAP vs PROVABLY_ABSENT).

| # | Attributname | Req/Exp | Example value | Notes |
|---|---|---|---|---|
| 1 | `Switch-Typ` | Req | `Managed` / `Smart-Managed` / `Unmanaged` | management class (mirrors L3) |
| 2 | `Layer` | Req | `L2` / `L2+` / `L3` | switching layer |
| 3 | `Portanzahl` | Req | `28` | total physical ports |
| 4 | `Port-Konfiguration` | Req | `24× 1GbE RJ45 (PoE), 4× 10G SFP+` | the defining spec (analog of Formfaktor) |
| 5 | `Geschwindigkeit` | Req | `1 GbE` (access-port class) | the speed analog; multi-rate listed |
| 6 | `Uplink-Ports` | Exp | `4× SFP+ (10G)` | when dedicated uplinks exist |
| 7 | `PoE` | Req | `PoE+ (802.3at), 450 W Budget` / `Nein` | always present; `Nein` if none |
| 8 | `Switching-Kapazität` | Exp | `128 Gbit/s` | non-blocking fabric capacity |
| 9 | `Durchsatz` | Exp | `95,2 Mpps` | forwarding rate |
| 10 | `Formfaktor` | Req | `19-Zoll-Rackmontage (1 HE)` / `Desktop` / `DIN-Schiene` | physical build |
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
- B.4 (no "—" placeholders) and B.8 (inline-template artifacts, all fields) apply unchanged.

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
Attributes (Attributgruppe = Switche; Sortiernummer in []):
  [1]  Switch-Typ          = Managed
  [2]  Layer               = L3 (RouterOS) / L2 (SwOS)
  [3]  Portanzahl          = 28
  [4]  Port-Konfiguration  = 24× 10/100/1000 RJ45 (PoE-Out 802.3af/at), 4× 10G SFP+
  [5]  Geschwindigkeit     = 1 GbE (Access) / 10 GbE (Uplink)
  [6]  Uplink-Ports        = 4× SFP+ (10G)
  [7]  PoE                 = PoE+ (802.3af/at), 500 W Budget
  [8]  Switching-Kapazität = 68 Gbit/s
  [9]  Durchsatz           = 50,5 Mpps
  [10] Formfaktor          = 19-Zoll-Rackmontage (1 HE)
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
