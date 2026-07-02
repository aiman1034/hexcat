# -*- coding: utf-8 -*-
"""STEP-2 Phase-1 SMB: Aruba Instant On fixed switches — 1960 (5) + 1930 (7+3 B-rev) + 1830 (6) + 1430 (7) = 28 SKUs.
Validated 15-Merkmal FIXED-switch schema, REUSED verbatim; 0 new Merkmal NAMES. Hersteller=HP, BRAND="Aruba"
(slug hpe-aruba). Per-PID SwK/Durchsatz VERBATIM from OEM Instant On data sheets (_scratch/ground/IO-*.md), never
port-math. Tiers: 1960/1930 = Managed (L2+, static routing; 1960 True-Stacks ×4); 1830 = Smart-Managed (pure L2);
1430 = UNMANAGED (Switch-Typ=Unmanaged, Layer=L2, Stacking SUPPRESSED per operator ruling). Instant On cloud/app
register (no on-box CLI). Prices = Phase-1 ESTIMATE (flagged). 1430 weights grounded; 1830/1930/1960 weights
estimated (verify fleet re-checks). $0 prose. Reuses locked reconcile->assemble->scrub->remap->gate pipeline."""
import json, re, shutil, tempfile, csv, sys
from pathlib import Path
sys.path.insert(0, "_scratch")
from hexcat.config import load_rules, load_weights
from hexcat.stage3 import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat.writers import write_csv
from hexcat import constants as C
import scrub_uwg as S

ROOT = Path("."); rules, weights = load_rules(), load_weights()
BRAND = "Aruba"; E1, E2 = "Netzwerk & Infrastruktur", "Switches"; VERIF = "2026-07-02"
def ws(s): return re.sub(r"\s+", " ", s).strip()
def wc(html): return len(re.sub(r"<[^>]+>", "", html).split())
PAD = ["Der {pid} wird als versiegelte Original-Neuware geliefert und eignet sich für den Erstaufbau ebenso "
       "wie für die planbare Ersatzbeschaffung.",
       "Vor dem Einsatz des {pid} empfiehlt sich ein kurzer Abgleich von Portzahl, PoE-Bedarf und Montageart, "
       "um den Switch ohne Nacharbeit in Betrieb zu nehmen."]
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

IO_CLOUD=["Aruba Instant On Cloud-Portal","Aruba Instant On Mobile-App","Lokale Web-GUI und SNMP"]
IO_PNP=["Plug-and-Play (kein Management erforderlich)"]
D=lambda i:f"https://www.hpe.com/psnow/doc/{i}"
FAM = {
 "1960": dict(e3="Aruba Instant On 1960 Switches", ser="1960", styp="Managed", lyr="L2", sclass="Managed Switch (L2)",
   stk="Aruba Instant On True Stacking – bis zu 4 Einheiten, zentral über die Instant On Cloud verwaltet",
   btemp="0 bis 40 °C", doc=D("a00118137enw"), unmanaged=False, mgmt=IO_CLOUD,
   feat="Layer-2+-Funktionen mit statischem IPv4/IPv6-Routing, VLANs, ACLs, QoS, 802.1X und Aruba Instant On True Stacking",
   anw="Smart-managed SMB-/Campus-Aggregation (Layer 2+, Aruba Instant On) mit 10-GbE-Uplinks, statischem Routing und True Stacking",
   os="der Aruba Instant On Cloud (Portal und Mobile-App)"),
 "1930": dict(e3="Aruba Instant On 1930 Switches", ser="1930", styp="Managed", lyr="L2", sclass="Managed Switch (L2)",
   stk="Nein (kein Stacking; Link-Aggregation über LACP)",
   btemp="0 bis 40 °C", doc=D("a00098249enw"), unmanaged=False, mgmt=IO_CLOUD,
   feat="Layer-2+-Funktionen mit statischem IPv4-Routing (bis 32 Routen), VLANs, ACLs, QoS und 802.1X",
   anw="Smart-managed SMB-Zugang (Layer 2+, Aruba Instant On) mit statischem Routing, ACLs und cloud-basiertem Management",
   os="der Aruba Instant On Cloud (Portal und Mobile-App)"),
 "1830": dict(e3="Aruba Instant On 1830 Switches", ser="1830", styp="Smart-Managed", lyr="L2", sclass="Smart-Managed Switch",
   stk="Nein (kein Stacking; Link-Aggregation über LACP)",
   btemp="0 bis 40 °C", doc=D("a00119988enw"), unmanaged=False, mgmt=IO_CLOUD,
   feat="Layer-2-Funktionen (VLANs, Spanning Tree, LACP, QoS, 802.1X) unter cloud-basiertem Instant-On-Management, ohne Layer-3-Routing",
   anw="Smart-managed SMB-Zugang (Layer 2, Aruba Instant On) mit VLANs, QoS und cloud-basiertem Management",
   os="der Aruba Instant On Cloud (Portal und Mobile-App)"),
 "1430": dict(e3="Aruba Instant On 1430 Switches", ser="1430", styp="Unmanaged", lyr="L2", sclass="Unmanaged Switch",
   stk=None, btemp="0 bis 40 °C", doc=D("a50004290enw"), unmanaged=True, mgmt=IO_PNP,
   feat="Layer-2-Plug-and-Play-Weiterleitung mit automatischem QoS (802.1p/DSCP), Flusssteuerung, Jumbo-Frames und Energy Efficient Ethernet – ohne Konfiguration",
   anw="Unmanaged SMB-/Heimbüro-Zugang (Layer 2, Plug-and-Play) ohne Management, für einfache Netzerweiterung",
   os="Plug-and-Play (kein Management)"),
}

