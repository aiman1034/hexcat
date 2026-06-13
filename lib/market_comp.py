"""Bridge-based NEW-SEALED reseller market-price comp pass — the $0 ingestion that unstubs the
pricing engine's T1-MARKET tier (src/hexcat/pricing.py).

A price is a commercial estimate, never a verifiable physical fact — so, exactly like the German
prose, the market observations are gathered IN-SESSION ($0, no paid API): WebSearch locates a SKU's
listing page on an AUTHORIZED new-sealed-original reseller, the page is fetched through the local
bridge (lib.local_fetch — queue + backoff on block, same as datasheets), and the PN-exact EUR price
is extracted here. Refurbished / "compatible" / gray-market sellers are NOT valid anchors and are
excluded. We position at the MEDIAN of the authorized new-sealed competitors (real street price, so
no operator list->net factor). Outliers are rejected; every observation traces to its source URL.

This module is the PURE, deterministic, offline-testable core:
  * seller_ok(url)          — authorized new-sealed domain? (deny refurb/compatible/gray)
  * parse_money(text)       — German/EUR/USD number -> (Decimal, currency)
  * extract_offers(html,pn) — PN-exact offers from JSON-LD/microdata/meta, then EUR-near-PN regex;
                              each tagged net|gross so VAT can be normalized to a Netto-VK
  * to_net_eur(...)         — normalize an offer to net EUR per single unit (strip 19% MwSt if gross)
  * aggregate(obs)          — [low, median, high] + spread, with IQR outlier rejection
The network half (WebSearch + bridge fetch) lives in the gatherer script; nothing here touches IO.
"""
from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from urllib.parse import urlsplit

# Authorized NEW-SEALED-ORIGINAL resellers (operator-named set + clearly-legitimate B2B dealers).
# Match is on the registrable host (suffix), so country variants (senetic.de/.com, …) all count.
AUTHORIZED_SELLERS: tuple[str, ...] = (
    "bechtle.com", "bechtle.de", "senetic.com", "senetic.de", "senetic.eu",
    "computacenter.com", "computacenter.de", "als.com", "also.com", "also.de",
    "cdw.com", "insight.com", "comms-express.com",
    "span.com", "misco.de", "jacob.de", "wiredzone.com",
)
# Refurbished / "compatible" (third-party optic) / gray-market — NOT valid new-sealed anchors.
# router-switch.com is here BY EVIDENCE + RULE: it advertises "new AND refurbished" Cisco optics and
# its USD listings price systematically gray-low (e.g. $102 for an SFP-10G-SR a German distributor
# sells new-sealed at ~€450) — so it fails the operator's "exclude refurbished/gray" rule and is a
# misleading anchor. Excluded; surfaced to the operator. Re-include only if a new-sealed-only feed exists.
EXCLUDED_SELLERS: tuple[str, ...] = (
    "fs.com", "it-planet.com", "itinstock.com", "ebay.", "amazon.", "refurbished",
    "flexoptix.net", "approved-networks.com", " proline", "compatible", "alibaba.",
    "aliexpress.", "serverschmiede", "used", "broker", "router-switch.com",
)

_VAT = Decimal("1.19")           # German MwSt; gross -> net = gross / 1.19
_CENT = Decimal("0.01")


def _host(url: str) -> str:
    return urlsplit(url).netloc.lower().lstrip("www.")


def seller_ok(url: str) -> bool:
    """True iff the URL is an authorized NEW-SEALED reseller and not on the exclusion list."""
    host = _host(url)
    full = url.lower()
    if any(bad in host or bad.strip() in full for bad in EXCLUDED_SELLERS):
        return False
    return any(host == d or host.endswith("." + d) or host == d.lstrip(".") for d in AUTHORIZED_SELLERS)


def seller_name(url: str) -> str:
    h = _host(url)
    return h.split(".")[0] if h else "?"


# --- money parsing ---------------------------------------------------------------------

_NUM = re.compile(r"\d[\d.,]*\d|\d")


