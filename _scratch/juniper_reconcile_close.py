# -*- coding: utf-8 -*-
"""EXACT Juniper reconciliation + close determinable [VERIFY] λ + write gate_completeness record.
  - drop 5 legacy parse-fragment keys (not real PNs, not in the 205 universe)
  - close λ by convention: 10G/25G-BX -> 1270/1330 BiDi pair; 25G CWDM channel CW-NN -> 1001+10*NN nm
  - leave genuinely-undeterminable [VERIFY] (PLR4 reach, 100G ERBD/LRBD λ, SFP-1GE-FE) for omit-at-author
  - arithmetic: grounded + aliased + flagged-out = 205 (shown, no '~')
"""
import json, re
from pathlib import Path
R = Path(__file__).resolve().parents[1] / "output" / "stage3"
G = json.loads((R / "juniper_grounded_facts.json").read_text(encoding="utf-8"))
AL = json.loads((R / "juniper_aliases.json").read_text(encoding="utf-8"))
FO = json.loads((R / "juniper_flagged_out.json").read_text(encoding="utf-8"))
E = set(json.loads((R / "juniper_locked_universe.json").read_text(encoding="utf-8"))["modules"])

# 1) drop legacy parse-fragments (in G but not in E, and clearly not real PNs)
frags = [k for k in list(G) if k not in E and (len(k) < 6 or k.endswith("-") or k in ("SFP-",))]
for k in frags:
    del G[k]

# 2) close determinable [VERIFY] λ
closed = 0
for pn, e in G.items():
    wl = e.get("wavelengths_nm") or []
    has_verify = any("[VERIFY]" in str(x) for x in wl)
    if not has_verify:
        continue
    u = pn.upper(); sp = e.get("speed")
    if "BX" in u and sp in ("10G", "25G"):
        e["wavelengths_nm"] = ["1270 nm / 1330 nm (BiDi-Paar, D/U komplementär)"]
        e["flags"] = [f for f in e.get("flags", []) if "[VERIFY]" not in f]
        e["note"] = (e.get("note", "") + " | λ closed: 10G/25G-BX 1270/1330 MSA pair").strip()
        closed += 1
    elif re.search(r'CW-?(\d\d)', u):
        nn = int(re.search(r'CW-?(\d\d)', u).group(1)); lam = 1001 + 10 * nn
        e["wavelengths_nm"] = [f"{lam} nm (CWDM)"]
        e["flags"] = [f for f in e.get("flags", []) if "[VERIFY]" not in f]
        e["note"] = (e.get("note", "") + f" | λ closed: CWDM ch {nn} = {lam} nm").strip()
        closed += 1

# remaining [VERIFY] (genuinely undeterminable -> omit Wellenlänge/reach at author, never ship [VERIFY])
remaining_verify = []
for pn, e in G.items():
    bad = [k for k in ("wavelengths_nm", "reach", "connector")
           if "[VERIFY]" in str(e.get(k))]
    if bad:
        e["omit_at_author"] = bad   # author drops these attrs (L4: never ship [VERIFY])
        remaining_verify.append((pn, bad))

(R / "juniper_grounded_facts.json").write_text(json.dumps(G, ensure_ascii=False, indent=1), encoding="utf-8")

# 3) EXACT arithmetic
gE, alE, foE = len(set(G) & E), len(set(AL) & E), len(set(FO) & E)
print(f"dropped fragments: {frags}")
print(f"λ closed this pass: {closed} | [VERIFY] remaining (omit-at-author): {len(remaining_verify)}")
for pn, bad in remaining_verify: print(f"   {pn}: {bad}")
print(f"\nEXACT RECONCILIATION: grounded {gE} + aliased {alE} + flagged-out {foE} = {gE+alE+foE}  (enumerated {len(E)})")
assert gE + alE + foE == len(E) == 205, "PARTITION NOT EXACT"

# 4) write gate_completeness record (distinct universe = 205 - 4 aliases = 201; captured == emitted == grounded)
gc = R.parent.parent / "config" / "coverage" / "gate_completeness.yaml"
import yaml
data = yaml.safe_load(gc.read_text(encoding="utf-8"))
flagged = [{"pn": pn, "reason_code": FO[pn]["reason_code"]} for pn in sorted(FO)]
data["Juniper_transceivers"] = {"enumerated": 201, "captured": gE, "flagged": flagged}
# append a comment block won't survive yaml.dump; write a note key instead
data["_Juniper_note"] = (f"enumerated 205 raw - {alE} alias-collapsed = 201 distinct; captured {gE} grounded "
                         f"(==emitted); flagged-out {foE} reason-coded; {gE}+{alE}+{foE}=205.")
gc.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
print(f"\ngate_completeness Juniper_transceivers: enumerated 201, captured {gE}, flagged {len(flagged)}")
print("captured+flagged =", gE + len(flagged), ">= enumerated 201:", gE + len(flagged) >= 201)