BF={"1U":"19-Zoll-Rackmontage (1 HE)","DT":"Desktop-/Wandmontage (kompakt)","DT1U":"Desktop-/1-HE-Rackmontage (kompakt)"}
def P(fam,model,n,acc,up,spd,poe,swk,mpps,price,gw,bauform="1U",kueh="Lüftergekühlt (variable Lüfterdrehzahl)",psu="Internes Netzteil",**kw):
    d=dict(fam=fam,model=model,n=n,acc=acc,up=up,spd=spd,poe=poe,swk=swk,mpps=mpps,price=price,gw=gw,
           bauform=BF[bauform],kueh=kueh,psu=psu); d.update(kw); return d
FANLESS="Lüfterlos (passiv gekühlt)"; FAN="Lüftergekühlt (variable Lüfterdrehzahl)"
PSU_INT="Internes Netzteil"; PSU_EXT="Externes Steckernetzteil (im Lieferumfang)"
poe4=lambda w:f"Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port, Budget {w} W)"
poe6=lambda w:f"Ja (IEEE 802.3af/at/bt, Class 4 und Class 6, bis 60 W/Port, Budget {w} W)"
SP_G="10/100/1000 Mbit/s (RJ45)"; SP_G_SFP="10/100/1000 Mbit/s (RJ45), 1 GbE (SFP)"
SP_G_SFPP="10/100/1000 Mbit/s (RJ45), 1/10 GbE (SFP+)"
SP_1960A="100/1000 Mbit/s / 10 GbE (10GBASE-T, RJ45), 10 GbE (SFP+)"
SP_1960="10/100/1000 Mbit/s (RJ45), 10 GbE (SFP+), 10 GbE (10GBASE-T, RJ45)"

