"""Brand-adapter seam — Stage 1 per-vendor logic (PHASE 4).

See base.py for the BrandAdapter interface. Onboarding brand #2-18 should be mostly
config (an adapter + a taxonomy map), not engine changes.
"""

from .base import BrandAdapter

__all__ = ["BrandAdapter"]
