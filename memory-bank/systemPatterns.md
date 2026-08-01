# System Patterns

## Architecture overview

The template uses a layered AI-agent architecture with `AGENTS.md` as the canonical command layer, thin tool adapters, durable Memory Bank context, reusable workflows/skills, deterministic scripts, documentation, and MCP placeholders.

## Key modules

- `AGENTS.md`: single source of truth for all agents.
- `memory-bank/`: durable project context.
- `.agents/skills/`: canonical portable Agent Skills source used directly by Gemini and Codex.
- `.claude/skills/` and `.cline/skills/`: byte-identical discovery mirrors.
- `.clinerules/` and `.agents/rules/`: thin client-specific rule adapters.
- `workflows/`: tool-agnostic SOPs.
- `scripts/`: local deterministic automation.
- `docs/`: human-readable documentation.
- `references/`: reference-only source material for people and agents.
- `assets/`: source project assets and content inputs.
- `.mcp/`: external context/tool configuration examples.

## Data flow

Agents read `AGENTS.md`, then `memory-bank/00-index.md`, then relevant Memory Bank/source/docs files. After meaningful work, agents update concise Memory Bank entries and summarize verification.

Initialization now follows a two-mode flow: start in `FAST_INIT` for low-token, high-signal setup and escalate to `DEEP_AUDIT` only when required facts are unavailable or the user requests full inspection.

## Important patterns

- Canonical instruction file plus thin adapters.
- Canonical `.agents/skills` plus SHA-256-checked client discovery mirrors.
- Dual initialization modes (`FAST_INIT` default, `DEEP_AUDIT` explicit) to balance token cost and robustness.
- Memory Bank as operational context, not a diary.
- Keep raw references in `references/`; summarize durable facts in `memory-bank/`.
- Keep project source assets in `assets/`; move runtime assets to stack-specific folders such as `public/` or `src/assets/` only after a stack is chosen.
- Atomic Step-Commit Agentic Cycle: Plan → Execute → Verify → Commit → Reflect. Every task step checkpoint in a plan is verified and committed atomically with Conventional Commit syntax.
- Prefer GitHub **Use this template** for clean new repositories; direct clone keeps template history/remotes until changed.
- Tool-agnostic workflows mirrored into tool-specific locations when useful.
- Standard-library-only validator for portability.
- One canonical specialist-role contract with thin native adapters; runtime
  parity requires a manual pilot.
- Manifest-based context experiments that never scan the repository or call a
  model/network service.

## Anti-patterns to avoid

- Duplicating conflicting instructions across adapters.
- Committing local `env/` folders, `.env` values, generated files, or dependencies.
- Treating raw PDFs/images as Memory Bank context instead of storing them under `references/` or `assets/`.
- Pulling/merging template files into an existing project without first committing current work and checking overlapping files.
- Adding dependencies or stack assumptions to the base template.

## Integration boundaries

Provider/model routing is documented in `memory-bank/model-routing.md`. MCP configuration examples must not include real tokens.
