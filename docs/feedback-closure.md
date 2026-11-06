# Optional feedback and retrospective closure

Use this for meaningful user feedback or repeated process failures. Small clear
edits can use a single task note. This workflow uses existing records, task
envelopes and parent acceptance; it is not an automatic feedback service.

## Trace one item

1. Assign an opaque ID, for example `feedback-017`. Keep the exact private source,
   timestamp/locator and authority provenance in a private register outside Git.
   Include owner, reviewed summary, state, decision ID, task ID and closure
   evidence. Never copy private messages into a public-history repository.
2. Review meaning before implementation. Distinguish a requirement/decision from
   an example, preference or hypothesis. Capture the reviewed project-safe record
   with `ctx.py record --source-ref feedback-017 ...`; preserve qualifiers. Use
   `--type fact --category example` for an example. Read back with `ctx.py show`.
   An ID/reference records provenance; it does not authenticate approval.
3. Before creating work, inspect the register's unresolved, rejected, deferred
   and superseded entries. Retrieve the exact relevant records by ID. Reopen a
   rejected idea only with a stated changed premise/new evidence and sufficient
   existing authority; otherwise retain the rejection. Do not relabel it as new.
4. Put the exact reviewed record path in the portable task's `inputs`, and its
   ID/feedback ID in the bounded `constraints` or `scope`. Define objective,
   non-goals, owner, acceptance environment and whole-package verification. Use
   `tasks.py create`, dependencies and existing WIP admission. Parent-only memory
   writes and the original source/ref remain separate from worker authority.
5. Submit evidence; independently verify the frozen artifact. A worker's
   `completed` result enters review. Close the implementation item only after
   parent `accept` succeeds, recording task/attempt/revision, reviewed digest and
   verification evidence in the private register. Preserve links to rejected or
   replaced decisions; a prose "done" note cannot substitute for acceptance.
6. Where the item concerns a user outcome, record its actual observation separately
   using `product-acceptance.md`. Implementation accepted with user observation
   pending is a valid explicit intermediate state. Never fabricate user approval.

Suggested register states: proposed, approved, rejected, deferred, superseded,
implementation-accepted, outcome-pending, closed. They are reviewed workflow
states, not a new machine-enforced schema. Duplicate IDs, missing links and
contradictory states require coordinator reconciliation before closure.

## Retrospective checkpoint

Start with prior unresolved actions and their owners/evidence, rather than a new
list of ideas. For each remaining item record one observed failure mechanism,
its impact on correctness/user outcome or process, a falsifiable change and the
check that will close it. Keep assumptions distinct from observed failures.

Use a short table: `action ID | owner | prior state | evidence | next check |
closure task/record`. Classify context loss, stale evidence, native capability,
scope/coordination and product behavior separately. Do not treat quota consumption
or agent count as progress. Close proven fixes; carry real external dependencies
forward without retrying unchanged premises. New recommendations need a concrete
check and a bounded owner before they become work.

Repeated failures should become a focused regression or lazy-loaded workflow.
Review instruction size before changing `AGENTS.md`; avoid adding another
permanent prohibition when a local check can express the rule. Semantic duplicate
detection and approval authenticity remain human/coordinator responsibilities.
