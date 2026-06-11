from __future__ import annotations

from hexcat.ledger import Ledger


def test_classify_and_record_dedupe(tmp_path):
    db = tmp_path / "ledger.sqlite3"
    with Ledger(db) as led:
        res = led.classify(["A", "B"])
        assert sorted(res.new_skus) == ["A", "B"]
        assert res.duplicate_skus == []
        led.record(["A", "B"], "Batch1", "Transceivers")

    with Ledger(db) as led:
        res = led.classify(["A", "B", "C"])
        assert sorted(res.duplicate_skus) == ["A", "B"]
        assert res.new_skus == ["C"]


def test_record_is_idempotent(tmp_path):
    db = tmp_path / "ledger.sqlite3"
    with Ledger(db) as led:
        led.record(["A"], "B1", "Cat")
        led.record(["A"], "B2", "Cat")  # ON CONFLICT update, no error
        assert led.classify(["A"]).duplicate_skus == ["A"]
