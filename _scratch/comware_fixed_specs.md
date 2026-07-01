# Comware FIXED-switch grounded specs (agent findings → transcribe into build SPECS)
# Hersteller=HP, BRAND="HPE" (slug hpe-aruba). SwK/Durchsatz VERBATIM from OEM QuickSpec, German-format at author.
# ZU_VERIFIZIEREN → customer-safe rephrase at author, NEVER ship token. Module slots phrased w/o "N×" token (S.3 clean).
# Comware OS: write "HPE-Comware-Betriebssystem" (no version — v7 not printed, agent flagged). IRF=stacking VALUE.

## FlexNetwork 5140 EI — DONE (agent a45e72daf3aff2c4d). doc a50002579enw. IRF max 9. temp -5..45°C. PSU internal fixed AC (+RPS on PoE; JL826A 2 slots). fan-cooled (airflow ZU_VERIF→omit). Layer=L3 (static+OSPF+RIP). Comware. CURRENT. mGig(1/2.5/5/10G XGT)=JL823A/JL825A/R8J41A.
# PID | model | n | access | uplink | speeds | PoE | SwK | Durchsatz | RU
JL823A | 5140 24G PoE+ 2SFP+ 2XGT EI | 28 | 24× 10/100/1000 (RJ45, PoE+) | 2× 1/10G SFP+ + 2× 1/2.5/5/10G XGT (RJ45) | 10/100/1000; mGig 1/2.5/5/10G; 1/10G SFP+ | PoE+ 370W | 128 Gbps | 95 Mpps | 1U
JL824A | 5140 48G PoE+ 4SFP+ EI | 52 | 48× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 370W | 176 Gbps | 131 Mpps | 1U
JL825A | 5140 48G PoE+ 2SFP+ 2XGT EI | 52 | 48× 10/100/1000 (RJ45, PoE+) | 2× 1/10G SFP+ + 2× 1/2.5/5/10G XGT (RJ45) | 10/100/1000; mGig; 1/10G SFP+ | PoE+ 370W | 176 Gbps | 131 Mpps | 1U
JL826A | 5140 24G SFP w/8 Combo 4SFP+ EI | 28 | 16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP) | 4× 1/10G SFP+ | 100/1000 SFP; 10/100/1000 combo; 1/10G SFP+ | Nein | 128 Gbps | 95 Mpps | 1U  (agent said n=32 — WRONG; 16+8+4=28)
JL827A | 5140 24G PoE+ 4SFP+ EI | 28 | 24× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 370W | 128 Gbps | 95 Mpps | 1U
JL828A | 5140 24G 4SFP+ EI | 28 | 24× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 128 Gbps | 95 Mpps | 1U
JL829A | 5140 48G 4SFP+ EI | 52 | 48× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 176 Gbps | 131 Mpps | 1U
R8J41A | 5140 24G 2SFP+ 2XGT EI | 28 | 24× 10/100/1000 (RJ45) | 2× 1/10G SFP+ + 2× 1/2.5/5/10G XGT (RJ45) | 10/100/1000; mGig; 1/10G SFP+ | Nein | 128 Gbps | 95 Mpps | 1U
R8J42A | 5140 8G 2SFP 2GT Combo EI | 10 | 8× 10/100/1000 (RJ45) | 2× Dual-Personality-Combo (1G SFP oder 10/100/1000 RJ45) | 10/100/1000; 1G SFP | Nein | 24 Gbps | 18 Mpps | 1U (kompakt)  (agent n=12; 2GT=combo w/2SFP→10)

