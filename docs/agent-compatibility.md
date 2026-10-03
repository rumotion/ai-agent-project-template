---
last_verified: 2026-09-05
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
| Status in this template | Instructions, canonical skills, and one reviewer adapter ship; MCP and hooks have inactive native examples | Instructions, canonical skills, and one reviewer adapter ship; MCP and hooks have inactive native examples | Instructions, skill mirrors, one reviewer adapter, and active sensitive-path/write-log hooks ship; MCP is opt-in (no active config) |

Important distinctions:

- `.mcp.json` is Claude Code's project MCP file format. This template no
  longer ships one: an active git MCP server would expose `git_push` outside
  the repository-boundary hooks. Opt in per client via `.mcp/README.md`.
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
shows the `.claude/skills` mirrors, and `/mcp` shows only the servers you
have deliberately opted into (none ship by default).

### Reviewer pilot status

The shared frozen-diff pilot is pending for Gemini, Codex, and Claude. No model
session is launched by validation or CI. When a maintainer runs a pilot, record
whether the reviewer found the correctness defect, ignored the harmless style
issue, preserved the worktree, and followed `docs/reviewer-role.md`.

## Additional agents (verified 2026-09-05)

`AGENTS.md` is an open standard, so most modern agents need **no adapter at
all**. Adding pointer files for them would be noise, not coverage. Verified
against first-party documentation:

| Agent | Reads root `AGENTS.md`? | Adapter shipped | Note |
|---|---|---|---|
| [Amp](https://ampcode.com/agent.md) (Sourcegraph) | Yes, natively | None needed | Reads the nearest file up the tree; subdirectory files take precedence |
| [opencode](https://opencode.ai/docs/rules/) | Yes, natively | None needed | Where both exist, `AGENTS.md` wins over `CLAUDE.md` |
| [Warp](https://docs.warp.dev/knowledge-and-collaboration/rules) | Yes, natively | None needed | Applies root and current-directory rules; filename must be uppercase |
| [Zed](https://zed.dev/docs/ai/instructions) | Only if nothing earlier matches | **`.rules`** | See below |

### Why Zed needs an adapter

Zed resolves project instructions by **first match wins**, in this order:

`.rules`, `.cursorrules`, `.windsurfrules`, `.clinerules`,
`.github/copilot-instructions.md`, `AGENT.md`, `AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`

This template ships `.windsurfrules`, `.clinerules/`, and
`.github/copilot-instructions.md` — all of which rank **above** `AGENTS.md`.
Without intervention, Zed would stop at `.windsurfrules` and never reach the
canonical file.

Two properties make this safe:

1. Every adapter in this template is a pointer that names `AGENTS.md`, so even
   a shadowed resolution still directs the agent to the canonical file. This is
   a deliberate design property, not luck — an adapter carrying independent
   policy would silently fork the rules.
2. `.rules` is shipped as Zed's highest-priority filename, so resolution is
   deterministic and reaches the pointer in one hop.

The validator enforces that every adapter names `AGENTS.md`, which is what
keeps property 1 true as adapters are added.

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

Additional agents (verified 2026-09-05):

- [Amp AGENTS.md](https://ampcode.com/agent.md)
- [opencode rules](https://opencode.ai/docs/rules/)
- [Warp rules for agents](https://docs.warp.dev/knowledge-and-collaboration/rules)
- [Zed instructions](https://zed.dev/docs/ai/instructions)

Shared format:

- [Agent Skills specification](https://agentskills.io/specification)
