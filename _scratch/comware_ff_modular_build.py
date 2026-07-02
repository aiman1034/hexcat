# -*- coding: utf-8 -*-
"""STEP-2 LANE A — HPE FlexFabric MODULAR chassis (12900E/7900/12500/11900). Validated Modular-Chassis schema
REUSED verbatim (Switch-Typ=Modular-Chassis / Layer / Steckplätze / Bauform / Switching-Kapazität /
Stromversorgung / Kühlung / Unterstützte Supervisor-Engines / Redundanz / Anwendung; temp->prose). 0 new Merkmal
NAMES: fabric+MPU slot counts FOLDED into Steckplätze as a role-qualified string ("N I/O + M Fabric + K MPU").
Hersteller=HP, BRAND="HPE" (slug hpe-aruba). Per-chassis SwK/slots/weight VERBATIM from OEM docs
(_scratch/ground/FF-*-chassis.md), never port-summed. GATE PRE-REMAP: gate on unterkategorie="Modularer Switch
(Chassis)" (200 kg chassis ceiling), then remap E3 to the family series. Prices Phase-1 ESTIMATE (flagged). $0 prose.
JG632A(12916 legacy)/JH113A(12910 TAA) + 12500E gen HELD pending courier/operator; built chassis = 17."""
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
BRAND="HPE"; E1,E2="Netzwerk & Infrastruktur","Switches"; VERIF="2026-07-02"
def ws(s): return re.sub(r"\s+"," ",s).strip()
def fit_meta(m):
    m=ws(m)
    while len(m)<140: m=m[:-1].rstrip()+" Neu und versiegelt."
    return m[:200].rstrip()
FAMDOC={"12900E":"https://www.hpe.com/psnow/doc/c04111378","7900":"https://www.hpe.com/h20195/v2/getdocument.aspx?docname=4AA5-2359ENW",
        "12500":"https://www.hpe.com/h20195/v2/getdocument.aspx?docname=4AA3-0666ENW","11900":"https://support.hpe.com/hpsc/doc/public/display?docId=emr_na-c03801956"}
FAME3={"12900E":"HPE FlexFabric 12900E Switches","7900":"HPE FlexFabric 7900 Switches",
       "12500":"HPE FlexFabric 12500 Switches","11900":"HPE FlexFabric 11900 Switches"}
CATMAP={"12900E":"HPE_FlexFabric_12900E_Switches","7900":"HPE_FlexFabric_7900_Switches",
        "12500":"HPE_FlexFabric_12500_Switches","11900":"HPE_FlexFabric_11900_Switches"}

# CH[pid]=dict(fam,model,slots,swk,ru,gw,price,psu,kueh,mpu,red,anw,tempprose,cw)  — all VERBATIM-grounded
def C_(fam,model,slots,swk,ru,gw,price,psu,kueh,mpu,red,anw,tempprose,cw="HPE Comware v7"):
    return dict(fam=fam,model=model,slots=slots,swk=swk,ru=ru,gw=gw,price=price,psu=psu,kueh=kueh,mpu=mpu,red=red,anw=anw,tempprose=tempprose,cw=cw)