## FlexNetwork 5140 HI — DONE. doc a50004280enw (a50006098/a50004280 live). IRF max 9. temp -5..45°C. PSU 2 hot-swap slots (AC 100-240 / DC -48..-60). fan (2 trays, side-to-back). Layer=L3 (OSPFv2/v3, VRRP, RIP). Comware. CURRENT. no mGig. +1 optionaler Erweiterungsschacht (nicht in Portanzahl).
R9L61A | 5140 24G 4SFP+ 1-slot HI | 28 | 24× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 288 Gbps | 180 Mpps | 1U (+1 Erweiterungsschacht optional)
R9L62A | 5140 48G 4SFP+ 1-slot HI | 52 | 48× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 336 Gbps | 180 Mpps | 1U (+1 Erweiterungsschacht optional)
R9L63A | 5140 24G PoE+ 4SFP+ 1-slot HI | 28 | 24× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 720W | 288 Gbps | 180 Mpps | 1U (+1 Erweiterungsschacht optional)
R9L64A | 5140 48G PoE+ 4SFP+ 1-slot HI | 52 | 48× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 1440W | 336 Gbps | 180 Mpps | 1U (+1 Erweiterungsschacht optional)

## FlexNetwork 5120 v3 — DONE. doc a50007006enw. IRF up to 9. temp -5..45°C. PSU embedded single AC. FANLESS. Layer=L2+RIP (limited routing, NOT full OSPF/BGP → Layer=L2). Comware. CURRENT thin line. no mGig.
S0F79A | 5120v3 8G PoE+ 2 SFP | 10 | 8× 10/100/1000 (RJ45, PoE+) | 2× 1000BASE-X SFP | 10/100/1000; 1G SFP | PoE+ (IEEE 802.3at 30W/Port; Gesamtbudget modellabhängig — 240W nicht separat gedruckt=ZU_VERIF→customer-safe) | 20 Gbps | 15 Mpps | 1U (kompakt, lüfterlos)

## FlexNetwork 5510 HI — DONE (agent ac814fc8e83a9c4d5). doc c04843027 (RETIRED/EOL). temp 0..45°C. IRF max 9. PSU 2 slots (1 min). fan, airflow front-to-back. Layer=L3 (static/RIP/OSPF/ISIS/BGP + IPv6/MPLS/VPLS). no fixed mGig. Comware v7. EOL. +1 Erweiterungsschacht (module, nicht in Portanzahl). SwK single figure per model.
JH145A | 5510 24G 4SFP+ HI 1-slot | 28 | 24× 10/100/1000 (RJ45) | 4× 10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 288 Gbps | 214 Mpps | 1U
JH146A | 5510 48G 4SFP+ HI 1-slot | 52 | 48× 10/100/1000 (RJ45) | 4× 10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 336 Gbps | 250 Mpps | 1U
JH147A | 5510 24G PoE+ 4SFP+ HI 1-slot | 28 | 24× 10/100/1000 (RJ45, PoE+) | 4× 10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 740W | 288 Gbps | 214 Mpps | 1U
JH148A | 5510 48G PoE+ 4SFP+ HI 1-slot | 52 | 48× 10/100/1000 (RJ45, PoE+) | 4× 10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 1440W | 336 Gbps | 250 Mpps | 1U
JH149A | 5510 24G SFP 4SFP+ HI 1-slot | 28 | 16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder SFP) | 4× 10G SFP+ | 100/1000 SFP; combo; 1/10G SFP+ | Nein | 288 Gbps | 214 Mpps | 1U

## FlexNetwork 5520 HI — DONE. doc a50002587enw V9. temp -5..45°C. IRF max 9 (160 Gbps). PSU 2 slots. fan, airflow side-to-back/back-to-side. Layer=L3 full + VXLAN/EVPN/DRNI/MPLS (no extra license). NO fixed mGig/QSFP (module S0T05A/S0T06A/JH155A only). Comware v7. CURRENT. +1 Erweiterungsschacht. SwK single figure.
R8M25A | 5520 24G 4SFP+ HI | 28 | 16× 10/100/1000 (RJ45) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP) | 4× 1/10G SFP+ | 10/100/1000; combo; 1/10G SFP+ | Nein | 288 Gbps | 180 Mpps | 1U
R8M26A | 5520 48G 4SFP+ HI 1-slot | 52 | 48× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 336 Gbps | 180 Mpps | 1U
R8M27A | 5520 24G SFP 4SFP+ HI | 28 | 16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP) | 4× 1/10G SFP+ | 100/1000 SFP; combo; 1/10G SFP+ | Nein | 288 Gbps | 180 Mpps | 1U
R8M28A | 5520 24G PoE+ 4SFP+ HI | 28 | 24× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 720W | 288 Gbps | 180 Mpps | 1U
R8M29A | 5520 48G PoE+ 4SFP+ HI 1-slot | 52 | 48× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 1440W | 336 Gbps | 180 Mpps | 1U

