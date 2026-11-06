"""Offline cost/progress semantics and hard-budget refusal regressions."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import unittest

import task_metrics as metrics

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("benchmark_metrics", HERE / "benchmark-context.py")
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 6, 12, tzinfo=timezone.utc)

    def sample(self, actor="lead", role="main", **kwargs):
        value = {"actor": actor, "role": role, "segment": "segment-one", "scope": "task", "source": "synthetic",
                 "started_at": (self.now - timedelta(minutes=2)).isoformat(), "observed_at": self.now.isoformat(),
                 "model": None, "effort": None, "counters": {name: 2 for name in metrics.COUNTERS},
                 "tokens": {"input_tokens": 100, "output_tokens": 20, "thought_tokens": 10, "cached_tokens": 40, "thought_in_output": True}}
        value.update(kwargs)
        return value

    def data(self, samples=None, **kwargs):
        data = {"task_id": "feature", "observed_at": self.now.isoformat(), "elapsed_seconds": 120,
                "completed": False, "actors": {"lead": "main"}, "snapshots": samples if samples is not None else [self.sample()]}
        data.update(kwargs)
        return data

    def report(self, data):
        return metrics.report(data, self.now)

    def test_reasoning_and_cache_are_not_added_twice(self):
        result = self.report(self.data())
        self.assertEqual(result["totals"]["total_tokens"], 120)
        self.assertTrue(result["unknown_model_or_effort"])
        self.assertFalse(result["pacing_activated"])

    def test_unknown_is_not_zero(self):
        sample = self.sample(tokens={})
        result = self.report(self.data([sample]))
        self.assertIsNone(result["totals"]["total_tokens"])
        self.assertIsNone(self.report(self.data([]))["totals"]["tool_calls"])

    def test_cumulative_snapshots_count_only_latest(self):
        old = self.sample(observed_at=(self.now-timedelta(minutes=1)).isoformat())
        new = self.sample()
        new["tokens"]["input_tokens"] = 150
        result = self.report(self.data([old, new]))
        self.assertEqual(result["totals"]["total_tokens"], 170)

    def test_main_and_multiple_workers_count_once(self):
        data = self.data([self.sample(), self.sample("one", "worker"), self.sample("two", "worker")],
                         actors={"lead": "main", "one": "worker", "two": "worker"})
        result = self.report(data)
        self.assertEqual(result["totals"]["total_tokens"], 360)
        self.assertEqual(result["by_role"]["worker"]["total_tokens"], 240)
        self.assertEqual(result["totals"]["elapsed_seconds"], 120)

    def test_missing_worker_makes_aggregate_unknown(self):
        result = self.report(self.data(actors={"lead": "main", "worker": "worker"}))
        self.assertIsNone(result["totals"]["total_tokens"])
        self.assertIn("missing_actor_measurements", result["gaps"])

    def test_account_session_or_stale_data_is_not_task_cost(self):
        for scope in ("account", "session"):
            self.assertIsNone(self.report(self.data([self.sample(scope=scope)]))["totals"]["total_tokens"])
        old = self.sample(started_at=(self.now-timedelta(hours=1)).isoformat(), observed_at=(self.now-timedelta(minutes=11)).isoformat())
        self.assertIsNone(self.report(self.data([old]))["totals"]["total_tokens"])

    def test_resets_and_model_changes_require_nonoverlapping_segment(self):
        old = self.sample(observed_at=(self.now-timedelta(minutes=1)).isoformat())
        new = self.sample(model="model-changed")
        with self.assertRaises(ValueError):
            self.report(self.data([old, new]))
        new["segment"], new["started_at"] = "segment-two", old["observed_at"]
        self.assertEqual(self.report(self.data([old, new]))["totals"]["total_tokens"], 240)
        reopened = self.sample(observed_at=(self.now+timedelta(seconds=1)).isoformat())
        with self.assertRaises(ValueError):
            self.report(self.data([old, new, reopened], observed_at=reopened["observed_at"]))

    def test_decreasing_counters_need_reset_segment(self):
        old = self.sample(observed_at=(self.now-timedelta(minutes=1)).isoformat())
        new = self.sample()
        new["counters"]["tool_calls"] = 1
        with self.assertRaises(ValueError):
            self.report(self.data([old, new]))

    def test_unknown_cannot_hide_counter_or_token_reset(self):
        for section in ("counters", "tokens"):
            for missing in (True, False):
                with self.subTest(section=section, omitted=missing):
                    old = self.sample(observed_at=(self.now-timedelta(seconds=90)).isoformat())
                    mid = self.sample(observed_at=(self.now-timedelta(seconds=30)).isoformat())
                    new = self.sample()
                    if section == "counters":
                        old[section]["tool_calls"] = 100
                        mid[section] = {} if missing else {"tool_calls": None}
                        limit = {"tool_calls": 10}
                    else:
                        mid[section] = {} if missing else {key: None for key in ("input_tokens", "output_tokens", "thought_tokens", "cached_tokens")}
                        mid[section]["thought_in_output"] = True
                        new[section].update(input_tokens=2, cached_tokens=0)
                        limit = {"total_tokens": 30}
                    with self.assertRaises(ValueError):
                        self.report(self.data([old, mid, new], limits=limit, remaining={key: 1 for key in limit}))

    def test_latest_unknown_stays_unknown_after_known_reading(self):
        old = self.sample(observed_at=(self.now-timedelta(minutes=1)).isoformat())
        new = self.sample(counters={}, tokens={"thought_in_output": True})
        result = self.report(self.data([old, new], limits={"tool_calls": 10}, remaining={"tool_calls": 1}))
        self.assertIsNone(result["totals"]["tool_calls"])
        self.assertIsNone(result["totals"]["total_tokens"])
        self.assertEqual(result["action"], "hold")

    def test_closed_segment_remains_valid_but_is_immutable(self):
        old = self.sample(started_at=(self.now-timedelta(hours=1)).isoformat(),
                          observed_at=(self.now-timedelta(minutes=30)).isoformat(), closed=True)
        self.assertEqual(self.report(self.data([old]))["totals"]["total_tokens"], 120)
        with self.assertRaises(ValueError):
            self.report(self.data([old, self.sample(started_at=old["started_at"])]))

    def test_stale_progress_and_configured_context_threshold(self):
        stale = self.data([], observed_at=(self.now-timedelta(minutes=11)).isoformat())
        self.assertEqual(self.report(stale)["action"], "hold")
        data = self.data(context={"used_tokens": 75, "window_tokens": 100}, context_checkpoint_ratio=.9)
        self.assertEqual(self.report(data)["action"], "continue")

    def test_hard_limits_hold_on_unknown_or_projected_overrun(self):
        for data in (self.data([], limits={"total_tokens": 500}, remaining={"total_tokens": 20}),
                     self.data(limits={"total_tokens": 130}, remaining={"total_tokens": 20}),
                     self.data(limits={"elapsed_seconds": 120}, remaining={"elapsed_seconds": 0}),
                     self.data(limits={"tool_calls": 10})):
            self.assertEqual(self.report(data)["action"], "hold")

    def test_completion_stops_early_but_cannot_hide_limit_breach(self):
        self.assertEqual(self.report(self.data(completed=True))["action"], "complete")
        self.assertEqual(self.report(self.data(completed=True, limits={"total_tokens": 119}))["action"], "hold")
        self.assertEqual(self.report(self.data(completed=True, limits={"total_tokens": 120}))["action"], "complete")

    def test_no_progress_and_context_pressure_checkpoint(self):
        for args in ({"no_progress_calls": 5}, {"repeated_hypotheses": 2}, {"context": {"used_tokens": 75, "window_tokens": 100}}):
            self.assertEqual(self.report(self.data(**args))["action"], "checkpoint")

    def test_unknown_fields_and_invalid_token_subsets_refused(self):
        with self.assertRaises(ValueError):
            self.report(self.data(prompt="not allowed"))
        sample = self.sample()
        sample["tokens"]["thought_tokens"] = 21
        with self.assertRaises(ValueError):
            self.report(self.data([sample]))
        with self.assertRaises(ValueError):
            self.report(self.data(elapsed_seconds=True))

    def test_benchmark_legacy_and_inclusive_reasoning(self):
        run = {"name": "baseline", "input_tokens": 100, "output_tokens": 20, "thought_tokens": 10, "cached_tokens": 40,
               "tool_calls": 2, "turns": 2, "correctness_score": 5, "clarity_score": 5, "high_severity_findings": 0, "privacy_concern": False}
        self.assertEqual(benchmark.validate_run(run, 0)["total_tokens"], 130)
        inclusive = deepcopy(run)
        inclusive["thought_in_output"] = True
        self.assertEqual(benchmark.validate_run(inclusive, 0)["total_tokens"], 120)


if __name__ == "__main__":
    unittest.main()
