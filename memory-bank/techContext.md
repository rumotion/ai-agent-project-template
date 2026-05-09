# Tech Context

## Stack

- Language: Markdown (docs/config) and Python (validation scripts)
- Runtime: Python (`python` command available; exact version `TBD`)
- Framework: `TBD` (no app framework detected in FAST_INIT pass)
- Package manager: `TBD` (no FAST_INIT stack manifest/config detected)
- Database: `TBD`
- Test framework: `TBD` (template uses validator scripts; project tests not defined)
- Deployment: Copyable repository template

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
python scripts/check-template.py --fast
python scripts/check-template.py
python scripts/check-template.py --benchmark
```

- `scripts/init-fast.py`: one-command FAST_INIT bootstrap (fast validation + token benchmark + short prompt).
- `--fast`: lightweight startup/integration checks aligned with FAST_INIT.
- (no flag): full template validation including secret hygiene and mirror-drift check.
- `--benchmark`: prints FAST_INIT startup-path char and approximate token cost (chars/4).

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