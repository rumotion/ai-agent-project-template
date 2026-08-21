# Upgrade Existing Project Workflow

Follow this procedure when upgrading an existing external repository/project to the latest AI Agent Project Template version.

## Core Mandates

- **Zero Breaking Changes**: Never overwrite, delete, or alter custom application code, test scripts (`test_*.py`, `*.spec.ts`), project assets, extraction logic, or custom domain skills.
- **Preserve Domain Rules**: Retain all custom domain rules in target's `AGENTS.md` (e.g. database safety rules, board selection rules).
- **Budget Compliance**: Keep target `AGENTS.md` <= 6,500 chars and `memory-bank/handoff.md` <= 1,200 chars to satisfy `FAST_INIT` budget checks.

## Workflow Steps

### Step 1: Preflight & Safety Inventory
1. Identify target project directory path (e.g. `c:\AI\_code\InnovationLab\KUMO\KumoQAToolkit`).
2. Run dry-run to preview planned changes:
   ```bash
   python scripts/upgrade-target.py --target <target-path> --dry-run
   ```
3. Inspect target `AGENTS.md` and `.agents/skills/` to identify custom rules and domain skills to preserve.

### Step 2: Automated Framework Upgrade
1. Execute the automated upgrade tool:
   ```bash
   python scripts/upgrade-target.py --target <target-path>
   ```
   This automatically:
   - Merges latest `AGENTS.md` canonical instructions and cognitive doctrines (falsifiable predictions, escalation ladder, bimodal execution, refutation ledger) while preserving target custom rules.
   - Synchronizes multi-agent adapters (`GEMINI.md`, `CLAUDE.md`, `CONVENTIONS.md`, `.windsurfrules`, `.codex/AGENTS.md`, `.cursor/rules/agents.mdc`, `.github/copilot-instructions.md`, `.clinerules/`, `.agents/rules/`).
   - Synchronizes 10 workflows across `workflows/`, `.agents/workflows/`, `.clinerules/workflows/`.
   - Synchronizes standard skills across `.agents/skills/`, `.claude/skills/`, `.cline/skills/` without touching custom domain skills.
   - Copies safety hooks, reviewer contracts, documentation, and validation scripts (`scripts/check-template.py`, `scripts/init-fast.py`, `scripts/detach-remote.py`, `scripts/benchmark-context.py`, `scripts/upgrade-target.py`).
   - Upgrades Memory Bank schemas (`00-index.md`, `startup.md`, `reminders.md`, `model-routing.md`, `handoff.md`) to schema v2.

### Step 3: Target Validation
1. Run fast template validation in target:
   ```bash
   python <target-path>/scripts/check-template.py --fast
   ```
2. Run benchmark and hook verification in target:
   ```bash
   python <target-path>/scripts/benchmark-context.py --self-test
   python <target-path>/scripts/hooks/verify-fixtures.py
   ```
3. Verify target application tests compile/pass cleanly:
   ```bash
   python -m py_compile <test_files>
   ```

### Step 4: Commit
1. Stage upgraded framework files in target repository:
   ```bash
   git add AGENTS.md GEMINI.md CLAUDE.md CONVENTIONS.md .codex/ .cursor/ .github/ .clinerules/ .agents/ .claude/ .gemini/ docs/ workflows/ scripts/ benchmarks/ memory-bank/ .gitignore
   ```
2. Commit:
   ```bash
   git commit -m "feat(template): upgrade framework to latest AI Agent Project Template"
   ```