PSU_2400="Netzteilschächte für 2400-W-AC- bzw. -48…-60-V-DC-Netzteile (mindestens 1, redundant lastverteilt; separat bestellt)"
KFB="Hot-Swap-Lüftertrays (Airflow front-to-back; separat bestellt)"
CHASSIS={
 # ===== 12900E (6 buildable; JG632A=12916-legacy + JH113A=12910-TAA pending courier) =====
 "JH951A":C_("12900E","12901E","1 I/O-Steckplatz (Switch-Fabric und MPU integriert)","9,6 Tbit/s (System-Switching-Kapazität; 5,76 Bpps Durchsatz)","2 HE","35,00",22000,
   "2 "+PSU_2400,"3 "+KFB+" (mindestens 2)","integrierte MPU (kein separates Management-Modul)","Netzteil- und Lüfter-Redundanz (Fabric und MPU integriert)","Kompaktes Rechenzentrums-Spine-/Core-Chassis (modularer Layer-3-Switch, HPE Comware v7) mit integrierter Fabric","0 bis 40 °C"),
 "JH345A":C_("12900E","12902E","2 I/O-Steckplätze + 2 integrierte Fabric-Module + 2 MPU-Steckplätze","19,2 Tbit/s (System-Switching-Kapazität; 11,52 Bpps Durchsatz)","3 HE","24,00",30000,
   "4 "+PSU_2400.replace("2400-W","1800-W"),"2 "+KFB,"HPE FlexFabric 12902E Main Processing Unit (JH346A), 2 Steckplätze aktiv/standby","Dual-MPU (1+1), integrierte Fabric, Netzteil- und Lüfter-Redundanz","Rechenzentrums-Spine/Core (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 "JH262A":C_("12900E","12904E","4 I/O + 6 Switch-Fabric + 2 MPU-Steckplätze","76,8 Tbit/s (System-Switching-Kapazität; 16 Bpps Durchsatz, mit H2-Fabric)","6 HE","36,00",42000,
   "4 "+PSU_2400,"2 "+KFB+" (Type-H-Fabric erfordert 2 High-Speed-Lüftertrays JH448A)","HPE FlexFabric 12904E v2 Main Processing Unit (JH668A), 2 Steckplätze; Type-X (JL844A) bzw. Type-H2 (R9F17A) herstellerseitig zu prüfen","Dual-MPU (1+1), N+1-Fabric (6 Steckplätze), Netzteil- und Lüfter-Redundanz","Rechenzentrums-Spine/Core (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 "JH255A":C_("12900E","12908E","8 I/O + 6 Switch-Fabric + 2 MPU-Steckplätze","152 Tbit/s (System-Switching-Kapazität; 32 Bpps Durchsatz, mit H2-Fabric)","12 HE","47,00",68000,
   "8 "+PSU_2400,"2 "+KFB+" (Type-H-Fabric erfordert 2 High-Speed-Lüftertrays JH424A)","HPE FlexFabric 12900E v2 Main Processing Unit (JH669A), 2 Steckplätze; Type-X (JL845A) bzw. Type-H2 (R9F18A) herstellerseitig zu prüfen","Dual-MPU (1+1), N+1-Fabric (6 Steckplätze), Netzteil- und Lüfter-Redundanz","Rechenzentrums-Spine/Core (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 "JH103A":C_("12900E","12916E","16 I/O + 6 Switch-Fabric + 2 MPU-Steckplätze","184 Tbit/s (System-Switching-Kapazität; 92,1 Bpps Durchsatz)","21 HE","86,10",120000,
   "16 "+PSU_2400,"2 "+KFB+" (Type-H-Fabric erfordert 2 High-Speed-Lüftertrays JH423A)","HPE FlexFabric 12900E v2 Main Processing Unit (JH669A), 2 Steckplätze; Type-X (JL845A) bzw. Type-H2 (R9F18A) herstellerseitig zu prüfen","Dual-MPU (1+1), N+1-Fabric (6 Steckplätze), Netzteil- und Lüfter-Redundanz","High-End-Rechenzentrums-Spine/Core (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 "JG619A":C_("12900E","12910","10 I/O + 6 Switch-Fabric + 2 MPU-Steckplätze","28,8 Tbit/s (System-Switching-Kapazität; bis 36 Bpps Durchsatz)","21 HE","85,03",70000,
   "8 Netzteilschächte für 2000-W-AC-Netzteile (mindestens 1, redundant; 2 Lüftertrays JG631A enthalten)","2 "+KFB,"HPE FlexFabric 12910 Main Processing Unit (JG621A), 2 Steckplätze aktiv/standby","Dual-MPU (1+1), N+1-Fabric, Netzteil- und Lüfter-Redundanz","Rechenzentrums-Core (modularer Layer-3-Switch, HPE Comware v7; Vorgängergeneration 12900)","0 bis 45 °C"),
 # ===== 7900 (4); temp ZU_VERIF -> prose customer-safe (no range) =====
 "JG682A":C_("7900","7904","4 I/O-Steckplätze (Switch-Fabric und MPU im festen Management-Modul integriert)","3,8 Tbit/s (System-Switching-Kapazität)","2 HE","40,00",14000,
   "2 PSR1800-56A-AC-Netzteile (N+1-Redundanz)","2 "+KFB.replace("front-to-back","front-to-back bzw. back-to-front je Variante"),"festes/integriertes Management-Modul (MIPS64-Dual-Core), nicht als separates Modul bestellbar","Netzteil- (N+1) und Lüfter-Redundanz; festes MPU/Fabric nicht redundant","Kompaktes Rechenzentrums-Top-of-Rack/-End-of-Row-Chassis (modularer Layer-3-Switch, HPE Comware v7)","für den Rechenzentrumsbetrieb ausgelegt"),
 "JG841A":C_("7900","7910","10 I/O-Steckplätze + 2 Fabric/MPU-Kombi-Steckplätze","9,6 Tbit/s (System-Switching-Kapazität)","5 HE","71,20",26000,
   "4 Netzteile (AC, N+1-Redundanz)","2 "+KFB.replace("front-to-back","front-to-back bzw. back-to-front je Variante"),"HPE FlexFabric 7910 7.2Tbps bzw. 2.4Tbps Fabric/Main Processing Unit (JG842A oder JH001A, kombiniertes Fabric/MPU-Modul), 2 Steckplätze aktiv/standby","Dual-Fabric/MPU (aktiv/standby), Netzteil- (N+1) und 2-fach-Lüfter-Redundanz","Rechenzentrums-Top-of-Rack/-End-of-Row-Chassis (modularer Layer-3-Switch, HPE Comware v7)","für den Rechenzentrumsbetrieb ausgelegt"),
 "JH122A":C_("7900","7904 TAA","4 I/O-Steckplätze (Switch-Fabric und MPU im festen Management-Modul integriert)","3,8 Tbit/s (System-Switching-Kapazität)","2 HE","40,00",14500,
   "2 PSR1800-56A-AC-Netzteile (N+1-Redundanz)","2 "+KFB.replace("front-to-back","front-to-back bzw. back-to-front je Variante"),"festes/integriertes Management-Modul (MIPS64-Dual-Core), nicht als separates Modul bestellbar","Netzteil- (N+1) und Lüfter-Redundanz; festes MPU/Fabric nicht redundant","Kompaktes Rechenzentrums-Chassis (modularer Layer-3-Switch, HPE Comware v7), TAA-konform","für den Rechenzentrumsbetrieb ausgelegt"),
 "JH123A":C_("7900","7910 TAA","10 I/O-Steckplätze + 2 Fabric/MPU-Kombi-Steckplätze","9,6 Tbit/s (System-Switching-Kapazität)","5 HE","71,20",26500,
   "4 Netzteile (AC, N+1-Redundanz)","2 "+KFB.replace("front-to-back","front-to-back bzw. back-to-front je Variante"),"HPE FlexFabric 7910 7.2Tbps bzw. 2.4Tbps Fabric/Main Processing Unit (JG842A oder JH001A, kombiniertes Fabric/MPU-Modul), 2 Steckplätze aktiv/standby","Dual-Fabric/MPU (aktiv/standby), Netzteil- (N+1) und 2-fach-Lüfter-Redundanz","Rechenzentrums-Chassis (modularer Layer-3-Switch, HPE Comware v7), TAA-konform","für den Rechenzentrumsbetrieb ausgelegt"),
 # ===== 12500 (6); temp 0-40 =====
 "JC654A":C_("12500","12504 AC","4 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","3,24 Tbit/s (Routing-/Switching-Kapazität; 1.920 Mpps Durchsatz)","10 HE","60,00",24000,
   "HPE 12500 2000-W-AC-Netzteile (JF429A) mit AC-Power-Entry-Modul JF426A, redundant","HPE 12504 Lüftereinheit (JC664A)","HPE 12500 Main Processing Unit (JC072B) bzw. Type-A-MPU mit Comware v7 (JG497A), 2 Steckplätze","volle Hardware-Redundanz (Netzteil, Lüfter, MPU 1+1, Fabric), hot-swap-fähig","Rechenzentrums-Core (modularer Layer-3-Switch, HPE Comware v7; IRF, MDC, EVI)","0 bis 40 °C"),
 "JC655A":C_("12500","12504 DC","4 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","3,24 Tbit/s (Routing-/Switching-Kapazität; 1.920 Mpps Durchsatz)","10 HE","60,00",24000,
   "HPE 12500 1800-W-DC-Netzteile (JC651A, -48…-60 V DC), redundant","HPE 12504 Lüftereinheit (JC664A)","HPE 12500 Main Processing Unit (JC072B) bzw. Type-A-MPU mit Comware v7 (JG497A), 2 Steckplätze","volle Hardware-Redundanz (Netzteil, Lüfter, MPU 1+1, Fabric), hot-swap-fähig","Rechenzentrums-Core mit DC-Speisung (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 "JF431C":C_("12500","12508 AC","8 I/O + 9 Switch-Fabric + 2 MPU-Steckplätze","6,12 Tbit/s (Routing-/Switching-Kapazität; 3.840 Mpps Durchsatz)","22 HE","95,00",42000,
   "HPE 12500 2000-W-AC-Netzteile (JF429A) mit AC-Power-Entry-Modul JF426A, redundant","obere und untere Lüftertrays (Airflow front-to-back)","HPE 12500 Main Processing Unit (JC072B) bzw. Type-A-MPU mit Comware v7 (JG497A), 2 Steckplätze","volle Hardware-Redundanz (Netzteil, Lüfter, MPU 1+1, Fabric), hot-swap-fähig","Rechenzentrums-Core (modularer Layer-3-Switch, HPE Comware v7; IRF, MDC, EVI)","0 bis 40 °C"),
 "JC652A":C_("12500","12508 DC","8 I/O + 9 Switch-Fabric + 2 MPU-Steckplätze","6,12 Tbit/s (Routing-/Switching-Kapazität; 3.840 Mpps Durchsatz)","22 HE","95,00",42000,
   "HPE 12500 1800-W-DC-Netzteile (JC651A, -48…-60 V DC), redundant","obere und untere Lüftertrays (Airflow front-to-back)","HPE 12500 Main Processing Unit (JC072B) bzw. Type-A-MPU mit Comware v7 (JG497A), 2 Steckplätze","volle Hardware-Redundanz (Netzteil, Lüfter, MPU 1+1, Fabric), hot-swap-fähig","Rechenzentrums-Core mit DC-Speisung (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 "JF430C":C_("12500","12518 AC","18 I/O + 9 Switch-Fabric + 2 MPU-Steckplätze","13,3 Tbit/s (Routing-/Switching-Kapazität; 8.640 Mpps Durchsatz)","38 HE","160,00",72000,
   "HPE 12500 2000-W-AC-Netzteile (JF429A) mit AC-Power-Entry-Modul JF426A, redundant","obere und untere Lüftertrays (Airflow front-to-back)","HPE 12500 Main Processing Unit (JC072B) bzw. Type-A-MPU mit Comware v7 (JG497A), 2 Steckplätze","volle Hardware-Redundanz (Netzteil, Lüfter, MPU 1+1, Fabric), hot-swap-fähig","High-End-Rechenzentrums-Core (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 "JC653A":C_("12500","12518 DC","18 I/O + 9 Switch-Fabric + 2 MPU-Steckplätze","13,3 Tbit/s (Routing-/Switching-Kapazität; 8.640 Mpps Durchsatz)","38 HE","160,00",72000,
   "HPE 12500 1800-W-DC-Netzteile (JC651A, -48…-60 V DC), redundant","obere und untere Lüftertrays (Airflow front-to-back)","HPE 12500 Main Processing Unit (JC072B) bzw. Type-A-MPU mit Comware v7 (JG497A), 2 Steckplätze","volle Hardware-Redundanz (Netzteil, Lüfter, MPU 1+1, Fabric), hot-swap-fähig","High-End-Rechenzentrums-Core mit DC-Speisung (modularer Layer-3-Switch, HPE Comware v7)","0 bis 40 °C"),
 # ===== 11900 (1) =====
 "JG608A":C_("11900","11908-V","8 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","7,7 Tbit/s (System-Switching-Kapazität; 5,8 Bpps Durchsatz)","20 HE","76,90",30000,
   "bis 6 Netzteile (HPE FF 11900 2500-W-AC JG616A bzw. 2400-W-DC JG617A; mindestens 1, N+1/N+N)","hot-swap-fähiges Lüftertray (JG618A; Airflow front-to-back)","HPE FF 11900 Main Processing Unit (JG609A), 2 Steckplätze; Fabric über 1,92-Tbps-Type-D-Module (JG610A)","Dual-MPU (1+1), 4 Fabric-Module, bis 6 redundante Hot-Swap-Netzteile, Hot-Swap-Lüftertray; IRF/TRILL","Vertikales Rechenzentrums-Core-/Aggregations-Chassis (modularer Layer-3-Switch, HPE Comware v7)","0 bis 45 °C"),
}

