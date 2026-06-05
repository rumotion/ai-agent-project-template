#!/usr/bin/env python3
"""PostToolUse hook: passively log file-modifying tool calls.

Wired up in .claude/settings.json for the Write|Edit matcher. Claude Code passes
a JSON event on stdin; this script appends one compact JSON line per write to
.agent-logs/session.jsonl and exits 0. The log costs zero model tokens — an
offline consolidation step (see docs/hooks.md) can later fold it into the
Memory Bank.

Design rules:
- Standard library only (matches the template's zero-dependency philosophy).
- Never block the agent: any error is swallowed and the script still exits 0.
- Never log file *contents* — only paths and metadata.
"""

from __future__ import annotations

import datetime
import json
import os
import sys


def main() -> int:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        event = {}

    try:
        tool_input = event.get("tool_input", {}) or {}
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "session": event.get("session_id"),
            "event": event.get("hook_event_name") or event.get("hook_event"),
            "tool": event.get("tool_name"),
            "path": tool_input.get("file_path") or tool_input.get("path"),
        }
        log_dir = os.path.join(os.getcwd(), ".agent-logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "session.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        # Logging must never interrupt the session.
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
