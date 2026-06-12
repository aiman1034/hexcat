"""§2 G6 — the merged-catalog cross-brand sweep.

Two halves:
  1. Unit tests on `sweep_catalog` over tiny synthetic bundles — prove every cross-brand
     collision class (Artikelnummer, URL-Pfad, GTIN, Titel-Tag, cross-brand sentence) is caught,
     and that a clean multi-brand catalog passes.
  2. A schema/reconciliation test on the tracked `config/merged_catalog_collisions.yaml`
     artifact (structure + internal consistency, not the volatile collision list).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from hexcat import constants as C
from hexcat import merged_sweep
from hexcat.merged_sweep import sweep_catalog
from hexcat.writers import BOM

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "config" / "merged_catalog_collisions.yaml"
BRANDS = {"Cisco", "Arista", "HPE", "Fortinet", "MikroTik"}


# ---- synthetic-bundle helpers ---------------------------------------------------------

def _write(path: Path, columns, delim: str, bom: bool, rows: list[dict]) -> None:
    header = delim.join(columns)
    lines = [header]
    for r in rows:
        lines.append(delim.join(r.get(c, "") for c in columns))
    text = "\r\n".join(lines) + "\r\n"
    payload = (BOM if bom else "") + text
    path.write_bytes(payload.encode("utf-8"))


def _bundle(root: Path, brand: str, skus: list[dict]) -> Path:
    """skus: list of {sku, url, titel, besch, gtin}. Writes a minimal Main + Attributes pair."""
    d = root / f"stage3_{brand}"
    d.mkdir(parents=True, exist_ok=True)
    main_rows = [{
        "Artikelnummer": s["sku"],
        "URL-Pfad": s.get("url", f"cisco/{s['sku'].lower()}"),
        "Titel-Tag (SEO)": s.get("titel", f"{s['sku']} | Hexwaren"),
        "Beschreibung": s.get("besch", f"<p>Original Cisco {s['sku']}.</p>"),
    } for s in skus]
    attr_rows = [{
        "Artikelnummer": s["sku"],
        "GTIN": s.get("gtin", ""),
        "Attributname": "Formfaktor",
        "Attributwert": "SFP+",
    } for s in skus]
    _write(d / f"Hexwaren_{brand}_Main.csv", C.MAIN_COLUMNS, C.MAIN_DELIMITER, C.MAIN_BOM, main_rows)
    _write(d / f"Hexwaren_{brand}_Attributes.csv", C.ATTRIBUTES_COLUMNS,
           C.ATTRIBUTES_DELIMITER, C.ATTRIBUTES_BOM, attr_rows)
    return d


def _kinds(result) -> set[str]:
    return {f.kind for f in result.findings}


# ---- clean path -----------------------------------------------------------------------

def test_clean_multi_brand_catalog_passes(tmp_path):
    a = _bundle(tmp_path, "Cisco", [
        {"sku": "C-1", "url": "cisco/c-1", "titel": "C-1 | Hexwaren", "gtin": ""},
        {"sku": "C-2", "url": "cisco/c-2", "titel": "C-2 | Hexwaren", "gtin": ""},
    ])
    b = _bundle(tmp_path, "Arista", [
        {"sku": "A-1", "url": "arista/a-1", "titel": "A-1 | Hexwaren", "gtin": ""},
        {"sku": "A-2", "url": "arista/a-2", "titel": "A-2 | Hexwaren", "gtin": ""},
    ])
    r = sweep_catalog({"Cisco": a, "Arista": b})
    assert r.ok, [str(f) for f in r.findings]
    assert r.n_brands == 2
    assert r.n_skus == 4


# ---- one positive test per collision class --------------------------------------------

def test_artikelnummer_collision_across_brands(tmp_path):
    a = _bundle(tmp_path, "Cisco", [{"sku": "SFP-10G-SR", "url": "cisco/sfp-10g-sr"}])
    b = _bundle(tmp_path, "Arista", [{"sku": "SFP-10G-SR", "url": "arista/sfp-10g-sr",
                                      "titel": "SFP-10G-SR Arista | Hexwaren"}])
    r = sweep_catalog({"Cisco": a, "Arista": b})
    assert not r.ok
    assert "Artikelnummer" in _kinds(r)
    f = next(f for f in r.findings if f.kind == "Artikelnummer")
    assert sorted(f.skus) == ["Arista:SFP-10G-SR", "Cisco:SFP-10G-SR"]


def test_url_pfad_collision_across_brands(tmp_path):
    a = _bundle(tmp_path, "Cisco", [{"sku": "C-1", "url": "shared/path"}])
    b = _bundle(tmp_path, "Arista", [{"sku": "A-1", "url": "shared/path"}])
    r = sweep_catalog({"Cisco": a, "Arista": b})
    assert "URL-Pfad" in _kinds(r)


def test_gtin_collision_across_brands(tmp_path):
    a = _bundle(tmp_path, "Cisco", [{"sku": "C-1", "gtin": "4006381333931"}])
    b = _bundle(tmp_path, "Arista", [{"sku": "A-1", "gtin": "4006381333931"}])
    r = sweep_catalog({"Cisco": a, "Arista": b})
    assert "GTIN" in _kinds(r)


def test_titel_collision_across_brands(tmp_path):
    a = _bundle(tmp_path, "Cisco", [{"sku": "C-1", "titel": "Identical Titel | Hexwaren"}])
    b = _bundle(tmp_path, "Arista", [{"sku": "A-1", "titel": "Identical Titel | Hexwaren"}])
    r = sweep_catalog({"Cisco": a, "Arista": b})
    assert "Titel-Tag (SEO)" in _kinds(r)


def test_same_brand_distinct_gtins_no_collision(tmp_path):
    # Two SKUs in ONE brand with different valid GTINs must not collide.
    a = _bundle(tmp_path, "Cisco", [
        {"sku": "C-1", "url": "cisco/c-1", "titel": "C-1 | Hexwaren", "gtin": "4006381333931"},
        {"sku": "C-2", "url": "cisco/c-2", "titel": "C-2 | Hexwaren", "gtin": "00012345600012"},
    ])
    r = sweep_catalog({"Cisco": a})
    assert r.ok, [str(f) for f in r.findings]


# ---- cross-brand sentence reuse: WARN at 2 brands, FAIL at 3 --------------------------

_SHARED = "<p>Dieses Modul arbeitet zuverlaessig in jedem modernen Rechenzentrum.</p>"


def test_cross_brand_sentence_two_brands_warns(tmp_path):
    a = _bundle(tmp_path, "Cisco", [{"sku": "C-1", "url": "cisco/c-1", "titel": "C-1 | Hexwaren",
                                     "besch": _SHARED}])
    b = _bundle(tmp_path, "Arista", [{"sku": "A-1", "url": "arista/a-1", "titel": "A-1 | Hexwaren",
                                      "besch": _SHARED}])
    r = sweep_catalog({"Cisco": a, "Arista": b})
    assert r.ok, [str(f) for f in r.findings]  # 2 brands is a WARN, not a FAIL
    assert any(w.kind == "Beschreibung" for w in r.warnings)


def test_cross_brand_sentence_three_brands_fails(tmp_path):
    a = _bundle(tmp_path, "Cisco", [{"sku": "C-1", "url": "cisco/c-1", "titel": "C-1 | Hexwaren",
                                     "besch": _SHARED}])
    b = _bundle(tmp_path, "Arista", [{"sku": "A-1", "url": "arista/a-1", "titel": "A-1 | Hexwaren",
                                      "besch": _SHARED}])
    c = _bundle(tmp_path, "HPE", [{"sku": "H-1", "url": "hpe/h-1", "titel": "H-1 | Hexwaren",
                                   "besch": _SHARED}])
    r = sweep_catalog({"Cisco": a, "Arista": b, "HPE": c})
    assert not r.ok
    assert "Beschreibung" in _kinds(r)


# ---- the tracked artifact -------------------------------------------------------------

def _load() -> dict:
    return yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_structure_and_reconciles():
    d = _load()
    assert d.get("policy")
    assert d["n_brands"] == 5
    assert d["n_skus"] == 902
    assert set(d["checks"]) == {"url_pfad", "gtin", "titel_tag", "beschreibung_cross_brand_3plus"}
    col = d["artikelnummer_collisions"]
    shared = col.get("shared") or []
    assert col["count"] == len(shared)
    for entry in shared:
        assert entry["sku"]
        brands = entry["brands"]
        assert len(brands) >= 2
        assert set(brands).issubset(BRANDS)


def test_thresholds_are_sane():
    # WARN strictly below FAIL, and FAIL at >=3 brands keeps the shipped 2-brand grounded
    # physics sentences (same DAC length / wavelength fact) out of the hard-fail set.
    assert merged_sweep.SENTENCE_CROSS_BRAND_WARN_BRANDS < merged_sweep.SENTENCE_CROSS_BRAND_FAIL_BRANDS
    assert merged_sweep.SENTENCE_CROSS_BRAND_FAIL_BRANDS >= 3
