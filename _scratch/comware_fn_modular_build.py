# -*- coding: utf-8 -*-
"""STEP-2 LANE B — HPE FlexNetwork MODULAR chassis (7500 + 10500 = 15). Validated Modular-Chassis schema REUSED
verbatim; 0 new Merkmal NAMES (fabric+MPU slot counts FOLDED into Steckplätze role-string). Hersteller=HP,
BRAND="HPE". Per-chassis SwK/slots/weight VERBATIM from OEM QuickSpecs (c04111585 / c04212581), never port-summed;
temp->prose. GATE PRE-REMAP (unterkategorie="Modularer Switch (Chassis)", 200 kg ceiling) → remap E3 to family.
7502 keeps distinct MPU slots + IRF-not-supported; 7503/06/10 use combined Fabric/MPU-Kombi slots. Prices Phase-1
ESTIMATE. $0 prose. 10500-TAA MODULE descriptors deferred (this script builds only the 15 CHASSIS)."""
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
ROOT=Path("."); rules,weights=load_rules(),load_weights()
BRAND="HPE"; E1,E2="Netzwerk & Infrastruktur","Switches"; VERIF="2026-07-02"
def ws(s): return re.sub(r"\s+"," ",s).strip()
def fit_meta(m):
    m=ws(m)
    while len(m)<140: m=m[:-1].rstrip()+" Neu und versiegelt."
    return m[:200].rstrip()
FAMDOC={"7500":"https://www.hpe.com/psnow/doc/c04111585","10500":"https://www.hpe.com/psnow/doc/c04212581"}
FAME3={"7500":"HPE FlexNetwork 7500 Switches","10500":"HPE FlexNetwork 10500 Switches"}
CATMAP={"7500":"HPE_FlexNetwork_7500_Switches","10500":"HPE_FlexNetwork_10500_Switches"}
def C_(fam,model,slots,swk,ru,gw,price,psu,kueh,mpu,red,anw,cw="HPE Comware v7"):
    return dict(fam=fam,model=model,slots=slots,swk=swk,ru=ru,gw=gw,price=price,psu=psu,kueh=kueh,mpu=mpu,red=red,anw=anw,cw=cw)
