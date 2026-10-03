"""Proposed scripts/push_backstop.py: explicit local-only accident prevention.

This is not a hostile-process security boundary. See boundary-hardening.md.
"""
from __future__ import annotations
import ast
from pathlib import Path
import subprocess

LOCAL_ONLY_HOOK = b'''#!/bin/sh
# Local-only accident prevention; an external sandbox enforces adversarial isolation.
echo "PUSH BLOCKED - this repository is local-only (AGENTS.md)." >&2
exit 1
'''


def git_value(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True,
                          text=True, encoding="utf-8", errors="strict")
    if proc.returncode:
        raise ValueError("cannot resolve repository hook configuration")
    return proc.stdout.strip()


def hook_path(root: Path) -> Path:
    root = root.resolve()
    # Refuse to mutate a user/global custom hook directory implicitly.
    custom = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                            cwd=root, capture_output=True)
    if custom.returncode not in (0, 1) or custom.stdout.strip():
        raise ValueError("custom core.hooksPath requires an explicit integration")
    value = Path(git_value(root, "rev-parse", "--git-path", "hooks/pre-push"))
    target = value if value.is_absolute() else root / value
    return target.resolve()


def strict_detach_hook(root: Path) -> bytes:
    # Read the trusted template's literal only; do not execute Python from disk.
    source = root / "scripts/detach-remote.py"
    if not source.is_file():
        return b""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "HOOK" for t in node.targets):
            value = ast.literal_eval(node.value)
            if isinstance(value, str):
                return value.encode("utf-8")
    return b""


def install(root: Path) -> Path:
    target = hook_path(root)
    if target.is_file():
        existing = target.read_bytes()
        approved = [LOCAL_ONLY_HOOK]
        detached = strict_detach_hook(root)
        if detached:
            approved.append(detached)
        if existing in approved:
            target.chmod(target.stat().st_mode | 0o111)
            return target
        raise ValueError("existing hook requires explicit review; it was preserved")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects an existing hook appearing after inspection.
    with target.open("xb") as handle:
        handle.write(LOCAL_ONLY_HOOK)
    target.chmod(0o755)
    if target.read_bytes() != LOCAL_ONLY_HOOK:
        raise ValueError("hook bytes differ after installation")
    return target
