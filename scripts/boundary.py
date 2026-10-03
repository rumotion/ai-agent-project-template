#!/usr/bin/env python3
"""Inspect advisory controls; refuse unsupported containment/release profiles."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
from push_backstop import LOCAL_ONLY_HOOK, hook_path, strict_detach_hook

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = ("claude", "codex", "gemini", "cline", "roo", "cursor",
           "copilot", "windsurf", "aider", "antigravity")
PROFILES = ("advisory", "contained-local", "release")


def inspect(root: Path, client: str, profile: str = "advisory") -> dict:
    resolved = installed = False
    limitations = [
        "Git hooks can be disabled or modified by the worker",
        "Native tool events and consumed denials have no live-client evidence",
        "No external egress or protected-path isolation is supplied",
        "Contained-local and release launchers are unsupported",
    ]
    try:
        target = hook_path(root)
        resolved = True
        approved = [LOCAL_ONLY_HOOK]
        detached = strict_detach_hook(ROOT)
        if detached:
            approved.append(detached)
        installed = (target.is_file() and target.read_bytes() in approved and
                     (os.name == "nt" or os.access(target, os.X_OK)))
    except (OSError, ValueError, SyntaxError):
        limitations.append("Git hook configuration cannot be verified")
    return {"version": 1, "client": client, "profile": profile,
            "hook_path_resolved": resolved, "approved_hook_installed": installed,
            "tool_events_verified": False, "egress_denied_outside_worker": False,
            "protected_paths_denied_outside_worker": False,
            "authority_outside_worker": False, "limitations": limitations}


def verified(document: dict) -> bool:
    # Advisory verifies only ordinary accidental-push prevention, never isolation.
    return (document["profile"] == "advisory" and
            document["hook_path_resolved"] and document["approved_hook_installed"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "verify"))
    parser.add_argument("--client", choices=CLIENTS, default="codex")
    parser.add_argument("--profile", choices=PROFILES, default="advisory")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    document = inspect(args.root, args.client, args.profile)
    if args.json:
        print(json.dumps(document, sort_keys=True))
    else:
        print("{}: {} ({})".format(args.client, args.profile,
              "verified advisory hook" if verified(document) else "unverified"))
        for limitation in document["limitations"]:
            print("- " + limitation)
    return 0 if args.command == "inspect" or verified(document) else 1


if __name__ == "__main__":
    sys.exit(main())
