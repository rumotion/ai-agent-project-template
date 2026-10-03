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

The checked-in Memory Bank is the only durable, cross-model store.

- **Write durable project state to `memory-bank/*.md`.** It is committed, so
  every model and machine sees it.
- **Never write durable state to an MCP memory server.** The starter
  `memory` server persists to `.mcp/memory.json`, which is **gitignored** —
  anything stored there is invisible to the next model and lost on a fresh
  clone. Treat it as session scratch only.
- The same applies to provider-native memory (Claude auto memory, Gemini saved
  memory, Codex local memory): advisory recall, never the source of truth.

If asked to "remember" something that must survive a model switch, the answer
is a Memory Bank file. See `docs/context-memory-bridges.md`.