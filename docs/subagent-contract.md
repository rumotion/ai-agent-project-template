# Portable Subagent Contract

This document defines the portable task delegation envelope and result schema shared across Gemini, Codex, Claude, Cline, Roo Code, Cursor, and other agent platforms.

## Core Rules

1. **Exclusive Path Ownership**: Only one worker agent may own a given file path for writing at any time.
2. **Read-Only Scope**: Workers marked `read_only: true` must never modify files or run mutating commands.
3. **Preservation Guarantee**: Worker agents must never revert, clean, or overwrite unrelated user work or dirty tree states.
4. **Evidence-Based Output**: Results must present empirical evidence (exit codes, test outputs, file diffs), never hidden or ungrounded model reasoning.
5. **Conflict Resolution**: If a worker encounters missing authority, unresolvable file conflicts, or ambiguous ownership, it must halt and return `status: blocked`.
6. **Parent Validation**: Parent / coordinator agents must independently run verification commands before accepting a worker result as `completed`.
7. **Envelope-Only Context**: Workers receive exactly the JSON task envelope (`schemas/subagent-task.schema.json`) — never the parent's transcript, other tasks, or secret-bearing history. The launcher must isolate context at dispatch time; this repository validates the declaration but does not supply that launcher.
8. **Write-Scope Audit**: Before accepting a result, the parent compares content hashes and file inventories before/after, including already-dirty files, deletions and untracked files. Reject every change outside `owned_paths` or within `forbidden_paths`, even when reported in `files_changed`. Status alone cannot detect edits to an already-dirty file.
9. **Memory Bank Serialization**: Only the parent writes `memory-bank/*`. Workers report facts in their result envelope; the parent merges them once, preventing parallel handoff clobbering.
10. **Report Caps**: `summary` <= 120 words; `findings` <= 5; every text field is schema-capped. Serialized envelopes are capped at 64,000 UTF-8 bytes, optionally lower through `max_result_bytes`. A token cap needs trusted provider telemetry; `tokens_used` is a worker report and cannot prove compliance.
11. **Machine Validation**: Both envelopes are JSON Schema artifacts validated by `python scripts/validate-schemas.py` (run in CI); free-text envelopes are non-conforming.

---

## Portable Reviewer Profile

The template ships exactly one native specialist role: the read-only reviewer.
Its canonical behavior and result shape live in `docs/reviewer-role.md`;
`.gemini/agents/reviewer.md`, `.codex/agents/reviewer.toml`, and
`.claude/agents/reviewer.md` are thin discovery adapters.

The reviewer receives a frozen artifact or diff, never owns write paths, and
returns evidence-backed findings plus an `accept|revise` verdict. Native
tool/sandbox restrictions are defense in depth, not proof of behavior. The
parent must compare the worktree before and after review and run independent
verification.

---

## Machine-Validated Envelopes (v2)

Both envelopes are JSON documents with machine-checkable schemas:

- Task envelope: `schemas/subagent-task.schema.json` — adds `forbidden_paths`, `tool_allowlist`, an `isolation` block (envelope-only context policy, secret masking, parent-only Memory Bank writes), and a `budget` block (`max_turns`, `max_repairs`, `max_output_tokens`).
- Result envelope: `schemas/subagent-result.schema.json` — adds schema-capped text fields and `tokens_used` so the parent can aggregate fleet cost.

Validated examples live in `schemas/examples/`. Validate any envelope with:

```bash
python scripts/validate-schemas.py --schema schemas/subagent-task.schema.json --instance my-task.json
```

The old free-text envelopes are **non-conforming**; free text cannot be validated in CI, invites per-platform drift, and has no caps against parent-context flooding.

## Semantic acceptance gate

Read-only tasks have `owned_paths: []`; writable tasks need ownership. Paths are
relative, use forward slashes, and reject traversal, drives, control characters,
and resolved symlink escapes. Scope matching is case-insensitive across hosts;
`forbidden_paths` wins. Memory Bank writes belong to the parent. Concrete inputs
must exist when `--root` is supplied. Results must match the task ID, obey scope,
and include successful verification when claiming completion.

```bash
python scripts/validate-schemas.py --schema schemas/subagent-result.schema.json --instance result.json --task task.json --root . --output-tokens 123 --require-usage
```

`--output-tokens` must come from trusted telemetry. `--require-usage` refuses a
missing count. Without paired validation, shape alone does not establish scope.
The validator accepts a closed schema keyword dialect and rejects unsupported
keywords. Byte caps and schema checks do not enforce tool allowlists, exclusive
leases, process isolation, or actual verification execution. Parents must run
verification independently. A supervisor-owned transaction ledger remains a
future design in `docs/audits/second-order/report.md`, not an implemented runtime.
