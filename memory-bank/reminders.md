# Reminders (Prospective Memory)

Trigger-keyed notes for *future* work — things that shouldn't be done now but must not be forgotten. Any agent checks this file when starting a new phase, before a deploy, or on a model switch. **Delete each entry once it has been acted on.**

Keep entries one line. Use a clear trigger in the first column.

| Trigger | Note |
|---|---|
| _example: phase-5_ | _Revisit the auth rate-limit decision recorded in `decisions.md`._ |
| _example: before-deploy_ | _Run a full secret scan — a new env var was added._ |
| _example: next-model-switch_ | _Open TODO left in `src/api/routes.py` near the rate limiter._ |

Replace the example rows with real reminders, or leave the table empty (`none`) for a fresh project.

See `docs/agent-loop.md` §5 for how this fits the phase-completion loop.
