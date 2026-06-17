# -*- coding: utf-8 -*-
"""Self-test for src/hexcat/gate.py — MISSION §8 L7 anti-blind-spot proof (full L1-L6).
Run: python _scratch/gate_selftest.py   (exit 0 = CERTIFIED)
  (1) KNOWN-GOOD: the 8 emitted bundles must PASS L1-L6.
  (2) NEGATIVE FIXTURES: one deliberately-broken copy per check class — gate MUST flag each at the
      expected layer. Any fixture that PASSES = gate blind -> fix the check (B.8 false-green lesson).
"""
import sys, shutil, tempfile, csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import hexcat.gate as G
from hexcat.config import load_rules
from hexcat.gate import gate

RULES = load_rules()
KNOWN = ["Cisco", "Arista", "HPE", "Fortinet", "Meraki", "NVIDIA", "MikroTik", "MikroTik_Switches", "Juniper", "Extreme", "Dell", "Lenovo", "Ubiquiti", "Supermicro"]
LIVE = ("L1", "L2", "L3", "L4", "L5", "L6")


def fails(d):
    return [L.layer for L in gate(d, RULES).layers if L.layer in LIVE and not L.passed]


def known_good():
    """Task #21 DOM backfill is COMPLETE + the L8-round-3 media<->DOM/Formfaktor tightening is live, so
    the honest bar is now ZERO violations on every emitted bundle. No DOM-GAP escape hatch — a missing
    DOM attribute OR a media<->DOM inconsistency (e.g. a copper SFP carrying DOM=Ja) is a REGRESSION, not
    a deferred gap. The old escape hatch masked exactly that (Arista SFP-1G-T). Certify = all PASS."""
    print("=== KNOWN-GOOD (L1-L6; backfill complete — zero-violation bar) ===")
    regressions = []
    for b in KNOWN:
        r = gate(ROOT / f"output/stage3_{b}", RULES)
        viol = [v for L in r.layers if L.layer in LIVE and not L.passed for v in L.violations]
        status = "PASS" if not viol else f"REGRESSION {[v.message[:50] for v in viol][:2]}"
        if viol:
            regressions.append(b)
        print(f"  {b:20s} {status}")
    return not regressions


# ---- CSV mutation helpers ------------------------------------------------------------------------
def _rw(path, delim, fn):
    rows = list(csv.reader(path.open(encoding="utf-8-sig", newline=""), delimiter=delim))
    rows = fn(rows)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh, delimiter=delim).writerows(rows)


def main_of(d): return next(d.glob("*_Main*.csv"))
def attrs_of(d): return next(d.glob("*_Attributes*.csv"))


def set_attr_value(d, attrname, newval, n=1):
    f = attrs_of(d)
    def fn(rows):
        h = rows[0]; ai, vi = h.index("Attributname"), h.index("Attributwert"); c = 0
        for r in rows[1:]:
            if c < n and len(r) > vi and r[ai] == attrname:
                r[vi] = newval; c += 1
        return rows
    _rw(f, ",", fn)


def drop_attr(d, attrname):
    f = attrs_of(d)
    _rw(f, ",", lambda rows: [rows[0]] + [r for r in rows[1:] if not (len(r) > rows[0].index("Attributname") and r[rows[0].index("Attributname")] == attrname)])


def set_main_value(d, col, newval, n=1):
    f = main_of(d)
    def fn(rows):
        h = rows[0]; ci = h.index(col); c = 0
        for r in rows[1:]:
            if c < n and len(r) > ci:
                r[ci] = newval; c += 1
        return rows
    _rw(f, ";", fn)


def set_price_cluster(d, val, n):
    """Force n SKUs to the SAME non-zero price (templated-cluster signature) — L5 price-sanity."""
    f = next(d.glob("*_Prices*.csv"))
    def fn(rows):
        pi = rows[0].index("Netto-VK"); c = 0
        for r in rows[1:]:
            if c < n and len(r) > pi:
                r[pi] = val; c += 1
        return rows
    _rw(f, ";", fn)


