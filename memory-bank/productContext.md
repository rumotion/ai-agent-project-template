# Product Context

## Problem this project solves

Provides a reusable, low-context repository template for AI-agent-assisted software development across multiple tools/providers.

## Target users

- Developers and technical teams bootstrapping new projects with agent workflows.
- Agent maintainers who need one canonical instruction source (`AGENTS.md`) with tool-specific adapters.

## Main user workflows

1. Copy/use template from GitHub.
2. Run `python scripts/check-template.py` to validate template integrity.
3. Initialize Memory Bank with project-specific facts.
4. Plan and implement features using lazy-loaded docs/workflows/skills.

## UX expectations

- Minimal startup context for agents (`AGENTS.md` + `memory-bank/startup.md`).
- Clear documentation for setup, GitHub usage, safety, and file organization.
- Predictable, deterministic validation via local script.

## Business/domain rules

- Keep `AGENTS.md` canonical; adapters should reference it.
- Do not commit secrets or local credentials.
- Keep Memory Bank concise and operational; unknowns must remain `TBD`.

## Open product questions

- What end-product (app/site/service) will be built in this copied repository?
- Which stack and deployment target should be adopted?
- Are there domain-specific compliance, security, or performance constraints beyond template defaults?