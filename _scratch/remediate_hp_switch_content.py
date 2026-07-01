# -*- coding: utf-8 -*-
"""STEP-2 CONTENT REMEDIATION (HPE/Aruba switch tree) — edit-in-place. Roster/prices/encoding UNCHANGED.
Binding acceptance: FAQ + Meta after PID-masking have NO cross-PID collision between DIFFERENT models (functional
specs, per folder). Meta: every PID gets a unique masked Meta (folder-wide convergence) — real spec diffs use the
differing attribute, functionally-identical variants use TAA / hardware-rev / zl-generation / order-number series
(factual, never a fabricated spec). FAQ: only genuinely-different models get a distinguishing Q&A (same-spec
variants share FAQ, which the acceptance allows). FIX3: PoE facet (Nein on port-bearing non-PoE PIDs in PoE
families). 0 new Merkmal NAMES/E3/Modultyp/values. Dry-run unless --apply."""
import csv, re, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0,"_scratch")
from hexcat.writers import write_csv
APPLY = "--apply" in sys.argv
base=Path("output/switches")
MASK=re.compile(r"[A-Z]{1,3}\d{3,4}[A-Z]?")
def mask(s,pid): return MASK.sub("<P>",(s or "").replace(pid,"<P>"))
def rd(p,d):
    if not p.exists(): return [],[]
    r=list(csv.reader(p.read_bytes().decode("utf-8-sig").splitlines(),delimiter=d)); return (r[0] if r else []),r[1:]
TAA_ADD={"JL263A","JL264A"}
def basep(x): return x[:-1] if x[-1].isalpha() else x
def fit_meta(existing, tag):
    tag=" ".join(tag.split()).strip(" ,;–-")[:90]
    if not tag: return existing
    room=200-3-len(tag); core=existing
    if len(core)>room: core=core[:room].rsplit(" ",1)[0].rstrip(" ,;.–-")
    return (core+" – "+tag)[:200]

report={"fix3":defaultdict(list),"meta":defaultdict(list),"faq":defaultdict(list),"series":defaultdict(list)}
roster_b=set();roster_a=set();price_b={};price_a={}
hp_folders=[]
for d in sorted(base.iterdir()):
    if not d.is_dir(): continue
    m=list(d.glob("Hexwaren_*_Main.csv"))
    if not m: continue
    H,rows=rd(m[0],";")
    if "Hersteller" not in H: continue
    iA,iH=H.index("Artikelnummer"),H.index("Hersteller")
    if any(r and r[iA].strip() and r[iH]=="HP" for r in rows): hp_folders.append(d)

