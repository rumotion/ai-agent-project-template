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
REMOTE_GUARD_SCRIPT = ROOT / "scripts" / "hooks" / "guard-remote-ops.py"
SESSION_CONTEXT_SCRIPT = ROOT / "scripts" / "hooks" / "session-context.py"
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

    # Shell redirection writes to sensitive paths must be denied too
    # (audit hardening: write-tool-only checks were a bypass).
    shell_denials = [
        'echo "SECRET=1" > .env',
        "cat id_rsa.txt >> server.key",
        "tee -a .env",
        "cp leaked.txt backup.pem",
        "mv token.txt token.json",
        'echo "K=v" > ".env"',
    ]
    for command in shell_denials:
        code, stdout, stderr = run_script(
            GUARD_SCRIPT,
            json.dumps({"tool_name": "Bash", "tool_input": {"command": command}}),
            ["--client", "claude"],
        )
        assert code == 0 and "deny" in stdout, "shell write not denied: " + command
        assert ".env" not in stdout and ".key" not in stdout

    # Ordinary shell output files must pass through.
    shell_safe = [
        "git diff > notes.md",
        "echo done > build.log",
        "cp src/main.py backup/",
        "python run.py > out.txt",
    ]
    for command in shell_safe:
        code, stdout, stderr = run_script(
            GUARD_SCRIPT,
            json.dumps({"tool_name": "Bash", "tool_input": {"command": command}}),
            ["--client", "claude"],
        )
        assert code == 0 and not stdout, "false positive: " + command


def expected_remote_denial(client: str) -> Dict[str, object]:
    reason = (
        "Publishing is denied by repository policy (AGENTS.md -> Repository "
        "boundaries). Pushing, remote changes, and PR/repo creation require an "
        "explicit human instruction in the current conversation. Commit locally "
        "instead, then ask."
    )
    if client == "gemini":
        return {"decision": "deny", "reason": reason}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def test_guard_remote_ops() -> None:
    for client in EXPECTED_WRITES:
        # A push must be denied in the client's native shape.
        code, stdout, stderr = run_script(
            REMOTE_GUARD_SCRIPT, fixture_text(client, "push"), ["--client", client]
        )
        assert code == 0 and not stderr
        assert json.loads(stdout) == expected_remote_denial(client)
        # The denial must not echo the command or a remote URL.
        assert "origin" not in stdout and "git push" not in stdout

        # Read-only git work that merely mentions "push" must pass through.
        code, stdout, stderr = run_script(
            REMOTE_GUARD_SCRIPT, fixture_text(client, "shell-safe"), ["--client", client]
        )
        assert code == 0 and not stdout and not stderr, "false positive on safe shell command"

        # Malformed input fails open.
        code, stdout, stderr = run_script(
            REMOTE_GUARD_SCRIPT, fixture_text(client, "malformed"), ["--client", client]
        )
        assert code == 0 and not stdout and not stderr


    # Regression: heredoc bodies are data. Writing a commit message or document
    # that merely mentions "git push" must not be denied, but a real command on
    # the heredoc-invoking line must still be caught.
    heredoc_safe = "\n".join(
        [
            "git commit -F - <<'MSG'",
            "fix: block git push",
            "- git push / remote add is denied",
            "MSG",
        ]
    )
    code, stdout, stderr = run_script(
        REMOTE_GUARD_SCRIPT,
        json.dumps({"tool_name": "Bash", "tool_input": {"command": heredoc_safe}}),
        ["--client", "claude"],
    )
    assert code == 0 and not stdout and not stderr, "heredoc body must not be parsed as a command"

    heredoc_blocked = "\n".join(["git push origin main <<'EOF'", "notes", "EOF"])
    code, stdout, stderr = run_script(
        REMOTE_GUARD_SCRIPT,
        json.dumps({"tool_name": "Bash", "tool_input": {"command": heredoc_blocked}}),
        ["--client", "claude"],
    )
    assert code == 0 and "deny" in stdout, "command on the heredoc-invoking line must be caught"

    # Adversarial indirection must still be denied (audit hardening, 2026-10).
    bypass_denials = [
        "git send-pack origin main",                         # plumbing push
        "sh -c 'git push origin main'",                       # interpreter wrapper
        'bash -c "git push origin main"',
        "echo $(git push origin main)",                      # command substitution
        "`git push origin main`",                             # backtick substitution
        "xargs git push",                                     # wrapper indirection
        "env git push origin main",
        "gh api repos/o/r -X POST",                           # raw API publishing
        "gh secret set AWS_SECRET_ACCESS_KEY",                # secret transmission
        "git config remote.origin.url https://host/x.git",    # config remote repoint
        "python -c \"import subprocess; subprocess.run(['git','push'])\"",
        'echo "$(git push origin main)"',                  # substitution in double quotes
    ]
    for command in bypass_denials:
        code, stdout, stderr = run_script(
            REMOTE_GUARD_SCRIPT,
            json.dumps({"tool_name": "Bash", "tool_input": {"command": command}}),
            ["--client", "claude"],
        )
        assert code == 0 and "deny" in stdout, "bypass not denied: " + command

    # Safe commands that merely mention publishing words must still pass.
    safe_mentions = [
        'git" "push origin main',
        'python -c "print(\'git push\')"',
        "git config --get remote.origin.url",
        "sh -c 'echo never run git push'",
        "git commit -m \"docs: explain why git push is blocked\"",
        "echo 'see gh secret set docs'",
        "python -c \"print('hello')\"",
        "gh api repos/o/r",                              # GET, no write method/field
        "git config user.name demo",                     # harmless config key
        "git commit -m \"docs; git push\"",              # quoted `;` is data
    ]
    for command in safe_mentions:
        code, stdout, stderr = run_script(
            REMOTE_GUARD_SCRIPT,
            json.dumps({"tool_name": "Bash", "tool_input": {"command": command}}),
            ["--client", "claude"],
        )
        assert code == 0 and not stdout, "false positive: " + command


