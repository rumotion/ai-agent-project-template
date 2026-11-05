# Context Hygiene Cheatsheet

Optional reference. Read only when an agent session feels slow, expensive, or "dumb." Not part of FAST_INIT.

Applies to Claude Code, Codex, Cline, Antigravity, and any chat-style coding agent. Commands shown are Claude Code; other tools have equivalents.

Provider-native memory is advisory and distinct from project instructions,
conversation compaction, the checked-in Memory Bank, and MCP memory. See
`docs/context-memory-bridges.md` before enabling or synchronizing any memory
feature. For measured optimization trials, use
`docs/performance-experiments.md` and `scripts/benchmark-context.py`.

## 1. Audit before you cut

You cannot optimize what you cannot see.

- `/context` — show where tokens are going (system, tools, memory, history).
- `/usage` — current limit/budget.
- `wc -w AGENTS.md CLAUDE.md memory-bank/*.md` — character/word weight of always-on files.
- `find . -name "*.log" -size +1M` (POSIX) or `Get-ChildItem -Recurse -Filter *.log | Where-Object Length -gt 1MB` (Windows) — find log bombs before the agent reads them.

If startup already shows >20k tokens before any work, investigate first.

## 2. Keep "always-on" files small

This template already enforces this via `AGENTS.md` + `memory-bank/startup.md` + lazy-loaded `docs/`. Reinforcing rules:

- `AGENTS.md` is the constitution. Strict prohibitions, stack invariants, code-style rules only.
- Reference material (architecture history, deployment, long examples) lives in `docs/` and loads only when relevant.
- `CLAUDE.md`, `GEMINI.md`, `.clinerules/`, `.agents/`, etc. are thin adapters. Never duplicate AGENTS.md content into them.

If an adapter file grows beyond ~30 lines, push the content back to `AGENTS.md` or `docs/`.

## 3. Filter tool output — never let the agent eat raw logs

Bad: "Run the tests." → agent reads 5,000 PASS lines.
Good: "Run tests, show only failures and the first error line."

Patterns:

- Tests: prefer the framework's concise reporter. Preserve its exit code and
  retain complete diagnostics for any failure; filtering must not hide failure.
- Search: ripgrep with `--files-with-matches` first, then read specific files.
- Logs: `tail -n 50` or `grep -A 3 ERROR`.
- Git: `git log --oneline -n 10`, not full log.
- Build: most build tools accept `--quiet` or equivalent.

## 3b. Batch independent tool calls

Modern models (Claude, Gemini, OpenAI) can run multiple tool calls from one response in parallel. When the next steps don't depend on each other, issue them together instead of one per turn.

- Reading 5 files in parallel costs the same wall-clock time as reading 1, and one fewer round-trip per saved turn.
- Safe to batch: independent reads, independent searches, independent status checks.
- Never batch: a write with a read of the same file, or two writes that can conflict.

See `docs/agent-loop.md` for turn/tool-call budgets and the error-and-retry taxonomy that bound a runaway loop.

## 4. Phase hygiene — close finished work

When a task is done, the agent doesn't need 50 messages of failed attempts in its head.

- `/compact` — summarize current state, replace history with summary. Use at ~70% context usage or after a feature ships.
- `/rewind` (also Esc+Esc) — jump to an earlier message; preserves file reads and learnings, drops a failed attempt.
- `/btw` (Claude Code v2.1.72+, Mar 2026) — quick question in a dismissible overlay; never enters history. Use for "what does this flag do?" while keeping main context clean.
- `/fork` — branch the session to try an alternative without polluting the original.

When in doubt: `/compact` after a passing test run, before switching feature.

## 5. Cache ordering — stable prefix, dynamic tail

Stable prompt prefixes can support provider cache reuse. Eligibility, retention,
billing and subscription-quota effects depend on the model and client. Measure
supported telemetry before claiming a saving.

Order from top to bottom:

1. System rules (most stable) — `AGENTS.md` and adapters.
2. Tool schemas (stable).
3. Project architecture / memory-bank routing (`startup.md`, `00-index.md`).
4. Current task, history, fresh tool output (most dynamic) — at the bottom.

Anti-patterns that silently kill the cache:

- A timestamp like `Current time: 2026-05-14T14:32:15Z` near the top.
- Editing the system prompt mid-session to "change the date" or "enter plan mode" — use system-reminder messages instead.
- Bytewise-edits to `AGENTS.md` / `startup.md` / `00-index.md` / adapter files (see `memory-bank/model-routing.md` cache-stable list).

There is no universal cache TTL or scope. See the current provider reference
and `memory-bank/model-routing.md`; API cache billing does not establish
subscription-quota savings.

## 6. Reasoning effort — match the task

Supported effort controls depend on model and client. Match effort to task
difficulty and measured verification outcomes; avoid universal timing or cost
multipliers.

| Task class | Reasoning effort |
|---|---|
| Rename / typo / add unit test / small UI tweak | Low / Standard |
| Bug fix with known repro | Standard |
| Refactor across <10 files | Standard / High |
| Architecture design, ghost-bug investigation, security review | High / Deep |

See per-model knobs in `memory-bank/model-routing.md`.

## 7. MCP discipline — disconnect what you aren't using

MCP discovery may load tool schemas eagerly or defer them. Inspect the actual
client context and tool discovery behavior instead of assuming every connected
tool is included in every request.

- Treat MCP servers like phone apps: keep the ones you use today; disconnect the rest.
- Don't leave `.mcp/` configs pointing at servers you've stopped using.
- If a tool will only be needed once a week, connect it on demand, not globally.

## 8. Cheap-worker / subagent split

For "grunt work" (scan 50 files, summarize an API, list endpoints), don't burn the senior model.

- Use a cheap model (Haiku-class, OpenRouter free tier, local model) in a side session to produce a small summary file.
- Or spawn a subagent: it runs in isolated context and returns only its final summary to your main session.

Roles map: `memory-bank/model-routing.md`.

## 9. When NOT to optimize

Preserve necessary diagnostic evidence during:

- **Production incidents** — expand relevant diagnostics without dropping
  confidentiality, authorization or explicit user hard limits.
- **Security review** — filtering may hide the exact byte an attacker exploits.
- **New architecture design** — "noise" often carries the business-logic context that matters.

## 10. Troubleshooting symptoms

| Symptom | Likely cause | Fix |
|---|---|---|
| Code quality dropped after `/compact` | Over-compaction lost nuance | Add the missing fact back to `AGENTS.md` or `memory-bank/activeContext.md` |
| 30–60s response times | Cache break or giant log/file read | Check for dynamic text near top of prompt; truncate the log |
| Agent loops on the same fix | Context full of failed attempts | `/rewind` to before the loop, or new session with current code + latest error only |
| Agent invents a tool that doesn't exist | Stale instructions for a disconnected MCP server | Sync `AGENTS.md` / adapter rules with actually-connected tools |
| You hit Enter then realized you forgot a detail | Don't append — that grows context | Press `Esc`, then `/rewind`; or `/btw` for a side question |
| Startup tokens climbing without code changes | New file got read eagerly | Run `/context`; move the file out of FAST_INIT read set |

## 11. Quick decision tree

- Long session, things slowing down → `/context`. If history is the bulk → `/compact`.
- About to ask a small side question → `/btw`.
- Last attempt failed, want to retry without the noise → `/rewind`.
- Want to try an alternative path without losing the current one → `/fork`.
- Need 50 files summarized → cheap model or subagent, not the senior session.
- Production incident → prioritize relevant evidence and recovery within the
  incident's authorized scope; measure optimization after stabilization.
