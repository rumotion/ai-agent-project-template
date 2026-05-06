# System Patterns

## Architecture overview

The template uses a layered AI-agent architecture with `AGENTS.md` as the canonical command layer, thin tool adapters, durable Memory Bank context, reusable workflows/skills, deterministic scripts, documentation, and MCP placeholders.

## Key modules

- `AGENTS.md`: single source of truth for all agents.
- `memory-bank/`: durable project context.
- `.clinerules/` and `.cline/skills/`: Cline-specific adapters and skills.
- `.agents/`: Google Antigravity rules, workflows, and skills.
- `workflows/`: tool-agnostic SOPs.
- `scripts/`: local deterministic automation.
- `docs/`: human-readable documentation.
- `references/`: reference-only source material for people and agents.
- `assets/`: source project assets and content inputs.
- `.mcp/`: external context/tool configuration examples.

## Data flow

Agents read `AGENTS.md`, then `memory-bank/00-index.md`, then relevant Memory Bank/source/docs files. After meaningful work, agents update concise Memory Bank entries and summarize verification.

## Important patterns

- Canonical instruction file plus thin adapters.
- Memory Bank as operational context, not a diary.
- Keep raw references in `references/`; summarize durable facts in `memory-bank/`.
- Keep project source assets in `assets/`; move runtime assets to stack-specific folders such as `public/` or `src/assets/` only after a stack is chosen.
- Prefer GitHub **Use this template** for clean new repositories; direct clone keeps template history/remotes until changed.
- Tool-agnostic workflows mirrored into tool-specific locations when useful.
- Standard-library-only validator for portability.

## Anti-patterns to avoid

- Duplicating conflicting instructions across adapters.
- Committing local `env/` folders, `.env` values, generated files, or dependencies.
- Treating raw PDFs/images as Memory Bank context instead of storing them under `references/` or `assets/`.
- Pulling/merging template files into an existing project without first committing current work and checking overlapping files.
- Adding dependencies or stack assumptions to the base template.

## Integration boundaries

Provider/model routing is documented in `memory-bank/model-routing.md`. MCP configuration examples must not include real tokens.