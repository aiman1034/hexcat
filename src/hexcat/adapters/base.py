"""BrandAdapter interface — the per-vendor seam for Stage 1 (PHASE 4, stub only).

Stage 1 discovery/mining differs per vendor. This interface keeps that logic out of the
deterministic Stage 3 core: Stage 3 never hardcodes brand behaviour, and Phase 4 onboards
a new brand by adding one adapter + its taxonomy map (config), not by editing the engine.

Nothing here is implemented this session. The signatures fix the contract Phases 3-4 fill.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BrandAdapter(ABC):
    """Per-vendor Stage 1 behaviour. One concrete subclass per brand (Phase 4)."""

    #: Vendor key as used in config/rules.yaml `vendors` (e.g. "Cisco").
    vendor: str

    @abstractmethod
    def discover_datasheets(self, category: str) -> list[dict]:
        """Find this brand's datasheets for a category.

        Returns source descriptors (e.g. {"group", "datasheet", "url"}) destined for the
        ledger's Quellen-Tracker sheet. Phase 4.
        """
        raise NotImplementedError

    @abstractmethod
    def mine_part_numbers(self, datasheet: dict) -> list[str]:
        """Extract raw part numbers from one fetched/cached datasheet. Phase 3/4."""
        raise NotImplementedError

    @abstractmethod
    def hygiene_rules(self) -> list:
        """Per-vendor part-number cleaning rules (strip feed-id suffixes, fix typos,
        normalize). Feeds the ledger's PN-Korrekturen sheet. Phase 3/4."""
        raise NotImplementedError

    @abstractmethod
    def taxonomy_map(self, category: str) -> dict[str, str]:
        """Map this vendor's naming into the one canonical Hexwaren taxonomy
        (e.g. {raw_form_factor -> Kategorie Ebene 3}). Phase 3/4."""
        raise NotImplementedError
