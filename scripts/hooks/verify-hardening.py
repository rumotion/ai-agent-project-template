#!/usr/bin/env python3
"""Regression replay of audited shell payloads without executing them."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/hooks" / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded
remote = module("remote_guard", "guard-remote-ops.py")
sensitive = module("sensitive_guard", "guard-sensitive-paths.py")
corpus = json.loads((ROOT / "scripts/hooks/fixtures/adversarial.json").read_text(encoding="utf-8"))
for case in corpus["remote"]:
    assert remote.is_blocked(case["command"]) == case["expected_block"], case["id"]
for case in corpus["sensitive"]:
    paths = sensitive.extract_paths({"tool_input": case["input"]})
    assert any(sensitive.is_sensitive(p) for p in paths) == case["expected_block"], case["id"]
for key in ("command", "cmd", "script", "CommandLine", "commandLine"):
    event = {"tool_input": {key: "git push"}}
    assert remote.is_blocked(remote.extract_command(event))
    paths = sensitive.extract_paths({"tool_input": {key: "echo demo > secret.key; echo done"}})
    assert any(sensitive.is_sensitive(p) for p in paths)
print("Adversarial guards: 24 remote and 12 sensitive cases plus payload aliases passed.")
