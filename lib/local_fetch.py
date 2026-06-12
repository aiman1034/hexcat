"""Universal local datasheet fetcher — category-agnostic, local, ZERO-DOLLAR.

This is Step 1, the foundation: the ability to autonomously reach and fetch every
datasheet a manufacturer publishes, run from the local PC (residential/business IP) so it
clears the bot blocks that 403 a hosted/cloud WebFetch. It fetches whatever URL it is
handed — it knows nothing about transceivers, switches, or any category. Every future
category inherits it unchanged; only new *sources* are ever supplied.

Escalation ladder (all local, all $0, cheapest first — escalate only on real failure):

  Tier 1  plain HTTP GET (httpx). Two header profiles, in order:
            (a) a realistic desktop-Chrome profile (UA + sec-ch-ua + sec-fetch + Accept*),
            (b) a minimal honest profile (Accept + Accept-Language only).
          We try the browser profile first, and on a 403/429/503 retry with the minimal
          profile. (Hard-won lesson from src/hexcat/ledger/fetch.py: against Akamai-fronted
          Cisco, a *spoofed* Chrome UA without the matching client-hints fingerprint can
          look faker than no UA at all — so the minimal profile is a genuine fallback, not
          a downgrade. From the local residential IP both profiles return 200; the IP is
          what matters most, and the two-profile retry covers the rest.)
  Tier 2  headless browser (Playwright + local Chromium), headless -> headed. Carries the
          browser's real TLS + client-hints fingerprint (a browser-context HTTP GET for
          PDFs/WAF-walled assets) and renders JS single-page apps to their post-JS DOM.
          Chromium lives on the project's D: drive (PLAYWRIGHT_BROWSERS_PATH), gitignored,
          never a paid API. ``--disable-http2`` avoids ERR_HTTP2_PROTOCOL_ERROR on some
          HPE/Aruba hosts.

Politeness (never hammer a manufacturer): one identity per host, a jittered 2-5s delay
between requests to the same host, no parallel hammering. The base delay can be bumped up
for the rest of a run if blocks appear.

Outcome, never an exception on a block: ``fetch`` returns a :class:`FetchOutcome` whose
``state`` is one of ok / blocked / gone / error. A *blocked* page is handed to the caller
(the harvester) to queue for a later retry — it is never missed, fabricated, or skipped.
Only a hard 404/410 is terminal (``gone``).

Offline-testable: inject ``http_get`` to drive Tier 1 deterministically; when injected,
the browser tier and all real sleeping are skipped, so the suite never opens a window or
touches the network.
"""
from __future__ import annotations

import os
import random
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

_REPO_ROOT = Path(__file__).resolve().parents[1]  # .../hexcat
CACHE_DIR = _REPO_ROOT / "datasheets" / "cache"
MANUAL_DIR = _REPO_ROOT / "datasheets"
BROWSER_DIR = _REPO_ROOT / ".playwright-browsers"

# HTTP statuses that mean "blocked, retry later" vs "confirmed gone, terminal".
BLOCK_STATUSES = frozenset({401, 403, 405, 406, 408, 409, 423, 429, 500, 502, 503, 504})
GONE_STATUSES = frozenset({404, 410})

# (a) realistic desktop-Chrome profile — UA paired with the client-hints + fetch-metadata
# headers a real Chrome sends, so the fingerprint is internally consistent.
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,application/pdf,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# (b) minimal honest profile — no spoofed UA. Proven to clear Cisco/Akamai where a bare
# spoofed Chrome UA does not. See src/hexcat/ledger/fetch.py docstring.
MINIMAL_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

HEADER_PROFILES = (("browser", BROWSER_HEADERS), ("minimal", MINIMAL_HEADERS))


# --------------------------------------------------------------------------------------
# Politeness: per-host jittered throttle.
# --------------------------------------------------------------------------------------

@dataclass
class HostThrottle:
    """One identity per host, a jittered delay between same-host requests.

    ``base_delay`` is the floor; an extra uniform ``jitter`` is added each wait, so a
    default ``2.0 + U(0, 3.0)`` lands in the 2-5s window the mission asks for. ``bump``
    raises the floor for the rest of a run when blocks start appearing.
    """

    base_delay: float = 2.0
    jitter: float = 3.0
    max_base: float = 30.0
    _last: dict[str, float] = field(default_factory=dict)
    _sleep = staticmethod(time.sleep)

    def wait(self, host: str) -> None:
        now = time.monotonic()
        last = self._last.get(host)
        target = self.base_delay + random.uniform(0.0, self.jitter)
        if last is not None:
            elapsed = now - last
            if elapsed < target:
                self._sleep(target - elapsed)
        self._last[host] = time.monotonic()

    def bump(self, factor: float = 1.5) -> float:
        """Raise the per-host floor (called after a block). Returns the new base delay."""
        self.base_delay = min(self.base_delay * factor, self.max_base)
        return self.base_delay


# --------------------------------------------------------------------------------------
# Result type.
# --------------------------------------------------------------------------------------

