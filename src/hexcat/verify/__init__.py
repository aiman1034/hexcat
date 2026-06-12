"""Deterministic post-mine verifier (Stage 1 self-audit).

Runs AFTER every mine and BEFORE a ledger is accepted as final. It re-derives the
authoritative SKU set from the raw source bytes by an independent method, asserts the V1-V8
invariants against the emitted ledger, and emits Audit_Report_{Brand}.md + a machine-readable
JSON. A ledger that fails any check must NOT be written as final.

$0, pure Python (pdfplumber/regex/openpyxl), no model calls — the same discipline as the
miner it polices.
"""
from __future__ import annotations

from .verifier import (
    VerifyResult,
    verify_catalog_coverage,
    verify_ledger,
    write_coverage_report,
)
from .extract import SourceToken, extract_authoritative

__all__ = [
    "VerifyResult",
    "verify_ledger",
    "verify_catalog_coverage",
    "write_coverage_report",
    "SourceToken",
    "extract_authoritative",
]
