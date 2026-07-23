# Workflow: Spec-Driven Development

Structure non-trivial feature additions and refactors through explicit specification and evidence reports before review.

## Workflow Sequence

```text
specify -> acceptance criteria -> implementation tasks -> implement -> verify -> evidence report -> review
```

## Task Specification Schema

Every work package or implementation task must define:

1. **Objective**: Concise description of the change.
2. **Owned Paths**: Exact list of files/directories to be edited.
3. **Explicit Non-Goals**: Out-of-scope items and forbidden changes.
4. **Acceptance Criteria**: Verifiable conditions required for completion.
5. **Verification Command**: Smallest deterministic check (build, test, lint).
6. **Expected Report Evidence**: Key output, exit codes, and diff metrics.

## Execution Rules

- **Preflight Check**: Run `workflows/pre-edit-check.md` before making edits.
- **Incremental Implementation**: Touch only owned paths; verify after each step.
- **Evidence Collection**: Record actual execution outputs, exit codes, and character/token counts.
- **Self-Evaluation**: Execute `workflows/self-evaluate.md` before submitting work for external review.
