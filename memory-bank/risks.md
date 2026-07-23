# Risks

## High-risk areas

- Tool-specific rules drifting away from `AGENTS.md`.
- Adding project-specific stack assumptions to the base template.

## Security-sensitive areas

- `.env` and provider API keys.
- MCP server configurations that may expose external systems.
- OAuth credentials and local tokens.
- Public repository copies should not include real secrets, local credential files, or unintended `.git/` history/remotes.

## Performance-sensitive areas

TBD per copied project.

## Migration risks

When copying into an existing project, avoid overwriting existing project-specific instructions without review.

## External dependencies

None required for the base template. MCP examples may require external packages or credentials only if enabled by the user.

## Risk Entry Schema

When logging new failure lessons or risks after a failed attempt or incident, use this format:

| Date | Area | Failed approach or risk | Evidence | Safer next attempt |
|---|---|---|---|---|
| 2026-07-23 | Hook fixtures | Exit-code-only tests can pass while payload schemas, log destinations, and denial semantics are wrong. | Gemini's first Phase 2 harness ignored its temp directory and never inspected JSONL records. | Assert exact normalized records and native denial JSON in an OS temp directory; validate adapter structure separately. |
| 2026-07-23 | Native reviewers | A valid adapter and declared read-only tools do not prove a model respects scope or produces equivalent findings. | CI can parse files but does not launch provider clients. | Use one frozen-diff pilot per installed client; compare the tree before/after and validate the portable result contract. |
| 2026-07-23 | Context optimization | Output-only savings can hide added input/thought/repair cost or correctness loss. | No paired usage records exist for the optional techniques. | Keep verdict `INSUFFICIENT_EVIDENCE`; count total session tokens and require correctness/privacy gates before adoption. |
