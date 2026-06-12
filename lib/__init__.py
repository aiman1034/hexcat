"""HexCat universal harvesting layer — category-agnostic, local, $0.

Three pieces, built once and reused by every future product category unchanged:

  * ``local_fetch``    — the universal datasheet fetcher (HTTP -> headless browser
                         escalation ladder, run from the local PC's residential/business
                         IP to clear hosted-WebFetch bot blocks). Knows nothing about
                         transceivers — it fetches whatever URL it is handed.
  * ``deferred_queue`` — a persistent, cross-session retry queue. A blocked page is never
                         missed, fabricated, or silently skipped: its exact URL is queued
                         with progressive backoff and circled back to until it yields (or
                         a hard 404/410 records it as confirmed-gone).
  * ``harvest``        — a category-agnostic harvester. Per-category inputs (discovery
                         seeds, per-family search terms, link patterns, allowed domains)
                         are pure CONFIG under ``config/sources/<category>.yaml``; the
                         discover + crawl + fetch machinery is universal. Adding a new
                         category = a new config file, zero code changes.
"""
