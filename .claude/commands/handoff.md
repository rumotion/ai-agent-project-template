---
description: Update memory-bank/handoff.md to pause or switch models
---

We are pausing or switching models. Update `memory-bank/handoff.md`:

- Refresh the YAML header: `last_touched`, `last_model`, `to_model`, `branch`, `status`, `task`, `next_action`, `files_modified`, `blocking_issues`.
- Verify `next_action` and `branch` against `git status` before writing them.
- Keep the prose body under ~30 lines. Overwrite — do not append history.

Then stop and report the single next concrete step.