def clone_beschreibung(d, src_sku, dst_sku):
    """Copy src_sku's Beschreibung onto a same-spec sibling dst_sku (PN-substituted) — a templated clone
    that, after the detector masks PN+feature-code, MUST trip the L5 near-duplicate-prose check."""
    f = main_of(d)
    def fn(rows):
        h = rows[0]; si = h.index("Artikelnummer"); bi = h.index("Beschreibung")
        src = next((r[bi] for r in rows[1:] if len(r) > bi and r[si] == src_sku), None)
        if src is not None:
            for r in rows[1:]:
                if len(r) > bi and r[si] == dst_sku:
                    r[bi] = src.replace(src_sku, dst_sku)
        return rows
    _rw(f, ";", fn)


def inject_text(d, sku, text):
    """Inject a clause into sku's Beschreibung — used to plant an ungrounded vendor/OEM claim that the
    L5 fabrication guard MUST catch (no matching Verification_Log row)."""
    f = main_of(d)
    def fn(rows):
        h = rows[0]; si = h.index("Artikelnummer"); bi = h.index("Beschreibung")
        for r in rows[1:]:
            if len(r) > bi and r[si] == sku:
                r[bi] = r[bi].replace("</p>", " " + text + "</p>", 1) if "</p>" in r[bi] else r[bi] + " " + text
        return rows
    _rw(f, ";", fn)


def set_thin_lambda(d, skus):
    """Make a λ-channel family THIN: overwrite each member's Beschreibung with the SAME wavelength-FREE
    templated body (λ survives only in the PN). The structural Pass-2 must then FIRE (no channel identity
    in Titel/prose, λ-masked framing identical)."""
    body = ("<p>Dieser Transceiver verbindet Netzwerkgeräte über Glasfaser und ist für den professionellen "
            "Einsatz vorgesehen. Er wird als versiegelte Neuware geliefert und ist im Betrieb steckbar.</p>")
    f = main_of(d)
    def fn(rows):
        h = rows[0]; si = h.index("Artikelnummer"); bi = h.index("Beschreibung")
        for r in rows[1:]:
            if len(r) > bi and r[si] in skus:
                r[bi] = body
        return rows
    _rw(f, ";", fn)


def set_grid_lambda(d, sku_wl):
    """Make a well-formed λ-grid: same body on every member EXCEPT each carries ITS OWN wavelength in the
    prose (sku_wl maps sku->'1470'). λ-masked similarity is then ~1.0 BUT every member has channel identity
    (λ in Titel via PN + λ in prose) -> Pass-2 must EXEMPT it (must NOT fire)."""
    f = main_of(d)
    def fn(rows):
        h = rows[0]; si = h.index("Artikelnummer"); bi = h.index("Beschreibung")
        for r in rows[1:]:
            if len(r) > bi and r[si] in sku_wl:
                r[bi] = ("<p>Optisches Modul auf der festen Wellenlänge %s nm für Singlemode-Glasfaser; "
                         "als wellenlängenspezifisches Modul im professionellen Einsatz.</p>" % sku_wl[r[si]])
        return rows
    _rw(f, ";", fn)


def set_chan_in_std(d, sku_chan):
    """Bake the channel code into the Standard attribute (e.g. '10G CWDM (ch27)') + give a wavelength-FREE
    generic body. Without Pass-2 key-normalization each channel reads as a different Std and never clusters;
    WITH it they collapse -> thin -> MUST FIRE. Proves the clustering-key normalization fix."""
    body = ("<p>Dieser Transceiver verbindet Netzwerkgeräte über Glasfaser und ist für den professionellen "
            "Einsatz vorgesehen; er wird als versiegelte Neuware geliefert und ist im Betrieb steckbar.</p>")
    af = attrs_of(d)
    def afn(rows):
        hh = rows[0]; si = hh.index("Artikelnummer"); ni = hh.index("Attributname"); vi = hh.index("Attributwert")
        for r in rows[1:]:
            if len(r) > vi and r[si] in sku_chan and r[ni] == "Standard":
                r[vi] = "10G CWDM (ch%s)" % sku_chan[r[si]]
        return rows
    _rw(af, ",", afn)
    mf = main_of(d)
    def mfn(rows):
        hh = rows[0]; si = hh.index("Artikelnummer"); bi = hh.index("Beschreibung")
        for r in rows[1:]:
            if len(r) > bi and r[si] in sku_chan:
                r[bi] = body
        return rows
    _rw(mf, ";", mfn)


