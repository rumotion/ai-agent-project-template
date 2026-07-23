# Portable Subagent Contract

This document defines the portable task delegation envelope and result schema shared across Gemini, Codex, Claude, Cline, Roo Code, Cursor, and other agent platforms.

## Core Rules

1. **Exclusive Path Ownership**: Only one worker agent may own a given file path for writing at any time.
2. **Read-Only Scope**: Workers marked `read_only: true` must never modify files or run mutating commands.
3. **Preservation Guarantee**: Worker agents must never revert, clean, or overwrite unrelated user work or dirty tree states.
4. **Evidence-Based Output**: Results must present empirical evidence (exit codes, test outputs, file diffs), never hidden or ungrounded model reasoning.
5. **Conflict Resolution**: If a worker encounters missing authority, unresolvable file conflicts, or ambiguous ownership, it must halt and return `status: blocked`.
6. **Parent Validation**: Parent / coordinator agents must independently run verification commands before accepting a worker result as `completed`.

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

## Task Envelope Schema

When delegating work to a subagent or secondary model, format the task payload with the following fields:

```text
task_id: "<unique-task-identifier>"
objective: "<concise description of the task>"
scope: "<component, phase, or boundaries of work>"
owned_paths:
  - "<path/to/file1>"
  - "<path/to/dir/*>"
read_only: false | true
inputs:
  - "<path/to/input1>"
constraints:
  - "<constraint 1>"
  - "<constraint 2>"
expected_output: "<description of expected artifact or behavior>"
verification:
  - "<command to verify task output>"
budget:
  max_turns: <integer>
  max_repairs: <integer>
```

---

## Result Envelope Schema

When a subagent completes, pauses, or blocks on a task, it must return a result matching this schema:

```text
task_id: "<unique-task-identifier>"
status: completed | partial | blocked
summary: "<one-paragraph summary of what was accomplished>"
files_changed:
  - path: "<path/to/modified_file>"
    action: added | modified | deleted
verification_run:
  - command: "<command line>"
    exit_code: <int>
    output_summary: "<key stdout/stderr snippet>"
findings:
  - severity: high | medium | low
    location: "<path:line>"
    evidence: "<observable fact>"
    required_fix: "<concrete fix>"
risks:
  - "<identified risk or regression potential>"
deferred:
  - "<item deferred and why>"
next_action: "<recommended next step>"
```
