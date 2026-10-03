#!/usr/bin/env python3
"""Exercise the proposed compiler in isolation; do not patch the worktree."""
from __future__ import annotations
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
builder = runpy.run_path(str(HERE / "build-context-patch.py"))
assert (HERE / "context-integrity.patch").read_text(encoding="utf-8") == builder["diff"], "frozen patch differs from generated proposal"
namespace = {"__file__": str(builder["ROOT"] / "scripts/ctx.py"), "__name__": "proposal"}
exec(compile(builder["updated"], namespace["__file__"], "exec"), namespace)
namespace["run_self_test"]()
record = "---\nid: {id}\ntype: {type}\npriority: {priority}\nsuperseded_by: {target}\n---\n{body}\n"
checks = []
with tempfile.TemporaryDirectory(prefix="context-proposal-") as tmp:
    root = Path(tmp)
    records = root / "memory-bank/records"
    records.mkdir(parents=True)
    proposal = root / "ctx-proposed.py"
    proposal.write_text(builder["updated"], encoding="utf-8")
    for name, values, invalid in [
        ("duplicate", [("a", "risk", "1", "", "one"), ("a", "risk", "1", "", "two")], True),
        ("cycle", [("a", "risk", "1", "b", "one"), ("b", "risk", "1", "a", "two")], True),
        ("self", [("a", "risk", "1", "a", "one")], True),
        ("missing", [("a", "risk", "1", "missing", "one")], True),
        ("type-change", [("a", "decision", "1", "b", "one"), ("b", "fact", "1", "", "two")], True),
        ("unicode-priority", [("a", "risk", "¹", "", "one")], True),
        ("preserve-full-decision", [("a", "decision", "1", "", "x" * 401 + " NEVER PUBLISH")], False),
        ("bom-unicode", [("a", "risk", "1", "", "風險🙂")], False),
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
    assert namespace["compile_context"](root / "absent", "claude", 6000)["malformed"]
    checks.append("missing-root")
print(json.dumps({"proposal_checks_passed": checks, "total": len(checks)}))
