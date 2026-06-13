"""Feature-model price FALLBACK for SKUs with no market observations (pricing.py tier below T1).

When the bridge comp pass finds no authorized new-sealed listing for a SKU, we do NOT invent a
number — we interpolate from REAL priced comparables along the dimensions that drive optic price:
form factor x line speed x reach class x optical type (x brand). The model is a transparent
nearest-cohort median: predict a SKU's net price as the median of the anchor SKUs in the narrowest
cohort that has enough members, widening the cohort (drop optic, then reach, then form) until it
does. Every prediction carries the cohort key and member count so confidence is explicit.

`back_test` validates the model the way pricing.back_test validates the policy factors: hold each
anchor out, predict it from the rest, and report MAPE — so the fallback is trusted only when it
actually reproduces known prices within bound. Pure, deterministic, offline.
"""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Features:
    form: str                      # Formfaktor token (SFP+, QSFP28, …)
    speed_gbps: float | None       # line rate in Gbit/s (0.155 for OC-3, etc.); None if unknown
    reach_band: str                # DAC|SR|MR|IR|LR|ER|ZR|DWDM|COHERENT|COPPER|?
    optic: str                     # MM|SM|COPPER|DAC|AOC|COHERENT|?
    brand: str = "Cisco"


_SPEED_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(g|gbit|gbps|gbe|gigabit|m|mbit|mbps|t|tbit|tbps)", re.I)


def _speed_gbps(text: str) -> float | None:
    if not text:
        return None
    t = text.lower()
    best: float | None = None
    for m in _SPEED_RE.finditer(t):
        val = float(m.group(1).replace(",", "."))
        unit = m.group(2)[0]
        g = val / 1000 if unit == "m" else (val * 1000 if unit == "t" else val)
        best = g if best is None else max(best, g)
    return best


def _reach_band(reach: str, optic: str, name: str) -> str:
    s = f"{reach} {name}".upper()
    if optic in ("DAC", "COPPER"):
        return "DAC" if optic == "DAC" else "COPPER"
    if "AOC" in s:
        return "AOC"
    if any(k in s for k in ("ZR", "DWDM")):
        return "ZR" if "ZR" in s else "DWDM"
    if "COHEREN" in s or "KOHÄREN" in s or "KOHAEREN" in s:
        return "COHERENT"
    if re.search(r"\bER\b|\bER4\b|80\s?KM", s):
        return "ER"
    if re.search(r"\bLR\b|\bLR4\b|10\s?KM|40\s?KM|LONG", s):
        return "LR"
    if re.search(r"\bIR\b|15\s?KM|INTERMEDIATE", s):
        return "IR"
    if re.search(r"\bSR\b|\bSR4\b|MULTIMODE|SHORT|\b2\s?KM|MM\b", s):
        return "SR"
    return "?"


def _optic(fasertyp: str, form: str, name: str) -> str:
    s = f"{fasertyp} {name}".upper()
    if "DAC" in s or "TWINAX" in s or "-CU" in name.upper():
        return "DAC"
    if "AOC" in s:
        return "AOC"
    if "KOHÄR" in s or "COHEREN" in s or form == "CIM8":
        return "COHERENT"
    if "KUPFER" in s or "COPPER" in s or "RJ-45" in s or "CAT" in s:
        return "COPPER"
    if "MULTIMODE" in s or s.strip().startswith("MM"):
        return "MM"
    if "SINGLEMODE" in s or "SINGLE-MODE" in s or "SM" in s:
        return "SM"
    return "?"


def extract_features(attrs: dict[str, str], pn: str, brand: str = "Cisco") -> Features:
    """Build pricing Features from a SKU's authored attributes (canonical names) + its PN."""
    form = (attrs.get("Formfaktor") or "").strip() or "?"
    speed = _speed_gbps(attrs.get("Geschwindigkeit") or "")
    optic = _optic(attrs.get("Fasertyp") or "", form, f"{pn} {attrs.get('Transceiver Typ','')}")
    reach = _reach_band(attrs.get("Reichweite") or attrs.get("Transceiver Typ") or "", optic, pn)
    return Features(form=form, speed_gbps=speed, reach_band=reach, optic=optic, brand=brand)


@dataclass(frozen=True)
class ModelPrediction:
    value: Decimal | None
    cohort: str                    # the cohort key used (or "" when ungrounded)
    n: int                         # anchors in the cohort


class PriceModel:
    """Nearest-cohort median model fit on (Features, net_price) anchors."""

    def __init__(self, samples: list[tuple[Features, Decimal]], min_members: int = 2):
        self.samples = [(f, p) for f, p in samples if p and p > 0]
        self.min_members = min_members

    def _cohorts(self, f: Features) -> list[tuple[str, callable]]:
        sp = f"{f.speed_gbps:g}G" if f.speed_gbps else "?"
        return [
            (f"{f.form}|{sp}|{f.reach_band}|{f.optic}",
             lambda g: g.form == f.form and g.speed_gbps == f.speed_gbps and g.reach_band == f.reach_band and g.optic == f.optic),
            (f"{f.form}|{sp}|{f.reach_band}",
             lambda g: g.form == f.form and g.speed_gbps == f.speed_gbps and g.reach_band == f.reach_band),
            (f"{sp}|{f.reach_band}",
             lambda g: g.speed_gbps == f.speed_gbps and g.reach_band == f.reach_band),
            (f"{sp}|{f.optic}",
             lambda g: g.speed_gbps == f.speed_gbps and g.optic == f.optic),
            (f"{sp}",
             lambda g: g.speed_gbps == f.speed_gbps),
        ]

    def predict(self, f: Features) -> ModelPrediction:
        for key, pred in self._cohorts(f):
            members = [p for g, p in self.samples if pred(g)]
            if len(members) >= self.min_members:
                med = Decimal(statistics.median(sorted(members)))
                return ModelPrediction(med.quantize(Decimal("0.01")), key, len(members))
        return ModelPrediction(None, "", 0)


def back_test(samples: list[tuple[Features, Decimal]], min_members: int = 2) -> tuple[Decimal | None, int, int]:
    """Leave-one-out MAPE over the anchors. Returns (mape, n_scored, n_total). A sample whose
    leave-one-out cohort is too thin to predict is skipped (n_scored < n_total)."""
    apes: list[Decimal] = []
    for i, (f, true) in enumerate(samples):
        rest = samples[:i] + samples[i + 1:]
        pred = PriceModel(rest, min_members=min_members).predict(f)
        if pred.value is not None and true > 0:
            apes.append(abs(pred.value - true) / true)
    if not apes:
        return None, 0, len(samples)
    return (sum(apes) / len(apes)), len(apes), len(samples)
