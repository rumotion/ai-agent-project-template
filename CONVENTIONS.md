# Conventions

Adapter for tools reading `CONVENTIONS.md` (e.g. Aider). Read `AGENTS.md` first; it is canonical. Then read `memory-bank/startup.md` and `memory-bank/handoff.md`.

## Git & Commit Conventions

- **Phased Planning**: Plan tasks with clear, verifiable step checkpoints.
- **Atomic Step Commits**: Run `git commit` immediately after verifying each step checkpoint (`<type>(<scope>): <step description>`).
- **Pre-Commit Check**: Verify tests pass before committing. Never commit broken builds.
- **Push Policy**: Push commits to remote (`git push`) on milestone/phase completion.


