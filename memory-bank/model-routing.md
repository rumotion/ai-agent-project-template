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

## Model selection and context

Resolve the exact model, context window, effort controls and account entitlement
from the installed client's picker and current first-party documentation. Do not
treat a product/plan name (Codex, Antigravity, Ultra) as a model ID. Use FAST_INIT
on every model; a larger window is not a reason for eager repository reads.
Use observed context percentage for handoff, not fixed 150k/250k thresholds.

## Reasoning effort / adaptive thinking

Thinking/effort controls and accepted values depend on model, API and client.
Use supported native controls, preserve an explicit user choice, and match
effort to task difficulty. Do not translate an API parameter directly into a
CLI flag or assume fixed-budget thinking works on every current model.

## Cache-stable files (do not bytewise-edit casually)

Keep stable guidance separate from volatile status; avoid incidental rewrites:

- `AGENTS.md`
- `memory-bank/startup.md`
- `memory-bank/00-index.md`
- All adapter files (`CLAUDE.md`, `GEMINI.md`, `CONVENTIONS.md`, `.windsurfrules`, `.clinerules/00-master.md`, `.agents/rules/00-master.md`, `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`)

Volatile files (safe to update often): `memory-bank/handoff.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`.

## Cache ordering rule (stable prefix, dynamic tail)

Where the client permits request ordering, put stable material before volatile
material. This is a design preference, not a measured cache guarantee:

1. System rules (`AGENTS.md`, adapters) — most stable.
2. Tool schemas — stable.
3. Memory-bank routing (`startup.md`, `00-index.md`) — mostly stable.
4. Current task, conversation history, fresh tool output — most dynamic.

Put dates, git status and mode switches in the dynamic tail. Cache matching,
minimum sizes, TTL and billing differ by provider and surface. A repository
cannot control all system/tool ordering; measure native telemetry before
claiming savings. Do not assume a universal five-minute or one-hour expiry.

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
| Initialization / planning | Available capable model in the chosen client | Another entitled provider |
| Routine implementation | Lowest-cost model that passes project checks | Stronger model after a demonstrated failure |
| Architecture / review / fixes | Model proven on representative project tasks | Independent model when review warrants it |
| Fast utility | Local or inexpensive capable model | Current client default |
| Long-context analysis | Model with a verified sufficient window | Chunked retrieval and short sessions |

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

## Optional quota pacing and goals

Default OFF; see `docs/usage-pacing.md`. Native goals continue a task but do not
measure subscription quota. Cross-client fallback is a verified task queue and
handoff. Current first-party sources: `docs/ai-market-review-2026-10.md`.
Installed-client behavior remains unverified.

Project-specific model pins: TBD. Record real model IDs and verification date
when selected; do not hardcode marketing names as universal defaults.
