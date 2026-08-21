# Workflow: Spec-Driven Development

Structure non-trivial feature additions, migrations, and refactors through explicit, executable specifications and evidence-backed verification.

## Workflow Sequence

```text
specify -> characterization safety net -> task breakdown -> implement with falsifiable predictions -> verify -> evidence report -> review
```

## Task Specification Schema

Every work package or implementation task must define:

1. **Objective**: Precise description of the change and business intent.
2. **Owned Paths**: Exact list of files/directories to be edited (exclusive ownership).
3. **Explicit Non-Goals**: Out-of-scope items, forbidden file edits, and architectural boundaries.
4. **Acceptance Criteria**: Verifiable conditions required for completion (e.g. exit codes, API schemas).
5. **Verification Command**: Smallest deterministic check (`pytest`, `npm test`, `check-template.py`).
6. **Expected Report Evidence**: Observable output, diff metrics, and token/character budgets.

## Execution Rules

- **Characterization Safety Net**: Before refactoring legacy or opaque code, write tests/assertions capturing *current baseline behavior* to immediately catch regressions.
- **Preflight Check**: Run `workflows/pre-edit-check.md` before making edits.
- **Falsifiable Step Execution**: Formulate the expected baseline failure and post-edit passing state before executing each checkpoint.
- **Incremental Implementation**: Touch only owned paths; verify and commit atomically after each checkpoint.
- **Evidence Collection**: Record actual execution outputs, exit codes, and character/token counts.
- **Self-Evaluation**: Execute `workflows/self-evaluate.md` before submitting work for external review.
