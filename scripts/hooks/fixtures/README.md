# Hook Event Fixtures

Redacted hook event payloads used to test canonical hook scripts (`log-writes.py` and `guard-sensitive-paths.py`) without external network or provider calls.

## Provenance and specifications

These minimized fixtures follow the current first-party hook schemas. Dynamic,
absolute, and content-bearing values are replaced with redacted placeholders.

| Client | Events | Verified source | Verification date |
|---|---|---|---|
| Claude Code | `PostToolUse` / `PreToolUse` | [Claude Code hooks](https://code.claude.com/docs/en/hooks-guide) | 2026-07-23 |
| Gemini CLI | `AfterTool` / `BeforeTool` | [Gemini CLI hooks reference](https://geminicli.com/docs/hooks/reference/) | 2026-07-23 |
| Codex | `PostToolUse` / `PreToolUse` | [Codex hooks](https://developers.openai.com/codex/hooks) | 2026-07-23 |

## Included Fixtures

- `claude-write.json`: Valid file write event payload for Claude Code.
- `claude-sensitive.json`: Write attempt to sensitive `.env` path for Claude Code.
- `claude-malformed.json`: Invalid/malformed JSON event for Claude Code.
- `gemini-write.json`: Valid file write event payload for Gemini CLI.
- `gemini-sensitive.json`: Write attempt to a sensitive credential path for Gemini CLI.
- `gemini-malformed.json`: Invalid/malformed JSON event for Gemini CLI.
- `codex-write.json`: Valid file write event payload for Codex CLI.
- `codex-sensitive.json`: Patch attempt to a sensitive key path for Codex.
- `codex-malformed.json`: Invalid/malformed JSON event for Codex CLI.
