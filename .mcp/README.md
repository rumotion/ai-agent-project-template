# MCP Configuration

This directory documents a logical set of
[Model Context Protocol](https://modelcontextprotocol.io) servers. It is not a
configuration location that clients load automatically.

## Native project configuration

| Client | Project file | Server key |
|---|---|---|
| Gemini CLI | `.gemini/settings.json` (example: `.gemini/settings.example.json`) | `mcpServers` |
| OpenAI Codex | `.codex/config.toml` (example: `.codex/config.example.toml`) | `[mcp_servers.<name>]` |
| Claude Code | Root `.mcp.json` | `mcpServers` |
| VS Code | `.vscode/mcp.json` | `servers` |

The root `.mcp.json` currently activates the starter set for Claude Code. Inactive native example files are provided for Gemini ([`.gemini/settings.example.json`](../.gemini/settings.example.json)) and Codex ([`.codex/config.example.toml`](../.codex/config.example.toml)). Translate the same server intent into each client's native schema; do not copy JSON fields blindly between clients.

See [`../docs/agent-compatibility.md`](../docs/agent-compatibility.md) for the
last-verified compatibility matrix and official client sources.

## Transports

- **stdio**: the client starts a local subprocess. Use it for local filesystem,
  git, and memory tools.
- **Streamable HTTP**: the client connects to a remote MCP endpoint. URL,
  headers, OAuth, and transport field names are client-specific.
- **SSE**: legacy transport retained by some clients. Prefer Streamable HTTP
  for new remote integrations when both client and server support it.

## Safe activation

- Review every command, package, URL, requested permission, and data scope
  before enabling a server.
- `npx -y` and `uvx` may download and execute packages. Pin versions where
  reproducibility matters.
- Never hardcode secrets. Use the environment-variable syntax supported by the
  target client.
- Activate only the servers needed for the current work. Connected tools add
  capability, attack surface, and context overhead.
- Do not expose secrets or sensitive production data without explicit
  approval.

The examples in [`mcp_config.example.json`](mcp_config.example.json) are a
catalog to adapt, not a drop-in configuration for every client. Verify package
names and current upstream instructions before use.

Official client guides:

- [Gemini CLI MCP](https://geminicli.com/docs/tools/mcp-server/)
- [Codex MCP](https://developers.openai.com/codex/extend/mcp)
- [Claude Code MCP](https://code.claude.com/docs/en/mcp)

For optional third-party integrations, see
[`../docs/third-party-integrations.md`](../docs/third-party-integrations.md).
