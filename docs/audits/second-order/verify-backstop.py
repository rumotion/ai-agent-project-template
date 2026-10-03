#!/usr/bin/env python3
"""Verify proposed hook installation in disposable repositories."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("backstop", HERE / "push_backstop.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
passed = []
with tempfile.TemporaryDirectory(prefix="backstop-proposal-") as tmp:
    root = Path(tmp) / "repo"
    subprocess.run(["git", "init", str(root)], capture_output=True, check=True)
    hook = module.install(root)
    assert hook.read_bytes() == module.LOCAL_ONLY_HOOK and b"\r" not in hook.read_bytes()
    passed.append("LF-source")
    assert module.install(root) == hook
    passed.append("idempotent")
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
print(json.dumps({"proposal_backstop_checks_passed": passed, "POSIX_mode_runtime_verified": os.name != "nt"}))
