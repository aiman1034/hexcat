"""Rich supervisor report (Workflow D): concise pass/fail, no prose dumps."""
from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table as RichTable

from .assemble import BundleManifest
from .models import SkuRecord
from .validate import ValidationResult


def render_report(
    console: Console,
    *,
    manifest: BundleManifest,
    records: list[SkuRecord],
    validation: ValidationResult,
    quarantined: bool,
) -> None:
    status = "[bold green]PASS[/]" if validation.ok else "[bold red]FAIL[/]"
    head = (
        f"Batch: [bold]{manifest.batch}[/]   Category: [bold]{manifest.category}[/]   "
        f"SKUs: [bold]{len(manifest.skus)}[/]   Gate: {status}"
    )
    console.print(Panel(head, title="HexCat — Supervisor Report", expand=False))

    # Per-file row counts
    ft = RichTable(title="Output files", show_lines=False)
    ft.add_column("Role")
    ft.add_column("File")
    ft.add_column("Rows", justify="right")
    for f in manifest.files:
        ft.add_row(f.role, f.path.name, str(f.rows))
    console.print(ft)

    # Validation
    if validation.ok:
        console.print("[green]Validation gate: PASS — 0 violations.[/]")
    else:
        vt = RichTable(title=f"Validation FAILURES ({len(validation.violations)})")
        vt.add_column("File")
        vt.add_column("SKU")
        vt.add_column("Field")
        vt.add_column("Problem")
        vt.add_column("Expected")
        vt.add_column("Got")
        for v in validation.violations:
            vt.add_row(v.file, v.sku or "—", v.field or "—", v.message, v.expected, v.got)
        console.print(vt)

    # Warnings (puffery flags)
    if validation.warnings:
        wt = RichTable(title=f"Warn-list flags ({len(validation.warnings)}) — review, not blocking")
        wt.add_column("File")
        wt.add_column("SKU")
        wt.add_column("Field")
        wt.add_column("Note")
        for w in validation.warnings:
            wt.add_row(w.file, w.sku or "—", w.field, w.message)
        console.print(wt)

    # Placeholder weights
    ph = [r.artikelnummer for r in records if r.weights_are_placeholder]
    if ph:
        console.print(
            f"[yellow]Placeholder weights still to confirm: {len(ph)} SKU(s)[/] "
            f"-> {', '.join(ph)}  (edit config/weights.yaml)"
        )
    else:
        console.print("[green]All emitted weights are operator-provided (no placeholders).[/]")

    # Skipped (empty) attributes per SKU
    skipped = {r.artikelnummer: r.skipped_attributes for r in records if r.skipped_attributes}
    if skipped:
        st = RichTable(title="Skipped empty attributes (not emitted)")
        st.add_column("SKU")
        st.add_column("Attributes left blank")
        for sku, attrs in skipped.items():
            st.add_row(sku, ", ".join(attrs))
        console.print(st)

    # v5.1 confirmation note (output format built to the v5.0 baseline).
    console.print(
        "[dim]Note: output built to the v5.0 baseline — v5.1 confirmation pending "
        "(format is config-driven; the delta is a config edit, not a code change).[/]"
    )

    # Output paths
    where = manifest.out_dir
    if quarantined:
        console.print(
            f"[bold red]Gate failed — bundle quarantined at:[/] {where}\n"
            f"[red]No compliant files were written to the output directory.[/]"
        )
    else:
        console.print(f"[bold green]Output written to:[/] {where}")
