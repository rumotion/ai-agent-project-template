# Active Context

## Current focus

Multi-model robustness pass complete (2026-05-09). Cross-model continuity, per-model routing, additional adapters (Copilot, Cursor, Codex), MCP parity, validator drift-check, and token benchmark are in place.

## DEEP_AUDIT findings (2026-05-09)

- `python scripts/check-template.py` (full): PASS — 36 required files, 4 adapters, 9 budgets, gitignore + secret hygiene clean.
- All adapters (`GEMINI.md`, `CLAUDE.md`, `.clinerules/00-master.md`, `.agents/rules/00-master.md`) are thin and reference `AGENTS.md`.
- Triplicated workflow trees (`workflows/`, `.clinerules/workflows/`, `.agents/workflows/`) and duplicated skill/rule trees (`.cline/skills/` vs `.agents/skills/`, `.clinerules/` vs `.agents/rules/`) are a maintenance/drift risk per the brief but currently consistent.
- Memory Bank consistent and within budget; `progress.md` has one mildly run-specific phrase ("Push updated template to GitHub") that could be generalized.
- `docs/setup.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `LICENSE` are not enforced by the validator's `REQUIRED_FILES`.

## Brief analysis (`docs/template-improvement-brief.md`)

Strengths: clear mission/non-goals, concrete token-usage measurements, backlog grouped by category, external-review prompt, proposal format, success metrics, maintenance cadence.

Gaps / candidate improvements (not yet applied):

1. No date/version stamp on the brief; hard to detect staleness.
2. Backlog mentions a token-benchmark script and `--json` output for validators but does not yet specify acceptance criteria or apply-now vs monitor.
3. No success metric for autonomous-mode turn count / narration verbosity, although §14 names it the top issue.
4. Triplicated workflow/skill/rule trees not flagged as a maintainable-surface risk.
5. External-review prompt (§10) does not include the brief's own current status, so an external LLM cannot easily judge what is already done.
6. Public-template hygiene checklist does not cover `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md` enforcement.
7. §14 says docs are not the bottleneck, but most of §8 is documentation; the conflict could be resolved by sharpening §8's "apply now / monitor" column.

## Changes applied (2026-05-09)

- Added `memory-bank/handoff.md` and `workflows/handoff.md` for cross-model continuity.
- Updated `AGENTS.md` startup path with handoff pointer; added "Cross-model continuity" section; added `handoff.md` to FAST_INIT update list. Budget bumped to 4,000.
- Rewrote `memory-bank/model-routing.md` with per-model context budgets, cache-stable file list, Antigravity sub-agent notes, and concrete current defaults.
- Added adapters: `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`. Validator enforces them.
- Expanded `.mcp/mcp_config.example.json` with filesystem, fetch, and git server stubs.
- Expanded `.vscode/extensions.json` recommendations.
- Synced mirrored workflows (`.clinerules/workflows/`, `.agents/workflows/`) and skills (`.agents/skills/`) to canonical content; validator now enforces zero drift.
- Validator: new adapters, handoff budget, mirror-drift check, and `--benchmark` flag.
- `scripts/init-fast.py` now prints the token benchmark in the bootstrap output.

## Next step

1. Run `python scripts/init-fast.py` in a fresh clone to confirm token cost.
2. Use `handoff.md` for every model switch.
3. Fill `memory-bank/projectbrief.md` once a real product/stack is chosen.