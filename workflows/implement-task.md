# Workflow: Implement Task

1. Confirm the goal and approved plan if one exists.
2. Read relevant Memory Bank files (including any `Refuted Hypotheses`).
3. For each task step/checkpoint in the plan:
   a. Formulate a falsifiable expectation: state what currently fails and what observable output will prove success.
   b. Apply bimodal execution: single narrow probes during exploration/discovery; batched parallel edits for verified mechanics.
   c. Make focused, surgical changes for that step.
   d. Verify cheapest-first (lint, types, unit tests); add a critic pass (`critic-review.md`) for risky steps.
   e. Perform an atomic git commit (`git commit -m "<type>(<scope>): <step description>"`).
4. Summarize files changed across all completed steps.
5. Reflect on phase/milestone completion: write a phase summary (`docs/agent-loop.md` section 7) and update `handoff.md`.
6. Update Memory Bank if project knowledge changed.
7. Push commits to remote repository upon phase/milestone completion (`git push`).
8. Recommend next tests or review steps.