PSU75="2 Netzteilschächte (mindestens 1 Netzteil, redundant; AC oder DC, separat bestellt)"
KFT="Lüftertray (1 Schacht, hot-swap; separat bestellt)"
MPU_75C="kombiniertes Fabric/Main-Processing-Unit-Modul (JH209A 2,4-Tbps-Fabric+MPU oder JH207A, Comware v7), 2 Steckplätze aktiv/standby"
ANW75="Campus-/Rechenzentrums-Core und -Aggregation (modularer Layer-3-Multiservice-Switch, HPE Comware v7)"
MPU_105="HPE 10500 Main Processing Unit (JC614A mit Comware v5 oder JG496A Type A / JH198A Type D mit Comware v7), 2 Steckplätze aktiv/standby"
MPU_105T=MPU_105+" (inkl. TAA-Variante JG375A)"
ANW105="Enterprise-Campus-Core (modularer Layer-3-Switch, HPE Comware v7; IRF bis 4 Chassis, MDC, MPLS/VPLS)"
def PSU105(slots,r): return f"bis {slots} Netzteilschächte (mindestens 1, {r}-Redundanz; JC610A 2500-W-AC oder JC747A 2400-W-DC, separat bestellt)"
KFT105="hot-swap-fähige Lüftertrays (separat bestellt)"
RED105="Dual-MPU (1+1), 4 Fabric-Module, redundante Netzteile und Lüfter (hot-swap); IRF (Virtualisierung von bis zu 4 Chassis), MDC"
CHASSIS={
 # ===== 7500 (7); temp 0-45 =====
 "JD242C":C_("7500","7502","2 I/O + 2 MPU-Steckplätze","bis 640 Gbit/s (System-Switching-Kapazität, mit zwei JH208A); Durchsatz bis 476 Mpps","4 HE","26,76",8000,
   PSU75,KFT,"HPE 7502 Main Processing Unit (JH208A) oder JH207A/JH209A (Comware v7), 2 MPU-Steckplätze","Dual-MPU (2 Steckplätze) und redundante Netzteile; IRF auf dem 7502 nicht unterstützt",ANW75),
 "JD240C":C_("7500","7503","3 I/O + 2 Fabric/MPU-Kombi-Steckplätze","bis 1.920 Gbit/s (System-Switching-Kapazität, mit zwei JH209A); Durchsatz bis 714 Mpps","10 HE","66,68",14000,
   PSU75,KFT,MPU_75C,"Dual-Fabric/MPU (aktiv/standby), redundante Netzteile und Lüfter; IRF-Stacking",ANW75),
 "JD239C":C_("7500","7506","6 I/O + 2 Fabric/MPU-Kombi-Steckplätze","bis 2.880 Gbit/s (System-Switching-Kapazität, mit zwei JH209A); Durchsatz bis 1.428 Mpps","13 HE","93,90",20000,
   PSU75,KFT,MPU_75C,"Dual-Fabric/MPU (aktiv/standby), redundante Netzteile und Lüfter; IRF-Stacking",ANW75),
 "JD238C":C_("7500","7510","10 I/O + 2 Fabric/MPU-Kombi-Steckplätze","bis 4.160 Gbit/s (System-Switching-Kapazität, mit zwei JH209A); Durchsatz bis 2.380 Mpps","16 HE","95,71",28000,
   PSU75,KFT,MPU_75C,"Dual-Fabric/MPU (aktiv/standby), redundante Netzteile und Lüfter; IRF-Stacking",ANW75),
 "JH331A":C_("7500","7503 Bundle","3 I/O + 2 Fabric/MPU-Kombi-Steckplätze (mit 2× JH209A vorinstalliert)","bis 1.920 Gbit/s (System-Switching-Kapazität, mit zwei JH209A); Durchsatz bis 714 Mpps","10 HE","72,00",22000,
   PSU75,KFT,"2× JH209A (kombiniertes 2,4-Tbps-Fabric/MPU-Modul, Comware v7) vorinstalliert, 2 Steckplätze aktiv/standby","Dual-Fabric/MPU (aktiv/standby), redundante Netzteile und Lüfter; IRF-Stacking",ANW75),
 "JH332A":C_("7500","7506 Bundle","6 I/O + 2 Fabric/MPU-Kombi-Steckplätze (mit 2× JH209A vorinstalliert)","bis 2.880 Gbit/s (System-Switching-Kapazität, mit zwei JH209A); Durchsatz bis 1.428 Mpps","13 HE","99,00",28000,
   PSU75,KFT,"2× JH209A (kombiniertes 2,4-Tbps-Fabric/MPU-Modul, Comware v7) vorinstalliert, 2 Steckplätze aktiv/standby","Dual-Fabric/MPU (aktiv/standby), redundante Netzteile und Lüfter; IRF-Stacking",ANW75),
 "JH333A":C_("7500","7510 Bundle","10 I/O + 2 Fabric/MPU-Kombi-Steckplätze (mit 2× JH209A vorinstalliert)","bis 4.160 Gbit/s (System-Switching-Kapazität, mit zwei JH209A); Durchsatz bis 2.380 Mpps","16 HE","101,00",36000,
   PSU75,KFT,"2× JH209A (kombiniertes 2,4-Tbps-Fabric/MPU-Modul, Comware v7) vorinstalliert, 2 Steckplätze aktiv/standby","Dual-Fabric/MPU (aktiv/standby), redundante Netzteile und Lüfter; IRF-Stacking",ANW75),
 # ===== 10500 (8: 4 base + 4 TAA); temp 0-45; dual Type-D/Type-B SwK =====
 "JC613A":C_("10500","10504","4 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 4,8 Tbit/s (Type-D-Fabric) oder 3,5 Tbit/s (Type-B-Fabric); Durchsatz bis 2,9 Bpps (Type D)","8 HE","38,70",18000,
   PSU105(4,"3+1"),KFT105,MPU_105,RED105.replace("3+1 oder 5+1",""),ANW105),
 "JC612A":C_("10500","10508","8 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 9,3 Tbit/s (Type-D-Fabric) oder 4,2 Tbit/s (Type-B-Fabric); Durchsatz bis 5,7 Bpps (Type D)","14 HE","56,70",30000,
   PSU105(6,"5+1"),KFT105,MPU_105,RED105,ANW105),
 "JC611A":C_("10500","10508-V","8 I/O (vertikal) + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 9,3 Tbit/s (Type-D-Fabric) oder 4,2 Tbit/s (Type-B-Fabric); Durchsatz bis 5,7 Bpps (Type D)","20 HE","76,90",34000,
   PSU105(6,"5+1"),KFT105,MPU_105,RED105,ANW105),
 "JC748A":C_("10500","10512","12 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 13,8 Tbit/s (Type-D-Fabric) oder 6,0 Tbit/s (Type-B-Fabric); Durchsatz bis 8,6 Bpps (Type D)","18 HE","75,40",42000,
   PSU105(6,"5+1"),KFT105.replace("Lüftertrays","Lüftertrays (oben JC758A + unten JC773A)"),MPU_105,RED105,ANW105),
 "JG820A":C_("10500","10504 TAA","4 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 4,8 Tbit/s (Type-D-Fabric) oder 3,5 Tbit/s (Type-B-Fabric); Durchsatz bis 2,9 Bpps (Type D)","8 HE","38,70",19000,
   PSU105(4,"3+1"),KFT105,MPU_105T,RED105.replace("3+1 oder 5+1",""),ANW105+", TAA-konform"),
 "JG821A":C_("10500","10508 TAA","8 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 9,3 Tbit/s (Type-D-Fabric) oder 4,2 Tbit/s (Type-B-Fabric); Durchsatz bis 5,7 Bpps (Type D)","14 HE","56,70",31500,
   PSU105(6,"5+1"),KFT105,MPU_105T,RED105,ANW105+", TAA-konform"),
 "JG822A":C_("10500","10508-V TAA","8 I/O (vertikal) + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 9,3 Tbit/s (Type-D-Fabric) oder 4,2 Tbit/s (Type-B-Fabric); Durchsatz bis 5,7 Bpps (Type D)","20 HE","76,90",35500,
   PSU105(6,"5+1"),KFT105,MPU_105T,RED105,ANW105+", TAA-konform"),
 "JG823A":C_("10500","10512 TAA","12 I/O + 4 Switch-Fabric + 2 MPU-Steckplätze","bis 13,8 Tbit/s (Type-D-Fabric) oder 6,0 Tbit/s (Type-B-Fabric); Durchsatz bis 8,6 Bpps (Type D)","18 HE","75,40",44000,
   PSU105(6,"5+1"),KFT105,MPU_105T,RED105,ANW105+", TAA-konform"),
}
def clip_titel(model,pid):
    for t in (f"HPE FlexNetwork {model} {pid} Chassis | Hexwaren", f"HPE FlexNetwork {model} {pid} | Hexwaren", f"FlexNetwork {model} {pid} | Hexwaren"):
        if len(t)<=60: return t
    return f"{pid} | Hexwaren"
