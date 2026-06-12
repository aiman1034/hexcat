"""Persistent, cross-session deferred-retry queue for blocked datasheet fetches.

The hard rule: a page that a manufacturer publishes is NEVER missed, fabricated, or
silently skipped. When :mod:`lib.local_fetch` reports a URL *blocked*, its exact address
is recorded here with a progressive backoff and circled back to — minutes, then tens of
minutes, then hours, then the next session — until it yields. The only terminal state is a
hard 404/410, recorded as ``gone`` (confirmed by the manufacturer, not assumed).

The store is a single tracked JSON file (``datasheets/deferred_queue.json``) so it survives
across sessions. One entry per URL:

    {
      "url": "...",
      "source_id": "...",
      "category": "transceivers",       # which harvest produced it (free-form tag)
      "state": "pending" | "done" | "gone",
      "attempts": 3,
      "first_seen": "2026-06-13T10:00:00Z",
      "last_attempt": "2026-06-13T11:30:00Z",
      "retry_after": "2026-06-13T13:30:00Z",   # do not retry before this (UTC)
      "last_status": 429,
      "last_detail": "tier1-minimal HTTP 429",
      "history": ["...", ...]                    # short audit trail, capped
    }

Backoff schedule (attempt -> wait before the next retry): 2m, 5m, 15m, 45m, 2h, 6h, 24h,
then capped at 24h. ``due`` returns the entries whose ``retry_after`` has passed; the
harvester re-fetches each, then calls ``mark_done`` / ``mark_gone`` / ``record_attempt``.
Deterministic and $0 — just JSON on disk and wall-clock timestamps.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = _REPO_ROOT / "datasheets" / "deferred_queue.json"

# attempt count (after this many failures) -> minutes to wait before the next retry.
BACKOFF_MINUTES = [2, 5, 15, 45, 120, 360, 1440]
BACKOFF_CAP_MINUTES = 1440  # 24h ceiling
_HISTORY_CAP = 20


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def backoff_for(attempts: int) -> timedelta:
    """Wait before the next retry given how many attempts have already failed (>=1)."""
    idx = max(0, attempts - 1)
    minutes = BACKOFF_MINUTES[idx] if idx < len(BACKOFF_MINUTES) else BACKOFF_CAP_MINUTES
    return timedelta(minutes=minutes)


class DeferredQueue:
    """A JSON-backed, URL-keyed retry queue. Load, mutate, ``save`` to persist."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else DEFAULT_PATH
        self._entries: dict[str, dict] = {}
        self.load()

    # ---- persistence ------------------------------------------------------------------

    def load(self) -> None:
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8") or "{}")
            items = raw.get("entries", raw) if isinstance(raw, dict) else raw
            if isinstance(items, dict):
                self._entries = dict(items)
            else:  # list form
                self._entries = {e["url"]: e for e in items}
        else:
            self._entries = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        ordered = sorted(self._entries.values(), key=lambda e: e.get("first_seen", ""))
        doc = {
            "schema": 1,
            "updated": _iso(_now()),
            "counts": self.counts(),
            "entries": {e["url"]: e for e in ordered},
        }
        self.path.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # ---- mutation ---------------------------------------------------------------------

    def enqueue(
        self,
        url: str,
        source_id: str,
        *,
        category: str = "",
        status: int = 0,
        detail: str = "",
        now: datetime | None = None,
    ) -> dict:
        """Add a freshly-blocked URL, or record another failed attempt on an existing one.

        Either way the backoff advances and ``retry_after`` is pushed out. Idempotent on
        URL: the same blocked page seen twice does not create a duplicate entry.
        """
        now = now or _now()
        e = self._entries.get(url)
        if e is None:
            e = {
                "url": url,
                "source_id": source_id,
                "category": category,
                "state": "pending",
                "attempts": 0,
                "first_seen": _iso(now),
                "last_attempt": None,
                "retry_after": None,
                "last_status": 0,
                "last_detail": "",
                "history": [],
            }
            self._entries[url] = e
        if category and not e.get("category"):
            e["category"] = category
        return self._record(e, status=status, detail=detail, state="pending", now=now)

    def record_attempt(
        self, url: str, *, status: int = 0, detail: str = "", now: datetime | None = None
    ) -> dict | None:
        """A due retry failed again — advance the backoff. No-op if the URL is unknown."""
        e = self._entries.get(url)
        if e is None:
            return None
        return self._record(e, status=status, detail=detail, state="pending", now=now or _now())

    def mark_done(self, url: str, *, detail: str = "fetched", now: datetime | None = None) -> None:
        e = self._entries.get(url)
        if e is None:
            return
        now = now or _now()
        e["state"] = "done"
        e["last_attempt"] = _iso(now)
        e["retry_after"] = None
        if detail:
            e["last_detail"] = detail
        self._push_history(e, f"{_iso(now)} done: {detail}")

    def mark_gone(self, url: str, *, status: int = 404, detail: str = "", now: datetime | None = None) -> None:
        """Terminal: the manufacturer confirms the page is gone (hard 404/410)."""
        e = self._entries.get(url)
        if e is None:
            # Record it anyway so the audit trail shows we observed the 404/410.
            e = {
                "url": url, "source_id": "", "category": "", "state": "gone",
                "attempts": 0, "first_seen": _iso(now or _now()),
                "last_attempt": None, "retry_after": None,
                "last_status": status, "last_detail": "", "history": [],
            }
            self._entries[url] = e
        now = now or _now()
        e["state"] = "gone"
        e["last_status"] = status
        e["last_attempt"] = _iso(now)
        e["retry_after"] = None
        if detail:
            e["last_detail"] = detail
        self._push_history(e, f"{_iso(now)} gone: HTTP {status} {detail}".rstrip())

    def _record(self, e: dict, *, status: int, detail: str, state: str, now: datetime) -> dict:
        e["attempts"] = int(e.get("attempts", 0)) + 1
        e["state"] = state
        e["last_attempt"] = _iso(now)
        e["last_status"] = status
        e["last_detail"] = detail
        e["retry_after"] = _iso(now + backoff_for(e["attempts"]))
        self._push_history(e, f"{_iso(now)} attempt#{e['attempts']} HTTP {status} {detail}".rstrip())
        return e

    @staticmethod
    def _push_history(e: dict, line: str) -> None:
        hist = e.setdefault("history", [])
        hist.append(line)
        if len(hist) > _HISTORY_CAP:
            del hist[: len(hist) - _HISTORY_CAP]

    # ---- queries ----------------------------------------------------------------------

    def due(self, now: datetime | None = None, *, category: str | None = None) -> list[dict]:
        """Pending entries whose ``retry_after`` has passed (or was never set), oldest first."""
        now = now or _now()
        out = []
        for e in self._entries.values():
            if e.get("state") != "pending":
                continue
            if category is not None and e.get("category") != category:
                continue
            ra = _parse(e.get("retry_after"))
            if ra is None or ra <= now:
                out.append(e)
        out.sort(key=lambda e: (e.get("retry_after") or "", e.get("first_seen", "")))
        return out

    def pending(self, *, category: str | None = None) -> list[dict]:
        return [
            e for e in self._entries.values()
            if e.get("state") == "pending" and (category is None or e.get("category") == category)
        ]

    def all(self) -> list[dict]:
        return list(self._entries.values())

    def get(self, url: str) -> dict | None:
        return self._entries.get(url)

    def counts(self) -> dict[str, int]:
        c = {"pending": 0, "done": 0, "gone": 0}
        for e in self._entries.values():
            c[e.get("state", "pending")] = c.get(e.get("state", "pending"), 0) + 1
        return c

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, url: str) -> bool:
        return url in self._entries
