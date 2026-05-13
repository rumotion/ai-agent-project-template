# Changelog

All notable changes to this template are documented here. This project follows
[Semantic Versioning](https://semver.org/) — `MAJOR.MINOR.PATCH`. The version
in [`VERSION`](VERSION) always matches the latest released git tag.

- **MAJOR** — breaking changes to the canonical `AGENTS.md` contract, the
  Memory Bank file layout, or the validator's public flags.
- **MINOR** — new opt-in features, new workflows/skills, new docs.
- **PATCH** — bug fixes, doc clarifications, validator polish.

For the release process, see [`docs/releasing.md`](docs/releasing.md).

## Unreleased

_Nothing yet._

## v0.3.0 — 2026-05-13 — Polished landing page + release workflow

Public-facing pass: the GitHub repo page now reads as a real product landing
page, and there is a clear, repeatable process for cutting future releases.

### Added

- **README rewritten as a landing page**: hero tagline, badges (Use this
  template, latest release, validator, FAST_INIT cost, license), a top-level
  table of contents, a three-step Quick Start, and a dedicated "Releases &
  changelog" section pointing visitors at the right docs.
- **`VERSION` file** at the repo root, single source of truth for the current
  release. Always matches the latest tag.
- **[`docs/releasing.md`](docs/releasing.md)**: step-by-step guide for cutting
  a new tagged release of the template — what to bump, what to write in the
  changelog, how to tag, how to push, how to publish the GitHub release. So
  you (and any future maintainer) never have to figure the workflow out from
  scratch.

### Changed

- CHANGELOG restructured into proper SemVer-style sections with Added /
  Changed / Fixed sub-headings. The previous flat list is now split between
  `v0.2.0` and `v0.3.0`.

## v0.2.0 — 2026-05-13 — Toolbox, identity cleanup, Windows-safe bootstrap

First substantial public release. Three coordinated changes prepared the
template for use as a real GitHub Template by others.

### Added

- **Toolbox of opt-in power-ups** (kept out of the FAST_INIT path):
  - [`workflows/build-graph.md`](workflows/build-graph.md) — Graphify
    integration for building a structural knowledge graph of large
    codebases, so agents stop burning tokens grepping.
  - [`workflows/calibrate.md`](workflows/calibrate.md) — continuous
    self-improvement workflow that distills repeated corrections into
    persistent rules.
  - [`docs/toolbox.md`](docs/toolbox.md) — single catalog of every opt-in
    power-up.
  - [`docs/prompts.md`](docs/prompts.md) — new `/calibrate`, `/align`,
    `/devil`, `/burst` steering prompts.
  - [`docs/proposals/graphify-integration.md`](docs/proposals/graphify-integration.md)
    and [`docs/proposals/hook-memory-integration.md`](docs/proposals/hook-memory-integration.md)
    — architecture notes including the Dream Phase (offline, hook-driven
    memory consolidation).
  - Parallel agent forking section in
    [`docs/start-new-project.md`](docs/start-new-project.md).
- **Proactive Tool Suggestion rule** in `AGENTS.md` so agents surface
  Graphify or Calibration when the project warrants it.

### Changed

- **Identity cleanup**: `memory-bank/projectbrief.md`, `startup.md`,
  `techContext.md`, and `activeContext.md` no longer frame the repo as a
  "newProject (copied from template)"; they describe the template itself.
  Stack TBDs replaced with concrete "None / Pure template" values so a fresh
  clone shows accurate baseline facts.
- **Welcome banner** in [`scripts/init-fast.py`](scripts/init-fast.py)
  rewritten to enumerate what users get out of the box (canonical
  `AGENTS.md`, shared Memory Bank, FAST_INIT cost, drift-proof mirrors,
  zero-dependency validator, reusable workflows + skills, proactive
  power-ups).
- **README counts reconciled** with validator output: ~1,500 token
  FAST_INIT, 13 Memory Bank files, 9 workflows. Added a
  `--benchmark` note to prevent future drift.

### Fixed

- **Windows bootstrap crash**: `scripts/init-fast.py` configures UTF-8 stdout
  and uses an ASCII-only fallback banner, so the bootstrap no longer crashes
  on Windows consoles with cp1251 / cp1252 default codepages
  (`UnicodeEncodeError` on the rocket emoji).

## v0.1.0 — Initial template foundation

The foundation that made everything above possible.

### Added

- Model-agnostic template structure with canonical `AGENTS.md`, Memory Bank,
  Cline/Antigravity adapters, workflows, skills, docs, MCP placeholder, and
  template validator.
- Explicit initialization modes in `AGENTS.md`: `FAST_INIT` (default) and
  `DEEP_AUDIT` (explicit).
- `python scripts/check-template.py --fast` for lightweight
  startup/integration validation.
- `python scripts/init-fast.py` one-command bootstrap helper (fast
  validation + short prompt output).
- `workflows/init-lite.md` for consistent low-token initialization behavior.
- `docs/template-improvement-brief.md` as a handoff file for future
  LLM/reviewer template-improvement analysis.
- Multi-model robustness pass: cross-model handoff layer, per-model routing
  / budgets / cache list, Copilot / Cursor / Codex adapters, MCP parity,
  validator drift-check, and token benchmark.
