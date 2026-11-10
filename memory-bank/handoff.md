---
handoff_version: 54
last_touched: 2026-11-09
last_model: Claude
to_model: Codex
branch: main
status: Production-readiness simulation Stage 1 complete; Stage 2 blind drift audit pending
task: Two-model production-readiness and upgrade simulation (Stage 1 Claude, Stage 2 Codex)
task_id: continuity-upgrade
required_records: decision-phased-continuity
next_action: Codex runs workflows/drift-report.md blind on .agent-logs/prod-sim-target/src contracts
blocking_issues: []
---

# Handoff

Stage 1 (Claude) results:

- **Reviewer re-check (`2d20606`)**: all 4 prior medium findings are resolved in `docs/peanuts-and-hay.md` and `workflows/drift-report.md`. Verdict is `revise`, not `approve`: the reviewer raised 2 new medium findings in `scripts/README.md`. (a) Interface rows list flags/subcommands that do not exist for `new-project.py`, `detach-remote.py`, `upgrade-target.py`, `ctx.py`, `continuity.py`, `tasks.py`, `routing_policy.py`, `usage-pacing.py`. (b) The "no script calls external APIs" invariant contradicts the remote `git fetch` in `template_upgrade.py`. Five low findings also open (exit-code-2 exceptions, `usage-pacing.py` state path, `--schemas`, drift-report Verification execution rule, "top-level" contract wording). Not fixed in Stage 1.
- **Upgrade simulation**: mock project at `.agent-logs/prod-sim-target` (untracked, gitignored). Dry-run exit 0 (259 add, 1 conflict, 2 preserve). `--apply-safe --backup-dir .agent-logs/prod-sim-backups` exit 2 with `AGENTS.md` the only conflict. All 9 custom files SHA-256 identical before/after; baseline in `.agent-logs/prod-sim-backups/pre-upgrade-hashes.json`. `.template-upstream.json` and `template-upgrade-_n1aiki1/report.json` (`applied_with_conflicts`) written; all 7 EGM files present and byte-identical to the template.
- **bootstrap-context (`CONTEXT.md` mode)**: contracts at `src/CONTEXT.md`, `src/auth/CONTEXT.md`, `src/billing/CONTEXT.md`, `src/api/CONTEXT.md`; `src/auth/README.md` untouched. Contracts were grounded against the pre-edit code.
- **Drift traps**: after the contracts were written, `src/auth/service.py` and `src/billing/invoice.py` were edited to seed 4 code-vs-contract drifts, one per `workflows/drift-report.md` category. `src/api/routes.py` is the clean control and must report `No drift detected.` The drifts are intentionally not listed here.
- `python scripts/check-template.py --fast` passes (FAST_INIT 8390/9500).

Stage 2 (Codex): audit `.agent-logs/prod-sim-target/src/**/CONTEXT.md` with `workflows/drift-report.md`, chat-first and read-only. Do not modify `.agent-logs/prod-sim-target` or `.agent-logs/prod-sim-backups`. Pacing OFF; local-only, no remote configured.
