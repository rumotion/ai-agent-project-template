# Workflow: Self-Evaluate

A mandatory, evidence-grounded self-evaluation loop executed after implementing a work package or phase.

## Sequence

```text
freeze criteria -> deterministic checks -> negative checks -> focused diff -> isolated read-only critic -> bounded repair -> re-run checks -> evidence ledger
```

## Core Principles

1. **Deterministic Evidence Outranks Model Judgment**: Passing unit tests, schema parsers, SHA-256 mirror checks, and linter exit codes outrank subjective LLM critique.
2. **Artifact-Only Critic Context**: Reviewers evaluate frozen diffs, criteria, and test outputs without generator chain-of-thought.
3. **Structured Finding Schema**:
   ```yaml
   verdict: accept | revise
   findings:
     - severity: high | medium | low
       location: path:line
       evidence: observable fact
       required_fix: concrete change
   ```
4. **Bounded Repair Loop**:
   - Repair all evidence-backed `high` and `medium` findings.
   - Re-run all deterministic verification checks after repairs.
   - Maximum **2 repair cycles** per work package.
   - If material findings persist after 2 cycles, halt, preserve last verified state, and mark package `PARTIAL` or `BLOCKED`.
5. **No Scope Expansion**: Do not expand feature scope merely to satisfy subjective critic feedback.
6. **Phase-Wide Regression Review**: Re-verify all phase gates, protected startup files, user-owned files, and FAST_INIT context budgets.

## Self-Evaluation Ledger Schema

Record evaluation results in the implementation report using this structure:

| Package | Frozen criteria | Deterministic evidence | Critic isolation | Findings | Repairs | Re-verification | Residual risk |
|---|---|---|---|---|---|---|---|
