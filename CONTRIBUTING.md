# Contributing

Thanks for considering a contribution. The template is intentionally small — keep that property in mind.

## Before changing files

1. Read `AGENTS.md`.
2. Read `memory-bank/startup.md` and `memory-bank/00-index.md` to understand current state.
3. If resuming someone else's work, read `memory-bank/handoff.md`.

## Development expectations

- Keep changes small and reviewable.
- Update relevant Memory Bank files when project knowledge changes.
- Do not commit secrets or generated artifacts.
- Run `python scripts/check-template.py` (full) before opening a PR.

## Template invariants

When changing this template, keep it:

- **Model-agnostic.** Anything model-specific belongs in adapters or `memory-bank/model-routing.md`, not in `AGENTS.md`.
- **Concise.** The FAST_INIT startup path stays small. Run `python scripts/check-template.py --benchmark` before/after non-trivial changes.
- **Copyable.** No external dependencies for validation; standard library only.
- **Drift-proof.** Canonical workflows live in `workflows/`; canonical skills live in `.cline/skills/`. Mirrors must be byte-identical (the validator enforces this).
- **Safe by default.** No real secrets, tokens, or local user paths in committed files.

## Adding or changing files

| You want to … | Where it goes |
|---|---|
| Add a tool adapter | New thin pointer file referencing `AGENTS.md`; add it to `ADAPTER_FILES` and `REQUIRED_FILES` in the validator |
| Add a workflow | Canonical: `workflows/`. Sync identical content to `.clinerules/workflows/` and `.agents/workflows/` |
| Add a skill | Canonical: `.cline/skills/<name>/SKILL.md`. Sync identical content to `.agents/skills/<name>/SKILL.md` |
| Add Memory Bank context | Concise file in `memory-bank/`; add a row to `memory-bank/00-index.md` |
| Add a doc | Lazy-loaded file in `docs/`; do not add to FAST_INIT eager reads |

## Validation

```bash
python scripts/check-template.py --fast        # lightweight
python scripts/check-template.py               # full (required for PRs)
python scripts/check-template.py --benchmark   # token cost
```

A passing full run is the bar for merge.

## License

This repository ships without a license file so consumers can pick. Maintainers can add a `LICENSE` if/when the project chooses one.
