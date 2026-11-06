"""Behavioral restoration checks; only disposable local fixtures are mutated."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
import re
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import continuity


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="continuity-check-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / "project"
        self.records = self.root / "memory-bank/records"
        self.records.mkdir(parents=True)
        (self.root / "AGENTS.md").write_text("Project rules.\n", encoding="utf-8")
        self.handoff = self.root / "memory-bank/handoff.md"
        self.handoff.write_text("---\nstatus: in progress\ntask: example\nnext_action: verify\n---\n", encoding="utf-8")
        (self.records / "decision.md").write_text("---\nid: decision\ntype: decision\npriority: 1\n---\nAn example is optional.\n", encoding="utf-8")
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(self.root)], check=True)
        self.receipt = self.base / "private/receipt.json"

    def doctor(self, mode="resume"):
        return continuity.doctor(self.root, "codex", mode, self.receipt)

    def checkpoint(self, inputs=()):
        return continuity.checkpoint(self.root, "codex", "example", list(inputs), self.receipt)

    def test_fresh_and_legacy_are_distinct(self):
        self.assertEqual(self.doctor("fresh")["status"], "ready")
        self.assertEqual(self.doctor("legacy")["status"], "degraded")
        self.assertEqual(self.doctor()["status"], "blocked")

    def test_cross_client_resume_and_revision(self):
        self.assertEqual(self.checkpoint()["revision"], 1)
        self.assertEqual(self.doctor()["status"], "ready")
        self.assertEqual(continuity.doctor(self.root, "claude", "resume", self.receipt)["status"], "ready")
        self.assertEqual(self.checkpoint()["revision"], 2)
        self.assertEqual(self.doctor()["native_delivery"], "unknown")

    def test_receipt_schema_and_large_binary_input(self):
        source = self.root / "asset.bin"
        source.write_bytes(b"\xff" * 20000)
        receipt = self.checkpoint(["asset.bin"])
        schema = json.loads((HERE.parent / "schemas/continuity-receipt.schema.json").read_text(encoding="utf-8"))
        validator = runpy.run_path(str(HERE / "validate-schemas.py"))
        self.assertEqual(validator["schema_errors"](schema), [])
        self.assertEqual(validator["validate"](receipt, schema, "receipt"), [])
        self.assertEqual(self.doctor()["status"], "ready")
        source.write_bytes(source.read_bytes() + b"x")
        self.assertEqual(self.doctor()["status"], "blocked")

    def test_changed_dirty_input_invalidates_receipt(self):
        path = self.root / "application.py"
        path.write_text("version one\n", encoding="utf-8")
        self.checkpoint(["application.py"])
        path.write_text("version two\n", encoding="utf-8")
        self.assertEqual(self.doctor()["status"], "blocked")

    def test_changed_record_or_handoff_invalidates_receipt(self):
        for path in (self.handoff, self.records / "decision.md"):
            before = path.read_bytes()
            self.checkpoint()
            path.write_bytes(before + b"Changed.\n")
            self.assertEqual(self.doctor()["status"], "blocked")
            path.write_bytes(before)

    def test_branch_mismatch(self):
        self.checkpoint()
        subprocess.run(["git", "symbolic-ref", "HEAD", "refs/heads/other"], cwd=self.root, check=True)
        self.assertEqual(self.doctor()["status"], "blocked")

    def test_missing_prose_and_multiline_handoff(self):
        self.handoff.unlink()
        self.assertEqual(self.doctor("fresh")["status"], "ready")
        self.assertEqual(self.doctor()["status"], "blocked")
        for content in ("# Handoff\nNo structured status\n", "---\nstatus: blocked\nblocking_issues: |\n  missing evidence\n---\n"):
            self.handoff.write_text(content, encoding="utf-8")
            self.assertEqual(self.doctor("legacy")["status"], "blocked")

    def test_handoff_size_encoding_and_duplicate_fields(self):
        for content in (b"---\nstatus: ok\n---\n" + b"x" * 20000, b"\xff", b"---\nstatus: one\nstatus: two\n---\n"):
            self.handoff.write_bytes(content)
            self.assertEqual(self.doctor("legacy")["status"], "blocked")

    def test_incomplete_handoff_cannot_checkpoint(self):
        self.handoff.write_text("---\nstatus: working\n---\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.checkpoint()
        self.assertFalse(self.receipt.exists())

    def test_collection_cannot_describe_required_handoff_fields(self):
        for sentinel in ("{}", "[]", '""', "''"):
            self.handoff.write_text("---\nstatus: {0}\ntask: {0}\nnext_action: {0}\n---\n".format(sentinel), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.checkpoint()

    def test_interleaved_handoff_edit_is_not_certified(self):
        original = continuity.source_digest
        def interleaved(*args):
            self.handoff.write_text("---\nstatus: working\n---\n", encoding="utf-8")
            return original(*args)
        with patch.object(continuity, "source_digest", side_effect=interleaved):
            with self.assertRaises(ValueError):
                self.checkpoint()
        self.assertFalse(self.receipt.exists())

    def test_resume_independently_requires_complete_handoff(self):
        self.checkpoint()
        self.handoff.write_text("---\nstatus: working\n---\n", encoding="utf-8")
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        receipt["source_sha256"] = continuity.source_digest(self.root, [])
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        self.assertEqual(self.doctor()["status"], "blocked")

    def test_tampered_wrong_project_and_future_receipt(self):
        self.checkpoint()
        original = self.receipt.read_text(encoding="utf-8")
        for key, value in (("project_id", "0" * 64), ("created_at", "2999-01-01T00:00:00+00:00"), ("revision", True), ("inputs", ["../outside"])):
            data = json.loads(original)
            data[key] = value
            self.receipt.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(self.doctor()["status"], "blocked")

    def test_lock_refusal_and_atomic_failure(self):
        self.checkpoint()
        original = self.receipt.read_bytes()
        lock = self.receipt.with_suffix(".lock")
        lock.write_text("another writer", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.checkpoint()
        self.assertEqual(self.receipt.read_bytes(), original)
        lock.unlink()
        with patch.object(continuity.os, "replace", side_effect=OSError("synthetic failure")):
            with self.assertRaises(OSError):
                self.checkpoint()
        self.assertEqual(self.receipt.read_bytes(), original)
        self.assertFalse(lock.exists())

    def test_private_storage_and_sensitive_inputs(self):
        with self.assertRaises(ValueError):
            continuity.checkpoint(self.root, "codex", "example", [], self.root / "receipt.json")
        for path in ("../outside", ".env", "nested/token.json", "missing.py"):
            with self.assertRaises((ValueError, OSError)):
                self.checkpoint([path])

    def test_cli_diagnostics_are_redacted(self):
        proc = subprocess.run([sys.executable, str(HERE / "continuity.py"), "--root", str(self.root), "doctor", "--mode", "resume", "--receipt", str(self.receipt)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        output = json.loads(proc.stdout)
        self.assertEqual(output["status"], "blocked")
        self.assertNotIn(str(self.base), proc.stdout)

    def test_hook_unexpected_failure_is_visible(self):
        spec = importlib.util.spec_from_file_location("hook_under_test", HERE / "hooks/session-context.py")
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)
        output = io.StringIO()
        with patch.object(hook, "build_startup_context", side_effect=RuntimeError("private detail")), patch("sys.stdin", io.StringIO("{}")), redirect_stdout(output):
            self.assertEqual(hook.main("session-start", str(self.root)), 0)
        payload = json.loads(output.getvalue())
        self.assertIn("continuity_unavailable", json.dumps(payload))
        self.assertNotIn("private detail", output.getvalue())

    def test_lifecycle_hook_uses_requested_renderer(self):
        for client in ("claude", "codex", "gemini", "unknown"):
            proc = subprocess.run([sys.executable, str(HERE / "hooks/session-context.py"),
                                   "--event", "session-start", "--client", client,
                                   "--workspace-root", str(self.root)],
                                  input="{}", capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
            expected = client if client != "unknown" else "generic"
            self.assertIn(continuity.compiler.CLIENT_NOTES[expected], context)
            self.assertLessEqual(len(context), 8000)

    def test_codex_hook_example_covers_startup_boundaries(self):
        config = json.loads((HERE.parent / ".codex/hooks.example.json").read_text(encoding="utf-8"))
        groups = config["hooks"].get("SessionStart", [])
        self.assertEqual(len(groups), 1)
        for source in ("startup", "resume", "clear", "compact", "fork"):
            self.assertIsNotNone(re.search(groups[0]["matcher"], source))
        hook = groups[0]["hooks"][0]
        self.assertEqual(hook["additionalContextLimit"], 0)
        self.assertFalse(hook.get("async", False))
        for name in ("command", "commandWindows"):
            self.assertIn("--event session-start", hook[name])
            self.assertIn("--client codex", hook[name])
            self.assertIn("--workspace-root", hook[name])

    def test_codex_invalid_context_diagnostic_uses_codex_command(self):
        (self.root / "memory-bank/handoff.md").write_text("---\ninvalid\n---\n", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(HERE / "hooks/session-context.py"),
                               "--event", "session-start", "--client", "codex",
                               "--workspace-root", str(self.root)],
                              input="{}", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("--for codex --check", context)
        self.assertNotIn("--for claude", context)

    def test_malformed_hook_event_never_loads_fallback_project(self):
        for raw in ("not json", "null", "[]"):
            proc = subprocess.run([sys.executable, str(HERE / "hooks/session-context.py"), "--event", "session-start", "--client", "claude"], input=raw, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("continuity_unavailable", proc.stdout)
            self.assertNotIn("## Decisions", proc.stdout)


if __name__ == "__main__":
    unittest.main()
