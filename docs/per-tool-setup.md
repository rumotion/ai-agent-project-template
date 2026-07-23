# Per-Tool Setup

How to connect each tool to the template's shared core: root `AGENTS.md`, the
Memory Bank, portable workflows, and canonical skills. Provider adapters are
discovery pointers only; they must not become independent policy files.

For the verified Gemini, Codex, and Claude paths, status, smoke checks, and
official sources, see
[`agent-compatibility.md`](agent-compatibility.md).

## Instruction file each tool reads

| Tool | File it loads | In this template | Notes |
|---|---|---|---|
| Gemini CLI / Antigravity | `GEMINI.md` | Ships | Imports root `AGENTS.md`; project skills use the `.agents/skills` alias |
| OpenAI Codex | Root `AGENTS.md` | Canonical | Reads the canonical file natively; `.codex/AGENTS.md` contains no independent policy |
| Claude Code | `CLAUDE.md` | Ships | Imports root `AGENTS.md`; project skills are mirrored to `.claude/skills` |
| Cline | `.clinerules/` | Ships | Adapter points to `AGENTS.md` |
| Roo Code | `.clinerules/` | Reuses | Cline-compatible adapter |
| Cursor | `.cursor/rules/*.mdc` | Ships | Adapter uses required MDC frontmatter |
| Windsurf | `.windsurfrules` | Ships | Root adapter |
| GitHub Copilot | `.github/copilot-instructions.md` | Ships | Repository instruction adapter |
| Aider | `CONVENTIONS.md` via `.aider.conf.yml` | Ships | Configuration loads the pointer read-only |

Conventions change. If an installed client no longer matches this table, verify
its current official documentation and update the thin adapter. Keep universal
content in `AGENTS.md`.

## First run

1. Open the repository root in the agent.
2. Paste an initialization prompt from [`prompts.md`](prompts.md), or run
   `python scripts/init-fast.py` and paste its prompt.
3. Confirm the agent follows `AGENTS.md` -> `memory-bank/startup.md` and only
   lazy-loads additional context.

## MCP (optional tools and context)

MCP server intent can be shared, but the project configuration file is
client-specific:

| Client | Native project config | Server key |
|---|---|---|
| Gemini CLI | `.gemini/settings.json` | `mcpServers` |
| OpenAI Codex | `.codex/config.toml` | `[mcp_servers.<name>]` |
| Claude Code | `.mcp.json` at the repository root | `mcpServers` |
| VS Code | `.vscode/mcp.json` | `servers` |

The checked-in root `.mcp.json` activates the filesystem, git, and memory starters for Claude Code. Inactive native example configurations are provided for Gemini ([`.gemini/settings.example.json`](../.gemini/settings.example.json)) and Codex ([`.codex/config.example.toml`](../.codex/config.example.toml)).

Use [`.mcp/README.md`](../.mcp/README.md) for transport and trust guidance and
[`mcp_config.example.json`](../.mcp/mcp_config.example.json) as a logical
starter catalog. Do not commit real keys; use environment-variable references.

## Claude Code extras

- `.claude/commands/` provides `/handoff`, `/save-context`, and `/start-task`.
- `.claude/settings.json` enables the sensitive-path guard and normalized
  write logger documented in [`hooks.md`](hooks.md). Gemini and Codex hook
  mappings remain inactive examples.

These are Claude-native conveniences, not portable project rules.

## Native read-only reviewer

The template ships one specialist role with a shared contract:
[`reviewer-role.md`](reviewer-role.md). Discovery adapters are:

| Client | Native adapter | Declared restriction |
|---|---|---|
| Gemini CLI | `.gemini/agents/reviewer.md` | Read/search tools only |
| OpenAI Codex | `.codex/agents/reviewer.toml` | Read-only sandbox |
| Claude Code | `.claude/agents/reviewer.md` | Read/search tools plus plan permission mode |

The adapters do not duplicate universal policy. Run the same frozen-diff smoke
pilot in each installed client before relying on native behavior; CI validates
structure only and never launches a model.

## Pruning

In a project copy, remove adapters for tools the team does not use. Keep
`AGENTS.md`, `memory-bank/`, and any canonical `.agents/skills` required by the
project.
