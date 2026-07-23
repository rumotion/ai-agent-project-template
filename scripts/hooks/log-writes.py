#!/usr/bin/env python3
"""Passive cross-client write logger.

Hook adapters pass ``--client`` explicitly. Event payloads arrive on stdin.
Only normalized metadata is written; prompts, contents, command arguments,
environment variables, and absolute paths are never persisted.

The logger is standard-library only, Python 3.9 compatible, and fails open.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from typing import Dict, List, Optional


SENSITIVE_RE = re.compile(
    r"(?i)(\.env($|[./])|\.key$|\.pem$|\.p12$|\.crt$|"
    r"credentials\.json$|token\.json$|id_rsa$|id_ed25519$)"
)
PATCH_PATH_RE = re.compile(
    r"(?m)^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$"
)
EVENT_NAMES = {
    "AfterTool": "post_tool_use",
    "BeforeTool": "pre_tool_use",
    "PostToolUse": "post_tool_use",
    "PreToolUse": "pre_tool_use",
}
TOOL_NAME_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


def parse_event(raw_input: str) -> Dict[str, object]:
    if not raw_input or not raw_input.strip():
        return {}
    try:
        data = json.loads(raw_input)
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def event_cwd(event: Dict[str, object]) -> str:
    value = event.get("cwd")
    return value if isinstance(value, str) and value else os.getcwd()


def extract_paths(event: Dict[str, object]) -> List[str]:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = event.get("input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    paths: List[str] = []
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            paths.append(value)
            break

    command = tool_input.get("command")
    if isinstance(command, str):
        paths.extend(PATCH_PATH_RE.findall(command))

    if not paths:
        for key in ("file_path", "path"):
            value = event.get(key)
            if isinstance(value, str) and value:
                paths.append(value)
                break
    return paths


def normalize_and_redact_path(
    raw_path: Optional[str],
    cwd: str,
    workspace_root: str,
) -> Optional[str]:
    if not raw_path or not isinstance(raw_path, str):
        return None
    if "\x00" in raw_path or "\n" in raw_path or "\r" in raw_path:
        return None

    clean_path = raw_path.replace("\\", "/")
    if SENSITIVE_RE.search(clean_path):
        return "<sensitive-path>"

    try:
        absolute_cwd = os.path.abspath(cwd)
        absolute_root = os.path.abspath(workspace_root)
        absolute_target = os.path.abspath(os.path.join(absolute_cwd, raw_path))
        common = os.path.commonpath([absolute_root, absolute_target])
        if os.path.normcase(common) != os.path.normcase(absolute_root):
            return "<outside-workspace>"

        relative_path = os.path.relpath(absolute_target, absolute_root).replace("\\", "/")
        if SENSITIVE_RE.search(relative_path):
            return "<sensitive-path>"
        return relative_path
    except (OSError, ValueError):
        return "<outside-workspace>"


def normalize_event_name(event: Dict[str, object]) -> str:
    raw_name = (
        event.get("hook_event_name")
        or event.get("hook_event")
        or event.get("event")
    )
    if not isinstance(raw_name, str):
        return "unknown_event"
    return EVENT_NAMES.get(raw_name, "unknown_event")


def normalize_tool_name(tool_name: object) -> Optional[str]:
    if not isinstance(tool_name, str) or not TOOL_NAME_RE.fullmatch(tool_name):
        return None
    return tool_name


def action_for_tool(tool_name: Optional[str]) -> str:
    value = str(tool_name).lower() if tool_name is not None else ""
    if "write" in value or "create" in value:
        return "write"
    if "edit" in value or "replace" in value or "patch" in value or "modify" in value:
        return "edit"
    return "unknown"


def extract_records(
    event: Dict[str, object],
    client: str,
    workspace_root: str,
) -> List[Dict[str, object]]:
    tool_name = normalize_tool_name(
        event.get("tool_name") or event.get("tool") or event.get("name")
    )
    normalized_paths = [
        normalize_and_redact_path(path, event_cwd(event), workspace_root)
        for path in extract_paths(event)
    ] or [None]
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return [
        {
            "schema_version": 1,
            "timestamp": timestamp,
            "client": client,
            "event": normalize_event_name(event),
            "tool": tool_name,
            "path": path,
            "action": action_for_tool(tool_name),
        }
        for path in normalized_paths
    ]


def main(
    client: str = "unknown",
    log_dir: Optional[str] = None,
    workspace_root: Optional[str] = None,
) -> int:
    try:
        event = parse_event(sys.stdin.read())
        root = workspace_root or os.getcwd()
        records = extract_records(event, client, root)
        target_dir = log_dir or os.path.join(root, ".agent-logs")
        os.makedirs(target_dir, exist_ok=True)
        log_file = os.path.join(target_dir, "session.jsonl")
        with open(log_file, "a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
    except Exception:
        # Passive observability must never block the calling agent.
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
    parser.add_argument(
        "--log-dir",
        help="Override the log directory (used by the fixture harness).",
    )
    parser.add_argument(
        "--workspace-root",
        help="Repository root used for path bounding and relative log paths.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    sys.exit(main(arguments.client, arguments.log_dir, arguments.workspace_root))
