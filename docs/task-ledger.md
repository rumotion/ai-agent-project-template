# Private task ledger

Use `scripts/tasks.py` when work spans sessions or agents. It stores one atomic
document per task outside Git, under the project's private continuity directory.
The rolling handoff remains a short entry point; the ledger preserves other open
tasks. No dependency installation, worker dispatch or quota pacing is required.

## Admission and recovery

Create a reviewed [portable task envelope](subagent-contract.md) with concrete
inputs and bounded owned paths, then run:

```text
python scripts/tasks.py create --envelope PATH_TO_PRIVATE_TASK_JSON
python scripts/tasks.py list
python scripts/tasks.py show TASK_ID
python scripts/tasks.py start TASK_ID --revision 1
```

Options `--root PROJECT` and `--state-dir PRIVATE_DIRECTORY` precede the command.
Default owner is `lead`; a custom owner must be repeated on mutations. On resume,
list open tasks, read each summary and reconcile actual workers before changing
state. Use `show TASK_ID --details` only when the full envelope/evidence is needed.
Lists contain at most 32 tasks; follow `next_offset` using `--offset`.

Every mutation requires the current revision. A start creates a unique attempt
ID and immutable file inventory. Save that ID from the output. Record a concrete
restart step with `note TASK_ID --revision N --next-action "Verify error path"`.
Dependencies supplied with `create --depends-on TASK_ID` must already exist;
starting waits for their parent acceptance. Cycles and missing dependencies fail.
Admission allows one running worker and two open tasks, including reviews and
blockers. Conservative glob overlap retains ownership until acceptance/cancellation.

## Submission and parent acceptance

Stop edits and freeze the work before either operation. The worker supplies a
portable result; the parent independently checks the artifact and prepares a
separate result envelope describing its actual verification:

```text
python scripts/tasks.py submit TASK_ID --revision N --attempt ATTEMPT_ID --result PRIVATE_RESULT_JSON
python scripts/tasks.py accept TASK_ID --revision N --attempt ATTEMPT_ID --verification PRIVATE_PARENT_RESULT_JSON
```

Submission enters `review`; it does not release dependencies. Acceptance requires
successful declared verification, an unchanged reviewed inventory and an exact
match between declared changes and observed added/modified/deleted files. Dirty
files are compared to their attempt-start bytes, rather than only to Git HEAD.
Commands inside envelopes are data: this helper never executes them. Tokens,
turn counts and process identity are not independently measured by this ledger.

For interrupted/failed work, use `block` or `cancel` with current revision,
attempt ID and `--stopped` after independently confirming the worker has stopped.
Queued tasks need no stop declaration. Restart a blocked task with `start
--stopped`; it consumes one repair and gets a new attempt ID. A late old result
is refused. A stopped flag records a coordinator declaration; it does not kill
or inspect a process. Preserve changes on every refusal and reconcile manually.

## Bounds and trust

The audit covers Git-eligible tracked/untracked files plus explicit inputs,
including ignored explicit inputs. It does not contain processes or cover other
ignored files, external state, transient edits reverted before observation or
concurrent writes during a scan. Use isolated workspaces and stop writers for
review. A same-user process can edit private files; hashes and owner strings are
cooperative integrity checks, not authentication or a security boundary.

Limits: 1,000 task documents; 32 history events per task; 64 KiB state; 10,000
inventory entries; 1 MiB per input and 64 MiB total content; 2 MiB inventory JSON.
Oversized, linked, sensitive or ambiguous paths fail closed for manual review.
Max repairs comes from the envelope (initial attempt plus that many restarts).
Retain old baselines for audit; no automatic cleanup or lock stealing occurs.
An interrupted state publication can leave an unreferenced inventory, while the
previous task document remains authoritative. Do not delete a lock until all
writers are confirmed stopped. Native leases, heartbeats and cancellation remain
a separate, conditional runtime work package.
