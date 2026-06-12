"""§5 Pass-1 — the grounded price-input loader (the seam that unstubs the pricing engine).

`pricing.py` is a pure, deterministic, $0 engine: given `PriceInputs` it derives a tiered price,
but it never reaches the network. The network half — gathering real manufacturer list prices — is
done by Claude IN-SESSION via WebSearch (exactly like the German prose is authored in-session,
never by the tool, never via a paid API). Those findings land in
`config/market_prices/list_prices.yaml`, each entry tracing verbatim to a real source URL with an
explicit confidence. THIS module reads that file, FX-converts the USD GPL list figures to EUR, and
hands `pricing.resolve_price` a grounded `PriceInputs` per SKU. No SKU absent from the file is
priced — it stays honest flagged-debt, never invented (the 1000% rule).

Pure and offline: the only inputs are the YAML file and the engine. No I/O beyond reading config.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import yaml

from hexcat.pricing import PriceInputs, PricePolicy, PriceResult, resolve_price

REPO = Path(__file__).resolve().parents[2]
LIST_PRICES_ARTIFACT = REPO / "config" / "market_prices" / "list_prices.yaml"


@dataclass(frozen=True)
class GroundedListPrice:
    """One grounded manufacturer list anchor, FX-converted to EUR, with its provenance."""
    sku: str
    list_usd: Decimal
    list_eur: Decimal      # list_usd * fx (the manufacturer UVP in EUR)
    kind: str              # e.g. "list-gpl"
    confidence: str        # "high" | "medium" | "low" — carries the honesty of the source
    source: str            # the real URL the figure traces to
    note: str = ""


@dataclass(frozen=True)
class PriceInputBook:
    """The whole grounded input set: the dated FX rate plus per-SKU list anchors."""
    usd_eur: Decimal
    fx_as_of: str
    fx_source: str
    entries: dict[str, GroundedListPrice]

    def __contains__(self, sku: str) -> bool:
        return sku in self.entries

    def get(self, sku: str) -> GroundedListPrice | None:
        return self.entries.get(sku)

    def price_inputs(self, sku: str) -> PriceInputs:
        """Build engine `PriceInputs` for a SKU: T2 list grounded iff the SKU is in the book.

        Returns an empty (ungrounded) PriceInputs for an absent SKU so the engine FLAGS it — the
        loader never fabricates a list price to fill a gap.
        """
        e = self.entries.get(sku)
        return PriceInputs(sku=sku, list_price=e.list_eur if e else None)

    def resolve(self, sku: str, policy: PricePolicy) -> PriceResult:
        """Resolve a grounded price for a SKU through the deterministic engine."""
        return resolve_price(self.price_inputs(sku), policy)


def _dec(v: object) -> Decimal:
    return Decimal(str(v))


def load_price_inputs(path: Path | None = None) -> PriceInputBook:
    """Read `config/market_prices/list_prices.yaml` and FX-convert each USD list anchor to EUR.

    Raises FileNotFoundError if the file is absent (an empty book is a deliberate state — write a
    file with an empty `skus:` map, do not delete it). Each USD figure is multiplied by the dated
    `fx.usd_eur` rate to yield the EUR manufacturer list price the engine consumes at T2.
    """
    p = path or LIST_PRICES_ARTIFACT
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    fx = data.get("fx", {}) or {}
    usd_eur = _dec(fx.get("usd_eur", 0))
    if usd_eur <= 0:
        raise ValueError(f"{p.name}: fx.usd_eur must be a positive rate, got {fx.get('usd_eur')!r}")

    entries: dict[str, GroundedListPrice] = {}
    for sku, raw in (data.get("skus") or {}).items():
        if "list_usd" not in raw:
            # Only USD GPL anchors are FX-converted here; an entry without list_usd is malformed.
            raise ValueError(f"{p.name}: sku {sku!r} has no list_usd")
        list_usd = _dec(raw["list_usd"])
        entries[sku] = GroundedListPrice(
            sku=sku,
            list_usd=list_usd,
            list_eur=list_usd * usd_eur,
            kind=str(raw.get("kind", "list-gpl")),
            confidence=str(raw.get("confidence", "low")),
            source=str(raw.get("source", "")),
            note=str(raw.get("note", "")),
        )

    return PriceInputBook(
        usd_eur=usd_eur,
        fx_as_of=str(fx.get("as_of", "")),
        fx_source=str(fx.get("source", "")),
        entries=entries,
    )
