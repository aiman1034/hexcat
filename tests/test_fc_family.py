# -*- coding: utf-8 -*-
"""Fibre-Channel-Switch (Cisco MDS V-series) — the 3rd product class registered in the gate-model
extension (2026-06-25). Proves the FC carve-out end-to-end through the REAL pipeline (reconcile →
assemble → 8-layer gate), and pins the per-Kat-L3 invariants so a future change can't silently
regress them. FC is switch-CLASS (SWITCH attribute set, "Switch" Attributgruppe) but lives under a
distinct Ebene-2 ("SAN & Fibre Channel") and uses the 12-attr FC model (no Layer, no Durchsatz, no
Uplink-Ports). The 3 PIDs here are a TEST FIXTURE only — no MDS catalog SKUs are emitted to output/."""
from __future__ import annotations
import csv
import re
from pathlib import Path

from hexcat.config import load_rules, load_weights
from hexcat.stage3.reconcile import reconcile_content
from hexcat.assemble import assemble_bundle
from hexcat.gate import gate

FIXTURE = Path(__file__).parent / "fixtures" / "fc_mds_v_content.json"
FC_PIDS = {"DS-C9124V-8EK9", "DS-C9148V-24EK9", "DS-C9396V-48EK9"}


def _emit(tmp_path: Path):
    """Run the real reconcile + assemble path for the FC fixture into a temp bundle dir."""
    rules = load_rules()
    weights = load_weights()
    recs = reconcile_content(str(FIXTURE), brand="Cisco", rules=rules, weights=weights)
    out = tmp_path / "Cisco_MDS_V_Switches"
    assemble_bundle(recs, rules, batch="Cisco_MDS_V_Switches",
                    category="Cisco_MDS_V_Switches", out_dir=str(out))
    return out


def _main_rows(out: Path):
    main = next(out.glob("*_Main.csv"))
    rows = list(csv.reader(main.read_bytes().decode("utf-8-sig").splitlines(), delimiter=";"))
    return rows[0], rows[1:]


def _attrs_by_sku(out: Path):
    att = next(out.glob("*_Attributes.csv"))
    names: dict[str, list[str]] = {}
    vals: dict[str, dict[str, str]] = {}
    groups: set[str] = set()
    for row in csv.reader(att.read_bytes().decode("utf-8-sig").splitlines(), delimiter=","):
        if len(row) > 4 and row[0] != "Artikelnummer":
            names.setdefault(row[0], []).append(row[3])
            vals.setdefault(row[0], {})[row[3]] = row[4]
            groups.add(row[2])
    return names, vals, groups


def test_fc_family_gates_clean(tmp_path):
    """ACCEPTANCE: the 3 FC SKUs gate ok=True with 0 violations / 0 warnings through all layers."""
    out = _emit(tmp_path)
    res = gate(out)
    failed = [(L.layer, [v.message for v in (L.violations or [])]) for L in res.layers if not L.passed]
    assert res.ok, failed
    assert sum(len(L.violations or []) for L in res.layers) == 0, failed


def test_fc_family_is_switch_class_under_san_branch(tmp_path):
    """FC is switch-class but emits the distinct Ebene-2 'SAN & Fibre Channel' + Kat-L3 'Fibre-Channel-Switch'."""
    out = _emit(tmp_path)
    hdr, rows = _main_rows(out)
    pids = {r[0] for r in rows}
    assert pids == FC_PIDS
    assert {r[hdr.index("Kategorie Ebene 1")] for r in rows} == {"Netzwerk & Infrastruktur"}
    assert {r[hdr.index("Kategorie Ebene 2")] for r in rows} == {"SAN & Fibre Channel"}
    assert {r[hdr.index("Kategorie Ebene 3")] for r in rows} == {"Fibre-Channel-Switch"}


def test_fc_family_12_attr_model_drops_layer_and_durchsatz(tmp_path):
    """12-attr FC model: 'Switch' Attributgruppe (switch-class), no Layer, no Durchsatz, no Uplink-Ports."""
    out = _emit(tmp_path)
    names, _vals, groups = _attrs_by_sku(out)
    assert names, "no attribute rows emitted"
    assert all(len(v) == 12 for v in names.values()), {k: len(v) for k, v in names.items()}
    assert groups == {"Switch"}, groups            # routes as switch-class, never transceiver
    assert all("Layer" not in v for v in names.values())
    assert all("Durchsatz" not in v for v in names.values())
    assert all("Uplink-Ports" not in v for v in names.values())


def test_fc_family_s3_portanzahl_parses(tmp_path):
    """S.3 still parses '96× Fibre-Channel-Ports (SFP+)' -> 96 = Portanzahl (active fraction stays out of it)."""
    out = _emit(tmp_path)
    _names, vals, _groups = _attrs_by_sku(out)
    pn = "DS-C9396V-48EK9"
    pk = vals[pn]["Port-Konfiguration"]
    parsed = sum(int(m) for m in re.findall(r"(\d+)\s*[×xX]", pk))
    assert parsed == int(vals[pn]["Portanzahl"]) == 96, (pk, vals[pn]["Portanzahl"])
