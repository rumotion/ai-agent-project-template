---
handoff_version: 2
last_touched: 2026-08-20
last_model: Gemini
to_model: Any
branch: main
status: automated upgrader and 2026 SDD integrated
task: Automated Target Upgrader & 2026 SDD Modernization
next_action: Run automated upgrades on target projects (scripts/upgrade-target.py)
files_modified: [scripts/upgrade-target.py, scripts/check-template.py, workflows/, .agents/, .claude/, .cline/, docs/, memory-bank/]
blocking_issues: []
---

# Handoff

Automated Target Project Upgrader (`scripts/upgrade-target.py`) and 2026 Spec-Driven Development doctrines integrated across the template.

- **Automation (`scripts/upgrade-target.py`)**: Safely upgrades any external target repository, preserves custom rules and domain skills, syncs 3 trees, runs post-upgrade validation.
- **SDD & Doctrines**: Spec-driven development with characterization safety nets, falsifiable prediction gates, 4-tier escalation ladder, and refutation tracking.
- **Verification**: `python scripts/check-template.py` full PASS (122 files, 15 budgets, FAST_INIT ~2,324 tokens, zero drift).
