# Model Routing

Cross-model usage map. Read only when choosing or switching providers. Keep concise.

## Tools and auth

| Tool | Use for | Auth | Adapter file |
|---|---|---|---|
| Google Antigravity / Gemini CLI | Workspace-native agent, planning, broad reads | Google account | `GEMINI.md`, `.agents/` |
| Claude Code / Claude Teams | Reasoning-heavy reviews, refactors, docs | Claude account or Anthropic API | `CLAUDE.md`, `.claude/` |
| ChatGPT Teams / Codex CLI | Implementation, fast iteration | ChatGPT sign-in or OpenAI API | `AGENTS.md` (native), `.codex/AGENTS.md` |
| Cline | Local IDE coding agent | OpenRouter / direct provider key | `.clinerules/` |
| Roo Code | Local IDE coding agent (Cline fork) | OpenRouter / direct provider key | `.clinerules/` (compatible — no separate adapter) |
| Cursor | Inline edits, agent mode | Native sign-in | `.cursor/rules/*.mdc` |
| Windsurf (Codeium) | Cascade agent, inline edits | Native sign-in | `.windsurfrules` |
| GitHub Copilot | Inline completions, Copilot agent | Native sign-in | `.github/copilot-instructions.md` |
| Aider | Terminal pair-programmer | Direct provider key | `CONVENTIONS.md` via `.aider.conf.yml` |
| OpenRouter | Multi-model fallback, free-tier exploration | OpenRouter API key | (depends on host tool) |

## Per-model context budgets and tactics

| Model | Approx context | Tactic |
|---|---|---|
| Claude Opus / Sonnet (current) | up to ~1M + prompt cache | Large window, but still prefer FAST_INIT — keep `AGENTS.md`, `memory-bank/startup.md`, `memory-bank/00-index.md` byte-stable for cache hits. Match `effort` to task (see below). |
| Claude Haiku (current) | ~200K | Fast/cheap tier for grunt work and subagents |
| Gemini 2.5 Pro / Flash | ~1M+ | Eager reads OK; still prefer FAST_INIT to keep responses tight |
| GPT / o-series (Codex) | ~128K–200K | Minimize tool turns; concise narration |
| OpenRouter free models | often 8K–32K | FAST_INIT mandatory; never escalate to DEEP_AUDIT |

Context windows grow over time — verify the current figure for your exact model rather than trusting this table. The tactic column is the durable part.

## Reasoning effort / adaptive thinking

Current frontier models expose a thinking control instead of (or alongside) a fixed token budget:

- **Claude** — `effort` (`low` / `medium` / `high`) with adaptive thinking; the model decides how much to think. Manual fixed `budget_tokens` is being phased out on the newest models. Default high effort on the largest models; lower it for trivial tasks.
- **OpenAI o-series** — `reasoning_effort`.
- **Gemini** — `thinking_budget` / dynamic thinking.

Match effort to the task class in the table below; do not run "high" on every rename.

## Cache-stable files (do not bytewise-edit casually)

These should change rarely so Claude prompt cache hits stay warm:

- `AGENTS.md`
- `memory-bank/startup.md`
- `memory-bank/00-index.md`
- All adapter files (`CLAUDE.md`, `GEMINI.md`, `CONVENTIONS.md`, `.windsurfrules`, `.clinerules/00-master.md`, `.agents/rules/00-master.md`, `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`)

Volatile files (safe to update often): `memory-bank/handoff.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`.

## Cache ordering rule (stable prefix, dynamic tail)

Prompt caching works top-down and breaks at the first changed byte. Order request material from most stable to most dynamic:

1. System rules (`AGENTS.md`, adapters) — most stable.
2. Tool schemas — stable.
3. Memory-bank routing (`startup.md`, `00-index.md`) — mostly stable.
4. Current task, conversation history, fresh tool output — most dynamic.

Anti-patterns: timestamps near the top, mid-session edits to the system prompt, casual rewrites of cache-stable files. Put dynamic facts (date, git status, mode switch) in user/system-reminder messages, not in the cached prefix. TTL is ~5 minutes; idle conversations cool fast.

## Reasoning effort defaults

Match thinking budget to task class — "high" on everything wastes time and tokens.

| Task class | Effort |
|---|---|
| Rename, typo, single-file unit test, small UI tweak | Low / Standard |
| Bug fix with known repro | Standard |
| Refactor across <10 files | Standard / High |
| Architecture design, ghost-bug investigation, security review | High / Deep |

Set per-model knobs (Claude `thinking`, OpenAI `reasoning_effort`, Gemini equivalents) accordingly. See `docs/context-hygiene.md` for the full hygiene cheatsheet.

## Role routing (default)

| Role | Preferred | Fallback |
|---|---|---|
| Initialization / planning | Gemini (Antigravity) | Claude |
| Routine implementation | Gemini 3.6 Flash High | ChatGPT / Codex or Cline |
| Architecture / review / fixes | ChatGPT / Codex or Claude | Gemini 3.6 Flash High |
| Fast utility | OpenRouter cheap model | Cline w/ small model |
| Long-context analysis | Gemini Ultra | Claude |

## Cascade routing (cheapest-capable first)

For a task of uncertain complexity, start with the cheapest capable model and escalate only on a real signal:

1. Try the cheap/fast tier first (Haiku-class, OpenRouter, local model).
2. Escalate to a stronger model when **any** of these holds:
   - the same tool call fails twice for the same reason,
   - the model reports it cannot proceed / low confidence,
   - verification (tests, critic, lint) fails twice on the same step.
3. Do **not** escalate for transient errors (rate limit, network) — retry with backoff instead (see error taxonomy in `AGENTS.md`).

Keep escalation explicit in `handoff.md` so the next session knows why the tier changed.

## Cross-model handoff

Single rolling file: `memory-bank/handoff.md` (structured YAML header + prose). Workflow: `workflows/handoff.md`.

Provider-native recall is optional and advisory; it never outranks checked-in
state, tests, or the Memory Bank. See `docs/context-memory-bridges.md` for the
authority order and current Gemini/Codex/Claude controls.

## Antigravity sub-agent notes

- Antigravity's Codex sub-agent reads root `AGENTS.md` natively; no separate adapter needed beyond `.codex/AGENTS.md`.
- Use `.agents/rules/`, `.agents/skills/`, `.agents/workflows/` for Antigravity-specific behavior.
- Switch between Antigravity native and external CLIs by updating `handoff.md` first.

## Rules

- Do not assume consumer subscriptions can be used inside every third-party extension.
- Prefer official sign-in paths where available.
- For Cline, prefer OpenRouter or direct API keys when subscription OAuth is unsupported.
- Use FAST_INIT by default; escalate to DEEP_AUDIT only when needed.
- Record project-specific overrides below.

## Current defaults

- Planning model: Gemini Ultra (Antigravity)
- Routine coding model: Gemini 3.6 Flash High
- Architecture & review model: ChatGPT Teams / Codex or Claude
- Fast/cheap model: OpenRouter free tier
- Long-context model: Gemini Ultra
