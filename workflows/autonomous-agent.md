# Workflow: Autonomous Agent Run

For longer hands-off runs where the agent works across many turns toward a goal without a human in the loop each step. Keeps an autonomous run from drifting, looping, or burning tokens. Tool-agnostic; some tools (e.g. Claude Code's goal/completion-condition feature) automate parts of this — the discipline below applies regardless.

## Before starting

1. **State the goal as a checkable completion condition.** Not "improve the API" but "all endpoints in `routes.py` have input validation and a passing test." The run ends when this is verifiably true.
2. **Set a budget.** Max tool calls and/or max wall-clock, matched to task size (see `docs/agent-loop.md` §2). The agent halts and reports when the budget is hit, success or not.
3. **Define the verification command.** The single check (test suite, lint, build) that decides whether a step succeeded.
4. **Snapshot state.** Commit or note the starting point so a bad run can be rolled back.

## Loop

```
while goal not met and budget not exhausted:
    pick the next smallest step toward the goal
    execute it (batch independent tool calls — docs/agent-loop.md §1)
    run the verification command
    if it fails: apply the error taxonomy (docs/agent-loop.md §3)
                 — backoff / revise / escalate; do not loop blindly
    commit the verified step (atomic)
    update memory-bank/handoff.md with progress
```

## On stop (any reason)

- Write a phase-completion summary (`docs/agent-loop.md` §5) to `memory-bank/activeContext.md`.
- Update `memory-bank/handoff.md` so another model can resume.
- If the goal was not met: record why and the last verified state in `handoff.md`; add a one-line lesson to `memory-bank/risks.md`.

## Guardrails

- Never run destructive commands (drops, force-push, mass delete) autonomously — these always need a human, per `AGENTS.md`.
- Stop and ask if the goal turns out to be ambiguous or the success condition can't be checked.
- Prefer many small verified commits over one large unverified change — they're the rollback points.
