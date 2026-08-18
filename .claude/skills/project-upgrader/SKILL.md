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

## Phased Upgrade Procedure

### Phase 1: Understand Target & Inventory

1. Identify the target project path (e.g. `c:\AI\_code\InnovationLab\KUMO\KumoQAToolkit`).
2. Read target `AGENTS.md` to identify custom project rules (e.g. database deletion rules, board selection rules).
3. Read target `.agents/skills/` to inventory custom domain skills that must be preserved.
4. Read target `memory-bank/handoff.md` to record current project status and completion history.

### Phase 2: Canonical Instructions & Multi-Agent Adapters

1. Merge latest template `AGENTS.md` structure (FAST_INIT/DEEP_AUDIT modes, Karpathy engineering defaults, agentic execution loop) while preserving target custom rules in the Core Rules section.
2. Compact `AGENTS.md` to <= 6,500 chars if necessary.
3. Update/create multi-agent adapter files in target:
   - `GEMINI.md` (`@AGENTS.md`)
   - `CLAUDE.md` (`@AGENTS.md`)
   - `CONVENTIONS.md`
   - `.codex/AGENTS.md` (`Read ../AGENTS.md; it is canonical.`)
   - `.cursor/rules/agents.mdc`
   - `.github/copilot-instructions.md`
   - `.clinerules/00-master.md`, `10-memory-bank.md`, `40-testing.md`
   - `.agents/rules/00-master.md`, `10-memory-bank.md`

### Phase 3: Workflows & Skill Ecosystem

1. Synchronize all workflow files across:
   - `workflows/` (canonical)
   - `.agents/workflows/` (mirror)
   - `.clinerules/workflows/` (mirror)
2. Copy standard template skills (`project-planner`, `karpathy-engineer`, `code-reviewer`, `test-strategist`, `docs-memory-maintainer`, `delegation-coordinator`, `project-upgrader`) across:
   - `.agents/skills/`
   - `.claude/skills/`
   - `.cline/skills/`
3. Ensure all custom domain skills in target `.agents/skills/` are left intact and unharmed.

### Phase 4: Documentation, Reviewer Roles & Hooks

1. Copy/update template documentation in `docs/` while preserving target-specific documentation files.
2. Install multi-agent reviewer contracts:
   - `.gemini/agents/reviewer.md`
   - `.codex/agents/reviewer.toml`
   - `.claude/agents/reviewer.md`
3. Install hook infrastructure and settings:
   - `scripts/hooks/log-writes.py`
   - `scripts/hooks/guard-sensitive-paths.py`
   - `scripts/hooks/verify-fixtures.py`
   - `scripts/hooks/fixtures/`
   - `.claude/settings.json`, `.gemini/settings.example.json`, `.codex/hooks.example.json`, `.codex/config.example.toml`

### Phase 5: Validator, Bootstrap, Benchmarks & Memory Bank

1. Copy latest `scripts/check-template.py` (v0.8.0 full validation suite).
2. Copy `scripts/init-fast.py` and `scripts/detach-remote.py`.
3. Copy `scripts/benchmark-context.py` and `benchmarks/context/`.
4. Add missing `.gitignore` patterns (e.g. `.agent-benchmarks/`).
5. Update `memory-bank/` files (`00-index.md`, `startup.md`, `reminders.md`, `model-routing.md`, `handoff.md`) to schema v2 while keeping all project status history.

### Phase 6: Verification & Commit

1. Run fast template validation in target:
   ```bash
   python scripts/check-template.py --fast
   ```
2. Run benchmark self-test in target:
   ```bash
   python scripts/benchmark-context.py --self-test
   ```
3. Run hook verification in target:
   ```bash
   python scripts/hooks/verify-fixtures.py
   ```
4. Verify custom test files compile/pass cleanly:
   ```bash
   python -m py_compile <test_files>
   ```
5. Stage and commit upgraded framework files:
   ```bash
   git commit -m "feat(template): upgrade framework to AI Agent Project Template v0.8.0"
   ```
