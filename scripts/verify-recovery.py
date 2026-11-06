"""Integrated synthetic recovery scenarios; no native model/compaction claims."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import continuity
import tasks

HERE = Path(__file__).resolve().parent
ctx = continuity.compiler
NEXT = "Verify the sentinel acceptance case."


def make_fixture(base):
    """Only synthetic public facts; also reusable by an explicit native pilot."""
    root = Path(base).resolve() / "application"
    records = root / "memory-bank/records"
    records.mkdir(parents=True)
    (root / "AGENTS.md").write_text("Synthetic recovery fixture. Preserve evidence; review is not acceptance.\n", encoding="utf-8")
    handoff = root / "memory-bank/handoff.md"
    handoff.write_text("---\nstatus: in progress\ntask: recovery fixture\nnext_action: verify\n---\n", encoding="utf-8")
    (root / "application.py").write_text("sentinel = 'before'\n", encoding="utf-8")
    subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)], check=True)
    ctx.store_record(root, "decision-boundary", "decision", "Keep the existing API response shape.",
                     scope="task", task_ids=["restore-main"], source_ref="feedback-fixture")
    ctx.store_record(root, "example-violet", "fact", "Violet is an example, not an approved requirement.",
                     scope="task", task_ids=["restore-main"], category="example", source_ref="feedback-fixture")
    handoff.write_text("---\nstatus: in progress\ntask: recovery fixture\ntask_id: restore-main\nrequired_records: decision-boundary\nnext_action: " + NEXT + "\n---\n", encoding="utf-8")
    store = tasks.TaskStore(root, Path(base).resolve() / "private/tasks")
    def task(tid, owned):
        return {"task_id": tid, "objective": "Restore persisted work without inferring acceptance.", "owned_paths": [owned],
                "read_only": False, "inputs": ["application.py"], "expected_output": NEXT,
                "isolation": {"context_policy": "envelope-only", "mask_secrets": True, "memory_bank_writes": "parent-only"},
                "budget": {"max_turns": 10, "max_repairs": 2, "max_output_tokens": 1000}}
    store.create(task("restore-main", "application.py"))
    started = store.transition("restore-main", "start", 1)
    store.transition("restore-main", "note", started["revision"], next_action=NEXT)
    store.create(task("restore-next", "integration.py"), depends_on=["restore-main"])
    receipt = Path(base).resolve() / "private/checkpoint.json"
    continuity.checkpoint(root, "codex", "restore-main", ["application.py"], receipt)
    return root, store, receipt


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="integrated-recovery-")
        self.addCleanup(self.temp.cleanup)
        self.root, self.store, self.receipt = make_fixture(self.temp.name)

    def cli(self, script, *args):
        proc = subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        return json.loads(proc.stdout)

    def projection(self, client="codex"):
        return self.cli("ctx.py", "compile", "--root", self.root, "--for", client, "--json")

    def board(self):
        return self.cli("tasks.py", "--root", self.root, "--state-dir", self.store.directory, "list")["tasks"]

    def test_fresh_process_restores_decision_next_step_and_all_open_work(self):
        projected = self.projection()
        self.assertIn("Keep the existing API response shape.", projected["blob"])
        self.assertIn("example", projected["blob"])
        self.assertIn("not an approved requirement", projected["blob"])
        board = {item["task_id"]: item for item in self.board()}
        self.assertEqual(set(board), {"restore-main", "restore-next"})
        self.assertEqual(board["restore-main"]["next_action"], NEXT)
        self.assertEqual(board["restore-main"]["state"], "running")
        doctor = self.cli("continuity.py", "--root", self.root, "doctor", "--mode", "resume", "--receipt", self.receipt)
        self.assertEqual(doctor["status"], "ready")
        self.assertEqual(doctor["native_delivery"], "unknown")

    def test_repeated_synthetic_context_loss_uses_persisted_state(self):
        # New compiler/ledger processes, not native client compaction.
        hashes = []
        for cycle in range(5):
            projected = self.projection()
            hashes.append(projected["blob_sha256"])
            self.assertEqual(len(self.board()), 2)
        self.assertEqual(len(set(hashes)), 1)

    def test_client_renderer_switch_preserves_required_facts(self):
        for client in ("codex", "claude", "gemini"):
            projected = self.projection(client)
            self.assertIn("decision-boundary", projected["blob"])
            self.assertIn(NEXT, projected["blob"])
            self.assertFalse(projected["malformed"])
            self.assertEqual(continuity.doctor(self.root, client, "resume", self.receipt)["native_delivery"], "unknown")

    def test_interrupted_review_stays_unaccepted_and_dependency_waits(self):
        (self.root / "application.py").write_text("sentinel = 'after'\n", encoding="utf-8")
        value = self.store.read("restore-main")
        result = {"task_id": "restore-main", "status": "completed", "summary": "Synthetic fixture check.",
                  "files_changed": [{"path": "application.py", "action": "modified"}],
                  "verification_run": [{"command": "synthetic fixture check", "exit_code": 0}], "tokens_used": 0}
        self.store.transition("restore-main", "submit", value["revision"], attempt_id=value["attempt_id"], result=result)
        continuity.checkpoint(self.root, "codex", "restore-main", ["application.py"], self.receipt)
        board = {item["task_id"]: item for item in self.board()}
        self.assertEqual(board["restore-main"]["state"], "review")
        self.assertEqual(continuity.doctor(self.root, "claude", "resume", self.receipt)["status"], "ready")
        with self.assertRaises(ValueError):
            tasks.TaskStore(self.root, self.store.directory).transition("restore-next", "start", 1)

    def test_superseded_required_decision_blocks_instead_of_replacing_meaning(self):
        ctx.store_record(self.root, "decision-new", "decision", "Change only after separate approval.",
                         scope="task", task_ids=["restore-main"], source_ref="feedback-fixture")
        path = self.root / "memory-bank/records/decision-boundary.md"
        path.write_text(path.read_text(encoding="utf-8").replace("priority: 1", "priority: 1\nsuperseded_by: decision-new"), encoding="utf-8")
        projected = ctx.compile_context(self.root, "codex", 6000)
        self.assertTrue(projected["malformed"])
        self.assertEqual(continuity.doctor(self.root, "codex", "resume", self.receipt)["status"], "blocked")
        self.assertIn("existing API", ctx.get_record(self.root, "decision-boundary")["raw_body"])

    def test_corrupted_receipt_preserves_open_tasks(self):
        self.receipt.write_text("{", encoding="utf-8")
        self.assertEqual(continuity.doctor(self.root, "codex", "resume", self.receipt)["status"], "blocked")
        self.assertEqual({item["state"] for item in self.board()}, {"running", "queued"})

    def test_missing_receipt_or_result_never_infers_completion(self):
        self.receipt.unlink()
        self.assertEqual(continuity.doctor(self.root, "codex", "resume", self.receipt)["status"], "blocked")
        self.assertEqual(continuity.doctor(self.root, "codex", "legacy", self.receipt)["status"], "degraded")
        (self.root / "application.py").write_text("sentinel = 'apparently done'\n", encoding="utf-8")
        self.assertEqual(self.board()[0]["state"], "running")


if __name__ == "__main__":
    unittest.main()
