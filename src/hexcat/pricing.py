"""§5 — the deterministic, ZERO-DOLLAR automated-pricing engine.

A price is NOT a verifiable physical fact (unlike a wavelength); it is a commercial estimate.
So this engine never *fabricates* a number out of thin air — it derives one ONLY from a grounded
input, tags every output with the tier that produced it, runs guard rails, and FLAGS (emits no
price) when nothing grounds it. Same discipline as the rest of HexCat: flag, don't invent.

Tier hierarchy (best grounded source wins):
  * T1 MARKET — observed competitor/market prices. Highest confidence. Ingestion is a STUBBED
    hook (`fetch_market_observations`) per the operator decision: NO network, NO paid call. It
    returns nothing until a real (operator-run) comp pass populates it.
  * T2 LIST   — manufacturer list price (UVP/MSRP) × an operator list→net policy factor.
  * T3 COST   — operator cost basis × an operator markup policy factor.
  * else      — FLAG: no grounded input, no price emitted (the readiness gate keeps it a BLOCK).

Guards run on whatever a tier produces and can DOWNGRADE it to a flag (e.g. an implausible
margin vs the known cost). `back_test` validates the policy factors against SKUs whose true
price is already known BEFORE the factors are trusted on unpriced SKUs. Pure, deterministic, $0.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
POLICY_ARTIFACT = REPO / "config" / "pricing_policy.yaml"

T1, T2, T3, FLAG = "T1-MARKET", "T2-LIST", "T3-COST", "FLAG"
TIER_ORDER = (T1, T2, T3)

_CENT = Decimal("0.01")


def to_eur(value: Decimal) -> str:
    """Format a Decimal as a German-decimal Netto-VK string, e.g. Decimal('120.5') -> '120,50'."""
    q = value.quantize(_CENT, rounding=ROUND_HALF_UP)
    return f"{q:.2f}".replace(".", ",")


def from_eur(s: str) -> Decimal | None:
    """Parse a German-decimal price string to Decimal; None if unparseable."""
    try:
        return Decimal(s.strip().replace(".", "").replace(",", "."))
    except (InvalidOperation, AttributeError):
        return None


@dataclass(frozen=True)
class PricePolicy:
    """Operator pricing POLICY (knobs, not market facts). Defaults are neutral placeholders the
    operator MUST confirm — they are not claims about real prices."""
    list_to_net: Decimal = Decimal("0.55")   # net sell = list * this (T2)
    cost_markup: Decimal = Decimal("0.35")   # net sell = cost * (1 + this) (T3)
    margin_min: Decimal = Decimal("0.10")    # acceptable gross margin band vs known cost
    margin_max: Decimal = Decimal("0.80")
    tier_tolerance: Decimal = Decimal("0.25")  # cross-tier agreement (relative) before a WARN
    backtest_max_mape: Decimal = Decimal("0.20")  # back-test passes if MAPE <= this

    @staticmethod
    def load(path: Path | None = None) -> "PricePolicy":
        p = path or POLICY_ARTIFACT
        if not p.exists():
            return PricePolicy()
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        pol = d.get("policy", d)

        def dec(key: str, default: Decimal) -> Decimal:
            return Decimal(str(pol[key])) if key in pol and pol[key] is not None else default

        base = PricePolicy()
        return PricePolicy(
            list_to_net=dec("list_to_net", base.list_to_net),
            cost_markup=dec("cost_markup", base.cost_markup),
            margin_min=dec("margin_min", base.margin_min),
            margin_max=dec("margin_max", base.margin_max),
            tier_tolerance=dec("tier_tolerance", base.tier_tolerance),
            backtest_max_mape=dec("backtest_max_mape", base.backtest_max_mape),
        )


@dataclass
class PriceInputs:
    """Grounded inputs for one SKU. Any may be missing; the engine uses the best present tier."""
    sku: str
    market_observations: list[Decimal] = field(default_factory=list)  # T1
    list_price: Decimal | None = None    # T2 (manufacturer UVP/MSRP)
    cost: Decimal | None = None          # T3 (operator cost basis)


@dataclass
class PriceResult:
    sku: str
    value: Decimal | None
    tier: str
    reason: str
    guards: list[str] = field(default_factory=list)  # guard messages (WARN-level)

    @property
    def flagged(self) -> bool:
        return self.value is None or self.tier == FLAG

    @property
    def netto_vk(self) -> str:
        return to_eur(self.value) if self.value is not None else ""


# --- the STUBBED market-ingestion hook -------------------------------------------------

def fetch_market_observations(sku: str) -> list[Decimal]:
    """STUB: real competitor/market price ingestion is DEFERRED (operator-run, $0, no network).

    Returns [] so T1 never grounds until a real comp pass populates inputs out-of-band. This is
    the single seam where a future operator-supplied feed plugs in — the engine code does not
    change, only this hook's data source.
    """
    return []


# --- tier resolution -------------------------------------------------------------------

def _tier_value(inputs: PriceInputs, tier: str, policy: PricePolicy) -> Decimal | None:
    if tier == T1:
        obs = inputs.market_observations
        return Decimal(statistics.median(obs)) if obs else None
    if tier == T2:
        return inputs.list_price * policy.list_to_net if inputs.list_price is not None else None
    if tier == T3:
        return inputs.cost * (Decimal(1) + policy.cost_markup) if inputs.cost is not None else None
    return None


def resolve_price(inputs: PriceInputs, policy: PricePolicy) -> PriceResult:
    """Pick the highest-confidence grounded tier, run guards, return a located result."""
    chosen_tier = None
    chosen_value = None
    for tier in TIER_ORDER:
        v = _tier_value(inputs, tier, policy)
        if v is not None and v > 0:
            chosen_tier, chosen_value = tier, v
            break

    if chosen_value is None:
        return PriceResult(inputs.sku, None, FLAG,
                           "no grounded input (market/list/cost all absent) — price flagged")

    guards = _guards(inputs, chosen_tier, chosen_value, policy)
    hard = [g for g in guards if g.startswith("BLOCK:")]
    if hard:
        return PriceResult(inputs.sku, None, FLAG,
                           f"guarded out ({chosen_tier}): {hard[0]}", guards=guards)
    return PriceResult(inputs.sku, chosen_value.quantize(_CENT, rounding=ROUND_HALF_UP),
                       chosen_tier, f"grounded via {chosen_tier}", guards=guards)


def _guards(inputs: PriceInputs, tier: str, value: Decimal, policy: PricePolicy) -> list[str]:
    out: list[str] = []
    # Margin band vs known cost: an auto-price below/above a plausible margin is blocked.
    if inputs.cost is not None and value > 0:
        margin = (value - inputs.cost) / value
        if margin < policy.margin_min:
            out.append(f"BLOCK: margin {margin:.0%} below floor {policy.margin_min:.0%} vs cost")
        elif margin > policy.margin_max:
            out.append(f"BLOCK: margin {margin:.0%} above ceiling {policy.margin_max:.0%} vs cost")
    # Cross-tier agreement: if another grounded tier disagrees materially, WARN (not block).
    for other in TIER_ORDER:
        if other == tier:
            continue
        ov = _tier_value(inputs, other, policy)
        if ov is not None and ov > 0:
            dev = abs(value - ov) / value
            if dev > policy.tier_tolerance:
                out.append(f"WARN: {tier} deviates {dev:.0%} from {other} (review)")
    return out


# --- back-test -------------------------------------------------------------------------

@dataclass
class BackTestSample:
    inputs: PriceInputs
    true_price: Decimal


@dataclass
class BackTestReport:
    n: int
    n_scored: int
    mape: Decimal | None           # mean absolute percentage error over scored samples
    median_ape: Decimal | None
    passed: bool
    detail: str


def back_test(samples: list[BackTestSample], policy: PricePolicy) -> BackTestReport:
    """Validate the policy factors: predict each sample from its inputs and compare to the KNOWN
    true price. Passes when MAPE <= policy.backtest_max_mape. A sample whose inputs ground no
    tier (or whose true price is 0) is skipped (n_scored < n). Guarantees the factors are sane
    before they are trusted on unpriced SKUs.
    """
    apes: list[Decimal] = []
    for s in samples:
        if s.true_price <= 0:
            continue
        r = resolve_price(s.inputs, policy)
        if r.value is None:
            continue
        apes.append(abs(r.value - s.true_price) / s.true_price)
    if not apes:
        return BackTestReport(len(samples), 0, None, None, False,
                              "no scorable samples (no grounded inputs) — cannot validate policy")
    mape = sum(apes) / len(apes)
    median = Decimal(statistics.median(apes))
    passed = mape <= policy.backtest_max_mape
    return BackTestReport(
        len(samples), len(apes), mape, median, passed,
        f"MAPE {mape:.1%} over {len(apes)}/{len(samples)} samples "
        f"({'PASS' if passed else 'FAIL'} vs {policy.backtest_max_mape:.0%} tolerance)",
    )
