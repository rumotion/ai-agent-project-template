# Upgrade Existing Project Guide

Use this guide when you have an existing project repository created from an older template version, and you want to upgrade its template framework, workflows, skills, adapters, and validators to the latest AI Agent Project Template version.

## Core Rules

1. **Zero Damage to Application Code**: Never overwrite, modify, or delete custom application code, test suites, scratch scripts, images, data files, or custom domain skills.
2. **Preserve Custom Rules**: Retain any project-specific rules in the target's `AGENTS.md`.
3. **Context Budget Compliance**: Ensure `AGENTS.md` remains <= 6,500 chars and `memory-bank/handoff.md` remains <= 1,200 chars.

---

## Upgrade Steps for AI Agents

When the user asks:
```text
Upgrade my project [project-path] using the latest template.
```

The agent executes the following steps:

1. **Read Target Context**: Inspect target `AGENTS.md`, `memory-bank/handoff.md`, and `.agents/skills/` to record custom rules, handoff state, and existing domain skills.
2. **Update Core Instructions & Adapters**: Merge latest template `AGENTS.md` while keeping target custom rules. Update `GEMINI.md`, `CLAUDE.md`, `CONVENTIONS.md`, `.codex/AGENTS.md`, `.cursor/rules/agents.mdc`, `.github/copilot-instructions.md`, `.clinerules/`, and `.agents/rules/`.
3. **Synchronize Workflows & Skills**: Copy all workflows (`workflows/`, `.agents/workflows/`, `.clinerules/workflows/`) and standard skills (`.agents/skills/`, `.claude/skills/`, `.cline/skills/`). Ensure custom domain skills are untouched.
4. **Copy Documentation & Hooks**: Copy `docs/`, reviewer contracts (`.gemini/agents/reviewer.md`, `.codex/agents/reviewer.toml`, `.claude/agents/reviewer.md`), and safety hook scripts (`scripts/hooks/`).
5. **Install Validator, Bootstrap & Security Scripts**: Copy `scripts/check-template.py`, `scripts/init-fast.py`, `scripts/detach-remote.py`, `scripts/benchmark-context.py`, and `benchmarks/context/`.
6. **Validate & Commit**:
   - `python scripts/check-template.py --fast` (PASS)
   - `python scripts/benchmark-context.py --self-test` (PASS)
   - `python scripts/hooks/verify-fixtures.py` (PASS)
   - `git commit -m "feat(template): upgrade framework to AI Agent Project Template v0.8.0"`
