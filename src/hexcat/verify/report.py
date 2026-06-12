"""Render the human-readable Audit_Report_{Brand}.md from a VerifyResult."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .verifier import VerifyResult


def render_markdown(result: "VerifyResult") -> str:
    status = "PASS ✅" if result.passed else "FAIL ❌"
    lines: list[str] = [
        f"# Audit Report — {result.brand}",
        "",
        f"- **Result:** {status}",
        f"- **Run date:** {result.run_date}",
        f"- **Authoritative distinct SKUs (2nd method):** {result.authoritative_count}",
        f"- **Emitted distinct SKUs (ledger):** {result.emitted_count}",
        "",
        "## Checks",
        "",
        "| Check | Title | Result | Offenders |",
        "| --- | --- | --- | --- |",
    ]
    for c in result.checks:
        mark = "PASS" if c.passed else "FAIL"
        lines.append(f"| {c.name} | {c.title} | {mark} | {len(c.offenders)} |")
    lines.append("")

    for c in result.checks:
        mark = "PASS ✅" if c.passed else "FAIL ❌"
        lines.append(f"### {c.name} — {c.title}: {mark}")
        lines.append("")
        lines.append(c.summary)
        lines.append("")
        if c.offenders:
            lines.append("Offending SKUs:")
            for pn in c.offenders:
                why = c.details.get(pn)
                lines.append(f"- `{pn}`" + (f" — {why}" if why else ""))
            lines.append("")
        # Surface structured details that are not keyed by a single offending SKU.
        for k, v in c.details.items():
            if k in c.offenders:
                continue
            if isinstance(v, list) and v:
                lines.append(f"- _{k}_: {', '.join(map(str, v))}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
