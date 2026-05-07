# Changelog

All notable changes to this template should be documented here.

## Unreleased

- Initial model-agnostic template structure with `AGENTS.md`, Memory Bank, Cline/Antigravity adapters, workflows, skills, docs, MCP placeholder, and template validator.
- Added explicit initialization modes in `AGENTS.md`: `FAST_INIT` (default) and `DEEP_AUDIT` (explicit).
- Added `python scripts/check-template.py --fast` for lightweight startup/integration validation.
- Added `python scripts/init-fast.py` one-command bootstrap helper (fast validation + short prompt output).
- Added `workflows/init-lite.md` for consistent low-token initialization behavior.
- Updated README and docs guides with a simpler beginner flow and clear `--fast`/`init-fast.py` usage.
- Added `docs/template-improvement-brief.md` as a handoff file for future LLM/reviewer template improvement analysis.