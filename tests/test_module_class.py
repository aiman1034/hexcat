# -*- coding: utf-8 -*-
"""Class-B MODULE lane (Switch-Module & Komponenten) — added 2026-06-28. Pins the additive module carve-out
end-to-end through the REAL pipeline (the chassis-carve-out pattern, second use):
  * the two module Merkmale (Modultyp, Kompatible Serie) are registered + actually EMITTED (name -> ATTR_ALIAS
    -> canonical -> _CANON_TO_FIELD -> SkuIntake field -> SWITCH_ATTRIBUTES emit-order);
  * the module Kat-L3 token routes switch-class but to Ebene-2 "Switch-Module & Komponenten" (override) and the
    REDUCED `_check_module_sku` gate (required Modultyp+Kompatible Serie; the switch/chassis-only Merkmale FORBIDDEN;
    S.2/S.4/S.5 skipped; S.1/S.3 kept-but-guarded — a portless supervisor passes, a 48-port linecard's S.3 holds);
  * the bundle gates ok=True / 0 / 0."""
from __future__ import annotations
import csv
from pathlib import Path

from hexcat.config import load_rules, load_weights
from hexcat.stage3.reconcile import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat import constants as C
from hexcat.stage3 import reconcile as R

FIXTURE = Path(__file__).parent / "fixtures" / "module_class_content.json"
PIDS = {"C6800-SUP6T", "WS-X6748-GE-TX"}
MODULE_MERKMALE = ("Modultyp", "Kompatible Serie")
FORBIDDEN = set(C.MODULE_FORBIDDEN_ATTRS)


def test_module_class_registered():
    rules = load_rules()
    names = C.SWITCH_ATTRIBUTE_NAMES_ORDERED
    for m in MODULE_MERKMALE:
        assert m in names, f"{m} not in SWITCH_ATTRIBUTES"
        assert m in R.ATTR_ALIAS, f"{m} not in ATTR_ALIAS"
        assert m in R._CANON_TO_FIELD, f"{m} not mapped to an intake field"
    assert "Switch-Modul" in C.MODULE_KAT3_VALUES
    assert "Switch-Modul" in set(rules.kategorie_ebene_3_switch_allowed)   # routes switch-class
    assert C.KATEGORIE_EBENE_2_BY_KAT3.get("Switch-Modul") == "Switch-Module & Komponenten"


def test_module_forbidden_set_is_switch_only():
    # the module carve-out forbids exactly the switch/chassis-only Merkmale, never the reused module ones
    reused = {"Portanzahl", "Port-Konfiguration", "Uplink-Ports", "Switching-Kapazität", "PoE"}
    assert FORBIDDEN.isdisjoint(reused)
    assert {"Switch-Typ", "Layer", "Bauform", "Stacking"} <= FORBIDDEN


def _emit(tmp_path: Path):
    rules, weights = load_rules(), load_weights()
    recs = reconcile_content(str(FIXTURE), brand="Cisco", rules=rules, weights=weights)
    out = tmp_path / "Cisco_ModuleTest_Modules"   # _Modules suffix -> the module L6 coverage namespace
    assemble_bundle(recs, rules, batch="Cisco_ModuleTest_Modules", category="Cisco_ModuleTest_Modules", out_dir=str(out))
    return out


def test_module_gates_clean_and_emits_reduced_set(tmp_path):
    out = _emit(tmp_path)
    res = gate(out)
    failed = [str(getattr(v, "message", v)) for L in res.layers for v in (L.violations or [])]
    assert res.ok, failed
    assert sum(len(L.violations or []) for L in res.layers) == 0, failed
    # Ebene-2 override -> the module hauptkat
    main = next(out.glob("*_Main.csv"))
    mrows = list(csv.reader(main.read_bytes().decode("utf-8-sig").splitlines(), delimiter=";"))
    h = mrows[0]
    e2 = h.index("Kategorie Ebene 2") if "Kategorie Ebene 2" in h else h.index("Kategorieebene2") if "Kategorieebene2" in h else None
    if e2 is not None:
        assert all(r[e2] == "Switch-Module & Komponenten" for r in mrows[1:]), [r[e2] for r in mrows[1:]]
    # Attributes: module Merkmale present, switch/chassis-only Merkmale absent
    att = next(out.glob("*_Attributes.csv"))
    by_sku: dict[str, dict[str, str]] = {}
    for row in csv.reader(att.read_bytes().decode("utf-8-sig").splitlines(), delimiter=","):
        if len(row) > 4 and row[0] != "Artikelnummer":
            by_sku.setdefault(row[0], {})[row[3]] = row[4]
    assert set(by_sku) == PIDS
    for pid, a in by_sku.items():
        assert all(m in a for m in MODULE_MERKMALE), (pid, sorted(a))     # both module Merkmale emitted
        assert not (FORBIDDEN & set(a)), (pid, FORBIDDEN & set(a))        # no switch/chassis-only Merkmal
    # the portless supervisor carries no Portanzahl; the linecard's S.3 (48 == 48× ...) held (gate is clean)
    assert "Portanzahl" not in by_sku["C6800-SUP6T"]
    assert by_sku["WS-X6748-GE-TX"].get("Portanzahl") == "48"
    # MULTI-VALUE Kompatible Serie: the cross-chassis linecard emits ONE Attributes row per series
    rows = [r for r in csv.reader(att.read_bytes().decode("utf-8-sig").splitlines(), delimiter=",")
            if len(r) > 4 and r[0] == "WS-X6748-GE-TX" and r[3] == "Kompatible Serie"]
    assert {r[4] for r in rows} == {"Catalyst 6500-E", "Catalyst 6807-XL"}, [r[4] for r in rows]
    assert "Kompatible Serie" in by_sku["C6800-SUP6T"]  # single-value path still works (supervisor)
