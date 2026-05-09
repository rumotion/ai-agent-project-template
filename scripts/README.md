# Scripts

Deterministic local scripts used by humans and agents. Standard library only — no installs required.

## Quick start (new users)

In a freshly cloned/copied template:

```bash
python scripts/init-fast.py
```

It will:

1. run `python scripts/check-template.py --fast`,
2. print the token cost of the FAST_INIT startup path,
3. print the FAST_INIT prompt to paste into a new agent context window.

## Included scripts

| Script | Purpose |
|---|---|
| `init-fast.py` | One-command bootstrap (validate + benchmark + prompt). |
| `check-template.py` | Template validator. Modes: `--fast` (lightweight), full (no flag), `--benchmark` (token cost only). |

## Validator details

Full mode enforces:

- All required files present (42 currently).
- All adapter files reference `AGENTS.md` (7 currently).
- Startup/context size budgets respected (13 budgets).
- `.gitignore` includes required safety patterns.
- Repository text scanned for secret-like content.
- SHA-256 hash equality across canonical and mirrored workflows / skills (zero drift).

## Rules

- Prefer simple, auditable scripts.
- Document inputs and side effects in the script's docstring.
- Do not store secrets in `scripts/`.
- Ask before adding scripts that call paid APIs or modify external systems.
