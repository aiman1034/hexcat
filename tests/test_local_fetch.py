"""Universal fetcher (lib/local_fetch) — offline unit tests.

The fetch ladder is driven by an INJECTED ``http_get`` so the suite never opens a browser
or touches the network. Covers: the two-header-profile Tier-1 retry, the blocked / gone /
ok outcome classification (the deferred-queue contract), cache reuse, the source-id keying,
and the per-host politeness throttle.
"""
from __future__ import annotations

from lib import local_fetch as LF
from lib.local_fetch import HostThrottle, fetch, source_id_from_url


def _getter(script):
    """Build an http_get(url, headers) that replays a list of (status, body, ctype)."""
    calls = []

    def _g(url, headers):
        calls.append(headers)
        status, body, ctype = script[min(len(calls) - 1, len(script) - 1)]
        return status, body, ctype

    _g.calls = calls
    return _g


# ---- source-id keying -----------------------------------------------------------------

def test_source_id_prefers_cisco_doc_id():
    u = "https://www.cisco.com/c/en/us/.../data_sheet_c78-455693.html"
    assert source_id_from_url(u) == "c78-455693"


def test_source_id_slugs_generic_segment_and_folds_host_when_generic():
    assert source_id_from_url("https://x.example.com/foo/Bar_Sheet.pdf") == "bar_sheet"
    # a generic last segment folds in the host to avoid cross-host collisions
    sid = source_id_from_url("https://a.example.com/datasheet.html")
    assert "example.com" in sid


# ---- Tier 1 two-profile behavior ------------------------------------------------------

def test_first_profile_200_is_ok(tmp_path):
    g = _getter([(200, b"<html>ok</html>", "text/html")])
    out = fetch("https://h.test/a.html", cache_dir=tmp_path, http_get=g, use_manual=False)
    assert out.ok and out.tier == "tier1-browser"
    assert out.read_bytes() == b"<html>ok</html>"
    assert len(g.calls) == 1  # minimal profile not needed


def test_403_then_minimal_profile_succeeds(tmp_path):
    g = _getter([(403, b"", "text/html"), (200, b"%PDF-1.7 body", "application/pdf")])
    out = fetch("https://h.test/x", cache_dir=tmp_path, http_get=g, use_manual=False)
    assert out.ok and out.tier == "tier1-minimal"
    assert out.content_type == "pdf"
    assert [h.get("User-Agent") is not None for h in g.calls] == [True, False]


def test_404_is_terminal_gone(tmp_path):
    g = _getter([(404, b"", "text/html")])
    out = fetch("https://h.test/missing", cache_dir=tmp_path, http_get=g, use_manual=False)
    assert out.gone and out.state == "gone" and out.http_status == 404


def test_403_both_profiles_is_blocked_not_raised(tmp_path):
    g = _getter([(403, b"", ""), (429, b"", "")])
    out = fetch("https://h.test/wall", cache_dir=tmp_path, http_get=g,
                use_manual=False, use_browser=False)
    assert out.blocked and out.state == "blocked"
    assert out.http_status == 429  # last status seen


def test_network_disabled_without_cache_is_error(tmp_path):
    out = fetch("https://h.test/x", cache_dir=tmp_path, allow_network=False, use_manual=False)
    assert out.state == "error" and out.path is None


# ---- cache reuse ----------------------------------------------------------------------

def test_cache_hit_short_circuits_network(tmp_path):
    (tmp_path / "c78-455693.html").write_bytes(b"cached")
    u = "https://www.cisco.com/.../data_sheet_c78-455693.html"
    out = fetch(u, cache_dir=tmp_path, http_get=_getter([(500, b"", "")]), use_manual=False)
    assert out.ok and out.tier == "cache" and out.read_bytes() == b"cached"


# ---- politeness throttle --------------------------------------------------------------

def test_throttle_sleeps_between_same_host_requests():
    t = HostThrottle(base_delay=2.0, jitter=0.0)
    slept: list[float] = []
    t._sleep = lambda s: slept.append(s)
    t.wait("host.a")          # first call: no prior timestamp, no sleep
    assert slept == []
    t.wait("host.a")          # second call: must wait ~base_delay
    assert len(slept) == 1 and 0 < slept[0] <= 2.0


def test_throttle_bump_raises_floor_and_caps():
    t = HostThrottle(base_delay=2.0, jitter=0.0, max_base=5.0)
    assert t.bump(2.0) == 4.0
    assert t.bump(2.0) == 5.0  # capped at max_base


def test_block_statuses_disjoint_from_gone():
    assert LF.BLOCK_STATUSES.isdisjoint(LF.GONE_STATUSES)
    assert 403 in LF.BLOCK_STATUSES and 404 in LF.GONE_STATUSES