def gen(pid):
    b=CHASSIS[pid]; fam=b['fam']; prod=f"HPE FlexNetwork {b['model']}"; doc=FAMDOC[fam]
    artikel=ws(f"{prod} {pid} modulares Switch-Chassis – {b['slots']}, {b['ru']}, {b['cw']}")
    titel=clip_titel(b['model'],pid)
    meta=fit_meta(f"Original {prod} ({pid}): modulares Layer-3-Core-Chassis ({b['cw']}) mit {b['slots']}, {b['swk']}.")
    kurz=(f"<p>Der {prod} ({pid}) ist ein modulares Layer-3-Chassis mit {b['slots']}. Unter {b['cw']} liefert der {pid} {b['swk']}.</p>"
          f"<p>Im Formfaktor 19-Zoll-Rackmontage ({b['ru']}) nimmt der {pid} die kompatiblen Linecards, Fabric- und Management-Module auf "
          f"und wird als versiegelte Original-Neuware geliefert.</p>")
    i1=(f"Der {prod} ({pid}) ist ein modularer Layer-3-Switch (Chassis) aus der HPE-FlexNetwork-{fam}-Serie, "
        f"ausgelegt für {b['anw']} und betrieben unter {b['cw']}.")
    i2=(f"Mit {b['slots']} erreicht der {pid} {b['swk']}. "
        f"Als Steuerungs- und Fabric-Ebene des {pid} dienen {b['mpu']}. Für die Ausfallsicherheit des {pid} sorgt {b['red']}.")
    i3=(f"Im Formfaktor 19-Zoll-Rackmontage ({b['ru']}) ist der {pid} für den Rechenzentrums- oder Campus-Core-Betrieb ausgelegt; "
        f"Kühlung und Stromversorgung des {pid} übernehmen {b['kueh']} sowie {b['psu']}. Das Artikelgewicht des {pid} ist ein "
        f"Konfigurationsgewicht. Geliefert wird der {pid} als versiegelte Original-Neuware. Originaler HP-Switch.")
    faq=[["Wie viele Steckplätze hat der "+pid+"?", f"Der {pid} bietet {b['slots']}."],
         ["Welche Switching-Kapazität erreicht der "+pid+"?", f"Der {pid} erreicht {b['swk']} – der Wert stammt aus dem OEM-Datenblatt und ist nicht aus der Portzahl hochgerechnet."],
         ["Welche Management-/Fabric-Module nutzt der "+pid+"?", f"Als Steuerungs- und Fabric-Ebene des {pid} dienen {b['mpu']}. Für die Ausfallsicherheit des {pid} sorgt {b['red']}."],
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