def clip_titel(model,pid):
    for t in (f"HPE FlexFabric {model} {pid} Chassis | Hexwaren", f"HPE FlexFabric {model} {pid} | Hexwaren", f"FlexFabric {model} {pid} | Hexwaren"):
        if len(t)<=60: return t
    return f"{pid} | Hexwaren"
def gen(pid):
    b=CHASSIS[pid]; fam=b['fam']; prod=f"HPE FlexFabric {b['model']}"; doc=FAMDOC[fam]
    artikel=ws(f"{prod} {pid} modulares Switch-Chassis – {b['slots']}, {b['ru'].split('(')[0].strip()}, {b['cw']}")
    titel=clip_titel(b['model'],pid)
    meta=fit_meta(f"Original {prod} ({pid}): modulares Rechenzentrums-Chassis (Layer 3, {b['cw']}) mit {b['slots']}, {b['swk']}.")
    kurz=(f"<p>Der {prod} ({pid}) ist ein modulares Layer-3-Rechenzentrums-Chassis mit {b['slots']}. Unter {b['cw']} "
          f"liefert der {pid} {b['swk']}.</p>"
          f"<p>Im Formfaktor 19-Zoll-Rackmontage ({b['ru']}) nimmt der {pid} die kompatiblen Linecards, Fabric- und "
          f"Management-Module auf und wird als versiegelte Original-Neuware geliefert.</p>")
    i1=(f"Der {prod} ({pid}) ist ein modularer Layer-3-Switch (Chassis) aus der HPE-FlexFabric-{'12900E' if fam=='12900E' else fam}-Serie, "
        f"ausgelegt für {b['anw']} und betrieben unter {b['cw']}.")
    i2=(f"Mit {b['slots']} erreicht der {pid} {b['swk']}; die Weiterleitung erfolgt verteilt über die Linecards. "
        f"Als Steuerungs- und Management-Ebene dienen {b['mpu']}. Für Ausfallsicherheit sorgt {b['red']}.")
    i3=(f"Im Formfaktor 19-Zoll-Rackmontage ({b['ru']}) ist der {pid} {b['tempprose']}; Kühlung und Stromversorgung "
        f"übernehmen {b['kueh']} sowie {b['psu']}. Das angegebene Artikelgewicht des {pid} ist ein Konfigurationsgewicht "
        f"(Herstellerangabe). Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch.")
    faq=[["Wie viele Steckplätze hat der "+pid+"?", f"Der {pid} bietet {b['slots']}."],
         ["Welche Switching-Kapazität erreicht der "+pid+"?", f"Der {pid} erreicht {b['swk']} – der Wert stammt aus dem OEM-Datenblatt und ist nicht aus der Portzahl hochgerechnet."],
         ["Welche Management-/Fabric-Module nutzt der "+pid+"?", f"Als Steuerungs- und Fabric-Ebene dienen {b['mpu']}. Für Ausfallsicherheit sorgt {b['red']}."],
         ["Ist der "+pid+" ein originales HPE-Produkt?", f"Ja. Der {pid} ist HPE-Original-Neuware der {FAME3[fam].replace(' Switches','')}-Serie – versiegelt geliefert und für den Betrieb unter {b['cw']} vorgesehen."]]
    attrs=[["Switch-Typ","Modular-Chassis"],["Layer","L3"],["Steckplätze",b['slots']],
           ["Bauform",f"19-Zoll-Rackmontage ({b['ru']})"],["Switching-Kapazität",b['swk']],
           ["Stromversorgung",b['psu']],["Kühlung",b['kueh']],["Unterstützte Supervisor-Engines",b['mpu']],
           ["Redundanz",b['red']],["Anwendung",b['anw']],["Zustand","Neu, versiegelt"]]
    prov={a[0]:[doc,"datasheet"] for a in attrs if a[0]!="Zustand"}
    versand=f"{float(b['gw'].replace(',','.'))+3.0:.2f}".replace('.',',')
    return {"_facts":{"unterkategorie":"Modularer Switch (Chassis)","quell_url":doc,"verifiziert_am":VERIF},
            "artikelname":artikel,"titel_tag":titel,"meta_description":meta,"artikelgewicht":b['gw'],"versandgewicht":versand,
            "kurzbeschreibung":ws(kurz),"intro":[ws(i1),ws(i2),ws(i3)],
            "kompatibilitaet":["HPE-Comware-Betriebssystem","HPE Intelligent Management Center (IMC)","NETCONF/YANG & SNMP"],
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{b['price']}.00"}

def build(cat, pids):
    doc={pid:gen(pid) for pid in pids}
    cpath=ROOT/"stage3_content"/f"{cat}_content.json"; cpath.write_text(json.dumps(doc,ensure_ascii=False,indent=1),encoding="utf-8")
    recs=reconcile_content(cpath,brand=BRAND,rules=rules,weights=weights)
    out=ROOT/"output"/"switches"/cat
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    assemble_bundle(recs,rules,batch=cat,category=cat,out_dir=out)
    S.process_main(out/f"Hexwaren_{cat}_Main.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    S.process_faq(out/f"Hexwaren_FAQ_{cat}.csv", out/f"Hexwaren_{cat}_Attributes.csv", is_switch=True)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/cat; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {cat:34s} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:8]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:105])
    # remap E1/E2/E3 POST-gate
    e3=FAME3[CHASSIS[pids[0]]['fam']]; mp=out/f"Hexwaren_{cat}_Main.csv"
    rows=list(csv.reader(mp.read_bytes().decode("utf-8-sig").splitlines(),delimiter=";")); H=rows[0]
    i1,i2,i3=H.index("Kategorie Ebene 1"),H.index("Kategorie Ebene 2"),H.index("Kategorie Ebene 3"); data=[]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        r[i1],r[i2],r[i3]=E1,E2,e3; data.append(r)
    write_csv(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{cat}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in pids: vrows.append([pid,f"{CHASSIS[pid]['price']},00","PHASE-1-SCHÄTZUNG — NICHT marktgegroundet. Chassis-Tier-Tarif. Echte HPE-Marktpreis-Recherche folgt.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    return out

if __name__=="__main__":
    only=sys.argv[1] if len(sys.argv)>1 else None
    for fam,cat in CATMAP.items():
        if only and fam!=only: continue
        build(cat,[p for p,s in CHASSIS.items() if s['fam']==fam])
