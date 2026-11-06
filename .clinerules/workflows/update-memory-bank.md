# Workflow: Update Memory Bank

1. Read `memory-bank/00-index.md`.
2. Review recent code/doc changes relevant to the task.
3. Update only relevant Memory Bank files.
   Durable decisions, risks and preferences must have typed source records:
   `python scripts/ctx.py record --id ID --type decision --source-ref SOURCE_ID --body-file REVIEWED_FILE`.
   Select `--scope task --task-id TASK_ID` for task-specific records or
   `--scope archive` for retrievable history; legacy/global constraints load
   by default. Record category `example` or `hypothesis` uses `--type fact`.
   Preserve qualifications. Inspect the returned path/hash/inclusion receipt;
   `stored: true` with a blocked projection requires recovery, not a retry that
   duplicates the record. Link record IDs from prose summaries. See
   `docs/context-compiler.md`; prose alone is not automatic restoration.
4. Keep entries concise.
5. Do not duplicate information.
6. (Optional, useful when several models share the project) End the touched file with `_Last touched: YYYY-MM-DD by <model>_` so provenance is visible.
7. Summarize what changed.

Keep raw private feedback and operational receipts outside public repositories.
Review and sanitize material before the record command; an opaque source ID
does not authorize importing confidential source contents. Store only useful,
reviewed project facts, not every message or failed attempt as a global rule.
