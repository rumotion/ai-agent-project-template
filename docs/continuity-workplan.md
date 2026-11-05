# Continuity implementation work packages

Authorized 2026-11-05: implement the audit plan in verified local phases and
extend its evidence beyond the supplied social-media article.

Plan: [audit implementation plan](audits/context-continuity-2026-11/implementation-plan.md).
Research: [primary-source evidence](agentic-engineering-evidence.md).

## Execution state

| Phase | State | Acceptance gate |
|---|---|---|
| Research extension | Complete | Nine primary sources with limitations and explicit implementation implications |
| 1: contract and CI | Complete locally | Full gate passed; one full invocation retains compatibility and self-test coverage |
| 2: restoration integrity | In progress | Invalid resume cannot look healthy; visible diagnostics and a manual fallback |
| 3: decision projection | Pending | Atomic record receipt, task selection, 1,000-record archive checks |
| 4: durable task state | Pending | Open work survives restart; stale evidence/results cannot imply acceptance |
| 5: cost awareness | Pending | Optional measurements remain distinct; pacing remains OFF by default |
| 6: recovery pilot | Pending | Offline scenarios plus named native evidence; no fabricated live passes |
| 7: feedback closure | Pending | Feedback/task/decision/evidence links and explicit environment acceptance |
| 8: concurrent runtime | Conditional | Measured need plus lease/cancellation tests before parallel expansion |

## Phase 1 specification

Objective: remove contradictory continuity advice and duplicated CI work.
Owned paths: the CI validation workflow, context compiler/hygiene/bridge/hook
documentation, testing documentation, historical decision correction, this
execution record and concise operational memory.
Non-goals: no client configuration activation, production change, provider
quota run or change to validation behavior.
Baseline: CI invoked the full validator twice and its benchmark self-test again;
docs asserted universal cache TTL and memory durability properties.
Expected: one full invocation retains compatibility, fixtures, pacing, upgrade,
context and hardening checks; guidance distinguishes documented/rendered/live
evidence and local persistence from authorized transport.
Verification: inspect check selection, assert the CI schedule and run the full
validator once. Review diff and commit the phase locally.

## Phase 2 specification

Objective: validate resume state and expose startup failure instead of silently
injecting incomplete context. Preserve explicitly labeled legacy/fresh paths.
Owned paths: compiler, new continuity CLI/schema/tests, lifecycle hook, context
tests, hook fixtures, relevant docs and generator/upgrade manifests.
Non-goals: no full dispatcher, global-config edits, network/model calls or
implicit state migration.
Baseline: missing/prose handoff, unsupported multiline blockers and stale branch
metadata can pass; unexpected lifecycle exceptions can produce no diagnostic.
Expected: bounded strict parsing; ready/degraded/blocked doctor with provenance;
legacy state is usable but never certified as a strict resume receipt; native
delivery remains unknown unless independently observed.
Verification: temporary malformed/fresh/resume/mismatch fixtures, redacted hook
failure tests, compiler regression checks and preservation-upgrade checks.

Each later phase receives its frozen implementation specification before edits.
Verified work is committed locally; no push or release is authorized.
