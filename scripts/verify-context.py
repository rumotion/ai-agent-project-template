#!/usr/bin/env python3
"""Exercise production compiler integrity in isolated temporary workspaces."""
from __future__ import annotations
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
import importlib.util
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location("context_compiler", ROOT / "scripts/ctx.py")
loaded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loaded)
namespace = vars(loaded)
namespace["run_self_test"]()
record = "---\nid: {id}\ntype: {type}\npriority: {priority}\nsuperseded_by: {target}\n---\n{body}\n"
checks = []
with tempfile.TemporaryDirectory(prefix="context-proposal-") as tmp:
    root = Path(tmp)
    records = root / "memory-bank/records"
    records.mkdir(parents=True)
    proposal = root / "ctx-proposed.py"
    proposal.write_text((ROOT / "scripts/ctx.py").read_text(encoding="utf-8"), encoding="utf-8")
    for name, values, invalid in [
        ("duplicate", [("a", "risk", "1", "", "one"), ("a", "risk", "1", "", "two")], True),
        ("cycle", [("a", "risk", "1", "b", "one"), ("b", "risk", "1", "a", "two")], True),
        ("self", [("a", "risk", "1", "a", "one")], True),
        ("missing", [("a", "risk", "1", "missing", "one")], True),
        ("type-change", [("a", "decision", "1", "b", "one"), ("b", "fact", "1", "", "two")], True),
        ("unicode-priority", [("a", "risk", "Р’в„–", "", "one")], True),
        ("preserve-full-decision", [("a", "decision", "1", "", "x" * 401 + " NEVER PUBLISH")], False),
        ("bom-unicode", [("a", "risk", "1", "", "Р№СћРЃР№С™Р„СЂСџв„ўвЂљ")], False),
        ("protected-over-budget", [("a", "decision", "1", "", "x" * 7000)], True),
    ]:
        for path in records.glob("*.md"):
            path.unlink()
        for i, (rid, kind, priority, target, body) in enumerate(values):
            text = record.format(id=rid, type=kind, priority=priority, target=target, body=body)
            if name == "bom-unicode":
                text = "\ufeff" + text
            (records / (str(i) + ".md")).write_text(text, encoding="utf-8")
        result = namespace["compile_context"](root, "claude", 6000)
        assert bool(result["malformed"] or result["over_budget"]) == invalid, name
        if name == "preserve-full-decision":
            assert "NEVER PUBLISH" in result["blob"]
        proc = subprocess.run([sys.executable, str(proposal), "compile", "--root", str(root), "--for", "claude"], capture_output=True, text=True, encoding="utf-8")
        assert proc.returncode == (1 if invalid else 0), name
        if invalid:
            assert not proc.stdout, name
        checks.append(name)
    for path in records.glob("*.md"):
        path.unlink()
    for name, content in [("duplicate-key", "---\nid: a\ntype: decision\ntype: fact\npriority: 1\n---\nbody"), ("empty-front-matter", "---\n---\nbody")]:
        (records / "0.md").write_text(content, encoding="utf-8")
        assert namespace["compile_context"](root, "claude", 6000)["malformed"], name
        checks.append(name)
    (records / "0.md").write_text(record.format(id="a", type="risk", priority="1", target="", body="risk"), encoding="utf-8")
    (root / "memory-bank/handoff.md").write_text("\ufeff---\nstatus: blocked\nblocking_issues: critical\n---\n", encoding="utf-8")
    assert namespace["load_handoff_status"](root)["status"] == "blocked"
    checks.append("bom-handoff")
    first = namespace["compile_context"](root, "claude", 6000)
    (root / "memory-bank/handoff.md").write_text("---\nstatus: new task\n---\n", encoding="utf-8")
    second = namespace["compile_context"](root, "claude", 6000)
    assert first["stable_prefix_sha256"] == second["stable_prefix_sha256"]
    assert first["blob"][:first["stable_prefix_chars"]] == second["blob"][:second["stable_prefix_chars"]]
    checks.append("stable-prefix-across-status-change")
    for client in namespace["CLIENT_NOTES"]:
        result = namespace["compile_context"](root, client, 6000)
        assert not result["malformed"] and not result["over_budget"], client
        (root / "memory-bank/handoff.md").write_text("---\nstatus: changed for " + client + "\n---\n", encoding="utf-8")
        changed = namespace["compile_context"](root, client, 6000)
        assert result["stable_prefix_sha256"] == changed["stable_prefix_sha256"], client
        assert "risk" in changed["blob"], client
        proc = subprocess.run([sys.executable, str(proposal), "compile", "--root", str(root),
                               "--for", client, "--json"], capture_output=True, text=True, encoding="utf-8")
        assert proc.returncode == 0 and json.loads(proc.stdout)["client"] == client
    checks.append("all-client-renderers")
    assert namespace["compile_context"](root / "absent", "claude", 6000)["malformed"]
    checks.append("missing-root")
print(json.dumps({"integrity_checks_passed": checks, "total": len(checks)}))
