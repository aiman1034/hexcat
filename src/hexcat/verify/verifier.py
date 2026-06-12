"""Orchestrate the V1-V8 checks for one ledger and render the audit artifacts.

A ledger is ACCEPTED only when every check passes. The caller (engine/CLI) must refuse to
write a non-passing ledger as final — `VerifyResult.passed` is that gate.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import checks as C
from .checks import CheckResult, EmittedRow
from .extract import (
    SourceToken,
    extract_authoritative,
    extract_authoritative_html,
    extract_authoritative_section,
    raw_source_text,
    ws_normalize,
)
from .report import render_markdown
from ..ledger.spec import LedgerSpec


@dataclass
class VerifyResult:
    brand: str
    passed: bool
    checks: list[CheckResult]
    authoritative_count: int
    emitted_count: int
    run_date: str
    tokens: list[SourceToken] = field(default_factory=list)

    def failed_checks(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.passed]

    def to_json(self) -> dict:
        return {
            "brand": self.brand,
            "run_date": self.run_date,
            "passed": self.passed,
            "authoritative_count": self.authoritative_count,
            "emitted_count": self.emitted_count,
            "checks": [
                {
                    "name": c.name, "title": c.title, "passed": c.passed,
                    "summary": c.summary, "offenders": c.offenders, "details": c.details,
                }
                for c in self.checks
            ],
        }


def verify_ledger(
    emitted: list[EmittedRow],
    spec: LedgerSpec,
    *,
    brand: str | None = None,
    pdf_bytes: bytes | None = None,
    html: str | None = None,
    run_date: str | None = None,
) -> VerifyResult:
    """Independently re-derive the authoritative SKU set from the raw source and run V1-V8."""
    brand = brand or spec.brand
    run_date = run_date or date.today().isoformat()

    if pdf_bytes is not None:
        pdf_cfg = spec.mine.pdf
        if pdf_cfg is None:
            raise ValueError(f"{brand}: PDF bytes supplied but spec.mine.pdf is unset.")
        if pdf_cfg.mode == "section":
            tokens = extract_authoritative_section(pdf_bytes, pdf_cfg)
        else:
            tokens = extract_authoritative(pdf_bytes, pdf_cfg)
        raw_text = raw_source_text(pdf_bytes)
    elif html is not None:
        tokens = extract_authoritative_html(html, spec)
        from bs4 import BeautifulSoup
        raw_text = ws_normalize(BeautifulSoup(html, "html.parser").get_text(" "))
    else:
        raise ValueError("verify_ledger needs either pdf_bytes or html.")

    # Symmetric flag-don't-emit: drop the same non-transceiver tokens the engine excludes, so the
    # independently re-derived authoritative set still equals the emitted set (V7/V8 stay honest).
    tokens = [t for t in tokens if not spec.is_excluded(t.pn, t.description)]

    source_skus = sorted({t.pn for t in tokens})

    v1 = C.v1_verbatim(emitted, raw_text, source_skus)
    v2 = C.v2_provenance(emitted, tokens)
    v3 = C.v3_no_silent_collision(emitted, tokens, spec)
    v4 = C.v4_separator_integrity(emitted, tokens)
    v5 = C.v5_classification(emitted, tokens)
    v6 = C.v6_switch_exclusion(emitted, tokens)
    v7 = C.v7_completeness(emitted, tokens, v2, v4)
    v8 = C.v8_count_honesty(emitted, tokens)
    checks = [v1, v2, v3, v4, v5, v6, v7, v8]

    authoritative_count = len({t.pn for t in tokens
                               if t.locus in ("sku_column", "pn_column", "flat", "callout")})
    return VerifyResult(
        brand=brand,
        passed=all(c.passed for c in checks),
        checks=checks,
        authoritative_count=authoritative_count,
        emitted_count=len({r.pn for r in emitted}),
        run_date=run_date,
        tokens=tokens,
    )


def verify_source_result(res, spec: LedgerSpec, fetched, *,
                         run_date: str | None = None) -> VerifyResult:
    """Bridge an engine SourceResult + its FetchResult to the V1-V8 verifier.

    This is the pipeline seam: the engine mines -> the verifier independently re-derives and
    audits -> the caller refuses to write a ledger whose VerifyResult.passed is False.
    """
    emitted = [EmittedRow(pn=r.pn, unterkategorie=r.unterkategorie, notiz=r.notiz or "")
               for r in res.rows]
    if fetched.content_type == "html":
        return verify_ledger(emitted, spec, brand=spec.brand,
                             html=fetched.read_text(), run_date=run_date)
    return verify_ledger(emitted, spec, brand=spec.brand,
                         pdf_bytes=fetched.read_bytes(), run_date=run_date)


def write_audit_report(result: VerifyResult, out_dir: str | Path) -> tuple[Path, Path]:
    """Write Audit_Report_{Brand}.md + Audit_Report_{Brand}.json. Returns both paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    safe = result.brand.replace("/", "_").replace(" ", "_")
    md_path = out / f"Audit_Report_{safe}.md"
    json_path = out / f"Audit_Report_{safe}.json"
    md_path.write_text(render_markdown(result), encoding="utf-8")
    json_path.write_text(json.dumps(result.to_json(), indent=2, ensure_ascii=False),
                         encoding="utf-8")
    return md_path, json_path
