"""Lock the PURE market-comp core (lib/market_comp.py): authorized new-sealed sellers only,
robust money parsing, PN-exact structured-data extraction, net-EUR-per-unit normalization, and
median positioning with outlier rejection. All offline — no network, no live pages."""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import market_comp as M  # noqa: E402

FX = Decimal("0.863")  # USD->EUR, matches the dated rate in config/market_prices/list_prices.yaml


# ---- seller allow / deny --------------------------------------------------------------

def test_authorized_new_sealed_sellers_pass():
    assert M.seller_ok("https://www.bechtle.com/de/shop/cisco-sfp-10g-sr-123")
    assert M.seller_ok("https://www.senetic.de/product/SFP-10G-SR")
    assert M.seller_ok("https://shop.jacob.de/produkte/cisco-sfp-10g-sr")


def test_refurb_compatible_graymarket_sellers_excluded():
    assert not M.seller_ok("https://www.fs.com/products/sfp-10g-sr.html")        # compatible optics
    assert not M.seller_ok("https://www.it-planet.com/sfp-10g-sr")               # gray/used
    assert not M.seller_ok("https://www.ebay.de/itm/cisco-sfp-10g-sr")           # marketplace
    assert not M.seller_ok("https://flexoptix.net/en/sfp-10g-sr")                # compatible
    assert not M.seller_ok("https://www.router-switch.com/sfp-10g-sr-p-123.html")  # new+refurb gray
    assert not M.seller_ok("https://some-random-shop.xyz/sfp-10g-sr")            # not authorized


# ---- money parsing --------------------------------------------------------------------

def test_parse_money_german_and_us_grouping_and_currency():
    assert M.parse_money("1.234,56 €") == (Decimal("1234.56"), "EUR")
    assert M.parse_money("$1,234.56") == (Decimal("1234.56"), "USD")
    assert M.parse_money("120,50 EUR") == (Decimal("120.50"), "EUR")
    assert M.parse_money("89.00 USD") == (Decimal("89.00"), "USD")
    assert M.parse_money("nonsense") is None


# ---- PN-exact structured extraction ---------------------------------------------------

def test_jsonld_offer_extracted_and_currency_kept():
    html = """<html><body>Cisco SFP-10G-SR module
      <script type="application/ld+json">
      {"@type":"Product","sku":"SFP-10G-SR",
       "offers":{"@type":"Offer","price":"129.00","priceCurrency":"EUR",
                 "priceSpecification":{"valueAddedTaxIncluded":false}}}
      </script></body></html>"""
    offers = M.extract_offers(html, "SFP-10G-SR")
    assert any(o.where == "jsonld" and o.amount == Decimal("129.00")
               and o.currency == "EUR" and o.basis == "net" for o in offers)


def test_pn_absent_yields_no_offers():
    html = '<script type="application/ld+json">{"@type":"Offer","price":"99.00"}</script>'
    assert M.extract_offers(html, "SFP-10G-SR") == []   # wrong product -> nothing


def test_regex_fallback_reads_eur_near_pn_with_basis():
    html = "<p>Cisco GLC-SX-MM</p><span>Preis: 45,90 € inkl. MwSt</span>"
    offers = M.extract_offers(html, "GLC-SX-MM")
    assert offers and offers[0].currency == "EUR"
    assert offers[0].basis == "gross"   # "inkl. MwSt" detected


# ---- normalization: USD FX, gross->net, per unit --------------------------------------

def test_to_net_eur_usd_is_fx_converted():
    off = M.Offer(Decimal("100.00"), "USD", "net", "jsonld")
    assert M.to_net_eur(off, FX) == Decimal("86.30")


def test_to_net_eur_gross_strips_vat():
    off = M.Offer(Decimal("119.00"), "EUR", "gross", "jsonld")
    assert M.to_net_eur(off, FX) == Decimal("100.00")


def test_unknown_basis_treated_as_gross_conservatively():
    off = M.Offer(Decimal("119.00"), "EUR", "unknown", "meta")
    assert M.to_net_eur(off, FX, assume_gross=True) == Decimal("100.00")


# ---- aggregation: median positioning + outlier rejection ------------------------------

def test_aggregate_positions_at_median():
    r = M.aggregate("X", [Decimal("100"), Decimal("110"), Decimal("130")])
    assert r.median == Decimal("110.00")
    assert r.low == Decimal("100") and r.high == Decimal("130")
    assert r.n_sources == 3 and r.grounded


def test_aggregate_rejects_outlier():
    # one absurd value among tight cluster -> rejected by the 1.5*IQR rule
    vals = [Decimal("100"), Decimal("105"), Decimal("110"), Decimal("115"), Decimal("9000")]
    r = M.aggregate("X", vals)
    assert Decimal("9000") in r.rejected
    assert r.high <= Decimal("115")


def test_aggregate_empty_is_not_grounded():
    r = M.aggregate("X", [])
    assert not r.grounded and r.median is None


# ---- guard rails ----------------------------------------------------------------------

def test_band_guard_blocks_below_floor_and_above_ceiling():
    lo = M.band_flags(Decimal("2"), floor=Decimal("8"), ceiling=Decimal("2000"),
                      n_sources=3, spread=Decimal("0.1"), high_value_eur=Decimal("1500"))
    assert any(f.startswith("BLOCK:below") for f in lo)
    hi = M.band_flags(Decimal("90000"), floor=Decimal("8"), ceiling=Decimal("2000"),
                      n_sources=3, spread=Decimal("0.1"), high_value_eur=Decimal("1500"))
    assert any(f.startswith("BLOCK:above") for f in hi)


def test_band_guard_flags_high_value_single_source_and_wide_spread():
    flags = M.band_flags(Decimal("5000"), floor=Decimal("100"), ceiling=Decimal("30000"),
                         n_sources=1, spread=Decimal("0.9"), high_value_eur=Decimal("1500"))
    assert any("high-value" in f for f in flags)
    assert any("single-source" in f for f in flags)
    assert any("wide-spread" in f for f in flags)
    assert not any(f.startswith("BLOCK") for f in flags)   # all advisory, ships
