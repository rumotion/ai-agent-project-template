#!/usr/bin/env python3
"""Offline pacing regressions; temporary databases, simulated time, no model calls."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("usage-pacing.py")
spec = importlib.util.spec_from_file_location("pacing", SCRIPT)
pacing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pacing)
NOW = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)


class PacingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = pacing.database(self.root)
        self.addCleanup(self.db.close)
        self.run = self.plan()["id"]

    def plan(self, **kwargs):
        options = dict(provider="claude", objective="Finish the approved test backlog",
                       deadline=(NOW + timedelta(hours=4)).isoformat(), max_agents=4,
                       max_open_tasks=4, now=NOW)
        options.update(kwargs)
        return pacing.create_plan(self.db, **options)

    def activate(self):
        pacing.confirm(self.db, self.run, self.run, NOW)

    def data(self, long=10, short=20, **extras):
        return {"windows": {
            "long": {"used_percent": long, "resets_at": (NOW + timedelta(days=2)).isoformat()},
            "short": {"used_percent": short, "resets_at": (NOW + timedelta(hours=5)).isoformat()}}, **extras}

    def samples(self, first=None, last=None):
        self.activate()
        pacing.record(self.db, self.run, first or self.data(), now=NOW)
        pacing.record(self.db, self.run, last or self.data(11, 22), now=NOW + timedelta(minutes=20))

    def advice(self, **kwargs):
        options = dict(agents=2, since=NOW.isoformat(), now=NOW + timedelta(minutes=20))
        options.update(kwargs)
        if "work" not in options:
            options["work"] = self.board(agents=options["agents"], now=options["now"])
        return pacing.advice(self.db, self.run, **options)

    def board(self, agents=2, now=None):
        return {"run_id": self.run, "observed_at": (now or NOW + timedelta(minutes=20)).isoformat(),
                "tasks": [{"task_id": "task-" + str(i), "state": "running" if i < agents else "queued",
                           "depends_on": [], "remaining_minutes": 10,
                           "quota_percent": {"long": .1, "short": .1}} for i in range(4)]}

    def test_confirmation_and_terminal_stop(self):
        self.assertEqual(self.advice()["state"], "inactive")
        with self.assertRaises(ValueError):
            pacing.record(self.db, self.run, self.data(), now=NOW)
        with self.assertRaises(ValueError):
            pacing.confirm(self.db, self.run, "another-plan", NOW)
        self.activate()
        self.assertEqual(pacing.get_run(self.db, self.run)["state"], "active")
        with self.db:
            self.db.execute("UPDATE runs SET state='stopped' WHERE id=?", (self.run,))
        with self.assertRaises(ValueError):
            self.activate()
        self.assertEqual(self.advice()["recommended_agents"], 0)

    def test_no_data_stale_and_missing_window(self):
        self.activate()
        self.assertEqual(self.advice()["state"], "hold")
        pacing.record(self.db, self.run, self.data(), now=NOW)
        self.assertEqual(self.advice()["recommended_agents"], 0)
        pacing.record(self.db, self.run, {"windows": {}}, now=NOW + timedelta(minutes=20))
        self.assertEqual(self.advice()["recommended_agents"], 0)

    def test_rate_growth_is_capped(self):
        self.samples()
        result = self.advice()
        self.assertEqual(result["state"], "run")
        self.assertEqual(result["recommended_agents"], 3)
        self.assertLessEqual(result["recommended_agents"], 4)
        self.assertEqual(result["dispatch_task_ids"], ["task-2"])

    def test_quota_headroom_alone_cannot_dispatch(self):
        self.samples()
        result = self.advice(work=None)
        self.assertEqual(result["state"], "drain")
        self.assertEqual(result["recommended_agents"], 2)
        self.assertEqual(result["dispatch_task_ids"], [])

    def test_default_wip_limit_includes_unaccepted_work(self):
        self.run = self.plan(max_open_tasks=2)["id"]
        self.samples()
        self.assertEqual(self.advice()["dispatch_task_ids"], [])
        self.assertEqual(self.advice()["recommended_agents"], 2)
        # The plan's real default is two; this fixture otherwise opts in to four.
        default = pacing.create_plan(self.db, "codex", "Finish one slice",
                                     (NOW + timedelta(hours=4)).isoformat(), now=NOW)
        self.assertEqual(default["plan"]["max_open_tasks"], 2)
        for state in ("review", "blocked"):
            board = self.board(agents=1)
            board["tasks"][1]["state"] = state
            result = self.advice(agents=1, work=board)
            self.assertEqual(result["state"], "drain")
            self.assertEqual(result["dispatch_task_ids"], [])

    def test_dependencies_release_only_after_parent_acceptance(self):
        self.samples()
        board = self.board(agents=0)
        board["tasks"] = board["tasks"][:2]
        board["tasks"][1]["depends_on"] = ["task-0"]
        self.assertEqual(self.advice(agents=0, work=board)["dispatch_task_ids"], ["task-0"])
        board["tasks"][0]["state"] = "accepted"
        self.assertEqual(self.advice(agents=0, work=board)["dispatch_task_ids"], ["task-1"])
        board["tasks"][1]["state"] = "accepted"
        self.assertEqual(self.advice(agents=0, work=board)["state"], "complete")

    def test_bad_boards_fail_closed(self):
        self.samples()
        def check(board):
            result = self.advice(work=board)
            self.assertEqual(result["state"], "drain")
            self.assertEqual(result["dispatch_task_ids"], [])
        board = self.board()
        board["run_id"] = "another-run"
        check(board)
        board = self.board(now=NOW)
        check(board)
        board = self.board(now=NOW + timedelta(minutes=21))
        check(board)
        board = self.board()
        board["tasks"][3]["task_id"] = "task-0"
        check(board)
        board = self.board()
        board["tasks"][0]["depends_on"] = ["unknown"]
        check(board)
        board = self.board()
        board["tasks"][2]["depends_on"] = ["task-3"]
        board["tasks"][3]["depends_on"] = ["task-2"]
        check(board)
        board = self.board(agents=1)
        check(board)
        board = self.board()
        board["tasks"][0]["depends_on"] = ["task-2"]
        check(board)
        board = self.board()
        board["tasks"] *= 9
        check(board)

    def test_empty_board_completes_without_consuming_quota(self):
        self.samples()
        board = self.board(agents=0)
        board["tasks"] = []
        result = self.advice(agents=0, work=board)
        self.assertEqual(result["state"], "complete")
        self.assertEqual(result["recommended_agents"], 0)

    def test_time_estimates_include_margin_and_open_work(self):
        self.samples()
        board = self.board()
        # 190 minutes to the wrap boundary. 2*10*1.5 + 110*1.5 exceeds it.
        board["tasks"][2]["remaining_minutes"] = 110
        board["tasks"] = board["tasks"][:3]
        self.assertEqual(self.advice(work=board)["dispatch_task_ids"], [])
        board["tasks"][0]["remaining_minutes"] = 130
        self.assertEqual(self.advice(work=board)["state"], "wrap_up")

    def test_every_quota_window_must_fund_open_and_new_work(self):
        self.samples()
        for window in ("long", "short"):
            board = self.board()
            board["tasks"] = board["tasks"][:3]
            board["tasks"][2]["quota_percent"][window] = 60
            self.assertEqual(self.advice(work=board)["dispatch_task_ids"], [])
            board["tasks"][0]["quota_percent"][window] = 60
            self.assertEqual(self.advice(work=board)["state"], "wrap_up")

    def test_unknown_cost_never_authorizes_more_work(self):
        self.samples()
        for field in ("remaining_minutes", "quota_percent"):
            board = self.board()
            board["tasks"][0].pop(field)
            self.assertEqual(self.advice(work=board)["state"], "drain")
        for costs in ({"long": 1}, {"long": float("nan"), "short": 1},
                      {"long": True, "short": 1}, {"long": 0, "short": 0}):
            board = self.board()
            board["tasks"][2]["quota_percent"] = costs
            board["tasks"] = board["tasks"][:3]
            self.assertEqual(self.advice(work=board)["dispatch_task_ids"], [])

    def test_context_75_drains_before_90_stops(self):
        self.samples(last=self.data(11, 22, context={"used_tokens": 75_000, "window_tokens": 100_000}))
        result = self.advice()
        self.assertEqual(result["state"], "drain")
        self.assertEqual(result["recommended_agents"], 2)
        self.assertEqual(result["dispatch_task_ids"], [])

    def test_ready_task_still_requires_parent_scope_checks(self):
        self.samples()
        result = self.advice(agents=0)
        self.assertEqual(result["recommended_agents"], 1)
        self.assertEqual(len(result["dispatch_task_ids"]), 1)
        self.assertIn("scope checks", result["reason"])

    def test_cli_reloads_board_and_old_calls_cannot_dispatch(self):
        live = datetime.now(timezone.utc)
        self.run = self.plan(now=live, deadline=(live + timedelta(hours=4)).isoformat())["id"]
        pacing.confirm(self.db, self.run, self.run, live)
        pacing.record(self.db, self.run, {
            "windows": {"long": {"used_percent": 10, "resets_at": (live + timedelta(days=2)).isoformat()},
                        "short": {"used_percent": 20, "resets_at": (live + timedelta(hours=5)).isoformat()}}}, now=live)
        board = self.board(agents=0, now=live)
        source = self.root / "work.json"
        source.write_text(json.dumps(board), encoding="utf-8")
        command = [sys.executable, str(SCRIPT), "--root", str(self.root), "pace", self.run]
        def run(*args):
            result = subprocess.run(command + list(args), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertEqual(run()["dispatch_task_ids"], [])
        self.assertEqual(run("--work-file", str(source))["dispatch_task_ids"], ["task-0"])
        board["tasks"][0]["state"] = "review"
        source.write_text(json.dumps(board), encoding="utf-8")
        self.assertEqual(run("--work-file", str(source))["state"], "drain")

    def test_legacy_plan_uses_safe_wip_default(self):
        self.samples()
        plan = pacing.get_run(self.db, self.run)["plan"]
        plan.pop("max_open_tasks")
        with self.db:
            self.db.execute("UPDATE runs SET plan=? WHERE id=?", (json.dumps(plan), self.run))
        self.assertEqual(self.advice()["dispatch_task_ids"], [])

    def test_margin_is_cumulative_and_exact_boundary_is_denied(self):
        self.samples()
        board = self.board()
        board["tasks"] = board["tasks"][:3]
        # 78 long-window points remain. 50*1.5 + 2*1.5 equals the boundary.
        board["tasks"][0]["quota_percent"]["long"] = 25
        board["tasks"][1]["quota_percent"]["long"] = 25
        board["tasks"][2]["quota_percent"]["long"] = 2
        self.assertEqual(self.advice(work=board)["dispatch_task_ids"], [])

    def test_required_package_cannot_skip_unaffordable_queued_work(self):
        self.samples()
        board = self.board()
        board["tasks"][2]["quota_percent"]["short"] = 90
        self.assertEqual(self.advice(work=board)["dispatch_task_ids"], [])

    def test_downstream_integration_is_reserved_before_prerequisite_launch(self):
        self.run = self.plan(deadline=(NOW + timedelta(minutes=140)).isoformat())["id"]
        self.samples()
        board = self.board(agents=0)
        board["tasks"] = board["tasks"][:2]
        board["tasks"][1]["depends_on"] = ["task-0"]
        # At minute 20, 90 usable minutes remain; 1.5*(10+60) cannot fit.
        board["tasks"][1]["remaining_minutes"] = 60
        self.assertEqual(self.advice(agents=0, work=board)["dispatch_task_ids"], [])
        board["tasks"][1]["remaining_minutes"] = 10
        for window in ("long", "short"):
            board["tasks"][1]["quota_percent"][window] = 90
            self.assertEqual(self.advice(agents=0, work=board)["dispatch_task_ids"], [])
            board["tasks"][1]["quota_percent"][window] = .1
        board["tasks"][1].pop("quota_percent")
        self.assertEqual(self.advice(agents=0, work=board)["dispatch_task_ids"], [])

    def test_all_open_states_are_checked_before_review_or_context_drain(self):
        self.samples(last=self.data(11, 22, context={"used_tokens": 75_000, "window_tokens": 100_000}))
        for state in ("running", "review", "blocked"):
            board = self.board(agents=0)
            board["tasks"] = board["tasks"][:1]
            board["tasks"][0]["state"] = state
            board["tasks"][0]["remaining_minutes"] = 200
            result = self.advice(agents=1 if state == "running" else 0, work=board)
            self.assertEqual(result["state"], "wrap_up")
            self.assertEqual(result["dispatch_task_ids"], [])

    def test_short_window_overrides_weekly_headroom(self):
        self.samples(self.data(10, 70), self.data(11, 95))
        self.assertEqual(self.advice()["recommended_agents"], 0)

    def test_reserve_short_ceiling_and_deadline(self):
        for long, short in ((89, 20), (10, 98)):
            clean = self.data(long, short)
            self.assertEqual(pacing.normalize(clean), clean)
        self.samples(last=self.data(89, 20))
        self.assertEqual(self.advice()["state"], "wrap_up")
        self.assertEqual(self.advice(now=NOW + timedelta(hours=3, minutes=30))["state"], "wrap_up")

    def test_short_ceiling_immediate_stop(self):
        self.samples(last=self.data(11, 98))
        self.assertEqual(self.advice()["state"], "wrap_up")

    def test_reset_is_not_extrapolated(self):
        changed = self.data(11, 22)
        changed["windows"]["long"]["resets_at"] = (NOW + timedelta(days=3)).isoformat()
        self.samples(last=changed)
        self.assertEqual(self.advice()["state"], "hold")

    def test_decreasing_usage_invalidates_rate(self):
        self.samples(self.data(20, 30), self.data(19, 31))
        self.assertEqual(self.advice()["recommended_agents"], 0)

    def test_reset_nearby_stops_before_boundary(self):
        changed = self.data(11, 22)
        changed["windows"]["short"]["resets_at"] = (NOW + timedelta(minutes=45)).isoformat()
        self.samples(last=changed)
        self.assertEqual(self.advice()["state"], "wrap_up")

    def test_zero_rate_never_scales_up(self):
        self.samples(self.data(10, 20), self.data(10, 23))
        self.assertEqual(self.advice()["state"], "measuring")
        self.assertEqual(self.advice()["recommended_agents"], 2)

    def test_fifteen_minutes_and_agent_count_boundary(self):
        self.samples()
        result = self.advice(since=(NOW + timedelta(minutes=10)).isoformat())
        self.assertEqual(result["state"], "measuring")
        self.assertEqual(self.advice(since=None)["state"], "hold")
        self.assertEqual(self.advice(agents=0)["state"], "ready")

    def test_changed_source_needs_new_baseline(self):
        self.samples()
        with self.db:
            self.db.execute("UPDATE samples SET source='claude_statusline' WHERE id=(SELECT MAX(id) FROM samples)")
        self.assertEqual(self.advice()["state"], "hold")

    def test_context_relative_to_actual_window(self):
        self.samples(last=self.data(11, 22, context={"used_tokens": 90_000, "window_tokens": 100_000}))
        self.assertEqual(self.advice()["state"], "wrap_up")
        metrics = pacing.metrics(self.db, self.run, "context", NOW + timedelta(minutes=20))
        self.assertEqual(metrics["context"]["window_tokens"], 100_000)

    def test_claude_statusline_allowlist_and_cost_not_summed(self):
        self.activate()
        raw = {"rate_limits": {"seven_day": {"used_percentage": 10, "resets_at": (NOW + timedelta(days=2)).timestamp()}},
               "session_id": "session-1", "cost": {"total_cost_usd": 2.5},
               "context_window": {"context_window_size": 100_000, "current_usage": {
                   "input_tokens": 1000, "cache_read_input_tokens": 2000, "cache_creation_input_tokens": 500}},
               "private_unknown_field": "MUST_NOT_PERSIST"}
        pacing.record(self.db, self.run, raw, claude=True, now=NOW)
        pacing.record(self.db, self.run, raw, claude=True, now=NOW + timedelta(minutes=1))
        stored = " ".join(row[0] for row in self.db.execute("SELECT data FROM samples"))
        self.assertNotIn("MUST_NOT_PERSIST", stored)
        self.assertEqual(pacing.metrics(self.db, self.run, "cost", NOW)["cost"]["total_usd"], 2.5)
        self.assertEqual(pacing.metrics(self.db, self.run, "context", NOW)["context"]["used_tokens"], 3500)

    def test_validation_time_numeric_and_provider(self):
        for kwargs in ({"target": float("nan")}, {"target": 100}, {"reserve": 95},
                       {"deadline": "2026-10-26T16:00:00"}, {"max_agents": 11}, {"max_agents": True},
                       {"max_open_tasks": 0}, {"max_open_tasks": 11}, {"max_open_tasks": True}):
            with self.assertRaises((ValueError, TypeError)):
                self.plan(**kwargs)
        self.activate()
        with self.assertRaises(ValueError):
            pacing.record(self.db, self.run, self.data(float("inf")), now=NOW)
        pacing.record(self.db, self.run, self.data(), now=NOW)
        with self.assertRaises(ValueError):
            pacing.record(self.db, self.run, self.data(), now=NOW)
        with self.assertRaises(ValueError):
            pacing.record(self.db, self.run, self.data(), now=NOW - timedelta(minutes=1))
        other = self.plan(provider="google")["id"]
        pacing.confirm(self.db, other, other, NOW)
        with self.assertRaises(ValueError):
            pacing.record(self.db, other, {}, claude=True, now=NOW)

    def test_concurrent_plan_writers(self):
        def write(_):
            with closing(pacing.database(self.root)) as db:
                return pacing.create_plan(db, "codex", "Queued useful work",
                                          (NOW + timedelta(hours=4)).isoformat(), now=NOW)["id"]
        with ThreadPoolExecutor(max_workers=2) as pool:
            ids = list(pool.map(write, range(8)))
        self.assertEqual(len(set(ids)), 8)
        self.assertEqual(self.db.execute("PRAGMA journal_mode").fetchone()[0], "wal")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM runs").fetchone()[0], 9)

    def test_cli_errors_bounded_and_no_raw_input_echo(self):
        source = self.root / "input.json"
        source.write_text('{"private":"MUST_NOT_ECHO",}', encoding="utf-8")
        self.activate()
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                                 "record", self.run, "--file", str(source)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("MUST_NOT_ECHO", result.stdout + result.stderr)
        self.assertLess(len(result.stderr), 300)
        self.assertIn("error", json.loads(result.stderr))
        source.write_bytes(b" " * 64_001)
        with self.assertRaises(ValueError):
            pacing.load_input(source)

    def test_upgrade_preserves_colliding_custom_skill_before_any_write(self):
        upgrade_spec = importlib.util.spec_from_file_location("upgrade", SCRIPT.with_name("upgrade-target.py"))
        upgrade = importlib.util.module_from_spec(upgrade_spec)
        upgrade_spec.loader.exec_module(upgrade)
        for name in ("usage-pacing", "handoff"):
            with tempfile.TemporaryDirectory() as folder:
                target = Path(folder)
                custom = target / ".agents/skills" / name / "SKILL.md"
                custom.parent.mkdir(parents=True)
                custom.write_text("Custom domain skill; keep this", encoding="utf-8")
                marker = target / "domain.py"
                marker.write_text("pass\n", encoding="utf-8")
                before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
                code, messages = upgrade.upgrade_project(target)
                self.assertEqual(code, 1)
                self.assertIn("no files changed", messages[0])
                after = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
                self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
