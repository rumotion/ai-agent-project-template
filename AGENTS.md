# AGENTS.md — Canonical Agent Instructions

This is the single source of truth for AI agents in this repo. Adapters (`GEMINI.md`, `CLAUDE.md`, `.clinerules/`, `.agents/`) must only point here and must not conflict.

## Startup path — keep context small

1. Read this file.
2. Read `memory-bank/startup.md`.
3. Read `memory-bank/00-index.md` only to choose additional relevant files.
4. Load source, docs, workflows, and skills only when the task requires them.

Most context should be reserved for the actual project, not template instructions.

## Initialization modes

Use these explicit modes when users ask to initialize a copied project.

### FAST_INIT (default)

Goal: low-token initialization with verified basics only.

- Read only: `AGENTS.md`, `memory-bank/startup.md`, `memory-bank/00-index.md`, `README.md`, and stack-detection files (`package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `tsconfig.json`, `vite.config.*`, `next.config.*`) when present.
- Do not read by default: `docs/`, `workflows/`, `.cline/skills/`, `.agents/skills/`, `references/`, `assets/`, `.mcp/`, or validator scripts.
- Update only: `memory-bank/startup.md`, `memory-bank/projectbrief.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`, `memory-bank/techContext.md`.
- Keep unknowns as `TBD`.
- Do not run full-repo audits unless requested.
- Prefer concise execution: minimize tool turns and keep final summaries short.

### DEEP_AUDIT (explicit request only)

Use when the user asks for full template review, publishing readiness, architecture audit, or broad cleanup.

- Read deeper docs/workflows/skills/scripts as needed.
- Run broader checks/validation when relevant.
- Document findings and propose focused changes.

### Escalation rule

Start in `FAST_INIT`. Escalate only when required facts cannot be verified from allowed files, or when the user explicitly asks for deeper inspection.

## Core rules

- Do not invent facts. If unknown, write `TBD` or ask.
- Do not expose or edit secrets, credentials, tokens, `.env` values, or production config unless explicitly requested.
- Ask before destructive commands, dependency installs, migrations, production-impacting actions, or broad refactors.
- Prefer small, reviewable changes that match existing style.
- Keep Memory Bank updates concise and operational.
- Do not re-read files already read in the current task unless they changed or the user asks.

## Engineering behavior

Use these Karpathy-style defaults:

- Think before coding: state assumptions, surface ambiguity, ask when unclear.
- Simplicity first: solve only what was asked; avoid speculative abstractions.
- Surgical changes: touch only what the task requires; do not clean unrelated code.
- Goal-driven execution: define success criteria, verify with the smallest useful check, then iterate if needed.

## Workflow

For implementation tasks: understand -> plan -> implement -> verify -> document. For complex or risky work, use relevant workflows in `workflows/` or tool-specific mirrors.

## Memory Bank

- Start with `memory-bank/startup.md`.
- Use `memory-bank/00-index.md` to lazy-load deeper context.
- After meaningful work, update only relevant Memory Bank files.

## More detail

- Prompt library: `docs/prompts.md`
- Antigravity/Cline setup prompt: `docs/antigravity-master-prompt.md`
- Optional skill/plugin guidance: `docs/agent-skill-ecosystem.md`
- Model/provider routing: `memory-bank/model-routing.md`