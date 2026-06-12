"""Category-agnostic harvester (lib/harvest) — offline unit tests.

The whole point is reuse: the discover + crawl + fetch machinery carries NO category
knowledge. These tests prove it with a fully synthetic web (an injected fetcher), and the
decisive one (`test_second_category_routes_same_code`) drives TWO different category configs
through the identical code path — adding a category is config, not code.

Also proves the never-miss contract: a blocked datasheet lands in the deferred queue.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from lib import harvest as H
from lib.deferred_queue import DeferredQueue
from lib.harvest import HarvestConfig, classify, discover, extract_links, harvest, load_sources
from lib.local_fetch import FetchOutcome


# ---- a synthetic web + fetcher --------------------------------------------------------

def _fake_fetcher(pages: dict[str, str], tmp_path: Path, blocked: set[str] | None = None,
                  gone: set[str] | None = None):
    """Return fetch_fn(url)->FetchOutcome backed by an in-memory page map.

    `pages` maps url -> HTML. Anything not in `pages` and not flagged is a benign block.
    """
    blocked = blocked or set()
    gone = gone or set()
    written: dict[str, Path] = {}

    def _f(url: str) -> FetchOutcome:
        sid = url.rsplit("/", 1)[-1] or "root"
        if url in gone:
            return FetchOutcome("gone", sid, url, None, "fake", "", 0, 404, "gone")
        if url in blocked:
            return FetchOutcome("blocked", sid, url, None, "fake", "", 0, 403, "blocked")
        if url in pages:
            p = written.get(url)
            if p is None:
                p = tmp_path / f"page_{len(written)}.html"
                p.write_text(pages[url], encoding="utf-8")
                written[url] = p
            return FetchOutcome("ok", sid, url, p, "fake", "html", p.stat().st_size, 200)
        return FetchOutcome("blocked", sid, url, None, "fake", "", 0, 403, "unknown")

    return _f


def _cfg(category="transceivers", domains=("acme.test",)) -> HarvestConfig:
    return HarvestConfig(
        category=category,
        allowed_domains=list(domains),
        datasheet_patterns=[r"data_?sheet", r"\.pdf$"],
        follow_patterns=["listing", "index"],
        max_depth=3,
        max_pages=100,
    )


# ---- link extraction + classification -------------------------------------------------

def test_extract_links_resolves_relative_and_filters_domain():
    html = """
      <a href="/c/datasheet_1.html">ds1</a>
      <a href="https://acme.test/c/listing.html">listing</a>
      <a href="https://evil.test/c/datasheet_x.html">offsite</a>
      <a href="mailto:x@y">mail</a>
    """
    links = extract_links(html, "https://acme.test/c/index.html", ["acme.test"])
    assert "https://acme.test/c/datasheet_1.html" in links
    assert "https://acme.test/c/listing.html" in links
    assert all("evil.test" not in u for u in links)   # offsite dropped
    assert all("mailto" not in u for u in links)       # non-http dropped


def test_classify_datasheet_follow_skip():
    cfg = _cfg()
    assert classify("https://acme.test/x/datasheet_9.html", cfg) == "datasheet"
    assert classify("https://acme.test/x/spec.pdf", cfg) == "datasheet"
    assert classify("https://acme.test/x/listing.html", cfg) == "follow"
    assert classify("https://acme.test/x/about.html", cfg) == "skip"


# ---- discovery (BFS over a synthetic web) ---------------------------------------------

def test_discover_crawls_follow_pages_and_collects_datasheets(tmp_path):
    pages = {
        "https://acme.test/index.html":
            '<a href="/datasheet_a.html">a</a><a href="/listing.html">more</a>',
        "https://acme.test/listing.html":
            '<a href="/datasheet_b.html">b</a><a href="/spec.pdf">c</a>',
    }
    cfg = _cfg()
    brand = H.BrandSources(name="Acme", seeds=["https://acme.test/index.html"])
    fetch_fn = _fake_fetcher(pages, tmp_path)
    datasheets, pages_crawled = discover(brand, cfg, root=tmp_path, fetch_fn=fetch_fn)
    assert set(datasheets) == {
        "https://acme.test/datasheet_a.html",
        "https://acme.test/datasheet_b.html",
        "https://acme.test/spec.pdf",
    }
    assert pages_crawled == 2  # index + listing fetched; datasheets are not crawled into


def test_discover_folds_in_frontier_file(tmp_path):
    # the WebSearch seam: a frontier file adds datasheet URLs without touching code
    frontier = tmp_path / "frontier.txt"
    frontier.write_text("# claude adds urls here\nhttps://acme.test/datasheet_z.html\n",
                        encoding="utf-8")
    pages = {"https://acme.test/index.html": "<a href='/about.html'>x</a>"}
    cfg = _cfg()
    brand = H.BrandSources(name="Acme", seeds=["https://acme.test/index.html"],
                           discovered_file=str(frontier))
    datasheets, _ = discover(brand, cfg, root=tmp_path, fetch_fn=_fake_fetcher(pages, tmp_path))
    assert "https://acme.test/datasheet_z.html" in datasheets


# ---- the real config seam loads -------------------------------------------------------

def test_real_transceivers_config_loads():
    cfg = load_sources("transceivers")
    assert cfg.category == "transceivers"
    assert "cisco.com" in cfg.allowed_domains
    assert "Cisco" in cfg.brands
    assert cfg.brands["Cisco"].seeds and cfg.brands["Cisco"].search_terms
    # datasheet pattern matches a real Cisco collateral id
    assert classify("https://www.cisco.com/c/.../data_sheet_c78-455693.html", cfg) == "datasheet"


# ---- the decisive reuse proof: a SECOND category, same code ---------------------------

def _write_category(root: Path, category: str, domain: str) -> None:
    d = root / "config" / "sources"
    d.mkdir(parents=True, exist_ok=True)
    doc = {
        "category": category,
        "allowed_domains": [domain],
        "datasheet_patterns": [r"data_?sheet", r"\.pdf$"],
        "follow_patterns": ["listing"],
        "crawl": {"max_depth": 2, "max_pages": 50},
        "brands": {"BrandX": {"seeds": [f"https://{domain}/index.html"]}},
    }
    (d / f"{category}.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")


def test_second_category_routes_same_code(tmp_path):
    # Two unrelated categories, two domains; the SAME discover() handles both with only
    # config differing. This is the ADD_A_CATEGORY guarantee.
    _write_category(tmp_path, "switches", "switchco.test")
    _write_category(tmp_path, "servers", "serverco.test")

    sw = load_sources("switches", root=tmp_path)
    sv = load_sources("servers", root=tmp_path)
    assert sw.allowed_domains == ["switchco.test"]
    assert sv.allowed_domains == ["serverco.test"]

    pages_sw = {"https://switchco.test/index.html": '<a href="/datasheet_s1.html">s1</a>'}
    pages_sv = {"https://serverco.test/index.html": '<a href="/datasheet_v1.html">v1</a>'}
    (tmp_path / "sw").mkdir(exist_ok=True)
    (tmp_path / "sv").mkdir(exist_ok=True)
    ds_sw, _ = discover(sw.brands["BrandX"], sw, root=tmp_path,
                        fetch_fn=_fake_fetcher(pages_sw, tmp_path / "sw"))
    ds_sv, _ = discover(sv.brands["BrandX"], sv, root=tmp_path,
                        fetch_fn=_fake_fetcher(pages_sv, tmp_path / "sv"))
    assert ds_sw == ["https://switchco.test/datasheet_s1.html"]
    assert ds_sv == ["https://serverco.test/datasheet_v1.html"]


# ---- never-miss: a blocked datasheet lands in the deferred queue ----------------------

def test_harvest_routes_blocked_to_queue_and_gone_to_terminal(tmp_path):
    _write_category(tmp_path, "widgets", "widgetco.test")
    pages = {
        "https://widgetco.test/index.html":
            '<a href="/datasheet_ok.html">ok</a>'
            '<a href="/datasheet_blocked.html">blk</a>'
            '<a href="/datasheet_gone.html">gone</a>',
        "https://widgetco.test/datasheet_ok.html": "<html>ok</html>",
    }
    blocked = {"https://widgetco.test/datasheet_blocked.html"}
    gone = {"https://widgetco.test/datasheet_gone.html"}
    fetch_fn = _fake_fetcher(pages, tmp_path, blocked=blocked, gone=gone)
    q = DeferredQueue(tmp_path / "dq.json")

    reports = harvest("widgets", root=tmp_path, fetch_fn=fetch_fn, queue=q)
    rep = reports[0]
    assert rep.blocked == ["https://widgetco.test/datasheet_blocked.html"]
    assert rep.gone == ["https://widgetco.test/datasheet_gone.html"]
    assert "datasheet_ok.html" in rep.fetched[0]
    # the blocked URL is now queued (never missed); the gone URL is terminal
    assert q.get("https://widgetco.test/datasheet_blocked.html")["state"] == "pending"
    assert q.get("https://widgetco.test/datasheet_gone.html")["state"] == "gone"
    assert (tmp_path / "dq.json").exists()  # queue persisted
