"""HexCat CLI: build, validate, new-intake (Phase 1) and generate (Phase 2).

Phase 1 commands (build/validate/new-intake) are 100% deterministic and offline — no
network, no model calls. The Phase 2 `generate` command is the ONLY one that calls the
Anthropic API; it writes a draft intake CSV for human review before `build`.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console

# Ensure UTF-8 console output on legacy Windows code pages (cp1252) so German
# umlauts and report symbols render instead of crashing the encoder.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

from . import constants as C
from .assemble import assemble_bundle
from .config import load_rules, load_weights
from .generate import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    GenerateError,
    Generator,
    make_anthropic_completer,
    merge_fields,
    read_skeleton,
    write_draft,
)
from .intake import IntakeError, read_intake
from .ledger import Ledger
from .models import INTAKE_COLUMNS
from .report import render_report
from .validate import validate_dir

app = typer.Typer(
    add_completion=False,
    help="HexCat — JTL-Ameise-ready CSV bundle generator for the Hexwaren catalog.",
)
console = Console()
err_console = Console(stderr=True)

_STAGING = ".staging"
_QUARANTINE = "_quarantine"


@app.command()
def build(
    input: Path = typer.Option(..., "--input", "-i", help="Wide intake CSV."),
    batch: str = typer.Option(..., "--batch", "-b", help="Batch name."),
    category: str = typer.Option(..., "--category", "-c", help="Category slug/name for filenames."),
    out: Path = typer.Option(..., "--out", "-o", help="Output directory."),
    ledger_path: Path = typer.Option("hexcat_ledger.sqlite3", "--ledger", help="SQLite ledger path."),
    rebuild: bool = typer.Option(False, "--rebuild", help="Re-emit SKUs already in the ledger."),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Strict posture (default)."),
):
    """Validate intake, assemble the six files + log, run the gate, update the ledger."""
    rules = load_rules()
    weights = load_weights()

    try:
        records = read_intake(input, rules, weights)
    except IntakeError as e:
        err_console.print(f"[bold red]Intake error:[/] {e}")
        raise typer.Exit(code=2)

    # Ledger dedupe.
    led = Ledger(ledger_path)
    ledger_result = led.classify([r.artikelnummer for r in records])
    if not rebuild:
        new_set = set(ledger_result.new_skus)
        to_build = [r for r in records if r.artikelnummer in new_set]
    else:
        to_build = records

    if not to_build:
        console.print(
            "[yellow]All SKUs are already in the ledger; nothing to build.[/] "
            "Use --rebuild to re-emit."
        )
        led.close()
        raise typer.Exit(code=0)

    out.mkdir(parents=True, exist_ok=True)
    staging = out / _STAGING
    if staging.exists():
        shutil.rmtree(staging)

    manifest = assemble_bundle(
        to_build, rules, batch=batch, category=category, out_dir=staging,
    )
    validation = validate_dir(rules, staging)

    quarantined = not validation.ok
    if validation.ok:
        # Promote staged files to the output directory.
        for f in manifest.files:
            dest = out / f.path.name
            if dest.exists():
                dest.unlink()
            shutil.move(str(f.path), str(dest))
            f.path = dest
        manifest.out_dir = out
        shutil.rmtree(staging, ignore_errors=True)
        led.record([r.artikelnummer for r in to_build], batch, category)
    else:
        # Never emit non-compliant files into the output dir; quarantine them.
        quarantine = out / _QUARANTINE
        if quarantine.exists():
            shutil.rmtree(quarantine)
        shutil.move(str(staging), str(quarantine))
        manifest.out_dir = quarantine
        for f in manifest.files:
            f.path = quarantine / f.path.name

    render_report(
        console,
        manifest=manifest,
        records=to_build,
        validation=validation,
        ledger=ledger_result,
        quarantined=quarantined,
    )
    led.close()
    raise typer.Exit(code=0 if validation.ok else 1)


@app.command()
def validate(
    dir: Path = typer.Option(..., "--dir", "-d", help="Bundle directory to re-validate."),
):
    """Re-run the validation gate against an already-produced bundle."""
    rules = load_rules()
    result = validate_dir(rules, dir)
    if result.ok:
        console.print(f"[bold green]PASS[/] — 0 violations in {dir}")
        if result.warnings:
            console.print(f"[yellow]{len(result.warnings)} warn-list flag(s):[/]")
            for w in result.warnings:
                console.print(f"  • {w}")
        raise typer.Exit(code=0)
    console.print(f"[bold red]FAIL[/] — {len(result.violations)} violation(s) in {dir}:")
    for v in result.violations:
        console.print(f"  • {v}")
    raise typer.Exit(code=1)


@app.command("new-intake")
def new_intake(
    out: Path = typer.Option(..., "--out", "-o", help="Path to write the blank template."),
    profile: str = typer.Option("transceiver", "--profile", help="Intake profile."),
):
    """Write a blank intake template with headers + one commented example row."""
    if profile != "transceiver":
        err_console.print(f"[red]Unknown profile {profile!r}; only 'transceiver' in Phase 1.[/]")
        raise typer.Exit(code=2)

    header = ",".join(INTAKE_COLUMNS)
    example = {
        "Artikelnummer": "# SFP-10G-SR",
        "Vendor": "Cisco",
        "KategorieEbene3": "SFP+",
        "Artikelname": "Cisco SFP-10G-SR 10G SFP+ Modul",
        "Kurzbeschreibung": "<p>…40-80 words, exactly 2 paragraphs…</p><p>…</p>",
        "Beschreibung": "<p>…</p><p>…</p><p>… Originaler Cisco-Transceiver …</p>",
        "TitelTag": "Cisco SFP-10G-SR 10G SR Modul | Hexwaren",
        "MetaDescription": "140-200 chars meta description …",
        "NettoVK": "120.50",
        "Artikelgewicht": "",
        "Versandgewicht": "",
        "Formfaktor": "SFP+",
        "Geschwindigkeit": "10 Gigabit",
        "TransceiverTyp": "SR",
        "Faseranzahl": "2",
        "Fasertyp": "Multimode",
        "Anschlusstyp": "LC Duplex",
        "Laenge": "",
        "Kabeltyp": "",
        "Wellenlaenge": "850 nm",
        "Anwendung": "Rechenzentrum",
        "Reichweite": "300 m",
        "DOMUnterstuetzung": "Ja",
        "Betriebstemperatur": "0 bis 70 Grad C",
        "Standard": "IEEE 802.3ae",
        "Condition": "new",
        "FAQ": "Frage 1?||Antwort 1.##Frage 2?||Antwort 2.##Frage 3?||Antwort 3.",
        "SourceURLs": "",
    }
    example_row = ",".join('"' + example.get(c, "").replace('"', '""') + '"' for c in INTAKE_COLUMNS)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "﻿" + header + "\r\n" + example_row + "\r\n",
        encoding="utf-8", newline="",
    )
    console.print(f"[green]Wrote intake template:[/] {out}")
    console.print("[dim]The first row is a commented example (Artikelnummer starts with '#') "
                  "and is skipped on build. Fill real rows below it.[/]")


@app.command()
def generate(
    input: Path = typer.Option(..., "--input", "-i", help="Facts-only skeleton intake CSV."),
    out: Path = typer.Option(..., "--out", "-o", help="Path to write the filled draft intake CSV."),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Anthropic model id."),
    max_retries: int = typer.Option(
        DEFAULT_MAX_RETRIES, "--max-retries", help="Self-check retries per SKU before flagging."
    ),
    limit: int = typer.Option(0, "--limit", help="Only generate the first N SKUs (0 = all)."),
    only: str = typer.Option("", "--only", help="Comma-separated SKUs to generate (subset)."),
):
    """Phase 2: draft the German content fields per SKU via the Anthropic API.

    Reads a facts-only skeleton intake, self-checks each draft against the build gate's
    own rules (retrying with feedback), and writes a draft intake CSV for human review.
    Run `hexcat build` on the reviewed draft. This command makes network/model calls.
    """
    rules = load_rules()

    try:
        facts = read_skeleton(input, rules)
    except GenerateError as e:
        err_console.print(f"[bold red]Skeleton error:[/] {e}")
        raise typer.Exit(code=2)

    if only.strip():
        wanted = {s.strip() for s in only.split(",") if s.strip()}
        facts = [f for f in facts if f.sku in wanted]
    if limit > 0:
        facts = facts[:limit]
    if not facts:
        err_console.print("[bold red]No SKUs selected to generate.[/]")
        raise typer.Exit(code=2)

    try:
        completer = make_anthropic_completer(model)
    except GenerateError as e:
        err_console.print(f"[bold red]Cannot start generation:[/] {e}")
        raise typer.Exit(code=2)

    gen = Generator(rules, completer=completer, model=model, max_retries=max_retries)

    console.print(
        f"[bold]Generating[/] {len(facts)} SKU(s) with [cyan]{model}[/] "
        f"(max {max_retries} attempts each)…"
    )
    results = []
    out_rows = []
    for f in facts:
        res = gen.generate_one(f)
        results.append(res)
        out_rows.append(merge_fields(f.row, res.fields))
        if res.ok:
            console.print(
                f"  [green]OK[/]      {res.sku}  "
                f"(attempt {res.attempts}; kurz {res.kurz_words}w, "
                f"besch {res.besch_words}w, {res.faq_pairs} FAQ)"
            )
        else:
            console.print(f"  [red]FLAGGED[/] {res.sku}  ({len(res.issues)} unmet check(s))")
            for issue in res.issues:
                console.print(f"            [dim]- {issue}[/]")

    write_draft(out, out_rows)

    ok_n = sum(1 for r in results if r.ok)
    flagged_n = len(results) - ok_n
    console.print()
    console.print(f"[bold]Draft written:[/] {out}")
    console.print(f"  passed self-check: [green]{ok_n}[/]   flagged: "
                  f"{'[red]' + str(flagged_n) + '[/]' if flagged_n else '0'}")
    if flagged_n:
        console.print(
            "[yellow]Review the flagged SKUs in the draft before running "
            "`hexcat build` — the gate will quarantine any that still fail.[/]"
        )
    else:
        console.print("[dim]Review the draft, then run `hexcat build` on it.[/]")
    raise typer.Exit(code=0 if flagged_n == 0 else 1)


if __name__ == "__main__":
    app()
