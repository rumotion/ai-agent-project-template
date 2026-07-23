---
name: delegation-coordinator
description: Coordinates task delegation across Gemini, Codex, Claude, and subagents using the portable subagent contract.
---

# Delegation Coordinator

Coordinates task breakdown, path ownership, worker dispatch, and evidence-grounded result validation across multi-agent sessions.

## Quick Start

1. Define worker tasks using the Task Envelope schema in `docs/subagent-contract.md`.
2. Assign disjoint `owned_paths` to each worker to prevent write collisions.
3. Require workers to return the standard Result Envelope containing verification exit codes and diff summaries.
4. Run parent verification checks before marking delegated tasks completed.

## Delegation Rules

- **Single Writer Rule**: Ensure no two concurrent subagents own the same target file path for editing.
- **Read-Only Workers**: Set `read_only: true` for audit, critic, or research workers.
- **Deterministic Verification**: Verify subagent results with explicit build, test, or lint commands before accepting the result.
- **Conflict Handling**: If a worker returns `status: blocked` or fails verification twice, halt and escalate to parent/Codex review.
