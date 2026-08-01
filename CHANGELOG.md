# Changelog

All notable changes to this template are documented here. This project follows
[Semantic Versioning](https://semver.org/) — `MAJOR.MINOR.PATCH`. The version
in [`VERSION`](VERSION) always matches the latest released git tag.

- **MAJOR** — breaking changes to the canonical `AGENTS.md` contract, the
  Memory Bank file layout, or the validator's public flags.
- **MINOR** — new opt-in features, new workflows/skills, new docs.
- **PATCH** — bug fixes, doc clarifications, validator polish.

For the release process, see [`docs/releasing.md`](docs/releasing.md).

## Unreleased

_Nothing yet._

## v0.8.0 — 2026-08-01 — Atomic step-commit workflow

### Changed

- Agent execution loop is now Plan → Execute → Verify → Commit → Reflect:
  phased plans carry discrete, individually verifiable checkpoints, and each
  verified checkpoint is committed atomically with Conventional Commit syntax
  (`AGENTS.md`, `docs/agent-loop.md`, `plan-task.md` / `implement-task.md`
  across all three workflow trees, `CONVENTIONS.md`).
- Validator now requires every mirrored workflow file (9 workflows x 3 trees)
  to exist, closing silent drift-skip gaps.

### Fixed

- Stale FAST_INIT and budget figures in README and Memory Bank summaries.
- Missing final newlines in `plan-task.md` / `implement-task.md` mirrors.

## v0.7.0 — 2026-07-23 — Cross-agent compatibility, delegation, and context benchmarks

### Added

- MIT license for clear reuse and redistribution terms.
- One canonical read-only reviewer role with minimal native Gemini, Codex, and
  Claude adapters and structural parity checks.
- A deterministic five-scenario context benchmark with JSON output, sanitized
  manual usage comparison, a 10% evidence gate, and Python 3.9 self-tests.
- Dated provider-memory bridge and protocol-watch guidance plus optional
  performance experiment recipes; no compressor, proxy, or protocol runtime is
  installed or activated.
- Portable subagent contract (`docs/subagent-contract.md`) and `delegation-coordinator` skill across 3 discovery trees.
- Workflows for pre-edit verification (`pre-edit-check.md`), spec-driven development (`spec-driven-development.md`), and evidence-grounded self-evaluation (`self-evaluate.md`) across 3 workflow trees.
- Shared zero-dependency hook library in `scripts/hooks/` (`log-writes.py`, `guard-sensitive-paths.py`, `verify-fixtures.py`), redacted client event fixtures, and `.codex/hooks.example.json`.
- Inactive native MCP example configurations `.gemini/settings.example.json` and `.codex/config.example.toml`.
- Gemini/Codex/Claude compatibility truth table and `--compat` validator mode.
- Five Claude skill mirrors, with three-tree SHA-256 drift protection.
- Python 3.9/current CI coverage on both Windows and Linux.

### Changed

- `.agents/skills/` is now the canonical Agent Skills source; `.claude/skills/`
  and `.cline/skills/` are discovery mirrors.
- Primary Gemini, Claude, and Codex adapters are exact one-line imports/pointers.
- MCP documentation now uses each client's native project configuration path.
- Validator enforces minimal skill schema and a hard 7,600-character aggregate
  FAST_INIT ceiling.
- Full/compatibility validation now checks the reviewer contract, advanced
  guidance metadata, required benchmark scenarios, and benchmark self-test.
- Optional integrations now include explicit install state, evidence, confidence,
  and portability caveats.

## v0.6.0 — 2026-06-05 — Universal agent features: MCP, hooks, execution loop

Tool-agnostic modernization pass. Adds verified MCP 2025-11-25 conventions, two
new tool adapters, a documented agent-execution loop (budgets, error taxonomy,
phase-completion summary), prospective memory, and an opt-in Claude Code hooks
example. Startup philosophy unchanged; the FAST_INIT path grew from ~1,500 to
~1,880 tokens to carry the new always-on execution rules.

### Added

- **New tool adapters**: `.windsurfrules` (Windsurf/Cascade) and `CONVENTIONS.md`
  + `.aider.conf.yml` (Aider). Roo Code documented as `.clinerules`-compatible
  (no separate adapter). Adapter count 7 → 9.
- **`docs/agent-loop.md`**: parallel tool-call batching, per-task-class tool-call
  budgets, an error/retry taxonomy, and a structured phase-completion summary
  block. Summarized as a new always-on "Agentic execution" section in `AGENTS.md`.
- **`memory-bank/reminders.md`**: prospective-memory file (trigger-keyed future
  notes) checked at phase start / pre-deploy / model switch. Indexed in `00-index.md`.
- **`docs/hooks.md` + `.claude/settings.json` + `.claude/hooks/log-writes.py`**:
  opt-in Claude Code hooks example for zero-token passive logging ("Dream Phase"
  pattern), with safe-hook rules and permission defaults. All opt-in — not required.
- **`workflows/critic-review.md`**: separate-context critic pattern with a
  structured findings format. **`workflows/autonomous-agent.md`**: guardrails and
  loop for longer hands-off runs.
- **Root `.mcp.json`** (de-facto multi-client standard) and **`.vscode/mcp.json`**
  (VS Code `servers` key) as working MCP starter configs.
- **`docs/per-tool-setup.md`**: a concrete map of which instruction file each of
  the 9 tools reads and how to wire MCP per client — the fastest path for a new
  user to get any tool sharing the project brain.
- **CI**: `.github/workflows/validate.yml` runs the full validator on every push
  and PR across Linux and Windows, plus the FAST_INIT benchmark.
- **Repo hygiene**: `.github/PULL_REQUEST_TEMPLATE.md`, issue templates
  (bug / feature), and a universal `.editorconfig`.
- **Claude Code slash commands**: `.claude/commands/` ships `/handoff`,
  `/save-context`, and `/start-task` that encode the core prompts.
- **Expanded `.env.example`**: documents the MCP-related env vars referenced by
  the example server configs (all commented/empty — safe to commit).

### Changed

- **`.mcp/mcp_config.example.json`**: corrected to verified MCP 2025-11-25 reality
  — `git` runs via `uvx`; added official `memory` and `sequential-thinking`
  servers; added a remote Streamable-HTTP example (`url` + `type: http`); flagged
  non-`@modelcontextprotocol` packages as community/unverified.
- **`.mcp/README.md`**: transport guidance (stdio vs Streamable HTTP), config-file
  location map per client, `uvx` for Python servers.
- **`memory-bank/model-routing.md`**: current model context windows (frontier
  models now ~1M); adaptive-thinking / `effort` guidance; cascade routing rule;
  added Roo Code, Windsurf, and Aider to the tools/adapters table.
- **`memory-bank/handoff.md`**: structured YAML header (status, models,
  next_action, files_modified, blocking_issues) above the prose narrative.
- **`docs/context-hygiene.md`**: new section on batching independent tool calls.
- **Skills** (`.cline/skills/`, `.agents/skills/`): self-documenting "Chains to"
  pointers; mirrors kept byte-identical.
- **`scripts/check-template.py`**: validates the new required files and adapters
  (49 files, 9 adapters, 15 budgets); `AGENTS.md` budget raised to 4,700 chars.

### Notes

- Speculative features flagged LOW-confidence during research (unverifiable
  Claude Code commands / version numbers) were deliberately **not** documented,
  per the template's "do not invent facts" rule.

## v0.5.0 — 2026-05-16 — Agentic Memory & Skill Chaining

### Added
- **`memory-bank/userPreferences.md`**: Introduced a Tier-0 memory layer specifically for tracking user communication style, workflow habits, and formatting quirks, separating user identity from project memory. Added pointer to `00-index.md`.

### Changed
- **`docs/agent-skill-ecosystem.md`**: Explicitly documented "Skill Chaining & Progressive Disclosure", instructing agents to chain modular, atomic skills (e.g., `project-planner` -> `karpathy-engineer`) rather than using monolithic mega-skills.

## v0.4.0 — 2026-05-14 — Context-hygiene cheatsheet + cache/reasoning rules

Operational pass aimed at the most common late-session failure mode: an
agent that started fast but now feels slow, expensive, or "dumb." Adds a
lazy-loaded reference distilled from the May-2026 community
context-management guide and reconciled with current Claude Code release
notes (`/btw` shipped in v2.1.72 on 2026-03-10, 5-minute prompt cache
TTL, workspace-scoped cache isolation since Feb 2026, the
system-reminder pattern for dynamic content).

### Added

- **[`docs/context-hygiene.md`](docs/context-hygiene.md)**: optional
  operational cheatsheet covering context audit (`/context`, `/usage`,
  `wc -w`, log-bomb hunt), tool-output filtering, phase hygiene
  (`/compact`, `/btw`, `/rewind`, `/fork`), prompt-cache ordering rule
  with anti-patterns, reasoning-effort defaults, MCP discipline,
  cheap-worker / subagent split, when NOT to optimize (incidents /
  security review / new architecture), a symptom→fix troubleshooting
  table, and a quick decision tree. Read only on demand — not part of
  FAST_INIT.

### Changed

- **[`memory-bank/model-routing.md`](memory-bank/model-routing.md)**:
  new "Cache ordering rule" section (stable prefix → dynamic tail; named
  anti-patterns; 5-minute TTL note) and a "Reasoning effort defaults"
  table mapping task class to thinking budget for Claude, OpenAI
  `reasoning_effort`, and Gemini equivalents.
- **[`memory-bank/00-index.md`](memory-bank/00-index.md)**: pointer row
  to `docs/context-hygiene.md` so agents discover it when relevant.
- **[`docs/toolbox.md`](docs/toolbox.md)**: entry 5 cataloguing the
  cheatsheet alongside Graphify, steering prompts, parallel forking,
  and the Dream Phase proposal.

### Unchanged (intentional)

- `AGENTS.md` and the other cache-stable files (`CLAUDE.md`,
  `GEMINI.md`, `memory-bank/startup.md`, adapter files) stay byte-stable
  so Claude prompt-cache hits keep warming across sessions.
- FAST_INIT read budget unchanged; none of the new material loads by
  default.

## v0.3.0 — 2026-05-13 — Polished landing page + release workflow

Public-facing pass: the GitHub repo page now reads as a real product landing
page, and there is a clear, repeatable process for cutting future releases.

### Added

- **README rewritten as a landing page**: hero tagline, badges (Use this
  template, latest release, validator, FAST_INIT cost, license), a top-level
  table of contents, a three-step Quick Start, and a dedicated "Releases &
  changelog" section pointing visitors at the right docs.
- **`VERSION` file** at the repo root, single source of truth for the current
  release. Always matches the latest tag.
- **[`docs/releasing.md`](docs/releasing.md)**: step-by-step guide for cutting
  a new tagged release of the template — what to bump, what to write in the
  changelog, how to tag, how to push, how to publish the GitHub release. So
  you (and any future maintainer) never have to figure the workflow out from
  scratch.

### Changed

- CHANGELOG restructured into proper SemVer-style sections with Added /
  Changed / Fixed sub-headings. The previous flat list is now split between
  `v0.2.0` and `v0.3.0`.

## v0.2.0 — 2026-05-13 — Toolbox, identity cleanup, Windows-safe bootstrap

First substantial public release. Three coordinated changes prepared the
template for use as a real GitHub Template by others.

### Added

- **Toolbox of opt-in power-ups** (kept out of the FAST_INIT path):
  - [`workflows/build-graph.md`](workflows/build-graph.md) — Graphify
    integration for building a structural knowledge graph of large
    codebases, so agents stop burning tokens grepping.
  - [`workflows/calibrate.md`](workflows/calibrate.md) — continuous
    self-improvement workflow that distills repeated corrections into
    persistent rules.
  - [`docs/toolbox.md`](docs/toolbox.md) — single catalog of every opt-in
    power-up.
  - [`docs/prompts.md`](docs/prompts.md) — new `/calibrate`, `/align`,
    `/devil`, `/burst` steering prompts.
  - [`docs/proposals/graphify-integration.md`](docs/proposals/graphify-integration.md)
    and [`docs/proposals/hook-memory-integration.md`](docs/proposals/hook-memory-integration.md)
    — architecture notes including the Dream Phase (offline, hook-driven
    memory consolidation).
  - Parallel agent forking section in
    [`docs/start-new-project.md`](docs/start-new-project.md).
- **Proactive Tool Suggestion rule** in `AGENTS.md` so agents surface
  Graphify or Calibration when the project warrants it.

### Changed

- **Identity cleanup**: `memory-bank/projectbrief.md`, `startup.md`,
  `techContext.md`, and `activeContext.md` no longer frame the repo as a
  "newProject (copied from template)"; they describe the template itself.
  Stack TBDs replaced with concrete "None / Pure template" values so a fresh
  clone shows accurate baseline facts.
- **Welcome banner** in [`scripts/init-fast.py`](scripts/init-fast.py)
  rewritten to enumerate what users get out of the box (canonical
  `AGENTS.md`, shared Memory Bank, FAST_INIT cost, drift-proof mirrors,
  zero-dependency validator, reusable workflows + skills, proactive
  power-ups).
- **README counts reconciled** with validator output: ~1,500 token
  FAST_INIT, 13 Memory Bank files, 9 workflows. Added a
  `--benchmark` note to prevent future drift.

### Fixed

- **Windows bootstrap crash**: `scripts/init-fast.py` configures UTF-8 stdout
  and uses an ASCII-only fallback banner, so the bootstrap no longer crashes
  on Windows consoles with cp1251 / cp1252 default codepages
  (`UnicodeEncodeError` on the rocket emoji).

## v0.1.0 — Initial template foundation

The foundation that made everything above possible.

### Added

- Model-agnostic template structure with canonical `AGENTS.md`, Memory Bank,
  Cline/Antigravity adapters, workflows, skills, docs, MCP placeholder, and
  template validator.
- Explicit initialization modes in `AGENTS.md`: `FAST_INIT` (default) and
  `DEEP_AUDIT` (explicit).
- `python scripts/check-template.py --fast` for lightweight
  startup/integration validation.
- `python scripts/init-fast.py` one-command bootstrap helper (fast
  validation + short prompt output).
- `workflows/init-lite.md` for consistent low-token initialization behavior.
- `docs/template-improvement-brief.md` as a handoff file for future
  LLM/reviewer template-improvement analysis.
- Multi-model robustness pass: cross-model handoff layer, per-model routing
  / budgets / cache list, Copilot / Cursor / Codex adapters, MCP parity,
  validator drift-check, and token benchmark.
