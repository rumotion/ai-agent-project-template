#!/usr/bin/env python3
"""Detach a project from an inherited git remote and block accidental pushes.

Why this exists
---------------
`git clone` copies the remote configuration. A project cloned from a template
therefore keeps pointing at the *template's* repository, and any push from the
project lands there -- mixing unrelated projects into one repository, and
publishing whatever the project contains if that repository is public.

This script makes a project local-only:

  1. reports the current remotes,
  2. removes remotes that point at the template (or all, with --all),
  3. installs a `pre-push` hook that refuses to push,
  4. verifies the result.

Nothing is uploaded, and no history is rewritten. Removing a remote loses only a
URL; adding one back later is a single command.

Usage
-----
    python scripts/detach-remote.py                 # remove template remotes
    python scripts/detach-remote.py --all           # remove every remote
    python scripts/detach-remote.py --pattern foo   # remove remotes matching "foo"
    python scripts/detach-remote.py --check         # report only, change nothing

Exit codes: 0 clean/fixed, 1 still unsafe, 2 not a git repository.
"""

from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys

DEFAULT_PATTERN = "ai-agent-project-template"

HOOK = """#!/bin/sh
# Installed by scripts/detach-remote.py -- this project is local-only by default.
echo "" >&2
echo "  PUSH BLOCKED - this project is local-only." >&2
echo "" >&2
echo "  To publish deliberately:" >&2
echo "    1. create a NEW repository for THIS project only" >&2
echo "    2. git remote add origin <that-new-repo-url>" >&2
echo "    3. rm .git/hooks/pre-push" >&2
echo "" >&2
echo "  Never point a project at a shared template repository." >&2
echo "  Never run: git push --force --mirror" >&2
echo "" >&2
exit 1
"""


def git(*args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return proc.returncode, (proc.stdout or "").strip()


def git_dir() -> str | None:
    code, out = git("rev-parse", "--git-dir")
    return out if code == 0 and out else None


def remotes() -> dict[str, str]:
    code, out = git("remote")
    if code != 0 or not out:
        return {}
    found = {}
    for name in out.splitlines():
        name = name.strip()
        if not name:
            continue
        _, url = git("remote", "get-url", name)
        found[name] = url
    return found


def install_hook(gitdir: str) -> str:
    hooks = os.path.join(gitdir, "hooks")
    os.makedirs(hooks, exist_ok=True)
    path = os.path.join(hooks, "pre-push")
    # LF endings matter: git runs this through sh even on Windows.
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HOOK)
    try:
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass  # chmod is a no-op on some Windows filesystems; git still honours the hook
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Make this project local-only.")
    ap.add_argument("--all", action="store_true", help="remove every remote, not just template ones")
    ap.add_argument("--pattern", default=DEFAULT_PATTERN, help=f"substring to match (default: {DEFAULT_PATTERN})")
    ap.add_argument("--check", action="store_true", help="report only, change nothing")
    args = ap.parse_args()

    gitdir = git_dir()
    if not gitdir:
        print("Not a git repository.")
        return 2

    current = remotes()
    if not current:
        print("No remotes configured - this project cannot push. Nothing to do.")
    else:
        print("Current remotes:")
        for name, url in current.items():
            flag = " <-- INHERITED TEMPLATE REMOTE" if args.pattern in url else ""
            print(f"  {name}: {url}{flag}")

    unpushed = None
    code, out = git("rev-list", "--count", "@{u}..HEAD")
    if code == 0 and out.isdigit():
        unpushed = int(out)
        if unpushed:
            print(f"\n{unpushed} local commit(s) have never been pushed. They stay on this machine.")

    doomed = [n for n, u in current.items() if args.all or args.pattern in u]

    if args.check:
        if doomed:
            print("\nUNSAFE: " + ", ".join(doomed) + " would allow a push to a shared repository.")
            print("Run without --check to detach.")
            return 1
        print("\nSafe: no inherited template remote.")
        return 0

    for name in doomed:
        rc, _ = git("remote", "remove", name)
        print(f"\nRemoved remote '{name}'" if rc == 0 else f"\nFailed to remove remote '{name}'")

    hook = install_hook(gitdir)
    print(f"Installed push block: {hook}")

    left = remotes()
    print("\nResult:")
    if left:
        for name, url in left.items():
            print(f"  remote {name}: {url}")
        print("  (a remote remains - the pre-push hook still blocks pushing)")
    else:
        print("  no remotes - this project cannot push anywhere")
    print("  This project is local-only. Local commits are fine.")
    print("  If it ever needs hosting, create a repository for THIS project alone.")

    return 0 if not [n for n, u in left.items() if args.pattern in u] else 1


if __name__ == "__main__":
    sys.exit(main())
