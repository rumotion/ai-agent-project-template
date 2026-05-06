# Tech Context

## Stack

- Language: Markdown plus Python for validation
- Runtime: Python 3 for `scripts/check-template.py`
- Framework: None
- Package manager: None required
- Database: None
- Test framework: Validator script only
- Deployment: Copyable repository template

## Commands

### Install

```bash
No install step required.
```

### Run

```bash
No runtime app is included in the base template.
```

### Test

```bash
python scripts/check-template.py
```

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

The validator uses only Python standard library modules. It checks required files, adapter references, startup/context budgets, public-template secret hygiene, and required `.gitignore` safety patterns.

## Dependency rules

Do not add dependencies to the base template unless they are necessary for template functionality. Keep project-specific dependencies in copied projects.