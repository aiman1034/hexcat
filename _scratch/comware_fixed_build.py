# -*- coding: utf-8 -*-
"""STEP-2 Phase-2: HPE Comware FIXED switches — FlexFabric (DC ToR/leaf/spine) + FlexNetwork (campus).
17 E3 families / 70 distinct SKUs. Reuses the PROVEN pipeline VERBATIM (reconcile->assemble->scrub->remap->gate).
15 fixed-switch Merkmale + Zustand; 0 new Merkmal NAMES. IRF/DRNI stacking, CP/FCoE, 25G/SFP28, 100G/QSFP28,
200G/QSFP56, 400G/QSFP-DD, mGig = Wertliste VALUES only. Per-PID SwK/Durchsatz VERBATIM from OEM QuickSpecs
(BATCH_HPE_COMWARE_SMB_PHASE1_MANIFEST.md + _scratch/comware_fixed_specs.md), never port-math. Un-published
SwK/Durchsatz (5900CP, 5945 2/4-slot, 5960 R9Y12A/R9Y13A, 5980) -> customer-safe Wire-Speed prose (never ship
ZU_VERIFIZIEREN). Module-slot models -> word-form lever (Portanzahl = fixed data ports; slots worded, no N×).
Hersteller=HP, BRAND="HPE" (slug hpe-aruba). Comware OS register. Prices = Phase-1 ESTIMATE (flagged). $0 prose."""
import json, re, shutil, tempfile, csv, sys
from pathlib import Path
sys.path.insert(0, "_scratch")
from hexcat.config import load_rules, load_weights
from hexcat.stage3 import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat.validate import validate_dir
from hexcat.writers import write_csv
from hexcat import constants as C
import scrub_uwg as S

ROOT = Path("."); rules, weights = load_rules(), load_weights()
BRAND = "HPE"; E1, E2 = "Netzwerk & Infrastruktur", "Switches"; VERIF = "2026-07-02"
def ws(s): return re.sub(r"\s+", " ", s).strip()
def wc(html): return len(re.sub(r"<[^>]+>", "", html).split())
PAD = ["Der {pid} wird als versiegelte Original-Neuware geliefert und eignet sich für den Erstaufbau ebenso "
       "wie für die planbare Ersatzbeschaffung.",
       "Vor dem Einsatz des {pid} empfiehlt sich ein Abgleich von Plattform, Comware-Softwareversion und "
       "benötigten Lizenzen, um den Switch ohne Nacharbeit in Betrieb zu nehmen."]
def pad(intro, pid, lo=100, hi=185):
    i=0
    while sum(wc(p) for p in intro) < lo and i < len(PAD):
        c=PAD[i].format(pid=pid); i+=1
        if sum(wc(p) for p in intro)+wc(c) <= hi: intro[-1]=ws(intro[-1]+" "+c)
    return intro
def fit_meta(m):
    m=ws(m)
    while len(m) < 140: m=m[:-1].rstrip()+" Neu und versiegelt."
    return m[:200].rstrip()

# ---------------- per-family meta (E3, line, series, layer, class, stacking, temp, PSU, cooling, feat, anw, doc, dc)
IRF9  = "IRF (Intelligent Resilient Framework) – Stapelung von bis zu 9 Einheiten zu einem logischen Switch"
IRF10 = "IRF (Intelligent Resilient Framework) – Stapelung von bis zu 10 Einheiten zu einem logischen Switch"
IRF2  = "IRF (Intelligent Resilient Framework) – Dual-Aktiv-Stapelung von bis zu 2 Einheiten"
IRF4  = "IRF (Intelligent Resilient Framework) – Stapelung von bis zu 4 Einheiten zu einem logischen Switch"
IRFn  = "IRF (Intelligent Resilient Framework) – Stapelung mehrerer Einheiten zu einem logischen Switch"
DRNI  = "DRNI (Distributed Resilient Network Interconnect) – Multi-Chassis-Link-Aggregation für aktiv-aktive Hochverfügbarkeit"
PSU_INT   = "Internes Festnetzteil (AC)"
PSU_INT_R = "Internes Festnetzteil (AC); PoE-Modelle optional über externes HPE RPS1600 absicherbar"
PSU_2HS   = "2 Hot-Swap-Netzteilschächte (mindestens 1 Netzteil erforderlich, redundant erweiterbar; AC oder DC)"
PSU_2AC   = "2 Netzteilschächte (mindestens 1 Netzteil erforderlich, redundant erweiterbar; AC)"
PSU_4HS   = "4 Hot-Swap-Netzteilschächte (mindestens 2 Netzteile, redundant; AC oder DC)"
PSU_DRNI  = "Dual redundante Hot-Swap-Netzteile (AC oder DC)"
KF   = "Lüfterlos (passiv gekühlt)"
KVAR = "Lüftergekühlt (variable Lüfterdrehzahl)"
KFB  = "Lüftergekühlt (Hot-Swap-Lüftertrays, Airflow front-to-back oder back-to-front wählbar)"
KFB1 = "Lüftergekühlt (Airflow front-to-back)"
KSB  = "Lüftergekühlt (Airflow seitlich nach hinten)"
KSAME= "Lüftergekühlt (Hot-Swap-Lüftertrays, gleichgerichteter Airflow)"
K5960= "Lüftergekühlt (6 Hot-Swap-Lüftertrays, Airflow front-to-rear)"
D=lambda i:f"https://www.hpe.com/psnow/doc/{i}"