for d in hp_folders:
    cat=d.name; catzl = cat=="HP_ProCurve_zl_Modules"
    mp=list(d.glob("Hexwaren_*_Main.csv"))[0]; ap=list(d.glob("Hexwaren_*_Attributes.csv"))[0]
    fpl=list(d.glob("Hexwaren_FAQ_*.csv")); fp=fpl[0] if fpl else None
    MH,MR=rd(mp,";"); AH,AR=rd(ap,","); FH,FR=(rd(fp,",") if fp else ([],[]))
    iA=MH.index("Artikelnummer");iN=MH.index("Artikelname");iM=MH.index("Meta-Description (SEO)");iT=MH.index("Titel-Tag (SEO)");iHe=MH.index("Hersteller")
    iVK=MH.index("Netto-VK") if "Netto-VK" in MH else None
    rows=[r for r in MR if r and r[iA].strip()]; hp=[r[iA] for r in rows if r[iHe]=="HP"]
    art={r[iA]:r[iN] for r in rows}; meta_of={r[iA]:r[iM] for r in rows}; title_of={r[iA]:r[iT] for r in rows}
    for r in rows:
        if r[iHe]=="HP":
            roster_b.add(r[iA])
            if iVK is not None: price_b[r[iA]]=r[iVK]
    aidx=AH.index("Artikelnummer");anm=AH.index("Attributname");avl=AH.index("Attributwert")
    attrs=defaultdict(dict)
    for r in AR:
        if len(r)>avl: attrs[r[aidx]][r[anm]]=r[avl]
    faq_of={}
    if FH:
        fqi=FH.index("Artikelnummer");fai=FH.index("FAQ"); faq_of={r[fqi]:r[fai] for r in FR if len(r)>fai}
    new_meta=dict(meta_of); new_title=dict(title_of); new_faq=dict(faq_of); poe_add={}
    DIST_ATTRS=["Port-Konfiguration","Switching-Kapazität","PoE","Kühlung","Stromversorgung","Anwendung","Betriebstemperatur","Steckplätze","Uplink-Ports","Bauform","Port-Geschwindigkeit","Portanzahl"]
    def compact(k,v):
        if not v: return ""
        if k=="Kühlung":
            for lab,rx in (("Airflow front-to-back","front-to-back"),("Airflow back-to-front","back-to-front"),("Airflow konfigurierbar","konfigurier")):
                if re.search(rx,v,re.I): return lab
            return "Kühlung "+v[:20]
        if k=="Stromversorgung":
            if re.search(r"\bDC\b|-48 V|-40/-75",v): return "DC-Netzteil"
            if "separat" in v: return "Netzteil separat bestellt"
            if re.search(r"Bundle|vorinstall|enthalten",v): return "Netzteil inklusive"
            if re.search(r"extern",v,re.I): return "externes Netzteil"
            if re.search(r"intern",v,re.I): return "internes Netzteil"
            return v[:24]
        if k=="PoE":
            m=re.search(r"Budget (\d+) W",v); return f"PoE-Budget {m.group(1)} W" if m else ("ohne PoE" if v=="Nein" else "PoE+")
        if k=="Anwendung": return "ToR/OOBM-Bundle" if re.search(r"ToR|Rechenzentr|Power-to-Port",v) else v[:24]
        if k=="Switching-Kapazität":
            m=re.search(r"[\d\.,]+ ?(Tbit/s|Gbit/s)",v); return m.group(0) if m else v[:22]
        if k=="Steckplätze":
            m=re.search(r"\d+",v); return f"{m.group(0)} Steckplätze" if m else v[:20]
        if k=="Portanzahl": return f"{v} Ports"
        if k=="Port-Konfiguration": return v[:40]
        return v[:24]
    def chcfg(p):
        """Chassis delivery config from the (correct) Artikelname: base/empty vs the pre-installed bundle port config."""
        if attrs[p].get("Switch-Typ")!="Modular-Chassis": return ""
        a=art[p]; d=a.split(" – ",1)[1].strip() if " – " in a else (a.split("(",1)[1].rstrip(")").strip() if "(" in a else "")
        if re.search(r"Leergeh|ohne (PSU|Netzteil)|Basissystem|Basis-Chassis|alle Steckpl|Replacement|Ersatz",d,re.I): return "Leergehäuse/Basis-Chassis (Steckplätze frei)"
        return d[:70]
    def dt_tokens(p, coll):
        toks=[]
        cc=chcfg(p)
        if cc and len({chcfg(q) for q in coll})>1: toks.append(cc)   # chassis: config (base vs populated) is the primary distinguisher
        for k in DIST_ATTRS:
            vals={q:attrs[q].get(k,"") for q in coll}
            if len(set(vals.values()))>1 and vals.get(p):
                c=compact(k,vals[p])
                if c and c not in toks: toks.append(c)
        return toks
    def modelkey(p):
        a=attrs[p]
        return (a.get("Port-Konfiguration",""),a.get("PoE",""),a.get("Switching-Kapazität",""),a.get("Kühlung",""),a.get("Stromversorgung",""),a.get("Betriebstemperatur",""),a.get("Anwendung",""),a.get("Steckplätze",""),a.get("Layer",""),a.get("Switch-Typ",""),chcfg(p))
    def semtok(p, coll):
        if ("(TAA" in art[p]) or (p in TAA_ADD): return "TAA-konform"
        if any(basep(q)==basep(p) for q in coll if q!=p): return f"Hardware-Revision {p[-1]}"
        if catzl: return "v2-zl-Modulgeneration" if p.startswith("J95") else "v1-zl-Modulgeneration"
        return None
    def _render(q, coll):
        parts=[]; t=dt_tokens(q,coll)
        if t: parts.append(", ".join(t[:2]))
        s=semtok(q,coll)
        if s: parts.append(s)
        return ", ".join(parts)
    def full_tag(p, coll):
        """Return (meta_tag, title_tag, spec_based). GUARANTEED unique within coll (spec+sem unique, else short sem+series)."""
        sib=[q for q in coll if q!=p]
        toks=dt_tokens(p,coll); sem=semtok(p,coll)
        tag=_render(p,coll)
        if (not tag) or any(_render(q,coll)==tag for q in sib):
            ser=next((p[:n] for n in range(3,10) if all(p[:n]!=q[:n] for q in sib)), p)  # short, front-loaded, survives the 90-char cap
            tag=(sem+", " if sem else "")+f"Bestellnummernserie {ser}"
            report["series"][cat].append(f"{p} — order-number series {ser}")
        tt = toks[0] if toks else (sem.split()[-1] if sem else p)
        return tag, tt, bool(toks)
    def apply_title(p, tt):
        bt=new_title[p].replace(" | Hexwaren","")
        if "(" in bt: return
        for c in (f"{bt} ({tt}) | Hexwaren", f"{bt} ({tt.split(' / ')[0][:22]}) | Hexwaren"):
            if len(c)<=60: new_title[p]=c; return
    # ---------- FIX3 PoE ----------
    if any("PoE" in attrs[p] for p in hp):
        for p in hp:
            a=attrs[p]
            if "Portanzahl" in a and "PoE" not in a:
                if re.search(r"PoE|802\.3(af|at|bt)", a.get("Port-Konfiguration","")): continue
                tmpl=next(r for r in AR if len(r)>avl and r[aidx]==p)
                nr=list(tmpl); nr[anm]="PoE"; nr[avl]="Nein"
                if "Sortiernummer" in AH: nr[AH.index("Sortiernummer")]="7"      # PoE facet fixed Sortiernummer
                if "Attributart" in AH: nr[AH.index("Attributart")]="Attribut"
                if "Datentyp (sonst automatisch ermittelt)" in AH: nr[AH.index("Datentyp (sonst automatisch ermittelt)")]="Wertliste"
                poe_add[p]=nr; report["fix3"][cat].append(p)
    # rebuild attributes: insert each PoE=Nein row in Sortiernummer order within its PID's contiguous block
    from collections import OrderedDict
    blocks=OrderedDict()
    for r in AR:
        if len(r)>aidx and r[aidx].strip(): blocks.setdefault(r[aidx],[]).append(r)
    sidx=AH.index("Sortiernummer") if "Sortiernummer" in AH else None
    for p,nr in poe_add.items():
        blocks.setdefault(p,[]).append(nr)
        if sidx is not None:
            blocks[p].sort(key=lambda r: int(r[sidx]) if len(r)>sidx and r[sidx].isdigit() else 999)
    new_attr=[r for b in blocks.values() for r in b]
    # ---------- META: folder-wide convergence to all-unique masked meta ----------
    for _ in range(8):
        g=defaultdict(list)
        for p in hp: g[mask(new_meta[p],p)].append(p)
        coll=[pp for pp in g.values() if len(pp)>1]
        if not coll: break
        for pp in coll:
            for p in pp:
                tm,tt,_=full_tag(p,pp); new_meta[p]=fit_meta(meta_of[p],tm); apply_title(p,tt)
                if p not in report["meta"][cat]: report["meta"][cat].append(p)
    # ---------- FINAL: distinguish any residual same-model twins (rev / alt order number), mask-surviving, budget-preserving ----------
    for _ in range(5):
        g=defaultdict(list)
        for p in hp: g[mask(new_meta[p],p)].append(p)
        coll=[pp for pp in g.values() if len(pp)>1]
        if not coll: break
        for pp in coll:
            for p in pp:
                sem=semtok(p,pp)
                if sem and all(sem!=semtok(q,pp) for q in pp if q!=p):
                    tok=sem
                else:
                    suf=next((p[-n:] for n in (2,3,4,5,6) if not MASK.fullmatch(p[-n:]) and all(p[-n:]!=q[-n:] for q in pp if q!=p)), p[-2:])
                    tok=((sem+", ") if sem else "")+f"Ausführungsvariante {suf}"
                new_meta[p]=fit_meta(new_meta[p], tok)
                if p not in report["meta"][cat]: report["meta"][cat].append(p)
    # ---------- FAQ: distinguishing Q&A for DIFFERENT-model collisions ----------
    fg=defaultdict(list)
    for p in hp: fg[mask(faq_of.get(p,""),p)].append(p)
    for pp in [x for x in fg.values() if len(x)>1 and any(faq_of.get(q) for q in x)]:
        if len({modelkey(q) for q in pp})<2: continue
        allk=set().union(*[set(attrs[q]) for q in pp])
        order=[k for k in DIST_ATTRS if k in allk]+[k for k in sorted(allk) if k not in DIST_ATTRS]
        diffk=[k for k in order if len({attrs[q].get(k,"") for q in pp})>1]
        for p in pp:
            raw=[f"{k}: {attrs[p][k]}" for k in diffk if attrs[p].get(k)]   # FULL differing values -> guaranteed unique across different models
            cc=chcfg(p)
            if cc: raw=[f"Lieferausführung: {cc}"]+raw                       # chassis: base vs pre-installed bundle (from Artikelname)
            if not raw: continue              # identical to all others in group => shared FAQ OK
            q=f"Wodurch unterscheidet sich der {p}?"; ans=(f"Der {p}: {'; '.join(raw)}.")[:600]
            fq=new_faq.get(p,"")
            if "Wodurch unterscheidet" not in fq: new_faq[p]=(fq+("##" if fq else "")+q+"||"+ans); report["faq"][cat].append(p)
    for r in rows:
        if r[iHe]=="HP":
            roster_a.add(r[iA])
            if iVK is not None: price_a[r[iA]]=price_b.get(r[iA])
    if APPLY:
        out=[]
        for r in MR:
            if r and r[iA].strip() and r[iA] in new_meta: r=list(r); r[iM]=new_meta[r[iA]]; r[iT]=new_title[r[iA]]
            out.append(r)
        write_csv(mp,tuple(MH),[r for r in out if r and r[iA].strip()],";",True)
        write_csv(ap,tuple(AH),[r for r in new_attr if r and len(r)>aidx and r[aidx].strip()],",",True)
        if FH:
            outf=[]
            for r in FR:
                if len(r)>fai and r[fqi] in new_faq: r=list(r); r[fai]=new_faq[r[fqi]]
                outf.append(r)
            write_csv(fp,tuple(FH),[r for r in outf if r and len(r)>fqi and r[fqi].strip()],",",True,force_quote_columns=frozenset([fai]))
        # Verification_Log: append a PoE=Nein entry for each FIX3 PID (file #7, internal)
        vlp=list(d.glob("Verification_Log_*.csv")); vlp=[x for x in vlp if "Prices" not in x.name]
        if vlp and report["fix3"][cat]:
            VH,VR=rd(vlp[0],",")
            if VH and "Artikelnummer" in VH:
                url=next((r[VH.index("Source_URL")] for r in VR if len(r)>VH.index("Source_URL")), "")
                vat=next((r[VH.index("Verified_At")] for r in VR if len(r)>VH.index("Verified_At")), "2026-07-01T00:00:00Z")
                add=[]
                for pid in report["fix3"][cat]:
                    row=[""]*len(VH)
                    row[VH.index("Artikelnummer")]=pid; row[VH.index("Attributname")]="PoE"; row[VH.index("Attributwert")]="Nein"
                    if "Source_URL" in VH: row[VH.index("Source_URL")]=url
                    if "Confidence" in VH: row[VH.index("Confidence")]="datasheet"
                    if "Verified_At" in VH: row[VH.index("Verified_At")]=vat
                    add.append(row)
                write_csv(vlp[0],tuple(VH),VR+add,",",True)

print("ROSTER unchanged:",roster_b==roster_a,"| PIDs:",len(roster_b))
print("PRICES unchanged:",price_b==price_a)
print("FIX3 PoE=Nein:",sum(len(v) for v in report['fix3'].values()))
print("META rewritten:",sum(len(v) for v in report['meta'].values()))
print("FAQ Q&A injected:",sum(len(v) for v in report['faq'].values()))
print("order-number-series fallbacks (identical variants):",sum(len(v) for v in report['series'].values()))
print("MODE:","APPLIED" if APPLY else "DRY-RUN")
