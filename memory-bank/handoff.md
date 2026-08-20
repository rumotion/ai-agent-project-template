---
handoff_version: 2
last_touched: 2026-08-20
last_model: Gemini
to_model: Any
branch: main
status: arc-skill cognitive doctrines integrated
task: ARC-Skill Cognitive Doctrines Integration
next_action: Create new repositories or upgrade existing projects
files_modified: [AGENTS.md, docs/agent-loop.md, workflows/, .agents/, .claude/, .cline/, memory-bank/]
blocking_issues: []
---

# Handoff

ARC-Skill cognitive doctrines (falsifiable predictions, 4-tier escalation ladder, bimodal probe vs batch, refuted hypotheses ledger) integrated across template.

- **Doctrines (`AGENTS.md`, `docs/agent-loop.md`, `workflows/`, `skills/`)**: Falsifiable predictions before edits, 4-tier problem-solving escalation, single probe for exploration vs parallel batch for execution, `REFUTED` dead hypothesis tracking.
- **Mirror Parity**: 100% byte parity verified across all 3 workflow trees and all 3 skill trees.
- **Verification**: `python scripts/check-template.py` full PASS (121 files, 15 budgets, FAST_INIT ~2,324 tokens, zero drift).
