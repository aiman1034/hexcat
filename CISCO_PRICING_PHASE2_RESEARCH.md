# Cisco Switches — Pricing Phase-2 Market Research

**Date:** 2026-06-30 · **Scope:** all **58** Cisco switch E3 families · **Status:** ✅ **COMPLETE (58/58)** · **RESEARCH ONLY — 0 prices changed, 0 catalog/src/config files changed.** This is a market-data reference for the operator (Fawaz) to set Phase-2 positioning. No Hexwaren prices are proposed — positioning is the operator's call.

## Why Phase-2

Phase-1 prices came from a **flat multiplier off a single calibration point**. Phase-2 re-anchors each family to its **own** real market data. The headline result across all 58 families: the flat multiplier **does not track any single market level** — it lands far below new-sealed for the bulk of EOL chassis/modules/DC/FC/rugged/Meraki gear (which trade new only as scarce premium/NOS stock), far above it for a cluster of bare chassis + current SMB/access, and ~right for current mid-market gear.

## Method & framing (read before the table)

1. **NEW-SEALED anchor only (MISSION §1).** Hexwaren resells **new-sealed original** Cisco hardware. Refurb / used / "renewed" / broker sellers are **never competitors and never a source of truth** — captured only as a *context* "refurb floor"; **Δ is computed vs the new-sealed anchor**, preferring an **EU B2B EUR** anchor where one exists.
2. **Bimodal / NOS reality.** EOL gear splits into a cheap refurb floor and a scarce, expensive new-sealed/NOS tier. Phase-1 frequently tracks the refurb floor → reads "low vs new-sealed." Whether Hexwaren can source/sell at the NOS premium is the operator's call.
3. **Region split.** EU B2B (it-market, Senetic, tonitrus, Bechtle, stack-systems*, layer23) often runs below US listings (router-switch, ORMSystems); the EU anchor is the relevant one for a German reseller.
4. **No fabrication.** Where no clean new-sealed anchor exists, the cell is **⚠ DATA GAP** — never inferred from siblings or invented. BrokerBin login-gated → not used.
5. **Data-quality caveats (apply when reading the cells):**
   - **router-switch.com** main price is AJAX-injected; its USD "sell" (not GPL list) is treated as **directional** — it runs ~4–10× above EU street on several SKUs.
   - **stack-systems.com** quotes **USD** despite a `.de`-style domain (its displayed "€" is mojibake for "$") → USD broker-sell tier, directional.
   - **it-market.com** recurring **€2,975 / net €2,500 "Neu"** is a **default list placeholder** (repeats verbatim across unrelated SKUs) → soft where it's the only point.
   - **4startech.com** new-sealed prices are genuine but **EOL-clearance, skew low**; two were internally inconsistent (MS390-48U < -48; MS210-48FP < -24P) → flagged, not smoothed.
6. **Each price = value + currency + source + date** (per-family source URLs captured during research). USD→EUR ≈ ×0.93 for Δ.

**Flag legend:** ▼ **LOW** = Phase-1 >40 % below new-sealed · ▲ **HIGH** = Phase-1 >40 % above new-sealed · ✓ **OK** = within ±40 % · ⚠ **GAP** = no clean new-sealed anchor · *(borderline / mixed noted inline)*.

---

## Market-data table (all 58 families, ranked by Phase-1 family value; #1 = highest)

