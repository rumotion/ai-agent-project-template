# Setup

Use this file for quick local setup and verification.

## Prerequisites

- Python available as `python` in your terminal
- Git (recommended)
- Your preferred coding agent/IDE (Cline, Antigravity, VS Code, etc.)

## Fresh template bootstrap

Run:

```bash
python scripts/init-fast.py
```

This command:

1. runs `python scripts/check-template.py --fast`
2. prints a short FAST_INIT prompt to paste into a new context window

## Validation modes

```bash
python scripts/check-template.py --fast
python scripts/check-template.py
```

- `--fast`: lightweight startup/integration checks
- full (no flag): deeper template/publish validation

## Environment variables

Use `.env.example` as reference and keep real values out of Git.

## Troubleshooting

- If fast validation fails, fix reported missing files/patterns first.
- If full validation fails on secret hygiene, remove/replace sensitive values and re-run.