## FlexFabric 5930 — DONE (agent aaf10a31dc8d20136). doc c04111326 (EOS/EOSL). temp 0..45°C. IRF max 9. PSU internal redundant hot-swap (dual slots), reversible airflow (f-t-b/b-t-f). dual hot-plug fan trays. Layer=L3 full (OSPF/BGP/ISIS/RIP/VRRP/PIM); VXLAN L2-gateway ONLY, NO EVPN; +TRILL/SPB/FCoE/DCB. Comware v7. EOS. PoE=Nein all.
JG726A | 5930 32QSFP+ | 32 | 32× 40G QSFP+ | 40G QSFP+ (10G via 4×10G-Breakout) | Nein | 2560 Gbps | 1429 Mpps | 1U | 0 slots
JH178A | 5930 2QSFP+ 2-slot | 2 fixed | 2× 40G QSFP+ (fest) | 40G QSFP+ (fest); modulabhängig | Nein | 1440 Gbps | 1071 Mpps | 1U | +2 Modulschächte (WORD, no N×)
JH179A | 5930 4-slot | 0 fixed | 0 feste Datenports | modulabhängig (10G/40G/converged) | Nein | 2560 Gbps | 1429 Mpps | 2U | 4 Modulschächte (Portanzahl=0)

## FlexFabric 5940 — DONE. doc c05158726 / DS 4AA6-6465ENW. temp 0..45°C. IRF max 9. PSU internal redundant hot-swap, reversible airflow. dual hot-plug fan trays. Layer=L3 full + VXLAN L2+L3 + EVPN (RFC7432) + OpenFlow/SDN. Comware v7. EOSL date ZU_VERIF→omit. PoE=Nein. (JG726A 5930 1429 vs JH396A 5940 1904 Mpps — distinct!)
JH390A | 5940 48SFP+ 6QSFP28 | 54 | 48× 1/10G SFP+ + 6× 100G QSFP28 | 10G SFP+, 100G QSFP28 | Nein | 2160 Gbps | 1607 Mpps | 1U | 0 slots
JH391A | 5940 48XGT 6QSFP28 | 54 | 48× 1/10GBASE-T (RJ45) + 6× 100G QSFP28 | 1/10G RJ45, 100G QSFP28 | Nein | 2160 Gbps | 1607 Mpps | 1U | 0 slots
JH394A | 5940 48XGT 6QSFP+ | 54 | 48× 1/10GBASE-T (RJ45) + 6× 40G QSFP+ | 1/10G RJ45, 40G QSFP+ | Nein | 1440 Gbps | 1071 Mpps | 1U | 0 slots
JH395A | 5940 48SFP+ 6QSFP+ | 54 | 48× 1/10G SFP+ + 6× 40G QSFP+ | 1/10G SFP+, 40G QSFP+ | Nein | 1440 Gbps | 1071 Mpps | 1U | 0 slots
JH396A | 5940 32QSFP+ | 32 | 32× 40G QSFP+ | 40G QSFP+ (10G via breakout) | Nein | 2560 Gbps | 1904 Mpps | 1U | 0 slots
JH397A | 5940 2-slot | 2 fixed | 2× 40G QSFP+ (fest) | 40G QSFP+ (fest); modulabhängig | Nein | 1440 Gbps | 1071 Mpps | 1U | +2 Modulschächte (WORD)
JH398A | 5940 4-slot | 0 fixed | 0 feste Datenports | modulabhängig | Nein | 2560 Gbps | 1904 Mpps | 2U | 4 Modulschächte (Portanzahl=0)

