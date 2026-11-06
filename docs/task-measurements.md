# Ordinary task measurements

`python scripts/task_metrics.py --file PRIVATE_SANITIZED_JSON` reports useful
progress/cost checkpoints without creating or activating a quota pacing plan.
It reads one explicit file (64 KiB maximum), never discovers transcripts,
credentials or telemetry and performs no network/model calls. Keep measurements
outside Git. This is advisory arithmetic over coordinator declarations; use
native provider limits for actual spending enforcement.

## Input contract

```json
{
  "task_id": "feature",
  "observed_at": "2026-11-06T12:00:00Z",
  "completed": false,
  "elapsed_seconds": 120,
  "actors": {"lead": "main"},
  "snapshots": [{
    "actor": "lead", "role": "main", "segment": "segment-one",
    "scope": "task", "source": "manual",
    "started_at": "2026-11-06T11:58:00Z",
    "observed_at": "2026-11-06T12:00:00Z",
    "model": null, "effort": null,
    "counters": {"tool_calls": 2, "restore_reads": 1, "review_rounds": 0, "test_runs": 1},
    "tokens": {"input_tokens": null, "output_tokens": null,
               "thought_tokens": null, "cached_tokens": null,
               "thought_in_output": true}
  }],
  "limits": {"tool_calls": 30},
  "remaining": {"tool_calls": 5},
  "no_progress_calls": 0, "repeated_hypotheses": 0
}
```

Replace timestamps with actual observations; never refresh an old reading's time.
Only these fields are accepted. IDs/model/effort are bounded neutral labels;
unknown model/effort is `null`. Declare every participating actor (maximum 32,
exactly one `main`), including workers without telemetry. Missing actors make
aggregate resource counts unknown, rather than silently excluding their costs.
At most 64 snapshots are accepted. Counter fields, `tokens`, elapsed time,
limits/remaining estimates and progress counters are optional; absence means
unknown except progress counters, whose omitted default is zero.

## Counting rules

Counters/tokens are cumulative **within one disjoint actor segment of this task**.
Repeated snapshots replace earlier readings; they are never added. Null/omitted
readings remain unknown but cannot erase an earlier known cumulative high-water
value for reset validation. A reset,
model/effort/source change or different measurement scope requires a new segment
with a non-overlapping start time. Do not copy whole-session cumulative counters
into a new segment. Normalize a task-start delta only when scope and reset
boundaries are known. Closed segments cannot reopen; set `closed: true` only
after final reconciliation. Their final counts remain usable after ten minutes.
Open snapshots and the progress report become stale after ten minutes.

Use `source: native|manual|synthetic` and `scope: task|session|account`. Every
result preserves these labels, timestamps and model gaps. Session/account values
are excluded from task totals; shared-account quota deltas and session API cost
snapshots cannot identify one task when concurrent sessions exist. The existing
pacing tool retains latest cost snapshots, never sums them into task cost.

`input_tokens` must include all cached input tokens. `cached_tokens` is a subset.
Set `thought_in_output: true` when output already includes reasoning; otherwise
output explicitly excludes it and thought is required for a known total. Never
add reasoning/cache subsets twice or turn a missing field into zero. Main and
worker totals are separate and aggregate each actor segment exactly once.
Exclude child totals already rolled into a parent's native counter before
declaring disjoint actor measurements; uncertain overlap means unknown usage.
`elapsed_seconds` is parent-measured task wall time, not the sum of overlapping
actor durations. No prices or subscription-quota conversion are inferred.

## Advice and limits

- `hold`: hard limit reached, exceeded/projected to be exceeded, missing data
  for a hard limit, missing completion-package estimate, or stale progress.
- `complete`: coordinator declares verified completion and no declared hard
  budget is violated. Stop early; no quota-filling work is suggested.
- `checkpoint`: five calls without progress, two repeats of a disproven
  hypothesis or context pressure. Save each open task's next action and review.
- `continue`: no preceding gate applies; existing task authorization still governs.

Hard `limits` and whole-package `remaining` estimates accept elapsed seconds,
tool calls and total tokens. Include review/integration/recovery in the estimates.
Unknown evidence holds limited work; this helper cannot enforce a provider cap
or reserve usage for other processes. Optional `context` uses the pacing tool's
`used_tokens`/`window_tokens` normalizer. `context_checkpoint_ratio` defaults to
0.75 (configurable 0.1–1): a repository policy, not a universal reliability fact.
Do not change a user's selected model/effort to satisfy a metric.
