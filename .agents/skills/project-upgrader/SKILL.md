---
name: project-upgrader
description: Upgrade an existing project's agent framework from a local AI Agent Project Template or its latest GitHub/GitLab source while preserving application code, custom rules, skills and memory. Use for requests to bring an older project up to date with the template.
---

# Project Upgrader

Read the target project's AGENTS.md, then follow the canonical
[upgrade workflow](../../../workflows/upgrade-project.md).

Resolve the template URL from the user or `.template-upstream.json`, never from
the application's origin. Obtain and inspect the latest template outside the
project before using its upgrader; an older installed script may have a stale
file inventory. Preview first and apply the same upstream commit SHA.

Conflicts are preserved for a careful agent merge. `--apply-safe` exit 2 means
incomplete. Keep project rules and history intact, verify baseline application
checks, and stage only reviewed upgrade paths. Existing user authorization
applies; this skill grants no permission to publish or deploy.
