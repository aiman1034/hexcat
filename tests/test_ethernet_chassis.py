# -*- coding: utf-8 -*-
"""Ethernet modular-chassis class (Cisco Catalyst 9400/9600) — the chassis carve-out extended from FC directors
to Ethernet campus chassis (this session). Proves the extension end-to-end through the REAL pipeline and pins
its invariants. Mirrors test_chassis_family, but the decisive difference is Ebene-2: an Ethernet chassis stays
on the DEFAULT switch branch "Switches" (NOT the FC override "SAN & Fibre Channel"), because
"Modularer Switch (Chassis)" is registered in CHASSIS_KAT3_VALUES but NOT in KATEGORIE_EBENE_2_BY_KAT3."""
from __future__ import annotations
import csv
from pathlib import Path

from hexcat.config import load_rules, load_weights
from hexcat.stage3.reconcile import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat import constants as C

FIXTURE = Path(__file__).parent / "fixtures" / "ethernet_chassis_catalyst_9400_content.json"
PIDS = {"C9404R", "C9407R", "C9410R"}
FORBIDDEN = {"Portanzahl", "Port-Konfiguration", "Port-Geschwindigkeit", "PoE", "Stacking"}


def _emit(tmp_path: Path):
    rules = load_rules()
    weights = load_weights()
    recs = reconcile_content(str(FIXTURE), brand="Cisco", rules=rules, weights=weights)
    out = tmp_path / "Cisco_Catalyst_9400_Switches"
    assemble_bundle(recs, rules, batch="Cisco_Catalyst_9400_Switches",
                    category="Cisco_Catalyst_9400_Switches", out_dir=str(out))
    return out


def test_ethernet_chassis_is_registered():
    assert "Modularer Switch (Chassis)" in C.CHASSIS_KAT3_VALUES
    # Ethernet chassis must NOT override Ebene-2 -> defaults to "Switches".
    assert "Modularer Switch (Chassis)" not in C.KATEGORIE_EBENE_2_BY_KAT3


def test_ethernet_chassis_gates_clean(tmp_path):
    out = _emit(tmp_path)
    res = gate(out)
    failed = [(L.layer, [v.message for v in (L.violations or [])]) for L in res.layers if not L.passed]
    assert res.ok, failed
    assert sum(len(L.violations or []) for L in res.layers) == 0, failed


def test_ethernet_chassis_default_switches_ebene2(tmp_path):
    out = _emit(tmp_path)
    main = next(out.glob("*_Main.csv"))
    rows = list(csv.reader(main.read_bytes().decode("utf-8-sig").splitlines(), delimiter=";"))
    hdr = rows[0]
    assert {r[0] for r in rows[1:]} == PIDS
    assert {r[hdr.index("Kategorie Ebene 2")] for r in rows[1:]} == {"Switches"}
    assert {r[hdr.index("Kategorie Ebene 3")] for r in rows[1:]} == {"Modularer Switch (Chassis)"}


def test_ethernet_chassis_7_attr_no_ports(tmp_path):
    out = _emit(tmp_path)
    att = next(out.glob("*_Attributes.csv"))
    names: dict[str, list[str]] = {}
    groups: set[str] = set()
    for row in csv.reader(att.read_bytes().decode("utf-8-sig").splitlines(), delimiter=","):
        if len(row) > 4 and row[0] != "Artikelnummer":
            names.setdefault(row[0], []).append(row[3])
            groups.add(row[2])
    assert names
    assert all(len(v) == 7 for v in names.values()), {k: len(v) for k, v in names.items()}
    # CHASSIS_REQUIRED_ATTRS is now 6 (Betriebstemperatur OPTIONAL); this fixture carries the 6 required +
    # Betriebstemperatur = 7, with no port Merkmale and no other extras.
    assert all(set(C.CHASSIS_REQUIRED_ATTRS) <= set(v) for v in names.values())
    assert all(set(v) == set(C.CHASSIS_REQUIRED_ATTRS) | {"Betriebstemperatur"} for v in names.values())
    assert groups == {"Switch"}
    assert all(not (FORBIDDEN & set(v)) for v in names.values())
