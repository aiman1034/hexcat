HEXWAREN — TRANSCEIVER CATEGORY — FINAL OUTPUT
==============================================

To fix the live shop now -> import the 2 files in 1_IMPORT_THESE\ via Ameise:
attributes first, DOM second. The folders in 2_full_catalog_by_brand\ are the
complete corrected catalog build -- only for a full rebuild, not this fix.

--------------------------------------------------------------------------
1_IMPORT_THESE\   (the ONLY files to run through Ameise for this fix)
    IMPORT_attributes_324overlap.csv    657 rows   -> import FIRST
    IMPORT_dom_324overlap.csv            74 rows   -> import SECOND

    These two delta files correct the live shop's attributes for the 324
    products that exist in both the live shop and the build. Attributes
    first, DOM second. Format: UTF-8 with BOM, ';' delimiter, Windows CRLF,
    attribute type = Wertliste. Pre-create any new Formfaktor values
    (DSFP, SFP-DD, QSFP-DD800, QSFP112) or enable "neue Werte uebernehmen".

2_full_catalog_by_brand\   (reference / full rebuild ONLY -- NOT this fix)
    One folder per brand (13), each with the 7 transceiver CSVs:
    Main, Attributes, PlatformFlag, Prices, Condition, FAQ, Verification_Log.
    This is the complete corrected catalog build.

    Do NOT import these folders for the current attribute fix.
    WARNING: the Prices CSVs are the 0,00 Phase-1 default -- never let them
    overwrite the live, market-anchored shop prices.
--------------------------------------------------------------------------
