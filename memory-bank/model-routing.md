# Model Routing

Cross-model usage map. Read only when choosing or switching providers. Keep concise.

## Tools and auth

| Tool | Use for | Auth |
|---|---|---|
| Google Antigravity (Gemini Ultra) | Workspace-native agent, planning, broad reads | Google account |
| Claude Code / Claude Teams | Reasoning-heavy reviews, refactors, docs | Claude account or Anthropic API |
| ChatGPT Teams / Codex | Implementation, fast iteration | ChatGPT sign-in or OpenAI API |
| Cline | Local IDE coding agent | OpenRouter / direct provider key |
| OpenRouter | Multi-model fallback, free-tier exploration | OpenRouter API key |
| Cursor / Copilot | Inline edits, completions | Native sign-in |

## Per-model context budgets and tactics

| Model | Approx context | Tactic |
|---|---|---|
| Gemini Ultra (Antigravity) | ~1M | Eager reads OK; still prefer FAST_INIT to keep responses tight |
| Claude (Teams / Code) | ~200K + prompt cache | Keep `AGENTS.md`, `memory-bank/startup.md`, `memory-bank/00-index.md` byte-stable for cache hits |
| ChatGPT Teams / Codex | ~128K | Minimize tool turns; concise narration |
| OpenRouter free models | often 8K–32K | FAST_INIT mandatory; never escalate to DEEP_AUDIT |

## Cache-stable files (do not bytewise-edit casually)

These should change rarely so Claude prompt cache hits stay warm:

- `AGENTS.md`
- `memory-bank/startup.md`
- `memory-bank/00-index.md`
- All adapter files (`CLAUDE.md`, `GEMINI.md`, `.clinerules/00-master.md`, `.agents/rules/00-master.md`, `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`)

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
| Implementation | ChatGPT / Codex or Cline | OpenRouter coding model |
| Review / refactor | Claude | Gemini |
| Fast utility | OpenRouter cheap model | Cline w/ small model |
| Long-context analysis | Gemini Ultra | Claude |

## Cross-model handoff

Single rolling file: `memory-bank/handoff.md`. Workflow: `workflows/handoff.md`.

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
- Coding model: ChatGPT Teams / Codex or Cline
- Review model: Claude (Teams or Code)
- Fast/cheap model: OpenRouter free tier
- Long-context model: Gemini Ultra
