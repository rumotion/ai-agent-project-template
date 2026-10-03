#!/usr/bin/env python3
"""Adversarial schema, path and paired-result contract checks."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import tempfile
from contract_checks import task_errors, result_errors

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate-schemas.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
task_schema = module.load_json(ROOT / "schemas/subagent-task.schema.json")
result_schema = module.load_json(ROOT / "schemas/subagent-result.schema.json")
task = module.load_json(ROOT / "schemas/examples/task-valid.json")
result = module.load_json(ROOT / "schemas/examples/result-valid.json")
assert not module.validate(task, task_schema, "task") and not task_errors(task)
assert not module.validate(result, result_schema, "result") and not result_errors(result)
for value, schema in [("wrong", {"const": "right"}), (99.5, {"type": "number", "maximum": 1}),
                      (float("nan"), {"type": "number"}), ("x", {"oneOf": []}),
                      (1, {"type": "number", "maximum": "bad"}), (True, {"enum": [1]}), (1, {"type": ["number"]}),
                      (1, {"type": "number", "maximum": float("inf")})]:
    assert module.validate(value, schema, "case")
for edits in ({"owned_paths": ["../../outside"]}, {"inputs": ["bad\tpath"]}, {"inputs": ["SECRET_TEXT=demo"]},
              {"owned_paths": ["memory-bank/handoff.md"]},
              {"read_only": False, "owned_paths": ["src/a.py"], "forbidden_paths": ["src/a.py"]}):
    candidate = copy.deepcopy(task)
    candidate.update(edits)
    assert task_errors(candidate)
oversized = copy.deepcopy(result)
oversized["summary"] = "word " * 150
oversized["files_changed"] = [{"path": "x" * 10000, "action": "modified"}] * 50
assert module.validate(oversized, result_schema, "oversized")
assert result_errors(oversized)
writer = copy.deepcopy(task)
writer.update(read_only=False, owned_paths=["src/a.py"])
good = copy.deepcopy(result)
good["task_id"] = writer["task_id"]
good["files_changed"] = [{"path": "src/a.py", "action": "modified"}]
assert not result_errors(good, writer, output_tokens=10, require_usage=True)
assert result_errors(good, writer, require_usage=True)
assert result_errors(good, writer, output_tokens=writer["budget"]["max_output_tokens"]+1)
bad = copy.deepcopy(good)
bad["files_changed"][0]["path"] = "memory-bank/handoff.md"
assert result_errors(bad, writer)
bad = copy.deepcopy(good)
bad["task_id"] = "different"
assert result_errors(bad, writer)
byte_task = copy.deepcopy(writer)
byte_task["budget"]["max_result_bytes"] = 256
byte_result = copy.deepcopy(good)
byte_result["summary"] = "\U0001f642" * 300
assert not module.validate(byte_result, result_schema, "byte-case")
assert any("byte budget" in e for e in result_errors(byte_result, byte_task))
readonly = copy.deepcopy(task)
readonly.update(read_only=True, owned_paths=[])
assert not task_errors(readonly)
assert result_errors(good, readonly)
assert module.validate_examples() == []
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    for contents in ('{"a":1,"a":2}', '{"a":NaN}', '"' + 'x'*64001 + '"'):
        path = root / "bad.json"
        path.write_text(contents, encoding="utf-8")
        try:
            module.load_json(path)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid JSON accepted")
print("Contract dialect, path scopes, report caps, pairing and telemetry checks passed.")
