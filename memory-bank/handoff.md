---
handoff_version: 54
last_touched: 2026-11-09
last_model: Claude
to_model: Codex
branch: main
status: Prod-readiness simulation Stage 1 done; Stage 2 blind drift audit pending
task: Two-model production-readiness and upgrade simulation
task_id: continuity-upgrade
required_records: decision-phased-continuity
next_action: Codex runs workflows/drift-report.md blind on .agent-logs/prod-sim-target/src
blocking_issues: []
---

# Handoff

Stage 1 (Claude): reviewer confirms the 4 prior findings resolved, but verdict is `revise`: `scripts/README.md` lists nonexistent CLI flags/subcommands (8 rows) and its no-network invariant contradicts the `template_upgrade.py` fetch. Unfixed.

Upgrade sim on `.agent-logs/prod-sim-target` passed: apply-safe exit 2, `AGENTS.md` sole conflict, 9 custom files hash-identical (`.agent-logs/prod-sim-backups/pre-upgrade-hashes.json`).

`CONTEXT.md` contracts exist under `src/`. 4 drifts (one per category) were seeded afterwards in `auth` and `billing`; `api` is the clean control. Drifts deliberately unlisted. Audit read-only, chat-first. Pacing OFF; local-only.
