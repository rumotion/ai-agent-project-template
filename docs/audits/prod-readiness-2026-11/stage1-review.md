# Production-Readiness Simulation, Stage 1: Review Findings and Fixes

Date: 2026-11-09. Author: Claude (Stage 1). Audience: any model or human resuming this work.

This records every finding from the Stage 1 reviewer passes and what was changed. The drift traps seeded in `.agent-logs/prod-sim-target` for the Stage 2 blind audit are deliberately not described here.

## Outcome

- The four medium findings from the earlier review are resolved (confirmed with file and line evidence).
- Three reviewer passes ran (`.claude/agents/reviewer.md`, `docs/reviewer-role.md`, `paraphrase:` block first each time). Pass 1: `revise`. Pass 2: `revise`. Pass 3: `accept`, no findings.
- 14 new findings were raised across passes 1 and 2 (4 medium, 10 low). All are fixed. One further inaccuracy was found and fixed outside the reviewer's list.
- Files changed: `scripts/README.md`, `workflows/drift-report.md`, and its mirrors `.agents/workflows/drift-report.md` and `.clinerules/workflows/drift-report.md`. No script source was changed.
- Verification after the fixes: `python scripts/check-template.py` (full) exit 0; `python scripts/gen-adapters.py --check` passes.

## Prior findings re-verified (commit `2d20606`)

| # | Prior finding | Status | Evidence |
|---|---|---|---|
| 1 | `<target_filename>` links in `CONTEXT.md` mode | Resolved | `docs/peanuts-and-hay.md` templates and rule 4; consistent with `workflows/bootstrap-context.md` |
| 2 | Bounded default scope and 10-document gate | Resolved | `workflows/drift-report.md` step 1 |
| 3 | `Interface`/`Invariants`/`Side Effects`/`Verification` mapped to drift categories | Resolved | `workflows/drift-report.md` step 2c |
| 4 | Read-only, chat-first report output | Resolved | `workflows/drift-report.md` Rules and step 3 |

The skill mirrors under `.agents/skills/` and `.claude/skills/` are thin pointers to the workflow and do not contradict it.

## Pass 1 findings and fixes

| # | Severity | Location | Finding | Fix |
|---|---|---|---|---|
| 1 | medium | `scripts/README.md` Interface table | Eight rows listed flags or subcommands that do not exist: `new-project.py`, `detach-remote.py`, `upgrade-target.py`, `ctx.py`, `continuity.py`, `tasks.py`, `routing_policy.py`, `usage-pacing.py` | Each row rewritten from the script's argparse definitions (see "Corrected interfaces" below) |
| 2 | medium | `scripts/README.md` Local-Only Boundary | "No script ... calls external APIs" contradicted the `git fetch` in `scripts/template_upgrade.py` | Invariant now names the read-only template fetch as the only network access of the core scripts; a Network bullet was added to Side Effects |
| 3 | low | `scripts/README.md` exit semantics | "Unless noted otherwise" but no exit `2` exceptions were noted | Exceptions listed for `upgrade-target.py --apply-safe`, `detach-remote.py`, `routing_policy.py`, `usage-pacing.py` |
| 4 | low | `scripts/README.md` Side Effects | `usage-pacing.py` state said to be under `.agent-logs/`; it is `~/.agent-usage-pacing` | Corrected, with the `--root` override |
| 5 | low | `scripts/README.md` `check-template.py` row | `--schemas` mode missing | Added |
| 6 | low | `workflows/drift-report.md` | Did not say whether `Verification` commands are executed during a read-only audit | New rule "Static Verification Check": do not execute; non-functional means the entry point, paths, or flags do not exist; run only if the user asks |
| 7 | low | `workflows/drift-report.md` step 1 | "root/top-level module contracts" was undefined | Defined as contracts at the repository root and in first-level directories that follow the Peanuts & Hay section structure; human-facing `README.md` files without it are skipped |

Found while fixing item 4, not raised by the reviewer: `continuity.py` and `tasks.py` were also described as keeping state under `.agent-logs/`. They use `~/.agent-continuity/<project-id>/` (`tasks.py --state-dir` overrides). Corrected in the same bullet. Only `hooks/log-writes.py` writes to `.agent-logs/session.jsonl`.

## Pass 2 findings and fixes