@dataclass
class FetchOutcome:
    state: str            # "ok" | "blocked" | "gone" | "error"
    source_id: str
    url: str
    path: Path | None = None
    tier: str = ""        # "cache" | "tier1-browser" | "tier1-minimal" | "tier2-browser" | "manual"
    content_type: str = ""  # "html" | "pdf"
    bytes: int = 0
    http_status: int = 0
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.state == "ok"

    @property
    def blocked(self) -> bool:
        return self.state == "blocked"

    @property
    def gone(self) -> bool:
        return self.state == "gone"

    def read_bytes(self) -> bytes:
        if self.path is None:
            raise FileNotFoundError(f"no cached body for {self.url!r} (state={self.state})")
        return self.path.read_bytes()

    def read_text(self) -> str:
        if self.path is None:
            raise FileNotFoundError(f"no cached body for {self.url!r} (state={self.state})")
        return self.path.read_text(encoding="utf-8", errors="replace")


def source_id_from_url(url: str) -> str:
    """Stable, filesystem-safe cache key from a URL.

    Primary key is the sanitized last path segment (minus a trailing .html/.pdf), which
    keeps human-readable names. A Cisco doc id (``c\\d\\d-\\d+``) inside the segment is
    preferred when present, so this layer reuses the existing datasheets/cache keys
    (e.g. ...data_sheet_c78-455693.html -> ``c78-455693``). When the segment is empty or
    generic, the host is folded in to avoid cross-host collisions.
    """
    parts = urlsplit(url)
    stem = (parts.path or "").rstrip("/").rsplit("/", 1)[-1]
    stem = re.sub(r"\.(html?|pdf)$", "", stem, flags=re.I)
    m = re.search(r"(c\d{2}-\d+)", stem, re.I)
    if m:
        return m.group(1).lower()
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-_.").lower()
    if not slug or slug in {"index", "datasheet", "data-sheet", "home", "default"}:
        host = parts.netloc.replace(":", "-")
        slug = f"{host}-{slug}".strip("-")
    return slug or "source"


def _ext_for(url: str, content_type: str, body: bytes = b"") -> str:
    if body[:4] == b"%PDF" or "pdf" in content_type.lower() or url.lower().split("?")[0].endswith(".pdf"):
        return "pdf"
    return "html"


def _classify_status(status: int) -> str:
    if status in GONE_STATUSES:
        return "gone"
    if status in BLOCK_STATUSES:
        return "blocked"
    return "error"


def _find_manual(source_id: str) -> Path | None:
    for ext in ("html", "htm", "pdf"):
        p = MANUAL_DIR / f"{source_id}.{ext}"
        if p.exists():
            return p
    return None


def _cached(source_id: str, cache_dir: Path) -> tuple[Path, str] | None:
    for ext in ("html", "pdf"):
        p = cache_dir / f"{source_id}.{ext}"
        if p.exists():
            return p, ext
    return None


# --------------------------------------------------------------------------------------
# Tier 1 — plain HTTP, two header profiles.
# --------------------------------------------------------------------------------------

def _httpx_get(url: str, headers: dict[str, str]) -> tuple[int, bytes, str]:
    import httpx

    r = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
    return r.status_code, r.content, r.headers.get("content-type", "")


# --------------------------------------------------------------------------------------
# The public entry point.
# --------------------------------------------------------------------------------------

