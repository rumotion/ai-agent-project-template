# Optional product intake and environment acceptance

Use for ambiguous or substantial application work. Infer answers already present
in the request, project records and approved references; continue independent
authorized work while resolving only material unknowns. Routine clear fixes do
not need a product interview or a new approval checkpoint.

## Short intake

Capture the user outcome, non-goals, constraints and approved examples. When a
choice changes the product materially, present two or three concrete options
with the behavior/tradeoff for the user. A visual example, draft or benchmark
is not an approved requirement by itself. Link the resulting reviewed decision
and source ID through `feedback-closure.md`; preserve the rejected alternatives
and the premise under which they could be reconsidered.

## Acceptance matrix

Include only routes the application actually has. Unknown stack, environment,
domain constraints and commands remain `TBD`; they cannot establish a pass.

| Requirement/task | Trigger and user outcome | Environment | Check and expected result | Actual evidence / owner |
|---|---|---|---|---|
| Relevant UI route, if present | Approved reference + key interaction; loading/empty/error state | Named browser/device/viewport and build | Reference fidelity, keyboard/focus/accessibility and behavior | TBD |
| Relevant API route, if present | Valid request and relevant invalid/auth/error case | Named local/test/staging service and dependency versions | Status/schema/side effect, retry/timeout behavior where applicable | TBD |
| Relevant MCP/tool route, if present | Authorized invocation and denied/invalid case | Exact client/server version, transport and permissions | Input/output contract, side effects and actual failure evidence | TBD |

Replace generic rows with concrete triggers/results before work is accepted.
Use approved visual standards only for UI projects; store references/assets
where the project expects them and check fidelity rather than inventing a new
layout. Do not impose UI ceremonies on CLI/library changes.

For each package distinguish deterministic technical evidence, observed product
behavior and any pending user observation. Record the exact artifact/build,
environment and evidence timestamp. A unit test or critic opinion cannot stand
in for a missing deployment, real integration, visual observation or user outcome.
Use the smallest relevant checks; do not add redundant tests for simple prose.

## Rollout and rollback

Record target environment, existing authorized scope, prerequisites, observable
health checks, rollback trigger and the tested recovery/revert path. Local
implementation acceptance does not authorize production changes. Keep pending
deployment/user observation explicit; request any genuinely missing authority
only after the concrete result is ready for review. Never put credentials or
production configuration values in the acceptance record.
