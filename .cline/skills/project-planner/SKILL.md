---
name: project-planner
description: Creates implementation plans from project requirements. Use when planning features, refactors, architecture changes, or multi-step development tasks.
---

# Project Planner Skill

Follow `AGENTS.md` startup routing; load only Memory Bank files relevant to the
requested plan. Identify the observable success check first. Scale detail to
the task: a short plan for routine work, phases for complex changes.

## Output format

Provide:

1. Goal
2. Current understanding
3. Assumptions
4. Proposed approach
5. Affected files
6. Risks
7. Test plan
8. Memory Bank updates needed

For a planning-only request, deliver the plan. When implementation is already
requested, continue within that authorization; ask only for missing information
or authority needed for a consequential action.

Chains to: `karpathy-engineer` for authorized implementation. See `docs/agent-skill-ecosystem.md`.
