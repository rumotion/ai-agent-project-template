# Changelog

All notable changes to this template should be documented here.

## Unreleased

## 2026-05-13 — Audit + Windows-safe bootstrap

- **Cross-platform bootstrap fix**: `scripts/init-fast.py` now configures UTF-8 stdout and uses ASCII-only fallback banners, so the bootstrap no longer crashes on Windows consoles with cp1251/cp1252 default codepages.
- **Expanded welcome banner**: First-run output now lists the template's main capabilities (canonical AGENTS.md, shared Memory Bank, FAST_INIT cost range, drift-proof mirrors, zero-dependency validator, reusable workflows + skills, proactive power-ups) so new users understand what they got out of the box.
- **README token / file-count drift fixed**: README now reports the actual FAST_INIT cost (~1,463 tokens / 5,855 chars), 13 Memory Bank files, and 9 workflows, matching the validator output.
- **Offline Memory Consolidation (Dream Phase) Proposal**: Logged a proposal (`docs/proposals/hook-memory-integration.md`) to use IDE lifecycle hooks for passive event logging and offline memory bank updates, reducing active token usage.
- **Graphify Integration**: Added optional workflow (`workflows/build-graph.md`) to build queryable structural knowledge graphs of the codebase, reducing token context bloat.
- **Advanced Agent Steering**: Added `/calibrate`, `/align`, `/devil`, and `/burst` prompts to `docs/prompts.md` based on professional Claude Code workflows.
- **Parallel Agent Forking**: Documented how to run parallel agents on the same project using the Memory Bank (`docs/start-new-project.md`).
- Initial model-agnostic template structure with `AGENTS.md`, Memory Bank, Cline/Antigravity adapters, workflows, skills, docs, MCP placeholder, and template validator.
- Added explicit initialization modes in `AGENTS.md`: `FAST_INIT` (default) and `DEEP_AUDIT` (explicit).
- Added `python scripts/check-template.py --fast` for lightweight startup/integration validation.
- Added `python scripts/init-fast.py` one-command bootstrap helper (fast validation + short prompt output).
- Added `workflows/init-lite.md` for consistent low-token initialization behavior.
- Updated README and docs guides with a simpler beginner flow and clear `--fast`/`init-fast.py` usage.
- Added `docs/template-improvement-brief.md` as a handoff file for future LLM/reviewer template improvement analysis.