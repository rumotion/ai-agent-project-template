# Scripts

This folder contains deterministic local scripts used by humans and agents.

## Quick start (new users)

Run this first in a freshly cloned template:

```bash
python scripts/init-fast.py
```

It will:

1. run `python scripts/check-template.py --fast`
2. print a short FAST_INIT prompt for a new agent context window

Rules:

- Prefer simple, auditable scripts.
- Document inputs and side effects.
- Do not store secrets here.
- Ask before adding scripts that call paid APIs or modify external systems.

## Included scripts

- `check-template.py`: template validation (`--fast` for lightweight checks; default for full checks).
- `init-fast.py`: runs `check-template.py --fast` and prints a short FAST_INIT prompt for a fresh agent context window.