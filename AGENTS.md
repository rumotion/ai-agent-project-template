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

- **This project is local-only until a human says otherwise in the current conversation.** `git clone` copies
  the remote configuration, so a derived project may still point at the **template's own repository**. A push
  would upload this project into a repository shared with unrelated projects. **Check `git remote -v` before any git work.**
  If `origin` points at the template or anything not this project's own repository, detach it:
  `python scripts/detach-remote.py`. Local commits are encouraged; transmission is not.
- **Never push, publish, or sync without an explicit instruction.** No `git push`, no remote branch, no pull
  request, no issue, no tag push. **Never run `git push --force --mirror`** — it uploads *every* local ref,
  including refs holding material meant to be deleted.
- **One project, one repository.** Two projects must never share a repository; the template repo is never a
  deployment source. If hosting is needed (Vercel, Cloudflare, Netlify), a **human** creates a dedicated repository
  and chooses its visibility.
- **Confidential material never enters a repository that is, or ever was, public.** Removing it later does not
  work: hosts retain unreachable commits retrievable by commit ID, and forks share object storage. Treat a
  public repository as permanent.
- **`.gitignore` is not a security control.** It prevents accidents, not decisions, and only for targeted paths.
  Verify with `git status --ignored --short` and `git ls-files` rather than assuming.

### General

- Do not invent facts. If unknown, write `TBD` or ask.
- Do not expose or edit secrets, credentials, tokens, `.env` values, or production config unless explicitly requested.
- Ask before destructive commands, dependency installs, migrations, production-impacting actions, or broad refactors.
- Prefer small, reviewable changes that match existing style.
- Keep Memory Bank updates concise and operational.
- Do not re-read files already read in the current task unless they changed.
- **Proactive Tool Suggestion:** If codebase is too large for standard file search, suggest Graphify (`workflows/build-graph.md`). If frequent style corrections occur, suggest Calibration (`workflows/calibrate.md`).

## Engineering behavior (Karpathy defaults)

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
- Prompts: `docs/prompts.md`
- Antigravity/Cline master setup: `docs/antigravity-master-prompt.md`
- Skills/plugins: `docs/agent-skill-ecosystem.md`
- Hooks (Claude Code automation): `docs/hooks.md`
- Model/provider routing: `memory-bank/model-routing.md`
