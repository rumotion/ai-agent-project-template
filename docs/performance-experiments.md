# Optional Context Performance Experiments

No compressor, proxy, or compact-output policy is adopted by this template.
Use `scripts/benchmark-context.py` to gather paired evidence before proposing
one. Keep sanitized totals in ignored `.agent-benchmarks/`, not tracked prompts.

## Required experiment record

Every experiment must record:

- hypothesis and technique under test;
- exact baseline and candidate scenario IDs;
- product/project version and first-party or upstream source;
- telemetry, retention, privacy, and repository-data review;
- failure modes, stop conditions, and rollback;
- actual input, output, thought, cached-token, tool-call, and turn counts;
- human correctness and clarity scores;
- high-severity review findings;
- decision: `ADOPT`, `REJECT`, or `INSUFFICIENT_EVIDENCE`.

The benchmark policy permits `ADOPT` only when a paired candidate uses at least
10% fewer total tokens, has no correctness regression, no high-severity
finding, and no material privacy concern. This threshold is a local review
policy, not a vendor claim.

## Recipe: compact-output prompting

- **Hypothesis:** a task-local request for concise tool output reduces total
  session tokens without omitting evidence.
- **Baseline/candidate:** run all five context scenarios with identical
  artifacts and verification; candidate adds only the compact-output request.
- **Version/source:** record the exact client, model, date, and prompt text in
  an untracked experiment note.
- **Privacy:** no new service should receive repository content.
- **Failure/rollback:** stop if paths, test failures, qualifications, or
  handoff facts disappear; remove the candidate prompt.
- **Evidence:** import only sanitized totals and human scores.
- **Current decision:** `INSUFFICIENT_EVIDENCE`.

## Recipe: Caveman-style response compression

- **Hypothesis:** an upstream response-style instruction reduces output enough
  to lower total tokens on routine edits while preserving correctness.
- **Baseline/candidate:** prioritize routine-code-edit and code-review, then
  repeat on handoff and research synthesis to detect lost nuance.
- **Version/source:** pin the reviewed commit from the
  [Caveman upstream](https://github.com/JuliusBrussee/caveman); do not install
  or copy instructions during the design pass.
- **Privacy:** review the files and tool permissions; reject any external
  transmission not separately approved.
- **Failure/rollback:** remove the temporary instruction and discard the
  candidate session if it hides evidence or increases repair turns.
- **Evidence:** total session tokens matter; output-only savings are
  insufficient.
- **Current decision:** `INSUFFICIENT_EVIDENCE`.

## Recipe: Headroom or comparable context proxy

- **Hypothesis:** a context proxy lowers total session tokens enough to justify
  another runtime and trust boundary.
- **Baseline/candidate:** run all scenarios with identical inputs, model,
  permissions, and tests; record proxy latency and failures in addition to
  usage totals.
- **Version/source:** pin and review the
  [Headroom upstream](https://github.com/headroomlabs-ai/headroom) or the exact
  comparable proxy version.
- **Privacy:** document what content leaves the machine, subprocess/network
  behavior, telemetry, retention, and credential access before any trial.
- **Failure/rollback:** use a disposable project; bypass/uninstall the proxy and
  verify direct client operation before considering the trial complete.
- **Evidence:** count added summarization/proxy tokens and repair turns; do not
  move cost out of the reported total.
- **Current decision:** `INSUFFICIENT_EVIDENCE`.

## Non-adoption rule

Do not install a compressor or proxy, route repository content through a new
service, or add an always-on compact-output skill without positive paired
evidence and separate user approval.
