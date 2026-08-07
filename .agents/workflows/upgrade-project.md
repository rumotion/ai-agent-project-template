# Upgrade Existing Project Workflow

Follow this procedure when upgrading an existing external repository/project to the latest AI Agent Project Template version.

## Core Mandates

- **Zero Breaking Changes**: Do not delete, overwrite, or mutate project-specific code, test scripts, assets, or domain configs.
- **Preserve Domain Rules**: Maintain any custom rules in target's `AGENTS.md` (e.g. SQLite locks, test board rules).
- **Budget Compliance**: Keep target `AGENTS.md` <= 4,700 chars and `memory-bank/handoff.md` <= 1,200 chars.

## Workflow Steps

### Step 1: Inventory & Backup Check
1. Read target's `AGENTS.md` and `memory-bank/handoff.md` to discover custom rules, status history, and domain skills in `.agents/skills/`.
2. Confirm target repository status with `git status`.

### Step 2: Framework Upgrade
1. Update canonical instructions (`AGENTS.md`) and adapters (`GEMINI.md`, `CLAUDE.md`, `CONVENTIONS.md`, `.codex/AGENTS.md`, `.cursor/rules/agents.mdc`, `.github/copilot-instructions.md`, `.clinerules/`, `.agents/rules/`).
2. Sync `workflows/`, `.agents/workflows/`, and `.clinerules/workflows/`.
3. Copy standard template skills to `.agents/skills/`, `.claude/skills/`, `.cline/skills/` without deleting target's custom skills.
4. Copy updated documentation files in `docs/` and reviewer contracts (`.gemini/agents/reviewer.md`, `.codex/agents/reviewer.toml`, `.claude/agents/reviewer.md`).
5. Copy `scripts/hooks/`, `scripts/check-template.py`, `scripts/benchmark-context.py`, and `benchmarks/context/`.

### Step 3: Validation & Memory Bank Sync
1. Run `python scripts/check-template.py --fast` in target project.
2. Run `python scripts/benchmark-context.py --self-test` in target project.
3. Run `python scripts/hooks/verify-fixtures.py` in target project.
4. Run python compile check on project test files (`python -m py_compile <test_files>`).

### Step 4: Commit
1. Stage upgraded template files:
   `git add AGENTS.md GEMINI.md CLAUDE.md CONVENTIONS.md .codex/ .cursor/ .github/ .clinerules/ .agents/ .claude/ .gemini/ docs/ workflows/ scripts/ benchmarks/ memory-bank/ .gitignore`
2. Commit:
   `git commit -m "feat(template): upgrade framework to AI Agent Project Template v0.8.0"`
