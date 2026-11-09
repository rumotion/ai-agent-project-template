# Workflow: Critic Review

Run a separate-context critic ("Goldfish") over a frozen artifact (plan, spec, code change, architecture decision, or Memory Bank handoff) produced by the primary context-rich session ("Elephant") before accepting it. Works across Gemini, Claude, Codex, and other clients; the key is that the critic does **not** see the generator's conversational history, only the frozen artifact + a rubric. That separation prevents confirmation bias and self-validation.

## When to use

- Before merging a non-trivial change.
- Before committing a plan or specification for a risky or ambiguous task.
- Before switching models or handing off complex multi-phase work.
- When a decision is hard to reverse (schema, public API, security-relevant code).

## Review lenses (Goldfish stages)

Select the smallest lens set that fits the artifact (or run all four for major specs):

1. **Zoom-Out (`zoom-out`)**: Check simplicity, YAGNI, and altitude. Perform a mandatory read-only codebase search (`grep`/`rg`) to verify whether proposed helpers, modules, or abstractions duplicate existing repository utilities. Flag premature implementation details ("weeds").
2. **Comprehension (`comprehension`)**: Paraphrase first as a naive project reader with zero chat history. Write 2-4 sentences stating *what the artifact proposes* and *how the existing system works per the artifact*. Any section that cannot be paraphrased without guessing unstated chat context is a `high` blocker.
3. **Design & Contradiction Critic (`critic`)**: Verify that viable alternatives were evaluated with concrete trade-offs, failure modes and scale/quota risks are mitigated, and no false architectural compromise was accepted without declaring secondary operational liabilities.
4. **Implementation Readiness (`readiness`)**: Enforce the **Zero-Decision Rule** — a fresh engineer or agent session must be able to execute the plan on the first attempt without making independent choices about schemas, API routes, dependencies, or edge cases. Confirm explicit `owned_paths` and deterministic verification commands.

## Steps

1. **Freeze the artifact.** Identify exactly what is being reviewed (a diff, a file, a plan section). Write long drafts to workspace files rather than dumping them into chat; never pass the generator's reasoning chain.
2. **Pick the rubric and lenses.** Default dimensions: comprehension paraphrase, zoom-out reuse/YAGNI, correctness, security (`SECURITY.md` when relevant), and implementation readiness.
3. **Run the critic in a fresh context.** Use a read-only subagent (`reviewer` adapter in `.gemini/agents/reviewer.md`, `.claude/agents/reviewer.md`, or `.codex/agents/reviewer.toml`), a second session, or a different model. Give it only the artifact + rubric + Task Envelope (`read_only: true` per `docs/subagent-contract.md`).
4. **Require structured output matching `docs/reviewer-role.md` and the portable result envelope:**
   ```yaml
   task_id: <id>
   status: completed | partial | blocked
   paraphrase:
     proposes: <2-3 sentences>
     current_system: <2-3 sentences>
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

This approach is informed by [court-skill](https://github.com/alexyc9381/court-skill)
and [google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model).
See the [assessment](../docs/court-skill-assessment.md) for scope and tradeoffs.

## Notes

- Cheapest critics run first: linters, type-checkers, and tests catch mechanical issues before the LLM critic spends tokens on judgment calls.
- Self-critique (same model, "now review as a skeptical security reviewer") is a fallback when a separate context isn't available — weaker, but better than nothing.
- Pairs with `.cline/skills/code-reviewer/SKILL.md` for the code-specific rubric.
