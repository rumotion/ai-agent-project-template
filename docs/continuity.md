# Local continuity and manual recovery

The stdlib-only `scripts/continuity.py` inspects project context and creates
private local checkpoints. It performs no model/network calls, starts no
workers, activates no quota pacing and changes no client/global settings.

## Inspect first

```powershell
python scripts/continuity.py doctor --client codex --mode legacy
python scripts/continuity.py doctor --client claude --mode fresh
python scripts/continuity.py doctor --client codex --mode resume
```

Put `--root PATH` before the command to inspect a different project. Modes:

- `legacy` (default): validates the available projection and explicitly reports
  `degraded`; a prose handoff is not a validated resume receipt. Read and
  reconcile the handoff and repository evidence manually before dependent edits.
- `fresh`: explicitly establishes a new task without a prior checkpoint. A
  missing handoff is allowed; an existing malformed source is rejected.
- `resume`: requires a valid private receipt for the same project, unchanged
  Git state and identical observed source/input fingerprints.

`ready` means the selected **local** check passed. `native_delivery` remains
`unknown`; neither a compiler nor a checkpoint proves that a model consumed the
context. The observed model and effort remain null without trusted runtime
telemetry. `blocked` exits 1; `ready`/`degraded` exit 0, so callers must also
inspect `status` before claiming a healthy resume.

## Checkpoint after meaningful progress

First save reviewed decisions and next actions in project memory, then:

```powershell
python scripts/continuity.py checkpoint --task-id service-fix --input src/service.py --client codex
```

The handoff must have nonempty scalar `status`, `task` and `next_action`.
Checkpointing validates the projection and records its sources plus up to 64
explicit input files. It requires a dedicated Git worktree. Inputs must be
relative regular files within that worktree; traversal, linked paths, Git
metadata and common secret paths are rejected. Context sources are capped at
16,384 bytes each; explicit application inputs at 1 MiB each. Add only relevant
files, never credentials. Fingerprints cover file bytes, including dirty data.

Default state lives under the user's private `.agent-continuity` directory,
keyed by a hash of the canonical project path. `--receipt PATH` can choose an
external private file. Storage inside the project and linked storage paths are
refused. A commit alone does not transfer state to another computer. Receipts
contain no prompts, source bodies or absolute project path, but local metadata
can still be private. Do not commit them.

The receipt schema is `schemas/continuity-receipt.schema.json`; runtime validation
also checks timestamp, scope and path semantics. A writer uses an exclusive
lock, a temporary file, fsync and atomic replacement. A failed write preserves
the previous receipt. A stale lock is never auto-removed: reconcile the actual
writer before removing it. This is cooperative single-writer checkpointing,
not authenticated identity or hostile-process containment.

## Recover a mismatch

1. Inspect `doctor` issues; it redacts raw exception text and private paths.
2. Read the handoff and applicable records, inspect the actual branch and files,
   and determine whether prior verification evidence still applies.
3. Preserve unfinished work. Update project memory only after reconciling facts.
4. Create a new checkpoint and re-run resume inspection. Do not refresh a receipt
   merely to hide unexplained differences.

No timeout based solely on wall-clock age invalidates unchanged state. Changed
HEAD/branch is deliberately conservative and requires reconciliation even for
an unrelated commit. A checkpoint covers named inputs and memory, not every
external service, process or unlisted file. It is not an acceptance verdict or
permission to spend, deploy, transmit data or expand scope.

## Native startup

Claude SessionStart injects the bounded compiler projection with an explicit
continuity limitation. Unexpected hook exceptions now emit `continuity_unavailable`
without raw details; the hook remains best-effort and exits zero. Unsupported
clients retain the manual path. The unverified PreCompact mapping has been
removed from active Claude configuration. The old script event remains a
compatibility notice only; it does not save state and is not a delivery claim.

Save at task milestones rather than waiting for automatic compaction. Live
startup/compaction behavior still requires a dated smoke receipt for each
installed client and orchestration surface. Tests here are offline fixtures.

Verification: `python scripts/verify-continuity.py` and
`python scripts/verify-context.py`; both use disposable local fixtures.