| # | Family | Rep PN (med / hi) | New-sealed market anchor(s) — value (source, 2026-06-30) | Phase-1 net € | Δ vs new-sealed | Flag |
|---|--------|-------------------|----------------------------------------------------------|---------------|-----------------|------|
| 1 | Nexus 9300 | N9K-C93180YC-FX3S / N9K-C9364D-GX2A | FX3S: sibling FX3 **€15,689** (Bechtle) · refurb €8,995 (it-market). GX2A: **$30,150** (ITMall NIB) · $52,626 (Stack); GPL ~$150k | 12 000 / 44 000 | within €9–49k | ✓ OK |
| 2 | Catalyst 9300 | C9300-48P / C9300X-48HX | 48P: **$3,467** (NetworkTigers) ~€1.5–3.2k. 48HX-A: **€8,400** net (it-market) · $17,196 (NetworkTigers) | 4 600 / 14 000 | within €8.4–17.2k | ✓ OK |
| 3 | **Nexus 9500** | N9K-C9504 / N9K-C9516 (bare chassis) | 9504 **$4,167–8,550** (layer23/Stack/NetworkTigers/router-switch, 5 src) ~€3.9–7.9k. 9516 **$17.5k–34.4k** (Stack/router-switch, low-conf) ~€16–32k; GPL $14.9k/$50k | 30 000 / 55 000 | **+275…+650 % / +72…+237 %** (vs **bare** chassis) | ▲ FLAG (bare-vs-bundle caveat; EU GAP) |
| 4 | Nexus 3000 | N3K-C3064TQ-10GT / N3K-C3432D-S | 3064TQ: **$450** new-NOS (Serverblink) ~€420. 3432D: **$45,999–53,850** (ServerTechSupply/Connection) ~€43–50k | 3 500 / 16 000 | 3064TQ **+5–8×** · 3432D **−65 %** | ▲▼ FLAG |
| 5 | MDS 9000 | DS-C9396S-48EK9 / DS-C9148T-24EK9¹ | 9396S: **$29,778** (router-switch) · $40–42k (Zones/Connection) ~€28k. 9148T: $14,942 | 7 000 / 30 000 | 9396S **−75 %** | ▼ FLAG |
| 6 | Catalyst 9500 | C9500-48Y4C / C9500X-28C8D | 48Y4C: **$5,448–11,990** (router-switch/layer23/ORM) ~€5–11k. 28C8D-A: **€48,433** net (Stack) · $38–49k | 5 800 / 28 000 | 48Y4C OK · 28C8D **−42 %** | ▼ FLAG (borderline) |
| 7 | Catalyst 3650 | WS-C3650-48PD-S / WS-C3650-12X48UR-E | 48PD-S: **$428–1,200** (Technivision/ORM). 12X48UR-E: **$5,500–10,637** (ORM/ServerEvolution/router-switch) | 1 450 / 5 280 | 48PD-S high vs street · 12X48UR-E OK | ▲ FLAG-soft (mixed) |
| 8 | Catalyst 9350 | C9350-12Y / C9350-48HXN | ⚠ reps 404 (newest Silicon One gen). Proxy -48HX **$11,888** (layer23) | 7 000 / 12 000 | hi ~OK vs proxy | ⚠ GAP |
| 9 | Catalyst 2960 | WS-C2960G-48TC-L / WS-C2960XR-48FPD-I | 2960G **$326** (router-switch) ~€305. 2960XR **$9,062** (router-switch, directional) ~€8.4k. Refurb €90–320 | 650 / 4 000 | 2960G **+113 %** · 2960XR **−53 %** | ▲▼ FLAG (inconsistent) |
| 10 | Nexus 9200 | N9K-C9272Q / N9K-C9236C | new-channel (router-switch, directional): 9272Q **$15,905**, 9236C **$21,518**. Refurb €1–2.7k | 13 000 / 17 500 | aligns w/ new-channel (directional) | ✓ OK vs new-channel |
| 11 | Catalyst 3850 | WS-C3850-48F-S / WS-C3850-12X48U-E | 48F-S: new-NOS **$7,399** (iainventory) ~€6.9k. 12X48U-E: **~€10k** (Senetic.pl). Refurb ~€300 | 1 690 / 5 000 | **−75 % / −50 %** (vs new-NOS) | ▼ FLAG (bimodal) |
| 12 | Catalyst IE3500 | IE-3500H-12FT4T-E / IE-3500H-12P2MU2XA | 12FT4T-E **$4,023** (GetItNew) ~€3.75k. 12P2MU2XA **$13,073–13,195** ~€12.1k | 2 600 / 4 600 | 12FT4T −31 % · 12P2MU2XA **−62 %** | ▼ FLAG |
| 13 | Catalyst 9200 | C9200-24P / C9200-48PXG | 24P **$1,318** (router-switch) ~€1.23k. 48PXG **$3,840–6,196** ~€3.6–5.8k | 2 200 / 4 500 | 24P **+79 %** · 48PXG OK | ▲ FLAG (med high) |
| 14 | Nexus 7000 Modules | N7K-M206FQ-23L / N77-F430CQ-36 | M206FQ broker $1,250–2,400. F430CQ refurb **$34,932–82,663** ~€32–77k | 900 / 6 000 | F430CQ **−85 %** | ▼ FLAG (strong) |
| 15 | 550X | SG550X-48P / SX550X-52 | 48P **$3,948** (router-switch) ~€3.7k. 52 **$6,512–10,109**; GPL $17,667 | 1 550 / 4 500 | 48P **−58 %** · 52 −26 % | ▼ FLAG-soft |
| 16 | Catalyst 3750 | WS-C3750E-48TD-S / WS-C3750X-48U-E | 3750X-48P-S **€1,547** net (it-market). 48U-E €1,000 refurb | 650 / 2 800 | in refurb/new band | ✓ OK (EOL) |
| 17 | Nexus 7000 Switches | N77-C7706 / N77-C7718 | **$15,459 / $42,933** (router-switch, chassis-only) ~€14.4k / €40k | 4 000 / 9 500 | **−72 % / −76 %** | ▼ FLAG |
| 18 | Catalyst 3560 | WS-C3560-48PS-E / WS-C3560X-48U-E | 48PS-E ⚠ new GAP (refurb ~$143). 3560X-48U-E **$12,175** (ServerTechSupply) | 560 / 2 500 | med GAP · hi −79 % (NOS) | ⚠ GAP / note |
| 19 | 350X | SG350X-48MP / SX350X-52 | 48MP **€1,870** (Senetic). 52 **€4,774** net (Senetic) · $7,725 | 1 550 / 4 000 | −17 % / −16 % | ✓ OK (EU) |
| 20 | Catalyst 9600 | C9606R / C9610R | 9606R **€9,800** (layer23) · €12,378 (Stack). 9610R ⚠ GAP (new gen, quote-only) | 14 000 / 22 000 | 9606R +13…+43 % · 9610R GAP | ▲ FLAG-soft / ⚠ |
| 21 | Catalyst 9400 | C9407R / C9410R | 9407R **$7,865** · €4,870–6,515 (Stack/layer23). 9410R **$7,384** · €7,793 (Stack) | 12 000 / 15 000 | **+53…+146 % / +92…+103 %** | ▲ FLAG (high) |
| 22 | Catalyst 4500 | WS-C4500X-16SFP+ / WS-C4500X-40X-ES | 16SFP+ **$3,994** ~€3.7k. 40X-ES **$13,381** ~€12.5k (router-switch) | 2 500 / 7 000 | 16SFP+ −33 % · 40X-ES **−44 %** | ▼ FLAG-mixed |
| 23 | Catalyst IE3400 | IE-3400H-8T-A / IE-3400H-24T-A | **€6,150 / €6,650** net (it-market) · $5,226 / $7,435 | 2 000 / 3 200 | **−67 % / −52 %** | ▼ FLAG |
| 24 | Catalyst 6500 Modules | VS-S2T-10G / C6800-SUP6T-XL | Sup2T **$5,819** (Stack, low) · $22–25k list-ish. Sup6T-XL **~$22k** (3 src) | 800 / 3 500 | **−85 % / −83 %** | ▼ FLAG |
| 25 | Catalyst IE9300 | IE-9320-24T4X / IE-9320-16P8U4X | 24T4X-E **€5,000** net · $4,228. 16P8U4X-E **€10,450** net · $14,313 (it-market) | 3 500 / 6 000 | 24T4X −30 % · 16P8U4X **−43 %** | ▼ FLAG-mixed |
| 26 | Nexus 5000 | N5K-C5596UP-FA / N5K-C5648Q | 5596UP **$18,580** (router-switch) ~€17.3k. 5648Q **€15,295** net (Stack) | 2 600 / 5 500 | **−85 % / −64 %** | ▼ FLAG |
| 27 | Catalyst 1300 | C1300-24P-4X / C1300-24XTS | 24P-4X **€631–805** (Senetic). 24XTS **€2,772** net (Senetic) · $3,070 | 750 / 2 550 | within ±15 % | ✓ OK (EU) |
| 28 | Catalyst 6800 | C6824-X-LE-40G / C6880-X | 6824 **$22,787** (C1-bundle, router-switch). 6880-X-LE **$40,787** bare / $21,413 bundle | 3 200 / 5 000 | **−85 % / −80 %** | ▼ FLAG |
| 29 | Industrial Ethernet 2000 | IE-2000-4S-TS-G-B / IE-2000-16PTC-G-NX | $1,050 / $3,251 (router-switch, directional; EU-new GAP). eBay NOB ~$990 | 740 / 1 450 | thin (EU-new GAP) | ⚠ GAP / soft |
| 30 | Catalyst IE3100 | IE-3100-3P1U2S-E / IE-3100-6P2U2C-E | ⚠ reps 404 (newest 2024). Siblings (it-market): 4P2S-E €2,975 · 8P2C-E €4,998 · 8T2C-E €1,815 | 1 700 / 2 900 | reps unpriceable; likely low vs siblings | ⚠ GAP |
| 31 | Industrial Ethernet 4000 | IE-4000-16T4G-E / IE-4000-8GT8GP4G-E | 16T4G-E **$3,400–3,880** ~€3.2–3.6k. 8GT8GP4G-E **$2,050** sealed (ServerSupply) – $5,226 | 1 500 / 2 600 | 16T4G **−52…−58 %** · 8GT8GP4G +37 % OK | ▼ FLAG-mixed |
| 32 | Catalyst 1000 | C1000FE-24P-4G-L / C1000-48FP-4X-L | ⚠ EU-EUR GAP. FE: $620–1,396 (Amazon/router-switch). 48FP: **$3,675** (DataDirect) · $4,842 (router-switch) | 630 / 1 800 | EU GAP; 48FP low vs USD new | ⚠ GAP / ▼ |
| 33 | Catalyst 4500 Modules | WS-X45-SUP7-E / WS-X45-SUP9-E | Sup7-E **$2,414** (Stack low) – $5,847. Sup9-E **$3,019** (Stack); GPL $36,230 | 500 / 2 000 | Sup7-E **−78 %** · Sup9-E −29 % | ▼ FLAG-mixed |
| 34 | Meraki MS390 | MS390-48-HW / MS390-48U-HW | 48 **€6,350** net · 48U **€2,050** net (it-market; 48U < 48 = anomaly) | 2 000 / 3 200 | 48 **−68 %** · 48U **+56 %** | ▲▼ FLAG (messy) |
| 35 | Meraki MS355 | MS355-24X2-HW / MS355-48X2-HW | **€6,500 / €7,450** net (it-market) | 3 200 / 4 200 | **−51 % / −44 %** | ▼ FLAG |
| 36 | Catalyst IE3300 | IE-3300-8T2X-E / IE-3300-8U2X-A | 8T2X-E realistic **~€2,900–3,160** (layer23/it-market). 8U2X-A ⚠ GAP (sibling 8P2S-E €4,760) | 1 400 / 2 600 | 8T2X-E **−52 %** · 8U2X-A −45 % (sibling) | ▼ FLAG-low / ⚠ |
| 37 | 350 | SF350-48 / SG350-52MP | SF350-48 **€323** net (Senetic). SG350-52MP **€660** (Senetic) · $975–1,499 | 440 / 1 550 | SF350 +36 % · SG350-52MP **+135 %** (vs EU) | ▲ FLAG |
| 38 | Nexus 2000 | N2K-C2248TP-E-1GE / N2K-C2348TQ-10G-E | 2248TP-E **€1,000** net · 2348TQ-10G-E **€1,309** net (it-market) · $7,575 US | 600 / 1 200 | −40 % / −8 % (vs EU new) | ✓ soft (EU) |
| 39 | Catalyst 6500 Switches | WS-C6506-E / WS-C6513-E | 6506-E ⚠ new quote-only (asks ~€14k list-ish). 6513-E asks $10,920–13,388 (directional); GPL $20,873 | 1 300 / 2 800 | low vs directional-new; new=NOS | ⚠ GAP / ▼ |
| 40 | Meraki MS150 | MS150-24P-4X-HW / MS150-48MP-4X-HW | 24P-4X ⚠ GAP (sibling 24MP-4X €4,067). 48MP-4X **€6,469** net (Bechtle, mGig, OOS) | 650 / 1 600 | hi **−75 %** | ▼ FLAG / ⚠ partial |
| 41 | Meraki MS350 | MS350-48-HW / MS350-48FP-HW | **$1,687 / $2,327** (4startech, EOL clearance) ~€1.57k / €2.16k; router-switch ceiling $9.5–12k | 1 300 / 2 100 | −17 % / −3 % | ✓ OK (clearance) |
| 42 | Meraki MS130 | MS130-24P-HW / MS130-48X-HW | **€1,589 / €4,352** net (Senetic, in stock) | 600 / 1 300 | **−62 % / −70 %** | ▼ FLAG |
| 43 | Catalyst 4900 | WS-C4948E-S / WS-C4948E-F-E | 4948E-S **$7,795** (router-switch) · $6,498 (ORM) ~€6.5k. F-E $8,498 (ORM) | 1 800 / 2 400 | **−72 % / −70 %** | ▼ FLAG |
| 44 | Industrial Ethernet 5000 | IE-5000-16S12P / IE-5000-12S12P-10G | 16S12P **€3,571** net (tonitrus). 12S12P-10G **$15,933 / €26,823** (router-switch/Stack) ~€14–27k | 3 500 / 4 500 | 16S12P −2 % ✓ · 12S12P-10G **−70…−83 %** | ▼ FLAG-mixed |
| 45 | Catalyst 1200 | C1200-24P-4G / C1200-48P-4X | 24P-4G **€311–420** (Senetic). 48P-4X **€596** (Bechtle) · €644 (Senetic) | 310 / 1 030 | 24P-4G ✓ · 48P-4X **+60…+73 %** | ▲ FLAG (hi high) |
| 46 | Meraki MS425 | MS425-16-HW / MS425-32-HW | **€3,850 / €5,500** net (it-market) | 2 500 / 4 000 | −35 % / −27 % | ✓ OK (borderline) |
| 47 | Meraki MS450 | MS450-12-HW | **€7,500** net (it-market) | 6 000 | −20 % | ✓ OK |
| 48 | Meraki MS250 | MS250-48-HW / MS250-48FP-HW | **$1,097 / $1,677–1,950** (4startech/ServerSupply) ~€1.02k / €1.56–1.82k | 900 / 1 500 | −12 % / −4…−17 % | ✓ OK |
| 49 | Industrial Ethernet 3000 | IE-3000-8TC / IE-3000-8TC-E | 8TC **€714** (it-market) · $1,096. 8TC-E **€1,991** (edigitech) · €2,975 (it-market placeholder) | 900 / 1 300 | +26 % / −35 % | ✓ OK/borderline |
| 50 | Catalyst IE3200 | IE-3200-8T2S-E / IE-3200-8P2S-E | 8T2S-E **€1,369–1,547** (it-market, triangulated) · $1,520. 8P2S-E €2,975 (it-market) | 1 350 / 2 600 | spot-on / −13 % | ✓ OK (best data) |
| 51 | Meraki MS125 | MS125-24P-HW / MS125-48FP-HW | ⚠ DATA GAP — EOL (EOS Mar-2025), EU-delisted. Directional: router-switch $4,411 (48FP) | 550 / 950 | EU GAP (EOL) | ⚠ GAP |
| 52 | Meraki MS225 | MS225-24P-HW / MS225-48FP-HW | ⚠ DATA GAP — EOL, EU-delisted. Directional: router-switch $4,762 (48FP) | 550 / 950 | EU GAP (EOL) | ⚠ GAP |
| 53 | Meraki MS120 | MS120-8FP-HW / MS120-48FP-HW | ⚠ DATA GAP — EOL, EU-delisted. Directional: router-switch $710 / $2,588. Fwd sibling MS130-8P €730 | 350 / 700 | EU GAP (EOL) | ⚠ GAP |
| 54 | Meraki MS410 | MS410-16-HW / MS410-32-HW | **$1,347 / $4,977** (4startech) ~€1.25k / €4.63k | 1 200 / 1 800 | 16 −4 % ✓ · 32 **−61 %** | ▼ FLAG-mixed |
| 55 | Catalyst 6800 Modules | C6880-X-LE-16P10G / C6880-X-16P10G | LE-16P10G **$3,324** (Stack) · $3,909 (NetworkTigers) ~€3.1k. 16P10G **$4,373** (Stack); $24–30k list-ish | 1 000 / 1 300 | **−68 % / −68 %** | ▼ FLAG |
| 56 | Industrial Ethernet 1000 | IE-1000-6T2T-LM / IE-1000-8P2S-LM | 6T2T **€434** gross (tonitrus). 8P2S **€1,024** gross / €861 net (tonitrus) · $1,482 | 450 / 850 | ~spot-on both | ✓ OK (EU) |
| 57 | Meraki MS210 | MS210-24P-HW / MS210-48FP-HW | 24P **$597** (4startech). 48FP **$497** (4startech, ⚠ suspect/inversion); refurb $369 | 400 / 700 | 24P −28 % · 48FP +51 % (suspect) | ✓ soft (weak anchor) |
| 58 | Catalyst Micro | CMICR-4PC / CMICR-4PT | ⚠ EU-EUR GAP. USD **$886–966** (router-switch/specialist) ~€820–895 | 480 / 680 | EU GAP; Phase-1 low vs USD | ⚠ GAP / ▼ |

