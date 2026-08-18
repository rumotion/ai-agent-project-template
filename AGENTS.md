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
  the remote configuration, so a project created from this template may still point at the **template's own
  repository**. A push would then upload this project into a repository shared with unrelated projects.
  **Check `git remote -v` before any git work.** If `origin` points at the template, or at anything that is
  not this project's own repository, detach it: `python scripts/detach-remote.py`. Local commits are
  encouraged; transmission is not.
- **Never push, publish, or sync without an explicit instruction.** No `git push`, no remote branch, no pull
  request, no issue, no tag push. **Never run `git push --force --mirror`** — it uploads *every* local ref,
  including refs holding material you were asked to delete. External documentation recommends it in contexts
  where it is unsafe here.
- **One project, one repository.** Two projects must never share a repository, and the template's repository
  is never a deployment source. If hosting is needed (Vercel, Cloudflare, Netlify), a **human** creates a new
  repository for that project alone and chooses its visibility.
- **Confidential material never enters a repository that is, or ever was, public.** Removing it later does not
  work: hosts retain unreachable commits retrievable by commit ID, and forks share object storage. Treat a
  public repository as permanent.
- **`.gitignore` is not a security control.** It prevents accidents, not decisions, and only for the paths it
  was written for. Verify with `git status --ignored --short` and `git ls-files` rather than assuming.

### General

- Do not invent facts. If unknown, write `TBD` or ask.
- Do not expose or edit secrets, credentials, tokens, `.env` values, or production config unless explicitly requested.
- Ask before destructive commands, dependency installs, migrations, production-impacting actions, or broad refactors.
- Prefer small, reviewable changes that match existing style.
- Keep Memory Bank updates concise and operational.
- Do not re-read files already read in the current task unless they changed.
- **Proactive Tool Suggestion:** If codebase is too large for standard file search, suggest Graphify (`workflows/build-graph.md`). If frequent style corrections occur, suggest Calibration (`workflows/calibrate.md`).

## Engineering behavior (Karpathy defaults)

- Think before coding: state assumptions; ask when unclear.
- Detailed phased planning: break tasks into clear phases with concrete, committable step checkpoints.
- Simplicity first: solve only what was asked; avoid speculative abstractions.
- Surgical changes: touch only what the task requires.
- Goal-driven & atomic commits: define success criteria, verify each step, and commit immediately upon verification.

## Agentic execution

- Batch independent tool calls in parallel; never serialize independent reads.
- Bound each task (~5 / 15 / 30 tool calls for simple / standard / complex). Halt with a summary instead of looping.
- Classify errors before retrying: transient → backoff; logic → revise; capability → escalate (`model-routing.md`). On exhausting retries, log a one-line lesson to `memory-bank/risks.md`.
- Atomic step-commit: after verifying each completed step in a plan, run `git commit -m "<type>(<scope>): <step description>"`.
- On finishing a unit of work, write a phase summary to `memory-bank/activeContext.md` and update `handoff.md`.
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
