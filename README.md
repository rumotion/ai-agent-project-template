# AI Agent Project Template

A copyable starter for building software with AI agents. One canonical instruction file, multi-model handoff, and a single-command bootstrap that costs roughly **1,344 tokens** to initialize.

Works with Claude Code, ChatGPT / Codex, Gemini (Google Antigravity), OpenRouter-backed models and in Cline — sharing the same project memory across all of them.

<img width="1122" height="1402" alt="image" src="https://github.com/user-attachments/assets/b18e7cc3-39dd-496e-88e0-c3665bdec370" />


## At a glance

| | |
|---|---|
| FAST_INIT bootstrap cost | ~1,344 tokens (4 files, 5,378 chars) |
| AI tool adapters | 7 (Claude, Gemini, Codex, Cline, Cursor, Copilot, Antigravity) |
| Memory Bank files | 12 (lazy-loaded) |
| Reusable skills | 5 |
| Reusable workflows | 6 |
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
| `AGENTS.md` | 870 |
| `memory-bank/startup.md` | 150 |
| `memory-bank/00-index.md` | 217 |
| `memory-bank/handoff.md` | 106 |
| **Total FAST_INIT** | **~1,344** |

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
  - AGENTS.md: 3482 chars (~870 tokens)
  - memory-bank/startup.md: 601 chars (~150 tokens)
  - memory-bank/00-index.md: 871 chars (~217 tokens)
  - memory-bank/handoff.md: 424 chars (~106 tokens)
  Total: 5378 chars (~1344 tokens)

Validation succeeded.

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

## What's inside

- `AGENTS.md` — canonical instruction file for every model.
- `memory-bank/` — durable, lazy-loaded project context (12 files, indexed in `00-index.md`).
  - `handoff.md` — rolling cross-model session pointer.
  - `model-routing.md` — per-model context budgets, cache-stable file list, routing defaults.
- `workflows/` — six reusable procedures (plan, implement, debug, refactor, update memory, handoff).
- `.cline/skills/`, `.agents/skills/` — five reusable skills (planner, Karpathy engineer, reviewer, test strategist, docs/memory maintainer).
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
