"""Cooperative task lifecycle, restart, stale evidence and preservation checks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="task-ledger-")
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.root = base / "application"
        self.root.mkdir()
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(self.root)], check=True)
        self.file = self.root / "application.py"
        self.file.write_text("old dirty content\n", encoding="utf-8")
        self.directory = base / "private/tasks"
        self.store = tasks.TaskStore(self.root, self.directory)

    def task(self, tid="feature", owned=None):
        return {"task_id": tid, "objective": "Verify application behavior", "owned_paths": owned or ["application.py"],
                "read_only": False, "inputs": ["application.py"],
                "isolation": {"context_policy": "envelope-only", "mask_secrets": True, "memory_bank_writes": "parent-only"},
                "budget": {"max_turns": 10, "max_repairs": 2, "max_output_tokens": 1000}}

    def result(self, tid="feature", changes=None):
        return {"task_id": tid, "status": "completed", "summary": "Synthetic fixture verification.",
                "files_changed": changes if changes is not None else [{"path": "application.py", "action": "modified"}],
                "verification_run": [{"command": "synthetic fixture check", "exit_code": 0, "output_summary": "passed"}],
                "tokens_used": 0}

    def start(self, tid="feature", deps=(), owned=None):
        self.store.create(self.task(tid, owned), depends_on=deps)
        return self.store.transition(tid, "start", 1)

    def submit(self, started, tid="feature", result=None):
        self.file.write_text("new content\n", encoding="utf-8")
        return self.store.transition(tid, "submit", started["revision"], attempt_id=started["attempt_id"], result=result or self.result(tid))

    def test_restart_and_parent_acceptance(self):
        started = self.start()
        review = self.submit(started)
        self.store = tasks.TaskStore(self.root, self.directory)
        self.assertEqual(self.store.read("feature")["state"], "review")
        accepted = self.store.transition("feature", "accept", review["revision"], attempt_id=review["attempt_id"], verification=self.result())
        self.assertEqual(accepted["state"], "accepted")
        schema = json.loads((Path(tasks.__file__).resolve().parent.parent / "schemas/task-state.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(tasks.validator.schema_errors(schema), [])
        self.assertEqual(tasks.validator.validate(self.store.read("feature"), schema, "state"), [])

    def test_submission_is_not_acceptance(self):
        started = self.start()
        self.submit(started)
        self.assertEqual(self.store.read("feature")["state"], "review")

    def test_checkpoint_note_survives_restart(self):
        started = self.start()
        noted = self.store.transition("feature", "note", started["revision"], next_action="Verify the remaining error path.")
        restarted = tasks.TaskStore(self.root, self.directory)
        self.assertEqual(restarted.read("feature")["next_action"], "Verify the remaining error path.")
        self.assertEqual(noted["state"], "running")

    def test_empty_optional_output_uses_objective(self):
        task = self.task()
        task["expected_output"] = " "
        self.store.create(task)
        self.assertEqual(self.store.read("feature")["next_action"], task["objective"])

    def test_stale_revision_and_attempt(self):
        started = self.start()
        for kwargs in ({"revision": 1, "attempt_id": started["attempt_id"]}, {"revision": 2, "attempt_id": "0" * 32}):
            with self.assertRaises(ValueError):
                self.store.transition("feature", "submit", result=self.result(), **kwargs)

    def test_changed_review_cannot_be_accepted(self):
        started = self.start()
        review = self.submit(started)
        self.file.write_text("changed during review\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.transition("feature", "accept", review["revision"], attempt_id=review["attempt_id"], verification=self.result())
        self.assertEqual(self.store.read("feature")["state"], "review")

    def test_unreported_or_out_of_scope_write_is_preserved(self):
        started = self.start()
        outside = self.root / "unowned.py"
        outside.write_text("preserve user work\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.submit(started)
        self.assertEqual(outside.read_text(encoding="utf-8"), "preserve user work\n")
        self.assertEqual(self.store.read("feature")["state"], "running")

    def test_declared_changes_must_match_actual_dirty_delta(self):
        started = self.start()
        with self.assertRaises(ValueError):
            self.submit(started, result=self.result(changes=[]))

    def test_explicit_ignored_input_is_still_audited(self):
        (self.root / ".gitignore").write_text("dependency.txt\n", encoding="utf-8")
        source = self.root / "dependency.txt"
        source.write_text("before\n", encoding="utf-8")
        task = self.task()
        task["inputs"].append("dependency.txt")
        self.store.create(task)
        started = self.store.transition("feature", "start", 1)
        source.write_text("changed dependency\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.submit(started)

    def test_dependency_release_requires_parent_acceptance(self):
        started = self.start()
        review = self.submit(started)
        self.store.create(self.task("dependent"), depends_on=["feature"])
        with self.assertRaises(ValueError):
            self.store.transition("dependent", "start", 1)
        self.store.transition("feature", "accept", review["revision"], attempt_id=review["attempt_id"], verification=self.result())
        self.assertEqual(self.store.transition("dependent", "start", 1)["state"], "running")

    def test_ownership_and_running_limit(self):
        self.start()
        self.store.create(self.task("second"))
        with self.assertRaises(ValueError):
            self.store.transition("second", "start", 1)

    def test_queued_block_cannot_bypass_open_capacity(self):
        for index in range(3):
            self.store.create(self.task("task-" + str(index), ["file-" + str(index)]))
        for index in range(2):
            self.store.transition("task-" + str(index), "block", 1)
        before = self.store.read("task-2")
        with self.assertRaises(ValueError):
            self.store.transition("task-2", "block", 1)
        self.assertEqual(self.store.read("task-2"), before)
        self.assertEqual(self.file.read_text(encoding="utf-8"), "old dirty content\n")

    def test_queued_block_cannot_bypass_ownership(self):
        self.start()
        self.store.create(self.task("second"))
        before = self.store.read("second")
        with self.assertRaises(ValueError):
            self.store.transition("second", "block", 1)
        self.assertEqual(self.store.read("second"), before)

    def test_stop_reconciliation_and_late_result(self):
        started = self.start()
        with self.assertRaises(ValueError):
            self.store.transition("feature", "block", 2, attempt_id=started["attempt_id"])
        blocked = self.store.transition("feature", "block", 2, attempt_id=started["attempt_id"], stopped=True)
        resumed = self.store.transition("feature", "start", blocked["revision"], stopped=True)
        self.assertNotEqual(started["attempt_id"], resumed["attempt_id"])
        with self.assertRaises(ValueError):
            self.store.transition("feature", "submit", resumed["revision"], attempt_id=started["attempt_id"], result=self.result())

    def test_failed_atomic_save_preserves_task(self):
        self.store.create(self.task())
        before = self.store.read("feature")
        with patch.object(tasks.os, "replace", side_effect=OSError("synthetic failure")):
            with self.assertRaises(OSError):
                self.store.transition("feature", "start", 1)
        self.assertEqual(self.store.read("feature"), before)

    def test_state_failure_after_baseline_preserves_authoritative_task(self):
        self.store.create(self.task())
        before = self.store.read("feature")
        replace = tasks.os.replace
        def fail_state(source, target):
            if str(target).endswith(".task.json"):
                raise OSError("synthetic state publication failure")
            return replace(source, target)
        with patch.object(tasks.os, "replace", side_effect=fail_state):
            with self.assertRaises(OSError):
                self.store.transition("feature", "start", 1)
        self.assertEqual(self.store.read("feature"), before)
        self.assertEqual(len(list(self.directory.glob("*.inventory.json"))), 1)

    def test_cycle_and_private_storage_refusal(self):
        with self.assertRaises(ValueError):
            tasks.TaskStore(self.root, self.root / "state")
        self.store.create(self.task())
        self.store.create(self.task("second"), depends_on=["feature"])
        value = self.store.read("feature")
        value["depends_on"] = ["second"]
        (self.directory / "feature.task.json").write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.all()

    def test_corrupt_terminal_state_cannot_claim_acceptance(self):
        self.store.create(self.task())
        value = self.store.read("feature")
        value["state"] = "accepted"
        (self.directory / "feature.task.json").write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.read("feature")

    def test_capacity_refusal_and_owner_conflict_preserve_state(self):
        self.store.create(self.task())
        before = self.store.read("feature")
        with patch.object(tasks, "MAX_TASKS", 1):
            with self.assertRaises(ValueError):
                self.store.create(self.task("second"))
        with self.assertRaises(ValueError):
            self.store.transition("feature", "start", 1, owner="another-owner")
        self.assertEqual(before, self.store.read("feature"))

    def test_deletion_and_addition_are_audited(self):
        started = self.start(owned=["application.py", "new.py"])
        self.file.unlink()
        (self.root / "new.py").write_text("new content\n", encoding="utf-8")
        result = self.result(changes=[{"path": "application.py", "action": "deleted"}, {"path": "new.py", "action": "added"}])
        review = self.store.transition("feature", "submit", started["revision"], attempt_id=started["attempt_id"], result=result)
        self.assertEqual(self.store.transition("feature", "accept", review["revision"], attempt_id=review["attempt_id"], verification=result)["state"], "accepted")

    def test_failed_verification_and_duplicate_identity(self):
        started = self.start()
        with self.assertRaises(ValueError):
            self.store.create(self.task())
        candidate = self.result()
        candidate["verification_run"][0]["exit_code"] = 1
        with self.assertRaises(ValueError):
            self.submit(started, result=candidate)

    def test_bounded_listing_cross_process(self):
        self.store.create(self.task())
        proc = subprocess.run([sys.executable, str(Path(tasks.__file__)), "--root", str(self.root), "--state-dir", str(self.directory), "list"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["tasks"][0]["task_id"], "feature")
        self.assertNotIn(str(self.root), proc.stdout)


if __name__ == "__main__":
    unittest.main()
