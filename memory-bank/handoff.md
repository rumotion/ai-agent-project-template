---
handoff_version: 2
last_touched: 2026-08-01
last_model: Cline
to_model: Any
branch: main
status: v0.8.0 released
task: Atomic step-commit workflow
next_action: Create new repositories via GitHub Use this template
files_modified: [AGENTS.md, docs/agent-loop.md, workflows/, CONVENTIONS.md, memory-bank/, check-template.py]
blocking_issues: []
---

# Handoff

DEEP_AUDIT passed; remediation committed on `main`; v0.8.0 bookkeeping done.

- **Loop (`AGENTS.md`, `docs/agent-loop.md`)**: Upgraded to **Plan → Execute → Verify → Commit → Reflect**.
- **Workflows (`plan-task.md`, `implement-task.md`)**: Phased planning with atomic, committable checkpoints; validator requires all 9 x 3 trees.
- **Conventions & Patterns (`CONVENTIONS.md`, `memory-bank/systemPatterns.md`)**: Git & Commit Conventions and Atomic Step-Commit pattern.
- **Verification**: `python scripts/check-template.py` full PASS (115 files, 15 budgets, zero drift).
