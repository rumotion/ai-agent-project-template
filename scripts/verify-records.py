"""Decision capture and task projection regressions on temporary records."""
import importlib.util
import json
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("records_compiler", HERE / "ctx.py")
ctx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctx)


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="record-projection-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / "memory-bank/records").mkdir(parents=True)
        self.handoff = self.root / "memory-bank/handoff.md"
        self.handoff.write_text("---\nstatus: working\ntask: example\nnext_action: verify\n---\n", encoding="utf-8")

    def store(self, rid="decision-one", body="For example, this option is optional.", **kwargs):
        return ctx.store_record(self.root, rid, "decision", body, source_ref="feedback-one", **kwargs)

    def test_record_has_readback_receipt_and_qualifier(self):
        receipt = self.store()
        self.assertTrue(receipt["stored"])
        self.assertTrue(receipt["included"])
        record = ctx.get_record(self.root, "decision-one")
        self.assertEqual(record["source_sha256"], receipt["source_sha256"])
        self.assertIn("option is optional", record["raw_body"])
        self.assertEqual(record["source_ref"], "feedback-one")
        validator = runpy.run_path(str(HERE / "validate-schemas.py"))
        schema = json.loads((HERE.parent / "schemas/context-record.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validator["schema_errors"](schema), [])
        self.assertEqual(validator["validate"](record, schema, "record"), [])

    def test_raw_body_preserves_code_indentation(self):
        self.store(body="    preserve_indent()\n    preserve_alternative()\n")
        self.assertTrue(ctx.get_record(self.root, "decision-one")["raw_body"].startswith("    preserve_indent"))

    def test_lock_and_failed_replace_preserve_existing_data(self):
        self.store()
        directory = self.root / "memory-bank/records"
        original = ctx.get_record(self.root, "decision-one")["source_sha256"]
        lock = directory / ".record-write.lock"
        lock.write_text("busy", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store("decision-two")
        lock.unlink()
        with patch.object(ctx.os, "replace", side_effect=OSError("synthetic")):
            with self.assertRaises(OSError):
                self.store("decision-two")
        self.assertFalse(lock.exists())
        self.assertFalse((directory / "decision-two.md").exists())
        self.assertEqual(ctx.get_record(self.root, "decision-one")["source_sha256"], original)

    def test_superseded_required_id_cannot_silently_change_meaning(self):
        self.store()
        self.store("decision-two", body="A new explicit decision.")
        path = self.root / "memory-bank/records/decision-one.md"
        path.write_text(path.read_text(encoding="utf-8").replace("priority: 1", "priority: 1\nsuperseded_by: decision-two"), encoding="utf-8")
        self.assertTrue(ctx.compile_context(self.root, "codex", 6000, required_ids=["decision-one"])["malformed"])
        self.assertIn("option is optional", ctx.get_record(self.root, "decision-one")["raw_body"])

    def test_over_budget_write_receipt_never_claims_inclusion_success(self):
        result = self.store(body="Keep this qualification. " * 300)
        self.assertTrue(result["stored"])
        self.assertEqual(result["projection_state"], "blocked")
        self.assertFalse(result["included"])
        self.assertTrue((self.root / result["path"]).is_file())

    def test_duplicate_id_does_not_overwrite(self):
        self.store()
        original = ctx.get_record(self.root, "decision-one")["source_sha256"]
        with self.assertRaises(ValueError):
            self.store(body="A conflicting new interpretation.")
        self.assertEqual(ctx.get_record(self.root, "decision-one")["source_sha256"], original)

    def test_capacity_refusal_preserves_archive(self):
        with patch.object(ctx, "MAX_RECORDS", 2, create=True):
            self.store("decision-one")
            self.store("decision-two")
            directory = self.root / "memory-bank/records"
            before = {path.name: path.read_bytes() for path in directory.glob("*.md")}
            with self.assertRaises(ValueError):
                self.store("decision-three")
            self.assertEqual(before, {path.name: path.read_bytes() for path in directory.glob("*.md")})
            self.assertIn("optional", ctx.get_record(self.root, "decision-one")["raw_body"])
            self.assertFalse(ctx.compile_context(self.root, "codex", 6000)["malformed"])

    def test_task_scope_is_explicit(self):
        self.store(scope="task", task_ids=["feature-a"])
        absent = ctx.compile_context(self.root, "codex", 6000, task_id="feature-b")
        present = ctx.compile_context(self.root, "codex", 6000, task_id="feature-a")
        self.assertNotIn("decision-one", absent["included"])
        self.assertIn("decision-one", absent["excluded"])
        self.assertIn("decision-one", present["included"])

    def test_task_switch_preserves_global_prefix(self):
        self.store("global-decision")
        self.store(scope="task", task_ids=["feature-a"])
        first = ctx.compile_context(self.root, "codex", 6000, task_id="feature-a")
        second = ctx.compile_context(self.root, "codex", 6000, task_id="feature-b")
        self.assertEqual(first["stable_prefix_sha256"], second["stable_prefix_sha256"])
        self.assertEqual(first["blob"][:first["stable_prefix_chars"]], second["blob"][:second["stable_prefix_chars"]])

    def test_required_archive_record_and_missing_id(self):
        self.store(scope="archive")
        result = ctx.compile_context(self.root, "codex", 6000, required_ids=["decision-one"])
        self.assertIn("decision-one", result["included"])
        self.assertTrue(ctx.compile_context(self.root, "codex", 6000, required_ids=["absent"])["malformed"])

    def test_handoff_binds_task_and_required_records(self):
        self.store(scope="task", task_ids=["feature-a"])
        self.handoff.write_text("---\nstatus: working\ntask: example\ntask_id: feature-a\nrequired_records: decision-one\nnext_action: verify\n---\n", encoding="utf-8")
        result = ctx.compile_context(self.root, "codex", 6000)
        self.assertEqual(result["task_id"], "feature-a")
        self.assertIn("decision-one", result["included"])

    def test_example_is_labeled_separately_from_decision(self):
        ctx.store_record(self.root, "example-one", "fact", "An example, not a mandate.", category="example", source_ref="feedback-one")
        result = ctx.compile_context(self.root, "codex", 6000)
        self.assertIn("[example", result["blob"])
        self.assertEqual(ctx.get_record(self.root, "example-one")["category"], "example")

    def test_required_fact_is_never_distilled(self):
        ctx.store_record(self.root, "fact-one", "fact", "Qualification. " * 50, source_ref="source-one", scope="archive")
        result = ctx.compile_context(self.root, "codex", 300, required_ids=["fact-one"])
        self.assertTrue(result["over_budget"])
        self.assertIn("fact-one", result["included"])

    def test_invalid_scope_category_and_source_are_rejected(self):
        for kwargs in ({"scope": "task"}, {"scope": "unknown"}, {"category": "example"}, {"scope": "global", "task_ids": ["feature-a"]}):
            with self.assertRaises(ValueError):
                self.store(**kwargs)
        with self.assertRaises(ValueError):
            ctx.store_record(self.root, "bad-source", "fact", "Body", source_ref="private/path")

    def test_thousand_record_archive_remains_retrievable(self):
        directory = self.root / "memory-bank/records"
        for i in range(1000):
            (directory / ("item-{}.md".format(i))).write_text("---\nid: item-{}\ntype: decision\npriority: 1\nscope: archive\n---\nPreserve historical qualification {}.\n".format(i, i), encoding="utf-8")
        self.store(scope="task", task_ids=["feature-a"])
        result = ctx.compile_context(self.root, "codex", 6000, task_id="feature-a")
        self.assertFalse(result["malformed"] or result["over_budget"])
        self.assertEqual(len(result["excluded"]), 1000)
        self.assertLessEqual(result["chars"], 6000)
        self.assertIn("qualification 999", ctx.get_record(self.root, "item-999")["raw_body"])

    def test_cross_process_record_and_projection(self):
        body = self.root / "feedback.txt"
        body.write_text("Keep this optional, including the alternative.\n", encoding="utf-8")
        command = [sys.executable, str(HERE / "ctx.py"), "record", "--root", str(self.root), "--id", "decision-one", "--type", "decision", "--source-ref", "feedback-one", "--body-file", str(body)]
        proc = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(json.loads(proc.stdout)["stored"])
        proc = subprocess.run([sys.executable, str(HERE / "ctx.py"), "compile", "--root", str(self.root), "--for", "claude", "--json"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("including the alternative", json.loads(proc.stdout)["blob"])


if __name__ == "__main__":
    unittest.main()
