# AGENTS.md — Canonical Agent Instructions

Canonical instructions for all agents in this repo. Client adapters point here.

## Startup path — keep context small

1. Read this file.
2. Read `memory-bank/startup.md`.
3. If resuming work or switching models, also read `memory-bank/handoff.md`.
4. Read `memory-bank/00-index.md` only to choose additional files.
5. Load source/docs/workflows/skills only when the task requires them.

Reserve most context for the actual project, not template instructions.

## Cross-model continuity

All clients share `memory-bank/handoff.md`: update on pause/switch, read on resume. Routing: `memory-bank/model-routing.md`.

## Initialization modes

### FAST_INIT (default)

Follow the startup path above. Read present stack manifests/configs (`package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `tsconfig.json`, `vite.config.*`, `next.config.*`).
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

- Transcribe locally with Whisper `large-v3` (32 layers), RTX A5000 first, via `scripts/transcribe_local_large_v3.py`. Never reduce model size.
- Fallback: `cuda/float16` -> `cuda/int8_float16` -> CPU chunked. Media and transcripts never leave the workstation.

### General


- Do not invent facts. If unknown, write `TBD` or ask.
- Write repository documentation and commit messages in English. Match the user's language in chat.
- Do not expose or edit secrets, credentials, tokens, `.env` values, or production config unless explicitly requested.
- Ask before destructive commands, dependency installs, migrations, production-impacting actions, or broad refactors.
- Prefer small, reviewable changes that match existing style.
- Keep Memory Bank updates concise and operational.
- Do not re-read files already read in the current task unless they changed.
- **HARD RULE — anything the user sends under their own name must read as human-written.** Apply `.agents/skills/human-voice-drafting/SKILL.md`; repo files are exempt.
- **Proactive Tool Suggestion:** If codebase is too large for standard file search, suggest Graphify (`workflows/build-graph.md`). If frequent style corrections occur, suggest Calibration (`workflows/calibrate.md`).

## Engineering and execution

- Define the observable success check first; state baseline and expected outcome. Use a short plan for routine work, phases for complex work. Detail: `docs/agent-loop.md`.
- Inspect the real flow, then reuse existing behavior, configuration or code before adding code. Keep validation, error handling, security and accessibility.
- Delegate ready, bounded tasks only: one worker by default, two open tasks unless explicitly planned otherwise. Review/blocked work counts as open. Accept results before releasing dependents; no recursive spawning. See `docs/subagent-contract.md`.
- Verify each step, then commit locally: `git commit -m "<type>(<scope>): <step>"`. Document completed work in `activeContext.md` and `handoff.md`.
- Batch independent reads/checks; keep dependent operations sequential. Escalate diagnostics only when evidence requires it.
- Use ~5 / 15 / 30 calls as diagnostic checkpoints, not forced task termination. Stop unproductive retries; continue authorized work while making measurable progress.
- Record consequential disproven hypotheses and evidence; classify failures before retrying (`docs/agent-loop.md`).
- Apply the cognitive harness proportionately; load `assets/LLM_PROJECT_HARNESS.md` only for deeper guidance.

## Optional usage pacing

If asked to maximize tokens/quota or pace agents, read `docs/usage-pacing.md`. Explain the concrete plan, resource use and stop conditions, then wait for separate human confirmation before activation. Default OFF on every client; never auto-resume after a handoff. Useful work and verified completion take priority over consuming quota.

## More detail (lazy-load)

- Agent execution loop (budgets, errors, phase summary): `docs/agent-loop.md`
- Subagent delegation contract: `docs/subagent-contract.md`
- Prompts: `docs/prompts.md`
- Antigravity/Cline master setup: `docs/antigravity-master-prompt.md`
- Skills/plugins: `docs/agent-skill-ecosystem.md`
- Hooks & safety guards (Antigravity, Claude, Codex): `docs/hooks.md`
- Model/provider routing: `memory-bank/model-routing.md`
- Local cross-client mail assessment: `docs/local-agent-mail.md`
