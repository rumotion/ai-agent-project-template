# Conventions

Adapter for tools that read a `CONVENTIONS.md` file (e.g. Aider).

Read `AGENTS.md` first; it is canonical. Then read `memory-bank/startup.md`. If resuming work, also read `memory-bank/handoff.md`. Lazy-load deeper context only when the task requires it.

Do not add instructions here that conflict with `AGENTS.md`. Aider loads this file via `.aider.conf.yml` (`read: [AGENTS.md, CONVENTIONS.md]`).