SPECS={
 # ===== 1960 (5) — Managed L2+, True Stacking x4 =====
 "JL805A":P("1960","1960 12XGT 4SFP+",16,"12× 100/1000/10GBASE-T (RJ45)","4× 10G SFP+",SP_1960A,"Nein","320 Gbit/s","238 Mpps",1400,"4,3",kueh=FAN,psu=PSU_INT),
 "JL806A":P("1960","1960 24G 2XGT 2SFP+",28,"24× 10/100/1000 (RJ45)","2× 10G SFP+ + 2× 10GBASE-T (RJ45)",SP_1960,"Nein","128 Gbit/s","95 Mpps",900,"3,9",kueh=FANLESS,psu=PSU_INT),
 "JL807A":P("1960","1960 24G PoE 2XGT 2SFP+ 370W",28,"24× 10/100/1000 (RJ45, davon 20 Class-4- und 4 Class-6-PoE-Ports)","2× 10G SFP+ + 2× 10GBASE-T (RJ45)",SP_1960,poe6(370),"128 Gbit/s","95 Mpps",1500,"4,7",kueh=FAN,psu=PSU_INT),
 "JL808A":P("1960","1960 48G 2XGT 2SFP+",52,"48× 10/100/1000 (RJ45)","2× 10G SFP+ + 2× 10GBASE-T (RJ45)",SP_1960,"Nein","176 Gbit/s","131 Mpps",1500,"4,4",kueh=FAN,psu=PSU_INT),
 "JL809A":P("1960","1960 48G PoE 2XGT 2SFP+ 600W",52,"48× 10/100/1000 (RJ45, davon 40 Class-4- und 8 Class-6-PoE-Ports)","2× 10G SFP+ + 2× 10GBASE-T (RJ45)",SP_1960,poe6(600),"176 Gbit/s","131 Mpps",2400,"4,9",kueh=FAN,psu=PSU_INT),
 # ===== 1930 (7 + 3 B-rev) — Managed L2+, no stacking =====
 "JL680A":P("1930","1930 8G 2SFP",10,"8× 10/100/1000 (RJ45)","2× 1G SFP",SP_G_SFP,"Nein","20 Gbit/s","14,88 Mpps",180,"0,82",bauform="DT",kueh=FANLESS,psu=PSU_EXT),
 "JL681A":P("1930","1930 8G Class4 PoE 2SFP 124W",10,"8× 10/100/1000 (RJ45, Class 4 PoE)","2× 1G SFP",SP_G_SFP,poe4(124),"20 Gbit/s","14,88 Mpps",320,"1,16",bauform="DT",kueh=FANLESS,psu=PSU_INT),
 "JL682A":P("1930","1930 24G 4SFP/SFP+",28,"24× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_G_SFPP,"Nein","128 Gbit/s","95,23 Mpps",420,"2,41",kueh=FANLESS,psu=PSU_INT),
 "JL683A":P("1930","1930 24G Class4 PoE 4SFP/SFP+ 195W",28,"24× 10/100/1000 (RJ45, Class 4 PoE)","4× 1/10G SFP+",SP_G_SFPP,poe4(195),"128 Gbit/s","95,23 Mpps",680,"3,50",kueh=FAN,psu=PSU_INT),
 "JL684A":P("1930","1930 24G Class4 PoE 4SFP/SFP+ 370W",28,"24× 10/100/1000 (RJ45, Class 4 PoE)","4× 1/10G SFP+",SP_G_SFPP,poe4(370),"128 Gbit/s","95,23 Mpps",900,"3,67",kueh=FAN,psu=PSU_INT),
 "JL685A":P("1930","1930 48G 4SFP/SFP+",52,"48× 10/100/1000 (RJ45)","4× 1/10G SFP+",SP_G_SFPP,"Nein","176 Gbit/s","130,95 Mpps",760,"3,13",kueh=FANLESS,psu=PSU_INT),
 "JL686A":P("1930","1930 48G Class4 PoE 4SFP/SFP+ 370W",52,"48× 10/100/1000 (RJ45, Class 4 PoE)","4× 1/10G SFP+",SP_G_SFPP,poe4(370),"176 Gbit/s","130,95 Mpps",1200,"4,52",kueh=FAN,psu=PSU_INT),
 "JL683B":P("1930","1930 24G Class4 PoE 4SFP/SFP+ 195W (Rev B)",28,"24× 10/100/1000 (RJ45, Class 4 PoE)","4× 1/10G SFP+",SP_G_SFPP,poe4(195),"128 Gbit/s","95,23 Mpps",680,"3,50",kueh=FAN,psu=PSU_INT),
 "JL684B":P("1930","1930 24G Class4 PoE 4SFP/SFP+ 370W (Rev B)",28,"24× 10/100/1000 (RJ45, Class 4 PoE)","4× 1/10G SFP+",SP_G_SFPP,poe4(370),"128 Gbit/s","95,23 Mpps",900,"3,67",kueh=FAN,psu=PSU_INT),
 "JL686B":P("1930","1930 48G Class4 PoE 4SFP/SFP+ 370W (Rev B)",52,"48× 10/100/1000 (RJ45, Class 4 PoE)","4× 1/10G SFP+",SP_G_SFPP,poe4(370),"176 Gbit/s","130,95 Mpps",1200,"4,52",kueh=FAN,psu=PSU_INT),
 # ===== 1830 (6) — Smart-Managed L2 =====
 "JL810A":P("1830","1830 8G",8,"8× 10/100/1000 (RJ45; Port 1 als 802.3af-Class-3-PD speisbar)","",SP_G,"Nein","16 Gbit/s","11,90 Mpps",120,"0,77",bauform="DT",kueh=FANLESS,psu=PSU_EXT),
 "JL811A":P("1830","1830 8G 4p Class4 PoE 65W",8,"8× 10/100/1000 (RJ45; davon 4 Class-4-PoE-Ports)","",SP_G,poe4(65),"16 Gbit/s","11,90 Mpps",200,"1,54",bauform="DT1U",kueh=FANLESS,psu=PSU_INT),
 "JL812A":P("1830","1830 24G 2SFP",26,"24× 10/100/1000 (RJ45)","2× 1G SFP",SP_G_SFP,"Nein","52 Gbit/s","38,68 Mpps",300,"2,49",kueh=FANLESS,psu=PSU_INT),
 "JL813A":P("1830","1830 24G 12p Class4 PoE 2SFP 195W",26,"24× 10/100/1000 (RJ45; davon 12 Class-4-PoE-Ports)","2× 1G SFP",SP_G_SFP,poe4(195),"52 Gbit/s","38,68 Mpps",520,"3,47",kueh=FAN,psu=PSU_INT),
 "JL814A":P("1830","1830 48G 4SFP",52,"48× 10/100/1000 (RJ45)","4× 1G SFP",SP_G_SFP,"Nein","104 Gbit/s","77,37 Mpps",560,"3,54",kueh=FAN,psu=PSU_INT),
 "JL815A":P("1830","1830 48G 24p Class4 PoE 4SFP 370W",52,"48× 10/100/1000 (RJ45; davon 24 Class-4-PoE-Ports)","4× 1G SFP",SP_G_SFP,poe4(370),"104 Gbit/s","77,37 Mpps",900,"4,94",kueh=FAN,psu=PSU_INT),
 # ===== 1430 (7) — UNMANAGED (Stacking suppressed) =====
 "R8R44A":P("1430","1430 5G",5,"5× 10/100/1000 (RJ45)","",SP_G,"Nein","10 Gbit/s","7,44 Mpps",60,"0,27",bauform="DT",kueh=FANLESS,psu=PSU_EXT),
 "R8R45A":P("1430","1430 8G",8,"8× 10/100/1000 (RJ45)","",SP_G,"Nein","16 Gbit/s","11,90 Mpps",80,"0,59",bauform="DT",kueh=FANLESS,psu=PSU_EXT),
 "R8R46A":P("1430","1430 8G Class4 PoE 64W",8,"8× 10/100/1000 (RJ45, Class 4 PoE)","",SP_G,poe4(64),"16 Gbit/s","11,90 Mpps",130,"0,77",bauform="DT1U",kueh=FANLESS,psu=PSU_EXT),
 "R8R47A":P("1430","1430 16G",16,"16× 10/100/1000 (RJ45)","",SP_G,"Nein","32 Gbit/s","23,80 Mpps",140,"1,72",kueh=FANLESS,psu=PSU_INT),
 "R8R48A":P("1430","1430 16G Class4 PoE 124W",16,"16× 10/100/1000 (RJ45, Class 4 PoE)","",SP_G,poe4(124),"32 Gbit/s","23,80 Mpps",240,"2,09",kueh=FANLESS,psu=PSU_INT),
 "R8R49A":P("1430","1430 24G",24,"24× 10/100/1000 (RJ45)","",SP_G,"Nein","48 Gbit/s","35,71 Mpps",200,"1,91",kueh=FANLESS,psu=PSU_INT),
 "R8R50A":P("1430","1430 26G 2SFP",28,"26× 10/100/1000 (RJ45)","2× 1G SFP",SP_G_SFP,"Nein","56 Gbit/s","41,68 Mpps",280,"2,27",kueh=FANLESS,psu=PSU_INT),
}

def clip_titel(ser,model,pid):
    for t in (f"Aruba Instant On {model} {pid} | Hexwaren", f"Instant On {model} {pid} | Hexwaren",
              f"Aruba Instant On {model} | Hexwaren", f"Instant On {model} | Hexwaren"):
        if len(t) <= 60: return t
    return f"Instant On {model}"[:60-len(' | Hexwaren')].rstrip()+" | Hexwaren"
def author(pid):
    b=SPECS[pid]; fam=b['fam']; f=FAM[fam]; ser=f['ser']; lyr=f['lyr']; styp=f['styp']; unmanaged=f['unmanaged']
    lyr_de="Layer-2"; model=b['model']; prod=f"Aruba Instant On {model}"
    poe_yes=b['poe']!="Nein"; up=b['up']; n=b['n']; kueh=b['kueh']; psu=b['psu']; btemp=f['btemp']
    portkonfig=(f"{b['acc']} + {up} (Uplink)") if up else b['acc']
    upattr=up if up else "Kein dedizierter Uplink (alle Ports gleichwertig nutzbar)"
    bau_short=b['bauform'].split('(')[0].strip()
    typ_de={"Managed":"gemanagter","Smart-Managed":"smart-gemanagter","Unmanaged":"unmanaged"}[styp]
    artikel=ws(f"{prod} {pid} {styp} Switch ({lyr}) – {b['acc']}{('' if not up else ' + '+up)}, {bau_short}")
    titel=clip_titel(ser,model,pid)
    poe_meta=(f"PoE-Budget {b['poe'].split('Budget ')[-1].rstrip(')')}" if (poe_yes and 'Budget ' in b['poe']) else ("PoE" if poe_yes else "ohne PoE"))
    meta=fit_meta(f"Original {prod} ({pid}): {typ_de} {lyr_de}-Switch mit {b['acc']}, Switching-Kapazität {b['swk']}, {poe_meta}, "
                  f"{'Plug-and-Play' if unmanaged else 'Aruba Instant On Cloud-Management'}.")
    # kurz
    mgmt_k=("ohne Konfiguration im Plug-and-Play-Betrieb" if unmanaged else f"zentral über {f['os']}")
    kp1=(f"<p>Der {prod} ({pid}) ist ein {typ_de} {lyr_de}-Switch der Aruba-Instant-On-{ser}-Serie mit {n} Ports, "
         f"verwaltet {mgmt_k}.</p>")
    poe_k=(f" Über Power over Ethernet versorgt der {pid} angeschlossene Endgeräte direkt per Netzwerkkabel." if poe_yes else "")
    kp2=(f"<p>Im Formfaktor {bau_short} liefert der {pid} eine Switching-Kapazität von {b['swk']} und bindet "
         f"per {(up if up else 'seine Gigabit-Ports')} an das Netz an.{poe_k} Er wird als versiegelte Original-Neuware geliefert.</p>")
    kurz=kp1+kp2
    # intro
    poe_i=(f" Der {pid} versorgt Access Points, IP-Telefone und Kameras per Power over Ethernet direkt über das Netzwerkkabel." if poe_yes
           else f" Der {pid} ist ein Modell ohne PoE und konzentriert sich auf reine Datenanbindung.")
    role=("den einfachen, konfigurationsfreien Netzzugang" if unmanaged else "den cloud-verwalteten Zugang in kleinen und mittleren Netzen")
    i1=(f"Der {prod} ({pid}) ist ein {typ_de} {lyr_de}-Switch aus der Aruba-Instant-On-{ser}-Familie mit {n} Ports "
        f"({b['acc']}), ausgelegt für {role}.")
    if unmanaged:
        mg=(f"Der {pid} arbeitet als Plug-and-Play-Gerät ohne Management: keine Konfiguration, kein VLAN-Setup und kein Stacking – "
            f"einstecken und betreiben.")
    elif "True Stacking" in (f['stk'] or ""):
        mg=(f"Über Aruba Instant On lässt sich der {pid} per Mobile-App oder Cloud-Portal verwalten; bis zu vier {pid} bilden "
            f"per True Stacking einen gemeinsam verwalteten Verbund.")
    else:
        mg=(f"Über Aruba Instant On wird der {pid} per Mobile-App oder Cloud-Portal verwaltet; mehrere Uplinks lassen sich per "
            f"LACP bündeln, ein dediziertes Stacking bietet die {ser}-Serie nicht.")
    i2=(f"Mit {n} Ports erreicht der {pid} eine Switching-Kapazität von {b['swk']} bei einer Weiterleitungsrate von {b['mpps']}.{poe_i} {mg}")
    i3=(f"Im Formfaktor {bau_short} arbeitet der {pid} im Temperaturbereich {btemp}; für Kühlung und Stromversorgung des {pid} "
        f"sorgen {kueh} sowie {psu}. Der {pid} bietet {f['feat']}. "
        f"Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch.")
    intro=pad([ws(i1),ws(i2),ws(i3)],pid)
    # faq
    faq=[[f"Wie viele Ports hat der {pid}?", f"Der {pid} bietet insgesamt {n} Ports: {portkonfig}."]]
    if poe_yes: faq.append([f"Unterstützt der {pid} PoE?", f"Ja. Der {pid} stellt {b['poe']} bereit und versorgt angeschlossene Geräte direkt über das Netzwerkkabel."])
    else: faq.append([f"Unterstützt der {pid} PoE?", f"Nein. Der {pid} ist ein Modell ohne Power over Ethernet und für reine Datenanbindung ausgelegt."])
    if unmanaged:
        faq.append([f"Muss der {pid} konfiguriert werden?", f"Nein. Der {pid} ist ein Unmanaged-Switch und arbeitet ohne Konfiguration im Plug-and-Play-Betrieb."])
    else:
        faq.append([f"Wie wird der {pid} verwaltet?", f"Der {pid} wird über {f['os']} verwaltet – ohne eigenen Management-Server, per Mobile-App oder Web-Portal."])
    swkp=f"eine Switching-Kapazität von {b['swk']}"
    faq.append([f"Was zeichnet den {pid} technisch aus?",
                f"Der {pid} bietet {swkp} und eine Weiterleitungsrate von {b['mpps']}. Er bietet {f['feat']}. "
                f"Für Stromversorgung und Kühlung des {pid} sorgen {psu} sowie {kueh}."])
    # attributes — unmanaged SUPPRESSES the Stacking Merkmal (operator ruling)
    attrs=[["Switch-Typ",styp],["Layer",lyr],["Portanzahl",str(n)],["Port-Konfiguration",portkonfig],
           ["Port-Geschwindigkeit",b['spd']],["Uplink-Ports",upattr],["PoE",b['poe']],["Switching-Kapazität",b['swk']],
           ["Durchsatz",b['mpps']],["Bauform",b['bauform']],["Stromversorgung",psu],["Kühlung",kueh]]
    if not unmanaged: attrs.append(["Stacking",f['stk']])
    attrs += [["Betriebstemperatur",btemp],["Anwendung",f['anw']],["Zustand","Neu, versiegelt"]]
    doc=f['doc']; prov={a[0]:[doc,"datasheet"] for a in attrs if a[0]!="Zustand"}
    versand=f"{float(b['gw'].replace(',','.'))+2.0:.2f}".replace('.',',')
    return {"_facts":{"unterkategorie":f['sclass'],"quell_url":doc,"verifiziert_am":VERIF},
            "artikelname":artikel,"titel_tag":titel,"meta_description":meta,"artikelgewicht":b['gw'],"versandgewicht":versand,
            "kurzbeschreibung":ws(kurz),"intro":intro,"kompatibilitaet":f['mgmt'],
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{b['price']}.00"}

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
        vrows.append([pid,f"{SPECS[pid]['price']},00","PHASE-1-SCHÄTZUNG — NICHT marktgegroundet. SMB-Tier-Tarif (Portzahl/PoE/Speed). Echte HPE-Marktpreis-Recherche folgt als eigene Phase.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/cat; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {cat:36s} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:8]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:105])
    return out

CATMAP={"1960":"Aruba_Instant_On_1960_Switches","1930":"Aruba_Instant_On_1930_Switches",
        "1830":"Aruba_Instant_On_1830_Switches","1430":"Aruba_Instant_On_1430_Switches"}
if __name__=="__main__":
    only=sys.argv[1] if len(sys.argv)>1 else None
    for fam,cat in CATMAP.items():
        if only and fam!=only: continue
        build(cat,[p for p,s in SPECS.items() if s['fam']==fam])