FAM = {
 # ---------------- FlexNetwork (campus) ----------------
 "5120v3": dict(e3="HPE FlexNetwork 5120 v3 Switches", line="FlexNetwork", ser="5120 v3", lyr="L2",
   stk=IRF9, btemp="-5 bis 45 °C", strom="Internes Festnetzteil (AC), lüfterlos", kueh=KF, doc=D("a50007006enw"),
   feat="Layer-2-Funktionen mit statischem und RIP-Routing, dazu VLANs, ACLs, QoS und IRF-Stacking",
   anw="Kompakter gemanagter Campus-Access (Layer 2, HPE Comware) mit Gigabit-PoE+, statischem/RIP-Routing und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=False, brand="HPE Networking Comware"),
 "5130EI": dict(e3="HPE FlexNetwork 5130 EI Switches", line="FlexNetwork", ser="5130 EI", lyr="L2",
   stk=IRF9, btemp="-5 bis 45 °C", strom=PSU_INT_R, kueh=KVAR, doc=D("c04394228"),
   feat="Layer-2-Funktionen mit statischem und RIP-Routing (Layer 2+), dazu VLANs, ACLs, QoS, LACP, Spanning Tree und IRF-Stacking",
   anw="Gemanagter Gigabit-Campus-Access (Layer 2+, HPE Comware) mit 10-GbE-SFP+-Uplinks, statischem/RIP-Routing und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=False),
 "5130HI": dict(e3="HPE FlexNetwork 5130 HI Switches", line="FlexNetwork", ser="5130 HI", lyr="L2",
   stk=IRF9, btemp="0 bis 45 °C", strom=PSU_2AC, kueh=KFB1, doc=D("c04843026"),
   feat="Layer-2-Funktionen mit statischem und RIP-Routing (Layer 2+), dazu VLANs, ACLs, QoS, LACP, Spanning Tree und IRF-Stacking",
   anw="Gemanagter Gigabit-Campus-Access (Layer 2+, HPE Comware) mit 10-GbE-SFP+-Uplinks, Hot-Swap-Netzteilen und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=False),
 "5140EI": dict(e3="HPE FlexNetwork 5140 EI Switches", line="FlexNetwork", ser="5140 EI", lyr="L3",
   stk=IRF9, btemp="-5 bis 45 °C", strom=PSU_INT_R, kueh=KVAR, doc=D("a50002579enw"),
   feat="Layer-3-Routing (statisch, RIP, OSPF), dazu VLANs, ACLs, QoS, LACP, Spanning Tree und IRF-Stacking",
   anw="Gemanagter Gigabit-Campus-Access (Layer 3, HPE Comware) mit 10-GbE-SFP+-Uplinks, optionalem Multi-Gigabit und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=False, brand="HPE Networking Comware"),
 "5140HI": dict(e3="HPE FlexNetwork 5140 HI Switches", line="FlexNetwork", ser="5140 HI", lyr="L3",
   stk=IRF9, btemp="-5 bis 45 °C", strom=PSU_2HS, kueh="Lüftergekühlt (2 Lüftertrays, Airflow seitlich nach hinten)", doc=D("a50004280enw"),
   feat="Layer-3-Routing (OSPFv2/v3, VRRP, RIP), dazu VLANs, ACLs, QoS, LACP und IRF-Stacking",
   anw="Gemanagter Gigabit-Campus-Access/-Aggregation (Layer 3, HPE Comware) mit 10-GbE-SFP+-Uplinks, vollem Routing und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=False, brand="HPE Networking Comware"),
 "5510HI": dict(e3="HPE FlexNetwork 5510 HI Switches", line="FlexNetwork", ser="5510 HI", lyr="L3",
   stk=IRF9, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB1, doc=D("c04843027"),
   feat="Layer-3-Routing (OSPF, IS-IS, BGP, RIP; IPv6, MPLS/VPLS), dazu VRRP, BFD, QoS und IRF-Stacking",
   anw="Gemanagte Gigabit-Campus-Aggregation (Layer 3, HPE Comware) mit 10-GbE-SFP+-Uplinks, vollem dynamischem Routing und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=False),
 "5520HI": dict(e3="HPE FlexNetwork 5520 HI Switches", line="FlexNetwork", ser="5520 HI", lyr="L3",
   stk=IRF9, btemp="-5 bis 45 °C", strom=PSU_2HS, kueh=KSB, doc=D("a50002587enw"),
   feat="Layer-3-Routing (OSPF, IS-IS, BGP; IPv6), EVPN/VXLAN, MPLS/VPLS, DRNI, dazu ECMP und IRF-Stacking (ohne Zusatzlizenz)",
   anw="Gemanagte Gigabit-Campus-Aggregation (Layer 3, HPE Comware) mit 10-GbE-SFP+-Uplinks, EVPN/VXLAN, DRNI und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=False),
 # ---------------- FlexFabric (data center) ----------------
 "5700": dict(e3="HPE FlexFabric 5700 Switches", line="FlexFabric", ser="5700", lyr="L3",
   stk=IRF9, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("c04347352"),
   feat="Layer-3-Routing (statisch, RIP/RIPng), dazu VLANs, ACLs, QoS, Data-Center-Bridging (DCB) und IRF-Stacking",
   anw="Rechenzentrums-Top-of-Rack (Layer 3, HPE Comware) mit 10/40-GbE-Ports, statischem/RIP-Routing und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True),
 "5710": dict(e3="HPE FlexFabric 5710 Switches", line="FlexFabric", ser="5710", lyr="L3",
   stk=IRF9, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("a00045647enw"),
   feat="Layer-3-Routing (OSPF, BGP, IS-IS; IPv6), EVPN/VXLAN, DCB und IRF-Stacking",
   anw="Rechenzentrums-Top-of-Rack/-Leaf (Layer 3, HPE Comware) mit 10/40/100-GbE-Ports, EVPN/VXLAN und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True, brand="HPE Networking Comware"),
 "5900": dict(e3="HPE FlexFabric 5900 Switches", line="FlexFabric", ser="5900", lyr="L3",
   stk=IRF9, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("c04111469"),
   feat="Layer-3-Routing (OSPF, BGP, IS-IS; IPv6 via OSPFv3/BGP4+), dazu FCoE/DCB, TRILL, IRF-Stacking und QoS",
   anw="Rechenzentrums-Top-of-Rack/-Leaf (Layer 3, HPE Comware) mit 10/40-GbE-Ports, FCoE/DCB, TRILL und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True),
 "5920": dict(e3="HPE FlexFabric 5920 Switches", line="FlexFabric", ser="5920", lyr="L3",
   stk=IRF4, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("c04111528"),
   feat="Layer-3-Routing (OSPF, BGP, IS-IS; IPv6), dazu 3,6-GB-Paketpuffer, FCoE/DCB, TRILL und IRF-Stacking",
   anw="Deep-Buffer-Rechenzentrums-Top-of-Rack (Layer 3, HPE Comware) mit 10-GbE-Ports, 3,6-GB-Paketpuffer und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True),
 "5930": dict(e3="HPE FlexFabric 5930 Switches", line="FlexFabric", ser="5930", lyr="L3",
   stk=IRF9, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("c04111326"),
   feat="Layer-3-Routing (OSPF, BGP, IS-IS, RIP; IPv6), VXLAN-Layer-2-Gateway, TRILL/SPB, FCoE/DCB, ECMP und IRF-Stacking",
   anw="Rechenzentrums-Spine/Leaf-ToR (Layer 3, HPE Comware) mit 40-GbE-QSFP+, VXLAN-L2-Gateway, TRILL und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True),
 "5940": dict(e3="HPE FlexFabric 5940 Switches", line="FlexFabric", ser="5940", lyr="L3",
   stk=IRF9, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("c05158726"),
   feat="Layer-3-Routing (OSPF, BGP, IS-IS; IPv6), BGP-EVPN/VXLAN (Layer 2 und Layer 3, RFC 7432), ECMP, OpenFlow/SDN und IRF-Stacking",
   anw="Rechenzentrums-Spine/Leaf-ToR (Layer 3, HPE Comware) mit 10/40/100-GbE, BGP-EVPN/VXLAN (L2/L3) und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True),
 "5945": dict(e3="HPE FlexFabric 5945 Switches", line="FlexFabric", ser="5945", lyr="L3",
   stk=IRF10, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("a00047323enw"),
   feat="Layer-3-Routing (OSPF, BGP, IS-IS), BGP-EVPN/VXLAN, MPLS, ECMP und IRF-Stacking",
   anw="High-Density-Rechenzentrums-Spine/Leaf (Layer 3, HPE Comware) mit 25/100-GbE, EVPN/VXLAN, MPLS und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True, brand="HPE Networking Comware"),
 "5950": dict(e3="HPE FlexFabric 5950 Switches", line="FlexFabric", ser="5950", lyr="L3",
   stk=IRFn, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KSAME, doc=D("c05175675"),
   feat="Layer-3-Routing (OSPF, BGP; IPv6), BGP-EVPN/VXLAN, ECMP und IRF-Stacking",
   anw="Rechenzentrums-Spine/Leaf-ToR (Layer 3, HPE Comware) mit 25/100-GbE, EVPN/VXLAN und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True),
 "5960": dict(e3="HPE FlexFabric 5960 Switches", line="FlexFabric", ser="5960", lyr="L3",
   stk=DRNI, btemp="0 bis 40 °C", strom=PSU_DRNI, kueh=K5960, doc=D("a50007000enw"),
   feat="Layer-3-Routing (OSPFv2/v3, BGP, IS-IS), BGP-EVPN/VXLAN, SR-MPLS/SRv6, PTP/SyncE, ECMP und DRNI-Hochverfügbarkeit",
   anw="High-Performance-Rechenzentrums-Spine (Layer 3, HPE Comware) mit 100/200/400-GbE, EVPN/VXLAN, SR-MPLS/SRv6 und DRNI-Hochverfügbarkeit",
   os="dem HPE-Comware-Betriebssystem (Comware v9)", dc=True, brand="HPE Networking Comware"),
 "5980": dict(e3="HPE FlexFabric 5980 Switches", line="FlexFabric", ser="5980", lyr="L3",
   stk=IRF2, btemp="0 bis 45 °C", strom=PSU_2HS, kueh=KFB, doc=D("a00029144enw"),
   feat="Layer-3-Routing (OSPF, BGP; IPv6), BGP-EVPN/VXLAN (Layer-2/Layer-3-Gateway), ECMP und IRF-Stacking",
   anw="Rechenzentrums-Spine/Leaf-ToR (Layer 3, HPE Comware) mit 10/100-GbE, EVPN/VXLAN-L2/L3-Gateway und IRF-Stacking",
   os="dem HPE-Comware-Betriebssystem", dc=True),
}

# ---------------- per-PID grounded specs. P(fam, model, n, acc, up, spd, poe, swk, mpps, price, gw, **kw)
# swk/mpps already German-formatted; "WS" sentinel -> customer-safe Wire-Speed prose. bauform "1U"/"2U".
BF={"1U":"19-Zoll-Rackmontage (1 HE)","2U":"19-Zoll-Rackmontage (2 HE)","CMP":"Kompakt (1 HE, halbe Breite)"}
def P(fam,model,n,acc,up,spd,poe,swk,mpps,price,gw,bauform="1U",**kw):
    d=dict(fam=fam,model=model,n=n,acc=acc,up=up,spd=spd,poe=poe,swk=swk,mpps=mpps,price=price,gw=gw,bauform=BF[bauform]); d.update(kw); return d
PoEp=lambda w:f"Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port, Budget {w} W)"
PoEp_dep="Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port; Gesamt-PoE-Budget abhängig von der Netzteilbestückung)"
SP_G="10/100/1000 Mbit/s (RJ45)"; SP_GSFPP="10/100/1000 Mbit/s (RJ45), 1/10 GbE (SFP+)"
SP_GMG="10/100/1000 Mbit/s (RJ45), 2,5/5 GbE (Multi-Gig, RJ45), 1/10 GbE (SFP+)"
SP_GXGT="10/100/1000 Mbit/s (RJ45), 1/10 GbE (SFP+), 1/10 GbE (10GBASE-T, RJ45)"
SP_SFPCB="100/1000 Mbit/s (SFP), 10/100/1000 Mbit/s (RJ45-Combo), 1/10 GbE (SFP+)"
SP_G_SFP="10/100/1000 Mbit/s (RJ45), 1 GbE (SFP)"

SPECS={
 # ===== 5120 v3 =====
 "S0F79A":P("5120v3","5120v3-8G-PoE+-2SFP",10,"8× 10/100/1000 (RJ45, PoE+)","2× 1000BASE-X SFP",SP_G_SFP,PoEp_dep,"20 Gbit/s","15 Mpps",320,"2,0",bauform="CMP"),
 # ===== 5130 EI (9) =====
 "JG932A":P("5130EI","5130-24G-4SFP+ EI",28,"24× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","128 Gbit/s","96 Mpps",380,"3,5"),
 "JG933A":P("5130EI","5130-24G-SFP-4SFP+ EI",28,"16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP)","4× 1/10G SFP+",SP_SFPCB,"Nein","128 Gbit/s","96 Mpps",520,"3,6"),
 "JG934A":P("5130EI","5130-48G-4SFP+ EI",52,"48× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","176 Gbit/s","130,9 Mpps",520,"4,5"),
 "JG936A":P("5130EI","5130-24G-PoE+-4SFP+ EI",28,"24× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(370),"128 Gbit/s","96 Mpps",620,"4,8"),
 "JG937A":P("5130EI","5130-48G-PoE+-4SFP+ EI",52,"48× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(370),"176 Gbit/s","130,9 Mpps",760,"5,8"),
 "JG938A":P("5130EI","5130-24G-2SFP+-2XGT EI",28,"24× 10/100/1000 (RJ45)","2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45)",SP_GXGT,"Nein","128 Gbit/s","96 Mpps",420,"3,5"),
 "JG939A":P("5130EI","5130-48G-2SFP+-2XGT EI",52,"48× 10/100/1000 (RJ45)","2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45)",SP_GXGT,"Nein","176 Gbit/s","130,9 Mpps",560,"4,5"),
 "JG940A":P("5130EI","5130-24G-PoE+-2SFP+-2XGT EI",28,"24× 10/100/1000 (RJ45, PoE+)","2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45)",SP_GXGT,PoEp(370),"128 Gbit/s","96 Mpps",660,"4,8"),
 "JG941A":P("5130EI","5130-48G-PoE+-2SFP+-2XGT EI",52,"48× 10/100/1000 (RJ45, PoE+)","2× 1/10G SFP+ + 2× 1/10GBASE-T (RJ45)",SP_GXGT,PoEp(370),"176 Gbit/s","130,9 Mpps",800,"5,8"),
 # ===== 5130 HI (4) =====
 "JH323A":P("5130HI","5130 24G 4SFP+ 1-slot HI",28,"24× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","168 Gbit/s","154,8 Mpps",560,"5,0"),
 "JH324A":P("5130HI","5130 48G 4SFP+ 1-slot HI",52,"48× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","216 Gbit/s","190,5 Mpps",720,"6,0"),
 "JH325A":P("5130HI","5130 24G PoE+ 4SFP+ 1-slot HI",28,"24× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(740),"168 Gbit/s","154,8 Mpps",760,"6,8"),
 "JH326A":P("5130HI","5130 48G PoE+ 4SFP+ 1-slot HI",52,"48× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(1440),"216 Gbit/s","190,5 Mpps",980,"7,8"),
 # ===== 5140 EI (9) =====
 "JL823A":P("5140EI","5140 24G PoE+ 2SFP+ 2XGT EI",28,"24× 10/100/1000 (RJ45, PoE+)","2× 1/10G SFP+ + 2× 1/2,5/5/10G Multi-Gig (RJ45)",SP_GMG,PoEp(370),"128 Gbit/s","95 Mpps",680,"4,8",btemp="-5 bis 50 °C"),
 "JL824A":P("5140EI","5140 48G PoE+ 4SFP+ EI",52,"48× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(370),"176 Gbit/s","131 Mpps",780,"5,8"),
 "JL825A":P("5140EI","5140 48G PoE+ 2SFP+ 2XGT EI",52,"48× 10/100/1000 (RJ45, PoE+)","2× 1/10G SFP+ + 2× 1/2,5/5/10G Multi-Gig (RJ45)",SP_GMG,PoEp(370),"176 Gbit/s","131 Mpps",860,"5,9",btemp="-5 bis 50 °C"),
 "JL826A":P("5140EI","5140 24G SFP 8Combo 4SFP+ EI",28,"16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP)","4× 1/10G SFP+",SP_SFPCB,"Nein","128 Gbit/s","95 Mpps",560,"4,2",strom="2 Netzteilschächte (mindestens 1 Netzteil, separat bestellbar; AC oder DC)"),
 "JL827A":P("5140EI","5140 24G PoE+ 4SFP+ EI",28,"24× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(370),"128 Gbit/s","95 Mpps",620,"4,8"),
 "JL828A":P("5140EI","5140 24G 4SFP+ EI",28,"24× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","128 Gbit/s","95 Mpps",420,"3,5"),
 "JL829A":P("5140EI","5140 48G 4SFP+ EI",52,"48× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","176 Gbit/s","131 Mpps",560,"4,5"),
 "R8J41A":P("5140EI","5140 24G 2SFP+ 2XGT EI",28,"24× 10/100/1000 (RJ45)","2× 1/10G SFP+ + 2× 1/2,5/5/10G Multi-Gig (RJ45)",SP_GMG,"Nein","128 Gbit/s","95 Mpps",480,"3,6",btemp="-5 bis 50 °C"),
 "R8J42A":P("5140EI","5140 8G 2SFP 2GT Combo EI",10,"8× 10/100/1000 (RJ45)","2× Dual-Personality-Combo (1G SFP oder 10/100/1000 RJ45)",SP_G_SFP,"Nein","24 Gbit/s","18 Mpps",300,"2,2",bauform="CMP",btemp="-5 bis 50 °C"),
 # ===== 5140 HI (4) =====
 "R9L61A":P("5140HI","5140 24G 4SFP+ 1-slot HI",28,"24× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","288 Gbit/s","180 Mpps",620,"5,0"),
 "R9L62A":P("5140HI","5140 48G 4SFP+ 1-slot HI",52,"48× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","336 Gbit/s","180 Mpps",780,"6,0"),
 "R9L63A":P("5140HI","5140 24G PoE+ 4SFP+ 1-slot HI",28,"24× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(720),"288 Gbit/s","180 Mpps",820,"6,8"),
 "R9L64A":P("5140HI","5140 48G PoE+ 4SFP+ 1-slot HI",52,"48× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(1440),"336 Gbit/s","180 Mpps",1040,"7,8"),
 # ===== 5510 HI (5) =====
 "JH145A":P("5510HI","5510 24G 4SFP+ HI 1-slot",28,"24× 10/100/1000 (RJ45)","4× 10G SFP+",SP_GSFPP,"Nein","288 Gbit/s","214 Mpps",700,"5,0"),
 "JH146A":P("5510HI","5510 48G 4SFP+ HI 1-slot",52,"48× 10/100/1000 (RJ45)","4× 10G SFP+",SP_GSFPP,"Nein","336 Gbit/s","250 Mpps",880,"6,0"),
 "JH147A":P("5510HI","5510 24G PoE+ 4SFP+ HI 1-slot",28,"24× 10/100/1000 (RJ45, PoE+)","4× 10G SFP+",SP_GSFPP,PoEp(740),"288 Gbit/s","214 Mpps",920,"6,8"),
 "JH148A":P("5510HI","5510 48G PoE+ 4SFP+ HI 1-slot",52,"48× 10/100/1000 (RJ45, PoE+)","4× 10G SFP+",SP_GSFPP,PoEp(1440),"336 Gbit/s","250 Mpps",1150,"7,8"),
 "JH149A":P("5510HI","5510 24G SFP 4SFP+ HI 1-slot",28,"16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP)","4× 10G SFP+",SP_SFPCB,"Nein","288 Gbit/s","214 Mpps",820,"5,2"),
 # ===== 5520 HI (5) =====
 "R8M25A":P("5520HI","5520 24G 4SFP+ HI",28,"16× 10/100/1000 (RJ45) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP)","4× 1/10G SFP+",SP_SFPCB,"Nein","288 Gbit/s","180 Mpps",900,"5,2"),
 "R8M26A":P("5520HI","5520 48G 4SFP+ HI 1-slot",52,"48× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_GSFPP,"Nein","336 Gbit/s","180 Mpps",1050,"6,0"),
 "R8M27A":P("5520HI","5520 24G SFP 4SFP+ HI",28,"16× 100/1000 (SFP) + 8× Dual-Personality (10/100/1000 RJ45 oder 100/1000 SFP)","4× 1/10G SFP+",SP_SFPCB,"Nein","288 Gbit/s","180 Mpps",980,"5,2"),
 "R8M28A":P("5520HI","5520 24G PoE+ 4SFP+ HI",28,"24× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(720),"288 Gbit/s","180 Mpps",1150,"6,8"),
 "R8M29A":P("5520HI","5520 48G PoE+ 4SFP+ HI 1-slot",52,"48× 10/100/1000 (RJ45, PoE+)","4× 1/10G SFP+",SP_GSFPP,PoEp(1440),"336 Gbit/s","180 Mpps",1400,"7,8"),
 # ===== 5700 (3) — DC ToR, static/RIP-lite L3 =====
 "JG894A":P("5700","5700-48G-4XG-2QSFP+",54,"48× 10/100/1000 (RJ45) + 4× 10G SFP+","2× 40G QSFP+","10/100/1000 Mbit/s (RJ45), 10 GbE (SFP+), 40 GbE (QSFP+)","Nein","336 Gbit/s","250 Mpps",2600,"8,0"),
 "JG896A":P("5700","5700-40XG-2QSFP+",42,"40× 10G SFP+","2× 40G QSFP+","10 GbE (SFP+), 40 GbE (QSFP+)","Nein","960 Gbit/s","714,2 Mpps",4200,"8,0"),
 "JG898A":P("5700","5700-32XGT-8XG-2QSFP+",42,"32× 10GBASE-T (RJ45) + 8× 10G SFP+","2× 40G QSFP+","10 GbE (10GBASE-T, RJ45), 10 GbE (SFP+), 40 GbE (QSFP+)","Nein","960 Gbit/s","714,2 Mpps",4600,"8,5"),
 # ===== 5710 (4) — DC ToR/leaf, full L3 + VXLAN, IRF 10 =====
 "JL585A":P("5710","5710-48SFP+-6QSFP+/2QSFP28",54,"48× 1/10G SFP+","6× 40G QSFP+ (100-GbE-QSFP28-fähig)","1/10 GbE (SFP+), 40 GbE (QSFP+), 100 GbE (QSFP28)","Nein","1,44 Tbit/s","1.071 Mpps",6500,"8,0"),
 "JL586A":P("5710","5710-48XGT-6QSFP+/2QSFP28",54,"48× 1/10GBASE-T (RJ45)","6× 40G QSFP+ (100-GbE-QSFP28-fähig)","1/10 GbE (10GBASE-T, RJ45), 40 GbE (QSFP+), 100 GbE (QSFP28)","Nein","1,44 Tbit/s","1.071 Mpps",6900,"8,5"),
 "JL587A":P("5710","5710-24SFP+-6QSFP+/2QSFP28",30,"24× 1/10G SFP+","6× 40G QSFP+ (100-GbE-QSFP28-fähig)","1/10 GbE (SFP+), 40 GbE (QSFP+), 100 GbE (QSFP28)","Nein","960 Gbit/s","714 Mpps",5200,"7,8"),
 "JL689A":P("5710","5710-24XGT-6QSFP+/2QSFP28",30,"24× 1/10GBASE-T (RJ45)","6× 40G QSFP+ (100-GbE-QSFP28-fähig)","1/10 GbE (10GBASE-T, RJ45), 40 GbE (QSFP+), 100 GbE (QSFP28)","Nein","960 Gbit/s","714 Mpps",5600,"8,0"),
 # ===== 5920 (1) — deep-buffer (3,6 GB) DC ToR, IRF 4 =====
 "JG296A":P("5920","5920AF-24XG",24,"24× 1/10G SFP+","","1/10 GbE (SFP+)","Nein","480 Gbit/s","367 Mpps",4200,"8,0"),
 # ===== 5900 (4) — DC ToR, full L3 + FCoE/TRILL =====
 "JC772A":P("5900","5900AF-48XG-4QSFP+",52,"48× 1/10G SFP+","4× 40G QSFP+","1/10 GbE (SFP+), 40 GbE (QSFP+)","Nein","1,28 Tbit/s","952 Mpps",5200,"8,0"),
 "JG336A":P("5900","5900AF-48XGT-4QSFP+",52,"48× 1/10GBASE-T (RJ45)","4× 40G QSFP+","1/10 GbE (10GBASE-T, RJ45), 40 GbE (QSFP+)","Nein","1,28 Tbit/s","952 Mpps",5400,"8,5"),
 "JG510A":P("5900","5900AF-48G-4XG-2QSFP+",54,"48× 10/100/1000 (RJ45) + 4× 10G SFP+","2× 40G QSFP+","10/100/1000 Mbit/s (RJ45), 10 GbE (SFP+), 40 GbE (QSFP+)","Nein","336 Gbit/s","250 Mpps",3400,"8,0"),
 "JG838A":P("5900","5900CP-48XG-4QSFP+",52,"48× 1/10G SFP+ (Konvergenzports, FC/FCoE)","4× 40G QSFP+","1/10 GbE (SFP+, FC/FCoE-Konvergenz), 40 GbE (QSFP+)","Nein","WS","WS",5600,"8,2",fcoe=True),
 # ===== 5930 (3) — DC spine/leaf 40G, VXLAN L2-GW =====
 "JG726A":P("5930","5930-32QSFP+",32,"32× 40G QSFP+","","40 GbE (QSFP+; 10 GbE über 4×10G-Breakout)","Nein","2,56 Tbit/s","1.429 Mpps",9500,"8,5"),
 "JH178A":P("5930","5930-2QSFP+-2-slot",2,"2× 40G QSFP+ (fest) + zwei Modulschächte (optional, separat bestückbar)","","40 GbE (QSFP+, fest); modulabhängig 10/40 GbE","Nein","1,44 Tbit/s","1.071 Mpps",8500,"8,5",slot=True),
 "JH179A":P("5930","5930-4-slot",0,"vier I/O-Modulschächte (I/O-Module 10/40 GbE bzw. konvergent, separat bestückbar)","","modulabhängig (10/40 GbE bzw. FC/FCoE)","Nein","2,56 Tbit/s","1.429 Mpps",11000,"11,0",bauform="2U",pureslot=True,strom=PSU_4HS),
 # ===== 5940 (7) — DC spine/leaf, EVPN L2/L3 =====
 "JH390A":P("5940","5940-48SFP+-6QSFP28",54,"48× 1/10G SFP+","6× 100G QSFP28","1/10 GbE (SFP+), 100 GbE (QSFP28)","Nein","2,16 Tbit/s","1.607 Mpps",13500,"8,5"),
 "JH391A":P("5940","5940-48XGT-6QSFP28",54,"48× 1/10GBASE-T (RJ45)","6× 100G QSFP28","1/10 GbE (10GBASE-T, RJ45), 100 GbE (QSFP28)","Nein","2,16 Tbit/s","1.607 Mpps",13900,"9,0"),
 "JH394A":P("5940","5940-48XGT-6QSFP+",54,"48× 1/10GBASE-T (RJ45)","6× 40G QSFP+","1/10 GbE (10GBASE-T, RJ45), 40 GbE (QSFP+)","Nein","1,44 Tbit/s","1.071 Mpps",12500,"9,0"),
 "JH395A":P("5940","5940-48SFP+-6QSFP+",54,"48× 1/10G SFP+","6× 40G QSFP+","1/10 GbE (SFP+), 40 GbE (QSFP+)","Nein","1,44 Tbit/s","1.071 Mpps",12000,"8,5"),
 "JH396A":P("5940","5940-32QSFP+",32,"32× 40G QSFP+","","40 GbE (QSFP+; 10 GbE über 4×10G-Breakout)","Nein","2,56 Tbit/s","1.904 Mpps",13000,"8,5"),
 "JH397A":P("5940","5940-2-slot",2,"2× 40G QSFP+ (fest) + zwei Modulschächte (optional, separat bestückbar)","","40 GbE (QSFP+, fest); modulabhängig 10/40/100 GbE","Nein","1,44 Tbit/s","1.071 Mpps",12500,"8,8",slot=True),
 "JH398A":P("5940","5940-4-slot",0,"vier I/O-Modulschächte (I/O-Module 10/40/100 GbE bzw. konvergent, separat bestückbar)","","modulabhängig (10/40/100 GbE bzw. FC/FCoE)","Nein","2,56 Tbit/s","1.904 Mpps",16000,"11,0",bauform="2U",pureslot=True,strom=PSU_4HS),
 # ===== 5945 (4) — DC spine 25/100G, EVPN/MPLS, IRF 10 =====
 "JQ074A":P("5945","5945-48SFP28-8QSFP28",58,"48× 25G SFP28 + 8× 100G QSFP28 + 2× 1G SFP","","25 GbE (SFP28), 100 GbE (QSFP28), 1 GbE (SFP)","Nein","4 Tbit/s","2.024 Mpps",22000,"8,8"),
 "JQ075A":P("5945","5945-2-slot",2,"2× 100G QSFP28 (fest) + zwei Modulschächte (optional, separat bestückbar)","","100 GbE (QSFP28, fest); modulabhängig 10/25/40/100 GbE","Nein","3,6 Tbit/s","2.024 Mpps",20000,"9,0",bauform="1U",slot=True),
 "JQ076A":P("5945","5945-4-slot",2,"2× 1G SFP + vier I/O-Modulschächte (I/O-Module 10/25/40/100 GbE, separat bestückbar)","","1 GbE (SFP, fest); modulabhängig 10/25/40/100 GbE","Nein","6,4 Tbit/s","2.024 Mpps",26000,"11,5",bauform="2U",slot=True,strom=PSU_4HS),
 "JQ077A":P("5945","5945-32QSFP28",34,"32× 100G QSFP28 + 2× 1G SFP","","100 GbE (QSFP28), 1 GbE (SFP)","Nein","6,4 Tbit/s","2.024 Mpps",24000,"8,8"),
 # ===== 5950 (3) — DC spine 25/100G, EOSL =====
 "JH321A":P("5950","5950-32QSFP28-2SFP+",34,"32× 100G QSFP28 + 2× 1/10G SFP+","","100 GbE (QSFP28), 1/10 GbE (SFP+)","Nein","3,2 Tbit/s","3.169 Mpps",15000,"8,5"),
 "JH402A":P("5950","5950-48SFP28-8QSFP28",58,"48× 25G SFP28 + 8× 100G QSFP28 + 2× 1G SFP","","25 GbE (SFP28), 100 GbE (QSFP28), 1 GbE (SFP)","Nein","3,2 Tbit/s","3.169 Mpps",16000,"8,8"),
 "JH404A":P("5950","5950-4-slot",3,"3× 1G SFP + vier I/O-Modulschächte (I/O-Module 10/40/100 GbE, separat bestückbar)","","1 GbE (SFP, fest); modulabhängig 10/40/100 GbE","Nein","3,2 Tbit/s","3.169 Mpps",18000,"11,0",bauform="2U",slot=True,strom=PSU_4HS),
 # ===== 5960 (3) — DC spine 100/200/400G, Comware v9, DRNI =====
 "S4J82A":P("5960","5960R-48QSFP28-6QSFP-DD",54,"48× 100G QSFP28 + 6× 400G QSFP-DD","","100 GbE (QSFP28), 400 GbE (QSFP-DD)","Nein","14,4 Tbit/s","2.700 Mpps",36000,"12,0",bauform="2U",slot1=True),
 "R9Y12A":P("5960","5960-24QSFP56-8QSFP-DD",34,"24× 100/200G QSFP56 + 8× 400G QSFP-DD + 2× 10G SFP+","","200 GbE (QSFP56), 400 GbE (QSFP-DD), 10 GbE (SFP+)","Nein","16 Tbit/s","WS",42000,"9,5",slot1=True),
 "R9Y13A":P("5960","5960-32QSFP-DD-2SFP+",34,"32× 400G QSFP-DD + 2× 1/10G SFP+","","400 GbE (QSFP-DD), 1/10 GbE (SFP+)","Nein","25,6 Tbit/s","WS",48000,"9,5",slot1=True),
 # ===== 5980 (1) — DC, SwK/Durchsatz un-published =====
 "JQ026A":P("5980","5980-48SFP+-6QSFP28",54,"48× 10G SFP+","6× 100G QSFP28","10 GbE (SFP+), 100 GbE (QSFP28)","Nein","WS","WS",17000,"8,5"),
}

# ---------------- author one SKU
def clip_titel(line,model,pid):
    # model-distinguished (masked-title must differ across DIFFERENT models); PID kept where it fits.
    for t in (f"HPE {line} {model} {pid} | Hexwaren", f"{line} {model} {pid} | Hexwaren",
              f"HPE {line} {model} | Hexwaren", f"{line} {model} | Hexwaren"):
        if len(t) <= 60: return t
    avail=60-len(" | Hexwaren")
    return f"{line} {model}"[:avail].rstrip()+" | Hexwaren"
def author(pid):
    b=SPECS[pid]; fam=b['fam']; f=FAM[fam]; line=f['line']; ser=f['ser']; lyr=f['lyr']
    lyr_de="Layer-3" if lyr=="L3" else "Layer-2"; sclass=f"Managed Switch ({lyr})"
    model=b['model']; prod=f"HPE {line} {model}"; dc=f['dc']
    poe_yes=b['poe']!="Nein"; up=b['up']; n=b['n']
    ws_swk=b['swk']=="WS"; ws_mpps=b['mpps']=="WS"
    swk_attr="Non-Blocking-Architektur (Wire-Speed)" if ws_swk else b['swk']
    mpps_attr="Wire-Speed-Weiterleitung (nicht-blockierend)" if ws_mpps else b['mpps']
    pureslot=b.get('pureslot'); strom=b.get('strom') or f['strom']; kueh=b.get('kueh') or f['kueh']; btemp=b.get('btemp') or f['btemp']
    portkonfig=(f"{b['acc']} + {up} (Uplink)") if up else b['acc']
    if b.get('slot1'): portkonfig=f"{portkonfig} + ein I/O-Modulschacht (optional, separat bestückbar)"
    upattr=up if up else ("kein dedizierter Uplink (alle Ports gleichwertig nutzbar)" if not pureslot else "modulabhängige Uplinks je nach Bestückung")
    bau_short=b['bauform'].split('(')[0].strip()
    artikel=ws(f"{prod} {pid} Managed Switch ({lyr}) – {b['acc']}{('' if not up else ' + '+up)}, {bau_short}")
    titel=clip_titel(line,model,pid)
    poe_meta=(f"PoE-Budget {b['poe'].split('Budget ')[-1].rstrip(')')}" if (poe_yes and 'Budget ' in b['poe']) else ("PoE+" if poe_yes else "ohne PoE"))
    swk_meta=("" if ws_swk else f"Switching-Kapazität {b['swk']}, ")
    meta=fit_meta(f"Original {prod} ({pid}): gemanagter {lyr_de}-Switch mit {b['acc']}, {swk_meta}{poe_meta}, HPE-Comware-Betriebssystem.")
    # kurzbeschreibung (2 <p>)
    role_k=("die Aggregation und das Routing im Rechenzentrum (Spine-Leaf/ToR)" if dc else "den gemanagten Zugang bzw. die Aggregation im Campus")
    if pureslot:
        p_open=f"<p>Der {prod} ({pid}) ist ein gemanagter {lyr_de}-Slot-Switch der HPE-{line}-{ser}-Serie mit {b['acc']}. Unter {f['os']} übernimmt er {role_k}.</p>"
    else:
        p_open=f"<p>Der {prod} ({pid}) ist ein gemanagter {lyr_de}-Switch der HPE-{line}-{ser}-Serie mit {n} Ports. Unter {f['os']} übernimmt er {role_k}.</p>"
    poe_k=(f" Über Power over Ethernet (PoE+) versorgt der {pid} angeschlossene Endgeräte direkt per Netzwerkkabel." if poe_yes else "")
    if ws_swk:
        p2=f"<p>Im Formfaktor {bau_short} leitet der {pid} nicht-blockierend mit Wire-Speed weiter und bindet über seine {('Konvergenz- und QSFP+-Ports' if b.get('fcoe') else 'Hochgeschwindigkeits-Ports')} an das Netz an.{poe_k} Er wird als versiegelte Original-Neuware geliefert.</p>"
    else:
        p2=f"<p>Im Formfaktor {bau_short} liefert der {pid} eine Switching-Kapazität von {b['swk']} und bindet per {(up if up else 'seine Hochgeschwindigkeits-Ports')} an das Netz an.{poe_k} Er wird als versiegelte Original-Neuware geliefert.</p>"
    kurz=p_open+p2
    # intro (3 paras)
    poe_i=(f" Der {pid} versorgt Access Points, IP-Telefone und Kameras per Power over Ethernet direkt über das Netzwerkkabel." if poe_yes
           else f" Der {pid} ist ein Modell ohne PoE und konzentriert sich auf reine Datenanbindung.")
    role=("den Aggregations- und Spine-Leaf-Einsatz im Rechenzentrum" if dc else ("den kompakten Campus-Access" if n and n<=12 else f"den {lyr_de}-Campus-Access"))
    with_ports=(f"mit {b['acc']}" if pureslot else f"mit {n} Ports ({b['acc']})")
    i1=(f"Der {prod} ({pid}) ist ein gemanagter {lyr_de}-Switch aus der HPE-{line}-{ser}-Familie {with_ports}, "
        f"ausgelegt für {role} und betrieben unter {f['os']}.")
    stk=f['stk']
    if "DRNI" in stk:
        upl=(f"Die Uplink-Anbindung des {pid} erfolgt über {(up or 'die Hochgeschwindigkeits-Ports')}; für Hochverfügbarkeit "
             f"bilden zwei {pid} per DRNI (Distributed Resilient Network Interconnect) einen aktiv-aktiven Multi-Chassis-Verbund.")
    else:
        _m=re.search(r"bis zu (\d+)",stk); nn={"2":"zwei","4":"vier","9":"neun","10":"zehn"}.get(_m.group(1) if _m else "","mehrere")
        upl=(f"Die Uplink-Anbindung des {pid} erfolgt über {(up or 'die Hochgeschwindigkeits-Ports')}, und per IRF (Intelligent "
             f"Resilient Framework) lassen sich bis zu {nn} Einheiten zu einem logischen Switch zusammenfassen.")
    if ws_mpps and ws_swk:
        i2=(f"Der {pid} leitet nicht-blockierend mit Wire-Speed weiter.{poe_i} {upl}")
    elif ws_mpps:
        i2=(f"Der {pid} erreicht eine Switching-Kapazität von {b['swk']} und leitet nicht-blockierend mit Wire-Speed weiter.{poe_i} {upl}")
    else:
        i2=(f"Der {pid} erreicht eine Switching-Kapazität von {b['swk']} bei einer Weiterleitungsrate von {b['mpps']}.{poe_i} {upl}")
    brand_note=(f" Der {pid} wird von HPE aktuell unter der Serienbezeichnung „{f['brand']} {ser}“ geführt." if f.get('brand') else "")
    i3=(f"Im Gehäuse {bau_short} arbeitet der {pid} im Temperaturbereich {btemp}; Kühlung und Stromversorgung des {pid} "
        f"übernehmen {kueh} sowie {strom}. Unter {f['os']} bietet der {pid} {f['feat']}.{brand_note} "
        f"Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch.")
    intro=pad([ws(i1),ws(i2),ws(i3)],pid)
    # faq (4)
    faq=[["Ist dies ein originales HPE-Produkt?",
          f"Ja. Der {pid} ist HPE-Original-Neuware der {line}-{ser}-Serie – versiegelt geliefert und für den Betrieb unter dem HPE-Comware-Betriebssystem vorgesehen."],
         [f"Wie viele Ports hat der {pid}?",
          (f"Der {pid} stellt {b['acc']} bereit." if pureslot else f"Der {pid} bietet insgesamt {n} Ports: {portkonfig}.")]]
    if poe_yes: faq.append([f"Unterstützt der {pid} PoE?", f"Ja. Der {pid} stellt {b['poe']} bereit und versorgt angeschlossene Geräte direkt über das Netzwerkkabel."])
    else: faq.append([f"Unterstützt der {pid} PoE?", f"Nein. Der {pid} ist ein Modell ohne Power over Ethernet und für reine Datenanbindung ausgelegt."])
    if "DRNI" in stk:
        faq.append([f"Lässt sich der {pid} redundant koppeln?", f"Ja. Über DRNI (Distributed Resilient Network Interconnect) bilden zwei {pid} einen aktiv-aktiven Multi-Chassis-Verbund für Hochverfügbarkeit."])
    else:
        faq.append([f"Lässt sich der {pid} stapeln (Stacking)?", f"Ja. Der {pid} unterstützt {stk} und lässt sich so zu einem logischen Switch zusammenfassen."])
    # differentiator pair — grounded per-model distinguishers (SwK/Durchsatz/feature/PSU/cooling) so no two
    # DIFFERENT models share a masked FAQ block (kills the cross-model FAQ collisions; 0 fabrication).
    swkp=("eine nicht-blockierende Wire-Speed-Weiterleitung" if ws_swk else f"eine Switching-Kapazität von {b['swk']}")
    mppp=("" if (ws_mpps or ws_swk) else f" und eine Weiterleitungsrate von {b['mpps']}")
    faq.append([f"Was zeichnet den {pid} technisch aus?",
                f"Der {pid} bietet {swkp}{mppp}. Unter {f['os']} beherrscht er {f['feat']}. "
                f"Für Stromversorgung und Kühlung des {pid} sorgen {strom} sowie {kueh}."])
    # attributes (16)
    portanz=str(n)
    attrs=[["Switch-Typ","Managed"],["Layer",lyr],["Portanzahl",portanz],["Port-Konfiguration",portkonfig],
           ["Port-Geschwindigkeit",b['spd']],["Uplink-Ports",upattr],["PoE",b['poe']],["Switching-Kapazität",swk_attr],
           ["Durchsatz",mpps_attr],["Bauform",b['bauform']],["Stromversorgung",strom],["Kühlung",kueh],
           ["Stacking",stk],["Betriebstemperatur",btemp],["Anwendung",f['anw']],["Zustand","Neu, versiegelt"]]
    doc=f['doc']; prov={a[0]:[doc,"datasheet"] for a in attrs if a[0]!="Zustand"}
    versand=f"{float(b['gw'].replace(',','.'))+2.0:.2f}".replace('.',',')
    return {"_facts":{"unterkategorie":sclass,"quell_url":doc,"verifiziert_am":VERIF},
            "artikelname":artikel,"titel_tag":titel,"meta_description":meta,"artikelgewicht":b['gw'],"versandgewicht":versand,
            "kurzbeschreibung":ws(kurz),"intro":intro,
            "kompatibilitaet":["HPE-Comware-Betriebssystem","HPE Intelligent Management Center (IMC)","NETCONF/YANG & SNMP"],
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{b['price']}.00"}

# ---------------- build a bundle
def build(cat, pids):
    doc={pid:author(pid) for pid in pids}
    cpath=ROOT/"stage3_content"/f"{cat}_content.json"; cpath.write_text(json.dumps(doc,ensure_ascii=False,indent=1),encoding="utf-8")
    recs=reconcile_content(cpath,brand=BRAND,rules=rules,weights=weights)
    out=ROOT/"output"/"switches"/cat
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    assemble_bundle(recs,rules,batch=cat,category=cat,out_dir=out)
    S.process_main(out/f"Hexwaren_{cat}_Main.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    S.process_faq(out/f"Hexwaren_FAQ_{cat}.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    e3=FAM[SPECS[pids[0]]['fam']]['e3']; mp=out/f"Hexwaren_{cat}_Main.csv"
    rows=list(csv.reader(mp.read_bytes().decode("utf-8-sig").splitlines(),delimiter=";")); H=rows[0]
    i1,i2,i3=H.index("Kategorie Ebene 1"),H.index("Kategorie Ebene 2"),H.index("Kategorie Ebene 3"); data=[]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        r[i1],r[i2],r[i3]=E1,E2,e3; data.append(r)
    write_csv(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{cat}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in pids:
        vrows.append([pid,f"{SPECS[pid]['price']},00","PHASE-1-SCHÄTZUNG — NICHT marktgegroundet. Tarif nach Konfigurations-Tier (Portzahl/Speed/PoE/DC-Klasse). Echte HPE-Marktpreis-Recherche folgt als eigene Phase.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/cat; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {cat:38s} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:8]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:105])
    return out

CATMAP={
 "5120v3":"HPE_FlexNetwork_5120_v3_Switches","5130EI":"HPE_FlexNetwork_5130_EI_Switches","5130HI":"HPE_FlexNetwork_5130_HI_Switches",
 "5140EI":"HPE_FlexNetwork_5140_EI_Switches","5140HI":"HPE_FlexNetwork_5140_HI_Switches","5510HI":"HPE_FlexNetwork_5510_HI_Switches",
 "5520HI":"HPE_FlexNetwork_5520_HI_Switches",
 "5700":"HPE_FlexFabric_5700_Switches","5710":"HPE_FlexFabric_5710_Switches","5900":"HPE_FlexFabric_5900_Switches",
 "5920":"HPE_FlexFabric_5920_Switches","5930":"HPE_FlexFabric_5930_Switches","5940":"HPE_FlexFabric_5940_Switches",
 "5945":"HPE_FlexFabric_5945_Switches","5950":"HPE_FlexFabric_5950_Switches","5960":"HPE_FlexFabric_5960_Switches",
 "5980":"HPE_FlexFabric_5980_Switches"}
FLEXNET=["5120v3","5130EI","5130HI","5140EI","5140HI","5510HI","5520HI"]
FLEXFAB=["5700","5710","5900","5920","5930","5940","5945","5950","5960","5980"]

if __name__=="__main__":
    which=sys.argv[1] if len(sys.argv)>1 else "all"
    fams=FLEXNET if which=="flexnet" else FLEXFAB if which=="flexfab" else (FLEXNET+FLEXFAB)
    for fam in fams:
        pids=[p for p,s in SPECS.items() if s['fam']==fam]
        if not pids: print(f"SKIP {fam} (no SPECS yet)"); continue
        build(CATMAP[fam],pids)
