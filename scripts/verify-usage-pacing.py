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
                       deadline=(NOW + timedelta(hours=4)).isoformat(), max_agents=4, now=NOW)
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
        return pacing.advice(self.db, self.run, **options)

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
                       {"deadline": "2026-10-26T16:00:00"}, {"max_agents": 11}, {"max_agents": True}):
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
