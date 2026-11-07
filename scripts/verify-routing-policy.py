"""Behavioral routing/receipt/CLI checks; no native model or network calls."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import routing_policy as policy


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.event_counter = 0

    def observation(self, **changes):
        value = {"schema_version": 1, "task_id": "task", "task_revision": 1, "attempt_id": "attempt-one",
                 "artifact_sha256": "a" * 64, "checkpoint": "routine", "material": True,
                 "permission": "allowed", "evidence_current": True, "model_available": True,
                 "advisor_available": True, "budget": "unknown", "hard_budget": False,
                 "verification": "unknown", "retry_count": 0, "errors": []}
        if "advisor_receipt" in changes:
            changes["advisor_receipts"] = [changes.pop("advisor_receipt")]
        value.update(changes)
        return value

    def error(self, kind="logic", signature="b", **changes):
        self.event_counter += 1
        value = {"task_id": "task", "task_revision": 1, "attempt_id": "attempt-one", "event_id": "event-" + str(self.event_counter), "kind": kind, "signature": signature * 64}
        value.update(changes)
        return value

    def receipt(self, checkpoint="completion", **changes):
        value = {"task_id": "task", "task_revision": 1, "attempt_id": "attempt-one", "artifact_sha256": "a" * 64,
                 "checkpoint": checkpoint, "verdict": "accept"}
        if checkpoint == "error":
            value["error_count"] = 2
            value["error_event_id"] = "event-2"
        value.update(changes)
        return value

    def test_routine_worker_has_no_authority(self):
        result = policy.decide(self.observation())
        self.assertEqual(result["route"], "worker")
        for key in ("authorizes_action", "dispatch_performed", "acceptance_performed"):
            self.assertFalse(result[key])

    def test_plan_and_completion_require_advice_without_model_request(self):
        for checkpoint in ("plan", "completion"):
            self.assertEqual(policy.decide(self.observation(checkpoint=checkpoint))["route"], "advisor")

    def test_two_same_logic_errors_escalate(self):
        self.assertEqual(policy.decide(self.observation(errors=[self.error()]))["route"], "worker")
        result = policy.decide(self.observation(errors=[self.error(), self.error()]))
        self.assertEqual((result["route"], result["reason"]), ("advisor", "error_review_required"))

    def test_other_errors_tasks_attempts_do_not_make_a_repeat(self):
        for other in (self.error(signature="c"), self.error(task_id="other"), self.error(attempt_id="old")):
            self.assertEqual(policy.decide(self.observation(errors=[other, self.error()]))["route"], "worker")

    def test_transient_retries_are_bounded_and_not_escalated(self):
        for count in range(3):
            self.assertEqual(policy.decide(self.observation(errors=[self.error("transient")], retry_count=count))["route"], "retry")
        self.assertEqual(policy.decide(self.observation(errors=[self.error("transient")], retry_count=3))["route"], "hold")

    def test_permission_and_stale_state_override_escalation(self):
        for changes in ({"permission": "denied"}, {"permission": "unknown"}, {"evidence_current": False},
                        {"model_available": False}, {"budget": "hold"}, {"budget": "unknown", "hard_budget": True}):
            self.assertEqual(policy.decide(self.observation(checkpoint="completion", **changes))["route"], "hold")

    def test_native_permission_denial_never_retries(self):
        self.assertEqual(policy.decide(self.observation(errors=[self.error("permission")]))["reason"], "permission_denial")

    def test_missing_advisor_holds_required_review(self):
        self.assertEqual(policy.decide(self.observation(checkpoint="plan", advisor_available=False))["route"], "hold")

    def test_current_receipt_releases_only_to_parent_review(self):
        value = self.observation(checkpoint="completion", verification="passed", advisor_available=False,
                                 advisor_receipt=self.receipt())
        self.assertEqual(policy.decide(value)["route"], "parent_review")
        self.assertFalse(policy.decide(value)["acceptance_performed"])

    def test_receipt_never_replaces_tests(self):
        for verification in ("failed", "unknown"):
            self.assertEqual(policy.decide(self.observation(checkpoint="completion", verification=verification,
                advisor_receipt=self.receipt()))["reason"], "verification_required")

    def test_stale_or_other_checkpoint_receipts_do_not_release(self):
        for changes in ({"task_id": "other"}, {"attempt_id": "old"}, {"artifact_sha256": "c" * 64}, {"checkpoint": "plan"}):
            self.assertEqual(policy.decide(self.observation(checkpoint="completion", advisor_receipt=self.receipt(**changes)))["route"], "advisor")

    def test_error_receipt_needs_matching_signature(self):
        value = self.observation(errors=[self.error(), self.error()], advisor_receipt=self.receipt("error", error_signature="c" * 64))
        self.assertEqual(policy.decide(value)["route"], "advisor")
        value["advisor_receipts"][0]["error_signature"] = "b" * 64
        self.assertEqual(policy.decide(value)["route"], "worker")

    def test_revise_routes_to_worker(self):
        self.assertEqual(policy.decide(self.observation(checkpoint="plan", advisor_receipt=self.receipt("plan", verdict="revise")))["reason"], "apply_advisor_findings")

    def test_new_failure_invalidates_previous_error_review(self):
        value = self.observation(errors=[self.error() for _ in range(3)],
                                 advisor_receipts=[self.receipt("error", error_signature="b" * 64, error_count=2)])
        self.assertEqual(policy.decide(value)["route"], "advisor")

    def test_error_review_does_not_replace_completion_review(self):
        value = self.observation(checkpoint="completion", verification="passed", errors=[self.error() for _ in range(2)],
                                 advisor_receipts=[self.receipt("error", error_signature="b" * 64, error_count=2)])
        self.assertEqual(policy.decide(value)["reason"], "completion_review_required")

    def test_changed_task_revision_invalidates_review(self):
        value = self.observation(checkpoint="completion", task_revision=2,
                                 advisor_receipts=[self.receipt(task_revision=1)])
        self.assertEqual(policy.decide(value)["route"], "advisor")

    def test_duplicate_events_are_not_two_failures(self):
        event = self.error()
        with self.assertRaises(ValueError):
            policy.decide(self.observation(errors=[event, event]))

    def test_bounded_history_replacement_invalidates_old_review(self):
        errors = [self.error() for _ in range(33)]
        value = self.observation(errors=errors[-32:], advisor_receipts=[
            self.receipt("error", error_signature="b" * 64, error_count=32, error_event_id="event-32")])
        self.assertEqual(policy.decide(value)["route"], "advisor")

    def test_both_error_and_completion_reviews_are_needed(self):
        value = self.observation(checkpoint="completion", verification="passed", errors=[self.error(), self.error()],
            advisor_receipts=[self.receipt("error", error_signature="b" * 64), self.receipt()])
        self.assertEqual(policy.decide(value)["route"], "parent_review")

    def test_model_request_is_additional_not_sole_trigger(self):
        self.assertEqual(policy.decide(self.observation(advisor_requested=True))["route"], "advisor")

    def test_trivial_completion_still_needs_tests(self):
        self.assertEqual(policy.decide(self.observation(checkpoint="completion", material=False))["route"], "worker")
        self.assertEqual(policy.decide(self.observation(checkpoint="completion", material=False, verification="passed"))["route"], "parent_review")

    def test_invalid_shapes_never_get_a_route(self):
        for changes in ({"schema_version": True}, {"retry_count": True}, {"material": 1}, {"errors": [self.error()] * 33},
                        {"command": "secret-marker"}, {"artifact_sha256": "missing"}, {"checkpoint": []}):
            with self.assertRaises((ValueError, TypeError)):
                policy.decide(self.observation(**changes))

    def test_cli_duplicate_and_oversized_inputs_are_redacted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            for raw in ('{"secret":"private-marker","secret":1}', 'x' * (policy.MAX_BYTES + 1), '[' * 1200 + ']' * 1200):
                path.write_text(raw, encoding="utf-8")
                result = subprocess.run([sys.executable, str(Path(policy.__file__)), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["reason"], "invalid_observation")
                self.assertNotIn("private-marker", result.stdout + result.stderr)

    def test_input_is_not_mutated_and_cli_valid(self):
        value = self.observation();before = copy.deepcopy(value)
        policy.decide(value);self.assertEqual(value, before)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.json";path.write_text(json.dumps(value), encoding="utf-8")
            result = subprocess.run([sys.executable, str(Path(policy.__file__)), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["route"], "worker")


if __name__ == "__main__":
    unittest.main(verbosity=2)
