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

The active Claude permissions deny secret-file access and publishing commands
as a first safety layer. Its `PreToolUse` mapping calls
`scripts/hooks/guard-sensitive-paths.py` on writes and both
`guard-sensitive-paths.py` (shell redirection/copy targets) and
`scripts/hooks/guard-remote-ops.py` on shell commands; its `PostToolUse`
mapping calls `scripts/hooks/log-writes.py`. Gemini maps the same roles to
`BeforeTool` and `AfterTool`; Codex uses `PreToolUse` and `PostToolUse`.

## Shipped hook scripts

| Script | Role | Behavior on trigger |
|---|---|---|
| `guard-sensitive-paths.py` | Block writes to secrets | Denies; reason never echoes the path |
| `guard-remote-ops.py` | Block unauthorized publishing | Denies; reason never echoes the command |
| `log-writes.py` | Passive write audit | Appends metadata only to `.agent-logs/` |
| `session-context.py` | Startup injection / compaction flush | Emits `additionalContext`; never blocks |
| `git/pre-push` (sh) | Local accident prevention | Denies all ordinary pushes |

### Advisory shell guards

The guards deny the reproduced publishing and sensitive-write cases when a
supported client supplies the expected event and consumes the denial. The
adversarial corpus covers wrappers, aliases, Git configuration, shell functions,
heredoc expansion, quoted arguments, redirection, copy/tee flags, PowerShell
writes, patch input, and command payload aliases. Literal Python print statements
are allowed; other inline Python is conservatively denied by the remote guard.
Malformed payloads fail open and unsupported clients do not claim enforcement.
Arbitrary programs, file execution, connectors and parser gaps remain outside
this advisory coverage. Synthetic fixtures prove script decisions, not live
client behavior or hostile-process containment.

### Local-only pre-push backstop

`scripts/push_backstop.py` is shared by init, new-project, and upgrade. It resolves
Git's actual hook path, including linked worktrees, installs an unconditional
LF-only block, and recognizes an existing strict detach-remote hook. Unknown
hooks are preserved and initialization fails explicitly; custom `core.hooksPath`
requires deliberate integration. There is no environment-variable escape hatch.

This prevents ordinary accidental pushes when installed and enabled. A process
able to alter Git configuration, use `--no-verify`, invoke `send-pack`, or use
another network client can bypass it. Publishing remains subject to the user's
current authorization. This template supplies no release launcher.

```bash
python scripts/boundary.py inspect --client codex --json
python scripts/boundary.py verify --profile advisory
```

Inspection reports six control booleans and bounded limitations, matching
`schemas/boundary-inspection.schema.json`. Advisory verification checks only the
installed push hook. `contained-local` and `release` return failure: no external
supervisor, egress isolation or protected-path isolation has been supplied.
`schemas/adapter-capabilities.json` lists all ten clients, candidate tool names,
configuration status, synthetic fixtures, and missing live evidence/version.
Unknown MCP coverage is explicit; adapter entries are not certified integrations.

### Compiled startup context and continuity

Claude's `SessionStart` hook compiles typed `memory-bank/records/` and handoff
status through the same compiler used by CLI validation. Durable records precede
volatile status. Invalid or oversized projections produce a diagnostic instead
of partial context. The compiler is loaded from the trusted hook's sibling
script, never from an event-selected workspace. The maximum injected output is
8,000 characters; the compiler's default projection cap is 6,000.

`PreCompact` reminds the parent to persist handoff, active context, decisions and
risks. Lifecycle injection is best-effort and exits zero. Other clients retain
the documented manual FAST_INIT path until native lifecycle behavior is verified.
Injected context is validated project data; current user instructions take
precedence. Injected bytes still consume model context and are not free tokens.

## Native event mapping

| Portable role | Claude Code | Gemini CLI | Codex |
|---|---|---|---|
| Check before a write | `PreToolUse` | `BeforeTool` | `PreToolUse` |
| Check before a shell command | `PreToolUse` | `BeforeTool` | `PreToolUse` |
| Log after a write | `PostToolUse` | `AfterTool` | `PostToolUse` |
| Inject startup context | `SessionStart` | (no verified equivalent) | (no verified equivalent) |
| Persist state before compaction | `PreCompact` | (no verified equivalent) | (no verified equivalent) |

`SessionStart` and `PreCompact` are currently Claude-only in this template. The
portable fallback is unchanged: `AGENTS.md` still instructs every agent to read
`memory-bank/startup.md` first and to update `handoff.md` on pause or switch.
The hooks make that deterministic where the client supports it; they never
become the only mechanism.

Native adapters pass `--client` explicitly because all three clients share
fields such as `session_id`, `hook_event_name`, and `tool_input`. Guessing the
client from those fields is unsafe.

The sensitive-path guard emits the denial shapes exercised by synthetic fixtures:

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
6. **Context injection never blocks** — `session-context.py` always exits `0`
   and emits nothing it cannot read.
7. **Injected context is size-capped** — so hooks cannot defeat the FAST_INIT
   budget.

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
