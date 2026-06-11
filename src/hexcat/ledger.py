"""SQLite ledger of already-built SKUs, for dedupe and clean re-run/diff."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LEDGER_PATH = "hexcat_ledger.sqlite3"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS built_skus (
    artikelnummer TEXT PRIMARY KEY,
    batch         TEXT NOT NULL,
    category      TEXT NOT NULL,
    built_at      TEXT NOT NULL
);
"""


@dataclass
class LedgerResult:
    new_skus: list[str] = field(default_factory=list)
    duplicate_skus: list[str] = field(default_factory=list)


class Ledger:
    def __init__(self, path: str | Path = DEFAULT_LEDGER_PATH):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute(_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Ledger":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def classify(self, skus: list[str]) -> LedgerResult:
        """Split SKUs into new vs already-built (without recording)."""
        result = LedgerResult()
        cur = self.conn.cursor()
        for sku in skus:
            row = cur.execute(
                "SELECT 1 FROM built_skus WHERE artikelnummer = ?", (sku,)
            ).fetchone()
            (result.duplicate_skus if row else result.new_skus).append(sku)
        return result

    def record(self, skus: list[str], batch: str, category: str) -> None:
        """Record SKUs as built (idempotent: re-running updates batch/time)."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.conn.executemany(
            "INSERT INTO built_skus(artikelnummer, batch, category, built_at) "
            "VALUES(?,?,?,?) "
            "ON CONFLICT(artikelnummer) DO UPDATE SET "
            "batch=excluded.batch, category=excluded.category, built_at=excluded.built_at",
            [(s, batch, category, now) for s in skus],
        )
        self.conn.commit()
