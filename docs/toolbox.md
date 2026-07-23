# The Toolbox: Optional Power-Ups

The base template has a zero-dependency core. This toolbox lists optional,
on-demand capabilities for projects that outgrow the defaults. External tools
are **not installed, configured, or validated by default**; built-in workflows
remain dormant until explicitly invoked.

For third-party entries, apply the evidence, compatibility, permission, and
rollback checks in [third-party-integrations.md](third-party-integrations.md).

## 1. Graphify (codebase knowledge graph)

**Default state:** Not installed; opt-in only.

**Why use it:** A structural code map may reduce repeated broad searches in a
large repository.

**What it does:** Builds a map of functions, schemas, and dependencies. Results
still require source verification.

**How to evaluate:** Review [the Graphify workflow](../workflows/build-graph.md),
verify the current upstream package and install command, then test it in a
disposable environment. Installation adds a third-party dependency and is not
part of template validation.

## 2. Advanced steering prompts

**Default state:** Shipped as documentation; invoked only on demand.

**Why use it:** A focused prompt can help clarify intent, challenge assumptions,
or recalibrate repeated styling and behavior corrections.

**What it does:** Provides reusable prompts such as `/align`, `/devil`,
`/burst`, and `/calibrate`. Slash-command availability is client-specific; copy
the prompt text directly when a client does not support that command surface.

**How to activate:** Read [prompts.md](prompts.md) and use only the relevant
prompt.

## 3. Parallel agent work

**Default state:** No background agents or external sessions are started.

**Why use it:** Independent, bounded frontend, backend, research, or review work
may benefit from parallel execution.

**What it does:** Uses explicit file ownership and the checked-in Memory Bank to
coordinate sessions. Native delegation features differ across Gemini, Codex,
and Claude, so do not assume identical availability or semantics.

**How to activate:** Follow the parallel-work guidance in
[start-new-project.md](start-new-project.md). Confirm each agent's scope before
allowing concurrent writes.

## 4. Offline memory consolidation ("dream phase")

**Default state:** The documented example is optional; no cross-client hook or
background consolidation service is enabled by the core template.

**Why use it:** Large projects may benefit from consolidating metadata-only
activity logs outside the active coding context.

**What it does:** Agent lifecycle hooks can record selected write events for a
later, reviewed Memory Bank update. Hooks and payloads are client-specific, and
logs must not capture secrets or file contents.

**How to evaluate:** See [hooks.md](hooks.md) for the current example and
[hook-memory-integration.md](proposals/hook-memory-integration.md) for the
experimental cross-client design. The checked-in Memory Bank remains
authoritative.

## 5. Context hygiene cheatsheet

**Default state:** Shipped as documentation; loaded only when needed.

**Why use it:** Slow or confused sessions often indicate excessive or stale
context.

**What it does:** Provides a checklist for tool-output filtering, prompt-cache
stability, compaction, session branching, reasoning effort, and incident-mode
fallbacks. Named commands vary by client.

**How to activate:** Read [context-hygiene.md](context-hygiene.md) when a
symptom appears. It is not part of FAST_INIT.

## 6. Third-party integrations and MCP servers

**Default state:** Every catalog item is uninstalled and unconfigured.

**Why use it:** A project may need specialized domain guidance or an explicit
connection to an external service.

**What it does:** Provides discovery leads for plugins, skills, CLIs, and MCP
servers. The catalog is not a compatibility or security allowlist.

**How to evaluate:** Review
[third-party-integrations.md](third-party-integrations.md), resolve official
upstream documentation, verify the exact target agent, minimize permissions,
and test with non-production data.

## 7. Optional context compression experiments

Neither option below is installed, enabled, required, or included in CI.

- [Headroom](https://github.com/headroomlabs-ai/headroom) is an optional
  runtime/proxy experiment. Review telemetry, privacy, failure behavior, and
  rollback; benchmark total session cost and correctness rather than accepting
  unqualified savings claims.
- [Caveman](https://github.com/JuliusBrussee/caveman) is an optional
  response-style experiment. It can remove useful qualifiers and may be
  **net-negative on already-terse workloads**. Disable it for security work,
  incidents, architecture decisions, and handoffs unless local tests prove it
  safe.

## 8. Protocol and native-memory watch items

ACP, A2A, and provider-native memory are watch items, not core template
features:

- ACP may connect an editor to an agent.
- A2A may connect remote agents.
- Claude-, Gemini-, or Codex-native memory may provide local recall.

They do not replace repository instructions, MCP, portable delegation, or the
checked-in Memory Bank. Adopt them only after verifying stable support in the
chosen clients and documenting a portable fallback.
