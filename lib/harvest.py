"""Category-agnostic datasheet harvester — config-driven, local, ZERO-DOLLAR.

The fetch machinery (:mod:`lib.local_fetch`) and the retry queue (:mod:`lib.deferred_queue`)
are universal. So is *this* harvester: it discovers and fetches the complete datasheet set
for a (brand, category), but it knows nothing about transceivers, switches, or servers. All
per-category knowledge lives in CONFIG — ``config/sources/<category>.yaml`` — which is a
seam consistent with the project's ADD_A_CATEGORY philosophy: adding a new category is a new
config file and ZERO code changes here.

What the config supplies (and the code consumes generically):

  * ``allowed_domains``     — discovery never leaves the manufacturer's own domains.
  * ``datasheet_patterns``  — regexes marking a link as a terminal datasheet to fetch.
  * ``follow_patterns``     — regexes marking a link as an index/landing page worth
                              crawling for more links (optional).
  * ``crawl.max_depth`` / ``crawl.max_pages`` — bounded crawl budget.
  * per brand: ``seeds`` (canonical landing/matrix pages to start from) and an optional
    ``discovered`` file — a plain-text frontier (one URL per line) that Claude tops up from
    in-session WebSearch results. That file is the $0 split: deterministic Python does the
    HTTP discovery + bounded crawl here; Claude runs WebSearch ("{brand} {family} datasheet")
    and appends any new URLs it finds to the frontier file, which this harvester then folds
    in. ``search_terms`` per family are recorded in config purely as the WebSearch script.

Discovery = BFS over seeds + frontier, bounded by depth/pages, staying inside
``allowed_domains``. Every link that matches ``datasheet_patterns`` becomes a fetch target;
every link matching ``follow_patterns`` is crawled for more links. Each datasheet is fetched
through :mod:`lib.local_fetch`; a *blocked* fetch is enqueued in the deferred queue (never
missed, fabricated, or skipped); a hard 404/410 is marked gone. Deterministic and $0.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlsplit

import yaml

from . import local_fetch
from .deferred_queue import DeferredQueue
from .local_fetch import HostThrottle, source_id_from_url

_REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = _REPO_ROOT / "config" / "sources"


# --------------------------------------------------------------------------------------
# Config model.
# --------------------------------------------------------------------------------------

@dataclass
class BrandSources:
    name: str
    seeds: list[str] = field(default_factory=list)
    search_terms: list[str] = field(default_factory=list)
    discovered_file: str = ""

    def frontier(self, root: Path) -> list[str]:
        """Seeds plus any URLs Claude appended to the brand's discovered-frontier file."""
        urls = list(self.seeds)
        if self.discovered_file:
            p = (root / self.discovered_file) if not Path(self.discovered_file).is_absolute() \
                else Path(self.discovered_file)
            if p.exists():
                for line in p.read_text(encoding="utf-8").splitlines():
                    s = line.strip()
                    if s and not s.startswith("#"):
                        urls.append(s)
        # de-dup, preserve order
        seen: set[str] = set()
        out = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out


@dataclass
class HarvestConfig:
    category: str
    allowed_domains: list[str] = field(default_factory=list)
    datasheet_patterns: list[str] = field(default_factory=list)
    follow_patterns: list[str] = field(default_factory=list)
    max_depth: int = 2
    max_pages: int = 300
    brands: dict[str, BrandSources] = field(default_factory=dict)

    @property
    def _datasheet_re(self) -> list[re.Pattern]:
        return [re.compile(p, re.I) for p in self.datasheet_patterns]

    @property
    def _follow_re(self) -> list[re.Pattern]:
        return [re.compile(p, re.I) for p in self.follow_patterns]


