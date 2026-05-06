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