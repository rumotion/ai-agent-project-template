---
last_verified: 2026-07-23
---

# Agent Protocol Watch

This watch list records interoperability signals without adding a protocol
runtime or dependency. Reverify first-party sources before changing the
template.

## MCP

- **Status:** `2025-11-25` is the common final target tracked here. The
  `2026-07-28` specification is still a release candidate as of this document's
  verification date.
- **First-party source:** [MCP 2025-11-25 specification](https://modelcontextprotocol.io/specification/2025-11-25)
  and [2026-07-28 release-candidate timeline](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/).
- **Template relevance:** agent-to-tool and agent-to-data interoperability for
  the optional native configuration examples.
- **Adoption trigger:** a newer final specification is supported by Gemini,
  Codex, and Claude project clients and existing examples pass smoke tests.
- **Current action:** keep examples conservative and client-native; do not
  advertise release-candidate features as portable.

## Agent Skills

- **Status:** the published Agent Skills specification requires a skill
  directory with a frontmatter-bearing `SKILL.md`; `allowed-tools` remains
  experimental.
- **First-party source:** [Agent Skills specification](https://agentskills.io/specification).
- **Template relevance:** `.agents/skills` is canonical, with SHA-256-checked
  mirrors for clients that require another discovery tree.
- **Adoption trigger:** a finalized schema change is implemented by all target
  clients or can be added without breaking current discovery.
- **Current action:** validate the stable name/description/body subset only;
  do not rely on experimental fields for security.

## ACP

- **Status:** ACP v1 is the latest documented editor-to-agent protocol; v2 is
  draft, and full remote-agent support is documented as work in progress.
- **First-party source:** [ACP introduction](https://agentclientprotocol.com/get-started/introduction)
  and [supported agents/clients](https://agentclientprotocol.com/get-started/clients).
- **Template relevance:** a possible transport between editors and Gemini,
  Codex, or Claude-compatible agents.
- **Adoption trigger:** the user's selected editor and all required agents
  support the same final ACP version with acceptable permission behavior.
- **Current action:** documentation watch only. ACP is not an MCP replacement
  and does not replace repository instructions or the delegation contract.

## A2A

- **Status:** A2A 1.0 is the current final remote-agent protocol documented by
  the Linux Foundation project, with explicit protocol-version negotiation.
- **First-party source:** [A2A specification](https://a2a-protocol.org/latest/specification/)
  and [A2A overview](https://a2a-protocol.org/latest/).
- **Template relevance:** future communication between independently deployed
  remote agents, not ordinary in-process/local subagent work.
- **Adoption trigger:** a real project needs remote agent discovery/task
  exchange, target runtimes implement the same version, and authentication,
  privacy, observability, and fallback are designed.
- **Current action:** documentation watch only. A2A is neither local
  delegation nor an MCP replacement.

## Review cadence

Review before a release that changes adapters, skills, MCP examples, editor
integration, or remote-agent architecture. Record the new ISO date and exact
final versions. A published standard alone is insufficient: target-client
support and a portable fallback are required.
