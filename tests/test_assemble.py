from __future__ import annotations

from hexcat import constants as C


def test_bundle_has_seven_files(good_bundle):
    _, manifest = good_bundle
    roles = {f.role for f in manifest.files}
    assert roles == {"main", "attributes", "platformflag", "prices",
                     "condition", "faq", "verification"}


def test_row_counts(good_bundle):
    _, manifest = good_bundle
    assert manifest.by_role("main").rows == 2
    assert manifest.by_role("platformflag").rows == 2
    assert manifest.by_role("prices").rows == 2
    assert manifest.by_role("condition").rows == 2
    assert manifest.by_role("faq").rows == 2
    # attributes & verification: one row per non-empty attribute value
    assert manifest.by_role("attributes").rows == manifest.by_role("verification").rows
    assert manifest.by_role("attributes").rows > 2


def test_filenames_match_contract(good_bundle):
    d, manifest = good_bundle
    names = {f.path.name for f in manifest.files}
    assert "Hexwaren_Transceivers_Main.csv" in names
    assert "Hexwaren_Transceivers_Attributes.csv" in names
    assert "Hexwaren_Transceivers_PlatformFlag.csv" in names
    assert "Hexwaren_Transceivers_Prices.csv" in names
    assert "Hexwaren_Condition_Cisco_Transceivers.csv" in names
    assert "Hexwaren_FAQ_Cisco_Transceivers.csv" in names
    assert "Verification_Log_Cisco_Transceivers.csv" in names


def test_main_bom_and_delimiter(good_bundle):
    d, manifest = good_bundle
    raw = manifest.by_role("main").path.read_bytes()
    assert raw[:3] == b"\xef\xbb\xbf"
    header = raw[3:].decode("utf-8").split("\r\n")[0]
    assert header.split(";") == list(C.MAIN_COLUMNS)


def test_prices_has_no_bom(good_bundle):
    _, manifest = good_bundle
    raw = manifest.by_role("prices").path.read_bytes()
    assert raw[:3] != b"\xef\xbb\xbf"
