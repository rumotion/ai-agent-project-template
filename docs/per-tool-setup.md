# Per-Tool Setup

How to point each AI tool at this template's shared brain (`AGENTS.md` + Memory Bank). Every adapter is a thin pointer to `AGENTS.md`, so all tools share one source of truth — you never re-explain the project when you switch.

> Conventions change. If a path below doesn't match your installed version, check the tool's current docs and update the adapter. The canonical content stays in `AGENTS.md` either way.

## Instruction file each tool reads

| Tool | File it loads | In this template | Notes |
|---|---|---|---|
| Claude Code | `CLAUDE.md` (+ `.claude/`) | ✅ ships | Also reads `.claude/settings.json`, `.claude/commands/`, `.claude/hooks/` |
| OpenAI Codex CLI | `AGENTS.md` (native) | ✅ canonical | Reads the root `AGENTS.md` directly; `.codex/AGENTS.md` is a backup pointer |
| Gemini CLI / Antigravity | `GEMINI.md` (+ `.agents/`) | ✅ ships | Antigravity uses `.agents/rules`, `.agents/skills`, `.agents/workflows` |
| Cline | `.clinerules/` (all `.md`) | ✅ ships | Loads every file in the dir |
| Roo Code | `.clinerules/` | ✅ reuses | Cline-compatible — no separate adapter |
| Cursor | `.cursor/rules/*.mdc` | ✅ ships | `.mdc` frontmatter: `description`, `globs`, `alwaysApply` |
| Windsurf (Codeium) | `.windsurfrules` | ✅ ships | Cascade reads this at the repo root |
| GitHub Copilot | `.github/copilot-instructions.md` | ✅ ships | Used by Copilot Chat and the coding agent |
| Aider | `CONVENTIONS.md` via `.aider.conf.yml` | ✅ ships | `.aider.conf.yml` lists files to load read-only |

## First run, any tool

1. Open the project in your tool.
2. Paste an init prompt from [`prompts.md`](prompts.md) (or run `python scripts/init-fast.py` and paste its prompt).
3. The agent reads `AGENTS.md` → `memory-bank/startup.md` → lazy-loads the rest. Done.

## MCP (optional tools/context)

| Client | MCP config file | Top-level key |
|---|---|---|
| Claude Code / Codex / Cursor / Cline | `.mcp.json` (repo root) | `mcpServers` |
| VS Code | `.vscode/mcp.json` | `servers` |
| Claude Desktop | `claude_desktop_config.json` (OS app-data) | `mcpServers` |

Starter servers ship in `.mcp.json` (filesystem, git, memory). Copy more from [`../.mcp/mcp_config.example.json`](../.mcp/mcp_config.example.json). Set any required keys in `.env` (see [`../.env.example`](../.env.example)). Details and transport guidance: [`../.mcp/README.md`](../.mcp/README.md).

## Claude Code extras (opt-in)

- **Slash commands** — `.claude/commands/` gives you `/handoff`, `/save-context`, `/start-task`.
- **Hooks** — `.claude/settings.json` wires a zero-token write-logger; see [`hooks.md`](hooks.md). Delete the file to opt out.

## Pruning for your project

The template ships every adapter so any teammate's tool works out of the box. In your copy, delete the adapters for tools you don't use — they're thin pointers, safe to remove. Keep `AGENTS.md` and `memory-bank/`.
