"""§5 — resolve a Netto-VK per SKU from gathered market observations, feeding the deterministic
engine (src/hexcat/pricing.py) its T1-MARKET tier, with the feature-model as the fallback and the
category bands as guard rails. Pure and offline; the network gathering lives in the gatherer script.

Resolution order (best grounded wins, nothing invented):
  1. T1-MARKET — authorized new-sealed reseller observations -> aggregate -> the engine medians
     them (pricing.resolve_price). confidence from source count / spread.
  2. MODEL     — no observations: interpolate from priced comparables (lib.price_model), confidence
     low/medium by cohort size. Only used if the model back-test passed upstream.
  3. FLAG      — neither grounds it: no price emitted (honest flagged-debt).
Category-band guards run on the resolved value; a BLOCK (absurd vs the category) downgrades to FLAG
(stays flagged-debt, never ships a wrong number); FLAG: notes ship but are recorded for review.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from hexcat.pricing import PriceInputs, PricePolicy, resolve_price, to_eur  # noqa: E402
from lib import market_comp as MC  # noqa: E402
from lib.price_model import Features, ModelPrediction, PriceModel, extract_features  # noqa: E402

OBSERVATIONS = ROOT / "config" / "market_prices" / "market_observations.yaml"
POLICY = ROOT / "config" / "pricing_policy.yaml"


@dataclass(frozen=True)
class PriceOutcome:
    sku: str
    value: Decimal | None
    tier: str                       # "T1-MARKET" | "MODEL" | "FLAG"
    confidence: str                 # "high" | "medium" | "low" | "none"
    low: Decimal | None = None
    median: Decimal | None = None
    high: Decimal | None = None
    n_sources: int = 0
    sources: tuple[str, ...] = ()
    flags: tuple[str, ...] = ()
    cohort: str = ""

    @property
    def netto_vk(self) -> str:
        return to_eur(self.value) if self.value is not None else "0,00"

    @property
    def shipped(self) -> bool:
        return self.value is not None


def _band(bands: dict, unterkat: str) -> tuple[Decimal | None, Decimal | None]:
    b = bands.get(unterkat) or bands.get("_default") or {}
    lo = Decimal(str(b["floor"])) if "floor" in b else None
    hi = Decimal(str(b["ceiling"])) if "ceiling" in b else None
    return lo, hi


def _confidence(n: int, spread: Decimal | None, max_spread: Decimal) -> str:
    if n >= 3 and (spread is None or spread <= max_spread):
        return "high"
    if n == 2:
        return "medium"
    return "low"


def resolve(sku: str, *, unterkat: str, attrs: dict[str, str], net_values: list[Decimal],
            sources: list[str], model: PriceModel | None, policy_doc: dict,
            fx: Decimal, brand: str = "Cisco", list_eur: Decimal | None = None) -> PriceOutcome:
    pol = policy_doc.get("policy", {})
    market = policy_doc.get("market", {})
    bands = policy_doc.get("category_bands", {})
    high_value = Decimal(str(pol.get("high_value_eur", 1500)))
    max_spread = Decimal(str(pol.get("max_spread", 0.6)))
    min_sources = int(market.get("min_sources", 1))
    floor, ceiling = _band(bands, unterkat)
    engine = PricePolicy.load(POLICY)

    comp = MC.aggregate(sku, net_values)
    value: Decimal | None = None
    tier = "FLAG"
    confidence = "none"
    cohort = ""

    # Engine resolves the best grounded tier natively: T1-MARKET (median of observations) wins, else
    # T2-LIST (manufacturer list * list_to_net) if a list anchor is present.
    obs = list(comp.net_eur_values) if (comp.grounded and comp.n_sources >= min_sources) else []
    if obs or list_eur is not None:
        res = resolve_price(PriceInputs(sku=sku, market_observations=obs, list_price=list_eur), engine)
        if res.value is not None:
            value, tier = res.value, res.tier
            confidence = (_confidence(comp.n_sources, comp.spread, max_spread)
                          if res.tier == "T1-MARKET" else "medium")
    if value is None and model is not None:
        pred: ModelPrediction = model.predict(extract_features(attrs, sku, brand))
        if pred.value is not None:
            value, tier, cohort = pred.value, "MODEL", pred.cohort
            confidence = "medium" if pred.n >= 4 else "low"

    flags: list[str] = []
    if value is not None:
        flags = MC.band_flags(value, floor=floor, ceiling=ceiling, n_sources=comp.n_sources,
                              spread=comp.spread, high_value_eur=high_value, max_spread=max_spread)
        if any(f.startswith("BLOCK:") for f in flags):
            value, tier, confidence = None, "FLAG", "none"   # guarded out -> honest flagged-debt
    if tier == "MODEL":
        flags = list(flags) + ["FLAG:modeled (no direct market observation)"]

    return PriceOutcome(
        sku=sku, value=value, tier=tier, confidence=confidence,
        low=comp.low, median=comp.median, high=comp.high, n_sources=comp.n_sources,
        sources=tuple(sources), flags=tuple(flags), cohort=cohort,
    )


def load_observations(path: Path | None = None) -> dict[str, dict]:
    """Read the gathered market_observations.yaml -> {sku: {net_values:[Decimal], sources:[url]}}.
    Missing file -> {} (no observations gathered yet)."""
    p = path or OBSERVATIONS
    if not p.exists():
        return {}
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    out: dict[str, dict] = {}
    for sku, raw in (doc.get("skus") or {}).items():
        vals, srcs = [], []
        for o in (raw.get("observations") or []):
            if o.get("net_eur") is not None:
                vals.append(Decimal(str(o["net_eur"])))
                srcs.append(str(o.get("url", o.get("seller", "?"))))
        out[sku] = {"net_values": vals, "sources": srcs}
    return out