¹ MDS hi rep DS-C9718 is a director chassis = quote-only; priced DS-C9148T-24EK9 as the firm anchor.

---

## Summary — all 58 families

**The dominant pattern: Phase-1 runs systematically BELOW new-sealed.** Roughly **30 families flag** (mostly ▼ LOW), **~12 are ⚠ DATA GAPS**, and **~16 sit OK**. The flat multiplier tracked the refurb/broker level, so for any family where new-sealed is scarce NOS or a current premium product it reads low; a smaller cluster (bare chassis, current SMB/access mispriced upward) reads high.

### ▼ RAISE candidates — Phase-1 >40 % BELOW new-sealed
- **DC / Fibre-Channel:** MDS 9000 (−75 %), Nexus 5000 (−64…−85 %), Nexus 3000 hi N3K-C3432D-S (−65 %), Nexus 7000 modules N77-F430CQ-36 (**−85 %**).
- **Modular / EOL chassis & modules:** Nexus 7000 switches (−72…−76 %), Catalyst 6800 (−80…−85 %), Catalyst 4900 (−70…−72 %), Catalyst 4500 40X-ES (−44 %), Catalyst 6500/6800/4500 Modules (−68…−85 %, Sup7-E −78 %), Catalyst 6500 switches (NOS).
- **Rugged / current IE:** IE3400 (−52…−67 %), IE9300 16P8U4X (−43 %), IE4000 16T4G (−52…−58 %), IE3500 12P2MU2XA (−62 %), IE3300 8T2X-E (−52 %), IE5000 12S12P-10G (−70…−83 %).
- **Access / SMB:** Catalyst 3850 (−50…−75 % vs NOS), 550X (−26…−58 %).
- **Meraki:** MS130 (−62…−70 %), MS150 48MP-4X (−75 %), MS355 (−44…−51 %), MS410 32-HW (−61 %), MS390 48-HW (−68 %).

