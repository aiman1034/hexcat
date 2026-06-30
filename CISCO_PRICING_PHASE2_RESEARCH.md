# Cisco Switches — Pricing Phase-2 Market Research

**Date:** 2026-06-30 · **Scope:** all 58 Cisco switch E3 families · **Status:** RESEARCH ONLY — **0 prices changed, 0 catalog/src/config files changed.** This document is a market-data reference for the operator (Fawaz) to set Phase-2 positioning. No Hexwaren prices are proposed here — positioning is the operator's call.

> **Progress: 34 / 58 families collected.** Resume point = ranked family **#26**; families **#3 (Nexus 9500) + #27–58 minus those already done** are in-flight (Wave B + Nexus 9500 refetch). See the in-flight rows (⏳) and the "Resume point" section at the end.

---

## Why Phase-2

Phase-1 prices were derived from a **flat multiplier off a single calibration point**. Phase-2 re-anchors each family to its **own** real market data. The headline result already visible across 34 families: the flat multiplier **does not track any single market level** — it lands far below new-sealed for EOL chassis/modules/DC switches (which trade new only as premium NOS), above the cheap end for some EOL access switches, and roughly right only for current SMB/DC gear.

## Method & framing (read before the table)

1. **NEW-SEALED anchor only (MISSION §1).** Hexwaren is a German B2B reseller of **new-sealed original** Cisco hardware. Refurbished / used / "renewed" / broker sellers are **never competitors and never a source of truth** — their prices are captured as a *context* "refurb floor" but **Δ is computed against the new-sealed anchor**, preferring an **EU B2B EUR** anchor where one exists.
2. **Bimodal / NOS reality.** For EOL gear the market splits into a cheap **refurb floor** and a scarce, expensive **new-sealed / new-old-stock (NOS)** tier. Phase-1 frequently tracks the refurb floor → reads "low vs new-sealed." Whether Hexwaren can source/sell at the NOS premium is the operator's call; we surface both numbers.
3. **Region split.** EU B2B (it-market, Senetic, stack-systems, layer23, Bechtle) often runs **materially below** US listings (router-switch, ORMSystems). The EU anchor is the relevant one for a German reseller; US figures are secondary/directional.
4. **router-switch.com caveat.** Its main price is AJAX-injected; where used we took the **actual sell price** (the lower figure after "List Price"), **not** the `og:price`/GPL list. Several agents found its sell figure inconsistent to extract → **router-switch USD is treated as directional**, not a firm anchor. `stack-systems` JSON `priceCurrency=USD` (its displayed € is a converted gross) → directional EU.
5. **No fabrication.** Where no clean new-sealed anchor exists (e.g. brand-new families not yet on the secondary market), the cell is **⚠ DATA GAP** — never inferred from siblings or invented. BrokerBin is login-gated → not used.
6. **Each price = value + currency + source + date** (full URLs captured per family). USD→EUR ≈ ×0.93 for the Δ comparisons.

**Flag legend:** ▼ **LOW** = Phase-1 >40 % below new-sealed · ▲ **HIGH** = Phase-1 >40 % above new-sealed · ✓ **OK** = within ±40 % · ⚠ **GAP** = no clean new-sealed anchor · *(borderline / mixed noted inline)*.

---

## Market-data table (ranked by family Phase-1 value; #1 = highest)

