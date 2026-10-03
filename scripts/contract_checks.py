"""Portable envelope semantics beyond the closed JSON Schema dialect."""
from __future__ import annotations
import fnmatch
import json
from pathlib import Path, PurePosixPath
import re

MAX_ENVELOPE_BYTES = 64_000


def relative_path(value: str, root: Path = None, allow_glob: bool = False) -> str:
    if not isinstance(value, str) or not value or len(value) > 240:
        raise ValueError("path must be a nonempty bounded relative path")
    if any(c in value for c in "\\:\x00\r\n=") or value.startswith("/") or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("absolute paths, control characters and assignments are forbidden")
    parts = value.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise ValueError("path traversal or noncanonical path")
    if not allow_glob and any(c in value for c in "*?["):
        raise ValueError("concrete file paths required")
    if root is not None and not any(c in value for c in "*?["):
        base = root.resolve()
        resolved = (base / PurePosixPath(value)).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            raise ValueError("path escapes workspace through a symlink")
    return value


def matches(path: str, patterns) -> bool:
    # Compare Windows-style collision keys on every host for portability.
    return any(fnmatch.fnmatchcase(path.casefold(), pattern.casefold()) for pattern in patterns)


def allowed_write(path: str, task: dict, root: Path = None) -> bool:
    relative_path(path, root)
    if task["read_only"] or path.casefold().startswith("memory-bank/"):
        return False
    return matches(path, task["owned_paths"]) and not matches(path, task.get("forbidden_paths", []))


def task_errors(task: dict, root: Path = None) -> list:
    errors = []
    owned = task.get("owned_paths", [])
    if task.get("read_only") and owned:
        errors.append("read-only workers must have zero owned write paths")
    if not task.get("read_only") and not owned:
        errors.append("writers require owned paths")
    if task.get("isolation", {}).get("mask_secrets") is not True:
        errors.append("secret masking must be attested true")
    for key in ("owned_paths", "forbidden_paths", "inputs"):
        values = task.get(key, [])
        if len(set(v.casefold() for v in values)) != len(values):
            errors.append(key + ": duplicate or case-colliding paths")
        for path in values:
            try:
                relative_path(path, root, allow_glob=key != "inputs")
                if key == "owned_paths" and path.casefold().startswith("memory-bank/"):
                    raise ValueError("Memory Bank is parent-only")
                if key == "inputs" and root is not None and not (root / path).is_file():
                    raise ValueError("input file does not exist")
            except ValueError as error:
                errors.append(key + ": " + str(error))
    for path in owned:
        if path.casefold() in {p.casefold() for p in task.get("forbidden_paths", [])}:
            errors.append("a path cannot be both owned and forbidden")
    return errors


def result_errors(result: dict, task: dict = None, root: Path = None, output_tokens: int = None,
                  require_usage: bool = False) -> list:
    errors = []
    if len(result.get("summary", "").split()) > 120:
        errors.append("summary exceeds 120 words")
    encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    cap = MAX_ENVELOPE_BYTES
    if task is not None:
        cap = task["budget"].get("max_result_bytes", MAX_ENVELOPE_BYTES)
        if result.get("task_id") != task["task_id"]:
            errors.append("result task_id differs from dispatched task")
        if require_usage and output_tokens is None:
            errors.append("trusted output-token telemetry is required")
        if output_tokens is not None and (output_tokens < 0 or output_tokens > task["budget"]["max_output_tokens"]):
            errors.append("trusted output-token usage exceeds task budget")
    if len(encoded) > cap:
        errors.append("serialized result exceeds byte budget")
    for change in result.get("files_changed", []):
        try:
            relative_path(change["path"], root)
            if task is not None and not allowed_write(change["path"], task, root):
                errors.append("result declares an out-of-scope or forbidden write")
        except ValueError as error:
            errors.append("files_changed: " + str(error))
    if result.get("status") == "completed":
        verification = result.get("verification_run", [])
        if not verification or any(v["exit_code"] != 0 for v in verification):
            errors.append("completed results require successful verification evidence")
    return errors