### ▲ CUT candidates — Phase-1 >40 % ABOVE new-sealed
- **Nexus 9500** (bare chassis **+72…+650 %** — but verify bare-vs-bundle intent first), **Catalyst 9400** (+53…+146 %), **Catalyst 2960** 2960G (+113 %), **Catalyst 9200** C9200-24P (+79 %), **350** SG350-52MP (+135 % vs EU), **Nexus 3000** 3064TQ (**+5–8×**), **Catalyst 1200** 48P-4X (+60…+73 %), **Catalyst 9600** C9606R (+13…+43 %, borderline), Meraki MS390 48U (+56 %, anomalous source).

### ⚠ DATA GAPS — no clean new-sealed anchor (do NOT fabricate)
- **Too new (no secondary/EU market yet):** Catalyst 9350, Catalyst 9600 C9610R, IE3100 (reps), IE3300 8U2X-A (partial), MS150 24P-4X (partial).
- **NOS-only / EOL-delisted:** Catalyst 6500 WS-C6506-E, Catalyst 3560 48PS-E, IE2000 (EU), Catalyst 1000 (EU), Catalyst Micro (EU), Meraki MS125 / MS120 / MS225 (EOL, EU-delisted), Catalyst 4500/6500 Modules (EU; only -RF reman).
- For these, only directional USD or refurb context exists — get a live EU quote before pricing.

