"""Universal completeness reconciler (lib/completeness) — offline unit tests.

Completeness is a VERIFIED reconcile against an INDEPENDENT union of official enumerations, never
asserted and never measured against the harvest itself. These tests pin that contract on a fully
synthetic, offline set of snapshots:

  * the universe is the UNION of several independent sources (each covers the others' blind spots);
  * the report says "captured X of Y" and lists every PN in the universe but not the harvest;
  * a hard-gone PN (404/410) is excused from the gap list but still recorded;
  * PNs are normalized (case / whitespace / trailing '=') so the comparison is apples-to-apples;
  * the verdict is COMPLETE only when the harvest covers the whole union AND at least one source
    is populated — an empty universe is NEVER vacuously "complete";
  * and the decisive reuse proof (`test_second_category_routes_same_code`) drives TWO unrelated
    categories through the identical reconciler — adding a category is config, not code.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from lib import completeness as CP
from lib.completeness import (
    EnumerationSource,
    build_universe,
    load_enumerations,
    normalize_pn,
    read_snapshot,
    reconcile,
    reconcile_brand,
    write_report,
)


# ---- normalization --------------------------------------------------------------------

def test_normalize_pn_case_space_and_trailing_equals():
    assert normalize_pn("sfp-10g-lr") == "SFP-10G-LR"
    assert normalize_pn("  QSFP-100G-SR4=  ") == "QSFP-100G-SR4"
    assert normalize_pn("GLC-LH-SMD==") == "GLC-LH-SMD"
    # distinct PNs are NOT merged by the conservative rule
    assert normalize_pn("SFP-10G-LR") != normalize_pn("SFP-10G-LR-S")


def _src(id, pns, kind="list", snapshot="x"):
    return EnumerationSource(id=id, kind=kind, note="", snapshot=snapshot,
                             pns=CP.normalize_set(pns))


# ---- union of independent sources -----------------------------------------------------

def test_universe_is_union_covering_blind_spots():
    current = _src("matrix", ["SFP-10G-LR", "QSFP-100G-SR4"])      # current list misses legacy
    eol = _src("eol", ["XENPAK-10GB-LR", "DWDM-GBIC-30.33"])       # eol list supplies legacy
    universe = build_universe([current, eol])
    assert universe == {"SFP-10G-LR", "QSFP-100G-SR4", "XENPAK-10GB-LR", "DWDM-GBIC-30.33"}


# ---- reconcile: captured X of Y, gaps listed explicitly -------------------------------

def test_reconcile_reports_captured_and_lists_gaps():
    sources = [
        _src("matrix", ["SFP-10G-LR", "QSFP-100G-SR4"]),
        _src("eol", ["XENPAK-10GB-LR", "DWDM-GBIC-30.33"]),
    ]
    # harvest has 3 of the 4, plus one extra not in any enumeration
    harvested = ["sfp-10g-lr", "QSFP-100G-SR4=", "XENPAK-10GB-LR", "SFP-1G-EXTRA"]
    rep = reconcile("Cisco", "transceivers", harvested, sources)

    assert len(rep.universe) == 4
    assert len(rep.captured) == 3
    assert rep.gaps == {"DWDM-GBIC-30.33"}        # the one real gap, listed explicitly
    assert rep.extra == {"SFP-1G-EXTRA"}          # informational, not counted against completeness
    assert not rep.complete
    assert "captured 3 of 4" in rep.summary()


def test_confirmed_gone_excused_from_gaps_but_recorded():
    sources = [_src("matrix", ["A-1", "B-2", "C-3"])]
    rep = reconcile("Cisco", "transceivers", ["A-1", "B-2"], sources,
                    confirmed_gone=["C-3"])
    assert rep.gaps == frozenset()        # C-3 is not a chaseable gap...
    assert rep.gone == {"C-3"}            # ...but it IS recorded
    assert rep.complete                   # harvest ⊇ union modulo confirmed-gone


def test_complete_only_when_harvest_covers_whole_union():
    sources = [_src("matrix", ["A-1", "B-2"])]
    assert reconcile("X", "c", ["A-1", "B-2"], sources).complete
    assert not reconcile("X", "c", ["A-1"], sources).complete


def test_empty_universe_is_never_vacuously_complete():
    # no populated source -> universe empty -> verdict must be INCOMPLETE, not a free pass
    empty = EnumerationSource(id="ungatherd", kind="list", note="", snapshot="p", pns=frozenset())
    rep = reconcile("X", "c", ["whatever"], [empty])
    assert rep.universe == frozenset()
    assert rep.populated_sources == 0
    assert not rep.complete


def test_per_source_breakdown_counts():
    sources = [
        _src("matrix", ["A-1", "B-2"]),
        _src("eol", ["B-2", "C-3"]),     # B-2 overlaps; C-3 only here
    ]
    rep = reconcile("X", "c", ["A-1", "B-2"], sources)
    by_id = {s["id"]: s for s in rep.per_source}
    assert by_id["matrix"]["captured"] == 2 and by_id["matrix"]["gaps"] == 0
    assert by_id["eol"]["captured"] == 1 and by_id["eol"]["gaps"] == 1   # C-3 missing


# ---- snapshot file reading ------------------------------------------------------------

def test_read_snapshot_ignores_comments_and_tolerates_suffixes(tmp_path):
    p = tmp_path / "snap.txt"
    p.write_text(
        "# a captured official list\n"
        "SFP-10G-LR\n"
        "\n"
        "QSFP-100G-SR4=   # spare PN\n"
        "GLC-LH-SMD\t1000BASE-LX/LH\n",
        encoding="utf-8",
    )
    assert read_snapshot(p) == {"SFP-10G-LR", "QSFP-100G-SR4", "GLC-LH-SMD"}


def test_read_snapshot_missing_file_is_empty_not_error(tmp_path):
    assert read_snapshot(tmp_path / "nope.txt") == frozenset()


# ---- config seam loads + writes a tracked artifact ------------------------------------

def _write_enum_config(root: Path, category: str, brand: str, snaps: dict[str, list[str]]):
    enum_dir = root / "config" / "enumerations"
    snap_dir = root / "config" / "coverage" / "enumerations"
    enum_dir.mkdir(parents=True, exist_ok=True)
    snap_dir.mkdir(parents=True, exist_ok=True)
    sources = []
    for sid, pns in snaps.items():
        rel = f"config/coverage/enumerations/{brand.lower()}_{sid}.txt"
        (root / rel).write_text("\n".join(pns) + "\n", encoding="utf-8")
        sources.append({"id": sid, "kind": sid, "note": "", "snapshot": rel})
    doc = {"category": category, "brands": {brand: {"confirmed_gone": [], "sources": sources}}}
    (enum_dir / f"{category}.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")


def test_load_enumerations_reads_snapshots(tmp_path):
    _write_enum_config(tmp_path, "transceivers", "Cisco",
                       {"matrix": ["SFP-10G-LR"], "eol": ["XENPAK-10GB-LR"]})
    brands = load_enumerations("transceivers", root=tmp_path)
    assert "Cisco" in brands
    universe = build_universe(brands["Cisco"].sources)
    assert universe == {"SFP-10G-LR", "XENPAK-10GB-LR"}


def test_reconcile_brand_and_write_report_roundtrip(tmp_path):
    _write_enum_config(tmp_path, "transceivers", "Cisco",
                       {"matrix": ["SFP-10G-LR", "QSFP-100G-SR4"], "eol": ["XENPAK-10GB-LR"]})
    rep = reconcile_brand("transceivers", "Cisco", ["SFP-10G-LR", "QSFP-100G-SR4"], root=tmp_path)
    assert len(rep.universe) == 3 and rep.gaps == {"XENPAK-10GB-LR"}

    out = tmp_path / "report.yaml"
    write_report(rep, out)
    doc = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert doc["universe_total"] == 3
    assert doc["captured_count"] == 2
    assert doc["gaps"] == ["XENPAK-10GB-LR"]
    assert doc["complete"] is False


# ---- the real Cisco config seam loads -------------------------------------------------

def test_real_transceivers_enumeration_config_loads():
    brands = load_enumerations("transceivers")
    assert "Cisco" in brands
    ids = {s.id for s in brands["Cisco"].sources}
    # the four independent yardsticks the mission names
    assert {"tmg_matrix", "eol_eos_bulletins", "ordering_guide", "gpl_price_list"} <= ids


# ---- the decisive reuse proof: a SECOND category, same code ---------------------------

def test_second_category_routes_same_code(tmp_path):
    # Two unrelated categories, two brands; the SAME reconciler handles both, config-only.
    _write_enum_config(tmp_path, "switches", "Acme", {"gpl": ["SW-48P", "SW-24P"]})
    _write_enum_config(tmp_path, "servers", "Globex", {"gpl": ["SRV-1U", "SRV-2U"]})

    sw = reconcile_brand("switches", "Acme", ["SW-48P"], root=tmp_path)
    sv = reconcile_brand("servers", "Globex", ["SRV-1U", "SRV-2U"], root=tmp_path)

    assert sw.gaps == {"SW-24P"} and not sw.complete
    assert sv.gaps == frozenset() and sv.complete
