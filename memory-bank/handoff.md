# Handoff

Cross-model session handoff. Update when pausing, switching models, or finishing a meaningful step. Keep under 30 lines.

- Last touched: 2026-05-14
- Last model: Claude Sonnet 4.6 (1M)
- Branch: main
- Status: ready_for_release

## Current task

Added context-hygiene cheatsheet derived from May-2026 guide + recent Claude Code release notes. Template still ready for publishing.

## Last concrete action

Created `docs/context-hygiene.md`; added cache-ordering rule and reasoning-effort table to `model-routing.md`; pointer rows in `00-index.md` and `toolbox.md`. `AGENTS.md` unchanged (cache-stable).

## Next concrete step

Run `python scripts/check-template.py` if publishing; otherwise resume normal work.

## Files touched this session

- docs/context-hygiene.md (new)
- memory-bank/{00-index.md, model-routing.md, handoff.md}
- docs/toolbox.md

## Open questions / blockers

- None.

## Notes for next model

Run `python scripts/init-fast.py` once on the target platform before publishing.
