# Setup

Quick local setup and verification.

## Prerequisites

- Python on `PATH` (`python --version`)
- Git (recommended)
- Your preferred coding agent / IDE: Claude Code, ChatGPT/Codex, Google Antigravity (Gemini), Cline, Cursor, Copilot, or any VS Code-compatible AI tool

## One-command bootstrap

```bash
python scripts/init-fast.py
```

This runs the lightweight validator, prints the FAST_INIT token cost, and prints a short prompt to paste into a new agent context window.

## Validation modes

```bash
python scripts/check-template.py --fast        # lightweight startup/integration checks
python scripts/check-template.py               # full validation (secrets, drift, required files)
python scripts/check-template.py --benchmark   # FAST_INIT startup-path token cost
```

| Mode | What it checks |
|---|---|
| `--fast` | required FAST_INIT files, adapter references, context budgets, `.gitignore` safety |
| full (no flag) | everything in `--fast`, plus repo-wide secret hygiene and SHA-256 mirror drift |
| `--benchmark` | character and approximate token cost of the FAST_INIT startup path |

## Environment variables

Use `.env.example` as the documented set of variables. Keep real values out of Git — use local `.env`, OS keychain, or your IDE's secret store.

Common keys for a multi-model project:

```text
OPENROUTER_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

## Resuming work across models

If multiple models share this project, update `memory-bank/handoff.md` on pause and read it on resume. See `workflows/handoff.md` for the protocol.

## Troubleshooting

- Fast validation fails → fix listed missing files / patterns first; re-run.
- Full validation fails on secret hygiene → remove or replace sensitive values, then re-run.
- Mirror drift reported → resync the affected files from canonical (`workflows/`, `.cline/skills/`).