def test_session_context() -> None:
    startup = '{"hook_event_name": "SessionStart", "source": "startup", "cwd": "."}'
    code, stdout, stderr = run_script(
        SESSION_CONTEXT_SCRIPT,
        startup,
        ["--event", "session-start", "--client", "claude",
         "--workspace-root", str(ROOT)],
    )
    assert code == 0 and not stderr
    payload = json.loads(stdout)["hookSpecificOutput"]
    assert payload["hookEventName"] == "SessionStart"
    assert "memory-bank/startup.md" in payload["additionalContext"]

    # Resuming additionally injects the cross-model handoff pointer.
    resume = '{"hook_event_name": "SessionStart", "source": "resume", "cwd": "."}'
    code, stdout, stderr = run_script(
        SESSION_CONTEXT_SCRIPT,
        resume,
        ["--event", "session-start", "--client", "claude",
         "--workspace-root", str(ROOT)],
    )
    assert code == 0 and not stderr
    assert "memory-bank/handoff.md" in json.loads(stdout)["hookSpecificOutput"]["additionalContext"]

    # Pre-compact emits the Memory Bank flush notice.
    code, stdout, stderr = run_script(
        SESSION_CONTEXT_SCRIPT, "{}", ["--event", "pre-compact", "--client", "claude"]
    )
    assert code == 0 and not stderr
    assert "handoff.md" in json.loads(stdout)["hookSpecificOutput"]["additionalContext"]

    # Never blocks, even on garbage.
    for bad in ("", "not json", '{"tool_input": null}'):
        code, _, stderr = run_script(
            SESSION_CONTEXT_SCRIPT, bad, ["--event", "session-start", "--client", "claude"]
        )
        assert code == 0 and not stderr


def main() -> int:
    try:
        test_log_writes()
        print("PASS: log-writes.py normalized output, redaction, and fail-open cases")
        test_guard_sensitive_paths()
        print("PASS: guard-sensitive-paths.py native denial and safe-pass cases")
        test_guard_remote_ops()
        print("PASS: guard-remote-ops.py publishing denial and safe-pass cases")
        test_session_context()
        print("PASS: session-context.py startup/resume/pre-compact injection")
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
