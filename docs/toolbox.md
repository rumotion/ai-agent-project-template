# The Toolbox: Optional Power-Ups

This template is designed to be as minimal as possible on day one. We enforce a strict "Zero Dependency" rule for the core template. 

However, as your project scales, you may hit context limits, require tighter AI steering, or need advanced memory management. This toolbox catalogs optional power-ups you can activate when needed.

## 1. Graphify (Codebase Knowledge Graph)
**Why use it:** When your codebase has hundreds of files, relying on standard "grep" searches or agent file-reading consumes massive amounts of tokens and leads to AI hallucinations.
**What it does:** Builds a structural map of your code (functions, schemas, dependencies).
**How to activate:**
Read `workflows/build-graph.md`.
```bash
uv tool install graphifyy && graphify .
```

## 2. Advanced Steering Prompts
**Why use it:** AI agents often suffer from "yes-man" behavior or rush into coding before fully understanding constraints.
**What it does:** Provides slash-commands (`/align`, `/devil`, `/burst`, `/calibrate`) to instantly force the agent to clarify intent, take contrarian views, or self-reflect.
**How to activate:**
Read `docs/prompts.md` and use the prompts directly in your chat.

## 3. Parallel Agent Forking
**Why use it:** You want one AI to build the frontend while another AI builds the backend, simultaneously.
**What it does:** Uses the external `memory-bank` to sync context across parallel sessions without them stepping on each other's toes.
**How to activate:**
Read Section 10 of `docs/start-new-project.md`.

## 4. Offline Memory Consolidation (The "Dream Phase")
**Why use it:** Your project is massive and manual updates to the `memory-bank` are eating up active coding tokens.
**What it does:** Uses IDE/agent lifecycle hooks to passively log agent actions (zero tokens), then runs an offline batch step to fold the log into the Memory Bank.
**How to activate:**
A working example ships now — see [`hooks.md`](file:///c:/AI/_code/_projectTemplate/docs/hooks.md): a `PostToolUse` hook (`.claude/settings.json` + `.claude/hooks/log-writes.py`) appends file changes to `.agent-logs/`. The deeper cross-IDE architecture is tracked in `docs/proposals/hook-memory-integration.md` as hooks standardize across tools.

## 5. Context Hygiene Cheatsheet
**Why use it:** Sessions feel slow, expensive, or the agent starts "acting dumb" — usually a context problem, not a model problem.
**What it does:** Operational checklist for auditing token usage, filtering tool output, using `/compact`/`/btw`/`/rewind`/`/fork`, preserving prompt-cache hits, tuning reasoning effort, and disabling optimizations during incidents.
**How to activate:**
Read [context-hygiene.md](file:///c:/AI/_code/_projectTemplate/docs/context-hygiene.md) only when you hit a symptom. Not part of FAST_INIT.

## 6. Third-Party Integrations & MCP Servers
**Why use it:** When your agent needs specific domain expertise (legal, finance), general productivity extensions (gstack, superpowers), or live app connections (slack, notion, perplexity).
**What it does:** Lists 24 curated third-party plugins, specialized skills, and MCP configurations.
**How to activate:**
Read [third-party-integrations.md](file:///c:/AI/_code/_projectTemplate/docs/third-party-integrations.md) to explore the catalog and find installation commands/configurations.

