# Workflow: Init Lite (FAST_INIT)

Use this workflow to initialize a copied project with low context/token usage.

1. Read `AGENTS.md` and `memory-bank/startup.md`.
2. Read `memory-bank/00-index.md` only for routing.
3. Read only FAST_INIT-allowed files (for example `README.md` and stack-detection configs).
4. Do not read `docs/`, `workflows/`, skills folders, `references/`, `assets/`, `.mcp/`, or validator scripts unless needed to resolve a critical unknown.
5. Update only `memory-bank/startup.md`, `memory-bank/projectbrief.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`, and `memory-bank/techContext.md`.
6. Keep unknown facts as `TBD`.
7. If required facts are missing, ask focused questions before escalating.
8. Escalate to `DEEP_AUDIT` only when the user requests it or FAST_INIT cannot verify required facts.
9. Keep execution terse: minimal tool turns, minimal narration, and a short final summary.
