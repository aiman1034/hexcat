HEXWAREN — TRANSCEIVER CATEGORY — FINAL OUTPUT
==============================================

Two separate jobs. Do not mix them.

==========================================================================
JOB 1 — FIX THE LIVE SHOP (the 324 products already online)
==========================================================================
Import the 2 files in 1_IMPORT_THESE\ via Ameise, in this order:

    1_IMPORT_THESE\
        IMPORT_attributes_324overlap.csv    657 rows   -> import FIRST
        IMPORT_dom_324overlap.csv            74 rows   -> import SECOND

These are attribute-only deltas. They do NOT touch prices, names, or images.
Format: UTF-8 with BOM, ';' delimiter, Windows CRLF, attribute type = Wertliste.
Pre-create any new Formfaktor values (DSFP, SFP-DD, QSFP-DD800, QSFP112) or
enable "neue Werte uebernehmen".

==========================================================================
JOB 2 — ADD THE NEW PRODUCTS (2_full_catalog_by_brand\)
==========================================================================
2_full_catalog_by_brand\<brand>\ now holds ONLY genuinely-new products
(every Artikelnummer already in the live shop was removed). One folder per
brand, the 7 transceiver CSVs each.

** PRICES: the Prices CSVs are the 0,00 Phase-1 PLACEHOLDER — NOT real prices. **
When importing the new products, run ONLY these four files per brand and
SKIP the Prices step entirely:

        Main  +  Attributes  +  PlatformFlag  +  Condition

Do NOT import Hexwaren_*_Prices.csv. Importing 0,00 would publish the new
products at price zero. Real prices come from a separate pricing pass.
(Verification_Log and FAQ are reference/audit files, not import files.)

Cross-brand Artikelnummer collisions were made unique by appending the brand
(QSFP-100G-LR4-ARISTA / -JUNIPER, ...); HAN keeps the bare MSA part number.
See COLLISION_RESOLUTION.txt.

==========================================================================
PENDING — NOT done in this build (do not assume these are finished)
==========================================================================
* Real pricing for every product (the 0,00 placeholders above).
* Datasheet verification of the 7 non-gold brands (Dell, Extreme, Juniper,
  Lenovo, NVIDIA, Supermicro, Ubiquiti) — content is built but not yet
  independently spec-verified.
* The 6 Dell collision entries flagged in COLLISION_RESOLUTION.txt
  (confirm Dell genuinely lists those MPNs, or remove).
* The 221 live products that exist in the shop but were never built.
==========================================================================
