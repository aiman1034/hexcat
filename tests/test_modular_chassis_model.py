# -*- coding: utf-8 -*-
"""Modular-campus-chassis model (Class A — Catalyst 4500-E / 6500-E), added this session. Pins the additive
gate/schema extension end-to-end through the REAL pipeline:
  * three NEW Wertliste Merkmale (Steckplätze, Unterstützte Supervisor-Engines, Redundanz) are registered and
    actually EMITTED (they thread name -> ATTR_ALIAS -> canonical -> _CANON_TO_FIELD -> SkuIntake field ->
    SWITCH_ATTRIBUTES emit-order);
  * Switch-Typ='Modular-Chassis' WITH Layer L3 passes the chassis S.2 (a chassis routes L3 via its supervisor);
  * Betriebstemperatur is OPTIONAL (operating temp in prose) and the port-centric Merkmale stay ABSENT;
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

FIXTURE = Path(__file__).parent / "fixtures" / "chassis_modular_campus_4500e_content.json"
PIDS = {"WS-C4503-E", "WS-C4506-E", "WS-C4507R+E", "WS-C4510R+E"}
NEW_MERKMALE = ("Steckplätze", "Unterstützte Supervisor-Engines", "Redundanz")
PORT_MERKMALE = {"Portanzahl", "Port-Konfiguration", "Port-Geschwindigkeit", "PoE", "Uplink-Ports",
                 "Durchsatz", "Stacking", "Betriebstemperatur"}


def test_new_merkmale_registered():
    names = C.SWITCH_ATTRIBUTE_NAMES_ORDERED
    for m in NEW_MERKMALE:
        assert m in names, f"{m} not in SWITCH_ATTRIBUTES"
        assert m in R.ATTR_ALIAS, f"{m} not in ATTR_ALIAS"
        assert m in R._CANON_TO_FIELD, f"{m} not mapped to an intake field"


def test_chassis_required_drops_betriebstemperatur():
    # the modular-campus model carries operating temp in prose -> Betriebstemperatur is OPTIONAL
    assert "Betriebstemperatur" not in C.CHASSIS_REQUIRED_ATTRS
    assert "Modularer Switch (Chassis)" in C.CHASSIS_KAT3_VALUES


def _emit(tmp_path: Path):
    rules, weights = load_rules(), load_weights()
    recs = reconcile_content(str(FIXTURE), brand="Cisco", rules=rules, weights=weights)
    out = tmp_path / "Cisco_4500E_Switches"
    assemble_bundle(recs, rules, batch="Cisco_4500E_Switches", category="Cisco_4500E_Switches", out_dir=str(out))
    return out


def test_modular_chassis_gates_clean_and_emits_new_model(tmp_path):
    out = _emit(tmp_path)
    res = gate(out)
    failed = [str(getattr(v, "message", v)) for L in res.layers for v in (L.violations or [])]
    assert res.ok, failed
    assert sum(len(L.violations or []) for L in res.layers) == 0, failed
    # read the emitted Attributes
    att = next(out.glob("*_Attributes.csv"))
    by_sku: dict[str, dict[str, str]] = {}
    for row in csv.reader(att.read_bytes().decode("utf-8-sig").splitlines(), delimiter=","):
        if len(row) > 4 and row[0] != "Artikelnummer":
            by_sku.setdefault(row[0], {})[row[3]] = row[4]
    assert set(by_sku) == PIDS
    for pid, a in by_sku.items():
        assert a.get("Switch-Typ") == "Modular-Chassis", pid          # NEW Switch-Typ value
        assert a.get("Layer") == "L3", pid                            # L3 chassis (S.2 exemption)
        assert all(m in a for m in NEW_MERKMALE), (pid, sorted(a))    # 3 new Merkmale emitted
        assert a.get("Steckplätze")                                   # non-empty slot count
        assert not (PORT_MERKMALE & set(a)), (pid, PORT_MERKMALE & set(a))  # no port Merkmale, no Betriebstemp
