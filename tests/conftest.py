"""Shared fixtures: load config, build good records from the example, assemble bundles."""
from __future__ import annotations

from pathlib import Path

import pytest

from hexcat.assemble import assemble_bundle
from hexcat.config import load_rules, load_weights
from hexcat.intake import read_intake

REPO = Path(__file__).resolve().parents[1]
EXAMPLE_INTAKE = REPO / "examples" / "Cisco_SampleBatch_intake.csv"


@pytest.fixture(scope="session")
def rules():
    return load_rules()


@pytest.fixture(scope="session")
def weights():
    return load_weights()


@pytest.fixture
def good_records(rules, weights):
    return read_intake(EXAMPLE_INTAKE, rules, weights)


@pytest.fixture
def good_bundle(tmp_path, good_records, rules):
    """Assemble the example into tmp_path and return (dir, manifest)."""
    manifest = assemble_bundle(
        good_records, rules,
        batch="Cisco_SampleBatch", category="Transceivers",
        out_dir=tmp_path, build_time="2026-06-11T00:00:00Z",
    )
    return tmp_path, manifest


def read_bytes_text(path: Path) -> str:
    """Decode a file preserving BOM/CRLF for targeted corruption in tests."""
    return path.read_bytes().decode("utf-8")


def write_text_bytes(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))