def load_sources(category: str, *, root: Path | None = None) -> HarvestConfig:
    """Load ``config/sources/<category>.yaml`` into a :class:`HarvestConfig`."""
    base = (root / "config" / "sources") if root else SOURCES_DIR
    path = base / f"{category}.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    crawl = doc.get("crawl") or {}
    brands: dict[str, BrandSources] = {}
    for name, b in (doc.get("brands") or {}).items():
        b = b or {}
        brands[name] = BrandSources(
            name=name,
            seeds=list(b.get("seeds") or []),
            search_terms=list(b.get("search_terms") or []),
            discovered_file=b.get("discovered") or b.get("discovered_file") or "",
        )
    return HarvestConfig(
        category=doc.get("category", category),
        allowed_domains=list(doc.get("allowed_domains") or []),
        datasheet_patterns=list(doc.get("datasheet_patterns") or []),
        follow_patterns=list(doc.get("follow_patterns") or []),
        max_depth=int(crawl.get("max_depth", 2)),
        max_pages=int(crawl.get("max_pages", 300)),
        brands=brands,
    )


# --------------------------------------------------------------------------------------
# Link extraction + classification (pure, testable offline).
# --------------------------------------------------------------------------------------

def _host_allowed(url: str, allowed: list[str]) -> bool:
    if not allowed:
        return True
    host = urlsplit(url).netloc.lower()
    return any(host == d.lower() or host.endswith("." + d.lower()) for d in allowed)


def extract_links(html: str, base_url: str, allowed_domains: list[str]) -> list[str]:
    """Absolute http(s) links from an HTML page, restricted to ``allowed_domains``.

    Uses bs4 with the stdlib ``html.parser`` (lxml is intentionally not a dependency).
    Falls back to a regex scan if bs4 is unavailable.
    """
    hrefs: list[str] = []
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            hrefs.append(a["href"])
    except Exception:  # noqa: BLE001 — regex fallback keeps discovery working
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I)

    out: list[str] = []
    seen: set[str] = set()
    for h in hrefs:
        if not h or h.startswith(("mailto:", "javascript:", "tel:", "#")):
            continue
        absu = urldefrag(urljoin(base_url, h))[0]
        if not absu.lower().startswith(("http://", "https://")):
            continue
        if not _host_allowed(absu, allowed_domains):
            continue
        if absu not in seen:
            seen.add(absu)
            out.append(absu)
    return out


def classify(url: str, cfg: HarvestConfig) -> str:
    """Return 'datasheet' | 'follow' | 'skip' for a discovered URL."""
    for rx in cfg._datasheet_re:
        if rx.search(url):
            return "datasheet"
    for rx in cfg._follow_re:
        if rx.search(url):
            return "follow"
    return "skip"


# --------------------------------------------------------------------------------------
# Discovery (BFS) + harvest.
# --------------------------------------------------------------------------------------

@dataclass
class HarvestReport:
    category: str
    brand: str
    datasheet_urls: list[str] = field(default_factory=list)
    fetched: list[str] = field(default_factory=list)   # source_ids newly fetched / cached
    blocked: list[str] = field(default_factory=list)   # urls queued for retry
    gone: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    pages_crawled: int = 0

    def summary(self) -> str:
        return (f"[{self.category}/{self.brand}] datasheets={len(self.datasheet_urls)} "
                f"fetched={len(self.fetched)} blocked={len(self.blocked)} "
                f"gone={len(self.gone)} errors={len(self.errors)} "
                f"pages_crawled={self.pages_crawled}")


def discover(
    brand: BrandSources,
    cfg: HarvestConfig,
    *,
    root: Path,
    fetch_fn,
    on_page=None,
) -> tuple[list[str], int]:
    """BFS from the brand's frontier; return (datasheet_urls, pages_crawled).

    ``fetch_fn(url) -> FetchOutcome`` is injectable so this runs fully offline in tests.
    Only pages classified 'follow' (and the initial seeds) are fetched and scraped for
    links; URLs classified 'datasheet' are collected as targets, never crawled into.
    """
    frontier = brand.frontier(root)
    queue: list[tuple[str, int]] = [(u, 0) for u in frontier]
    visited: set[str] = set()
    datasheets: list[str] = []
    ds_seen: set[str] = set()
    pages = 0

    while queue and pages < cfg.max_pages:
        url, depth = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        # A seed/follow page is fetched and scraped. A seed that is itself a datasheet is
        # also recorded as a target.
        if classify(url, cfg) == "datasheet" and url not in ds_seen:
            ds_seen.add(url)
            datasheets.append(url)
            # still fall through: a datasheet seed is not crawled for links

        if depth > cfg.max_depth:
            continue

        outcome = fetch_fn(url)
        pages += 1
        if on_page is not None:
            on_page(url, outcome)
        if not getattr(outcome, "ok", False):
            continue
        try:
            html = outcome.read_text()
        except Exception:  # noqa: BLE001 — non-HTML (e.g. a PDF seed) has no links
            continue

        for link in extract_links(html, url, cfg.allowed_domains):
            kind = classify(link, cfg)
            if kind == "datasheet":
                if link not in ds_seen:
                    ds_seen.add(link)
                    datasheets.append(link)
            elif kind == "follow" and link not in visited and depth + 1 <= cfg.max_depth:
                queue.append((link, depth + 1))

    return datasheets, pages


