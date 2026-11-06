---
name: docs-memory-maintainer
description: Updates project documentation and Memory Bank files after meaningful changes. Use after features, refactors, setup changes, architecture decisions, or user requests to update memory.
---

# Docs and Memory Maintainer Skill

Read:

1. `AGENTS.md`
2. `memory-bank/00-index.md`
3. Relevant Memory Bank files
4. Relevant docs in `docs/`

## Update policy

Update only what changed.

Prioritize:

- `memory-bank/activeContext.md`
- `memory-bank/progress.md`
- `memory-bank/decisions.md`
- `memory-bank/systemPatterns.md`
- `memory-bank/techContext.md`

Keep entries concise.

## Where memory goes

Reviewed Memory Bank records are the portable source of project facts. Private
operational checkpoints have a separate local persistence contract.

- **Write durable decisions through `scripts/ctx.py record`.** Follow
  `workflows/update-memory-bank.md`, choose global/task/archive scope and verify
  the returned record ID, hash and inclusion state. Prose files link to records;
  prose alone does not enter the compiled startup packet. Commit only reviewed
  material suitable for this repository. A commit is not automatic transport.
- **Never write durable state to an MCP memory server.** The starter
  `memory` server persists to `.mcp/memory.json`, which is **gitignored** —
  anything stored there is invisible to the next model and lost on a fresh
  clone. Treat it as session scratch only.
- The same applies to provider-native memory (Claude auto memory, Gemini saved
  memory, Codex local memory): advisory recall, never the source of truth.

For a model switch, persist reviewed facts as records and use a private local
checkpoint for operational state. See `docs/context-memory-bridges.md` and
`docs/continuity.md`. Raw feedback and private receipts stay outside public Git.
