"""Phase 2: the $0 content flow (no paid API, no network).

HexCat never makes a paid LLM API call. The German prose is authored by Claude Code
in-session. This package turns a facts-only *skeleton* intake CSV into a fill-in
*worksheet* (`write_worksheet`), reads the authored worksheet back (`read_worksheet`),
merges it with the skeleton facts, and writes a *draft* intake CSV (`write_draft`). The
draft is then gated by `hexcat validate` (same `content_checks` predicates as `build`)
and assembled by the deterministic, offline `hexcat build`.

This package re-exports a flat public API so callers use `from hexcat.generate import …`.
"""
from __future__ import annotations

from .engine import (
    CONTENT_COLUMNS,
    FLAG_PREFIX,
    GenerateError,
    SkuFacts,
    merge_fields,
    read_skeleton,
    soft_spec_flags,
    write_draft,
    write_skeleton_template,
)
from .prompt import GUIDE_VERSION, build_voice_guide, facts_block
from .worksheet import read_worksheet, write_worksheet

__all__ = [
    "CONTENT_COLUMNS", "FLAG_PREFIX", "GenerateError", "SkuFacts",
    "merge_fields", "read_skeleton", "soft_spec_flags", "write_draft",
    "write_skeleton_template",
    "GUIDE_VERSION", "build_voice_guide", "facts_block",
    "read_worksheet", "write_worksheet",
]