All in `scripts/README.md`, in text that predated the pass 1 edits.

| # | Severity | Finding | Fix |
|---|---|---|---|
| 8 | medium | `ctx.py record` was said to update `memory-bank/00-index.md`; it writes only `memory-bank/records/<id>.md` | Claim removed; the transient `.record-write.lock` is noted |
| 9 | medium | Exit semantics said blocked hook operations exit `2`. The guard hooks always exit `0` and deny through a JSON payload on stdout | New "Hook Exit Semantics" bullet: guards exit `0`, deny payload for `claude`/`codex`/`gemini` only, fail open on malformed events, `hooks/git/pre-push` exits `1` |
| 10 | low | Exit `2` exception list read as exhaustive | Reworded to "include" and added `benchmark-context.py`, `validate-schemas.py`, `transcribe_local_large_v3.py` |
| 11 | low | `upgrade-target.py` row said it upgrades from the local checkout by default; a source URL saved in the target's `.template-upstream.json` takes precedence | Row and Network bullet now state the saved-URL default |
| 12 | low | "Only network access" ignored that `transcribe_local_large_v3.py` loads Whisper models by name, which `faster-whisper` may download on first use | Invariant now notes the possible model-weight download; media and transcripts are never uploaded |
| 13 | low | `push_backstop.py` row claimed LF conflict handling that does not exist; `detach-remote.py` overwriting an existing `pre-push` hook was undocumented | `push_backstop.py` row reworded (refuses custom `core.hooksPath`, preserves an existing non-approved hook and raises `ValueError`); `detach-remote.py` row notes the overwrite |
| 14 | low | `validate-schemas.py` row named schemas that do not exist and omitted the CLI | Row uses `schemas/subagent-task.schema.json` and `schemas/subagent-result.schema.json` and lists the flags |

## Pass 3

Verdict `accept`, zero findings. Two observations were folded into the hook bullet: an invalid `--client` value exits `2` through argparse, and a guard failure launched through `hooks/antigravity-dispatch.py` makes the launcher exit `1`.

## Corrected interfaces (finding 1)

| Script | Was documented as | Actual |
|---|---|---|
| `new-project.py` | `--name`, `--dest`, `--stack`, `--init-git`, `--force` | positional `<target>`, `--name`, `--dry-run`, `--force`, `--no-git` |
| `detach-remote.py` | `--dry-run`, `--force` | `--check`, `--pattern`, `--all` |
| `upgrade-target.py` | `--pin-sha`; `--source` as local path or URL | `--expect-commit`; `--source` is an HTTPS/SSH URL only; also `--baseline-ref`, `--apply-safe` |
| `ctx.py` | `--task`; clients `windsurf`, `copilot` | `--task-id`; clients `antigravity`, `claude`, `cline`, `codex`, `cursor`, `gemini`, `generic`; plus `show --id` |
| `continuity.py` | `doctor --mode legacy\|strict`, `restore` | `doctor --mode fresh\|legacy\|resume`, `checkpoint --task-id`; no `restore` |
| `tasks.py` | `complete`, `review`, `audit` | `create`, `list`, `start`, `submit`, `accept`, `block`, `cancel`, `show`, `note` |
| `routing_policy.py` | `evaluate`, `--json` | one positional observation JSON path |
| `usage-pacing.py` | `status`, `plan`, `record`, `--db` | `plan`, `start`, `status`, `stop`, `record`, `pace`, `usage`, `context`, `cost`; `--root` |

## Notes for whoever continues

- `scripts/README.md` drifted from the code because its interface table was written by hand. When a script's CLI changes, regenerate its row from the argparse definition, and prefer checking a contract with `workflows/drift-report.md` before accepting it.
- The copy of `workflows/drift-report.md` inside `.agent-logs/prod-sim-target` was installed before these fixes and is the older text. Stage 2 should use the repository root `workflows/drift-report.md`.
- Behaviours documented here but not changed, which a maintainer may want to revisit as code: the guard hooks fail open on malformed events, and `detach-remote.py` overwrites an existing `.git/hooks/pre-push` without a backup.
- Reviewer limits: the reviewer is read-only and ran no commands. Mirror byte-identity was confirmed separately with `gen-adapters.py --check`. The `.cline/skills` mirrors were not individually inspected by the reviewer; the full `check-template.py` hash check covers them.
