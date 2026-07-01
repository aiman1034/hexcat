# -*- coding: utf-8 -*-
"""STEP-2 ArubaOS-Switch EXPANSION MODULES: the 2920/2930M/3810M uplink + stacking module family (9 modules; the section-(C)
Phase-1 hole the coverage reconciler flagged). REUSES the validated module schema (Modultyp + Kompatible Serie + reused port
Merkmale) VERBATIM. 0 new Merkmal NAMES; TWO new Modultyp VALUES ("Uplink-Modul", "Stacking-Modul"). 1 new E3 "ArubaOS-Switch
Expansion Modules" (PLURAL). Kompatible Serie tagged PER module. Grounded: Aruba 3810 datasheet + 2930M IGSG + 2920 QuickSpec
(agent, findings-only). Module-slot bandwidth 40 Gbit/s (2930M/3810M IGSG) where grounded; else customer-safe (never port-math,
never ship ZU_VERIFIZIEREN). Only JL081A carries PoE+. Hersteller=HP. Prices PHASE-1 ESTIMATE (flagged). $0 prose."""
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
E1, E2 = "Netzwerk & Infrastruktur", "Switches"; CAT = "ArubaOS_Switch_Expansion_Modules"; E3 = "ArubaOS-Switch Expansion Modules"
VERIF = "2026-07-01"
DOC = "https://www.hpe.com/psnow/doc/a00004551enw"   # Aruba 2930M/3810M/2920 module data (QuickSpec/IGSG); modules cross-checked
KOMPAT = ["HPE Aruba Networking ArubaOS-Switch","Aruba 2920 / 2930M / 3810M","Aruba Central"]
SWK40 = "40 Gbit/s (Uplink-Modulschacht-Bandbreite, Aruba 2930M)"   # verbatim 2930M IGSG; 3810M switch-level, not per-module
SWK_CS = "Modulschacht-vermittelt (modellspezifischer Wert nicht ausgewiesen)"
SWK_STK = "Stacking-Backplane-vermittelt (modellspezifischer Wert nicht ausgewiesen)"
SWK_336 = "Bis zu 336 Gbit/s Stacking-Durchsatz (42 Gbit/s je Richtung und Port)"    # 3810M QuickSpec
SWK_40P = "Bis zu 40 Gbit/s je Stacking-Port"                                          # 2920 QuickSpec
poe_at = "Ja (IEEE 802.3at Class 4 PoE+, 30 W/Port; Gesamt-PoE-Budget abhängig von der Netzteilbestückung des Switches)"
def ws(s): return re.sub(r"\s+", " ", s).strip()

