# Hooks — Zero-Token Automation

Hooks are shell commands a tool runs at lifecycle events (session start, before/after a tool call, on stop). They run **outside the model context**, so they cost zero tokens — ideal for logging, formatting, safety gates, and passive memory capture.

This page documents the **Claude Code** hooks system, which this template wires up by example. Other tools have their own mechanisms (Cursor/Cline have their own settings; Aider has `--lint-cmd` / `--test-cmd`); the *patterns* here transfer even when the config format differs. Always confirm the exact schema against your tool's current docs — hook formats change.

## Where it's configured

`.claude/settings.json` (project-scoped, checked into git) or `~/.claude/settings.json` (user-global). This template ships a project file with:

- **Permissions** — an `allow`/`deny` list. The denies block reads/writes of secret files (`.env`, `*.pem`, `*.key`) as a safety net.
- **A PostToolUse hook** — runs [`.claude/hooks/log-writes.py`](../.claude/hooks/log-writes.py) after every `Write`/`Edit`.

## Common lifecycle events

| Event | Fires | Typical use |
|---|---|---|
| `SessionStart` | Session begins | Print/inject startup context, set env |
| `UserPromptSubmit` | Before a prompt is sent | Inject reminders, redact secrets |
| `PreToolUse` | Before a tool runs | Safety gate (block dangerous Bash) |
| `PostToolUse` | After a tool completes | Log writes, auto-format, run quick checks |
| `Stop` | Agent finishes a turn | Summarize, flush logs |

Exact event names and output fields are version-specific — verify in your installed version.

## The config shape

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "python .claude/hooks/log-writes.py" }
        ]
      }
    ]
  }
}
```

`matcher` is a regex over the tool name (empty string = all tools). The hook receives a JSON event on **stdin**.

## Writing a safe hook

The shipped `log-writes.py` follows three rules every hook should:

1. **Standard library only** — no install step, runs in a fresh clone.
2. **Never block the agent** — swallow all errors and exit `0` (unless the hook's *job* is to block, e.g. a `PreToolUse` safety gate).
3. **Never log file contents** — paths and metadata only, so logs are safe to keep.

## Pattern: passive memory capture ("Dream Phase")

The high-value use of hooks for this template:

```
PostToolUse hook  ──>  append JSON line to .agent-logs/session.jsonl   (0 tokens)
                              │
                              ▼  (run manually, or on a schedule)
              an offline consolidation step reads the log and
              updates memory-bank/*.md with what actually changed
```

Keep the hook dumb (just append). Put any intelligence in the offline step so it never spends live session tokens. `.agent-logs/` is gitignored. This realizes the consolidation idea tracked in `docs/toolbox.md` §4.

## Disabling

Delete the `hooks` block from `.claude/settings.json` (or the whole file) to opt out. The template works fine without hooks; they are an optional power-up.
