#!/usr/bin/env python3
"""Bootstrap a new project from this template into a separate directory.

A plain folder copy is the wrong tool: it drags in this repository's untracked
development scratch (local planning notes, `tmp/`, `.agent-logs/`,
`__pycache__/`, local agent settings) and, worse, hands the new project a
Memory Bank describing *the template's* history. Agents read
`memory-bank/startup.md` and `handoff.md` on every session, so a copied Memory
Bank makes the new project's agent confidently believe it is working on the
template.

This script instead:

1. copies only git-tracked files (so `.gitignore` decides what is scratch),
2. resets the Memory Bank to blank, project-appropriate stubs,
3. resets `README.md`, `VERSION`, and `CHANGELOG.md`,
4. drops template-governance files a derived project should not inherit,
5. initializes a fresh local repository with no remote.

It never adds a remote, pushes, or publishes anything, per `AGENTS.md`
-> Repository boundaries.

Usage:

    python scripts/new-project.py <target-dir> [--name NAME] [--dry-run]

Standard library only, so it runs in a fresh clone with no install step.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import List, Optional
from push_backstop import install


ROOT = Path(__file__).resolve().parents[1]

# Template governance and release history. A derived project should start with
# its own. None of these appear in check-template.py REQUIRED_FILES, so the new
# project still validates without them.
DROP_PATHS = [
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/releasing.md",
    "docs/template-improvement-brief.md",
    "docs/proposals",
]

# Memory Bank files holding the template's own history. Replaced with stubs.
# Not listed here (kept verbatim, they are scaffolding not history):
#   00-index.md, model-routing.md, reminders.md, userPreferences.md
MEMORY_STUBS = {
    "startup.md": """# Startup Context

Project: {name}.

Goal: TBD РІР‚вЂќ describe the project in one or two sentences.

Current focus: Initial setup. No implementation yet.

If resuming work or switching models, read `memory-bank/handoff.md` next.

Next:
- Define goal, stack, and first milestone with the user.
- Keep unknowns as `TBD` until the user provides them.
""",
    "handoff.md": """---
handoff_version: 3
last_touched: {date}
last_model: none
to_model: Any
branch: main
status: Fresh project created from the AI Agent Project Template
task: Initial setup
next_action: Define goal, stack, and first milestone with the user
files_modified: []
blocking_issues: []
---

# Handoff

New project. Nothing implemented yet.

Read `AGENTS.md`, then `memory-bank/startup.md`. Ask the user for goal, stack,
and first milestone before writing code.
""",
    "projectbrief.md": """# Project Brief

- **Project**: {name}
- **Goal**: TBD
- **Users**: TBD
- **Scope**: TBD
- **Out of scope**: TBD
- **Constraints**: TBD
- **Success criteria**: TBD
""",
    "activeContext.md": """# Active Context

Current task: Initial setup.

Nothing in progress yet.

## Refuted hypotheses

None yet. Record disproven beliefs and their killing evidence here.
""",
    "progress.md": """# Progress

## Done

- Project created from the AI Agent Project Template.

## Next

- TBD

## Known issues

- None.
""",
    "productContext.md": """# Product Context

- **Problem**: TBD
- **Audience**: TBD
- **Key user journeys**: TBD
- **Non-functional requirements**: TBD
""",
    "systemPatterns.md": """# System Patterns

Architecture, module boundaries, and recurring patterns.

TBD РІР‚вЂќ record these once the stack is chosen.
""",
    "techContext.md": """# Tech Context

- **Stack**: TBD
- **Package manager**: TBD
- **Run**: TBD
- **Test**: TBD
- **Lint / typecheck**: TBD
- **Build**: TBD
""",
    "decisions.md": """# Decisions

Important decisions and their rationale. Newest first.

## Decision template

### YYYY-MM-DD РІР‚вЂќ Decision title

Status: Proposed / Accepted / Rejected / Superseded

Context:

Decision:

Consequences:

Related files:
""",
    "risks.md": """# Risks

Security, migration, and performance risks, plus one-line lessons from
exhausted retries.

- None recorded yet.
""",
    "glossary.md": """# Glossary

Domain terms used in this project.

- TBD
""",
}

README_STUB = """# {name}

TBD РІР‚вЂќ one-paragraph description of this project.

## Status

Fresh project created from the AI Agent Project Template.

## Working with AI agents

`AGENTS.md` is the canonical instruction file for every agent. Start a session
with:

```text
FAST_INIT (default mode per AGENTS.md).
```

Validate repository structure at any time:

```bash
python scripts/check-template.py
```

## Getting started