## FlexFabric 5945 — DONE (agent a5296b91978ed15c5). doc a00047323enw. temp 0..45°C. IRF max 10. PSU hot-plug (2 or 4 slots), reversible airflow. hot-plug fan trays. Layer=L3 full + EVPN/VXLAN/MPLS. Comware v7. CURRENT. PoE=Nein. SwK bidirectional.
JQ074A | 5945 48SFP28 8QSFP28 | 58 | 48× 25G SFP28 + 8× 100G QSFP28 + 2× 1G SFP | 25G SFP28, 100G QSFP28, 1G SFP | Nein | 4 Tbps | 2024 Mpps | 1U | 0 slots
JQ075A | 5945 2-slot | 2 fixed | 2× 100G QSFP28 (fest) | 100G QSFP28 (fest); modulabhängig | Nein | 3.6 Tbps | ZU_VERIF→wire-speed | 2U | +2 Modulschächte (WORD)
JQ076A | 5945 4-slot | 2 fixed (SFP mgmt) | 2× 1G SFP | 1G SFP (fest); modulabhängig | Nein | 6.4 Tbps | ZU_VERIF→wire-speed | 2U | +4 Modulschächte (WORD)
JQ077A | 5945 32QSFP28 | 34 | 32× 100G QSFP28 + 2× 1G SFP | 100G QSFP28, 1G SFP | Nein | 6.4 Tbps | 2024 Mpps | 1U | 0 slots

## FlexFabric 5950 — DONE. doc c05175675 (clean specs) / c05051989 (RETIRED). temp 0..45°C. IRF ~10 (table ZU_VERIF→soften, no hard number). PSU hot-swap (2 or 4 slots), same-direction airflow, 6 fan slots. Layer=L3 full + VXLAN/EVPN. Comware v7. EOSL (JH321A EOS 2019-09-30 / EOSL 2020-03-31). PoE=Nein.
JH321A | 5950 32QSFP28 2SFP+ | 34 | 32× 100G QSFP28 + 2× 1/10G SFP+ | 100G QSFP28, 1/10G SFP+ | Nein | 3200 Gb/s (=3,2 Tbit/s) | 3169 Mpps | 1U | 0 slots
JH402A | 5950 48SFP28 8QSFP28 | 58 | 48× 25G SFP28 + 8× 100G QSFP28 + 2× 1G SFP | 25G SFP28, 100G QSFP28, 1G SFP | Nein | 3200 Gb/s (=3,2 Tbit/s) | 3169 Mpps | 1U | 0 slots
JH404A | 5950 4-slot | 3 fixed (SFP) | 3× 1G SFP | 1G SFP (fest); modulabhängig | Nein | 3,2 Tbit/s | 3169 Mpps | 2U | +4 Modulschächte (WORD)

## FlexFabric 5960 — DONE. doc a50007000enw. temp 0..40°C. Stacking=DRNI (NOT IRF; IRF ZU_VERIF). PSU dual redundant hot-swap (AC/DC). 6 hot-swap fan trays, front-to-rear. Layer=L3 full + EVPN/VXLAN + SR-MPLS/SRv6 + PTP/SyncE + DRNI. Comware V9. CURRENT (200G/400G leader). PoE=Nein. SwK=QuickSpec bidirectional (unidir noted). NEW VALUES: 200G/QSFP56, 400G/QSFP-DD.
S4J82A | 5960R 48QSFP28 6QSFP-DD | 54 | 48× 100G QSFP28 + 6× 400G QSFP-DD | 100G QSFP28, 400G QSFP-DD | Nein | 14,4 Tbit/s (bidir; 7,2 unidir) | 2700 Mpps | 2U | +1 I/O-Modulschacht (WORD)
R9Y12A | 5960 24QSFP56 8QSFP-DD | 34 | 24× 100/200G QSFP56 + 8× 400G QSFP-DD + 2× 10G SFP+ | 200G QSFP56, 400G QSFP-DD, 10G SFP+ | Nein | 16 Tbit/s (bidir; 8 unidir) | ZU_VERIF→wire-speed | 1U | +1 I/O-Modulschacht (WORD)
R9Y13A | 5960 32QSFP-DD 2SFP+ | 34 | 32× 400G QSFP-DD + 2× 1/10G SFP+ | 400G QSFP-DD, 1/10G SFP+ | Nein | 25,6 Tbit/s (bidir; 12,8 unidir) | ZU_VERIF→wire-speed | 1U | +1 I/O-Modulschacht (WORD)

