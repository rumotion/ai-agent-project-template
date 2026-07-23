# Context Benchmark Pack

This local, deterministic harness measures the static context files assigned to
representative agent tasks and can compare manually exported usage totals. It
does not call a model, open a network connection, or scan the repository.

## Static measurement

```text
python scripts/benchmark-context.py
python scripts/benchmark-context.py --scenario fast-init
python scripts/benchmark-context.py --scenario fast-init --json
```

`scenarios.json` is an explicit manifest. Character counts use decoded text;
estimated tokens use the same `characters // 4` heuristic as
`scripts/check-template.py`. The estimate is only a stable local comparison,
not a tokenizer or billing measurement.

## Paired usage records

Keep unredacted exports outside the repository. If a sanitized local record is
useful, put it under ignored `.agent-benchmarks/`. Records contain totals, not
prompts. Unknown run fields are rejected so the harness cannot echo prompt text
through `--json`:

Run names are limited to 1-64 letters, digits, dots, underscores, or hyphens;
use neutral labels rather than account, project, or machine identifiers.

```json
{
  "schema_version": 1,
  "scenario": "fast-init",
  "runs": [
    {
      "name": "baseline",
      "input_tokens": 2000,
      "output_tokens": 500,
      "thought_tokens": 100,
      "cached_tokens": 800,
      "tool_calls": 4,
      "turns": 3,
      "correctness_score": 5,
      "clarity_score": 5,
      "high_severity_findings": 0,
      "privacy_concern": false
    },
    {
      "name": "candidate",
      "input_tokens": 1700,
      "output_tokens": 400,
      "thought_tokens": 100,
      "cached_tokens": 700,
      "tool_calls": 4,
      "turns": 3,
      "correctness_score": 5,
      "clarity_score": 5,
      "high_severity_findings": 0,
      "privacy_concern": false
    }
  ]
}
```

Compare with:

```text
python scripts/benchmark-context.py --scenario fast-init --usage .agent-benchmarks/fast-init.json --candidate candidate
```

`total_tokens` is input + output + thought tokens. Cached tokens are reported
separately because they are normally a subset of input, not additional tokens.
Tool calls and turns are comparison signals, not token estimates.

The policy verdict is:

- `ADOPT` only at 10% or greater total-token reduction, with no correctness
  regression, no candidate high-severity finding, and no privacy concern;
- `REJECT` when complete paired evidence fails any threshold;
- `INSUFFICIENT_EVIDENCE` when no paired record is supplied.

This is a repository review policy, not a vendor performance claim. A human
still reviews clarity, telemetry, failure behavior, and task-specific risk.

## Harness check

```text
python scripts/benchmark-context.py --self-test
```

The self-test verifies parsing, verdicts, malformed-input diagnostics, and that
the FAST_INIT total agrees with `check-template.py`.
