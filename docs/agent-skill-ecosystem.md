# Agent Skill Ecosystem

Keep this guidance out of the startup path. Read it only when choosing or designing skills/plugins.

## Portable skill layout

`.agents/skills/` is the canonical, project-owned skill source. Gemini and
ChatGPT/Codex discover skills there directly. Claude reads byte-for-byte mirrors
from `.claude/skills/`, and Cline reads byte-for-byte mirrors from
`.cline/skills/`. The template validator compares mirrored `SKILL.md` files to
their canonical source with SHA-256 so an adapter cannot silently drift.

Each skill lives in a named directory with a `SKILL.md` entry point. Keep the
YAML front matter valid and limited to the portable `name` and `description`
fields; put operational instructions in the Markdown body. Load only the
selected `SKILL.md` first, then follow links to scripts, references, or assets
only when the active task requires them. This progressive disclosure keeps
normal startup context small while preserving richer, task-specific guidance.

## Selection rule

Add skills/plugins only when they clearly:

- save time,
- reduce cost,
- reduce human error, or
- improve verification for risky work.

## Useful patterns

- **Skill creator/factory:** turn repeatable SOPs into small auditable skills.
- **Skill chaining:** break workflows into atomic skills and chain them sequentially (for example, `project-planner` -> `karpathy-engineer` -> `code-reviewer`).
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
- `delegation-coordinator` (see `docs/subagent-contract.md`)

## Recommended third-party integrations

- **Graphify**: `uv tool install graphifyy && graphify .` for generating a structural knowledge graph of the codebase (`GRAPH_REPORT.md`).
