"""Persistent deferred-retry queue (lib/deferred_queue) — offline unit tests.

The contract: a blocked page is never missed. Covers the progressive backoff schedule,
idempotent enqueue, the due/pending queries against a controllable clock, the done/gone
terminal transitions, and JSON persistence across a reload (the cross-session guarantee).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from lib.deferred_queue import BACKOFF_CAP_MINUTES, DeferredQueue, backoff_for

T0 = datetime(2026, 6, 13, 10, 0, 0, tzinfo=timezone.utc)


def test_backoff_schedule_progresses_then_caps():
    assert backoff_for(1) == timedelta(minutes=2)
    assert backoff_for(2) == timedelta(minutes=5)
    assert backoff_for(3) == timedelta(minutes=15)
    # far beyond the table -> 24h ceiling
    assert backoff_for(99) == timedelta(minutes=BACKOFF_CAP_MINUTES)


def test_enqueue_is_idempotent_and_advances_backoff(tmp_path):
    q = DeferredQueue(tmp_path / "dq.json")
    q.enqueue("https://h/x", "x", category="transceivers", status=429, detail="429", now=T0)
    q.enqueue("https://h/x", "x", category="transceivers", status=403, detail="403", now=T0)
    assert len(q) == 1
    e = q.get("https://h/x")
    assert e["attempts"] == 2 and e["category"] == "transceivers"
    # retry_after pushed out by the 2nd-attempt backoff (5m)
    assert e["retry_after"] == "2026-06-13T10:05:00Z"


def test_due_respects_retry_after_clock(tmp_path):
    q = DeferredQueue(tmp_path / "dq.json")
    q.enqueue("https://h/x", "x", now=T0)  # retry_after = T0 + 2m
    assert q.due(now=T0) == []                       # not yet
    assert q.due(now=T0 + timedelta(minutes=2)) != []  # now due
    assert [e["url"] for e in q.due(now=T0 + timedelta(hours=1))] == ["https://h/x"]


def test_due_filters_by_category(tmp_path):
    q = DeferredQueue(tmp_path / "dq.json")
    q.enqueue("https://h/a", "a", category="transceivers", now=T0)
    q.enqueue("https://h/b", "b", category="switches", now=T0)
    later = T0 + timedelta(hours=1)
    assert [e["url"] for e in q.due(now=later, category="switches")] == ["https://h/b"]


def test_mark_done_and_gone_remove_from_due(tmp_path):
    q = DeferredQueue(tmp_path / "dq.json")
    q.enqueue("https://h/a", "a", now=T0)
    q.enqueue("https://h/b", "b", now=T0)
    q.mark_done("https://h/a", now=T0)
    q.mark_gone("https://h/b", status=410, now=T0)
    later = T0 + timedelta(hours=1)
    assert q.due(now=later) == []
    assert q.get("https://h/a")["state"] == "done"
    assert q.get("https://h/b")["state"] == "gone" and q.get("https://h/b")["last_status"] == 410


def test_mark_gone_records_even_unknown_url(tmp_path):
    q = DeferredQueue(tmp_path / "dq.json")
    q.mark_gone("https://h/never-seen", status=404, now=T0)
    assert q.get("https://h/never-seen")["state"] == "gone"


def test_persistence_round_trip(tmp_path):
    path = tmp_path / "dq.json"
    q = DeferredQueue(path)
    q.enqueue("https://h/a", "a", category="transceivers", status=503, detail="503", now=T0)
    q.save()
    # a brand-new instance (next session) sees the same pending work
    q2 = DeferredQueue(path)
    assert len(q2) == 1
    e = q2.get("https://h/a")
    assert e["state"] == "pending" and e["attempts"] == 1 and e["category"] == "transceivers"
    assert q2.counts()["pending"] == 1


def test_record_attempt_unknown_url_is_noop(tmp_path):
    q = DeferredQueue(tmp_path / "dq.json")
    assert q.record_attempt("https://h/ghost") is None