def set_std_for(d, sku, val):
    """Set ONE named SKU's Standard attribute — used by the scope-exclusion fixtures (F27-F29)."""
    f = attrs_of(d)
    def fn(rows):
        h = rows[0]; si = h.index("Artikelnummer"); ni = h.index("Attributname"); vi = h.index("Attributwert")
        for r in rows[1:]:
            if len(r) > vi and r[si] == sku and r[ni] == "Standard":
                r[vi] = val
        return rows
    _rw(f, ",", fn)


def scope_inject(d, src_sku, new_pn, new_std):
    """Rename src_sku -> new_pn in the Attributes file and set its Standard (=''  clears it, mimicking the
    empty-Standard TDM framers). check_scope_exclusion reads only the Attributes file, so this suffices."""
    f = attrs_of(d)
    def fn(rows):
        h = rows[0]; si = h.index("Artikelnummer"); ni = h.index("Attributname"); vi = h.index("Attributwert")
        for r in rows[1:]:
            if r[si] == src_sku:
                r[si] = new_pn
                if r[ni] == "Standard":
                    r[vi] = new_std
        return rows
    _rw(f, ",", fn)


def scope_fixtures():
    """L7 proof for check_scope_exclusion (the Cisco scope-leak check, now wired into gate() L6). Calls the
    check DIRECTLY (a fixture mutating a single SKU is cleaner than a whole-bundle layer run). MUST fire:
    pure SONET/SDH, pure FC, a SAToP PN, a channelized OC-x framer PN (empty Standard). MUST NOT fire:
    a multirate optic carrying the 'BASE' in-scope signal, and an operator-confirmed gray keeper."""
    base = ROOT / "output/stage3_Cisco"
    tmp = Path(tempfile.mkdtemp())
    arows = list(csv.reader(attrs_of(base).open(encoding="utf-8-sig", newline=""), delimiter=","))
    h = arows[0]; si, ni, vi = h.index("Artikelnummer"), h.index("Attributname"), h.index("Attributwert")
    # 4 distinct, currently in-scope Ethernet SKUs (Standard contains BASE) to overwrite
    subs = []
    for r in arows[1:]:
        if len(r) > vi and r[ni] == "Standard" and "BASE" in r[vi].upper() and r[si] not in subs:
            subs.append(r[si])
        if len(subs) >= 4:
            break
    S0, S1, S2, S3 = subs[:4]
    cases = [
        ("F27 pure-SONET-fires", S0, lambda d: set_std_for(d, S0, "SONET/SDH OC-3/STM-1 (Short Reach)"), True),
        ("F28 pure-FC-fires",    S0, lambda d: set_std_for(d, S0, "8GFC"), True),
        ("F29 multirate-OC192-passes", S0,
         lambda d: set_std_for(d, S0, "10GBASE-ER/-EW, OC-192/STM-64 IR-2 (Multirate)"), False),
        ("F30 SAToP-PN-fires", "SFP-E1F-SATOP-I",
         lambda d: scope_inject(d, S1, "SFP-E1F-SATOP-I", ""), True),
        ("F31 OCx-framer-fires", "SFP-TS-OC3STM1-I",
         lambda d: scope_inject(d, S2, "SFP-TS-OC3STM1-I", ""), True),
        ("F32 gray-keeper-exempt", "DS-SFP-FCGE-SW",
         lambda d: scope_inject(d, S3, "DS-SFP-FCGE-SW", "8GFC"), False),
    ]
    print("\n=== SCOPE-EXCLUSION FIXTURES (check_scope_exclusion — wired into L6) ===")
    ok = True
    for name, target, mut, must_fire in cases:
        d = tmp / name.split()[0]; shutil.rmtree(d, ignore_errors=True); shutil.copytree(base, d); mut(d)
        fired = target in {v.sku for v in G.check_scope_exclusion(d)}
        good = (fired == must_fire); ok &= good
        verdict = ("OK" if good else "BLIND!") if must_fire else ("OK" if good else "FALSE-FLAG!")
        print(f"  {name:30s} fired={fired} expect={must_fire} {verdict}")
    # F33 — prove scope is WIRED INTO the hard gate (not merely callable): an injected scope SKU must make
    # gate() L6 FAIL with a SCOPE violation. Guards against silently un-wiring check_scope_exclusion from
    # gate() — without this, F27-F32 (direct calls) would still pass while enforcement was dead.
    d = tmp / "F33"; shutil.rmtree(d, ignore_errors=True); shutil.copytree(base, d)
    scope_inject(d, S0, "SFP-E1F-SATOP-I", "")   # TDM framer PN, empty Standard
    l6 = next((L for L in gate(d, RULES).layers if L.layer == "L6"), None)
    wired = bool(l6) and not l6.passed and any("SCOPE" in v.message for v in l6.violations)
    ok &= wired
    print(f"  {'F33 scope-wired-into-L6':30s} L6-scope-fail={wired} expect=True {'OK' if wired else 'BLIND!'}")
    shutil.rmtree(tmp, ignore_errors=True)
    return ok