def _default_fetch(throttle: HostThrottle):
    def _f(url: str):
        return local_fetch.fetch(url, throttle=throttle)
    return _f


def harvest(
    category: str,
    *,
    root: Path | None = None,
    brands: list[str] | None = None,
    fetch_fn=None,
    queue: DeferredQueue | None = None,
    throttle: HostThrottle | None = None,
) -> list[HarvestReport]:
    """Discover + fetch the full datasheet set for each brand in a category.

    ``fetch_fn`` is injectable (offline tests). When omitted, the real local fetcher is
    used with a shared per-host politeness throttle. Blocked datasheets are enqueued in the
    deferred queue; the queue is saved at the end.
    """
    root = root or _REPO_ROOT
    cfg = load_sources(category, root=root)
    throttle = throttle or HostThrottle()
    fetch_fn = fetch_fn or _default_fetch(throttle)
    queue = queue if queue is not None else DeferredQueue()

    selected = brands or list(cfg.brands.keys())
    reports: list[HarvestReport] = []
    for bname in selected:
        bcfg = cfg.brands.get(bname)
        if bcfg is None:
            continue
        rep = HarvestReport(category=cfg.category, brand=bname)
        datasheet_urls, pages = discover(bcfg, cfg, root=root, fetch_fn=fetch_fn)
        rep.datasheet_urls = datasheet_urls
        rep.pages_crawled = pages

        for url in datasheet_urls:
            outcome = fetch_fn(url)
            sid = getattr(outcome, "source_id", source_id_from_url(url))
            if getattr(outcome, "ok", False):
                rep.fetched.append(sid)
                queue.mark_done(url)
            elif getattr(outcome, "gone", False):
                rep.gone.append(url)
                queue.mark_gone(url, status=outcome.http_status, detail=outcome.detail)
            elif getattr(outcome, "blocked", False):
                rep.blocked.append(url)
                queue.enqueue(url, sid, category=cfg.category,
                              status=outcome.http_status, detail=outcome.detail)
            else:
                rep.errors.append(url)
        reports.append(rep)

    queue.save()
    return reports


def retry_due(
    *,
    root: Path | None = None,
    category: str | None = None,
    fetch_fn=None,
    queue: DeferredQueue | None = None,
    throttle: HostThrottle | None = None,
    now=None,
) -> dict[str, int]:
    """Re-fetch every due entry in the deferred queue; advance backoff on still-blocked.

    Returns a small tally {fetched, blocked, gone, errors}. This is the "circle back"
    half of the never-miss contract — run it again next session and the still-blocked
    URLs come due with a longer wait.
    """
    root = root or _REPO_ROOT
    throttle = throttle or HostThrottle()
    fetch_fn = fetch_fn or _default_fetch(throttle)
    queue = queue if queue is not None else DeferredQueue()

    tally = {"fetched": 0, "blocked": 0, "gone": 0, "errors": 0}
    for entry in queue.due(now=now, category=category):
        url = entry["url"]
        outcome = fetch_fn(url)
        if getattr(outcome, "ok", False):
            queue.mark_done(url)
            tally["fetched"] += 1
        elif getattr(outcome, "gone", False):
            queue.mark_gone(url, status=outcome.http_status, detail=outcome.detail, now=now)
            tally["gone"] += 1
        elif getattr(outcome, "blocked", False):
            queue.record_attempt(url, status=outcome.http_status, detail=outcome.detail, now=now)
            tally["blocked"] += 1
        else:
            queue.record_attempt(url, status=outcome.http_status, detail=outcome.detail, now=now)
            tally["errors"] += 1
    queue.save()
    return tally
