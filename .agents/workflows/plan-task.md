# Workflow: Plan Task

Use this workflow when planning a feature, fix, refactor, or automation.

1. Read `AGENTS.md`.
2. Read `memory-bank/00-index.md`.
3. Read relevant Memory Bank files.
4. Inspect relevant source files.
5. Identify a verification command or observable acceptance check that proves the requested behavior. Record baseline and expected outcome. Do not weaken checks just to obtain a pass.
6. Scale the plan: one to three steps for routine changes; discrete, verifiable and committable phases for complex work. Include assumptions, exact affected files (`owned_paths`), material risks, rollback where relevant and Memory Bank updates.
   Apply the **Zero-Decision Rule** for multi-step plans: resolve architectural choices, schemas, and edge cases in the plan so a fresh session can execute it without guessing, and verify via codebase search (`grep`) that new helpers do not duplicate existing utilities.
   For ambiguous product work, use the optional intake in `docs/product-acceptance.md`.
   For feedback-driven work, trace the source/decision/task with `docs/feedback-closure.md`;
   check unresolved/rejected actions before proposing repeats. Keep examples qualified.
7. Continue implementation when already authorized. Ask only for missing information or new authority needed for a high-risk or materially ambiguous action.
