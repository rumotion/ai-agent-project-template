<!-- Keep changes small and reviewable (see CONTRIBUTING.md). -->

## What changed

<!-- One or two sentences. -->

## Why

<!-- Problem this solves or value it adds. -->

## Checklist

- [ ] `python scripts/check-template.py` passes (full mode).
- [ ] Canonical content lives in `AGENTS.md` / `workflows/` / `.cline/skills/`; adapters and mirrors only point or duplicate-in-sync (no drift).
- [ ] Startup/context budgets respected; if `AGENTS.md` or a startup file grew, the FAST_INIT benchmark number in `README.md` was updated.
- [ ] No secrets, real tokens, emails, or local user paths added.
- [ ] `CHANGELOG.md` updated and `VERSION` bumped if this is a release.
- [ ] Facts are real — no invented commands, flags, or APIs. Uncertain specifics are framed as "verify in your tool's docs".
