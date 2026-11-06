---
description: Write a phase-completion summary and update the Memory Bank
---

The current unit of work is finished. Following `docs/agent-loop.md` §7:

1. Append a phase-completion summary (outcome, key decisions, files modified, open items, next) to `memory-bank/activeContext.md`.
2. Update `memory-bank/progress.md` (Done / Next) and `memory-bank/handoff.md`.
3. Clear any acted-on entries from `memory-bank/reminders.md`.
4. Persist durable decisions as typed records using `workflows/update-memory-bank.md`;
   link their IDs from summaries and verify inclusion for the selected task.

Change only files whose facts changed. Keep every entry concise.
