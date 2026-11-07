# Workflow: Session Handoff

Use when pausing, switching models, or resuming work. Keeps context coherent across Gemini/Claude/ChatGPT/OpenRouter without re-reading the full Memory Bank.

## On pause / model switch

1. Update `memory-bank/handoff.md` (timestamp, model, branch, current task, last action, next step, files touched, blockers).
2. Keep it under 30 lines and at most 1,200 characters (the existing validator
   limit). Leave headroom; link to authoritative documents instead of copying
   detailed history. Preserve facts in their source documents or typed records.
3. Reconcile status, next action, startup notes and required records with current
   sources. An initial not-started/TBD record can become stale even when syntax
   checks pass. Preserve its body, mark it superseded by a new same-type record,
   and update required IDs; never leave a superseded ID required.
4. Update `memory-bank/activeContext.md` only if durable project knowledge changed.
5. Run `python scripts/check-template.py --fast` and
   `python scripts/ctx.py compile --for generic --check` before checkpointing.
   If a budget fails, shorten the summary while retaining source links and facts;
   do not relax the validator or truncate evidence merely to pass.
6. Commit if work is in a clean state. Preserve concurrent edits; refresh a stale
   snapshot before writing, and checkpoint only the reconciled final state.

## On resume

1. Read `memory-bank/handoff.md` first (after `AGENTS.md` and `memory-bank/startup.md`).
2. Verify branch and last action match `git status` / `git log -1`.
3. Continue from "Next concrete step".
4. After meaningful progress, refresh `handoff.md`.

For multi-task work, run `python scripts/tasks.py list`, follow all pages and
reconcile open attempts before starting a replacement worker. Save each task's
next action through `note`; see `docs/task-ledger.md`. A handoff never replaces
the ledger, and a submitted result does not imply parent acceptance.

Use `python scripts/continuity.py doctor --mode legacy` to validate and explicitly
label existing state before manual reconciliation. After saving a meaningful
checkpoint, use `checkpoint --task-id ID --input RELATIVE_FILE` and inspect with
`doctor --mode resume`; see `docs/continuity.md`. Checkpoints belong outside the
repository. A ready local receipt does not prove native model consumption or
grant authority. Preserve unfinished work on every failure path.

For a task-specific projection, add scalar `task_id: ID` and optional comma-separated
`required_records: ID1,ID2` to the handoff header. Required records must exist and
be active; they are never dropped to fit the budget. Store decisions through
`workflows/update-memory-bank.md` before checkpointing. Retrieve full records
with `python scripts/ctx.py show --id ID` instead of re-reading all history.

## Rules

- `handoff.md` is volatile and ephemeral. `activeContext.md` is durable.
- Never store secrets or large logs here.
- One handoff file per repo, not per task; recent task wins.
