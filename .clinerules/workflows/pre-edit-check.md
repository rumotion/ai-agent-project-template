# Workflow: Pre-Edit Check

A fast, pre-flight verification procedure executed before modifying any file in the workspace. Prevents scope creep, accidental overwrites, and repeat failures.

## Steps

1. **Inspect Targets & Working Tree**: Run `git status --short` and inspect target file paths and existing uncommitted diffs (`git diff`). Confirm you have exclusive ownership of target paths.
2. **Consult Memory Bank Risks & Decisions**: Search `memory-bank/risks.md` and `memory-bank/decisions.md` for past failure patterns or architectural rules affecting target paths.
3. **Confirm Scope & Non-Goals**: Clearly define what lines/files will change and what must NOT be touched.
4. **Identify Verification Command**: Determine the smallest deterministic test, script, or syntax check that will verify the change (e.g. `python scripts/check-template.py --fast`).
5. **Enforce Safety Boundaries**: STOP and seek explicit human approval if the edit involves:
   - Destructive operations (`git reset`, file deletion, table drops)
   - Secrets, credentials, or `.env` entries
   - Adding new third-party dependencies or external API calls
   - Production deployment or database migration scripts
