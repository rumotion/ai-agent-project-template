# Context Hygiene Cheatsheet

Optional reference. Read only when an agent session feels slow, expensive, or "dumb." Not part of FAST_INIT.

Applies to Claude Code, Codex, Cline, Antigravity, and any chat-style coding agent. Commands shown are Claude Code; other tools have equivalents.

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

- Tests: `npm test 2>&1 | grep -E "FAIL|✗|Error"` (or framework's `--reporter=min`).
- Search: ripgrep with `--files-with-matches` first, then read specific files.
- Logs: `tail -n 50` or `grep -A 3 ERROR`.
- Git: `git log --oneline -n 10`, not full log.
- Build: most build tools accept `--quiet` or equivalent.

## 4. Phase hygiene — close finished work

When a task is done, the agent doesn't need 50 messages of failed attempts in its head.

- `/compact` — summarize current state, replace history with summary. Use at ~70% context usage or after a feature ships.
- `/rewind` (also Esc+Esc) — jump to an earlier message; preserves file reads and learnings, drops a failed attempt.
- `/btw` (Claude Code v2.1.72+, Mar 2026) — quick question in a dismissible overlay; never enters history. Use for "what does this flag do?" while keeping main context clean.
- `/fork` — branch the session to try an alternative without polluting the original.

When in doubt: `/compact` after a passing test run, before switching feature.

## 5. Cache ordering — stable prefix, dynamic tail

Prompt caching costs ~90% less and is much faster, but caching works **top-down** and breaks at the first changed byte.

Order from top to bottom:

1. System rules (most stable) — `AGENTS.md` and adapters.
2. Tool schemas (stable).
3. Project architecture / memory-bank routing (`startup.md`, `00-index.md`).
4. Current task, history, fresh tool output (most dynamic) — at the bottom.

Anti-patterns that silently kill the cache:

- A timestamp like `Current time: 2026-05-14T14:32:15Z` near the top.
- Editing the system prompt mid-session to "change the date" or "enter plan mode" — use system-reminder messages instead.
- Bytewise-edits to `AGENTS.md` / `startup.md` / `00-index.md` / adapter files (see `memory-bank/model-routing.md` cache-stable list).

Note: prompt cache TTL is **5 minutes** (idle conversations cool fast). Caches are per-model and per-workspace.

## 6. Reasoning effort — match the task

Modern models support hidden-thinking budgets. "High" on everything wastes 20s and ~10x cost for a one-line rename.

| Task class | Reasoning effort |
|---|---|
| Rename / typo / add unit test / small UI tweak | Low / Standard |
| Bug fix with known repro | Standard |
| Refactor across <10 files | Standard / High |
| Architecture design, ghost-bug investigation, security review | High / Deep |

See per-model knobs in `memory-bank/model-routing.md`.

## 7. MCP discipline — disconnect what you aren't using

Every connected MCP server contributes tool schemas to every request — even if you never call them this session.

- Treat MCP servers like phone apps: keep the ones you use today; disconnect the rest.
- Don't leave `.mcp/` configs pointing at servers you've stopped using.
- If a tool will only be needed once a week, connect it on demand, not globally.

## 8. Cheap-worker / subagent split

For "grunt work" (scan 50 files, summarize an API, list endpoints), don't burn the senior model.

- Use a cheap model (Haiku-class, OpenRouter free tier, local model) in a side session to produce a small summary file.
- Or spawn a subagent: it runs in isolated context and returns only its final summary to your main session.

Roles map: `memory-bank/model-routing.md`.

## 9. When NOT to optimize

Skip filters and budgets during:

- **Production incidents** — give the agent full logs, full history, all tools. Token cost is irrelevant when downtime costs more.
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
- Production on fire → ignore everything above. Optimize after.
