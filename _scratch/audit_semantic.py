# -*- coding: utf-8 -*-
"""Catalog-wide semantic cross-check audit over BOTH Cisco + Meraki (post-reconcile = emitted truth).
Enumerates EVERY instance of the 5 semantic-error classes (not just the operator's samples)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
from hexcat.config import load_rules, load_weights
from hexcat.stage3.reconcile import reconcile_content

RULES, WEIGHTS = load_rules(), load_weights()
# Per-brand: pass brand names as argv (e.g. `python audit_semantic.py MikroTik`); default Cisco+Meraki.
_DEFAULT = ["Cisco", "Meraki"]
_NAMES = [a for a in sys.argv[1:] if not a.startswith("-")] or _DEFAULT
BRANDS = [(b, ROOT / "stage3_content" / f"{b}_content.json") for b in _NAMES]

SFP_FAM = {"SFP", "SFP+", "SFP28", "SFP56"}
QSFP_CONN = re.compile(r"QSFP|MPO|MTP|CXP|CPAK", re.I)
DUPLEX_CONN = re.compile(r"duplex|dual lc|\bLC\b", re.I)
MPO12 = re.compile(r"MPO-?12|MPO\b(?!-?24)", re.I)
MPO24 = re.compile(r"MPO-?24", re.I)
MULTI_WL_STD = re.compile(r"\bLR4|\bER4|\bERLT|\bFR4|\bLR8|\bCWDM4|\bSWDM4|LAN-?WDM|kohär|coheren", re.I)  # \b: PLR8/PLR4 + SR4/ESR4/PSM4/DR4 (parallel, 1 λ) must NOT match. ERLT/SWDM4 added (L8 ER4LT miss).
SINGLE_WL = re.compile(r"^\s*[~≈]?\s*\d{3,4}(?:[.,]\d+)?\s*nm", re.I)  # one wavelength only
TUNABLE_WL = re.compile(r"durchstimmbar|tunable", re.I)
COHERENT_TYPE = re.compile(r"kohär|coheren|\bDCO\b|\bACO\b|400ZR|800ZR|DWDM|tunable|durchstimmbar|\d{3}G(?:BASE)?[- ]?ZR", re.I)  # \d{3}G..ZR = coherent 100/400/800ZR, not grey 10/40G
CABLE_KABELTYP = re.compile(r"twinax|\bdac\b|\baoc\b|active optical|aktiv.{0,4}optisch|direct attach", re.I)
CABLE_CATS = {"DAC Kabel", "AOC Kabel", "MPO Kabel"}
# B.8 inline-template artifacts (mirror of validate.py)
EMPTY_SLOT = re.compile(
    r"\bvon\s*[.;,)]"
    r"|\b(?:von|auf|mit|über|zu|nach)\s{2,}\S"
    r"|\b(?:ein|eine|einen)\s+-[A-Za-zÄÖÜ]"   # indefinite only (definite die/das -X = legit suffix ref)
    r"|:\s*[.;,]|\(\s*\)", re.I)
DUP_TOKEN = re.compile(r"\b([A-Za-zÄÖÜäöü0-9][\w+/.\-]*)\s+\1\b")
DBL_SEP = re.compile(r",\s*[–—-]\s|[–—]\s*,")


def av(rec, name):
    return next((a.value for a in rec.attributes if a.name == name), None)


def audit():
    findings = {k: [] for k in ("ff_conn", "faser", "multi_wl", "tunable_wl", "dash", "hersteller", "cable_k3", "template")}
    for brand, path in BRANDS:
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))   # authored truth for the all-fields B.8 scan
        vendor = brand.replace("_Switches", "").replace("_Transceivers", "")   # file name -> vendor
        for rec in reconcile_content(path, brand=vendor, rules=RULES, weights=WEIGHTS):
            pn = rec.artikelnummer
            ff = av(rec, "Formfaktor") or ""
            ans = av(rec, "Anschlusstyp") or ""
            fa = av(rec, "Faseranzahl")
            fiber = (av(rec, "Fasertyp") or "")
            wl = av(rec, "Wellenlänge")
            std = (av(rec, "Standard") or "") + " " + (av(rec, "Transceiver Typ") or "")
            copper = "kupfer" in fiber.lower() or "copper" in fiber.lower() or "twinax" in (av(rec, "Kabeltyp") or "").lower()
            # 1. Formfaktor <-> Anschlusstyp
            if ff in SFP_FAM and QSFP_CONN.search(ans):
                findings["ff_conn"].append(f"{brand}:{pn} ff={ff} conn={ans!r}")
            # 2. Faseranzahl PRESENT for any optical fibre-connector part (deriver fills it lane-aware;
            #    flag only genuinely-missing so we surface the real residual gaps, not correct fills).
            if not copper and ans and re.search(r"MPO|MTP|\bLC\b|\bCS\b", ans, re.I) and not fa:
                findings["faser"].append(f"{brand}:{pn} faser MISSING conn={ans!r} std~{std.strip()[:30]!r}")
            # 3. multi-wavelength single value
            # 3b. tunable/durchstimmbar wavelength only on a coherent/tunable part (B.6)
            if wl and TUNABLE_WL.search(wl) and not COHERENT_TYPE.search(std):
                findings["tunable_wl"].append(f"{brand}:{pn} wl={wl[:40]!r} std~{std.strip()[:30]!r}")
            if MULTI_WL_STD.search(std) and wl and SINGLE_WL.match(wl) and "/" not in wl and "–" not in wl and "..." not in wl and "bis" not in wl.lower():
                findings["multi_wl"].append(f"{brand}:{pn} std~{std.strip()[:30]!r} wl={wl!r}")
            # 4. "—" placeholders
            for a in rec.attributes:
                if a.value.strip() in ("—", "-", "–", "N/A", "n/a"):
                    findings["dash"].append(f"{brand}:{pn} {a.name}={a.value!r}")
            # 5. Hersteller vs product line (MGB = Cisco SB, not Meraki; MGBIC- = Enterasys/Extreme)
            if pn.upper().startswith("MGB") and not pn.upper().startswith("MGBIC") and rec.hersteller == "Meraki":
                findings["hersteller"].append(f"{brand}:{pn} hersteller={rec.hersteller} (MGB = Cisco Small Business)")
            # 7. DAC/AOC cable must carry a cable k3, not a module form factor (B.7)
            kab = av(rec, "Kabeltyp") or ""
            if kab and CABLE_KABELTYP.search(kab) and rec.kategorie_ebene_3 not in CABLE_CATS:
                findings["cable_k3"].append(f"{brand}:{pn} k3={rec.kategorie_ebene_3} kabeltyp={kab!r}")
            # 8. inline-template artifacts (B.8): scan EVERY authored field from the raw content JSON
            # (Beschreibung = composed intro; FAQ = joined Q||A — the fields B.8's first version
            # missed). Read from `raw`, not the reconciled record (which drops intro/faq).
            e = raw.get(pn, {})
            name = e.get("artikelname", "") or ""
            titel = e.get("titel_tag", "") or ""
            intro_txt = " ".join(str(x) for x in (e.get("intro") or []))
            faq_txt = " ".join(" ".join(map(str, p)) for p in (e.get("faq") or []))
            allflds = {"name": name, "kurz": e.get("kurzbeschreibung", "") or "",
                       "beschr": intro_txt, "titel": titel,
                       "meta": e.get("meta_description", "") or "", "faq": faq_txt}
            hit = None
            for fld, txt in allflds.items():
                ms = EMPTY_SLOT.search(txt)
                if ms:
                    hit = f"empty[{fld}]:{ms.group(0)!r}"; break
            if not hit:
                md = DUP_TOKEN.search(name) or DUP_TOKEN.search(titel)
                mp = DBL_SEP.search(name) or DBL_SEP.search(titel)
                if md:
                    hit = f"dup:{md.group(0)!r}"
                elif mp:
                    hit = f"sep:{mp.group(0)!r}"
            if hit:
                findings["template"].append(f"{brand}:{pn} {hit}")
    return findings


if __name__ == "__main__":
    f = audit()
    for k, items in f.items():
        print(f"=== {k}: {len(items)} ===")
        for it in items[:60]:
            print("  ", it)