| # | Family | Rep PN (med / hi) | New-sealed market anchor(s) — value (source, date) | Phase-1 net € | Δ vs new-sealed | Flag |
|---|--------|-------------------|----------------------------------------------------|---------------|-----------------|------|
| 1 | Nexus 9300 | N9K-C93180YC-FX3S / N9K-C9364D-GX2A | FX3S: new-sibling FX3 **€15,689** (Bechtle DE) · refurb €8,995 (it-market). GX2A: **$30,150** (ITMall NIB) · $52,626 (Stack DE); GPL ~$150k | 12 000 / 44 000 | FX3S −23 % · GX2A within €28–49k | ✓ OK |
| 2 | Catalyst 9300 | C9300-48P / C9300X-48HX | 48P: **$3,467** new (NetworkTigers) ~€1.5–3.2k. 48HX-A: **€8,400** net new (it-market) · $17,196 (NetworkTigers US) | 4 600 / 14 000 | 48HX within €8.4–17.2k | ✓ OK |
| 3 | **Nexus 9500** | N9K-C9504 / N9K-C9516 | ⏳ **in-flight** (refetch agent running) | 30 000 / 55 000 | ⏳ | ⏳ |
| 4 | Nexus 3000 | N3K-C3064TQ-10GT / N3K-C3432D-S | 3064TQ: **$450** new-NOS (Serverblink) ~€420. 3432D: **$45,999–53,850** new (ServerTechSupply/Connection) ~€43–50k | 3 500 / 16 000 | 3064TQ **+5–8×** · 3432D **−65 %** | ▲▼ FLAG |
| 5 | MDS 9000 | DS-C9396S-48EK9 / DS-C9148T-24EK9¹ | 9396S: **$29,778** new (router-switch) · $40–42k (Zones/Connection) ~€28k. 9148T: $14,942 new | 7 000 / 30 000 | 9396S **−75 %** | ▼ FLAG |
| 6 | Catalyst 9500 | C9500-48Y4C / C9500X-28C8D | 48Y4C: **$5,448–11,990** new (router-switch/layer23/ORM) ~€5–11k. 28C8D-A: **€48,433** net (Stack DE) · $38–49k | 5 800 / 28 000 | 48Y4C OK · 28C8D **−42 %** | ▼ FLAG (borderline) |
| 7 | Catalyst 3650 | WS-C3650-48PD-S / WS-C3650-12X48UR-E | 48PD-S: **$428–1,200** new (Technivision/ORM) ~€400–1.1k. 12X48UR-E: **$5,500–10,637** new (ORM/ServerEvolution/router-switch) | 1 450 / 5 280 | 48PD-S high vs street · 12X48UR-E OK | ▲ FLAG-soft (mixed) |
| 8 | Catalyst 9350 | C9350-12Y / C9350-48HXN | ⚠ both reps 404 everywhere (newest Silicon One "Smart Switch" gen). Proxy -48HX **$11,888** (layer23) | 7 000 / 12 000 | hi ~OK vs proxy; reps unpriceable | ⚠ GAP |
| 9 | Catalyst 2960 | WS-C2960G-48TC-L / WS-C2960XR-48FPD-I | 2960G: **$326** new (router-switch) ~€305. 2960XR: **$9,062** new (router-switch, OOS, directional) ~€8.4k. Refurb €90–320 | 650 / 4 000 | 2960G **+113 %** · 2960XR **−53 %** | ▲▼ FLAG (inconsistent) |
| 10 | Nexus 9200 | N9K-C9272Q / N9K-C9236C | new-channel (router-switch, directional): 9272Q **$15,905**, 9236C **$21,518**, 92160YC-X $12,252. Refurb €1–2.7k | 13 000 / 17 500 | aligns with new-channel (directional) | ✓ OK vs new-channel |
| 11 | Catalyst 3850 | WS-C3850-48F-S / WS-C3850-12X48U-E | 48F-S: new-NOS **$7,399** (iainventory) ~€6.9k. 12X48U-E: **~€10k** new (Senetic.pl). Refurb ~€300 | 1 690 / 5 000 | 48F-S **−75 %** · 12X48U-E **−50 %** (vs new-NOS) | ▼ FLAG (bimodal) |
| 12 | Catalyst IE3500 | IE-3500H-12FT4T-E / IE-3500H-12P2MU2XA | 12FT4T-E: **$4,023** new (GetItNew) ~€3.75k. 12P2MU2XA: **$13,073–13,195** new (GetItNew/NetworkDevicesInc) ~€12.1k | 2 600 / 4 600 | 12FT4T −31 % · 12P2MU2XA **−62 %** | ▼ FLAG (hi underpriced) |
| 13 | Catalyst 9200 | C9200-24P / C9200-48PXG | 24P: **$1,318** new (router-switch) ~€1.23k. 48PXG: **$3,840–6,196** new (router-switch -A/-E) ~€3.6–5.8k | 2 200 / 4 500 | 24P **+79 %** · 48PXG OK | ▲ FLAG (med high) |
| 14 | Nexus 7000 Modules | N7K-M206FQ-23L / N77-F430CQ-36 | M206FQ: broker $1,250–2,400 (used). F430CQ: refurb **$34,932–82,663** (NetworkHardwares/GovConnection/Optdex) ~€32–77k | 900 / 6 000 | F430CQ **−85 %** (order of magnitude) | ▼ FLAG (strong) |
| 15 | 550X | SG550X-48P / SX550X-52 | 48P: **$3,948** new (router-switch) ~€3.7k. 52: **$6,512–10,109** new (SecureITStore/router-switch); GPL $17,667 | 1 550 / 4 500 | 48P **−58 %** · 52 −26 % (vs new) | ▼ FLAG-soft |
| 16 | Catalyst 3750 | WS-C3750E-48TD-S / WS-C3750X-48U-E | 3750X-48P-S: **€1,547** net new (it-market). 48U-E: €1,000 refurb (it-market); new thin | 650 / 2 800 | 650 in refurb band; 2800 above refurb | ✓ OK (EOL) |
| 17 | Nexus 7000 Switches | N77-C7706 / N77-C7718 | **$15,459 / $42,933** new-sealed (router-switch, sell; chassis-only) ~€14.4k / €40k. No EU retail anchor | 4 000 / 9 500 | **−72 % / −76 %** | ▼ FLAG |
| 18 | Catalyst 3560 | WS-C3560-48PS-E / WS-C3560X-48U-E | 48PS-E: ⚠ new GAP (refurb ~$143). 3560X-48U-E: **$12,175** new (ServerTechSupply); GPL $16,700 | 560 / 2 500 | med GAP · hi −79 % (NOS) | ⚠ GAP / note |
| 19 | 350X | SG350X-48MP / SX350X-52 | 48MP: **€1,870** new (Senetic SE). 52: **€4,774** net new (Senetic, 45 % off) · $7,725 US | 1 550 / 4 000 | −17 % / −16 % | ✓ OK (EU) |
| 20 | Catalyst 9600 | C9606R / C9610R | 9606R: **€9,800** new (layer23) · $10,098 (router-switch) · €12,378 (Stack). 9610R: ⚠ GAP (new C9610 gen, quote-only) | 14 000 / 22 000 | 9606R +13…+43 % · 9610R GAP | ▲ FLAG-soft / ⚠ |
| 21 | Catalyst 9400 | C9407R / C9410R | 9407R: **$7,865** (router-switch) · €6,515 (layer23) · €4,870 (Stack). 9410R: **$7,384** (router-switch) · €7,793 (Stack) | 12 000 / 15 000 | **+53…+146 % / +92…+103 %** | ▲ FLAG (high) |
| 22 | Catalyst 4500 | WS-C4500X-16SFP+ / WS-C4500X-40X-ES | 16SFP+: **$3,994** new (router-switch) ~€3.7k. 40X-ES: **$13,381** new (router-switch) ~€12.5k | 2 500 / 7 000 | 16SFP+ −33 % · 40X-ES **−44 %** | ▼ FLAG-mixed |
| 23 | Catalyst IE3400 | IE-3400H-8T-A / IE-3400H-24T-A | **€6,150 / €6,650** net new (it-market) · router-switch $5,226 / $7,435 | 2 000 / 3 200 | **−67 % / −52 %** | ▼ FLAG |
| 24 | Catalyst 6500 Modules | VS-S2T-10G / C6800-SUP6T-XL | Sup2T: **$5,819** new (Stack, realistic low) · $22–25k (router-switch/ORM list-ish). Sup6T-XL: **~$22k** (3 sources cluster) | 800 / 3 500 | **−85 % / −83 %** | ▼ FLAG |
| 25 | Catalyst IE9300 | IE-9320-24T4X / IE-9320-16P8U4X | 24T4X-E: **€5,000** net (it-market) · $4,228. 16P8U4X-E: **€10,450** net (it-market) · $14,313 | 3 500 / 6 000 | 24T4X −30 % · 16P8U4X **−43 %** | ▼ FLAG-mixed |
| 26 | Nexus 5000 | N5K-C5596UP-FA / N5K-C5648Q | 5596UP: **$18,580** new (router-switch) ~€17.3k. 5648Q: **€15,295** net (Stack) | 2 600 / 5 500 | **−85 % / −64 %** | ▼ FLAG |
| 27 | Catalyst 1300 | C1300-24P-4X / C1300-24XTS | ⏳ in-flight (Wave B) | 750 / 2 550 | ⏳ | ⏳ |
| 28 | Catalyst 6800 | C6824-X-LE-40G / C6880-X | 6824: **$22,787** new (C1-bundle, router-switch). 6880-X-LE: **$40,787** bare / $21,413 C1-bundle | 3 200 / 5 000 | **−85 % / −80 %** | ▼ FLAG |
| 29 | Industrial Ethernet 2000 | IE-2000-4S-TS-G-B / IE-2000-16PTC-G-NX | $1,050 / $3,251 new (router-switch, directional; EU-new GAP). eBay NOB ~$990 | 740 / 1 450 | thin (EU-new GAP) | ⚠ GAP / soft |
| 30 | Catalyst IE3100 | IE-3100-3P1U2S-E / IE-3100-6P2U2C-E | ⏳ in-flight (Wave B) | 1 700 / 2 900 | ⏳ | ⏳ |
| 31 | Industrial Ethernet 4000 | IE-4000-16T4G-E / IE-4000-8GT8GP4G-E | 16T4G-E: **$3,400–3,880** new (router-switch/ORM) ~€3.2–3.6k. 8GT8GP4G-E: **$2,050** factory-sealed (ServerSupply) – $5,226 | 1 500 / 2 600 | 16T4G **−52…−58 %** · 8GT8GP4G +37 % OK | ▼ FLAG-mixed |
| 32 | Catalyst 1000 | C1000FE-24P-4G-L / C1000-48FP-4X-L | ⏳ in-flight (Wave B) | 630 / 1 800 | ⏳ | ⏳ |
| 33 | Catalyst 4500 Modules | WS-X45-SUP7-E / WS-X45-SUP9-E | Sup7-E: **$2,414** new (Stack low) – $5,847 (ORM). Sup9-E: **$3,019** new (Stack, only anchor); GPL $36,230 | 500 / 2 000 | Sup7-E **−78 %** · Sup9-E −29 % | ▼ FLAG-mixed |
| 34 | Meraki MS390 | MS390-48-HW / MS390-48U-HW | ⏳ in-flight (Wave B) | 2 000 / 3 200 | ⏳ | ⏳ |
| 35 | Meraki MS355 | MS355-24X2-HW / MS355-48X2-HW | ⏳ in-flight (Wave B) | 3 200 / 4 200 | ⏳ | ⏳ |
| 36 | Catalyst IE3300 | IE-3300-8T2X-E / IE-3300-8U2X-A | ⏳ in-flight (Wave B) | 1 400 / 2 600 | ⏳ | ⏳ |
| 37 | 350 | SF350-48 / SG350-52MP | SF350-48: **€323** net new (Senetic IT). SG350-52MP: **€660** new (Senetic UK) · $975–1,499 US | 440 / 1 550 | SF350 +36 % · SG350-52MP **+135 %** (vs EU) | ▲ FLAG |
| 38 | Nexus 2000 | N2K-C2248TP-E-1GE / N2K-C2348TQ-10G-E | 2248TP-E: **€1,000** net new (it-market). 2348TQ-10G-E: **€1,309** net new (it-market) · $7,575 US (region-split) | 600 / 1 200 | −40 % / −8 % (vs EU new) | ✓ soft (EU) |
| 39 | Catalyst 6500 Switches | WS-C6506-E / WS-C6513-E | 6506-E: ⚠ new quote-only (asks ~€14k list-ish). 6513-E: new asks $10,920–13,388 (directional); GPL $20,873 | 1 300 / 2 800 | low vs directional-new; new=NOS | ⚠ GAP / ▼ |
| 40 | Meraki MS150 | MS150-24P-4X-HW / MS150-48MP-4X-HW | ⏳ in-flight (Wave B) | 650 / 1 600 | ⏳ | ⏳ |
| 41 | Meraki MS350 | MS350-48-HW / MS350-48FP-HW | ⏳ in-flight (Wave B) | 1 300 / 2 100 | ⏳ | ⏳ |
| 42 | Meraki MS130 | MS130-24P-HW / MS130-48X-HW | ⏳ in-flight (Wave B) | 600 / 1 300 | ⏳ | ⏳ |
| 43 | Catalyst 4900 | WS-C4948E-S / WS-C4948E-F-E | 4948E-S: **$7,795** new (router-switch) · $6,498 (ORM) ~€6.5k. F-E: $8,498 (ORM, directional) | 1 800 / 2 400 | **−72 % / −70 %** | ▼ FLAG |
| 44 | Industrial Ethernet 5000 | IE-5000-16S12P / IE-5000-12S12P-10G | ⏳ in-flight (Wave B) | 3 500 / 4 500 | ⏳ | ⏳ |
| 45 | Catalyst 1200 | C1200-24P-4G / C1200-48P-4X | ⏳ in-flight (Wave B) | 310 / 1 030 | ⏳ | ⏳ |
| 46 | Meraki MS425 | MS425-16-HW / MS425-32-HW | ⏳ in-flight (Wave B) | 2 500 / 4 000 | ⏳ | ⏳ |
| 47 | Meraki MS450 | MS450-12-HW | ⏳ in-flight (Wave B) | 6 000 | ⏳ | ⏳ |
| 48 | Meraki MS250 | MS250-48-HW / MS250-48FP-HW | ⏳ in-flight (Wave B) | 900 / 1 500 | ⏳ | ⏳ |
| 49 | Industrial Ethernet 3000 | IE-3000-8TC / IE-3000-8TC-E | ⏳ in-flight (Wave B) | 900 / 1 300 | ⏳ | ⏳ |
| 50 | Catalyst IE3200 | IE-3200-8T2S-E / IE-3200-8P2S-E | ⏳ in-flight (Wave B) | 1 350 / 2 600 | ⏳ | ⏳ |
| 51 | Meraki MS125 | MS125-24P-HW / MS125-48FP-HW | ⏳ in-flight (Wave B) | 550 / 950 | ⏳ | ⏳ |
| 52 | Meraki MS225 | MS225-24P-HW / MS225-48FP-HW | ⏳ in-flight (Wave B) | 550 / 950 | ⏳ | ⏳ |
| 53 | Meraki MS120 | MS120-8FP-HW / MS120-48FP-HW | ⏳ in-flight (Wave B) | 350 / 700 | ⏳ | ⏳ |
| 54 | Meraki MS410 | MS410-16-HW / MS410-32-HW | ⏳ in-flight (Wave B) | 1 200 / 1 800 | ⏳ | ⏳ |
| 55 | Catalyst 6800 Modules | C6880-X-LE-16P10G / C6880-X-16P10G | LE-16P10G: **$3,324** (Stack) · $3,909 (NetworkTigers) ~€3.1k. 16P10G: **$4,373** (Stack); $24–30k list-ish | 1 000 / 1 300 | **−68 % / −68 %** | ▼ FLAG |
| 56 | Industrial Ethernet 1000 | IE-1000-6T2T-LM / IE-1000-8P2S-LM | ⏳ in-flight (Wave B) | 450 / 850 | ⏳ | ⏳ |
| 57 | Meraki MS210 | MS210-24P-HW / MS210-48FP-HW | ⏳ in-flight (Wave B) | 400 / 700 | ⏳ | ⏳ |
| 58 | Catalyst Micro | CMICR-4PC / CMICR-4PT | ⏳ in-flight (Wave B) | 480 / 680 | ⏳ | ⏳ |

