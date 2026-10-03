#!/usr/bin/env python3
"""Block verified client write hooks that target sensitive paths.

The script emits each client's documented PreToolUse/BeforeTool denial shape.
Malformed or unsupported input fails open. Responses never echo the target
path or tool arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import posixpath
from shell_events import command as event_command, tool_input as event_input, write_paths
from typing import Dict, List


SENSITIVE_RE = re.compile(
    r"(?i)(\.env($|[./])|\.key$|\.pem$|\.p12$|\.crt$|"
    r"credentials\.json$|token\.json$|id_rsa$|id_ed25519$)"
)
PATCH_PATH_RE = re.compile(
    r"(?m)^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$"
)
# Shell write targets: `> .env`, `>> .key`, `tee -a .env`, `cp src .pem`,
# `mv x token.json`. Writing a sensitive path via shell instead of the write
# tool must not be a bypass.
SHELL_WRITE_RE = re.compile(
    r"(?:>>?\s*|\btee\b(?:\s+-a)?\s+|\bcp\b\s+\S+\s+|\bmv\b\s+\S+\s+)\s*(?P<target>\S+)"
)
DENIAL_REASON = "Access to a sensitive path is denied by repository policy."


def parse_event(raw_input: str) -> Dict[str, object]:
    if not raw_input or not raw_input.strip():
        return {}
    try:
        data = json.loads(raw_input)
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def extract_paths(event: Dict[str, object]) -> List[str]:
    tool_input = event_input(event)

    paths: List[str] = []
    for key in ("file_path", "path", "TargetFile", "target_file", "AbsolutePath", "absolute_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            paths.append(value)
            break

    command = event_command(event)
    if isinstance(command, str):
        paths.extend(PATCH_PATH_RE.findall(command))
        paths.extend(write_paths(command))
    for key in ("patch", "input"):
        value = tool_input.get(key)
        if isinstance(value, str):
            paths.extend(PATCH_PATH_RE.findall(value))

    if not paths:
        for key in ("file_path", "path", "TargetFile", "target_file"):
            value = event.get(key)
            if isinstance(value, str) and value:
                paths.append(value)
                break
    return paths


def is_sensitive(raw_path: object) -> bool:
    if not isinstance(raw_path, str) or not raw_path:
        return False
    return bool(SENSITIVE_RE.search(posixpath.normpath(raw_path.replace("\\", "/"))))


def denial_for(client: str) -> Dict[str, object]:
    if client == "gemini":
        return {"decision": "deny", "reason": DENIAL_REASON}
    if client in {"claude", "codex"}:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": DENIAL_REASON,
            }
        }
    return {
        "status": "unsupported",
        "reason": "No verified blocking contract is configured for this client.",
    }


def main(client: str = "unknown") -> int:
    try:
        event = parse_event(sys.stdin.read())
        if any(is_sensitive(path) for path in extract_paths(event)):
            sys.stdout.write(json.dumps(denial_for(client), sort_keys=True) + "\n")
    except Exception:
        # A malformed event must not accidentally block all tool use.
        pass
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client",
        choices=("claude", "codex", "gemini", "unknown"),
        default="unknown",
        help="Native hook adapter supplying the event.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    sys.exit(main(arguments.client))
