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

Multiple models share this project (Gemini, Claude, Codex, Cline, Cursor, Copilot). `memory-bank/handoff.md` is the rolling "where we left off" pointer — update on pause/switch, read on resume. Model routing lives in `memory-bank/model-routing.md`.

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

### Repository boundaries — read before any git command

- **This project is local-only until human says otherwise in current conversation.** Check `git remote -v` before any git work. If `origin` points to the template repo, detach: `python scripts/detach-remote.py`. Local commits encouraged; transmission forbidden.
- **Never push, publish, or sync without explicit instruction.** No `git push`, remote branch, PR, issue, or tag push. Never run `git push --force --mirror`.
- **One project, one repository.** Never share a repo between projects. Humans create dedicated repos for hosting (Vercel, Cloudflare, Netlify).
- **Confidential material never enters a repository that is or was public.** Removing later does not work (commits retrievable, forks share objects).
- **`.gitignore` is not a security control.** Verify with `git status --ignored --short` and `git ls-files`.

### Media & Transcription (Local GPU-Only)

- **Always GPU-first (`large-v3`):** Audio/video transcription runs locally on GPU (RTX A5000) via `faster-whisper` (`scripts/transcribe_local_large_v3.py`). Never downgrade model size (32 layers).
- **Precision ladder & privacy:** `cuda/float16` -> `cuda/int8_float16` -> CPU chunked. 100% confidential; media and transcripts never leave workstation.

### General


- Do not invent facts. If unknown, write `TBD` or ask.
- Do not expose or edit secrets, credentials, tokens, `.env` values, or production config unless explicitly requested.
- Ask before destructive commands, dependency installs, migrations, production-impacting actions, or broad refactors.
- Prefer small, reviewable changes that match existing style.
- Keep Memory Bank updates concise and operational.
- Do not re-read files already read in the current task unless they changed.
- **HARD RULE — anything the user sends under their own name must read as human-written.** Apply `.agents/skills/human-voice-drafting/SKILL.md`; repo files are exempt.
- **Proactive Tool Suggestion:** If codebase is too large for standard file search, suggest Graphify (`workflows/build-graph.md`). If frequent style corrections occur, suggest Calibration (`workflows/calibrate.md`).

## Engineering behavior (Karpathy defaults & Cognitive Harness)

- Cognitive harness (`assets/LLM_PROJECT_HARNESS.md`, `.agents/rules/30-cognitive-harness.md`): candid thinking partner, challenge unsound assumptions, ground in evidence, evaluate before committing, execute to verified completion.
- Think before coding: state falsifiable prediction (expected baseline failure vs expected passing outcome).
- Phased planning: discrete, committable step checkpoints with verification criteria.
- Simplicity & surgical changes: solve only what was asked; touch only necessary lines.
- Escalation ladder: escalate diagnostics (surgical fix → scratch script → mock harness → model redesign).
- Goal-driven atomic commits: verify each step and commit immediately upon verification.

## Agentic execution

- Bimodal discipline: single narrow probes for exploration; batch independent calls for verified execution.
- Bound tasks (~5 / 15 / 30 tool calls for simple / standard / complex). Halt with summary on limit.
- Classify errors: transient → backoff; logic → revise; capability → escalate (`model-routing.md`). Log disproven hypotheses and killing evidence to `activeContext.md` / `risks.md`.
- Atomic step-commit: after verifying each completed step, run `git commit -m "<type>(<scope>): <step description>"`.
- Phase summary: on completing a work unit, write summary to `memory-bank/activeContext.md` and update `handoff.md`.
- Detail: `docs/agent-loop.md`.

## Workflow

Implementation tasks: understand → plan → implement → verify → commit → document. For risky work use procedures in `workflows/`.

## Memory Bank

Start with `memory-bank/startup.md`; lazy-load via `memory-bank/00-index.md`; update only files whose facts changed.

## More detail (lazy-load)

- Agent execution loop (budgets, errors, phase summary): `docs/agent-loop.md`
- Subagent delegation contract: `docs/subagent-contract.md`
- Prompts: `docs/prompts.md`
- Antigravity/Cline master setup: `docs/antigravity-master-prompt.md`
- Skills/plugins: `docs/agent-skill-ecosystem.md`
- Hooks & safety guards (Antigravity, Claude, Codex): `docs/hooks.md`
- Model/provider routing: `memory-bank/model-routing.md`
