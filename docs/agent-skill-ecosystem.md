# Agent Skill Ecosystem

Keep this guidance out of the startup path. Read it only when choosing or designing skills/plugins.

## Selection rule

Add skills/plugins only when they clearly:

- save time,
- reduce cost,
- reduce human error, or
- improve verification for risky work.

## Useful patterns

- **Skill creator/factory:** turn repeatable SOPs into small auditable skills.
- **Skill Chaining & Progressive Disclosure:** Break workflows into atomic skills. Chain them sequentially (e.g., `project-planner` -> `karpathy-engineer` -> `code-reviewer`) and only load the specific skill context needed for the current step to minimize context bloat.
- **Senior-dev workflow:** plan, test, implement, review, and verify instead of rushing code.
- **Clean context execution:** use subagents or isolated contexts for broad research/risky work when supported.
- **Review gates:** run local review for normal changes and stronger review for auth, payments, migrations, security, or large refactors.
- **Context hygiene:** summarize noisy tool output; keep raw logs out of the main context.
- **Durable memory:** store concise decisions and project facts; retrieve only what is relevant.
- **Design polish:** use frontend/design skills only for UI or visual deliverables.

## Constraints

- Do not auto-install third-party plugins from this template.
- Do not make Claude-specific plugins mandatory for Cline, Antigravity, Gemini, OpenRouter, or ChatGPT/Codex workflows.
- Prefer local skills that are short, inspectable, and project-owned.

## Current local skills

- `project-planner`
- `karpathy-engineer`
- `code-reviewer`
- `test-strategist`
- `docs-memory-maintainer`

## Recommended third-party integrations

- **Graphify**: `uv tool install graphifyy && graphify .` for generating a structural knowledge graph of the codebase (`GRAPH_REPORT.md`).