## FlexFabric 5980 — DONE. doc a00029144enw (DAM). temp 0..45°C. IRF max 2. PSU hot-plug (2 slots), reversible airflow, 5 fan slots. Layer=L3 full + EVPN/VXLAN L2/L3. Comware v7. CURRENT. PoE=Nein. ⚠️ SwK+Durchsatz ZU_VERIF (DAM "800 Gbps/720 Mpps" IMPLAUSIBLE — do NOT ship; use wire-speed graceful).
JQ026A | 5980 48SFP+ 6QSFP28 | 54 | 48× 10G SFP+ + 6× 100G QSFP28 | 10G SFP+, 100G QSFP28 | Nein | ZU_VERIF→wire-speed (non-blocking) | ZU_VERIF→wire-speed | 1U | 0 slots

## FlexFabric 5700 — DONE (agent ad0a0fa9170253344). doc c04347352. temp 0..45°C. IRF max 9 (fabric bis 30). PSU 2 slots + 2 fan (F-B/B-F variants). Layer=L3-LITE (statisch + RIP/RIPng NUR; KEIN OSPF/BGP → Anwendung: statisches/RIP-Routing). Comware v7. EOL. PoE=Nein. DC ToR.
JG894A | 5700-48G-4XG-2QSFP+ | 54 | 48× 10/100/1000 (RJ45) + 4× 10G SFP+ + 2× 40G QSFP+ | 10/100/1000, 10G SFP+, 40G QSFP+ | Nein | 336 Gbps | 250 Mpps | 1U | 0 slots
JG896A | 5700-40XG-2QSFP+ | 42 | 40× 10G SFP+ + 2× 40G QSFP+ | 10G SFP+, 40G QSFP+ | Nein | 960 Gbps | 714,2 Mpps | 1U | 0 slots
JG898A | 5700-32XGT-8XG-2QSFP+ | 42 | 32× 10GBASE-T (RJ45) + 8× 10G SFP+ + 2× 40G QSFP+ | 10GBASE-T, 10G SFP+, 40G QSFP+ | Nein | 960 Gbps | 714,2 Mpps | 1U | 0 slots

## FlexFabric 5900 — DONE (agent ad0a0fa9170253344). doc c04111469 v23. temp 0..45°C. IRF max 9. PSU 2 slots + 2 fan-tray, reversible F-B/B-F. Layer=L3 full (OSPF/BGP/ISIS + IPv6 OSPFv3/BGP4+). Comware v7. DCB/FCoE/TRILL. EOL. PoE=Nein. DC ToR. JG838A=5900CP convergence (FCoE).
JC772A | 5900AF-48XG-4QSFP+ | 52 | 48× 1/10G SFP+ + 4× 40G QSFP+ | 1/10G SFP+, 40G QSFP+ | Nein | 1280 Gb/s | 952 Mpps | 1U | 0 slots
JG336A | 5900AF-48XGT-4QSFP+ | 52 | 48× 1/10GBASE-T (RJ45) + 4× 40G QSFP+ | 1/10GBASE-T, 40G QSFP+ | Nein | 1280 Gb/s | 952 Mpps | 1U | 0 slots
JG510A | 5900AF-48G-4XG-2QSFP+ | 54 | 48× 10/100/1000 (RJ45) + 4× 10G SFP+ + 2× 40G QSFP+ | 10/100/1000, 10G SFP+, 40G QSFP+ | Nein | 336 Gb/s | 250 Mpps | 1U | 0 slots
JG838A | 5900CP-48XG-4QSFP+ | 52 | 48× 1/10G SFP+ (Konvergenz/FCoE) + 4× 40G QSFP+ | 1/10G SFP+ (FC/FCoE), 40G QSFP+ | Nein | ZU_VERIF→wire-speed | ZU_VERIF→wire-speed | 1U | 0 slots | convergence-port/FCoE

