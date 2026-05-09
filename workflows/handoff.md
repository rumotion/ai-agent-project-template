# Workflow: Session Handoff

Use when pausing, switching models, or resuming work. Keeps context coherent across Gemini/Claude/ChatGPT/OpenRouter without re-reading the full Memory Bank.

## On pause / model switch

1. Update `memory-bank/handoff.md` (timestamp, model, branch, current task, last action, next step, files touched, blockers).
2. Keep it under 30 lines. Overwrite, do not append history.
3. Update `memory-bank/activeContext.md` only if durable project knowledge changed.
4. Commit if work is in a clean state.

## On resume

1. Read `memory-bank/handoff.md` first (after `AGENTS.md` and `memory-bank/startup.md`).
2. Verify branch and last action match `git status` / `git log -1`.
3. Continue from "Next concrete step".
4. After meaningful progress, refresh `handoff.md`.

## Rules

- `handoff.md` is volatile and ephemeral. `activeContext.md` is durable.
- Never store secrets or large logs here.
- One handoff file per repo, not per task; recent task wins.
