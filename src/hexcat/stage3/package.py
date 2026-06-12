"""Stage-3 template flow — read the Stage-1 ledger and emit the $0 in-session content sidecar.

The divergent v5.0 *writer* that once lived here (build_package/write_package/
compose_beschreibung + its own MAIN/ATTR column orders) is RETIRED. Stage-3 packages are now
assembled by the canonical `assemble.assemble_bundle` via `reconcile.reconcile_content`, so
there is exactly ONE output contract (see stage3/reconcile.py).

What remains here is only the authoring bridge:
  * `read_ledger_facts` — read the DONE-VERIFIED Stage-1 ledger workbook into `SkuFacts`
    (the deterministic spine: PN, Unterkategorie -> Kategorie Ebene 3, datasheet URL).
  * `write_content_template` — emit a JSON sidecar (one entry per SKU, prose fields blank,
    the two derivable attributes pre-seeded) for Claude to FILL in-session ($0, never an API).
    `reconcile_content` later folds that authored sidecar onto the canonical pipeline.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# The only condition value the scaffold seeds (a commerce flag, becomes the Condition file).
ZUSTAND_NEU = "Neu, versiegelt"


@dataclass
class SkuFacts:
    """Ledger-derived facts for one SKU (the deterministic spine)."""
    pn: str
    unterkategorie: str                 # locked-22 token -> Kategorie Ebene 3
    quell_url: str = ""
    verifiziert_am: str = ""
    notiz: str = ""


def _derive_attributes(facts: SkuFacts) -> list[tuple[str, str]]:
    """The only spec attributes derivable WITHOUT the datasheet: form factor + condition.
    Everything else (speed, wavelength, reach, FEC, temp, DOM) is authored + verified
    in-session, so the scaffold seeds just these two and leaves the rest content-pending."""
    return [("Formfaktor", facts.unterkategorie), ("Zustand", ZUSTAND_NEU)]


def read_ledger_facts(xlsx_path: str | Path) -> list[SkuFacts]:
    """Read the Stage-1 ledger workbook's 'Neue Artikel' sheet into SkuFacts (the spine).

    Columns (verbatim, see workbook.py): Artikelnummer (Part Number) | Hauptkategorie |
    Unterkategorie | Quelle (... Datasheet) | Quell-URL | Verifiziert am | Notiz.
    """
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb["Neue Artikel"]
    facts: list[SkuFacts] = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # header
        cells = (list(row) + [None] * 7)[:7]
        pn, _haupt, unter, _quelle, quell_url, verif_am, notiz = cells
        if not pn:
            continue
        facts.append(SkuFacts(
            pn=str(pn), unterkategorie=str(unter or ""),
            quell_url=str(quell_url or ""), verifiziert_am=str(verif_am or ""),
            notiz=str(notiz or ""),
        ))
    return facts


# --- in-session content sidecar (the $0 authoring bridge) --------------------------------
# A JSON file keyed by Part Number carries the authored, datasheet-verified prose + verified
# spec attributes back into the package. JSON (not Markdown blocks) because the prose embeds
# HTML and an FAQ — any text delimiter would collide. The tool EMITS a template (facts +
# source URL per SKU, content fields blank, the two derivable attributes pre-seeded); Claude
# FILLS it in-session ($0, never an API); `reconcile_content` READS it onto the pipeline.


def write_content_template(facts: list[SkuFacts], path: str | Path) -> Path:
    """Emit a JSON content template — one entry per SKU, content blank, facts as `_facts`.

    `_facts` (PN, Unterkategorie, Quell-URL) is the author's spine: every claim is
    round-tripped against that datasheet URL. `attributes` is pre-seeded with the two
    derivable values (Formfaktor, Zustand); the author appends verified spec rows and
    records each in `provenance` (Attributname -> [Source_URL, Confidence]). `netto_vk`
    stays null (operator-supplied). Keys with a leading underscore are hints, ignored on read.
    """
    out = Path(path)
    template: dict[str, dict] = {}
    for f in facts:
        template[f.pn] = {
            "_facts": {"unterkategorie": f.unterkategorie, "quell_url": f.quell_url,
                       "verifiziert_am": f.verifiziert_am},
            "artikelname": "",
            "titel_tag": "",
            "meta_description": "",
            "kurzbeschreibung": "",          # 2× <p>, 40-80 words
            "intro": [],                      # 3 plain-text paragraphs (composed into <p>)
            "faq": [],                        # [["Frage?","Antwort"], …] 3-10 pairs
            "beschreibung": "",              # leave blank — composed from intro by reconcile
            "attributes": [list(pair) for pair in _derive_attributes(f)],
            "netto_vk": None,
            "provenance": {},
        }
    out.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