TBD РІР‚вЂќ add setup, run, and test commands once the stack is chosen.
"""

CHANGELOG_STUB = """# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Project created from the AI Agent Project Template.
"""


def _configure_stdout_utf8() -> None:
    # Windows consoles often default to cp1251/cp1252 and crash on non-ASCII.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def fail(message: str) -> "NoReturn":  # type: ignore[valid-type]
    print("ERROR: {}".format(message), file=sys.stderr)
    raise SystemExit(1)


def tracked_files() -> List[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        fail("`git ls-files` failed in the template root. Is this a git repository?")
    return [line for line in result.stdout.splitlines() if line.strip()]


def working_tree_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return bool(result.stdout.strip())


def today() -> str:
    # Avoid importing datetime for a single value the user can correct.
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stamp = result.stdout.strip()
    return stamp if stamp else "TBD"


def copy_tracked(target: Path, files: List[str], dry_run: bool) -> int:
    copied = 0
    for relative in files:
        source = ROOT / relative
        if not source.is_file():
            # Tracked but deleted in the working tree; skip rather than crash.
            continue
        destination = target / relative
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        copied += 1
    return copied


def drop_template_governance(target: Path, dry_run: bool) -> List[str]:
    removed = []
    for relative in DROP_PATHS:
        path = target / relative
        # On a dry run nothing was copied, so report against the template.
        probe = (ROOT / relative) if dry_run else path
        if not probe.exists():
            continue
        if dry_run:
            removed.append(relative)
            continue
        if not dry_run:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        removed.append(relative)
    return removed


def reset_memory_bank(target: Path, name: str, date: str, dry_run: bool) -> List[str]:
    written = []
    bank = target / "memory-bank"
    for filename, template in MEMORY_STUBS.items():
        path = bank / filename
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(template.format(name=name, date=date), encoding="utf-8")
        written.append("memory-bank/{}".format(filename))
    return written


# Typed record starter. The template's own records describe the template;
# a derived project must start from a blank, project-appropriate record.
RECORD_STUB = """---
id: fact-project-created
type: fact
priority: 3
superseded_by:
---
Project created from the AI Agent Project Template on {date}. Add typed records here (type: fact | decision | risk | preference; priority 1-5) and compile them with `python scripts/ctx.py compile --for <client>`.
"""


def reset_records(target: Path, date: str, dry_run: bool) -> None:
    records_dir = target / "memory-bank" / "records"
    if not dry_run:
        if records_dir.exists():
            shutil.rmtree(records_dir)
        records_dir.mkdir(parents=True, exist_ok=True)
        (records_dir / "fact-project-created.md").write_text(
            RECORD_STUB.format(date=date), encoding="utf-8"
        )


def reset_project_files(target: Path, name: str, dry_run: bool) -> List[str]:
    written = []
    for relative, content in (
        ("README.md", README_STUB.format(name=name)),
        ("CHANGELOG.md", CHANGELOG_STUB),
        ("VERSION", "0.1.0\n"),
    ):
        if not dry_run:
            (target / relative).write_text(content, encoding="utf-8")
        written.append(relative)
    return written


def install_push_backstop(target: Path) -> bool:
    """Install local-only accident prevention; preserve unknown hooks on error."""
    install(target)
    return True


def git_init(target: Path, dry_run: bool) -> Optional[str]:
    """Initialize a local repository. Never adds a remote."""
    if dry_run:
        return None
    init = subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=target,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if init.returncode != 0:
        # Older git without -b support.
        init = subprocess.run(
            ["git", "init"],
            cwd=target,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if init.returncode != 0:
            return "git init failed: {}".format(init.stderr.strip())
    subprocess.run(["git", "add", "-A"], cwd=target, capture_output=True)
    commit = subprocess.run(
        ["git", "commit", "-m", "chore: initial project from AI Agent Project Template"],
        cwd=target,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if commit.returncode != 0:
        return "git commit failed (configure user.name/user.email): {}".format(
            commit.stderr.strip() or commit.stdout.strip()
        )
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new project from this template.",
        epilog="Never adds a remote or pushes. Publishing stays a human decision.",
    )
    parser.add_argument("target", help="Directory for the new project.")
    parser.add_argument(
        "--name",
        default=None,
        help="Project name used in stubs. Defaults to the target directory name.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would happen without writing anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Proceed even if the target directory is not empty.",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git init and the initial commit.",
    )
    return parser.parse_args()


def main() -> int:
    _configure_stdout_utf8()
    args = parse_args()

    target = Path(args.target).expanduser().resolve()
    name = args.name or target.name

    if target == ROOT:
        fail("Target is the template itself. Choose a different directory.")
    if ROOT in target.parents:
        fail("Target is inside the template directory. Choose a location outside it.")

    if target.exists():
        if not target.is_dir():
            fail("Target exists and is not a directory: {}".format(target))
        existing = [p for p in target.iterdir() if p.name != ".git"]
        if existing and not args.force:
            fail(
                "Target directory is not empty ({} entries). "
                "Re-run with --force to proceed anyway.".format(len(existing))
            )

    if working_tree_dirty():
        print(
            "Note: the template working tree has uncommitted changes. "
            "Current file contents will be copied.\n"
        )

    files = tracked_files()
    date = today()

    print("Template : {}".format(ROOT))
    print("Target   : {}".format(target))
    print("Name     : {}".format(name))
    print("Mode     : {}\n".format("DRY RUN (no writes)" if args.dry_run else "apply"))

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    copied = copy_tracked(target, files, args.dry_run)
    print("1. Copied {} git-tracked files (untracked scratch excluded).".format(copied))

    removed = drop_template_governance(target, args.dry_run)
    print("2. Dropped template governance: {}".format(", ".join(removed) or "nothing"))

    stubs = reset_memory_bank(target, name, date, args.dry_run)
    reset_records(target, date, args.dry_run)
    print("3. Reset {} Memory Bank files and typed records to blank stubs.".format(len(stubs)))

    project_files = reset_project_files(target, name, args.dry_run)
    print("4. Reset {}.".format(", ".join(project_files)))

    if args.no_git or args.dry_run:
        print("5. Skipped git init.")
    else:
        error = git_init(target, args.dry_run)
        if error:
            print("5. git init incomplete: {}".format(error), file=sys.stderr)
            return 1
        else:
            print("5. Initialized local git repository on 'main' (no remote).")
            if install_push_backstop(target):
                print("   Verified local-only pre-push hook in Git's resolved hook directory.")

    print("\nDone." if not args.dry_run else "\nDry run complete. Nothing written.")
    print("\nNext steps:")
    print("  cd {}".format(target))
    print("  python scripts/check-template.py     # verify structure")
    print("  python scripts/init-fast.py          # print the FAST_INIT prompt")
    print("\nThis project has no git remote. Publishing is a human decision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
