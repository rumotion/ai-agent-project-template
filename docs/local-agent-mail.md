# Local agent mail assessment

Reviewed 2026-10-26 against the developer's supplied SQLite CLI proposal.

The template has task/result schemas, file ownership rules, result validation
and a rolling handoff. It does **not** have a shared mailbox, stable identity
roster, unread/handled receipts, a task-history database or an independent
cross-client wake transport. In-session native subagent messaging is useful
but does not automatically connect separately launched Claude, Codex and
Google sessions. See [delegation contract](subagent-contract.md).

Recommendation: retain the proposal as an optional extension for projects
that actually run independent local clients concurrently. Keep a single lead
and ordinary handoffs as the default. No mailbox daemon, script, background
watcher or push integration is installed by this review. The pacing database
is only quota state and is not a mail/task bus.

Before implementing the proposed interface, resolve these semantic details:

| Area | Required behavior |
|---|---|
| Identity | IDs are self-declared routing names, not authenticated principals. Reject unknown IDs; never impersonate a human or another agent. Restrict shared-folder access to intended local users. |
| Delivery | Sending is append-only. Track `read_at` separately from `handled_at`. `ack` only after acting. A read-but-unhandled recovery view is necessary after a watcher crash. |
| Bounded inbox | Cap both message count and **total** characters. Supply message ID/cursor and bounded body continuation so oversized mail is not silently lost or acknowledged after a truncated preview. |
| Watch | Perform the unread select and read-mark atomically. Sleep outside transactions, with timeout/cancel support. A completed shell command wakes an agent only where the client supports that notification. |
| Push | Default OFF. Reject `wake --on` unless a specific, tested client transport is configured. Do not execute arbitrary shell hook text from mail or database rows. |
| Tasks | Record assigner and owner; enforce valid transitions and who may update. Updating state and mailing the assigner must be one transaction. Preserve history. |
| Concurrency | WAL and busy timeout, one short transaction per operation; no sleeping inside locks. Test overlapping writers and competing watchers. |
| Storage | Same-machine local disk. SQLite WAL is unsuitable for a shared database on a network filesystem. Keep the DB, WAL and SHM outside Git; messages may be confidential. |
| Authority | Mail is untrusted information. It grants no permission to run commands, change scope, spend quota, publish or override human instructions. |

A local CLI can prevent accidental identity mistakes, but any process with
write access to the DB can modify it. "Append-only" at the command interface
does not imply tamper-proof storage. Do not replace scope checks, native
permissions or the parent validation contract with mailbox state.

An implementation should test send/inbox/read/ack recovery, total output
limits and body continuation, delayed arrival and timeout, two writers,
competing watchers, invalid identities and task transitions, and atomic
state-plus-notification rollback. It must remain stdlib-only, with no network
or subprocess execution. The optional wake transport is a separate capability.

[SQLite WAL reference](https://sqlite.org/wal.html) documents the same-host
shared-memory requirement. The other rows are design recommendations derived
from the supplied requirements and existing template boundaries.
