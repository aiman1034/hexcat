# -*- coding: utf-8 -*-
"""Chassis-switch class (Cisco MDS 9700 directors) — the modular-chassis carve-out (this session).
Proves the carve-out end-to-end through the REAL pipeline (reconcile → assemble → 8-layer gate) and pins
the chassis invariants so a future change can't silently regress them. A chassis-class SKU (Kat-L3 in
constants.CHASSIS_KAT3_VALUES) carries the REDUCED 7-Merkmal set, FORBIDS the port-centric Merkmale, and
skips S.1/S.3/S.4 (keeps S.2/S.5). The 3 PIDs here are a TEST FIXTURE only."""
from __future__ import annotations
import csv
from pathlib import Path

from hexcat.config import load_rules, load_weights
from hexcat.stage3.reconcile import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate
from hexcat import constants as C

FIXTURE = Path(__file__).parent / "fixtures" / "chassis_mds_9700_content.json"
CHASSIS_PIDS = {"DS-C9706", "DS-C9710", "DS-C9718"}
FORBIDDEN = {"Portanzahl", "Port-Konfiguration", "Port-Geschwindigkeit", "PoE", "Stacking"}


def _emit(tmp_path: Path):
    rules = load_rules()
    weights = load_weights()
    recs = reconcile_content(str(FIXTURE), brand="Cisco", rules=rules, weights=weights)
    out = tmp_path / "Cisco_MDS_9700_Switches"
    assemble_bundle(recs, rules, batch="Cisco_MDS_9700_Switches",
                    category="Cisco_MDS_9700_Switches", out_dir=str(out))
    return out


def _attrs_by_sku(out: Path):
    att = next(out.glob("*_Attributes.csv"))
    names: dict[str, list[str]] = {}
    groups: set[str] = set()
    for row in csv.reader(att.read_bytes().decode("utf-8-sig").splitlines(), delimiter=","):
        if len(row) > 4 and row[0] != "Artikelnummer":
            names.setdefault(row[0], []).append(row[3])
            groups.add(row[2])
    return names, groups


def test_chassis_family_gates_clean(tmp_path):
    """ACCEPTANCE: the 3 MDS 9700 chassis gate ok=True with 0 violations / 0 warnings."""
    out = _emit(tmp_path)
    res = gate(out)
    failed = [(L.layer, [v.message for v in (L.violations or [])]) for L in res.layers if not L.passed]
    assert res.ok, failed
    assert sum(len(L.violations or []) for L in res.layers) == 0, failed


def test_chassis_is_chassis_class_san_director(tmp_path):
    out = _emit(tmp_path)
    main = next(out.glob("*_Main.csv"))
    rows = list(csv.reader(main.read_bytes().decode("utf-8-sig").splitlines(), delimiter=";"))
    hdr = rows[0]
    assert {r[0] for r in rows[1:]} == CHASSIS_PIDS
    assert {r[hdr.index("Kategorie Ebene 2")] for r in rows[1:]} == {"SAN & Fibre Channel"}
    assert {r[hdr.index("Kategorie Ebene 3")] for r in rows[1:]} == {"Fibre-Channel-Director"}
    assert CHASSIS_PIDS == set(r[0] for r in rows[1:])
    assert "Fibre-Channel-Director" in C.CHASSIS_KAT3_VALUES


def test_chassis_7_attr_no_port_merkmale(tmp_path):
    """Reduced 7-Merkmal set, 'Switch' Attributgruppe, and the port-centric Merkmale ABSENT."""
    out = _emit(tmp_path)
    names, groups = _attrs_by_sku(out)
    assert names, "no attribute rows emitted"
    assert all(len(v) == 7 for v in names.values()), {k: len(v) for k, v in names.items()}
    assert all(set(v) == set(C.CHASSIS_REQUIRED_ATTRS) for v in names.values())
    assert groups == {"Switch"}
    assert all(not (FORBIDDEN & set(v)) for v in names.values())
