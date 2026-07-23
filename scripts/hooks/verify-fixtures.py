#!/usr/bin/env python3
"""Verify shared hook behavior with redacted native-client fixtures.

All generated logs are confined to an OS temporary directory. The harness
checks normalized records, redaction, malformed input, native denial shapes,
and fail-open behavior using only the Python standard library.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT / "scripts" / "hooks" / "fixtures"
LOG_WRITES_SCRIPT = ROOT / "scripts" / "hooks" / "log-writes.py"
GUARD_SCRIPT = ROOT / "scripts" / "hooks" / "guard-sensitive-paths.py"
LOG_KEYS = {
    "schema_version",
    "timestamp",
    "client",
    "event",
    "tool",
    "path",
    "action",
}
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
EXPECTED_WRITES = {
    "claude": ("Write", "src/app.py", "write"),
    "gemini": ("write_file", "src/main.rs", "write"),
    "codex": ("apply_patch", "docs/architecture.md", "edit"),
}


def fixture_text(client: str, kind: str) -> str:
    path = FIXTURES_DIR / "{}-{}.json".format(client, kind)
    assert path.is_file(), "Missing fixture {}".format(path)
    return path.read_text(encoding="utf-8")


def run_script(
    script_path: Path,
    payload: str,
    arguments: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    command = [sys.executable, str(script_path)]
    if arguments:
        command.extend(arguments)
    process = subprocess.run(
        command,
        input=payload,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    return process.returncode, process.stdout, process.stderr


def read_records(log_dir: str) -> List[Dict[str, object]]:
    log_file = Path(log_dir) / "session.jsonl"
    assert log_file.is_file(), "Logger did not create session.jsonl in temp dir"
    records = []
    for line in log_file.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        assert isinstance(value, dict), "Log line must be a JSON object"
        records.append(value)
    return records


def assert_record_shape(record: Dict[str, object], client: str) -> None:
    assert set(record) == LOG_KEYS, "Unexpected log fields: {}".format(set(record))
    assert record["schema_version"] == 1
    assert record["client"] == client
    assert isinstance(record["timestamp"], str)
    assert TIMESTAMP_RE.fullmatch(record["timestamp"])
    serialized = json.dumps(record)
    assert str(ROOT) not in serialized, "Absolute workspace path leaked"
    assert "SECRET=123" not in serialized, "Fixture file content leaked"


def test_log_writes() -> None:
    with tempfile.TemporaryDirectory() as log_dir:
        expected_count = 0
        for client, (tool, path, action) in EXPECTED_WRITES.items():
            code, stdout, stderr = run_script(
                LOG_WRITES_SCRIPT,
                fixture_text(client, "write"),
                [
                    "--client", client,
                    "--log-dir", log_dir,
                    "--workspace-root", str(ROOT),
                ],
            )
            assert code == 0 and not stdout and not stderr
            expected_count += 1
            records = read_records(log_dir)
            assert len(records) == expected_count
            record = records[-1]
            assert_record_shape(record, client)
            assert record["event"] == "post_tool_use"
            assert record["tool"] == tool
            assert record["path"] == path
            assert record["action"] == action

        for client in EXPECTED_WRITES:
            code, stdout, stderr = run_script(
                LOG_WRITES_SCRIPT,
                fixture_text(client, "sensitive"),
                [
                    "--client", client,
                    "--log-dir", log_dir,
                    "--workspace-root", str(ROOT),
                ],
            )
            assert code == 0 and not stdout and not stderr
            expected_count += 1
            record = read_records(log_dir)[-1]
            assert_record_shape(record, client)
            assert record["event"] == "pre_tool_use"
            assert record["path"] == "<sensitive-path>"

        for client in EXPECTED_WRITES:
            code, stdout, stderr = run_script(
                LOG_WRITES_SCRIPT,
                fixture_text(client, "malformed"),
                [
                    "--client", client,
                    "--log-dir", log_dir,
                    "--workspace-root", str(ROOT),
                ],
            )
            assert code == 0 and not stdout and not stderr
            expected_count += 1
            record = read_records(log_dir)[-1]
            assert_record_shape(record, client)
            assert record["event"] == "unknown_event"
            assert record["tool"] is None
            assert record["path"] is None
            assert record["action"] == "unknown"

        outside_path = Path(tempfile.gettempdir()).resolve() / "outside.py"
        outside_event = json.dumps(
            {
                "cwd": str(ROOT),
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": str(outside_path), "content": "<redacted>"},
            }
        )
        run_script(
            LOG_WRITES_SCRIPT,
            outside_event,
            [
                "--client", "claude",
                "--log-dir", log_dir,
                "--workspace-root", str(ROOT),
            ],
        )
        assert read_records(log_dir)[-1]["path"] == "<outside-workspace>"

        inside_event = json.dumps(
            {
                "cwd": str(ROOT),
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {
                    "file_path": str(ROOT / "src" / "absolute.py"),
                    "content": "<redacted>",
                },
            }
        )
        run_script(
            LOG_WRITES_SCRIPT,
            inside_event,
            [
                "--client", "claude",
                "--log-dir", log_dir,
                "--workspace-root", str(ROOT),
            ],
        )
        assert read_records(log_dir)[-1]["path"] == "src/absolute.py"

        subdirectory_event = json.dumps(
            {
                "cwd": str(ROOT / "src"),
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "../docs/from-subdirectory.md",
                    "content": "<redacted>",
                },
            }
        )
        run_script(
            LOG_WRITES_SCRIPT,
            subdirectory_event,
            [
                "--client", "claude",
                "--log-dir", log_dir,
                "--workspace-root", str(ROOT),
            ],
        )
        assert read_records(log_dir)[-1]["path"] == "docs/from-subdirectory.md"

        untrusted_metadata_event = json.dumps(
            {
                "cwd": str(ROOT),
                "hook_event_name": "arbitrary payload text",
                "tool_name": "tool name with payload text",
                "tool_input": {"file_path": "src/file.py\nembedded text"},
            }
        )
        run_script(
            LOG_WRITES_SCRIPT,
            untrusted_metadata_event,
            [
                "--client", "claude",
                "--log-dir", log_dir,
                "--workspace-root", str(ROOT),
            ],
        )
        record = read_records(log_dir)[-1]
        assert record["event"] == "unknown_event"
        assert record["tool"] is None
        assert record["path"] is None
        assert record["action"] == "unknown"


def expected_denial(client: str) -> Dict[str, object]:
    reason = "Access to a sensitive path is denied by repository policy."
    if client == "gemini":
        return {"decision": "deny", "reason": reason}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def test_guard_sensitive_paths() -> None:
    for client in EXPECTED_WRITES:
        payload = fixture_text(client, "sensitive")
        code, stdout, stderr = run_script(
            GUARD_SCRIPT,
            payload,
            ["--client", client],
        )
        assert code == 0 and not stderr
        assert json.loads(stdout) == expected_denial(client)
        assert ".env" not in stdout and ".key" not in stdout
        assert "credentials.json" not in stdout

        code, stdout, stderr = run_script(
            GUARD_SCRIPT,
            fixture_text(client, "write"),
            ["--client", client],
        )
        assert code == 0 and not stdout and not stderr

        code, stdout, stderr = run_script(
            GUARD_SCRIPT,
            fixture_text(client, "malformed"),
            ["--client", client],
        )
        assert code == 0 and not stdout and not stderr


def main() -> int:
    try:
        test_log_writes()
        print("PASS: log-writes.py normalized output, redaction, and fail-open cases")
        test_guard_sensitive_paths()
        print("PASS: guard-sensitive-paths.py native denial and safe-pass cases")
        print("All hook fixtures verified successfully.")
        return 0
    except AssertionError as error:
        print("FAIL: {}".format(error), file=sys.stderr)
        return 1
    except Exception as error:
        print("ERROR: Unexpected fixture failure: {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
