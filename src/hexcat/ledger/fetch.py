"""Datasheet fetch layer — Stage 1, ZERO-DOLLAR, deterministic.

Tiered, cheapest-first, escalate only on real failure:

  Tier 1  plain httpx GET (honest default User-Agent).  <-- proven to clear Cisco's
          403 on C78-455693. Counter-intuitively, SPOOFING a desktop-Chrome UA is what
          triggers the Akamai bot block (a "Chrome" UA without sec-ch-ua/sec-fetch
          fingerprint headers looks fake); the plain client passes.
  Tier 2  headless browser (playwright + local Chromium) — NOT built; free/local if ever
          needed. Escalate only after Tier 1 demonstrably fails, and only with operator
          confirmation (Chromium download goes to a D: path).
  Tier 3  manual drop-in — read a datasheet the operator downloaded by hand into
          datasheets/<source>.{html,pdf}. The guaranteed safety net behind the 1000% rule.

Every successful fetch is cached under datasheets/cache/ and reused (never re-fetched).
No paid API, no network beyond the manufacturer GET. Tier 2 is intentionally absent.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_DIR.parents[2]  # .../hexcat
CACHE_DIR = _REPO_ROOT / "datasheets" / "cache"
MANUAL_DIR = _REPO_ROOT / "datasheets"

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
    tier: str          # "cache" | "tier1-httpx" | "tier3-manual"
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
    http_get=None,
) -> FetchResult:
    """Fetch one datasheet, cheapest tier first. `http_get` is injectable for tests.

    Order: cache -> Tier 1 (httpx) -> Tier 3 (manual drop-in). Tier 3 is also tried first
    implicitly via cache; if the network is unavailable, a manual file still satisfies.
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
        except Exception as e:  # noqa: BLE001 — fall through to manual tier
            last_err = e

    # Tier 3: manual drop-in safety net.
    manual = _find_manual(sid)
    if manual is not None:
        ext = "pdf" if manual.suffix.lower() == ".pdf" else "html"
        return FetchResult(sid, url, manual, "tier3-manual", ext, manual.stat().st_size)

    raise FetchError(
        f"Could not fetch {url!r}. Tier 1 failed ({last_err}); no manual drop-in at "
        f"{MANUAL_DIR / (sid + '.html')} or .pdf. Download the datasheet by hand to enable Tier 3."
    )


def _httpx_get(url: str) -> tuple[int, bytes, str]:
    import httpx

    r = httpx.get(url, headers=DEFAULT_HEADERS, follow_redirects=True, timeout=30)
    return r.status_code, r.content, r.headers.get("content-type", "")
