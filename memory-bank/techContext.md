# Tech Context

## Stack

- Language: Markdown (docs/config) and Python (validation scripts)
- Runtime: Python 3.9+ (validated locally on 3.13; CI covers 3.9 and current 3.x)
- Framework: None (Pure template)
- Package manager: None
- Database: None
- Test framework: Python validator scripts (`scripts/check-template.py`)
- Deployment: GitHub Template

## Commands

### Install

```bash
TBD per copied project.
```

### Run

```bash
TBD per copied project.
```

### Test

```bash
python scripts/init-fast.py
python scripts/hooks/verify-fixtures.py
python scripts/benchmark-context.py --self-test
python scripts/benchmark-context.py --scenario fast-init
python scripts/check-template.py --fast
python scripts/check-template.py --compat
python scripts/check-template.py
python scripts/check-template.py --benchmark
```

- `scripts/hooks/verify-fixtures.py`: temp-only behavioral tests for normalized
  records, redaction, malformed input, and Claude/Gemini/Codex denial outputs.
- `scripts/benchmark-context.py`: offline manifest measurement and sanitized
  paired-usage comparison; no model or network calls.
- `scripts/init-fast.py`: one-command FAST_INIT bootstrap (fast validation + token benchmark + short prompt).
- `--fast`: lightweight startup/integration checks aligned with FAST_INIT.
- `--compat`: full Gemini/Codex/Claude compatibility-contract validation.
- (no flag): full template validation including secret hygiene and mirror-drift check.

### Lint

```bash
TBD per copied project
```

### Build

```bash
TBD per copied project
```

## Environment variables

See `.env.example`.

## Tooling notes

Initialization behavior is policy-driven through `AGENTS.md` (`FAST_INIT` default, `DEEP_AUDIT` explicit).

Use `scripts/init-fast.py` for fresh-context bootstrap prompts and `check-template.py --fast` for lightweight validation.

FAST_INIT stack detection found no `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `tsconfig.json`, `vite.config.*`, or `next.config.*` files.

## Dependency rules

Do not add dependencies to the base template unless they are necessary for template functionality. Keep project-specific dependencies in copied projects.