¹ MDS hi rep DS-C9718 is a director chassis = quote-only; priced the DS-C9148T-24EK9 fixed switch as the firm anchor.

---

## Summary so far (34 / 58 families)

### ▼ RAISE candidates — Phase-1 well BELOW new-sealed (>40 %)
The dominant pattern. Phase-1's flat multiplier tracked the refurb/broker level; new-sealed (often NOS) is far higher:
- **Datacenter / Fibre-Channel:** MDS 9000 (−75 %), Nexus 5000 (−64…−85 %), Nexus 3000 high-end N3K-C3432D-S (−65 %), Nexus 7000 modules N77-F430CQ-36 (**−85 %, order of magnitude**).
- **Modular / EOL chassis:** Nexus 7000 switches (−72…−76 %), Catalyst 6800 (−80…−85 %), Catalyst 4900 (−70…−72 %), Catalyst 4500 40X-ES (−44 %), Catalyst 6500 switches (new=NOS, low vs directional).
- **Modules:** Catalyst 6500 Modules (−83…−85 %), Catalyst 6800 Modules (−68 %), Catalyst 4500 Modules Sup7-E (−78 %).
- **Rugged / current IE & access:** IE3400 (−52…−67 %), IE9300 16P8U4X (−43 %), IE4000 16T4G (−52…−58 %), Catalyst IE3500 12P2MU2XA (−62 %), Catalyst 3850 (−50…−75 % vs new-NOS), 550X (−26…−58 %).
- **Caveat:** for EOL families the new-sealed anchor is thin NOS — raising to match assumes Hexwaren can source new-sealed at that level.

