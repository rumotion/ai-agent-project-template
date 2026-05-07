# Active Context

## Current focus

FAST_INIT + TOKEN_SAVER initialization pass. Keep context minimal, use `AGENTS.md` as canonical instructions, and avoid deeper docs/workflows/scripts unless explicitly escalated.

## Recent changes

- Refreshed FAST_INIT Memory Bank context from allowed files only (`AGENTS.md`, `memory-bank/startup.md`, `memory-bank/00-index.md`, `README.md`, and stack-file detection).
- Verified no stack manifest/config file is present among FAST_INIT detection targets.
- Added explicit initialization modes in `AGENTS.md`: `FAST_INIT` (default) and `DEEP_AUDIT` (explicit).
- Added optional `python scripts/check-template.py --fast` for lightweight startup validation.
- Added `python scripts/init-fast.py` helper for fresh context windows.
- Added `workflows/init-lite.md` for consistent FAST_INIT behavior.

## Next step

1. Keep template memory concise and generic for fresh project copies.
2. Keep unknown product/domain details as `TBD`.
3. Escalate to `DEEP_AUDIT` only if explicitly requested or FAST_INIT-allowed files are insufficient.