def author(pid, modtyp, series, short, n, portkonfig, poe, swk, price, detail):
    """modtyp in {Uplink-Modul, Stacking-Modul}; series = display string of compatible fixed switches."""
    serclause = f"der Serie{'n' if '/' in series else ''} {series}"
    poe_attr=[["PoE",poe]] if poe else []
    is_stk = modtyp=="Stacking-Modul"
    kindde = "Stacking-Modul" if is_stk else "Uplink-Modul"
    func = (f"aktiviert Backplane-Stacking an den Switches {series}" if is_stk
            else f"ergänzt die Switches {series} um {short}")
    poe_k = (f" Über das Modul lassen sich angeschlossene Geräte per PoE+ versorgen." if poe else "")
    poe_i = (f" Als einziges Modul der Reihe führt die {pid} Power over Ethernet (IEEE 802.3at PoE+); das Gesamt-PoE-Budget hängt von der Netzteilbestückung des Switches ab." if poe else
             (f" Die {pid} überträgt Stacking-Daten und führt kein Power over Ethernet." if is_stk else f" Die {pid} ist ein reines Uplink-Modul ohne Power over Ethernet."))
    slotname = "Stacking-Modulschacht" if is_stk else "Uplink-Modulschacht"
    artikel = f"HPE Aruba Networking {pid} {kindde} – {portkonfig} für {series}"
    titel = f"Aruba {pid} {kindde} | Hexwaren"
    if len(titel) > 60: titel = f"Aruba {pid} Modul | Hexwaren"
    meta = f"Original HPE Aruba Networking {pid}: {kindde} ({portkonfig}) für die ArubaOS-Switch-Modelle {series}. Modul, Switch separat. Neu und versiegelt."
    kurz = (f"<p>Die HPE Aruba Networking {pid} ist ein {kindde} für den {slotname} der ArubaOS-Switch-Modelle {series}. Die {pid} {func} und stellt {portkonfig} bereit.{poe_k}</p>"
            f"<p>Die {pid} wird im laufenden Betrieb in den Modulschacht des Switches gesteckt (hot-swap-fähig), ist als Erweiterungsmodul kein eigenständiger Switch und benötigt einen kompatiblen Switch. Auslieferung als versiegelte Original-Neuware.</p>")
    intro = [f"Die HPE Aruba Networking {pid} ist ein {kindde} für die ArubaOS-Switch-Modelle {series}. Die {pid} {func} und wird in den {slotname} des jeweiligen Switches eingesetzt.",
             f"Mit {portkonfig} erweitert die {pid} den Switch im laufenden Betrieb (hot-swap), ohne dass ein Gehäusetausch nötig ist.{poe_i} {detail}",
             f"Kompatibel ist die {pid} ausschließlich mit den ArubaOS-Switch-Modellen {series}; sie benötigt dort einen freien {slotname} und ist als Zubehörmodul kein eigenständiger Switch. Geliefert wird die {pid} als versiegelte Original-Neuware. Originales HP-Modul für HP-Netzwerkumgebungen."]
    faq = [[f"Wofür wird die {pid} verwendet?", f"Die {pid} ist ein {kindde} ({portkonfig}), das {func}."],
           [f"In welche Switches passt die {pid}?", f"Die {pid} ist mit den ArubaOS-Switch-Modellen {series} kompatibel und belegt deren {slotname}."],
           ([f"Führt die {pid} PoE?", f"Ja. Die {pid} speist angeschlossene Geräte per IEEE 802.3at PoE+ ein; das Gesamt-PoE-Budget hängt von der Netzteilbestückung des Switches ab."] if poe else
            [f"Führt die {pid} PoE?", f"Nein. Die {pid} ist ein {kindde} ohne Power over Ethernet."]),
           [f"Ist die {pid} ungebraucht?", f"Ja. Hexwaren führt die {pid} ausschließlich als versiegelte Original-Neuware."]]
    attrs = [["Modultyp",modtyp],["Kompatible Serie",series],["Portanzahl",str(n)],["Port-Konfiguration",portkonfig]]+poe_attr+[["Switching-Kapazität",swk],["Zustand","Neu, versiegelt"]]
    versand = "1,20"; prov={a[0]:[DOC,"datasheet"] for a in attrs if a[0]!="Zustand"}
    return {"_facts":{"unterkategorie":"Switch-Modul","quell_url":DOC,"verifiziert_am":VERIF},
            "artikelname":ws(artikel),"titel_tag":titel,"meta_description":ws(meta),"artikelgewicht":"0,60","versandgewicht":versand,
            "kurzbeschreibung":ws(kurz),"intro":[ws(p) for p in intro],"kompatibilitaet":KOMPAT,
            "faq":faq,"verwandte":[],"attributes":attrs,"provenance":prov,"netto_vk":f"{price}.00"}

