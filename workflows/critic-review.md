# Workflow: Critic Review

Run a separate-context critic over an artifact (plan, code change, architecture decision, Memory Bank entry) before accepting it. Works with any model; the key is that the critic does **not** see the generator's reasoning, only the artifact + a rubric. That separation is what prevents a model from rubber-stamping its own work.

## When to use

- Before merging a non-trivial change.
- Before committing a plan for a risky or ambiguous task.
- When a decision is hard to reverse (schema, public API, security-relevant code).

## Steps

1. **Freeze the artifact.** Identify exactly what is being reviewed (a diff, a file, a plan section). Do not include the chain of reasoning that produced it.
2. **Pick the rubric.** Default dimensions: correctness, simplicity, security, matches existing style, meets the stated success criteria. For security-sensitive work, use `SECURITY.md`.
3. **Run the critic in a fresh context.** A subagent, a second session, or a different model. Give it only the artifact + rubric + Task Envelope (`read_only: true` per `docs/subagent-contract.md`).
4. **Require structured output matching the portable result envelope:**
   ```yaml
   task_id: <id>
   status: completed | partial | blocked
   verdict: accept | revise
   findings:
     - severity: high | medium | low
       location: <file:line or section>
       evidence: <observable fact>
       required_fix: <concrete suggested change>
   ```
5. **Act on it.** Address every `high`/`medium` issue, then re-run. Cap at 2 revise cycles; if still failing, escalate to a human or a stronger model (see `model-routing.md`).

## Evidence and opposing cases

For a consequential or contested decision, include a short case stating the
proposal, constraints, known facts and unknowns. Have the critic examine the
strongest honest case for failure and the strongest honest case for proceeding.
Require each material objection to name a failure mechanism, evidence and a
specific check or change that would reverse the finding. Distinguish observed
facts from assumptions; missing evidence is not a fabricated result.

Keep judgments tied to tests and artifacts. Several personas of one model do
not establish independent evidence or a statistical confidence level. A review
verdict never substitutes for application checks. Use the smallest review that
resolves the decision; a full multi-agent jury is an explicit optional exercise,
not a default requirement for code changes or template upgrades.

This approach is informed by [court-skill](https://github.com/alexyc9381/court-skill).
See the [assessment](../docs/court-skill-assessment.md) for scope and tradeoffs.

## Notes

- Cheapest critics run first: linters, type-checkers, and tests catch mechanical issues before the LLM critic spends tokens on judgment calls.
- Self-critique (same model, "now review as a skeptical security reviewer") is a fallback when a separate context isn't available — weaker, but better than nothing.
- Pairs with `.cline/skills/code-reviewer/SKILL.md` for the code-specific rubric.
