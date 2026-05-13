# Calibration Workflow

Use this workflow to implement continuous self-improvement, reducing repeated corrections across sessions.

## When to use
At the end of a long session or milestone where the user had to correct the agent multiple times on style, preferences, or architecture.

## Procedure

1. **Review Session History:**
   The agent scans the current chat history for repeated corrections (e.g., "don't use Tailwind", "use functional components", "stop summarizing so much").

2. **Extract Rules:**
   Distill these corrections into concrete, actionable rules.

3. **Update Persistent Memory:**
   Depending on the scope of the rule:
   - For agent behavior/style: Update `.clinerules/00-master.md` or `.agents/rules/00-master.md`.
   - For tech stack rules: Update `memory-bank/techContext.md`.
   - For product/UX rules: Update `memory-bank/productContext.md`.

4. **Confirm:**
   Report a short summary of the newly learned rules back to the user.

## Advanced: The Dream Phase
For extremely large projects, this calibration can be run as an offline "Dream Phase." Instead of using the active session's context tokens, developers can configure IDE hooks to passively log agent actions to a local file, and then run an offline script to summarize those logs into the Memory Bank without interrupting active coding.
