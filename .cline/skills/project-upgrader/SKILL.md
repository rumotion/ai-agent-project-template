---
name: project-upgrader
description: Upgrades an existing target project to the latest AI Agent Project Template version. Use when asked to upgrade another project, port template updates, or bring an existing repository up to date with the latest template logic, skills, workflows, adapters, and validation tools without altering or breaking existing project scripts, tests, assets, or domain logic.
---

# Project Upgrader Skill

Use this skill whenever asked to upgrade an existing repository/project using the latest version of the AI Agent Project Template.

## Core Directives

> [!IMPORTANT]
> 1. **Zero Damage to Existing Project Domain Code**: Never overwrite, delete, or alter custom application code, test scripts (`test_*.py`, `*.spec.ts`, etc.), project assets, extraction logic, authentication configs (`*.json`, `.env`), or custom domain skills (e.g., `kumo-canvas`).
> 2. **Preserve Custom AGENTS.md Rules**: Always retain project-specific domain rules found in the target repository's `AGENTS.md` (e.g. database safety rules, test board rules).
> 3. **Context Budget Enforcement**: Ensure target `AGENTS.md` stays <= 6,500 chars and `memory-bank/handoff.md` stays <= 1,200 chars to satisfy `FAST_INIT` budget checks.

---

## Upgrade Execution Procedure

### Step 1: Preflight & Dry-Run
1. Identify target project path (e.g. `c:\AI\_code\InnovationLab\KUMO\KumoQAToolkit`).
2. Run a dry-run to preview planned modifications:
   ```bash
   python scripts/upgrade-target.py --target <target-path> --dry-run
   ```
3. Read target `AGENTS.md` and `.agents/skills/` to verify custom domain rules and custom domain skills to preserve.

### Step 2: Automated Framework Upgrade
1. Execute the automated upgrade tool:
   ```bash
   python scripts/upgrade-target.py --target <target-path>
   ```
   This automatically:
   - Preserves custom domain rules in `AGENTS.md` while merging latest canonical instructions, falsifiable predictions, escalation ladder, and bimodal execution.
   - Synchronizes multi-agent adapters (`GEMINI.md`, `CLAUDE.md`, `CONVENTIONS.md`, `.windsurfrules`, `.codex/AGENTS.md`, `.cursor/rules/agents.mdc`, `.github/copilot-instructions.md`, `.clinerules/`, `.agents/rules/`).
   - Synchronizes 10 workflows across `workflows/`, `.agents/workflows/`, `.clinerules/workflows/`.
   - Synchronizes standard skills across `.agents/skills/`, `.claude/skills/`, `.cline/skills/` while preserving custom domain skills intact.
   - Copies safety hooks, reviewer contracts, documentation, and validation scripts (`scripts/check-template.py`, `scripts/init-fast.py`, `scripts/detach-remote.py`, `scripts/benchmark-context.py`, `scripts/upgrade-target.py`).
   - Updates Memory Bank schemas to schema v2 while keeping project history.

### Step 3: Verification & Health Check
1. Run fast template validation in target:
   ```bash
   python <target-path>/scripts/check-template.py --fast
   ```
2. Run benchmark self-test and hook verification in target:
   ```bash
   python <target-path>/scripts/benchmark-context.py --self-test
   python <target-path>/scripts/hooks/verify-fixtures.py
   ```
3. Verify target application test files compile/pass cleanly:
   ```bash
   python -m py_compile <test_files>
   ```

### Step 4: Commit Upgraded Target
1. Stage and commit upgraded framework files in target repository:
   ```bash
   git add AGENTS.md GEMINI.md CLAUDE.md CONVENTIONS.md .codex/ .cursor/ .github/ .clinerules/ .agents/ .claude/ .gemini/ docs/ workflows/ scripts/ benchmarks/ memory-bank/ .gitignore
   git commit -m "feat(template): upgrade framework to latest AI Agent Project Template"
   ```
