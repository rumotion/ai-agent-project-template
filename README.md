# AI Agent Project Template

A copyable starter for building software with AI agents. One canonical instruction file, multi-model handoff, and a single-command bootstrap that costs roughly **1,500 tokens** to initialize (under 1,400 if `handoff.md` is skipped on a fresh start).

Works with Claude Code, ChatGPT / Codex, Gemini (Google Antigravity), OpenRouter-backed models and in Cline — sharing the same project memory across all of them.

<img width="1122" height="1402" alt="image" src="https://github.com/user-attachments/assets/b18e7cc3-39dd-496e-88e0-c3665bdec370" />


## At a glance

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

Numbers reproduced by `python scripts/check-template.py --benchmark`.

## Why this template

**One source of truth, many models.**
`AGENTS.md` is canonical. Every tool-specific file is a thin pointer to it. Switch from Claude to Gemini to ChatGPT mid-project without re-explaining anything.

**Continuity across model switches.**
`memory-bank/handoff.md` is a single rolling pointer for "where we left off". Any model writes it on pause, any model reads it on resume — so Claude can finish what Gemini started.

**Minimal startup tokens.**
The default startup path is four small files. Everything else lazy-loads only when the task needs it. Agents stop burning tokens crawling docs they don't need.

**No tool lock-in, no installs.**
The validator runs on Python stdlib alone. No Node, no global packages, no MCP server required for the template itself.

**Drift-proof by construction.**
Tool-specific mirrors of workflows and skills are SHA-256 hashed against the canonical copy. The validator fails if anyone forgets to sync.

## Where the savings come from

Most agent setups spend the first 5,000–80,000 tokens "reading the project". This template publishes a deliberately small, agent-shaped startup path:

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

## Quick start

After cloning, downloading the ZIP, or using GitHub's **Use this template**:

```bash
python scripts/init-fast.py
```

That one command:

1. validates the template (lightweight check),
2. prints the token cost of the startup path,
3. prints the FAST_INIT prompt to paste into a fresh agent context window.

Open the project in your IDE, paste the prompt, and the agent initializes Memory Bank from your project's actual state — keeping unknowns as `TBD` instead of inventing them.

A first session typically looks like:

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

Validation succeeded.

============================================================
WELCOME TO THE AI AGENT PROJECT TEMPLATE
============================================================
What this template gives you out of the box:
 * One canonical instruction file (AGENTS.md) read by every model
   (Claude, Gemini, ChatGPT/Codex, Cline, Cursor, Copilot,
   Antigravity) - no per-tool rewrites.
 * Shared Memory Bank for cross-session and cross-model continuity
   (handoff.md lets one model pick up where another left off).
 * FAST_INIT bootstrap (~1.3-1.5K tokens) so agents skip the usual
   5K-80K token "read the whole repo" warm-up.
 * Drift-proof mirrors of workflows and skills (SHA-256 checked).
 * Zero-dependency validator (Python stdlib only).
 * Reusable workflows + skills (plan, implement, debug, refactor,
   handoff, calibrate, build-graph) ready to lazy-load when needed.
 * Proactive power-ups: agents will suggest Graphify, Calibration,
   or steering prompts (/align, /devil, /burst) as your project
   grows. See docs/toolbox.md for the full list.

Next: paste the prompt below into a fresh agent context window.
============================================================

Paste this into a new agent context window:

