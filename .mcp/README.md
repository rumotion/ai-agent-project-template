# MCP Configuration

This project may use [MCP](https://modelcontextprotocol.io) servers to give agents live external context and tools.

## Where config lives

| Client | Config file | Top-level key |
|---|---|---|
| Claude Code / Codex / Cursor / Cline | `.mcp.json` (project root) | `mcpServers` |
| VS Code | `.vscode/mcp.json` | `servers` (note: per-server `type`) |
| Claude Desktop | `claude_desktop_config.json` (OS app-data dir) | `mcpServers` |

`.mcp.json` at the repo root is the de-facto multi-client standard. Start there; copy extra servers from [`mcp_config.example.json`](mcp_config.example.json).

## Transports (spec 2025-11-25)

- **stdio** — client spawns the server as a local subprocess. Preferred for local tools (filesystem, git, memory). Secrets via the `env` block.
- **Streamable HTTP** — remote servers, given as `{ "url": "...", "type": "http" }`. The client runs an OAuth browser flow on first connect, so no token needs to live in the config file. This replaces the deprecated HTTP+SSE transport.

## Conventions

- TypeScript/JS servers run via `npx -y <package>`. Python servers run via `uvx <package>` (preferred over `pip`).
- Never hardcode secrets. Use `${ENV_VAR}` placeholders and set them in your shell or a local `.env`.
- Only the official `@modelcontextprotocol/server-*` packages are guaranteed to exist under that scope (filesystem, git, memory, fetch, sequentialthinking, time, everything). Search/browser/comms servers are community or company packages — verify the package name before use.
- Treat MCP servers like phone apps: connect what you use this session, disconnect the rest. Every connected server adds tool schemas to every request (see [`../docs/context-hygiene.md`](../docs/context-hygiene.md) §7).

Do not connect MCP servers that expose secrets or sensitive production data without explicit approval.

For the curated catalog of third-party servers, see [`../docs/third-party-integrations.md`](../docs/third-party-integrations.md).
