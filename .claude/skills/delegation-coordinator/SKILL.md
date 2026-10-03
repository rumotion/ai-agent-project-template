---
name: delegation-coordinator
description: Coordinates task delegation across Gemini, Codex, Claude, and subagents using the portable subagent contract.
---

# Delegation Coordinator

Coordinates task breakdown, path ownership, worker dispatch, and evidence-grounded result validation across multi-agent sessions.

## Quick Start

1. Define worker tasks using the JSON task envelope validated by `schemas/subagent-task.schema.json` (rules in `docs/subagent-contract.md`).
2. Assign disjoint `owned_paths` to each worker to prevent write collisions; list hard exclusions in `forbidden_paths`.
3. Dispatch the envelope only — never forward the parent transcript, other tasks, or secret-bearing history.
4. Require workers to return the result envelope validated by `schemas/subagent-result.schema.json`, capped by `max_output_tokens`.
5. Run parent verification checks and diff the worktree against `owned_paths` before marking delegated tasks completed.

## Delegation Rules

- **Single Writer Rule**: Ensure no two concurrent subagents own the same target file path for editing.
- **Read-Only Workers**: Set `read_only: true` for audit, critic, or research workers.
- **Envelope-Only Context**: Workers receive only their JSON task envelope; mask secrets before dispatch.
- **Deterministic Verification**: Verify subagent results with explicit build, test, or lint commands before accepting the result; reject every write outside `owned_paths` or within `forbidden_paths`, including reported writes. Compare content hashes for already-dirty files, not just status.
- **Memory Bank Serialization**: Only the parent writes `memory-bank/*`; merge worker-reported facts once.
- **Conflict Handling**: If a worker returns `status: blocked` or fails verification twice, halt and escalate to parent/Codex review.

Validate paired results with `scripts/validate-schemas.py --schema schemas/subagent-result.schema.json --instance result.json --task task.json --root .`. Read-only tasks use `owned_paths: []`. Serialized-byte limits are independent of token telemetry; declarations do not create a sandbox or lease system.
