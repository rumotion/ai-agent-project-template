# Agent Execution Loop

Operational rules for how an agent should *execute* a task: tool batching, turn budgets, error handling, and what to write when a unit of work finishes. Lazy-loaded — `AGENTS.md` carries the one-line summary; the detail lives here.

Applies to any tool (Claude, Gemini, Codex, Cline, Roo Code, Cursor, Windsurf, Copilot, Aider). Where a feature is provider-specific it is labelled.

## 1. Parallel tool calls

When steps are independent, issue the tool calls **in a single batch** instead of serializing them. Reading 5 files in parallel costs the same wall-clock time as reading 1.

- Batch independent reads/searches together (most providers run them concurrently).
- Never batch a write with a read of the same resource, or two writes that can conflict.
- Prefer `--files-with-matches` / map-first search, then read only the hits.

## 2. Turn / tool-call budgets

Bound every task so a stuck agent halts instead of looping and burning tokens:

| Task class | Soft budget (tool calls) |
|---|---|
| Simple (rename, typo, one unit test, small tweak) | ~5 |
| Standard (bug fix, single feature) | ~15 |
| Complex (refactor, architecture, cross-module) | ~30 |

On reaching the budget without success: stop, summarize what was tried, and report — do not keep looping silently. Claude Code exposes a `/goal`-style completion condition for long autonomous runs; other tools rely on this convention.

## 3. Error taxonomy and retry limits

Classify the failure before reacting; not every error deserves a retry.

| Error type | Response | Max retries |
|---|---|---|
| Transient (network, rate limit) | Back off and retry; do not change context | 3 |
| Logic (wrong output, failed test) | Self-critique → revise → retry | 2 |
| State corruption (bad write, inconsistent tree) | Restore from last verified state / `handoff.md`, then retry | 1 |
| Capability (task exceeds model) | Escalate to a stronger model (see `model-routing.md` cascade rule) | — |
| Context overflow | Compact/summarize, then resume | — |
| Retries exhausted | Write a one-line lesson to `memory-bank/risks.md`, then halt | — |

The "one-line lesson on failure" matters: it stops the next session repeating the same dead end.

## 4. Plan → execute → verify → commit → reflect

1. **Plan** — structure detailed phases and concrete task checkpoints with success criteria (`workflows/plan-task.md`).
2. **Execute** — perform small, focused, surgical changes for the active task step.
3. **Verify** — run cheapest checks first (lint, types, unit tests), followed by an agent/critic pass (`workflows/critic-review.md`).
4. **Commit** — immediately commit verified work for the current step (`git commit -m "<type>(<scope>): <step description>"`). Keep commits atomic and frequent per plan step.
5. **Reflect** — write the phase-completion summary below upon finishing a milestone/phase.

### Atomic Commit Guidelines
- **Frequency**: Commit after *every* verified task step or phase checkpoint in the plan (do not accumulate uncommitted diffs across multiple steps).
- **Conventional Commits**: Use standardized commit prefixes: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `style`, `perf`.
- **Clean Working Tree**: Verify tests pass before committing; never commit broken build states.
- **Pushing**: Push commits to remote branch upon phase completion or major milestone verification (`git push`).

## 5. Phase-completion summary

When a unit of work (phase, feature, fix) completes, append a structured block to `memory-bank/activeContext.md` (or `progress.md`). Keep it short — it is what the next session/model reads instead of replaying history.

```markdown
## Phase summary: <name> — <YYYY-MM-DD>
- Outcome: COMPLETE | PARTIAL | FAILED
- Key decisions: <=3 bullets (link to memory-bank/decisions.md if deeper)
- Files modified: <list>
- Open items: <list or "none">
- Next: <name + first concrete action>
```

Then update `memory-bank/handoff.md` (rolling pointer) and clear any acted-on entries in `memory-bank/reminders.md`.

