# AI Agent Project Template

> **One canonical instruction file. Many models. ~1,900-token startup.**
> A copyable starter for building software with AI agents that share the same memory across Claude, Gemini, ChatGPT/Codex, Cline, Roo Code, Cursor, Windsurf, Copilot, Aider, and Google Antigravity.

[![Use this template](https://img.shields.io/badge/Use%20this%20template-2ea44f?style=for-the-badge&logo=github)](https://github.com/rumotion/ai-agent-project-template/generate)
[![Latest release](https://img.shields.io/github/v/release/rumotion/ai-agent-project-template?display_name=tag&sort=semver)](https://github.com/rumotion/ai-agent-project-template/releases)
[![Validate template](https://github.com/rumotion/ai-agent-project-template/actions/workflows/validate.yml/badge.svg)](https://github.com/rumotion/ai-agent-project-template/actions/workflows/validate.yml)
[![Validator](https://img.shields.io/badge/validator-python%20stdlib-blue)](scripts/check-template.py)
[![Bootstrap cost](https://img.shields.io/badge/FAST__INIT-%7E1.9K%20tokens-success)](#where-the-savings-come-from)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<img src="assets/images/hero-template.svg" alt="AI Agent Project Template — one canonical AGENTS.md and a shared Memory Bank read by Claude, Gemini, Codex, Cline, Roo Code, Cursor, Windsurf, Copilot, Aider, and Antigravity, with an atomic Plan-Execute-Verify-Commit-Reflect workflow. ~1.9K-token startup." width="1280" />

---

## Table of contents

- [What you get](#what-you-get)
- [Quick start](#quick-start) — one command after clone
- [Why this template](#why-this-template)
- [Where the savings come from](#where-the-savings-come-from)
- [Atomic step-commit workflow](#atomic-step-commit-workflow)
- [Multi-model continuity](#multi-model-continuity)
- [Optional power-ups](#optional-power-ups)
- [What's inside](#whats-inside)
- [Documentation map](#documentation-map)
- [Validation](#validation)
- [Publishing your copy](#publishing-your-copy)
- [Releases & changelog](#releases--changelog)
- [Contributing](#contributing)
- [License](#license)

---

## What you get

| | |
|---|---|
| FAST_INIT bootstrap cost | ~1,886 tokens (4 files, 7,545 chars) |
| AI tool adapters | 9 (Claude, Gemini, Codex, Cline, Roo Code, Cursor, Windsurf, Copilot, Aider; + Antigravity) |
| Memory Bank files | 14 (lazy-loaded, indexed in `00-index.md`) |
| Reusable skills | 6 (portable `.agents/skills` source + Claude/Cline mirrors) |
| Reusable workflows | 14 (incl. pre-edit check, spec-driven development, self-evaluation, critic-review, autonomous-agent, Calibration, Graphify) |
| MCP config | Claude `.mcp.json`, VS Code config, and inactive Gemini/Codex native examples (spec 2025-11-25) |
| Automation | Shared hook library (`scripts/hooks/`), Claude Code hooks + `/handoff`, `/save-context`, `/start-task` commands |
| Continuous validation | GitHub Actions on Linux + Windows |
| Drift protection | SHA-256 checks across workflow and three-tree skill mirrors |
| Agentic loop | Plan → Execute → Verify → Commit → Reflect with per-checkpoint atomic commits |
| Validator dependencies | 0 (Python stdlib only) |
| First command after clone | `python scripts/init-fast.py` |

Numbers reproduced live by `python scripts/check-template.py --benchmark`.

---

## Quick start

Three steps from zero to a working agent:

```bash
# 1. Create your project from this template (or clone / ZIP)
#    On GitHub: click "Use this template" → "Create a new repository"
git clone https://github.com/<your-user>/<your-new-repo>.git
cd <your-new-repo>

# 2. Bootstrap (validates the template + prints a ~1,500-token prompt)
python scripts/init-fast.py

# 3. Paste the printed prompt into a fresh agent context window
#    (Claude Code, Gemini in Antigravity, ChatGPT/Codex, Cline, etc.)
```

That's it. The agent reads `AGENTS.md`, fills the Memory Bank from your actual repo state, and keeps unknowns marked `TBD` instead of inventing facts.

**A first session looks like this:**

```text
$ python scripts/init-fast.py
== FAST_INIT bootstrap ==
Template FAST validation passed.
FAST_INIT startup-path size:
  - AGENTS.md: 4588 chars (~1147 tokens)
  - memory-bank/startup.md: 495 chars (~123 tokens)
  - memory-bank/00-index.md: 1540 chars (~385 tokens)
  - memory-bank/handoff.md: 922 chars (~230 tokens)
  Total: 7545 chars (~1886 tokens)

============================================================
WELCOME TO THE AI AGENT PROJECT TEMPLATE
============================================================
What this template gives you out of the box:
 * One canonical instruction file (AGENTS.md) read by every model.
 * Shared Memory Bank for cross-session and cross-model continuity.
 * FAST_INIT bootstrap so agents skip the usual 5K-80K token warm-up.
 * Drift-proof mirrors of workflows and skills (SHA-256 checked).
 * Zero-dependency validator (Python stdlib only).
 * Reusable workflows + skills (plan, implement, debug, refactor, ...).
 * Proactive power-ups: Graphify, Calibration, /align, /devil, /burst.
============================================================
```

---

## Why this template

**One source of truth, many models.**
`AGENTS.md` is canonical. Every tool-specific file is a one-line pointer to it. Switch from Claude to Gemini to ChatGPT mid-project without re-explaining anything.

**Continuity across model switches.**
`memory-bank/handoff.md` is a single rolling pointer for "where we left off." Any model writes it on pause, any model reads it on resume — so Claude can finish what Gemini started.

**Minimal startup tokens.**
The default startup path is four small files. Everything else lazy-loads only when the task needs it. Agents stop burning tokens crawling docs they don't need.

**No tool lock-in, no installs.**
The validator runs on Python stdlib alone. No Node, no global packages, no MCP server required for the template itself.

**Drift-proof by construction.**
Tool-specific workflow and skill mirrors are SHA-256 hashed against their canonical copies. The validator fails if anyone forgets to sync.

---

## Where the savings come from

Most agent setups spend the first 5,000–80,000 tokens "reading the project." This template publishes a deliberately small, agent-shaped startup path:

| File | Tokens (approx) |
|---|---|
| `AGENTS.md` | 1,147 |
| `memory-bank/startup.md` | 123 |
| `memory-bank/00-index.md` | 385 |
| `memory-bank/handoff.md` | ~230 (volatile; lighter on a fresh template) |
| **Total FAST_INIT** | **~1,886** |

Run `python scripts/check-template.py --benchmark` to see the exact current cost.

Three design choices keep that number small:

1. **A small canonical instruction file.** No repeated rules across tool-specific files; adapters are one-line pointers.
2. **A routing index, not a knowledge dump.** `00-index.md` tells the agent which Memory Bank file to load *for the current task*, instead of preloading them all.
3. **A handoff pointer, not a session log.** `handoff.md` is volatile and overwritten — never an append-only history.

Time savings stack on top: switch tools without re-explaining the project, because every model reads the same Memory Bank.

---

## Atomic step-commit workflow

<p align="center">
  <img src="assets/images/atomic-step-commit-workflow.svg" alt="Atomic Step-Commit Workflow — Plan, Execute, Verify, Commit, Reflect cycle with per-checkpoint Conventional Commits" width="900" />
</p>

Every implementation runs as **Plan → Execute → Verify → Commit → Reflect**: plans break work into discrete, individually verifiable checkpoints, and each verified checkpoint is committed immediately with Conventional Commit syntax. You get a clean, bisectable history where every commit is a working state — and rollbacks cost nothing.

- `AGENTS.md` carries the always-on rule; [`docs/agent-loop.md`](docs/agent-loop.md) §4 holds the operational detail.
- [`workflows/plan-task.md`](workflows/plan-task.md) requires committable step checkpoints; [`workflows/implement-task.md`](workflows/implement-task.md) commits each one.
- The validator enforces all 9 workflows across 3 mirror trees, so the rule cannot drift between tools.

---

## Multi-model continuity

You can drive the same project with several models in sequence or in parallel. Default routing:

| Role | Default model | Why |
|---|---|---|
| Planning, broad reads | Gemini Ultra (Antigravity) | ~1M context |
| Implementation | Cline / Codex / ChatGPT | Tight tool loops |
| Review and refactor | Claude (Teams or Code) | Reasoning + prompt cache |
| Fast utility | OpenRouter free models | Cheap; often <32K context — FAST_INIT essential |

Each model reads `memory-bank/handoff.md` on resume and updates it on pause. Cache-stable files (listed in `memory-bank/model-routing.md`) stay byte-stable so Claude prompt-cache hits stay warm across sessions.

---

## Optional power-ups

The template scales with your project. These are kept **out of the fast path** so you aren't forced to use them; activate any of them when needed:

- **Graphify (Knowledge Graphs).** When grepping fails in large codebases, run `uv tool install graphifyy && graphify .` to build a structural graph of your code. Agents automatically read the resulting `GRAPH_REPORT.md`. See [`workflows/build-graph.md`](workflows/build-graph.md).
- **Advanced Steering Prompts.** Force clarification, contrarian review, or divergent options on demand: `/align`, `/devil`, `/burst`, `/calibrate`. See [`docs/prompts.md`](docs/prompts.md).
- **Parallel Agent Forking.** Open a second terminal, run `init-fast.py`, and have multiple agents work on different features simultaneously — sharing context through the Memory Bank. See [`docs/start-new-project.md`](docs/start-new-project.md).
- **Zero-token automation (hooks).** Shared stdlib scripts guard sensitive paths and log normalized write metadata outside model context. Claude mappings are active; Gemini and Codex mappings ship as inactive native examples. See [`docs/hooks.md`](docs/hooks.md).
- **Critic & autonomous workflows.** Run a separate-context critic over risky artifacts, or drive a bounded hands-off run with explicit guardrails. See [`workflows/critic-review.md`](workflows/critic-review.md) and [`workflows/autonomous-agent.md`](workflows/autonomous-agent.md).
- **Portable read-only reviewer.** One canonical reviewer contract has minimal
  native Gemini, Codex, and Claude adapters; behavioral smoke pilots remain
  explicit and manual. See [`docs/reviewer-role.md`](docs/reviewer-role.md).
- **Local context experiments.** Five deterministic scenarios measure declared
  file context and compare sanitized manual usage totals without model or
  network calls. See [`benchmarks/context/README.md`](benchmarks/context/README.md).

Full list: [`docs/toolbox.md`](docs/toolbox.md).

---

## What's inside

- `AGENTS.md` — canonical instruction file for every model, incl. the always-on "Agentic execution" rules.
- `memory-bank/` — durable, lazy-loaded project context (14 files, indexed in `00-index.md`).
  - `handoff.md` — rolling cross-model session pointer (structured YAML header + prose).
  - `reminders.md` — prospective memory: trigger-keyed notes for future work.
  - `model-routing.md` — per-model context budgets, cache-stable file list, cascade routing, routing defaults.
- `docs/agent-loop.md` — tool-call batching, turn budgets, error/retry taxonomy, phase-completion summary.
- `docs/hooks.md` + `scripts/hooks/` — shared zero-dependency hook library (`log-writes.py`, `guard-sensitive-paths.py`, `verify-fixtures.py`).
- `docs/reviewer-role.md` + native `reviewer` adapters — one portable,
  read-only specialist contract for Gemini, Codex, and Claude.
- `benchmarks/context/` + `scripts/benchmark-context.py` — deterministic
  context scenarios and optional paired-usage comparison.
- `workflows/` — 14 reusable procedures (pre-edit check, spec-driven development, self-evaluate, critic-review, autonomous-agent, handoff, build graph, etc.).
- `.agents/skills/` — canonical source for six reusable Agent Skills (incl. `delegation-coordinator`); `.claude/skills/` and `.cline/skills/` are SHA-256-checked discovery mirrors.
- `scripts/check-template.py` — stdlib-only validator with `--fast`, `--compat`, `--benchmark`, and full mode.
- `scripts/init-fast.py` — one-command bootstrap.
- Adapters: `CLAUDE.md`, `GEMINI.md`, `CONVENTIONS.md` (Aider), `.windsurfrules`, `.clinerules/` (Cline + Roo Code), `.agents/`, `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`.
- `.mcp.json`, `.vscode/mcp.json`, `.gemini/settings.example.json`, `.codex/config.example.toml` — Claude/VS Code MCP starters and inactive Gemini/Codex native examples.
- `references/`, `assets/` — reference material and project asset folders.
- [`docs/start-new-project.md`](docs/start-new-project.md) — beginner walkthrough from clone to first feature.
- [`docs/per-tool-setup.md`](docs/per-tool-setup.md) — exactly which file each of the 9 tools reads, and how to wire MCP.
- [`docs/agent-compatibility.md`](docs/agent-compatibility.md) — last-verified Gemini, Codex, and Claude instruction, skill, MCP, hook, and subagent paths.
- [`docs/context-memory-bridges.md`](docs/context-memory-bridges.md) —
  authority and safety guidance for optional provider-local memory.
- [`docs/protocol-watch.md`](docs/protocol-watch.md) — dated MCP, Agent
  Skills, ACP, and A2A adoption gates.
- [`docs/performance-experiments.md`](docs/performance-experiments.md) —
  evidence templates for optional compression/proxy trials.
- [`docs/use-from-github.md`](docs/use-from-github.md) — GitHub template, clone, ZIP, and pull-into-existing-project flows.
- [`docs/setup.md`](docs/setup.md) — one-page local setup.
- [`docs/agent-loop.md`](docs/agent-loop.md) — execution rules: tool batching, turn budgets, error taxonomy, phase-completion summary.
- [`docs/hooks.md`](docs/hooks.md) — shared Claude, Gemini, and Codex hook mappings and safety contract.
- [`docs/file-organization.md`](docs/file-organization.md) — where to put research, assets, and runtime files.
- [`docs/toolbox.md`](docs/toolbox.md) — catalog of every optional power-up.
- [`docs/prompts.md`](docs/prompts.md) — reusable prompts (`/calibrate`, `/align`, `/devil`, `/burst`, init prompts).
- [`docs/agent-skill-ecosystem.md`](docs/agent-skill-ecosystem.md) — when and how to add skills or plugins.
- [`docs/antigravity-master-prompt.md`](docs/antigravity-master-prompt.md) — long-form initialization prompt.
- [`docs/architecture.md`](docs/architecture.md) — placeholder for project-specific architecture.
- [`docs/template-improvement-brief.md`](docs/template-improvement-brief.md) — handoff brief for reviewers proposing template improvements.
- [`docs/releasing.md`](docs/releasing.md) — how to cut a new tagged release of the template.

---

## Validation

```bash
python scripts/init-fast.py                    # bootstrap (validate + benchmark + prompt)
python scripts/check-template.py --fast        # lightweight check
python scripts/check-template.py               # full check (secrets, drift, all required files)
python scripts/check-template.py --compat      # Gemini/Codex/Claude contracts
python scripts/check-template.py --benchmark   # token cost report only
python scripts/benchmark-context.py --self-test
python scripts/benchmark-context.py --scenario fast-init
```

Full validation enforces required files, 9 adapters referencing `AGENTS.md`,
exact primary adapter imports, 15 per-file budgets, a 7,600-character aggregate
FAST_INIT cap, Agent Skills schema checks, public-template secret hygiene,
native hook/MCP/reviewer structures, the context-harness self-test,
`.gitignore` safety patterns, and SHA-256 drift across canonical and mirrored
workflows/skills.

CI runs fast, full, compatibility, startup benchmark, and context-harness
self-tests on every push and PR across Linux and Windows using Python 3.9 and
current Python 3.x ([`.github/workflows/validate.yml`](.github/workflows/validate.yml)).

---

## Publishing your copy

1. Run `python scripts/check-template.py` and confirm it passes.
2. Confirm no `.env`, credential files, or unintended `.git/` history are committed.
3. Review the included MIT `LICENSE`; replace it before publishing if your
   project requires different terms.
4. In GitHub repository settings, enable **Template repository** so others can create clean copies via **Use this template**.

### Where to put your files

- Research PDFs, briefs, transcripts, reference-only images → `references/`
- Source project assets (images, content data) → `assets/`
- Runtime website/app files → stack-specific folder (usually `public/` or `src/assets/`) once a stack is chosen
- Durable project facts → `memory-bank/`
- Secrets, real keys, credentials → never committed (use local `.env`, OS keychain, IDE settings)

Full guide: [`docs/file-organization.md`](docs/file-organization.md).

---

## Releases & changelog

This template follows [Semantic Versioning](https://semver.org/) with dated entries in [`CHANGELOG.md`](CHANGELOG.md). The current version lives in [`VERSION`](VERSION).

**For users of the template:**
- [Latest release](https://github.com/rumotion/ai-agent-project-template/releases/latest) — what changed and how to upgrade.
- [All releases](https://github.com/rumotion/ai-agent-project-template/releases) — full history.
- [`CHANGELOG.md`](CHANGELOG.md) — machine- and human-readable list of changes per version.

**For maintainers:** the step-by-step process for cutting a new release is in [`docs/releasing.md`](docs/releasing.md).

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Keep changes small and reviewable. Run `python scripts/check-template.py` before opening a PR.

Security issues: see [`SECURITY.md`](SECURITY.md).

---

## License

Released under the [MIT License](LICENSE). A project created from this template
may replace the license before publishing if it needs different terms.
