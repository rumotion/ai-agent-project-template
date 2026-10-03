#!/usr/bin/env python3
"""Inject validated typed context; remind the parent to persist before compaction.

Lifecycle injection is best-effort and never blocks a session. Invalid or
oversized projections emit a diagnostic rather than truncated source records.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import importlib.util
from typing import Dict, Optional


MAX_TOTAL_CHARS = 8_000

PRE_COMPACT_NOTICE = (
    "Context is about to be compacted. Before continuing, persist anything "
    "durable that only exists in this transcript:\n"
    "1. Update memory-bank/handoff.md (status, next_action, files_modified, "
    "blocking_issues).\n"
    "2. Append any phase summary / refuted hypotheses to "
    "memory-bank/activeContext.md.\n"
    "3. Record new decisions in memory-bank/decisions.md and new risks in "
    "memory-bank/risks.md.\n"
    "Treat the checked-in Memory Bank, not this transcript, as the source of "
    "truth after compaction."
)


def parse_event(raw_input: str) -> Dict[str, object]:
    if not raw_input or not raw_input.strip():
        return {}
    try:
        data = json.loads(raw_input)
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def resolve_root(event: Dict[str, object], override: Optional[str]) -> Path:
    if override:
        return Path(override)
    for key in ("cwd", "workspace_root", "project_dir"):
        value = event.get(key)
        if isinstance(value, str) and value:
            return Path(value)
    # scripts/hooks/<file> -> repository root
    return Path(__file__).resolve().parents[2]


def build_startup_context(root: Path, source: str) -> str:
    # Import the trusted hook's sibling compiler, never code from event.cwd.
    script = Path(__file__).resolve().parents[1] / "ctx.py"
    spec = importlib.util.spec_from_file_location("context_compiler", script)
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    result = compiler.compile_context(root, "claude", compiler.DEFAULT_MAX_CHARS)
    if result["malformed"] or result["over_budget"]:
        return "Compiled context is invalid. Run scripts/ctx.py compile --for claude --check before using Memory Bank context."
    note = "Sources: memory-bank/records/ and memory-bank/handoff.md; replaces repeated memory-bank/startup.md reads."
    context = result["blob"] + "\n" + note
    if len(context) > MAX_TOTAL_CHARS:
        return "Compiled context exceeds injection budget; run the context validator."
    return context


def emit(event_name: str, context: str) -> None:
    if not context:
        return
    payload = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }
    }
    sys.stdout.write(json.dumps(payload, sort_keys=True) + "\n")


def main(event_kind: str, root_override: Optional[str]) -> int:
    try:
        event = parse_event(sys.stdin.read())
        root = resolve_root(event, root_override)

        if event_kind == "session-start":
            source = event.get("source")
            source = source.lower() if isinstance(source, str) else "startup"
            emit("SessionStart", build_startup_context(root, source))
        else:
            emit("PreCompact", PRE_COMPACT_NOTICE)
    except Exception:
        # Context injection is best-effort and must never break a session.
        pass
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event",
        choices=("session-start", "pre-compact"),
        required=True,
        help="Which lifecycle role this invocation serves.",
    )
    parser.add_argument(
        "--client",
        choices=("claude", "codex", "gemini", "unknown"),
        default="unknown",
        help="Native hook adapter supplying the event.",
    )
    parser.add_argument(
        "--workspace-root",
        dest="workspace_root",
        default=None,
        help="Explicit repository root; falls back to the event payload.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    sys.exit(main(arguments.event, arguments.workspace_root))
