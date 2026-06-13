"""HexCat CLI — a ZERO-DOLLAR tool: it never makes a paid LLM API call.

The deterministic core (build/validate/new-intake/new-skeleton) is 100% offline. The
content flow is also $0: `worksheet` turns a facts-only skeleton into a fill-in surface
that Claude Code completes IN-SESSION (no API key, no billing), `draft` merges that back
into a draft intake CSV, and `validate` gates the draft with the SAME content rules the
build uses. Workflow: new-skeleton → fill facts → worksheet → (Claude fills) → draft →
validate → build.
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
from .config import load_rules, load_weights, verify_taxonomy
from .generate import (
    CONTENT_COLUMNS,
    GenerateError,
    merge_fields,
    read_skeleton,
    read_worksheet,
    write_draft,
    write_skeleton_template,
    write_worksheet,
)
from .intake import IntakeError, read_intake
from .models import INTAKE_COLUMNS
from .report import render_report
from .validate import validate_dir, validate_draft

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
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Strict posture (default)."),
):
    """Validate intake, assemble the six files + log, run the gate."""
    rules = load_rules()
    weights = load_weights()
    verify_taxonomy()  # fail loud if config/taxonomy/transceivers.yaml drifts from the contract

    try:
        records = read_intake(input, rules, weights)
    except IntakeError as e:
        err_console.print(f"[bold red]Intake error:[/] {e}")
        raise typer.Exit(code=2)

    to_build = records

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
        quarantined=quarantined,
    )
    raise typer.Exit(code=0 if validation.ok else 1)


@app.command()
def validate(
    dir: Path = typer.Option(None, "--dir", "-d", help="Bundle directory to re-validate."),
    input: Path = typer.Option(
        None, "--input", "-i", help="Draft/intake CSV to content-validate before build."
    ),
):
    """Validate a produced bundle (`--dir`) or a draft intake CSV (`--input`).

    `--input` runs the content gate (word/char budgets, exact <p> counts, banned language,
    Titel-Tag suffix/length, Meta range, authenticity closer, FAQ format + pair count, plus
    advisory soft spec flags) using the SAME predicates `build` enforces — so a draft that
    passes here passes the build gate's content checks.
    """
    if (dir is None) == (input is None):
        err_console.print("[bold red]Pass exactly one of[/] --dir [bold red]or[/] --input.")
        raise typer.Exit(code=2)

    rules = load_rules()
    target = dir if dir is not None else input
    result = validate_draft(rules, input) if input is not None else validate_dir(rules, dir)

    if result.ok:
        console.print(f"[bold green]PASS[/] — 0 violations in {target}")
        if result.warnings:
            console.print(f"[yellow]{len(result.warnings)} warn/soft flag(s):[/]")
            for w in result.warnings:
                console.print(f"  • {w}")
        raise typer.Exit(code=0)
    console.print(f"[bold red]FAIL[/] — {len(result.violations)} violation(s) in {target}:")
    for v in result.violations:
        console.print(f"  • {v}")
    if result.warnings:
        console.print(f"[yellow]{len(result.warnings)} warn/soft flag(s):[/]")
        for w in result.warnings:
            console.print(f"  • {w}")
    raise typer.Exit(code=1)


@app.command()
def sweep(
    dirs: list[Path] = typer.Argument(
        ..., help="Two or more produced bundle directories (one per brand) to cross-check."
    ),
):
    """Cross-brand merged-catalog sweep (§2 G6).

    The per-bundle `validate` gate is blind to clashes BETWEEN brands. This sweep reads every
    given bundle and FAILS on any cross-brand identity collision (Artikelnummer, URL-Pfad,
    GTIN, Titel-Tag) or a body sentence reused across 3+ brands — defects that only appear once
    the brands are merged into one JTL import. The brand label is the directory's trailing
    name component (e.g. `output/stage3_Cisco` -> `Cisco`).
    """
    from .merged_sweep import SweepError, sweep_catalog

    bundles: dict[str, Path] = {}
    for d in dirs:
        name = d.name
        brand = name.split("stage3_", 1)[1] if "stage3_" in name else name
        bundles[brand] = d
    try:
        result = sweep_catalog(bundles)
    except SweepError as e:
        err_console.print(f"[bold red]SWEEP ERROR[/] — {e}")
        raise typer.Exit(code=2)

    head = f"{result.n_brands} brands, {result.n_skus} SKUs"
    if result.ok:
        console.print(f"[bold green]PASS[/] — 0 cross-brand collisions ({head})")
        if result.warnings:
            console.print(f"[yellow]{len(result.warnings)} cross-brand warn(s):[/]")
            for w in result.warnings:
                console.print(f"  • {w}")
        raise typer.Exit(code=0)
    console.print(f"[bold red]FAIL[/] — {len(result.findings)} cross-brand collision(s) ({head}):")
    for f in result.findings:
        console.print(f"  • {f}")
    if result.warnings:
        console.print(f"[yellow]{len(result.warnings)} cross-brand warn(s):[/]")
        for w in result.warnings:
            console.print(f"  • {w}")
    raise typer.Exit(code=1)


@app.command()
def readiness(
    dirs: list[Path] = typer.Argument(
        ..., help="The produced bundle directories (one per brand) to assess for go-live."
    ),
):
    """Import-readiness validator — catalog-level GO / NO-GO (§2 G7).

    Composes every signal into one honest verdict: per-bundle build gate (STRUCTURE), the
    cross-brand merged sweep (CROSS-BRAND), price grounding (PRICES), plus the tracked
    deferred-debt artifacts (GTIN, WEIGHTS, ATTR-GAPS). A BLOCK means "not importable yet";
    a WARN means "importable with an accepted, tracked deferred-grounding debt". Exit 0 only on
    GO (zero blockers). The brand label is the directory's trailing name component.
    """
    from .import_readiness import assess_readiness

    bundles: dict[str, Path] = {}
    for d in dirs:
        brand = d.name.split("stage3_", 1)[1] if "stage3_" in d.name else d.name
        bundles[brand] = d

    report = assess_readiness(bundles, load_rules())
    head = f"{report.n_brands} brands, {report.n_skus} SKUs"
    colour = "bold green" if report.go else "bold red"
    console.print(f"[{colour}]{report.verdict}[/] — import readiness ({head})")
    for c in report.checks:
        style = {"GO": "green", "BLOCK": "bold red", "WARN": "yellow"}[c.status]
        console.print(f"  [{style}]{c.status}[/] {c.name}: {c.detail}")
    raise typer.Exit(code=0 if report.go else 1)


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


@app.command("new-skeleton")
def new_skeleton(
    out: Path = typer.Option(..., "--out", "-o", help="Path to write the facts-only skeleton."),
    profile: str = typer.Option("transceiver", "--profile", help="Skeleton profile."),
):
    """Write a facts-only intake skeleton (content columns blank) for `hexcat worksheet`."""
    if profile != "transceiver":
        err_console.print(f"[red]Unknown profile {profile!r}; only 'transceiver' in Phase 2.[/]")
        raise typer.Exit(code=2)
    write_skeleton_template(out)
    console.print(f"[green]Wrote facts-only skeleton:[/] {out}")
    console.print("[dim]Fill the facts (content columns stay blank), then run "
                  "`hexcat worksheet`. The first row is a commented example.[/]")


@app.command()
def worksheet(
    input: Path = typer.Option(..., "--input", "-i", help="Facts-only skeleton intake CSV."),
    out: Path = typer.Option(..., "--out", "-o", help="Path to write the Markdown content worksheet."),
):
    """Turn a facts-only skeleton into a fill-in worksheet (the $0 content surface).

    Emits the rendered voice guide plus one section per SKU — its verified facts, the
    per-field rules from config, and an empty BEGIN/END block per content field. Claude
    Code fills those blocks IN-SESSION (no API, no cost); then run `hexcat draft`.
    """
    rules = load_rules()
    verify_taxonomy()
    try:
        facts = read_skeleton(input, rules)
    except GenerateError as e:
        err_console.print(f"[bold red]Skeleton error:[/] {e}")
        raise typer.Exit(code=2)

    write_worksheet(out, facts, rules, skeleton_path=input)
    console.print(f"[green]Wrote content worksheet:[/] {out}   [dim]({len(facts)} SKU(s))[/]")
    console.print(
        "[dim]Fill each BEGIN/END content block (Claude Code, in-session), then run "
        "`hexcat draft --worksheet …`.[/]"
    )


@app.command()
def draft(
    worksheet: Path = typer.Option(..., "--worksheet", "-w", help="Authored content worksheet."),
    out: Path = typer.Option(..., "--out", "-o", help="Path to write the draft intake CSV."),
    skeleton: Path = typer.Option(
        None, "--skeleton", "-s",
        help="Facts-only skeleton (default: the one referenced in the worksheet header).",
    ),
):
    """Merge authored worksheet content with skeleton facts into a draft intake CSV.

    Errors (without writing) if any content block is empty, naming the SKU/field. The
    resulting draft is the input for `hexcat validate --input …` and then `hexcat build`.
    """
    rules = load_rules()
    verify_taxonomy()

    try:
        embedded_skeleton, content = read_worksheet(worksheet)
    except GenerateError as e:
        err_console.print(f"[bold red]Worksheet error:[/] {e}")
        raise typer.Exit(code=2)

    skeleton_path = skeleton or (Path(embedded_skeleton) if embedded_skeleton else None)
    if skeleton_path is None:
        err_console.print(
            "[bold red]No skeleton:[/] the worksheet has no HEXCAT:SKELETON header; "
            "pass --skeleton explicitly."
        )
        raise typer.Exit(code=2)

    try:
        facts = read_skeleton(skeleton_path, rules)
    except GenerateError as e:
        err_console.print(f"[bold red]Skeleton error:[/] {e}")
        raise typer.Exit(code=2)

    empty: list[str] = []
    rows: list[dict[str, str]] = []
    for f in facts:
        authored = content.get(f.sku)
        if authored is None:
            err_console.print(f"[bold red]Missing content:[/] worksheet has no blocks for {f.sku}.")
            raise typer.Exit(code=2)
        for col in CONTENT_COLUMNS:
            if not (authored.get(col) or "").strip():
                empty.append(f"{f.sku} / {col}")
        rows.append(merge_fields(f.row, {c: authored.get(c, "") for c in CONTENT_COLUMNS}))

    if empty:
        err_console.print(f"[bold red]Empty content blocks ({len(empty)})[/] — fill them, then re-run:")
        for e in empty:
            err_console.print(f"  • {e}")
        raise typer.Exit(code=2)

    write_draft(out, rows)
    console.print(f"[green]Wrote draft intake:[/] {out}   [dim]({len(rows)} SKU(s))[/]")
    console.print("[dim]Next: `hexcat validate --input …`, fix any violations, then `hexcat build`.[/]")


@app.command("ledger")
def ledger(
    seed: Path = typer.Option(
        Path("Cisco_BUILD_LEDGER.xlsx"), "--seed",
        help="Workbook whose Quellen-Tracker sheet is the source seed list.",
    ),
    source: str = typer.Option(
        "c78-455693", "--source", "-s",
        help="Datasheet source id to process (e.g. c78-455693), or 'all' for every resolvable seed row.",
    ),
    out: Path = typer.Option(
        Path("output/Cisco_Transceivers_Ledger.xlsx"), "--out", "-o",
        help="Path to write the 5-sheet ledger workbook.",
    ),
    spec_path: Path = typer.Option(
        None, "--spec",
        help="Path to the brand mining spec (config/ledger/<brand>_transceivers.yaml). "
             "Default: the Cisco pilot spec.",
    ),
    live: Path = typer.Option(
        None, "--live",
        help="Optional CSV of existing PNs (default: inputs/live_pns_cisco.csv if present). "
             "Enables new-vs-existing tagging + PN-Korrekturen.",
    ),
    skeleton_out: Path = typer.Option(
        None, "--skeleton-out",
        help="Optional: also export Neue Artikel as a Stage-3 skeleton intake CSV (§7 seam).",
    ),
    no_network: bool = typer.Option(
        False, "--no-network", help="Disable Tier-1 fetch (use cache / manual drop-in only)."
    ),
):
    """Stage 1: mine part numbers from a Cisco datasheet into the 5-sheet Excel ledger.

    Fetch (cheapest tier) → mine the ordering table → normalize against the datasheet →
    classify → dedup → write the workbook. ZERO-DOLLAR, deterministic, no model calls.
    """
    from .ledger import (
        export_skeleton,
        fetch_datasheet,
        load_ledger_spec,
        load_live_pns,
        read_sources_from_workbook,
        run_source,
        verify_ledger_spec,
        write_workbook,
    )
    from .ledger.fetch import FetchError
    from .ledger.mine import MineError

    if not seed.exists():
        err_console.print(f"[bold red]Seed workbook not found:[/] {seed} "
                          "(drop Cisco_BUILD_LEDGER.xlsx in the project root).")
        raise typer.Exit(code=2)

    try:
        # fail loud if classification drifts from locked-22 (per-brand spec or Cisco pilot default)
        spec = verify_ledger_spec(str(spec_path) if spec_path else None)
    except Exception as e:  # noqa: BLE001
        err_console.print(f"[bold red]Ledger spec error:[/] {e}")
        raise typer.Exit(code=2)

    sources = read_sources_from_workbook(seed)
    if source != "all":
        sources = [s for s in sources if s.source_id == source.lower()]
    if not sources:
        err_console.print(f"[bold red]No matching source[/] for --source {source!r} in {seed}.")
        raise typer.Exit(code=2)

    live_path = live if live is not None else Path("inputs/live_pns_cisco.csv")
    live_pns = load_live_pns(live_path)

    results = []
    fetched_by_src = []
    for src in sources:
        try:
            fetched = fetch_datasheet(src.url, src.source_id, allow_network=not no_network)
            res = run_source(src, spec, live_pns=live_pns, fetched=fetched)
        except (FetchError, MineError) as e:
            err_console.print(f"[bold red]{src.source_id}:[/] {e}")
            raise typer.Exit(code=1)
        results.append(res)
        fetched_by_src.append(fetched)
        console.print(
            f"[green]{src.source_id}[/] — tier=[cyan]{res.tier}[/], "
            f"mined [bold]{res.mined_count}[/] PNs, "
            f"corrections [bold]{len(res.corrections)}[/], flagged [bold]{len(res.flagged)}[/]"
        )

    # --- Verifier gate: independently re-derive + audit before accepting the ledger ----------
    from .verify import verify_ledger
    from .verify.verifier import verify_source_result, write_audit_report

    audit_dir = out.parent
    any_failed = False
    for res, fetched in zip(results, fetched_by_src):
        try:
            vres = verify_source_result(res, spec, fetched)
        except Exception as e:  # noqa: BLE001 — a verifier crash must not silently pass a ledger
            err_console.print(f"[bold red]Verifier error ({res.source.source_id}):[/] {e}")
            raise typer.Exit(code=1)
        md_path, _ = write_audit_report(vres, audit_dir)
        if vres.passed:
            console.print(f"[green]✓ Audit PASS[/] ({res.source.source_id}) — "
                          f"{vres.authoritative_count} SKUs verified → {md_path.name}")
        else:
            any_failed = True
            failed = ", ".join(c.name for c in vres.failed_checks())
            err_console.print(f"[bold red]✗ Audit FAIL[/] ({res.source.source_id}) — "
                              f"checks {failed} → {md_path.name}")
    if any_failed:
        err_console.print("[bold red]Ledger NOT written:[/] one or more sources failed "
                          "verification. See the Audit_Report_*.md for offending SKUs.")
        raise typer.Exit(code=1)

    out_path = write_workbook(results, out, brand=spec.brand)
    console.print(f"[bold green]Wrote ledger workbook:[/] {out_path}")

    # --- V9 catalog-coverage gate (whole-brand, on the MERGED ledger) ------------------------
    # V1-V8 prove each source was mined honestly; V9 proves the merged catalog spans the brand's
    # known transceiver families. Only a V9 PASS lets the brand reach DONE-VERIFIED (Stage-3).
    from .verify.verifier import verify_catalog_coverage, write_coverage_report
    from .verify.checks import EmittedRow

    merged_emitted = [
        EmittedRow(pn=r.pn, unterkategorie=r.unterkategorie, notiz=r.notiz or "")
        for res in results for r in res.rows
    ]
    cov_res = verify_catalog_coverage(merged_emitted, spec)
    cov_md, _ = write_coverage_report(cov_res, audit_dir)
    v9 = cov_res.checks[0]
    if cov_res.passed:
        console.print(f"[bold green]✓ V9 Catalog coverage PASS[/] — DONE-VERIFIED — "
                      f"{v9.summary} → {cov_md.name}")
    else:
        console.print(f"[bold yellow]⚠ V9 Catalog coverage:[/] {v9.summary} → {cov_md.name}")

    # Coverage summary.
    cov: dict[str, int] = {}
    for res in results:
        for uk, n in res.coverage().items():
            cov[uk] = cov.get(uk, 0) + n
    console.print("[dim]Unterkategorie coverage:[/] " +
                  ", ".join(f"{k}={v}" for k, v in sorted(cov.items())))

    if live_pns is None:
        console.print("[yellow]No live list[/] (inputs/live_pns_cisco.csv absent) — "
                      "mined every PN, PN-Korrekturen empty, no new-vs-existing tag.")

    if skeleton_out is not None:
        sk = export_skeleton(results, skeleton_out, spec)
        console.print(f"[green]Exported Stage-3 skeleton:[/] {sk}   "
                      "[dim](Artikelnummer/Vendor/KategorieEbene3/SourceURLs seeded; specs blank)[/]")


@app.command("stage3-template")
def stage3_template(
    ledger: Path = typer.Option(
        Path("output/Cisco_Transceivers_Ledger.xlsx"), "--ledger", "-l",
        help="DONE-VERIFIED Stage-1 ledger workbook (its 'Neue Artikel' sheet is the spine).",
    ),
    out: Path = typer.Option(
        Path("output/stage3/content.json"), "--out", "-o",
        help="Path to write the content sidecar template.",
    ),
):
    """Emit the $0 in-session content template: one JSON entry per SKU (facts + source URL,
    blank prose, derivable attributes pre-seeded). Claude fills it IN-SESSION, then pass it to
    `hexcat stage3 --content …` to lift the package to PRICES-PENDING / IMPORT-READY."""
    from .stage3 import read_ledger_facts, write_content_template

    if not ledger.exists():
        err_console.print(f"[bold red]Ledger not found:[/] {ledger} (run `hexcat ledger … ` first).")
        raise typer.Exit(code=2)
    facts = read_ledger_facts(ledger)
    if not facts:
        err_console.print(f"[bold red]No SKUs[/] in {ledger} 'Neue Artikel' sheet.")
        raise typer.Exit(code=2)
    out.parent.mkdir(parents=True, exist_ok=True)
    p = write_content_template(facts, out)
    console.print(f"[green]Wrote content template:[/] {p}   [dim]({len(facts)} SKU(s))[/]")
    console.print("[dim]Fill each SKU's prose + verified attributes IN-SESSION ($0), record "
                  "provenance, then run `hexcat stage3 --content …`.[/]")


@app.command("stage3")
def stage3(
    content: Path = typer.Option(
        ..., "--content", "-c",
        help="Authored content sidecar JSON (from `hexcat stage3-template`, filled in-session). "
             "Carries facts + prose + verified attributes; reconciled onto the canonical contract.",
    ),
    brand: str = typer.Option(..., "--brand", "-b", help="Brand / vendor key (e.g. Cisco, MikroTik)."),
    out: Path = typer.Option(
        Path("output/stage3"), "--out", "-o", help="Directory for the v5.0 package files."
    ),
    category: str = typer.Option(
        None, "--category", help="Category slug for Main/Attr/Flag/Prices filenames "
                                 "(default: <Brand>_Transceivers)."
    ),
    batch: str = typer.Option(
        None, "--batch", help="Batch name for Condition/FAQ/Verification filenames (default: <Brand>)."
    ),
):
    """Stage 3: generate the byte-exact v5.0 JTL-Ameise import package from an authored sidecar.

    CONVERGED path — each authored SKU is reconciled onto a canonical SkuRecord and assembled by
    the SAME `assemble_bundle` / `constants` / `writers` the proof slice used, then gated by the
    full-spec `validate_dir`. There is exactly ONE output contract (the divergent package.py
    writer is retired). Prices stay PRICES-PENDING; German prose + verified specs are authored
    IN-SESSION ($0). Non-compliant bundles are quarantined, never emitted.
    """
    from .stage3 import reconcile_content
    from .stage3.reconcile import ReconcileError

    rules = load_rules()
    weights = load_weights()
    verify_taxonomy()

    if not content.exists():
        err_console.print(f"[bold red]Content sidecar not found:[/] {content} "
                          "(run `hexcat stage3-template` first, then fill it in-session).")
        raise typer.Exit(code=2)

    try:
        records = reconcile_content(content, brand=brand, rules=rules, weights=weights)
    except ReconcileError as e:
        err_console.print(f"[bold red]Reconcile error:[/] {e}")
        raise typer.Exit(code=2)

    category = category or f"{brand}_Transceivers"
    batch = batch or brand

    out.mkdir(parents=True, exist_ok=True)
    staging = out / _STAGING
    if staging.exists():
        shutil.rmtree(staging)

    manifest = assemble_bundle(
        records, rules, batch=batch, category=category, out_dir=staging,
    )
    validation = validate_dir(rules, staging)

    quarantined = not validation.ok
    if validation.ok:
        for f in manifest.files:
            dest = out / f.path.name
            if dest.exists():
                dest.unlink()
            shutil.move(str(f.path), str(dest))
            f.path = dest
        manifest.out_dir = out
        shutil.rmtree(staging, ignore_errors=True)
    else:
        quarantine = out / _QUARANTINE
        if quarantine.exists():
            shutil.rmtree(quarantine)
        # Quarantine ONLY the rejected rows, never a full catalog copy. Re-assemble a focused bundle
        # from just the SKUs that drew a violation (reuses the writers, so the quarantine files keep
        # the exact byte contract). File-level violations (BOM/header/delimiter) can't be isolated to
        # rows, so those fall back to moving the whole staging bundle.
        failed_skus = {v.sku for v in validation.violations if v.sku}
        has_file_level = any(not v.sku for v in validation.violations)
        rejected = [r for r in records if r.artikelnummer in failed_skus]
        if rejected and not has_file_level:
            assemble_bundle(rejected, rules, batch=batch, category=category,
                            out_dir=quarantine, build_time=manifest.build_time)
            shutil.rmtree(staging, ignore_errors=True)
        else:
            shutil.move(str(staging), str(quarantine))
        manifest.out_dir = quarantine
        for f in manifest.files:
            f.path = quarantine / f.path.name

    render_report(
        console,
        manifest=manifest,
        records=records,
        validation=validation,
        quarantined=quarantined,
    )
    raise typer.Exit(code=0 if validation.ok else 1)


if __name__ == "__main__":
    app()