def set_main_for(d, sku, col, val):
    f = main_of(d)
    def fn(rows):
        h = rows[0]; si = h.index("Artikelnummer"); ci = h.index(col)
        for r in rows[1:]:
            if len(r) > ci and r[si] == sku:
                r[ci] = val
        return rows
    _rw(f, ";", fn)


def harden_fixtures():
    """L7 proof for the G1-G5 hardening checks (the Supermicro-cycle misses). Positive cases FIRE,
    legit-variant cases stay silent. Direct-call (like the scope fixtures)."""
    base = ROOT / "output/stage3_Supermicro"
    tmp = Path(tempfile.mkdtemp())

    def mk(name, mut):
        d = tmp / name; shutil.rmtree(d, ignore_errors=True); shutil.copytree(base, d)
        if mut: mut(d)
        return d
    ok = True
    print("\n=== HARDENING FIXTURES (G1-G5) ===")

    # G1a: word-identical CROSS-family pair (SR4 body cloned onto iSR4 — different Standard) -> HARD fires
    def clone_be_kurz(dd, src, dst):
        f = main_of(dd)
        def fn(rows):
            h = rows[0]; si = h.index("Artikelnummer"); bi = h.index("Beschreibung"); ki = h.index("Kurzbeschreibung")
            sb = next((r[bi] for r in rows[1:] if r[si] == src), None)
            sk = next((r[ki] for r in rows[1:] if r[si] == src), None)
            for r in rows[1:]:
                if r[si] == dst:
                    if sb is not None: r[bi] = sb.replace(src, dst)
                    if sk is not None: r[ki] = sk.replace(src, dst)
            return rows
        _rw(f, ";", fn)
    pair = lambda lst, x, y: any({x, y} == {a, b} for a, b, _ in lst)
    # G1a: WITHIN-signature word-identical (clone SR4 body onto its SR4 twin) -> HARD fires
    d = mk("G1a", lambda d: clone_be_kurz(d, "AOM-TQSFP-79EQPZ-AVG", "AOM-TQSFP-79EQDZ-AVG"))
    g1a = pair(G.check_dup_matrix(d)["hard"], "AOM-TQSFP-79EQPZ-AVG", "AOM-TQSFP-79EQDZ-AVG")
    # G1b: AOC 1m-vs-3m (length-variant family) -> EXEMPT from BOTH tiers (clean base)
    clean = G.check_dup_matrix(mk("G1b", None))
    g1b = not pair(clean["hard"], "CBL-SFP+AOC-1M", "CBL-SFP+AOC-3M") and not pair(clean["warn"], "CBL-SFP+AOC-1M", "CBL-SFP+AOC-3M")
    # G1c: CROSS-signature word-identical (SR4 body onto iSR4 — different Standard) -> WARN, NEVER hard
    d = mk("G1c", lambda d: clone_be_kurz(d, "AOM-TQSFP-79EQPZ-AVG", "AOM-TQSFP-79EIPZ-AVG"))
    cm = G.check_dup_matrix(d)
    g1c = pair(cm["warn"], "AOM-TQSFP-79EQPZ-AVG", "AOM-TQSFP-79EIPZ-AVG") and not pair(cm["hard"], "AOM-TQSFP-79EQPZ-AVG", "AOM-TQSFP-79EIPZ-AVG")
    # G1d: clean Supermicro -> 0 HARD (the CBL-0347L~CBL-NTWK-0347 latch pair is a legit build-variant)
    g1d = len(clean["hard"]) == 0 and not pair(clean["hard"], "CBL-0347L", "CBL-NTWK-0347")
    for tag, good in (("G1a within-sig HARD-fires", g1a), ("G1b AOC-1m/3m EXEMPT", g1b),
                      ("G1c cross-sig→WARN not hard", g1c), ("G1d Supermicro 0 HARD (latch exempt)", g1d)):
        ok &= good; print("  %-32s %s" % (tag, "OK" if good else "BLIND!"))
    # G3: condition-claim stem in Meta -> fires
    d = mk("G3", lambda d: set_main_for(d, "AOC-E10GSFPSR", "Meta-Description (SEO)", "Original Supermicro AOC-E10GSFPSR. Neu, versiegelt und werkseitig geprüft."))
    g3 = any(v.sku == "AOC-E10GSFPSR" for v in G.check_banned_stem(d))
    # G4: orphan text after </p> in Kurz -> fires
    d = mk("G4", lambda d: set_main_for(d, "AOC-E10GSFPSR", "Kurzbeschreibung", "<p>A B C D E F.</p><p>G H I J K L.</p> Orphan-Satz hinter dem Block."))
    g4 = any(v.sku == "AOC-E10GSFPSR" for v in G.check_orphan_text(d))
    # G5: 87-word Kurz -> gate L2 word-count fires
    blob = "<p>" + " ".join(["Wort"] * 45) + ".</p><p>" + " ".join(["Wort"] * 42) + ".</p>"
    d = mk("G5", lambda d: set_main_for(d, "AOC-E10GSFPSR", "Kurzbeschreibung", blob))
    g5 = "L2" in fails(d)
    for tag, good in (("G3 versiegel-stem fires", g3), ("G4 orphan-text fires", g4), ("G5 87-word Kurz fires", g5)):
        ok &= good; print("  %-30s %s" % (tag, "OK" if good else "BLIND!"))
    shutil.rmtree(tmp, ignore_errors=True)
    return ok


