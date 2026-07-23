# Active Context

## Current focus

Release `v0.7.0` packages the completed cross-agent Phase 1–3 upgrades under
the MIT license. Native reviewer behavior pilots remain optional and pending;
no compressor, proxy, memory sync, or protocol runtime was activated.

## Phase summary: Phase 3 Advanced Optional Features — 2026-07-23

- Outcome: IMPLEMENTED_AND_CODE_REVIEWED
- Added one canonical read-only reviewer contract with minimal Gemini, Codex,
  and Claude native adapters; validator checks markers, paths, formats, and
  declared restrictions without claiming runtime parity.
- Added a five-scenario, stdlib-only context benchmark with JSON output,
  sanitized paired-usage records, correctness/privacy gates, and self-tests.
- Added provider-memory authority guidance, a dated MCP/Agent Skills/ACP/A2A
  watch, and optional performance experiment recipes.
- Kept all Phase 3 material lazy-loaded and all integrations disabled.
- Verification: compile, benchmark self-test/text/JSON, hook fixtures, fast,
  compatibility, full, startup benchmark, bootstrap, and diff checks pass.
- Current validator: 103 required files, 9 adapters, 15 budgets; FAST_INIT is
  7,196 chars (~1,799 tokens).

## Phase summary: Phase 2 Core Enhancements — 2026-07-23

- Outcome: REVIEWED_AND_CORRECTED
- P2.0: Preflight verified baseline diff (24 files changed); model routing updated for Gemini-first implementation & Codex review; user preferences recorded.
- P2.1: Portable subagent contract (`docs/subagent-contract.md`) and `delegation-coordinator` skill created and mirrored across `.agents/skills`, `.claude/skills`, and `.cline/skills`.
- P2.2: Pre-edit check (`workflows/pre-edit-check.md`), spec-driven development (`workflows/spec-driven-development.md`), and self-evaluation (`workflows/self-evaluate.md`) workflows created and mirrored across `workflows/`, `.agents/workflows/`, and `.clinerules/workflows/`. Reusable risk entry schema added to `memory-bank/risks.md`.
- P2.3: Shared stdlib hook library now uses verified Claude, Gemini, and Codex
  event/denial schemas, explicit client routing, redacted native fixtures, and
  behavior assertions confined to an OS temporary directory.
- P2.4: Inactive native MCP examples created (`.gemini/settings.example.json`, `.codex/config.example.toml`); documentation and validator updated for stdlib JSON and TOML validation.
- P2.5: Validator enforces 92 required files, 9 adapters, 6 skills across 3
  trees, 9 workflows across 3 trees, hook behavior/adapter checks, native MCP
  examples, mirror hashes, and machine-local file-URI hygiene.
- Codex corrections: replaced obsolete Gemini/Codex hook shapes, made the
  fixture harness assert records and denials, restored Python 3.9 syntax,
  removed machine-local links, and aligned cross-agent docs/configs.
- Verification: fast, compatibility, full, benchmark, fixture, Python
  3.9-grammar, negative validator, mirror, bootstrap, and diff checks pass.

## Phase summary: cross-agent compatibility quick wins — 2026-07-23

- Outcome: COMPLETE
- Normalized Gemini/Claude imports and the Codex pointer while preserving root `AGENTS.md` as the sole instruction source.
- Made `.agents/skills` canonical; added five byte-identical `.claude/skills` mirrors and retained `.cline/skills` mirrors.
- Added the compatibility truth table and corrected client-specific MCP guidance for Gemini, Codex, and Claude.
- Validator now enforces exact primary adapters, minimal skill schema, three-tree SHA-256 parity, and the 7,600-character FAST_INIT ceiling; CI covers Python 3.9/current on Windows/Linux.
- Cleaned optional-integration claims and added evidence/confidence labels.
- Verification: fast, full, compatibility, bootstrap, negative fixtures, compile, and diff checks pass; FAST_INIT is 7,381 chars (~1,845 tokens).
- Native smoke status: Codex CLI 0.142.0 and Claude Code 2.1.116 are installed; Gemini CLI is unavailable. No paid model sessions were launched.

## Phase summary: v0.6.0 universal agent features — 2026-06-05

- Outcome: COMPLETE
- Key decisions:
  - Added only verified / tool-agnostic features; deliberately omitted LOW-confidence Claude Code commands (e.g. `/goal`, `/ultracode`) per "do not invent facts".
  - Detail in lazy-loaded `docs/agent-loop.md`; only a tight summary in always-on `AGENTS.md` (budget raised 4,000 → 4,700).
  - Activatable configs (`.claude/`, `.mcp.json`, `.aider.conf.yml`) ship but are NOT validator-required, so users can opt out.
- Files modified: AGENTS.md, model-routing.md, handoff.md, context-hygiene.md, toolbox.md, mcp config + README, check-template.py, README.md, CHANGELOG.md, VERSION, all 10 SKILL.md mirrors, init-fast.py; new: `.windsurfrules`, `CONVENTIONS.md`, `.aider.conf.yml`, `.mcp.json`, `.vscode/mcp.json`, `.claude/settings.json`, `.claude/hooks/log-writes.py`, `docs/agent-loop.md`, `docs/hooks.md`, `memory-bank/reminders.md`, `workflows/critic-review.md`, `workflows/autonomous-agent.md`.
- Also added (infra wave): CI (`.github/workflows/validate.yml`, Linux+Windows), `.github/PULL_REQUEST_TEMPLATE.md` + issue templates, `.editorconfig`, `.claude/commands/` (`/handoff`, `/save-context`, `/start-task`), `docs/per-tool-setup.md`, expanded `.env.example`.
- Validator: 50 required files, 9 adapters, 15 budgets — full pass on Python 3.13.
- Open items: none blocking. Optional future: MCP memory-server as a scaling path for large `memory-bank/`.
- Next: commit when the user is ready (branch off main first).

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

1. Start new product repositories through GitHub **Use this template**.
2. Optionally run the frozen-diff reviewer pilot in installed Gemini, Codex,
   and Claude clients and record behavioral evidence.
