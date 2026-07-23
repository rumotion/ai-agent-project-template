# Hooks — Zero-Token Automation

Hooks are commands a client runs at lifecycle events such as before or after a
tool call. They run outside the model context, so they are useful for
deterministic logging and safety checks without spending model tokens.

The canonical Python scripts are shared, while each client keeps a thin native
event mapping. Hook formats change, so `scripts/hooks/fixtures/README.md`
records the first-party schemas last checked by this template.

## Configuration shipped

| Client | Configuration | Status |
|---|---|---|
| Claude Code | `.claude/settings.json` | Active project guard and logger |
| Gemini CLI | `.gemini/settings.example.json` | Inactive example; copy deliberately to `.gemini/settings.json` |
| Codex | `.codex/hooks.example.json` | Inactive example; copy deliberately to `.codex/hooks.json` |

The active Claude permissions deny secret-file access as a first safety layer.
Its `PreToolUse` mapping calls `scripts/hooks/guard-sensitive-paths.py`, and its
`PostToolUse` mapping calls `scripts/hooks/log-writes.py`. Gemini maps the same
roles to `BeforeTool` and `AfterTool`; Codex uses `PreToolUse` and
`PostToolUse`.

## Native event mapping

| Portable role | Claude Code | Gemini CLI | Codex |
|---|---|---|---|
| Check before a write | `PreToolUse` | `BeforeTool` | `PreToolUse` |
| Log after a write | `PostToolUse` | `AfterTool` | `PostToolUse` |

Native adapters pass `--client` explicitly because all three clients share
fields such as `session_id`, `hook_event_name`, and `tool_input`. Guessing the
client from those fields is unsafe.

The sensitive-path guard emits each verified client's documented denial shape:

- Claude and Codex: `hookSpecificOutput.permissionDecision: "deny"`;
- Gemini: top-level `decision: "deny"`;
- unknown clients: an `unsupported` result that does not claim to block.

## Claude configuration shape

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/scripts/hooks/log-writes.py\" --client claude --workspace-root \"$CLAUDE_PROJECT_DIR\""
          }
        ]
      }
    ]
  }
}
```

`matcher` is a regex over the native tool name. The client supplies one JSON
event on stdin.

## Safety contract

The shipped scripts follow these rules:

1. **Standard library only** — no install step in a fresh clone.
2. **Passive logging always fails open** — malformed logger input exits `0`.
3. **Denials never echo target paths** — feedback uses a generic reason.
4. **Logs never contain contents or commands** — only normalized metadata.
5. **Paths are bounded** — workspace paths become relative, external paths
   become `<outside-workspace>`, and sensitive paths become
   `<sensitive-path>`.

Run the deterministic fixture suite with:

```bash
python scripts/hooks/verify-fixtures.py
```

It writes logs only to an OS temporary directory and verifies normalized
records, redaction, outside-workspace handling, malformed input, and all three
native denial shapes.

## Passive memory capture

```text
post-write hook -> append .agent-logs/session.jsonl metadata (0 model tokens)
                               |
                               v
              optional offline consolidation updates Memory Bank
```

Keep the hook mechanical. Put any summarization in an explicit offline step.
`.agent-logs/` is gitignored.

## Disabling

Delete the `hooks` block from `.claude/settings.json` to disable the active
Claude hooks. Gemini and Codex examples remain inactive until copied to their
native filenames. The template works without hooks.

## First-party references

- [Claude Code hooks](https://code.claude.com/docs/en/hooks-guide)
- [Gemini CLI hooks](https://geminicli.com/docs/hooks/)
- [Codex hooks](https://developers.openai.com/codex/hooks)
