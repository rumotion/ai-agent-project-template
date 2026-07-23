---
last_verified: 2026-07-23
---

# Gemini, Codex, and Claude Compatibility

This is the compatibility truth table for the template's three primary agents.
Root `AGENTS.md` is the only canonical repository instruction file.

## Portable core and native adapters

Portable core is content that every agent can use without a provider-specific
fork:

- `AGENTS.md` for repository rules
- `memory-bank/` for durable shared context
- `workflows/` for on-demand procedures
- `.agents/skills/*/SKILL.md` as the canonical skill source
- `.mcp/` as documentation and logical MCP starter examples

Native adapters only expose that core through a client's discovery or
configuration format. They must not add universal policy. A native path listed
below is not necessarily shipped or enabled; see the Status row.

Current interoperability statuses and adoption gates are tracked separately in
`docs/protocol-watch.md`; no protocol runtime is installed by the template.

## Compatibility matrix

| Capability | Gemini CLI | Codex | Claude Code |
|---|---|---|---|
| Instructions | `GEMINI.md` imports `@AGENTS.md` | Reads root `AGENTS.md` natively | `CLAUDE.md` imports `@AGENTS.md` |
| Project skills | `.agents/skills/<name>/SKILL.md` alias | `.agents/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` mirror |
| Project MCP | `.gemini/settings.json`, `mcpServers` | `.codex/config.toml`, `[mcp_servers.<name>]` | Root `.mcp.json`, `mcpServers` |
| Project hooks (client-native) | `.gemini/settings.example.json` (inactive example) | `.codex/hooks.example.json` (inactive example) | `.claude/settings.json` (active) |
| Project subagents | `.gemini/agents/reviewer.md` | `.codex/agents/reviewer.toml` | `.claude/agents/reviewer.md` |
| Reviewer restriction | Read/search tool allowlist | `sandbox_mode = "read-only"` | Read/search tool allowlist plus `permissionMode: plan` |
| Status in this template | Instructions, canonical skills, and one reviewer adapter ship; MCP and hooks have inactive native examples | Instructions, canonical skills, and one reviewer adapter ship; MCP and hooks have inactive native examples | Instructions, skill mirrors, one reviewer adapter, root `.mcp.json`, and active sensitive-path/write-log hooks ship |

Important distinctions:

- `.mcp.json` is Claude Code's project MCP file. It is not a universal Gemini
  or Codex project configuration.
- `.mcp/` contains reusable documentation and examples; clients do not load
  that directory automatically.
- `.agents/skills` is canonical. Claude's `.claude/skills` copies are
  SHA-256-validated mirrors, not a second source of truth.
- Hook event names and payloads differ by client. Shared hook behavior may be
  implemented in portable scripts, but each client still needs a native
  mapping.
- Native subagent definitions are optional adapters. Durable project rules
  remain in `AGENTS.md`, not in provider-specific agent files.
- `docs/reviewer-role.md` is the canonical contract for the only shipped
  specialist role. Validator checks prove structure and restrictions are
  declared; they do not prove runtime behavior.
- Shared scripts normalize the portable behavior, while native files retain
  each client's verified event names, matcher shape, and denial response.
- Gemini and Codex examples are opt-in. Copying an example to its active native
  filename is an explicit activation step.

## Manual smoke checks

Run these from the repository root in an interactive session. MCP checks for
Gemini and Codex require adding their native project config first.

### Gemini CLI

```text
gemini
/memory show
/skills list
/mcp
```

Confirm that `/memory show` includes the imported root `AGENTS.md` content and
that `/skills list` discovers `.agents/skills`.

### Codex

```text
codex
Summarize the active repository instructions and name their source file.
/skills
/mcp
```

Confirm that Codex names root `AGENTS.md` and discovers the project skills from
`.agents/skills`.

### Claude Code

```text
claude
/context
/skills
/mcp
```

Confirm that `/context` shows `CLAUDE.md` and its `AGENTS.md` import, `/skills`
shows the `.claude/skills` mirrors, and `/mcp` shows the approved servers from
root `.mcp.json`.

### Reviewer pilot status

The shared frozen-diff pilot is pending for Gemini, Codex, and Claude. No model
session is launched by validation or CI. When a maintainer runs a pilot, record
whether the reviewer found the correctness defect, ignored the harmless style
issue, preserved the worktree, and followed `docs/reviewer-role.md`.

## Official sources

Gemini CLI:

- [GEMINI.md context and imports](https://geminicli.com/docs/cli/gemini-md/)
- [Agent Skills discovery](https://geminicli.com/docs/cli/using-agent-skills/)
- [MCP project configuration](https://geminicli.com/docs/tools/mcp-server/)
- [Hooks](https://geminicli.com/docs/hooks/)
- [Subagents](https://geminicli.com/docs/core/subagents/)

Codex:

- [AGENTS.md instructions](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Agent Skills](https://developers.openai.com/codex/build-skills)
- [MCP configuration](https://developers.openai.com/codex/extend/mcp)
- [Hooks](https://developers.openai.com/codex/hooks)
- [Subagents](https://developers.openai.com/codex/agent-configuration/subagents)

Claude Code:

- [CLAUDE.md and AGENTS.md import](https://code.claude.com/docs/en/memory)
- [Skills](https://code.claude.com/docs/en/skills)
- [MCP configuration](https://code.claude.com/docs/en/mcp)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [Subagents](https://code.claude.com/docs/en/sub-agents)

Shared format:

- [Agent Skills specification](https://agentskills.io/specification)
