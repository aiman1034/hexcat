"""Datasheet fetch layer — Stage 1, ZERO-DOLLAR, deterministic.

Tiered, cheapest-first, escalate only on real failure:

  Tier 1  plain httpx GET (honest default User-Agent).  <-- proven to clear Cisco's
          403 on C78-455693. Counter-intuitively, SPOOFING a desktop-Chrome UA is what
          triggers the Akamai bot block (a "Chrome" UA without sec-ch-ua/sec-fetch
          fingerprint headers looks fake); the plain client passes.
  Tier 2  headless browser (playwright + local Chromium) — for sources Tier 1 cannot
          reach: soft-WAF blocks that stall/403 a plain client (e.g. HPE psnow PDFs) and
          JS single-page apps that serve only a shell to a non-browser (Juniper HCT,
          Extreme/Avaya optics matrix). Two moves in one: a browser-context HTTP GET
          (real TLS + header fingerprint, beats the WAF) and, for HTML shells, a full
          page render that returns the post-JS DOM. Free/local; Chromium lives on a D:
          path (PLAYWRIGHT_BROWSERS_PATH), never bundled, never a paid API.
  Tier 3  manual drop-in — read a datasheet the operator downloaded by hand into
          datasheets/<source>.{html,pdf}. The guaranteed safety net behind the 1000% rule.

Every successful fetch is cached under datasheets/cache/ and reused (never re-fetched).
No paid API, no network beyond the manufacturer GET/render.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_DIR.parents[2]  # .../hexcat
CACHE_DIR = _REPO_ROOT / "datasheets" / "cache"
MANUAL_DIR = _REPO_ROOT / "datasheets"
# Local Chromium store for Tier 2 — kept on the project's (D:) drive, gitignored.
BROWSER_DIR = _REPO_ROOT / ".playwright-browsers"

# Deliberately NOT a spoofed browser UA — see module docstring.
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class FetchError(Exception):
    """All fetch tiers failed (and no manual drop-in present)."""


@dataclass
class FetchResult:
    source_id: str
    url: str
    path: Path
    tier: str          # "cache" | "tier1-httpx" | "tier2-browser" | "tier3-manual"
    content_type: str  # "html" | "pdf"
    bytes: int

    def read_bytes(self) -> bytes:
        return self.path.read_bytes()

    def read_text(self) -> str:
        return self.path.read_text(encoding="utf-8", errors="replace")


def source_id_from_url(url: str) -> str:
    """Stable cache key from a datasheet URL, e.g. ...data_sheet_c78-455693.html -> c78-455693."""
    stem = url.rstrip("/").rsplit("/", 1)[-1]
    stem = re.sub(r"\.(html?|pdf)$", "", stem, flags=re.I)
    m = re.search(r"(c\d{2}-\d+)", stem, re.I)
    return (m.group(1) if m else stem).lower()


def _ext_for(url: str, content_type: str) -> str:
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        return "pdf"
    return "html"


def _find_manual(source_id: str) -> Path | None:
    for ext in ("html", "htm", "pdf"):
        p = MANUAL_DIR / f"{source_id}.{ext}"
        if p.exists():
            return p
    return None


def fetch_datasheet(
    url: str,
    source_id: str | None = None,
    *,
    use_cache: bool = True,
    allow_network: bool = True,
    use_browser: bool = True,
    http_get=None,
) -> FetchResult:
    """Fetch one datasheet, cheapest tier first. `http_get` is injectable for tests.

    Order: cache -> Tier 1 (httpx) -> Tier 2 (headless browser) -> Tier 3 (manual drop-in).
    Tier 2 only runs after Tier 1 demonstrably fails, is skipped when a test getter is
    injected (`http_get`) so tests stay offline, and degrades to Tier 3 if Playwright/
    Chromium is unavailable. A manual file also satisfies when the network is down.
    """
    sid = source_id or source_id_from_url(url)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Tier "cache": reuse a prior successful fetch.
    if use_cache:
        for ext in ("html", "pdf"):
            cached = CACHE_DIR / f"{sid}.{ext}"
            if cached.exists():
                return FetchResult(sid, url, cached, "cache", ext, cached.stat().st_size)

    # Tier 1: plain httpx GET.
    last_err: Exception | None = None
    if allow_network:
        try:
            getter = http_get or _httpx_get
            status, body, ctype = getter(url)
            if status == 200 and body:
                ext = _ext_for(url, ctype)
                out = CACHE_DIR / f"{sid}.{ext}"
                out.write_bytes(body)
                return FetchResult(sid, url, out, "tier1-httpx", ext, len(body))
            last_err = FetchError(f"Tier 1 HTTP {status} for {url}")
        except Exception as e:  # noqa: BLE001 — fall through to next tier
            last_err = e

    # Tier 2: headless browser (real fingerprint + JS render). Skipped under injected
    # getters (tests) so the suite never launches a browser or touches the network.
    if allow_network and use_browser and http_get is None:
        try:
            status, body, ctype, final = _browser_get(url)
            if status == 200 and body:
                ext = _ext_for(final or url, ctype)
                out = CACHE_DIR / f"{sid}.{ext}"
                out.write_bytes(body)
                return FetchResult(sid, url, out, "tier2-browser", ext, len(body))
            last_err = FetchError(f"Tier 2 browser HTTP {status} for {url}")
        except Exception as e:  # noqa: BLE001 — fall through to manual tier
            last_err = e

    # Tier 3: manual drop-in safety net.
    manual = _find_manual(sid)
    if manual is not None:
        ext = "pdf" if manual.suffix.lower() == ".pdf" else "html"
        return FetchResult(sid, url, manual, "tier3-manual", ext, manual.stat().st_size)

    raise FetchError(
        f"Could not fetch {url!r}. Tier 1 + Tier 2 failed ({last_err}); no manual drop-in at "
        f"{MANUAL_DIR / (sid + '.html')} or .pdf. Download the datasheet by hand to enable Tier 3."
    )


def fetch_via_browser(url: str, source_id: str | None = None) -> FetchResult:
    """Force a Tier-2 browser fetch and cache the result (tier='tier2-browser').

    Use for sources known to defeat Tier 1 even with a 200 — JS single-page apps that
    serve only a shell to a plain client (Juniper HCT, Extreme/Avaya optics matrix). The
    cached bytes are the post-JS DOM, ready for the deterministic miner.
    """
    sid = source_id or source_id_from_url(url)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    status, body, ctype, final = _browser_get(url)
    if status != 200 or not body:
        raise FetchError(f"Tier 2 browser HTTP {status} for {url}")
    ext = _ext_for(final or url, ctype)
    out = CACHE_DIR / f"{sid}.{ext}"
    out.write_bytes(body)
    return FetchResult(sid, url, out, "tier2-browser", ext, len(body))


def _httpx_get(url: str) -> tuple[int, bytes, str]:
    import httpx

    r = httpx.get(url, headers=DEFAULT_HEADERS, follow_redirects=True, timeout=30)
    return r.status_code, r.content, r.headers.get("content-type", "")


def _browser_get(
    url: str,
    *,
    timeout_ms: int = 45000,
    settle_ms: int = 3000,
) -> tuple[int, bytes, str, str]:
    """Browser-grade fetch with a headless->headed escalation: (status, body, ctype, final).

    Try a fast headless pass first; if it fails (empty/non-200/error) escalate to a headed
    browser. Empirically, some manufacturer WAFs and captcha gates reject the headless
    fingerprint but pass a headed one — HPE's transceiver PDF 403s headless yet returns 200
    headed; Juniper's HCT (hCaptcha-gated) likewise needs headed. Headless stays the default
    so the common case never opens a window.
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
    """One browser fetch attempt at a given headless setting.

    1) Browser-context HTTP GET — carries Chromium's real TLS + header fingerprint, which
       clears soft WAFs that stall/403 a plain httpx client. If it yields a PDF, return bytes.
    2) Otherwise render the page (goto + settle) and return the post-JS DOM as HTML — this
       materializes the part-number grids that JS single-page apps build client-side.
    """
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BROWSER_DIR))
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # --disable-http2 avoids ERR_HTTP2_PROTOCOL_ERROR seen on some HPE/Aruba hosts.
        browser = p.chromium.launch(headless=headless, args=["--disable-http2"])
        try:
            context = browser.new_context(locale="en-US")
            # (1) browser-context HTTP GET — best for PDFs and WAF-walled assets.
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

            # (2) full render for HTML / JS single-page apps.
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