## FlexNetwork 5130 EI — DONE (agent a0fad6c426b569614). doc c04394228 (EOL/RETIRED). temp -5..45°C. IRF up to 9. PSU internal fixed AC (JG933A=2 modular slots; PoE models optional RPS1600). fan-cooled. Layer=L2 (L2+ static+RIP, NO OSPF/BGP → campus access role). Comware v7. EOL. XGT here=1/10GBASE-T (NOT mGig). PoE=370W.
JG932A | 5130-24G-4SFP+ EI | 28 | 24× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 128 Gbps | 96 Mpps | 1U
JG933A | 5130-24G-SFP-4SFP+ EI | 28 | 16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP) | 4× 1/10G SFP+ | 100/1000 SFP; combo; 1/10G SFP+ | Nein | 128 Gbps | 96 Mpps | 1U
JG934A | 5130-48G-4SFP+ EI | 52 | 48× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 176 Gbps | 130,9 Mpps | 1U
JG936A | 5130-24G-PoE+-4SFP+ (370W) EI | 28 | 24× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 370W | 128 Gbps | 96 Mpps | 1U
JG937A | 5130-48G-PoE+-4SFP+ (370W) EI | 52 | 48× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 370W | 176 Gbps | 130,9 Mpps | 1U
JG938A | 5130-24G-2SFP+-2XGT EI | 28 | 24× 10/100/1000 (RJ45) | 2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45) | 10/100/1000; 1/10G SFP+; 1/10GBASE-T | Nein | 128 Gbps | 96 Mpps | 1U
JG939A | 5130-48G-2SFP+-2XGT EI | 52 | 48× 10/100/1000 (RJ45) | 2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45) | 10/100/1000; 1/10G SFP+; 1/10GBASE-T | Nein | 176 Gbps | 130,9 Mpps | 1U
JG940A | 5130-24G-PoE+-2SFP+-2XGT EI | 28 | 24× 10/100/1000 (RJ45, PoE+) | 2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45) | 10/100/1000; 1/10G SFP+; 1/10GBASE-T | PoE+ 370W | 128 Gbps | 96 Mpps | 1U
JG941A | 5130-48G-PoE+-2SFP+-2XGT EI | 52 | 48× 10/100/1000 (RJ45, PoE+) | 2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45) | 10/100/1000; 1/10G SFP+; 1/10GBASE-T | PoE+ 370W | 176 Gbps | 130,9 Mpps | 1U

## FlexNetwork 5130 HI — DONE. doc c04843026 (EOL/RETIRED). temp 0..45°C. IRF 9-chassis (80 Gbps). PSU 2 hot-swap slots (min 1). fan, front-to-back. Layer=L2 (L2+ static+RIP per QuickSpec; full OSPF/BGP via license=ZU_VERIF→omit → campus access role). Comware v7. EOL. +1 slot. PoE=740/1440W.
JH323A | 5130 24G 4SFP+ 1-slot HI | 28 | 24× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 168 Gbps | 154,8 Mpps | 1U
JH324A | 5130 48G 4SFP+ 1-slot HI | 52 | 48× 10/100/1000 (RJ45) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | Nein | 216 Gbps | 190,5 Mpps | 1U
JH325A | 5130 24G PoE+ 4SFP+ 1-slot HI | 28 | 24× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 740W | 168 Gbps | 154,8 Mpps | 1U
JH326A | 5130 48G PoE+ 4SFP+ 1-slot HI | 52 | 48× 10/100/1000 (RJ45, PoE+) | 4× 1/10G SFP+ | 10/100/1000; 1/10G SFP+ | PoE+ 1440W | 216 Gbps | 190,5 Mpps | 1U

## FlexFabric 5710 + 5920 + 5900CP-capacity — PENDING (agent ab3fb5a4fd919b90b; a75137c2 orphan-child found nothing for 5710)