### ▲ CUT candidates — Phase-1 ABOVE new-sealed (>40 %)
- **Catalyst 9400** (+53…+146 % — bare chassis far cheaper new than Phase-1 assumed).
- **Catalyst 2960** WS-C2960G-48TC-L (+113 %), **Catalyst 9200** C9200-24P (+79 %), **350** SG350-52MP (+135 % vs EU), **Nexus 3000** low-end N3K-C3064TQ-10GT (**+5–8×**), **Catalyst 3650** 48PD-S (high vs street). Catalyst 9600 C9606R borderline (+13…+43 %).

### ⚠ DATA GAPS — no clean new-sealed anchor (do NOT fabricate)
- **Catalyst 9350** (newest Silicon One gen; reps 404 everywhere; proxy -48HX only).
- **Catalyst 9600 C9610R** (brand-new C9610 gen; quote-only).
- **Catalyst 6500 switches WS-C6506-E** (new quote-only/NOS; only refurb is firm).
- **Catalyst 3560 WS-C3560-48PS-E** (EOL, refurb-only).
- **IE2000** EU-new (router-switch USD directional only).
- Catalyst 4500/6500 Modules EU-new (Senetic carries only -RF reman).

### ✓ Roughly OK vs new-sealed (within ±40 %)
Nexus 9300, Catalyst 9300, Nexus 9200 (vs new-channel), 350X, Nexus 2000 (vs EU new), Catalyst 3750, Catalyst 9500 48Y4C.

---

## Resume point

- **Collected: 34 / 58** families (ranked #1–26 done except #3 Nexus 9500; plus #28, 29, 31, 33, 37, 38, 39, 43, 55).
- **In-flight (⏳ 24): #3 Nexus 9500** (refetch agent running) + **Wave B** = #27 Catalyst 1300, #30 IE3100, #32 Catalyst 1000, #34 MS390, #35 MS355, #36 IE3300, #40 MS150, #41 MS350, #42 MS130, #44 IE5000, #45 Catalyst 1200, #46 MS425, #47 MS450, #48 MS250, #49 IE3000, #50 IE3200, #51 MS125, #52 MS225, #53 MS120, #54 MS410, #56 IE1000, #57 MS210, #58 Catalyst Micro.
- Next: fill the 24 ⏳ rows as the agents land, then finalize the summary across all 58.

*Collection method: per-family / small-cluster direct-fetch agents (WebFetch/WebSearch/curl, browser UA). Sources: it-market, Senetic, stack-systems, layer23-switch, Bechtle, comms-express, router-switch (USD, directional), eBay-DE, US catalog resellers. BrokerBin login-gated (not used). Every figure is dated 2026-06-30 and source-attributed; no value was fabricated or inferred from siblings.*