def parse_money(text: str) -> tuple[Decimal, str] | None:
    """Parse a price token -> (amount, currency). Handles German (1.234,56) and US (1,234.56)
    grouping and €/EUR/$/USD markers. Returns None if no sane number is found."""
    if not text:
        return None
    t = text.strip()
    cur = "EUR" if ("€" in t or "eur" in t.lower()) else ("USD" if ("$" in t or "usd" in t.lower()) else "")
    m = _NUM.search(t.replace("\xa0", " "))
    if not m:
        return None
    raw = m.group(0)
    # Decide decimal separator: the LAST of '.'/',' with <=2 trailing digits is the decimal point.
    if "," in raw and "." in raw:
        dec_sep = "," if raw.rfind(",") > raw.rfind(".") else "."
    elif "," in raw:
        dec_sep = "," if len(raw.split(",")[-1]) <= 2 else ""
    elif "." in raw:
        dec_sep = "." if len(raw.split(".")[-1]) <= 2 else ""
    else:
        dec_sep = ""
    if dec_sep == ",":
        norm = raw.replace(".", "").replace(",", ".")
    elif dec_sep == ".":
        norm = raw.replace(",", "")
    else:
        norm = raw.replace(".", "").replace(",", "")
    try:
        val = Decimal(norm)
    except InvalidOperation:
        return None
    return (val, cur or "EUR")


# --- offer extraction ------------------------------------------------------------------

@dataclass(frozen=True)
class Offer:
    amount: Decimal
    currency: str          # "EUR" | "USD"
    basis: str             # "net" | "gross" | "unknown"
    where: str             # which extractor found it (jsonld|meta|microdata|regex)


def _gross_or_net(context: str) -> str:
    c = context.lower()
    if any(k in c for k in ("zzgl", "exkl", "netto", "net price", "ex vat", "excl. vat", "without vat")):
        return "net"
    if any(k in c for k in ("inkl", "incl", "brutto", "mwst", "vat", "gross")):
        return "gross"
    return "unknown"


def _pn_present(html: str, pn: str) -> bool:
    """The page must actually be about this PN (PN-exact), not a near-match listing."""
    norm = re.sub(r"\s+", "", html).upper()
    return re.sub(r"\s+", "", pn).upper() in norm


def extract_offers(html: str, pn: str) -> list[Offer]:
    """Extract PN-exact price offers from a reseller page, structured-data first (most reliable).

    Order: JSON-LD Offer(s) -> og:/product: price meta -> itemprop=price microdata -> EUR-near-PN
    regex. Returns [] if the PN is not present on the page (guards against wrong-product matches).
    """
    if not _pn_present(html, pn):
        return []
    offers: list[Offer] = []

    # 1) JSON-LD Offer blocks
    for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
        try:
            data = json.loads(blk.strip())
        except (ValueError, json.JSONDecodeError):
            continue
        for node in data if isinstance(data, list) else [data]:
            for off in _jsonld_offers(node):
                offers.append(off)

    # 2) meta price tags (og:price:amount / product:price:amount + currency)
    amt = re.search(r'<meta[^>]+(?:og:price:amount|product:price:amount)["\'][^>]*content=["\']([\d.,]+)', html, re.I)
    curm = re.search(r'<meta[^>]+price:currency["\'][^>]*content=["\']([A-Z]{3})', html, re.I)
    if amt:
        pm = parse_money(amt.group(1))
        if pm:
            offers.append(Offer(pm[0], (curm.group(1) if curm else pm[1]), "unknown", "meta"))

    # 3) microdata itemprop=price
    for m in re.finditer(r'itemprop=["\']price["\'][^>]*content=["\']([\d.,]+)', html, re.I):
        pm = parse_money(m.group(1))
        if pm:
            offers.append(Offer(pm[0], pm[1], "unknown", "microdata"))

    # 4) EUR-near-PN regex fallback (only if nothing structured was found)
    if not offers:
        for m in re.finditer(r'(\d[\d. ]*,\d{2})\s*(?:€|EUR)', html):
            pm = parse_money(m.group(1) + " EUR")
            if pm:
                ctx = html[max(0, m.start() - 60): m.end() + 20]
                offers.append(Offer(pm[0], "EUR", _gross_or_net(ctx), "regex"))
    return offers


