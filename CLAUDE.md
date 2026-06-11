# HexCat — session instructions for Claude Code

## Cross-session memory (ruflo)

This project uses **ruflo** as a local, cross-session memory layer so context survives
between sessions. It is registered as the `ruflo` MCP server in `.mcp.json`. The memory
store is fully local (SQLite + on-device ONNX embeddings at `.swarm/memory.db`) — **$0,
no API key, no network**. Project state lives under the `hexcat/*` key namespace.

### At the START of every session
Recall the project context before doing anything else:
- `memory_search` for `"hexcat"`, or
- `memory_retrieve` the keys: `hexcat/overview`, `hexcat/hard-rules`, `hexcat/phases`,
  `hexcat/pipeline-stages`, `hexcat/next-step`, `hexcat/ruflo-memory-usage`.

(If the MCP tools are unavailable, the CLI works in-session:
`npx ruflo@3.10.42 memory retrieve -k hexcat/next-step`.)

### At the END of every session (when state changed)
Store an updated snapshot so the next session picks up where you left off — e.g. update
`hexcat/phases` (what's built), `hexcat/next-step` (what's next), or add a new `hexcat/*`
key. Keep values to a single line.

## MEMORY ONLY — do not use orchestration
Use **only** the `memory_*` tools (`memory_store`, `memory_retrieve`, `memory_search`,
`memory_list`). **Never** invoke ruflo's swarm/agent orchestration tools
(`swarm_*`, `agent_*`, `managed_agent_*`, `wasm_agent_*`, `daa_*`). They add
nondeterminism and can consume Max usage. ruflo is here for memory and nothing else.

## HexCat hard rules (do not violate)
- **ZERO-DOLLAR:** the tool never makes a paid LLM API call. Ever.
- German prose is written by **Claude in-session under the Max subscription**, not by the
  tool and not via any paid API.
- Deterministic core; **flag, don't emit** on uncertainty; **no DB, files-only**; no
  over-engineering. This is environment/memory setup only — keep the hexcat tool code
  unchanged unless explicitly asked.
