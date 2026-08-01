# Workflow: Implement Task

1. Confirm the goal and approved plan if one exists.
2. Read relevant Memory Bank files.
3. For each task step/checkpoint in the plan:
   a. Make focused, surgical changes for that step.
   b. Run targeted checks (lint, types, tests).
   c. Perform an atomic git commit (`git commit -m "<type>(<scope>): <step description>"`).
4. Summarize files changed across all completed steps.
5. Update Memory Bank if project knowledge changed.
6. Push commits to remote repository upon phase/milestone completion (`git push`).
7. Recommend next tests or review steps.