def _jsonld_offers(node: object) -> list[Offer]:
    out: list[Offer] = []
    if not isinstance(node, dict):
        return out
    # recurse into @graph / nested
    for v in node.values():
        if isinstance(v, (list, dict)):
            out += _jsonld_offers(v) if isinstance(v, dict) else [o for x in v for o in _jsonld_offers(x)]
    offer = node.get("offers") or (node if str(node.get("@type", "")).endswith("Offer") else None)
    for off in (offer if isinstance(offer, list) else [offer] if offer else []):
        if not isinstance(off, dict):
            continue
        price = off.get("price") or off.get("lowPrice")
        if price is None:
            continue
        pm = parse_money(str(price))
        if not pm:
            continue
        cur = str(off.get("priceCurrency") or pm[1] or "EUR").upper()[:3]
        spec = off.get("priceSpecification") or {}
        basis = "net" if (isinstance(spec, dict) and spec.get("valueAddedTaxIncluded") is False) else \
                ("gross" if (isinstance(spec, dict) and spec.get("valueAddedTaxIncluded") is True) else "unknown")
        out.append(Offer(pm[0], cur, basis, "jsonld"))
    return out


# --- normalization to net EUR per single unit -----------------------------------------

def to_net_eur(off: Offer, usd_eur: Decimal, *, assume_gross: bool = True) -> Decimal | None:
    """Normalize an offer to NET EUR per single unit. USD is FX-converted; gross is divided by VAT.
    An "unknown" basis is treated as gross when assume_gross (the conservative B2C default) so we
    never over-state the net price. Returns None for a non-positive amount."""
    amt = off.amount
    if amt <= 0:
        return None
    if off.currency == "USD":
        amt = amt * usd_eur
    basis = off.basis if off.basis != "unknown" else ("gross" if assume_gross else "net")
    if basis == "gross":
        amt = amt / _VAT
    return amt.quantize(_CENT, rounding=ROUND_HALF_UP)


# --- aggregation -----------------------------------------------------------------------

@dataclass(frozen=True)
class CompResult:
    sku: str
    net_eur_values: tuple[Decimal, ...]      # the kept (outlier-filtered) net EUR observations
    low: Decimal | None
    median: Decimal | None
    high: Decimal | None
    n_sources: int
    n_raw: int
    spread: Decimal | None                    # (high-low)/median, relative
    rejected: tuple[Decimal, ...] = field(default_factory=tuple)

    @property
    def grounded(self) -> bool:
        return self.median is not None and self.n_sources >= 1


def _iqr_keep(values: list[Decimal]) -> tuple[list[Decimal], list[Decimal]]:
    """Reject outliers via the 1.5*IQR rule (needs >=4 points; otherwise keep all)."""
    if len(values) < 4:
        return values, []
    s = sorted(values)
    q1 = s[len(s) // 4]
    q3 = s[(3 * len(s)) // 4]
    iqr = q3 - q1
    lo, hi = q1 - Decimal("1.5") * iqr, q3 + Decimal("1.5") * iqr
    keep = [v for v in values if lo <= v <= hi]
    drop = [v for v in values if not (lo <= v <= hi)]
    return (keep or values), (drop if keep else [])


def band_flags(net_eur: Decimal, *, floor: Decimal | None, ceiling: Decimal | None,
               n_sources: int, spread: Decimal | None, high_value_eur: Decimal,
               max_spread: Decimal = Decimal("0.6")) -> list[str]:
    """Guard rails on a resolved net price. BLOCK: = absurd, do not ship (flagged-debt instead).
    FLAG: = ships but recorded for optional operator review. Nothing is silently clamped."""
    out: list[str] = []
    if floor is not None and net_eur < floor:
        out.append(f"BLOCK:below category floor €{floor}")
    if ceiling is not None and net_eur > ceiling:
        out.append(f"BLOCK:above category ceiling €{ceiling}")
    if net_eur > high_value_eur:
        out.append(f"FLAG:high-value (>€{high_value_eur})")
    if n_sources <= 1:
        out.append("FLAG:single-source")
    if spread is not None and spread > max_spread:
        out.append(f"FLAG:wide-spread ({spread:.0%})")
    return out


def aggregate(sku: str, net_values: list[Decimal]) -> CompResult:
    """[low, median, high] over outlier-filtered net-EUR observations; positions at the MEDIAN."""
    raw = [v for v in net_values if v and v > 0]
    if not raw:
        return CompResult(sku, (), None, None, None, 0, len(net_values), None)
    keep, drop = _iqr_keep(raw)
    keep_sorted = sorted(keep)
    med = Decimal(statistics.median(keep_sorted))
    lo, hi = keep_sorted[0], keep_sorted[-1]
    spread = ((hi - lo) / med) if med > 0 else None
    return CompResult(sku, tuple(keep_sorted), lo, med.quantize(_CENT, rounding=ROUND_HALF_UP),
                      hi, len(keep_sorted), len(net_values), spread, tuple(drop))
