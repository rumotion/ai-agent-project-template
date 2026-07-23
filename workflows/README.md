# Workflows

This directory contains model-readable standard operating procedures that are not tied to one tool.

Tool-specific copies/adapters exist in `.clinerules/workflows/` and `.agents/workflows/` for Cline and Google Antigravity compatibility.

If a workflow changes, keep all copies consistent unless a tool-specific difference is intentional.

## Available workflows

- `plan-task.md`, `implement-task.md`, `debug-issue.md`, `refactor-safely.md` — the core build loop (mirrored for Cline/Antigravity).
- `update-memory-bank.md`, `handoff.md` — Memory Bank and cross-model continuity (mirrored).
- `pre-edit-check.md`, `spec-driven-development.md`, `self-evaluate.md` — pre-flight verification, spec-driven execution, and evidence-grounded self-evaluation (mirrored).
- `critic-review.md` — separate-context review of an artifact before accepting it.
- `autonomous-agent.md` — guardrails and loop for longer hands-off runs.
- `calibrate.md`, `build-graph.md`, `init-lite.md` — optional power-ups (calibration, Graphify, lightweight init).