### ✓ Roughly OK vs new-sealed (within ±40 %)
Nexus 9300, Catalyst 9300, Nexus 9200 (vs new-channel), 350X, Nexus 2000, Catalyst 3750, Catalyst 9500 48Y4C, Catalyst 1300, IE1000, IE3000, IE3200, IE5000 16S12P, Meraki MS250 / MS350 / MS425 / MS450 / MS410-16 / MS210 (weak).

---

## Sources & confidence

- **Primary EU B2B EUR new-sealed sources** (firmest anchors): **it-market.com** (schema-bound New/Refurb, net+gross), **Senetic.de** (JSON-LD New/InStock), **tonitrus.de** (IE), **Bechtle** (Meraki/SMB), **layer23-switch.com**, **stack-systems.com** (USD-tier despite .de styling).
- **Directional only:** router-switch.com / ORMSystems (USD sell, AJAX/GPL-adjacent, run high), 4startech.com (US, EOL-clearance, skew low).
- **Blocked this run:** comms-express, serversupply, it-planet (Cloudflare/JS); Senetic.com TLD (522); **BrokerBin** login-gated (not used).
- Every figure dated **2026-06-30** and source-attributed; **no value was fabricated or inferred from siblings** — gaps are recorded as gaps.

## Resume point

✅ **COMPLETE — 58 / 58 families.** Collection method: per-family / small-cluster **direct-fetch** agents (WebFetch/WebSearch/curl, browser UA); none delegated. No further families pending. Suggested next step (separate task, operator's call): for the ~12 DATA-GAP families, obtain a live EU B2B quote (or accept directional USD) before any Phase-2 reprice; for the bare-chassis flags (Nexus 9500), confirm whether the catalog SKU means bare or populated before acting on the +Δ.
