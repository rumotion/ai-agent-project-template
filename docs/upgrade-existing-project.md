# Upgrade Existing Projects from GitHub or GitLab

Ask the agent inside an existing project:

```text
Upgrade this project's AI agent framework from
https://github.com/rumotion/ai-agent-project-template using its latest upgrade
workflow. Preserve application code, tests, custom rules, skills, settings and
project memory. Preview, apply safe changes, resolve conflicts and run the
project's checks. Do not push or deploy.
```

Replace the URL with your template repository on GitHub or GitLab. The example
URL is this template's published source; forks should use their own source.
This works with an older project even if it does not yet have the upgrade skill:
the prompt tells the agent to obtain the latest workflow from the supplied source.
The agent needs local file/command access, Python 3.9+ and Git. Private sources
need existing Git credentials or SSH access. No GitHub/GitLab API token is stored.

After the first remote update, `.template-upstream.json` remembers the source
and installed hashes. The next request can be:

```text
Update this project from its saved AI template source using the latest upgrade
workflow, preserve project customizations, and verify the result locally.
```

## What gets updated

The upgrader has an explicit inventory of agent adapters, standard skills and
workflows, reviewer contracts, hook source files, documentation and validation
scripts. It compares each candidate with the current source and previously
installed hashes. Unchanged files can update automatically; local edits and
unknown older files become conflicts. It never deletes retired template files.
A known earlier template release can supply a baseline for legacy projects.

Existing Memory Bank files are preserved. Missing project context gets neutral
stubs. Active client settings, application manifests, lockfiles, code, tests,
root README, release version and Git configuration stay under project control.
Conflicting AGENTS.md rules need an agent merge, preserving all domain rules.

## Commands

Run from a reviewed current template checkout outside the target:

```bash
# Local source: preview and apply (no network)
python scripts/upgrade-target.py --target /path/to/project --dry-run
python scripts/upgrade-target.py --target /path/to/project

# Remote source: GitHub, GitLab or self-hosted GitLab
python scripts/upgrade-target.py --target /path/to/project --source https://gitlab.com/GROUP/TEMPLATE.git --dry-run
python scripts/upgrade-target.py --target /path/to/project --source https://gitlab.com/GROUP/TEMPLATE.git --expect-commit FULL_SHA --apply-safe
```

`--ref` selects a branch, tag or SHA (default HEAD, or saved ref). Use the exact
commit from the preview with `--expect-commit`; if HEAD moves, apply stops.
For a verified older version, add `--baseline-ref PREVIOUS_TAG_OR_SHA` to the
preview and its resolved baseline SHA to apply. Unknown changes remain conflicts.

Default apply stops before any write when conflicts exist. `--apply-safe` applies
safe paths and reports conflicts with exit 2. Exit 0 does not certify that the
application tests pass: the agent runs baseline and post-update checks separately.
No downloaded hooks, installers or validators are executed by the upgrader.

## Review and recovery

Each apply prints an external backup/report directory. `files/` contains the
original contents of replaced files, and `report.json` lists additions, updates,
conflicts and source commit. Backups may contain project-specific instructions;
keep them private and outside Git. Ordinary write errors roll back the files
already changed. If the process or machine stops abruptly, inspect the report
and restore reviewed paths from that backup before another upgrade. Check
current edits before any manual restoration or removal of newly created files.

The canonical [agent workflow](../workflows/upgrade-project.md) covers source
review, conflict merges, application checks and exact-path local commits. It
never pushes, deploys or modifies the application's origin. Automated file
preservation reduces risk; application compatibility still requires those checks.

Offline regression checks: `python scripts/verify-upgrade.py`.

Use `--backup-dir /external/private/directory` to select an existing backup
parent. A backup location inside the target is rejected before any write.
