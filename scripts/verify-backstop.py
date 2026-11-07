#!/usr/bin/env python3
"""Verify local-only hook installation in disposable repositories."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("backstop", HERE / "push_backstop.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
bootstrap_spec = importlib.util.spec_from_file_location("bootstrap", HERE / "new-project.py")
bootstrap = importlib.util.module_from_spec(bootstrap_spec)
bootstrap_spec.loader.exec_module(bootstrap)
passed = []
with tempfile.TemporaryDirectory(prefix="backstop-proposal-") as tmp:
    root = Path(tmp) / "repo"
    subprocess.run(["git", "init", str(root)], capture_output=True, check=True)
    hook = module.install(root)
    assert hook.read_bytes() == module.LOCAL_ONLY_HOOK and b"\r" not in hook.read_bytes()
    passed.append("LF-source")
    assert module.install(root) == hook
    passed.append("idempotent")
    nested = root / "nested-project"
    nested.mkdir()
    try:
        module.install(nested)
    except ValueError:
        passed.append("nested-project-root-rejected")
    else:
        raise AssertionError("nested project modified parent repository hook")
    shell = shutil.which("sh")
    if not shell and os.name == "nt":
        git_exec = subprocess.run(["git", "--exec-path"], capture_output=True, text=True, check=True).stdout.strip()
        candidate = Path(git_exec).parents[2] / "bin/sh.exe"
        if candidate.is_file():
            shell = str(candidate)
    assert shell, "POSIX shell required to verify the Git hook runtime"
    for label, overrides in [("clean", {}), ("agent", {"CLAUDECODE": "1"}),
                             ("override", {"ALLOW_AGENT_PUSH": "1"})]:
        environment = os.environ.copy()
        for key in ("CLAUDECODE", "ALLOW_AGENT_PUSH", "AGENT"):
            environment.pop(key, None)
        environment.update(overrides)
        proc = subprocess.run([shell, str(hook)], env=environment, capture_output=True)
        assert proc.returncode == 1 and b"PUSH BLOCKED" in proc.stderr, label
        passed.append(label + "-runtime-denied")
    if os.name != "nt":
        hook.chmod(0o644)
        module.install(root)
        assert hook.stat().st_mode & 0o111
        passed.append("POSIX-executable-mode-repaired")
    for name, data in [("CRLF", module.LOCAL_ONLY_HOOK.replace(b"\n", b"\r\n")),
                       ("permissive", b"#!/bin/sh\nexit 0\n"), ("empty", b"")]:
        hook.write_bytes(data)
        try:
            module.install(root)
        except ValueError:
            pass
        else:
            raise AssertionError(name + " hook was silently accepted")
        assert hook.read_bytes() == data
        passed.append(name + "-conflict-preserved")
    subprocess.run(["git", "config", "core.hooksPath", "custom-hooks"], cwd=root, capture_output=True, check=True)
    try:
        module.install(root)
    except ValueError:
        passed.append("custom-hooksPath-explicit-failure")
    else:
        raise AssertionError("custom hooksPath silently accepted")
    subprocess.run(["git", "config", "--unset", "core.hooksPath"], cwd=root, capture_output=True, check=True)
    hook.unlink()
    (root / "fixture.txt").write_text("fixture", encoding="utf-8")
    subprocess.run(["git", "add", "fixture.txt"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "commit", "-m", "fixture"], cwd=root, capture_output=True, check=True)
    worktree = Path(tmp) / "worktree"
    subprocess.run(["git", "worktree", "add", "-b", "fixture-worktree", str(worktree)], cwd=root, capture_output=True, check=True)
    assert (worktree / ".git").is_file()
    assert module.install(worktree) == hook.resolve()
    passed.append("linked-worktree")
    # A failed index update must be reported before attempting a misleading commit.
    ok = SimpleNamespace(returncode=0, stdout="", stderr="")
    failed_add = SimpleNamespace(returncode=1, stdout="", stderr="synthetic add failure")
    failed_commit = SimpleNamespace(returncode=1, stdout="nothing staged", stderr="")
    with patch.object(bootstrap.subprocess, "run", side_effect=[ok, failed_add, failed_commit]) as runner:
        failure = bootstrap.git_init(root, False)
        assert failure.startswith("git add failed:"), failure
        assert runner.call_count == 2, "Commit attempted after failed add"
    passed.append("bootstrap-add-failure-is-explicit")
    deep = Path(tmp) / "bootstrap project [case]"
    deep.resolve().relative_to(Path(tmp).resolve())
    data = deep / ("nested-" + "a" * 70) / ("nested-" + "b" * 70) / ("nested-" + "c" * 70) / "fixture.txt"
    data.parent.mkdir(parents=True)
    data.write_text("synthetic long-path fixture\n", encoding="utf-8")
    identity = {"GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.com",
                "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.com"}
    with patch.dict(os.environ, identity):
        assert bootstrap.git_init(deep, False) is None
    tracked = subprocess.check_output(["git", "ls-files"], cwd=deep).decode().splitlines()
    assert data.relative_to(deep).as_posix() in tracked
    assert not subprocess.check_output(["git", "remote", "-v"], cwd=deep).strip()
    if os.name == "nt":
        assert subprocess.check_output(["git", "config", "--local", "--get", "core.longpaths"], cwd=deep).strip() == b"true"
    passed.append("bootstrap-long-path-local-repository")
print(json.dumps({"backstop_checks_passed": passed, "POSIX_mode_runtime_verified": os.name != "nt"}))
