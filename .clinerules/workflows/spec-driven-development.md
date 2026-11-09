# Workflow: Spec-Driven Development

Structure non-trivial feature additions, migrations, and refactors through explicit, executable specifications and evidence-backed verification.

## Workflow Sequence

```text
specify -> characterization safety net -> task breakdown -> implement with falsifiable predictions -> verify -> evidence report -> review
```

## Task Specification Schema

Every work package or implementation task must define:

1. **Objective**: Precise description of the change and business intent.
2. **Owned Paths**: Exact list of repository-relative files/directories to be created or edited (exclusive ownership; no opportunistic adjacent edits).
3. **Explicit Non-Goals**: Out-of-scope items, forbidden file edits, and architectural boundaries.
4. **Alternatives & Trade-offs**: For non-trivial features, document at least one rejected alternative and the concrete technical reason it was rejected.
5. **Zero-Decision Implementation Plan**: Precise API signatures, data/schema contracts, error handling, and edge-case behaviors. The spec fails if the implementer must guess parameter defaults or make independent architectural choices during coding.
6. **Open Questions (Persistent)**: Unresolved technical unknowns kept in the spec across sessions so future sessions do not re-ask answered questions; remove items as they are resolved.
7. **Acceptance Criteria**: Verifiable conditions required for completion (e.g. exit codes, API schemas).
8. **Verification Command**: Smallest deterministic check (`pytest`, `npm test`, `check-template.py`).
9. **Expected Report Evidence**: Observable output, diff metrics, and token/character budgets.

For applicable application routes, add the environment/trigger/expected-outcome
matrix in `docs/product-acceptance.md`. Feedback packages link the reviewed
record as a concrete task input; see `docs/feedback-closure.md`. Technical checks
and observed user outcomes have separate evidence. Deployment authority is scoped
independently of implementation acceptance; reuse existing authorization.

## Execution Rules

- **Characterization Safety Net**: Before refactoring legacy or opaque code, write tests/assertions capturing *current baseline behavior* to immediately catch regressions.
- **Preflight Check**: Run `workflows/pre-edit-check.md` before making edits.
- **Falsifiable Step Execution**: Formulate the expected baseline failure and post-edit passing state before executing each checkpoint.
- **Incremental Implementation**: Touch only owned paths; verify and commit atomically after each checkpoint.
- **Evidence Collection**: Record actual execution outputs, exit codes, and character/token counts.
- **Self-Evaluation**: Execute `workflows/self-evaluate.md` before submitting work for external review.
