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

Start from a demonstrated recurring failure or a client discovery requirement.
Do not add a skill just to restate general model competence. Before deleting
one, compare representative tasks with/without it using the same checks,
model and settings; retain project-specific invariants. No universal skill
win/loss ratio is assumed. Long references benefit from a short contents list;
tiny entry points do not need a ceremonial checklist.

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

- `project-planner` — creates structured implementation plans from requirements
- `karpathy-engineer` — surgical, falsifiable, simplicity-first engineering behavior
- `code-reviewer` — reviews diffs for correctness, security, maintainability, and tests
- `test-strategist` — designs test suites and characterization harnesses
- `docs-memory-maintainer` — keeps Memory Bank and documentation synchronized
- `delegation-coordinator` — orchestrates subagents across model surfaces (`docs/subagent-contract.md`)
- `project-upgrader` — upgrades projects to latest template standards (`docs/upgrade-existing-project.md`)
- `human-voice-drafting` — mandatory for any message sent under the user's name (enforced in `AGENTS.md`)
- `local-media-transcription` — local GPU-accelerated Whisper large-v3 transcription with zero cloud leakage
- `sharepoint-teams-video-transcript-downloader` — downloads Teams/SharePoint recordings and 100% complete transcripts
- `storm-research` — 4-phase adversarial multi-perspective research briefing with verified citations and HTML deliverable
- `usage-pacing` — explicit-request quota planning; activation requires separate human confirmation

The ten canonical `workflows/*.md` also have thin skill entry points using
their workflow names. These preserve current Antigravity slash discovery
after its October 19, 2026 workflow migration; they link to the original
procedures instead of duplicating them. `gen-adapters.py` maintains their
Claude/Cline mirrors. Existing legacy workflow mirrors remain for older clients.
The upgrader refuses before writing if one of these newly reserved names (or
`usage-pacing`) collides with differing custom skill content. Resolve the
naming conflict deliberately; custom project instructions must be preserved.
[Google migration guide](https://antigravity.google/docs/migration/workflows-to-skills/).


## Recommended third-party integrations

- **Graphify**: `uv tool install graphifyy && graphify .` for generating a structural knowledge graph of the codebase (`GRAPH_REPORT.md`).
