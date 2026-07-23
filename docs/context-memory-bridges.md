---
last_verified: 2026-07-23
---

# Provider-Native Context and Memory Bridges

This optional guide explains how provider-local recall can complement the
checked-in Memory Bank. None of these features is required for the template.
There is no automatic synchronization script.

## Keep the layers distinct

| Layer | Purpose | Authority / portability |
|---|---|---|
| Project instructions | Rules loaded from `AGENTS.md` through each native adapter | Canonical and checked in |
| Memory Bank | Deliberately maintained project state and cross-model handoff | Portable and checked in |
| Context compaction | A lossy summary of one active conversation | Session-local; verify after compaction |
| Provider-native memory | Provider-managed recall across chats or sessions | Advisory and often local/account-specific |
| MCP memory | State held by an explicitly configured MCP server | Optional external/local service with its own trust boundary |

Resolve conflicting claims in this order:

1. checked-in repository state and passing tests;
2. current working state that has been directly verified;
3. checked-in Memory Bank;
4. provider-native local memory as advisory recall.

Never let provider memory override repository evidence. Do not automatically
copy secrets, credentials, personal data, absolute machine paths, raw prompts,
or unreviewed chat history into any shared layer.

## Claude Code

- **Project instructions:** `CLAUDE.md` can import root `AGENTS.md`; this
  template keeps `CLAUDE.md` as a one-line adapter.
- **Automatic memory:** Claude Code auto memory is local to a project and is
  advisory. Inspect it with `/memory`.
- **Compaction:** `/compact` summarizes the active conversation. Recheck
  requirements and git state after compaction because details can be lost.
- **Disable/reset:** use `/memory` to manage auto memory. Officially documented
  controls include `autoMemoryEnabled: false` in settings or
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Delete or edit unwanted entries from the
  location shown by `/memory`; `/clear` starts a fresh conversation.

Sources: [Claude Code memory](https://code.claude.com/docs/en/memory) and
[Claude Code interactive mode](https://code.claude.com/docs/en/interactive-mode).

## Gemini CLI

- **Project instructions:** Gemini loads hierarchical `GEMINI.md` context;
  this template's root file imports `AGENTS.md`.
- **Saved memory:** `/memory show` displays loaded memory, while
  `/memory refresh` reloads context files after edits.
- **Compaction:** conversation compression is a session concern, not durable
  project state. After any automatic/manual compression, use the handoff and
  repository to re-establish facts.
- **Disable/reset:** remove or edit deliberately saved memory with Gemini's
  documented memory commands. Do not delete project `GEMINI.md` merely to
  clear provider-local recall. No template-wide automatic-memory toggle is
  asserted here because support can vary by CLI version.

Sources: [Gemini CLI memory management](https://geminicli.com/docs/cli/tutorials/memory-management/),
[save memory tool](https://geminicli.com/docs/tools/memory/), and
[`GEMINI.md` context](https://geminicli.com/docs/cli/gemini-md/).

## Codex

- **Project instructions:** Codex reads root `AGENTS.md`; mandatory team rules
  remain there or in checked-in docs.
- **Local memory:** local Codex clients use a local memory store distinct from
  ChatGPT web memory. Treat both as recall, not governance.
- **Compaction:** an active client may compact long context. Re-open the
  handoff and verify the tree when exact detail matters.
- **Disable/reset:** in supported ChatGPT/Codex surfaces, `/memories` controls
  whether a chat uses or contributes to local memories. Settings >
  Personalization provides the documented on/off and management surface.

Source: [ChatGPT and Codex memories](https://learn.chatgpt.com/docs/customization/memories).

## Safe operating pattern

1. Read `AGENTS.md`, startup context, and the handoff.
2. Use native memory only to suggest files or facts worth checking.
3. Verify each material fact against repository state or a current source.
4. Write cross-agent facts to the appropriate Memory Bank file.
5. Keep provider-local memory optional; disabling it must not break startup,
   validation, handoff, or testing.
