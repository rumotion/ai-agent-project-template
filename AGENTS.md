# AGENTS.md — Canonical Agent Instructions

Single source of truth for all AI agents in this repo. Adapters (`GEMINI.md`, `CLAUDE.md`, `.clinerules/`, `.agents/`, `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`) only point here.

## Startup path — keep context small

1. Read this file.
2. Read `memory-bank/startup.md`.
3. If resuming work or switching models, also read `memory-bank/handoff.md`.
4. Read `memory-bank/00-index.md` only to choose additional files.
5. Load source/docs/workflows/skills only when the task requires them.

Reserve most context for the actual project, not template instructions.

## Cross-model continuity

Multiple models may share this project (Gemini, Claude, ChatGPT/Codex, Cline, OpenRouter, Cursor, Copilot). `memory-bank/handoff.md` is the single rolling "where we left off" pointer — update on pause/switch, read on resume. Per-model budgets, cache-stable files, and routing live in `memory-bank/model-routing.md`.

## Initialization modes

### FAST_INIT (default)

Low-token initialization with verified basics only.

- Read only: `AGENTS.md`, `memory-bank/startup.md`, `memory-bank/00-index.md`, `memory-bank/handoff.md` (if resuming), and stack-detection files (`package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `tsconfig.json`, `vite.config.*`, `next.config.*`) when present.
- Do not read by default: `README.md`, `docs/`, `workflows/`, skills, `references/`, `assets/`, `.mcp/`, validator scripts.
- Update only: `memory-bank/startup.md`, `memory-bank/handoff.md`, `memory-bank/projectbrief.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`, `memory-bank/techContext.md`.
- Keep unknowns as `TBD`. Do not run full-repo audits. Minimize turns and narration.

### DEEP_AUDIT (explicit only)

Use when the user asks for full template review, publishing readiness, architecture audit, or broad cleanup. Read deeper docs/workflows/skills/scripts as needed; document findings; propose focused changes.

### Escalation rule

Start in `FAST_INIT`. Escalate only when required facts cannot be verified from allowed files, or the user explicitly asks.

## Core rules

- Do not invent facts. If unknown, write `TBD` or ask.
- Do not expose or edit secrets, credentials, tokens, `.env` values, or production config unless explicitly requested.
- Ask before destructive commands, dependency installs, migrations, production-impacting actions, or broad refactors.
- Prefer small, reviewable changes that match existing style.
- Keep Memory Bank updates concise and operational.
- Do not re-read files already read in the current task unless they changed.
- **Proactive Tool Suggestion:** If the codebase becomes too large for standard file searches, proactively suggest using Graphify (`workflows/build-graph.md`) to map the project. If the user requires frequent styling/behavior corrections, suggest running the Calibration workflow (`workflows/calibrate.md`).

## Engineering behavior (Karpathy defaults)

- Think before coding: state assumptions; ask when unclear.
- Simplicity first: solve only what was asked; avoid speculative abstractions.
- Surgical changes: touch only what the task requires.
- Goal-driven: define success criteria; verify with the smallest useful check.

## Workflow

Implementation tasks: understand → plan → implement → verify → document. For risky work use procedures in `workflows/`.

## Memory Bank

Start with `memory-bank/startup.md`; lazy-load via `memory-bank/00-index.md`; update only files whose facts changed.

## More detail (lazy-load)

- Prompts: `docs/prompts.md`
- Antigravity/Cline master setup: `docs/antigravity-master-prompt.md`
- Skills/plugins: `docs/agent-skill-ecosystem.md`
- Model/provider routing: `memory-bank/model-routing.md`
