# AI Agent Project Template

> **One canonical instruction file. Many models. ~1,500-token startup.**
> A copyable starter for building software with AI agents that share the same memory across Claude, Gemini, ChatGPT/Codex, Cline, Cursor, Copilot, and Google Antigravity.

[![Use this template](https://img.shields.io/badge/Use%20this%20template-2ea44f?style=for-the-badge&logo=github)](https://github.com/rumotion/ai-agent-project-template/generate)
[![Latest release](https://img.shields.io/github/v/release/rumotion/ai-agent-project-template?display_name=tag&sort=semver)](https://github.com/rumotion/ai-agent-project-template/releases)
[![Validator](https://img.shields.io/badge/validator-python%20stdlib-blue)](scripts/check-template.py)
[![Bootstrap cost](https://img.shields.io/badge/FAST__INIT-%7E1.5K%20tokens-success)](#where-the-savings-come-from)
[![License](https://img.shields.io/badge/license-pick%20your%20own-lightgrey)](#license)

<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/0d6e7a40-ec62-4efb-b799-785172ac1054" />

---

## Table of contents

- [What you get](#what-you-get)
- [Quick start](#quick-start) — one command after clone
- [Why this template](#why-this-template)
- [Where the savings come from](#where-the-savings-come-from)
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
| FAST_INIT bootstrap cost | ~1,500 tokens (4 files, ~6,000 chars) |
| AI tool adapters | 7 (Claude, Gemini, Codex, Cline, Cursor, Copilot, Antigravity) |
| Memory Bank files | 13 (lazy-loaded, indexed in `00-index.md`) |
| Reusable skills | 5 |
| Reusable workflows | 9 (including Calibration and Graphify) |
| Drift protection | SHA-256 hash check across mirrors |
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
  - AGENTS.md: 3790 chars (~947 tokens)
  - memory-bank/startup.md: 495 chars (~123 tokens)
  - memory-bank/00-index.md: 1027 chars (~256 tokens)
  - memory-bank/handoff.md: 767 chars (~191 tokens)
  Total: 6079 chars (~1519 tokens)

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
Tool-specific mirrors of workflows and skills are SHA-256 hashed against the canonical copy. The validator fails if anyone forgets to sync.

---

## Where the savings come from

Most agent setups spend the first 5,000–80,000 tokens "reading the project." This template publishes a deliberately small, agent-shaped startup path:

| File | Tokens (approx) |
|---|---|
| `AGENTS.md` | 947 |
| `memory-bank/startup.md` | 123 |
| `memory-bank/00-index.md` | 256 |
| `memory-bank/handoff.md` | ~190 (volatile; ~135 on a fresh template) |
| **Total FAST_INIT** | **~1,500** |

Run `python scripts/check-template.py --benchmark` to see the exact current cost.

Three design choices keep that number small:

1. **A small canonical instruction file.** No repeated rules across tool-specific files; adapters are one-line pointers.
2. **A routing index, not a knowledge dump.** `00-index.md` tells the agent which Memory Bank file to load *for the current task*, instead of preloading them all.
3. **A handoff pointer, not a session log.** `handoff.md` is volatile and overwritten — never an append-only history.

Time savings stack on top: switch tools without re-explaining the project, because every model reads the same Memory Bank.

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
- **Dream Phase (proposal).** IDE-hook-driven offline memory consolidation. See [`docs/proposals/hook-memory-integration.md`](docs/proposals/hook-memory-integration.md).

Full list: [`docs/toolbox.md`](docs/toolbox.md).

---

## What's inside

- `AGENTS.md` — canonical instruction file for every model.
- `memory-bank/` — durable, lazy-loaded project context (13 files, indexed in `00-index.md`).
  - `handoff.md` — rolling cross-model session pointer.
  - `model-routing.md` — per-model context budgets, cache-stable file list, routing defaults.
- `workflows/` — reusable procedures (plan, implement, debug, refactor, update memory, handoff, build graph, calibrate, init-lite).
- `.cline/skills/`, `.agents/skills/` — five reusable skills (planner, Karpathy engineer, reviewer, test strategist, docs/memory maintainer).
- `scripts/check-template.py` — stdlib-only validator with `--fast`, `--benchmark`, and full mode.
- `scripts/init-fast.py` — one-command bootstrap.
- Adapters: `CLAUDE.md`, `GEMINI.md`, `.clinerules/`, `.agents/`, `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`.
- `.mcp/mcp_config.example.json` — example MCP servers (GitHub, filesystem, fetch, git).
- `references/`, `assets/` — reference material and project asset folders.

---

## Documentation map

- [`docs/start-new-project.md`](docs/start-new-project.md) — beginner walkthrough from clone to first feature.
- [`docs/use-from-github.md`](docs/use-from-github.md) — GitHub template, clone, ZIP, and pull-into-existing-project flows.
- [`docs/setup.md`](docs/setup.md) — one-page local setup.
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
python scripts/check-template.py --benchmark   # token cost report only
```

Full validation enforces: 42 required files, 7 adapters all referencing `AGENTS.md`, 13 startup/context size budgets, public-template secret hygiene, `.gitignore` safety patterns, and SHA-256 drift between canonical and mirrored workflows/skills.

---

## Publishing your copy

1. Run `python scripts/check-template.py` and confirm it passes.
2. Confirm no `.env`, credential files, or unintended `.git/` history are committed.
3. Add a `LICENSE` file that matches your intent (MIT, Apache-2.0, etc.) — not included by default so you can choose.
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

This template ships without a license so you can pick the one that matches your project. Add a `LICENSE` file before publishing publicly.