---
FAST_INIT + TOKEN_SAVER.
Follow AGENTS.md initialization modes exactly.
Use minimal turns and minimal narration.
Update only allowed Memory Bank files.
If resuming, also read memory-bank/handoff.md.
Keep unknowns as TBD.
Ask only critical questions before any escalation.
Return a short final summary.
---
```

## Multi-model continuity

You can drive the same project with several models in sequence or in parallel. Default routing:

| Role | Default model | Why |
|---|---|---|
| Planning, broad reads | Gemini Ultra (Antigravity) | ~1M context |
| Implementation | Cline / Codex / ChatGPT | Tight tool loops |
| Review and refactor | Claude (Teams or Code) | Reasoning + prompt cache |
| Fast utility | OpenRouter free models | Cheap; often <32K context — FAST_INIT essential |

Each model reads `memory-bank/handoff.md` on resume and updates it on pause. Cache-stable files (listed in `memory-bank/model-routing.md`) stay byte-stable so Claude prompt-cache hits stay warm across sessions.

## 🧰 Power Tools & Toolbox (Optional)

As your project grows, this template scales with you. We keep these out of the fast-path so you aren't forced to use them, but you can activate them at any time:

- **Graphify (Knowledge Graphs):** When grepping fails in large codebases, run `uv tool install graphifyy && graphify .` to build a structural graph of your code. Your agents will automatically read the resulting `GRAPH_REPORT.md`. (See `workflows/build-graph.md`).
- **Advanced Steering Prompts:** Take control of your AI with commands like `/align` (force clarification), `/devil` (red-teaming), and `/calibrate` (auto-tune memory rules). (See `docs/prompts.md`).
- **Parallel Agent Forking:** Open a new terminal, run `init-fast.py`, and have multiple agents working on different features simultaneously. (See `docs/start-new-project.md`).

For a full list of integrations, see `docs/toolbox.md`.

## What's inside

- `AGENTS.md` — canonical instruction file for every model.
- `memory-bank/` — durable, lazy-loaded project context (13 files, indexed in `00-index.md`).
  - `handoff.md` — rolling cross-model session pointer.
  - `model-routing.md` — per-model context budgets, cache-stable file list, routing defaults.
- `workflows/` — reusable procedures (plan, implement, debug, refactor, update memory, handoff, build graph, calibrate).
- `.cline/skills/`, `.agents/skills/` — five reusable skills (planner, Karpathy engineer, reviewer, test strategist, docs/memory maintainer), plus third-party integration recommendations (e.g. Graphify).
- `scripts/check-template.py` — stdlib-only validator with `--fast`, `--benchmark`, and full mode.
- `scripts/init-fast.py` — one-command bootstrap.
- Adapters: `CLAUDE.md`, `GEMINI.md`, `.clinerules/`, `.agents/`, `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`.
- `.mcp/mcp_config.example.json` — example MCP servers (GitHub, filesystem, fetch, git).
- `references/`, `assets/` — reference material and project asset folders.

## Documentation map

- [`docs/start-new-project.md`](docs/start-new-project.md) — beginner walkthrough from clone to first feature.
- [`docs/use-from-github.md`](docs/use-from-github.md) — GitHub template, clone, ZIP, and advanced pull-into-existing-project flows.
- [`docs/setup.md`](docs/setup.md) — one-page local setup.
- [`docs/file-organization.md`](docs/file-organization.md) — where to put research, assets, and runtime files.
- [`docs/agent-skill-ecosystem.md`](docs/agent-skill-ecosystem.md) — when and how to add skills or plugins.
- [`docs/antigravity-master-prompt.md`](docs/antigravity-master-prompt.md) — long-form initialization prompt.
- [`docs/prompts.md`](docs/prompts.md) — reusable prompts for common operations.
- [`docs/architecture.md`](docs/architecture.md) — placeholder for project-specific architecture.
- [`docs/template-improvement-brief.md`](docs/template-improvement-brief.md) — handoff brief for reviewers proposing template improvements.

## Validation

```bash
python scripts/init-fast.py                    # bootstrap (validate + benchmark + prompt)
python scripts/check-template.py --fast        # lightweight check
python scripts/check-template.py               # full check (secrets, drift, all required files)
python scripts/check-template.py --benchmark   # token cost report only
```

Full validation enforces: 42 required files, 7 adapters all referencing `AGENTS.md`, 13 startup/context size budgets, public-template secret hygiene, `.gitignore` safety patterns, and SHA-256 drift between canonical and mirrored workflows/skills.

## Where to put your files

See [`docs/file-organization.md`](docs/file-organization.md) for the full guide.

- Research PDFs, briefs, transcripts, reference-only images → `references/`
- Source project assets (images, content data) → `assets/`
- Runtime website/app files → stack-specific folder (usually `public/` or `src/assets/`) once a stack is chosen
- Durable project facts → `memory-bank/`
- Secrets, real keys, credentials → never committed (use local `.env`, OS keychain, IDE settings)

## Publishing your copy

1. Run `python scripts/check-template.py` and confirm it passes.
2. Confirm no `.env`, credential files, or unintended `.git/` history are committed.
3. Add a `LICENSE` file that matches your intent (MIT, Apache-2.0, etc.) — not included by default so you can choose.
4. In GitHub repository settings, enable **Template repository** so others can create clean copies via **Use this template**.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Keep changes small and reviewable. Run `python scripts/check-template.py` before opening a PR.

## License

This template ships without a license so you can pick the one that matches your project. Add a `LICENSE` file before publishing.
