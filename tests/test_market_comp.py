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

def test_seller_tiers_authorized_vs_secondary_vs_excluded():
    # Tier 1: German authorized
    assert M.seller_tier("https://www.bechtle.com/de/shop/cisco-sfp-10g-sr-123") == "authorized"
    assert M.seller_tier("https://shop.jacob.de/produkte/cisco-sfp-10g-sr") == "authorized"
    # Tier 2: legit genuine-new SECONDARY market (anchors legacy/EOL parts the authorized channel lacks)
    assert M.seller_tier("https://www.router-switch.com/xenpak-10gb-lr.html") == "secondary"
    assert M.seller_tier("https://www.ebay.de/itm/cisco-dwdm-gbic-30-33") == "secondary"
    # Excluded at the seller level: compatible / third-party-optic vendors
    assert M.seller_tier("https://www.fs.com/products/sfp-10g-sr.html") is None
    assert M.seller_tier("https://flexoptix.net/en/sfp-10g-sr") is None


def test_listing_condition_filters_refurb_used_compatible_keeps_new():
    assert M.listing_condition("<h1>Cisco SFP-10G-SR brandneu, versiegelt</h1>", "SFP-10G-SR") == "new"
    assert M.listing_condition("<h1>Cisco XENPAK-10GB-LR refurbished</h1>", "XENPAK-10GB-LR") == "refurbished"
    assert M.listing_condition("<h1>SFP-10G-SR compatible transceiver</h1>", "SFP-10G-SR") == "compatible"
    assert M.listing_condition('{"itemCondition":"https://schema.org/UsedCondition"} GLC-SX-MM', "GLC-SX-MM") == "used"


def test_jsonld_per_offer_item_condition():
    html = ('XENPAK-10GB-LR <script type="application/ld+json">{"@type":"Product","sku":"XENPAK-10GB-LR",'
            '"offers":{"@type":"Offer","price":"450.00","priceCurrency":"EUR",'
            '"itemCondition":"https://schema.org/RefurbishedCondition"}}</script>')
    offers = M.extract_offers(html, "XENPAK-10GB-LR")
    assert offers and offers[0].condition == "refurbished"


def test_related_product_offer_does_not_leak():
    # an X2 page whose carousel lists a neighbouring XFP as a bare Offer must NOT price the X2
    html = ('DWDM-X2-30.33 <script type="application/ld+json">'
            '[{"@type":"Product","sku":"DWDM-X2-30.33","offers":{"@type":"Offer","price":"3200","priceCurrency":"USD"}},'
            '{"@type":"Offer","price":"9476","priceCurrency":"USD"}]</script>')
    offers = M.extract_offers(html, "DWDM-X2-30.33")
    amounts = {str(o.amount) for o in offers}
    assert "3200" in amounts and "9476" not in amounts   # only the X2's own offer


def test_family_key_groups_channel_variants():
    assert M.family_key("DWDM-GBIC-30.33") == "DWDM-GBIC"
    assert M.family_key("DWDM-XENPAK-60.61") == "DWDM-XENPAK"
    assert M.family_key("CWDM-SFP-1470") == "CWDM-SFP"
    assert M.family_key("DWDM-SFP10G-C") == "DWDM-SFP10G"        # tunable channel member
    assert M.family_key("SFP-10G-SR") is None                    # not a channel family
    assert M.family_key("QSFP-40G-SR4") is None


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
