"""Reproduce audit observations without changing project/runtime configuration.

This is an audit probe, not a regression suite that requires defects to remain.
Exit zero means the probe ran; inspect observation values. All fixture writes
are confined to a newly allocated TemporaryDirectory. No network/model calls.
"""

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]


def main():
    compiler = runpy.run_path(str(ROOT / "scripts/ctx.py"))
    compile_context = compiler["compile_context"]
    hook_path = ROOT / "scripts/hooks/session-context.py"
    observations = {}
    with tempfile.TemporaryDirectory(prefix="template-continuity-audit-") as tmp:
        root = Path(tmp).resolve()
        bank = root / "memory-bank"
        records = bank / "records"
        records.mkdir(parents=True)
        record = records / "keep.md"
        record.write_text("---\nid: keep\ntype: decision\npriority: 1\n---\nKeep the accepted interface.\n", encoding="utf-8")
        handoff = bank / "handoff.md"
        handoff.write_text("---\nstatus: in progress\ntask: example\nnext_action: verify\n---\n", encoding="utf-8")
        result = compile_context(root, "codex", 6000)
        assert not result["malformed"] and not result["over_budget"]

        (bank / "decisions.md").write_text("# Decisions\nPRESERVE_OPTIONAL_EXAMPLE_482: an example is not a mandate.\n", encoding="utf-8")
        result = compile_context(root, "codex", 6000)
        observations["prose_decision_absent_from_projection"] = "PRESERVE_OPTIONAL_EXAMPLE_482" not in result["blob"]

        handoff.unlink()
        result = compile_context(root, "codex", 6000)
        observations["missing_handoff_accepted_without_diagnostic"] = not result["malformed"] and "## Status" not in result["blob"]

        handoff.write_text("# Handoff\nTask: example\nNext: check RESULT_429\n", encoding="utf-8")
        result = compile_context(root, "codex", 6000)
        observations["prose_handoff_accepted_but_status_omitted"] = not result["malformed"] and "RESULT_429" not in result["blob"]

        handoff.write_text("---\nstatus: in progress\nbranch: noncurrent-branch\nlast_touched: 2001-01-01\ntask: example\n---\n", encoding="utf-8")
        result = compile_context(root, "codex", 6000)
        observations["branch_and_freshness_not_validated"] = not result["malformed"] and "noncurrent-branch" not in result["blob"]

        handoff.write_text("---\nstatus: blocked\nblocking_issues: |\n  BLOCKER_DETAIL_913\n---\n", encoding="utf-8")
        result = compile_context(root, "codex", 6000)
        observations["multiline_blocker_accepted_but_detail_omitted"] = not result["malformed"] and "BLOCKER_DETAIL_913" not in result["blob"]

        handoff.write_text("---\nstatus: in progress\n---\n" + "x" * 20000, encoding="utf-8")
        result = compile_context(root, "codex", 6000)
        observations["handoff_exceeds_record_source_limit_without_rejection"] = handoff.stat().st_size > compiler["MAX_SOURCE_BYTES"] and not result["malformed"]

        handoff.write_text("---\nstatus: in progress\n---\n", encoding="utf-8")
        before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
        proc = subprocess.run([sys.executable, str(hook_path), "--event", "pre-compact", "--client", "claude", "--workspace-root", str(root)], input="{}", capture_output=True, text=True, encoding="utf-8")
        after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
        payload = json.loads(proc.stdout)
        observations["precompact_emits_reminder_without_persisting_files"] = proc.returncode == 0 and before == after and bool(payload["hookSpecificOutput"].get("additionalContext"))

        hook = runpy.run_path(str(hook_path))
        def fail_startup(*args):
            raise RuntimeError("synthetic compiler failure")
        hook["main"].__globals__["build_startup_context"] = fail_startup
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO("{}")), redirect_stdout(output):
            code = hook["main"]("session-start", str(root))
        observations["unexpected_startup_exception_exits_zero_silently"] = code == 0 and output.getvalue() == ""

        for i in range(50):
            (records / ("decision-{}.md".format(i))).write_text("---\nid: decision-{}\ntype: decision\npriority: 1\n---\n{}\n".format(i, "Preserve the approved behavior and its qualifications. " * 3), encoding="utf-8")
        result = compile_context(root, "codex", 6000)
        observations["fifty_durable_decisions_exceed_projection_budget"] = result["over_budget"]
        observations["over_budget_projected_chars"] = result["chars"]

        logger = runpy.run_path(str(ROOT / "scripts/hooks/log-writes.py"))
        event = {"session_id": "fixture-session", "hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": str(root), "tool_input": {"file_path": "example.md"}}
        logged = logger["extract_records"](event, "claude", str(root))
        observations["write_metadata_omits_session_identity"] = all("session_id" not in entry for entry in logged)

    inputs = ["scripts/ctx.py", "scripts/hooks/session-context.py", "scripts/hooks/log-writes.py"]
    print(json.dumps({"schema_version": 1, "kind": "audit_observations_not_acceptance_tests", "inputs_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs}, "observations": observations}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
