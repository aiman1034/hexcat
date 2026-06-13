# Completeness enumeration snapshots

Each `*.txt` here is a **verbatim capture of one official manufacturer enumeration** — one part
number per line; `#` comments and blank lines ignored; an inline `# note` or a `<TAB>`/`,`/`;`/`|`
suffix after a PN is tolerated (only the leading token is read). These are the INDEPENDENT
yardsticks `lib/completeness.py` unions into the ground-truth universe a harvest must cover.

**Grounding rule (non-negotiable, per CLAUDE.md 1000% rule):**

- A PN in a snapshot must come straight from an official Cisco list — the TMG compatibility
  matrix, an EOL/EOS bulletin, an ordering / product-family guide, or the GPL price list.
- **Never** fabricate or pattern-generate a PN (e.g. do not synthesize `SFP-10G-*` variants).
  If a list isn't gathered yet, leave its file absent or empty — the reconciler simply does not
  count an empty source toward the completeness verdict (an empty universe is never "complete").
- EOL/legacy parts belong in these snapshots; EOL is an informational flag, never a reason to
  omit a real transceiver PN.

Files (referenced by `config/enumerations/transceivers.yaml`):

| file                          | source kind            |
|-------------------------------|------------------------|
| `cisco_tmg_matrix.txt`        | compatibility_matrix   |
| `cisco_eol_bulletins.txt`     | eol_eos_bulletins      |
| `cisco_ordering_guide.txt`    | ordering_guide         |
| `cisco_gpl.txt`               | price_list             |