def fixtures():
    tx = ROOT / "output/stage3_Cisco"           # transceiver base (14-attr, reach)
    sw = ROOT / "output/stage3_MikroTik_Switches"  # switch base (S.1-S.6)
    tmp = Path(tempfile.mkdtemp())

    def mk(name, base, mut):
        d = tmp / name; shutil.rmtree(d, ignore_errors=True); shutil.copytree(base, d); mut(d); return d

    rt = lambda f: f.read_text(encoding="utf-8-sig"); wt = lambda f, s: f.write_text(s, encoding="utf-8-sig")
    FX = [
        ("F01 mojibake-umlaut",   sw, lambda d: main_of(d).write_bytes(main_of(d).read_bytes().replace("ü".encode(), "Ã¼".encode(), 1)), "L1"),
        ("F02 BOM-in-body",       sw, lambda d: main_of(d).write_bytes(main_of(d).read_bytes()[:200] + b"\xef\xbb\xbf" + main_of(d).read_bytes()[200:]), "L1"),
        ("F03 unbalanced-</p>",   sw, lambda d: wt(main_of(d), rt(main_of(d)).replace("</p>", "", 1)), "L1"),
        ("F04 stray-<",           sw, lambda d: wt(main_of(d), rt(main_of(d)).replace("<p>", "<p> 3 < 5 ", 1)), "L1"),
        ("F05 wrong-delimiter",   sw, lambda d: wt(main_of(d), rt(main_of(d)).replace(";", ",")), "L1"),
        ("F06 banned-phrase",     sw, lambda d: wt(main_of(d), rt(main_of(d)).replace("</p>", " sofort lieferbar</p>", 1)), "L2"),
        ("F07 wrong-Attributgrp", sw, lambda d: _rw(attrs_of(d), ",", lambda rows: [rows[0]] + [[*(["Switche" if (i == rows[0].index("Attributgruppe")) else c for i, c in enumerate(r)])] for r in rows[1:]]), "L3"),
        ("F08 L3-on-unmanaged",   sw, lambda d: set_attr_value(d, "Switch-Typ", "Unmanaged", n=50), "L3"),
        ("F09 Portanzahl-wrong",  sw, lambda d: set_attr_value(d, "Portanzahl", "999", n=1), "L3"),
        ("F10 [VERIFY]-shipped",  sw, lambda d: set_attr_value(d, "Anwendung", "[VERIFY]", n=1), "L4"),
        ("F11 optic-wt-on-switch", sw, lambda d: set_main_value(d, "Artikelgewicht", "0,05", n=1), "L5"),
        ("F12 reach-out-of-band", tx, lambda d: set_attr_value(d, "Reichweite", "500 km", n=1), "L5"),
        ("F15 missing-DOM",       ROOT / "output/stage3_Juniper",
         lambda d: _rw(attrs_of(d), ",", lambda rows: [rows[0]] + [r for r in rows[1:]
                   if not (len(r) > rows[0].index("Attributname") and r[rows[0].index("Attributname")] == "DOM Unterstützung")]), "L3"),
        # L8 round-3 gate-tightening fixtures (back-applied):
        ("F16 optical-DOM=Nein",  tx, lambda d: set_attr_value(d, "DOM Unterstützung", "Nein", n=300), "L3"),
        ("F17 Formfaktor-unlocked", tx, lambda d: set_attr_value(d, "Formfaktor", "BOGUSFF", n=20), "L3"),
        ("F18 price-cluster",     tx, lambda d: set_price_cluster(d, "1234,56", n=8), "L5"),
        # F19 (L8 ER4LT miss): a WDM multi-lane standard (LR4/ER4/ERLT/CWDM4/LAN-WDM) must carry the 4-λ
        # SET — force every Wellenlänge to a single C-band 1550 nm; the ERLT/LR4/ER4 modules MUST fail B.3.
        # (Positive direction = the known-good bundles, whose real WDM modules carry the set and PASS.)
        ("F19 R4-single-wl",      ROOT / "output/stage3_Extreme",
         lambda d: set_attr_value(d, "Wellenlänge", "1550 nm", n=300), "L3"),
        # F20 (L8 Dell #2): a >=16-fibre parallel optic on a bare MPO-12 is impossible (carries 8) — force
        # every Anschlusstyp to MPO-12; the 16-fibre 800G parts (VR8/2×R4) MUST fail the fibre-connector check.
        ("F20 fibre>conn",        ROOT / "output/stage3_Dell",
         lambda d: set_attr_value(d, "Anschlusstyp", "MPO-12", n=400), "L5"),
        # F21 (L8 Dell #1): force every cable Anschlusstyp to same-to-same "OSFP auf OSFP" — the breakout-PN
        # cables (DAC-…2x400G / …4Q28 / 8xSFP56) MUST fail (breakout end dropped); straight PNs are exempt.
        ("F21 breakout-ends",     ROOT / "output/stage3_Dell",
         lambda d: set_attr_value(d, "Anschlusstyp", "OSFP auf OSFP", n=400), "L5"),
        # F22 (L8 Lenovo finding ①): two distinct same-spec optics (10GBASE-SR/SFP+/300m/850nm) must NOT
        # share near-identical Beschreibung. Clone one onto its sibling -> after PN/feature-code masking the
        # near-dup detector MUST fire. (Positive direction = the real Lenovo SR cluster, 8 unique voices, PASSES.)
        ("F22 near-dup-prose",    ROOT / "output/stage3_Lenovo",
         lambda d: clone_beschreibung(d, "49Y4216", "49Y8578"), "L5"),
        # F23 (L8 Lenovo finding ①, fabrication guard): inject an OEM claim ("Finisar") with NO matching
        # Verification_Log row -> the ungrounded-claim guard MUST fire. (Positive direction = the real
        # Lenovo bundle, whose grounded prose names no third-party OEM, PASSES.)
        ("F23 ungrounded-claim",  ROOT / "output/stage3_Lenovo",
         lambda d: inject_text(d, "46C3447", "Auf Basis eines Finisar-Optikmoduls."), "L5"),
        # F24/F25 use the Ubiquiti base — it has ZERO near_dup_exempt entries (its CWDM passes structurally),
        # so the renamed-fixture-dir doesn't lose any registry exemption and the test isolates Pass-2.
        # F24 (L8 λ-grid policy, THIN negative): make λ-channels thin — wavelength only in the PN, identical
        # wavelength-FREE templated body. Pass-2 (no channel identity in Titel/prose) MUST FIRE.
        ("F24 lambda-thin",       ROOT / "output/stage3_Ubiquiti",
         lambda d: set_thin_lambda(d, {"UACC-OM-SFP10-1270", "UACC-OM-SFP10-1290"}), "L5"),
        # F25 (L8 λ-grid policy, WELL-FORMED positive): every member carries ITS OWN wavelength in Titel +
        # Wellenlänge attr + prose. λ-masked similarity ~1.0 (honest grid signature) BUT Pass-2 must EXEMPT
        # via channel identity — must NOT fire L5.
        ("F25 lambda-grid-ok",    ROOT / "output/stage3_Ubiquiti",
         lambda d: set_grid_lambda(d, {"UACC-OM-SFP10-1310": "1310", "UACC-OM-SFP10-1330": "1330",
                                       "UACC-OM-SFP10-1470": "1470"}), "noL5"),
        # F26 (L8 clustering blind-spot): channel code baked into the Standard attr (10G CWDM (ch27/29/31))
        # so each channel reads as a different Std. Pass-2 key-normalization must collapse them; thin λ-free
        # body -> MUST FIRE. (Pre-fix this never clustered -> never flagged.)
        ("F26 chan-in-std",       ROOT / "output/stage3_Ubiquiti",
         lambda d: set_chan_in_std(d, {"UACC-OM-SFP10-1270": "27", "UACC-OM-SFP10-1290": "29",
                                       "UACC-OM-SFP10-1310": "31"}), "L5"),
        ("F13 count-mismatch-L6", sw, lambda d: _rw(main_of(d), ";", lambda rows: rows[:-1]), "L6"),
    ]
    print("\n=== NEGATIVE/POSITIVE FIXTURES (each MUST behave as expected) ===")
    ok = True
    for name, base, mut, exp in FX:
        f = fails(mk(name.split()[0], base, mut))
        caught = ("L5" not in f) if exp == "noL5" else (exp in f)
        ok &= caught
        verdict = ("PASS-exempt OK" if caught else "FALSE-FLAG!") if exp == "noL5" else ("OK" if caught else "BLIND!")
        print(f"  {name:24s} failed={f or 'NONE'} expect {exp} {verdict}")

    # F14 flag-without-reason-code (L6) — monkeypatch the completeness record to a bad temp one
    badrec = tmp / "bad_completeness.yaml"
    badrec.write_text("MikroTik_switches: {enumerated: 37, captured: 36, flagged: [{family: foo}]}\n", encoding="utf-8")
    orig = G._GATE_COMPLETENESS; G._GATE_COMPLETENESS = badrec
    f = fails(sw)
    G._GATE_COMPLETENESS = orig
    caught = "L6" in f
    ok &= caught
    print(f"  {'F14 flag-no-reason-code':24s} failed={f or 'NONE!'} expect L6 {'OK' if caught else 'BLIND!'}")
    shutil.rmtree(tmp, ignore_errors=True)
    return ok


if __name__ == "__main__":
    kg, fx, sx = known_good(), fixtures(), scope_fixtures()
    hx = harden_fixtures()
    print(f"\nKNOWN-GOOD all-pass: {kg} | FIXTURES all-caught: {fx} | SCOPE-fixtures: {sx} | HARDENING-fixtures: {hx}")
    print("FULL GATE L1-L6 CERTIFIED" if (kg and fx and sx and hx) else "GATE NOT CERTIFIED — fix + re-run")
    sys.exit(0 if (kg and fx and sx and hx) else 1)
