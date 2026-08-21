# Upgrade Existing Project Guide

Use this guide when you have an existing project repository created from an older template version, and you want to upgrade its template framework, workflows, skills, adapters, and validators to the latest AI Agent Project Template version.

## Core Rules

1. **Zero Damage to Application Code**: Never overwrite, modify, or delete custom application code, test suites, scratch scripts, images, data files, or custom domain skills.
2. **Preserve Custom Rules**: Retain any project-specific rules in the target's `AGENTS.md`.
3. **Context Budget Compliance**: Ensure `AGENTS.md` remains <= 6,500 chars and `memory-bank/handoff.md` remains <= 1,200 chars.

---

## Automated Upgrade Tool (`scripts/upgrade-target.py`)

The template includes an automated, standard-library Python tool to safely upgrade any target repository:

```bash
# Preview planned changes
python scripts/upgrade-target.py --target /path/to/target/project --dry-run

# Execute upgrade and validate
python scripts/upgrade-target.py --target /path/to/target/project
```

### What `scripts/upgrade-target.py` does:
1. **Preserves Custom Rules**: Merges latest `AGENTS.md` instructions and cognitive doctrines (falsifiable predictions, escalation ladder, bimodal execution, refutation ledger) while preserving target custom rules.
2. **Synchronizes Multi-Agent Adapters**: Updates `GEMINI.md`, `CLAUDE.md`, `CONVENTIONS.md`, `.windsurfrules`, `.codex/AGENTS.md`, `.cursor/rules/agents.mdc`, `.github/copilot-instructions.md`, `.clinerules/`, and `.agents/rules/`.
3. **Synchronizes 3-Tree Workflows**: Keeps all 10 workflows byte-identical across `workflows/`, `.agents/workflows/`, and `.clinerules/workflows/`.
4. **Synchronizes 3-Tree Skills**: Copies standard skills across `.agents/skills/`, `.claude/skills/`, and `.cline/skills/` while leaving custom domain skills intact.
5. **Copies Safety Hooks, Docs & Scripts**: Installs latest reviewer contracts, hooks, benchmark tools, and `scripts/check-template.py`.
6. **Validates Target**: Automatically executes `python scripts/check-template.py --fast` in the target repository.

---

## Upgrade Steps for AI Agents

When the user asks:
```text
Upgrade my project [project-path] using the latest template.
```

The agent executes:
1. `python scripts/upgrade-target.py --target [project-path] --dry-run` (inspect preview)
2. `python scripts/upgrade-target.py --target [project-path]` (apply upgrade)
3. `python [project-path]/scripts/check-template.py --fast` (verify target health)
4. `python [project-path]/scripts/benchmark-context.py --self-test` (verify benchmark harness)
5. `python [project-path]/scripts/hooks/verify-fixtures.py` (verify hook safety)
6. Commit upgraded framework files in target repository.