# roster: pid, modtyp, series, short, n, portkonfig, poe, swk, price, detail
ROSTER=[
 ("JL078A","Uplink-Modul","Aruba 2930M / Aruba 3810M","einen 40-GbE-QSFP+-Uplink",1,"1× QSFP+ (40G)",None,SWK40,650,
  "Der QSFP+-Port nimmt einen 40-GbE-Transceiver auf und lässt sich per Breakout-Kabel auf 4× 10 GbE aufteilen."),
 ("JL079A","Uplink-Modul","Aruba 3810M","zwei 40-GbE-QSFP+-Uplinks",2,"2× QSFP+ (40G)",None,SWK_CS,1100,
  "Beide QSFP+-Ports sind dem Aruba 3810M vorbehalten und liefern zusammen zwei 40-GbE-Uplinks in den Verteiler."),
 ("JL081A","Uplink-Modul","Aruba 2930M / Aruba 3810M","vier HPE-Smart-Rate-Multi-Gigabit-Ports",4,"4× HPE Smart Rate (1/2.5/5/10GBASE-T, Class 4 PoE+)",poe_at,SWK40,900,
  "Die vier HPE-Smart-Rate-Ports treiben Multi-Gigabit-Endgeräte wie Wi-Fi-6-Access-Points mit 2,5/5/10 GbE über Kupfer und speisen sie im PoE-fähigen Switch per PoE+."),
 ("JL083A","Uplink-Modul","Aruba 2930M / Aruba 3810M","vier 10-GbE-SFP+-Uplinks mit MACsec",4,"4× SFP+ (10G, MACsec)",None,SWK40,700,
  "Die vier SFP+-Ports verschlüsseln den Uplink-Verkehr durchgängig per MACsec und nehmen 10-GbE-Glasfaser-Transceiver auf."),
 ("JL084A","Stacking-Modul","Aruba 3810M","",4,"4× Stacking-Ports (Backplane-Stacking)",None,SWK_336,550,
  "Über das Modul lassen sich mehrere Aruba-3810M-Switches per Backplane-Stacking mit bis zu 336 Gbit/s zu einem virtuellen Switch verbinden."),
 ("JL325A","Stacking-Modul","Aruba 2930M","",2,"2× Stacking-Ports (VSF-Backplane-Stacking)",None,SWK_STK,450,
  "Über das Modul lassen sich mehrere Aruba-2930M-Switches per VSF im Ring zu einem gemeinsam verwalteten Verbund stapeln."),
 ("J9731A","Uplink-Modul","Aruba 2920","zwei 10-GbE-SFP+-Uplinks",2,"2× SFP+ (10G)",None,SWK_CS,400,
  "Die beiden SFP+-Ports dienen als 10-GbE-Glasfaser-Uplink des Aruba 2920 zum Aggregations-Switch."),
 ("J9732A","Uplink-Modul","Aruba 2920","zwei 10GBASE-T-Uplinks",2,"2× 10GBASE-T (10 GbE, RJ45)",None,SWK_CS,420,
  "Die beiden 10GBASE-T-Ports liefern 10-GbE-Uplinks des Aruba 2920 über strukturierte Kupferverkabelung (Cat6a)."),
 ("J9733A","Stacking-Modul","Aruba 2920","",2,"2× Stacking-Ports (Backplane-Stacking)",None,SWK_40P,380,
  "Über das Modul lassen sich bis zu vier Aruba-2920-Switches per Stacking-Port mit bis zu 40 Gbit/s je Port verbinden."),
]
DOCMAP={}
for pid,modtyp,series,short,n,pk,poe,swk,price,detail in ROSTER:
    DOCMAP[pid]=author(pid,modtyp,series,short,n,pk,poe,swk,price,detail)

def build():
    cpath=ROOT/"stage3_content"/f"{CAT}_content.json"; cpath.write_text(json.dumps(DOCMAP,ensure_ascii=False,indent=1),encoding="utf-8")
    recs=reconcile_content(cpath,brand="Aruba",rules=rules,weights=weights)
    out=ROOT/"output"/"switches"/CAT
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    assemble_bundle(recs,rules,batch=CAT,category=CAT,out_dir=out)
    S.process_main(out/f"Hexwaren_{CAT}_Main.csv", out/f"Hexwaren_{CAT}_Attributes.csv", is_switch=True)
    S.process_faq(out/f"Hexwaren_FAQ_{CAT}.csv", out/f"Hexwaren_{CAT}_Attributes.csv", is_switch=True)
    mp=out/f"Hexwaren_{CAT}_Main.csv"
    rows=list(csv.reader(mp.read_bytes().decode("utf-8-sig").splitlines(),delimiter=";")); H=rows[0]
    i1,i2,i3=H.index("Kategorie Ebene 1"),H.index("Kategorie Ebene 2"),H.index("Kategorie Ebene 3"); data=[]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        r[i1],r[i2],r[i3]=E1,E2,E3; data.append(r)
    write_csv(mp,tuple(H),data,C.MAIN_DELIMITER,C.MAIN_BOM)
    vp=out/f"Verification_Log_{CAT}_Prices.csv"; vrows=[["Artikelnummer","Netto-VK","Anker-Quelle","Methode","Anker-PN"]]
    for pid in DOCMAP:
        vrows.append([pid,f"{DOCMAP[pid]['netto_vk'].replace('.',',')}","PHASE-1-SCHÄTZUNG — NICHT marktgegroundet (ArubaOS-Switch Expansion-Modul). Tier-Tarif. Echte HPE-Marktpreis-Recherche folgt.","geschätzt-Tier (PLATZHALTER)","—"])
    write_csv(vp,tuple(vrows[0]),vrows[1:],",",False)
    tmp=Path(tempfile.mkdtemp()); gd=tmp/CAT; shutil.copytree(out,gd); res=gate(gd,rules); shutil.rmtree(tmp,ignore_errors=True)
    viol=sum(len(L.violations or []) for L in res.layers)
    print(f"GATE {CAT} ok={res.ok} viol={viol} SKUs={len(recs)}")
    for L in res.layers:
        if not L.passed:
            for v in (L.violations or [])[:10]: print("  VIOL",L.layer,getattr(v,"sku",""),str(getattr(v,"message",v))[:110])
    return out

if __name__=="__main__":
    build()
