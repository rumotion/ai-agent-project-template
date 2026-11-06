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
| 2: restoration integrity | Complete locally | 18 behavioral cases, 15 compiler checks, full gate and isolated review passed |
| 3: decision projection | Complete locally | 16 record tests, 1,000-record archive, full gate, new-project smoke and isolated review passed |
| 4: durable task state | Complete locally | 22 lifecycle/preservation tests, full gate, fresh-project smoke and isolated acceptance |
| 5: cost awareness | Next | Optional measurements remain distinct; pacing remains OFF by default |
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

Phase 2 evidence: full 171-file gate; hook fixtures; Python 3.9 syntax;
disposable new-project smoke; isolated reviewer accepted after one repair round.
Refuted assumption: nonempty metadata plus matching hashes suffices. Empty
collections, interleaved writes and independent resume completeness now have
behavioral regressions. Native delivery remains unverified.

## Phase 3 specification

Objective: make an intentionally recorded decision recoverable with provenance
without injecting the entire archive. Owned: compiler/record CLI and tests,
memory-write workflows/skill mirrors, context guide and upgrade/test manifests.
Non-goals: embeddings, transcript capture, automatic private-data export or a
worker fleet. Preserve legacy records as global scope and existing budgets.
Acceptance: atomic create with read-back hash, explicit category/source/scope,
required-ID selection, full retrieval by ID, no required record dropped, and a
bounded projection over a 1,000-record synthetic archive. Missing/superseded
required IDs and invalid scopes fail visibly. Verify cross-process roundtrip,
budget refusal, collision preservation and schema/mirror compatibility.

Phase 3 evidence: 16 record-capture/selection regressions; 15 compiler cases;
18 restoration tests in the full 173-file gate; new-project capture/restore;
Python 3.9 syntax; generated mirrors; isolated acceptance after one repair.
Capacity refusal is checked under the writer lock before publication. Global
prefix stability is tested across task switches; provider cache gains remain
unmeasured. The default scope for legacy records is unchanged.

## Phase 4 specification — 2026-11-06

Objective: preserve open tasks and parent acceptance independently of one rolling
handoff. Owned: private task-state CLI/library, schema/tests, preservation
manifests, delegation/handoff documentation and concise operational memory.
Non-goals: no worker launcher, remote transport, authenticated identities or
automatic process cancellation. Reuse portable task/result envelopes.
Acceptance: atomic private per-task documents; explicit revisions/attempt IDs;
dependency and conservative ownership/WIP gates; content/inventory scope audit
against an immutable attempt baseline; result submission distinct from parent
acceptance; changed artifacts invalidate pending acceptance; restart and late
result tests. Imported commands are never executed. Verification evidence is
the coordinator's declared externally observed result, not a signed runtime
attestation. Future native supervision remains phase 8.

Phase 4 evidence: full 177-file gate, 22 task tests, Python 3.9 syntax and
fresh-project ledger smoke. Critic accepted after one repair: queued blockers
now pass the same open-capacity/ownership admission as other open work. Frozen
315-file inventories were unchanged during both read-only reviews. The generator
intentionally copies tracked files only; new artifacts were staged before its
successful smoke. No native dispatcher or pacing run was activated.

## Phase 5 specification - 2026-11-06

Objective: support bounded ordinary-task cost/progress checkpoints without
starting quota pacing. Owned: sanitized measurement helper/tests, benchmark
token semantics, measurement docs and preservation/test manifests.
Non-goals: provider billing enforcement, quota attribution from shared accounts,
automatic telemetry discovery or changing model defaults.
Acceptance: cumulative snapshots count once per actor/segment; reasoning/cache
subsets never inflate totals; unknown/stale/session/account data cannot become
task cost; explicit hard budgets hold on missing evidence or projected overrun;
completion stops useful work early. Preserve pacing confirmation/OFF semantics.
Verify missing/stale measurements, resets/model switches, double counting,
worker/main aggregation, hard limits, no-progress checkpoints and early completion.