def fetch(
    url: str,
    source_id: str | None = None,
    *,
    cache_dir: Path | None = None,
    use_cache: bool = True,
    allow_network: bool = True,
    use_browser: bool = True,
    use_manual: bool = True,
    http_get=None,
    throttle: HostThrottle | None = None,
) -> FetchOutcome:
    """Fetch one URL, cheapest tier first; never raise on a block.

    Returns a :class:`FetchOutcome`. ``ok`` carries the cached body path; ``blocked`` means
    "retry later" (hand it to the deferred queue); ``gone`` is a terminal 404/410; ``error``
    is an unexpected failure with no body.

    ``http_get(url, headers) -> (status, body, content_type)`` is injectable for offline
    tests. When provided, the browser tier and all real sleeping are skipped.
    """
    sid = source_id or source_id_from_url(url)
    cdir = cache_dir or CACHE_DIR
    cdir.mkdir(parents=True, exist_ok=True)
    injected = http_get is not None

    # Tier "cache": reuse a prior successful fetch.
    if use_cache:
        hit = _cached(sid, cdir)
        if hit is not None:
            path, ext = hit
            return FetchOutcome("ok", sid, url, path, "cache", ext, path.stat().st_size, 200)

    last_status = 0
    last_detail = ""

    if allow_network:
        host = urlsplit(url).netloc
        getter = http_get or _httpx_get

        # Tier 1: try each header profile in order; a per-host throttle precedes each
        # real (non-injected) network attempt.
        for profile_name, headers in HEADER_PROFILES:
            if not injected and throttle is not None:
                throttle.wait(host)
            try:
                status, body, ctype = getter(url, headers)
            except Exception as e:  # noqa: BLE001 — record and try the next profile/tier
                last_detail = f"tier1-{profile_name} raised: {e}"
                last_status = 0
                continue
            last_status = status
            if status == 200 and body:
                ext = _ext_for(url, ctype, body)
                out = cdir / f"{sid}.{ext}"
                out.write_bytes(body)
                return FetchOutcome("ok", sid, url, out, f"tier1-{profile_name}", ext,
                                    len(body), 200)
            if status in GONE_STATUSES:
                return FetchOutcome("gone", sid, url, None, f"tier1-{profile_name}", "",
                                    0, status, f"HTTP {status} (confirmed gone)")
            last_detail = f"tier1-{profile_name} HTTP {status}"
            # Non-200, non-gone: fall through to the next profile, then Tier 2.

        # Tier 2: headless -> headed browser. Skipped under an injected getter (offline
        # tests) and when the caller disabled it.
        if use_browser and not injected:
            if throttle is not None:
                throttle.wait(host)
            try:
                status, body, ctype, final = _browser_get(url)
                last_status = status or last_status
                if status == 200 and body:
                    ext = _ext_for(final or url, ctype, body)
                    out = cdir / f"{sid}.{ext}"
                    out.write_bytes(body)
                    return FetchOutcome("ok", sid, url, out, "tier2-browser", ext,
                                        len(body), 200)
                if status in GONE_STATUSES:
                    return FetchOutcome("gone", sid, url, None, "tier2-browser", "",
                                        0, status, f"HTTP {status} (confirmed gone)")
                last_detail = f"tier2-browser HTTP {status}"
            except Exception as e:  # noqa: BLE001 — fall through to manual / blocked
                last_detail = f"tier2-browser raised: {e}"

    # Manual drop-in safety net (the 1000% rule's backstop).
    if use_manual:
        manual = _find_manual(sid)
        if manual is not None:
            ext = "pdf" if manual.suffix.lower() == ".pdf" else "html"
            return FetchOutcome("ok", sid, url, manual, "manual", ext,
                                manual.stat().st_size, 200)

    # Nothing yielded a body. Classify for the caller: gone is terminal, everything else
    # is blocked (retry later) unless we never even reached the network.
    if not allow_network:
        return FetchOutcome("error", sid, url, None, "", "", 0, 0,
                            "network disabled and no cache/manual body")
    state = _classify_status(last_status) if last_status else "blocked"
    if state == "error" and last_status:
        # An unexpected status with a body-less response — treat as blocked so it is
        # retried rather than silently dropped (never miss a page).
        state = "blocked"
    return FetchOutcome(state, sid, url, None, "", "", 0, last_status,
                        last_detail or "no body from any tier")


# --------------------------------------------------------------------------------------
# Tier 2 internals (carried forward from src/hexcat/ledger/fetch.py, proven).
# --------------------------------------------------------------------------------------

def _browser_get(
    url: str,
    *,
    timeout_ms: int = 45000,
    settle_ms: int = 3000,
) -> tuple[int, bytes, str, str]:
    """Browser-grade fetch with a headless->headed escalation: (status, body, ctype, final).

    Headless first (the common case never opens a window); escalate to headed when the
    headless pass yields nothing, since some WAFs/captcha gates reject the headless
    fingerprint but pass a headed one.
    """
    last_exc: Exception | None = None
    for headless in (True, False):
        try:
            status, body, ctype, final = _browser_get_once(
                url, headless=headless, timeout_ms=timeout_ms, settle_ms=settle_ms
            )
        except Exception as e:  # noqa: BLE001 — retry headed, then give up
            last_exc = e
            continue
        if (status == 200 and body) or not headless:
            return status, body, ctype, final
    if last_exc is not None:
        raise last_exc
    return 0, b"", "", url


def _browser_get_once(
    url: str,
    *,
    headless: bool,
    timeout_ms: int = 45000,
    settle_ms: int = 3000,
) -> tuple[int, bytes, str, str]:
    """One browser fetch attempt: a browser-context HTTP GET (best for PDFs/WAF assets),
    falling through to a full JS render that returns the post-JS DOM."""
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BROWSER_DIR))
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=["--disable-http2"])
        try:
            context = browser.new_context(locale="en-US", user_agent=BROWSER_HEADERS["User-Agent"])
            status, ctype, body = 0, "", b""
            try:
                resp = context.request.get(url, timeout=timeout_ms)
                status = resp.status
                ctype = resp.headers.get("content-type", "")
                body = resp.body()
            except Exception:  # noqa: BLE001 — fall through to a full render
                pass
            if status == 200 and (body[:4] == b"%PDF" or "pdf" in ctype.lower()):
                return status, body, ctype or "application/pdf", url
            if status in GONE_STATUSES:
                return status, b"", ctype, url

            page = context.new_page()
            r = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:  # noqa: BLE001 — networkidle is best-effort
                pass
            page.wait_for_timeout(settle_ms)
            html = page.content()
            pstatus = (r.status if r is not None else 0) or (status or 200)
            return pstatus, html.encode("utf-8", "replace"), "text/html", page.url
        finally:
            browser.close()
