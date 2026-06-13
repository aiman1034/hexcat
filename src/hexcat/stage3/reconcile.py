"""Reconcile an in-session-authored content sidecar (`*_content.json`) onto the canonical
build pipeline.

This is the convergence layer: it turns each authored SKU into a wide `SkuIntake` row and
hands it to `intake.build_record`, so Stage-3 packages are assembled by the SAME
`assemble_bundle` / `constants` / `writers` / `validate` path the proof slice was built with.
There is exactly ONE output contract; the divergent `package.py` writer is retired.

What this layer does (deterministic, $0, no model calls):

  * ATTRIBUTES — remap the author's free-vocabulary attribute names onto the locked 14-schema
    (`constants.TRANSCEIVER_ATTRIBUTES`); names with no canonical slot are dropped (the rich
    detail survives in the prose). On a name collision the first authored value wins. The
    `Formfaktor` VALUE is reduced to its physical connector token (QSFP56, SFP+, …) — never a
    commerce category like "DAC Kabel" (that stays in Kategorie Ebene 3).
  * BESCHREIBUNG — compose the 3 authored intro paragraphs as prose-only `<p>` blocks (NO
    spec `<ul>`, NO inline FAQ — those were `package.py` composition artifacts), and weave the
    mandatory authenticity closer ("Originaler {Hersteller}-…") into the final paragraph so the
    Beschreibung ENDS on it.
  * FAQ — emit as the separate canonical `Q||A##…` cell (never inline in the Beschreibung).
  * CONDITION / WEIGHTS / PRICE — condition is "new"; weights derive from `weights.yaml` by the
    physical Formfaktor; price stays a PRICES-PENDING placeholder ("0,00") unless authored.

The author still owns every German sentence and every verified spec VALUE (in-session, $0).
This module only re-shapes that authored content onto the locked structural contract.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .. import constants as C
from ..config import Rules, Weights
from ..intake import build_record
from ..models import SkuIntake, SkuRecord

# --- attribute-name aliasing -> the locked 14-schema -------------------------------------
# Canonical names (the only ones validate.py accepts) live in constants.TRANSCEIVER_ATTRIBUTES.
# The authors used a richer free vocabulary across brands; this map folds each onto its
# canonical slot. Names absent here have no canonical slot and are DROPPED (their detail is
# carried by the prose). On collision (two aliases -> one canonical) the FIRST authored value
# wins (see `map_attributes`).
ATTR_ALIAS: dict[str, str] = {
    "Formfaktor": "Formfaktor",
    # speed / data rate
    "Datenrate": "Geschwindigkeit",
    "Geschwindigkeit": "Geschwindigkeit",
    # transceiver / optical type
    "Transceiver": "Transceiver Typ",
    "Transceiver Typ": "Transceiver Typ",
    "Typ": "Transceiver Typ",
    "Optischer Typ": "Transceiver Typ",
    # fibre / media
    "Fasertyp": "Fasertyp",
    "Medientyp": "Fasertyp",
    "Medium": "Fasertyp",
    # fibre count (canonical schema field; self-alias so authored depth is not dropped)
    "Faseranzahl": "Faseranzahl",
    # connector / interface
    "Anschluss": "Anschlusstyp",
    "Anschlusstyp": "Anschlusstyp",
    "Anschlussenden": "Anschlusstyp",
    "Schnittstelle": "Anschlusstyp",
    # length
    "Länge": "Länge",
    # cable type
    "Kabeltyp": "Kabeltyp",
    # wavelength
    "Wellenlänge": "Wellenlänge",
    # application context
    "Aufteilung": "Anwendung",
    "Übertragung": "Anwendung",
    "Anwendung": "Anwendung",
    # reach
    "Reichweite": "Reichweite",
    # DOM/DDM
    "DOM/DDM": "DOM Unterstützung",
    "DDM/DOM": "DOM Unterstützung",
    "DOM Unterstützung": "DOM Unterstützung",
    # operating temperature
    "Betriebstemperatur": "Betriebstemperatur",
    "Betriebstemperatur (Gehäuse)": "Betriebstemperatur",
    "Betriebstemperatur (getestet)": "Betriebstemperatur",
    "Temperaturbereich": "Betriebstemperatur",
    # standard / conformance
    "Standard": "Standard",
    "Schnittstellenstandard": "Standard",
    "Konformität": "Standard",
}

# Canonical name -> the SkuIntake field that carries it (from the locked schema).
_CANON_TO_FIELD: dict[str, str] = {name: field for name, field in C.TRANSCEIVER_ATTRIBUTES}

_CABLE_CATEGORIES = C.CABLE_CATEGORIES


class ReconcileError(ValueError):
    """Raised when an authored content entry cannot be mapped onto the contract."""


# --- physical form-factor extraction -----------------------------------------------------
def physical_formfaktor(*candidates: str) -> str | None:
    """Return the physical connector token (QSFP56, SFP+, …) found in any candidate string.

    Candidates are tried in order (authored Formfaktor value, then connector/speed text, then
    the PN). Tokens are matched most-specific-first so "SFP28" never collapses to "SFP" and
    "QSFP-DD800" never collapses to "QSFP-DD". Returns None if nothing matches (caller flags).
    """
    for text in candidates:
        if not text:
            continue
        for tok in C.PHYSICAL_FORMFAKTOR_ORDERED:
            idx = text.find(tok)
            if idx == -1:
                continue
            # Guard the right edge: the char after the token must not extend it into a
            # different (longer) connector we haven't matched — but since we scan
            # most-specific-first, a longer token would already have matched. We only need
            # to avoid matching e.g. "SFP" inside "SFP+" when the '+' belongs to the token:
            after = text[idx + len(tok): idx + len(tok) + 1]
            if after in ("+",) and not tok.endswith("+"):
                continue  # this "SFP" is really "SFP+"; let the SFP+ pass catch it
            before = text[idx - 1: idx] if idx > 0 else ""
            if tok.startswith("SFP") and before.upper() == "Q":
                continue  # this "SFP" is really "QSFP…" — never collapse QSFP-200 to SFP
            return tok
    # Cisco PN abbreviation: "QDD" == QSFP-DD (e.g. QDD-400-CU1M, QDD-4ZQ100-CU2M); the 800G
    # variants (QDD-800…) are QSFP-DD800. Only consulted when no explicit token matched above.
    for text in candidates:
        if text and re.search(r"\bQDD-?8", text):
            return "QSFP-DD800"
        if text and re.search(r"\bQDD\b|\bQDD-", text):
            return "QSFP-DD"
    return None


def map_attributes(authored: list[tuple[str, str]], formfaktor: str) -> dict[str, str]:
    """Fold authored (name, value) pairs onto the canonical 14-schema intake fields.

    Returns {intake_field: value}. The Formfaktor field is forced to the physical connector
    token. Unmappable names are dropped; on collision the first authored value wins. The
    "Zustand" attribute is intentionally NOT mapped here (it becomes the Condition file).
    """
    out: dict[str, str] = {}
    canon_seen: set[str] = set()
    for name, value in authored:
        canon = ATTR_ALIAS.get(name)
        if canon is None or canon == "Formfaktor":
            continue  # dropped (no slot) or handled separately below
        if canon in canon_seen:
            continue  # first authored value wins
        value = (value or "").strip()
        if not value:
            continue
        canon_seen.add(canon)
        out[_CANON_TO_FIELD[canon]] = value
    out["Formfaktor"] = formfaktor
    return out


# --- authenticity closer ------------------------------------------------------------------
def _closer(hersteller: str, kategorie3: str) -> str:
    """The mandatory authenticity closer sentence woven onto the END of the Beschreibung.

    Article ending agrees with the product noun's gender ("Originaler …Transceiver" m. /
    "Originales …Kabel" n.). Uses ONLY the Hersteller token (matching the gate's closer
    regex) and carries no banned/transactional language.
    """
    tail = f"den professionellen Einsatz in {hersteller}-Netzwerkumgebungen"
    if kategorie3 == "DAC Kabel":
        return f"Originales {hersteller}-Direktanschlusskabel für {tail}."
    if kategorie3 == "AOC Kabel":
        return f"Originales {hersteller}-AOC-Kabel für {tail}."
    if kategorie3 == "MPO Kabel":
        return f"Originales {hersteller}-MPO-Kabel für {tail}."
    return f"Originaler {hersteller}-Transceiver für {tail}."


def _compose_beschreibung(intro: list[str], hersteller: str, kategorie3: str) -> str:
    """3 prose-only <p> blocks; the closer is appended to the final paragraph so the
    Beschreibung ENDS on it. No <ul>/<strong>/<br>/<a> and no inline FAQ."""
    paras = [p.strip() for p in intro if p and p.strip()]
    if not paras:
        raise ReconcileError("intro is empty — cannot compose Beschreibung")
    closer = _closer(hersteller, kategorie3)
    last = paras[-1].rstrip()
    if not last.endswith((".", "!", "?")):
        last += "."
    paras[-1] = f"{last} {closer}"
    return "".join(f"<p>{p}</p>" for p in paras)


def _faq_cell(faq: list[tuple[str, str]]) -> str:
    """Canonical Q||A##Q||A cell (build_record re-parses it). Strips any separator chars that
    would corrupt the cell out of the authored Q/A text."""
    pairs = []
    for item in faq:
        if not (isinstance(item, (list, tuple)) and len(item) >= 2):
            continue
        q = str(item[0]).replace(C.FAQ_QA_SEP, "/").replace(C.FAQ_PAIR_SEP, " ").strip()
        a = str(item[1]).replace(C.FAQ_QA_SEP, "/").replace(C.FAQ_PAIR_SEP, " ").strip()
        if q and a:
            pairs.append(f"{q}{C.FAQ_QA_SEP}{a}")
    return C.FAQ_PAIR_SEP.join(pairs)


def entry_to_intake(pn: str, entry: dict, *, brand: str, rules: Rules) -> SkuIntake:
    """Map one authored content.json entry onto a wide SkuIntake row."""
    vendor_entry = rules.resolve_vendor(brand)
    if vendor_entry is None:
        raise ReconcileError(
            f"[{pn}] brand {brand!r} not in the vendor map {sorted(rules.vendors)}"
        )
    hersteller = vendor_entry.hersteller

    facts = entry.get("_facts") or {}
    kategorie3 = str(facts.get("unterkategorie") or "").strip()
    quell_url = str(facts.get("quell_url") or "").strip()

    authored_attrs = [
        (str(a[0]), str(a[1]))
        for a in (entry.get("attributes") or [])
        if isinstance(a, (list, tuple)) and len(a) >= 2
    ]

    # Physical connector: authored Formfaktor value -> connector/speed text -> PN.
    authored_ff = next((v for n, v in authored_attrs if n == "Formfaktor"), "")
    anschluss = next((v for n, v in authored_attrs
                      if n in ("Anschluss", "Anschlusstyp", "Anschlussenden", "Schnittstelle")), "")
    datenrate = next((v for n, v in authored_attrs
                      if n in ("Datenrate", "Geschwindigkeit")), "")
    ff = physical_formfaktor(authored_ff, anschluss, datenrate, pn)
    if ff is None:
        raise ReconcileError(
            f"[{pn}] could not derive a physical Formfaktor from "
            f"{authored_ff!r}/{anschluss!r}/{datenrate!r}/{pn!r}"
        )

    attr_fields = map_attributes(authored_attrs, ff)

    intro = [str(p) for p in (entry.get("intro") or [])]
    beschreibung = _compose_beschreibung(intro, hersteller, kategorie3)

    price = entry.get("netto_vk")
    netto_vk = str(price).strip() if price else "0.00"  # PRICES-PENDING placeholder

    payload = {
        "Artikelnummer": pn,
        "Vendor": brand,
        "KategorieEbene3": kategorie3,
        "Artikelname": str(entry.get("artikelname") or "").strip(),
        "Kurzbeschreibung": str(entry.get("kurzbeschreibung") or "").strip(),
        "Beschreibung": beschreibung,
        "TitelTag": str(entry.get("titel_tag") or "").strip(),
        "MetaDescription": str(entry.get("meta_description") or "").strip(),
        "NettoVK": netto_vk,
        "Artikelgewicht": "",   # derived from weights.yaml by Formfaktor
        "Versandgewicht": "",
        "Condition": "new",
        "FAQ": _faq_cell(entry.get("faq") or []),
        "SourceURLs": quell_url,
    }
    payload.update(attr_fields)
    return SkuIntake(**payload)


def reconcile_content(
    path: str | Path, *, brand: str, rules: Rules, weights: Weights
) -> list[SkuRecord]:
    """Read an authored content.json and return canonical SkuRecords ready for assemble_bundle.

    Each entry flows through `intake.build_record`, so weights, FAQ normalisation, vendor
    resolution, URL-Pfad, the German-decimal price, and the canonical attribute transpose are
    all produced by the SAME code the proof-slice build used. Raises ReconcileError on the
    first entry that cannot be mapped (flag-don't-emit).
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    records: list[SkuRecord] = []
    for pn, entry in data.items():
        if not isinstance(entry, dict):
            continue
        intake = entry_to_intake(str(pn), entry, brand=brand, rules=rules)
        # Carry each authored per-attribute provenance onto the canonical attribute name (via the
        # same ATTR_ALIAS the values flow through) so the Verification_Log records the real source +
        # confidence (datasheet / derivation / standard-derived / ...), not a blanket operator label.
        canon_prov: dict[str, tuple[str, str]] = {}
        for k, v in (entry.get("provenance") or {}).items():
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                canon_prov[ATTR_ALIAS.get(k, k)] = (str(v[0]), str(v[1]))
        records.append(build_record(intake, rules, weights, attr_provenance=canon_prov))
    if not records:
        raise ReconcileError(f"{Path(path).name} contained no usable SKU entries")
    return records
