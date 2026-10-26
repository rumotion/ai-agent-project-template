#!/usr/bin/env python3
"""Offline quota pacing; Python 3.9+, standard library only.

Stores plans and sanitized numeric observations in SQLite outside this repo.
No credentials, transcript discovery, network, subprocesses or agent launching.
Plans are inactive until separately confirmed by the human via the lead agent.
This records a confirmation declaration, not authenticated human identity.
All CLI output is bounded JSON. Times require an explicit UTC offset.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import re
import sqlite3
import sys
import time
import uuid

UTC = timezone.utc
MAX_INPUT = 64_000


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("time must be an ISO timestamp with UTC offset")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("time requires an explicit UTC offset")
    return result.astimezone(UTC)


def number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError("numeric field required")
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError("numeric field outside allowed range")
    return value


def database(root):
    root = Path(root).expanduser().resolve()
    repo = Path(__file__).resolve().parents[1]
    if root == repo or repo in root.parents:
        raise ValueError("pacing state must live outside the template repository")
    root.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(root / "pacing.sqlite3"), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=10000")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY, plan TEXT NOT NULL,
            state TEXT NOT NULL, confirmed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL, observed_at TEXT NOT NULL,
            source TEXT NOT NULL, data TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS sample_lookup ON samples(run_id, id);
    """)
    return db


def get_run(db, run_id):
    row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    if row is None:
        raise ValueError("unknown run")
    return {"id": row["id"], "state": row["state"],
            "confirmed_at": row["confirmed_at"], "plan": json.loads(row["plan"])}


def create_plan(db, provider, objective, deadline, target=90, max_agents=1,
                reserve=1, wrap_minutes=30, now=None):
    now = now or datetime.now(UTC)
    end = timestamp(deadline)
    if provider not in ("claude", "codex", "google"):
        raise ValueError("unsupported provider")
    if not isinstance(objective, str) or not objective.strip() or len(objective) > 500:
        raise ValueError("objective must contain 1 to 500 characters")
    if any(ord(c) < 32 for c in objective):
        raise ValueError("objective must be plain single-line text")
    number(target, 2, 99)
    number(reserve, 1, 20)
    number(max_agents, 1, 10)
    number(wrap_minutes, 1, 120)
    if int(max_agents) != max_agents or int(wrap_minutes) != wrap_minutes:
        raise ValueError("agent count and wrap minutes must be integers")
    if reserve >= target or not now + timedelta(minutes=wrap_minutes) < end <= now + timedelta(days=7):
        raise ValueError("invalid reserve or deadline (must allow wrap-up, within seven days)")
    plan = {"provider": provider, "objective": objective.strip(), "deadline": end.isoformat(),
            "target": target, "reserve": reserve, "max_agents": max_agents,
            "wrap_minutes": wrap_minutes, "created_at": now.isoformat()}
    run_id = uuid.uuid4().hex[:16]
    with db:
        db.execute("INSERT INTO runs VALUES (?, ?, 'pending', NULL)",
                   (run_id, json.dumps(plan, allow_nan=False)))
    return {**get_run(db, run_id), "warning":
            "Higher quota use can exhaust shared limits. Extra paid usage is not authorized. "
            "Only useful queued work; stop on completion, stale data, limits or deadline. "
            "Review provider, scope, deadline and max agents; wait for separate human confirmation."}


def confirm(db, run_id, confirmation, now=None):
    now = now or datetime.now(UTC)
    with db:
        db.execute("BEGIN IMMEDIATE")
        run = get_run(db, run_id)
        if confirmation != run_id or run["state"] != "pending":
            raise ValueError("a pending plan and its exact confirmation ID are required")
        if timestamp(run["plan"]["deadline"]) <= now + timedelta(minutes=run["plan"]["wrap_minutes"]):
            raise ValueError("plan has reached its wrap-up time; create a new plan")
        changed = db.execute("UPDATE runs SET state='active', confirmed_at=? WHERE id=? AND state='pending'",
                             (now.isoformat(), run_id)).rowcount
        if changed != 1:
            raise ValueError("plan state changed; inspect status")
    return get_run(db, run_id)


def normalize(data, claude=False):
    """Allowlist numeric metrics; never persist raw statusline input."""
    if not isinstance(data, dict):
        raise ValueError("observation must be an object")
    if claude:
        limits = data.get("rate_limits") or {}
        windows = {}
        for native, name in (("seven_day", "long"), ("five_hour", "short"), ("spend_limit", "spend")):
            raw = limits.get(native)
            if isinstance(raw, dict) and raw.get("used_percentage") is not None and raw.get("resets_at") is not None:
                reset = number(raw["resets_at"], 0, 32_503_680_000)
                windows[name] = {"used_percent": raw["used_percentage"],
                                 "resets_at": datetime.fromtimestamp(reset, UTC).isoformat()}
        window = data.get("context_window") or {}
        current = window.get("current_usage") or {}
        context = None
        if current and window.get("context_window_size"):
            used = sum(number(current.get(k, 0), 0, 100_000_000) for k in
                       ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            context = {"used_tokens": used, "window_tokens": window["context_window_size"]}
        cost = data.get("cost") or {}
        session_cost = None
        if cost.get("total_cost_usd") is not None and data.get("session_id"):
            session_cost = {"session_id": data["session_id"], "total_usd": cost["total_cost_usd"]}
        data = {"windows": windows, "context": context, "cost": session_cost}
    result = {"windows": {}}
    windows = data.get("windows", {})
    if not isinstance(windows, dict) or len(windows) > 8:
        raise ValueError("at most eight quota windows allowed")
    for name, raw in windows.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", name) or not isinstance(raw, dict):
            raise ValueError("invalid quota window")
        result["windows"][name] = {
            "used_percent": number(raw.get("used_percent"), 0, 100),
            "resets_at": timestamp(raw.get("resets_at")).isoformat()}
    if data.get("context") is not None:
        raw = data["context"]
        size = number(raw["window_tokens"], 1, 100_000_000)
        used = number(raw["used_tokens"], 0, size)
        result["context"] = {"used_tokens": used, "window_tokens": size}
    if data.get("cost") is not None:
        raw = data["cost"]
        session = raw["session_id"]
        if not isinstance(session, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", session):
            raise ValueError("invalid session ID")
        result["cost"] = {"session_id": session,
                          "total_usd": number(raw["total_usd"], 0, 1_000_000)}
    return result


def record(db, run_id, data, claude=False, observed_at=None, now=None):
    now = now or datetime.now(UTC)
    at = timestamp(observed_at) if observed_at else now
    clean = normalize(data, claude)
    with db:
        db.execute("BEGIN IMMEDIATE")
        run = get_run(db, run_id)
        if run["state"] != "active":
            raise ValueError("recording requires an active, human-confirmed plan")
        if claude and run["plan"]["provider"] != "claude":
            raise ValueError("Claude statusline requires a Claude plan")
        if at > now + timedelta(seconds=30) or at < now - timedelta(days=1):
            raise ValueError("observation time must be recent and not in the future")
        if at < timestamp(run["confirmed_at"]):
            raise ValueError("observation predates confirmation")
        last = db.execute("SELECT observed_at FROM samples WHERE run_id=? ORDER BY id DESC LIMIT 1",
                          (run_id,)).fetchone()
        if last and at <= timestamp(last[0]):
            raise ValueError("observation times must strictly increase")
        db.execute("INSERT INTO samples(run_id,observed_at,source,data) VALUES (?,?,?,?)",
                   (run_id, at.isoformat(), "claude_statusline" if claude else "manual",
                    json.dumps(clean, allow_nan=False)))
    return {"recorded": True, "observed_at": at.isoformat(), **clean}


def recent(db, run_id):
    rows = db.execute("SELECT * FROM samples WHERE run_id=? ORDER BY id DESC LIMIT 256", (run_id,)).fetchall()
    return [{"at": timestamp(r["observed_at"]), "source": r["source"],
             **json.loads(r["data"])} for r in reversed(rows)]


def advice(db, run_id, agents=0, since=None, now=None):
    now = now or datetime.now(UTC)
    run = get_run(db, run_id)
    plan = run["plan"]
    number(agents, 0, plan["max_agents"])
    if int(agents) != agents:
        raise ValueError("agents must be an integer")

    def verdict(state, count, reason):
        return {"state": state, "recommended_agents": count, "reason": reason,
                "advisory_only": True}

    if run["state"] != "active":
        return verdict("inactive", 0, "No confirmed active plan")
    wrap = timedelta(minutes=plan["wrap_minutes"])
    end = timestamp(plan["deadline"]) - wrap
    if now >= end:
        return verdict("wrap_up", 0, "Deadline wrap-up time reached")
    samples = recent(db, run_id)
    if not samples or now - samples[-1]["at"] > timedelta(minutes=10):
        return verdict("hold", 0, "Missing or stale telemetry; stop pacing until refreshed")
    latest = samples[-1]
    windows = latest["windows"]
    if "long" not in windows:
        return verdict("hold", 0, "Long quota window unknown; do not infer quota from tokens")
    for name, window in windows.items():
        ceiling = plan["target"] - plan["reserve"] if name == "long" else 98
        reset = timestamp(window["resets_at"])
        if window["used_percent"] >= ceiling or now >= reset - wrap:
            return verdict("wrap_up", 0, "Quota reserve, window reset or short-window ceiling reached")
        end = min(end, reset - wrap)
    context = latest.get("context")
    if context and context["used_tokens"] / context["window_tokens"] >= .90:
        return verdict("wrap_up", 0, "Context at 90%; save handoff and stop this pacing run")
    if agents == 0:
        return verdict("ready", 0, "Start at most one approved worker on queued useful work; then measure")
    if since is None:
        return verdict("hold", agents, "Supply --since with the last agent-count change; never scale from mixed counts")
    start = timestamp(since)
    if start > now:
        raise ValueError("agent-count change cannot be in the future")
    history = [s for s in samples if s["at"] >= max(start, now - timedelta(minutes=30))]
    if len(history) < 2 or (history[-1]["at"] - history[0]["at"]).total_seconds() < 900:
        return verdict("measuring", agents, "Need at least fifteen minutes at the same agent count")
    # A missing window, source change, reset or decreasing reading invalidates this rate.
    for old, new in zip(history, history[1:]):
        if old["source"] != new["source"] or set(old["windows"]) != set(windows) or set(new["windows"]) != set(windows):
            return verdict("hold", 0, "Telemetry source or window set changed; establish a fresh baseline")
        for name in windows:
            a, b = old["windows"][name], new["windows"][name]
            if a["resets_at"] != b["resets_at"] or b["used_percent"] < a["used_percent"]:
                return verdict("hold", 0, "Window reset or nonmonotonic usage; establish a fresh baseline")
    first = history[0]
    minutes = (latest["at"] - first["at"]).total_seconds() / 60
    long_rate = (windows["long"]["used_percent"] - first["windows"]["long"]["used_percent"]) / minutes
    if long_rate <= 0:
        return verdict("measuring", agents, "Long-window rate not measurable; do not scale up")
    ratios = []
    remaining = (end - now).total_seconds() / 60
    for name, window in windows.items():
        rate = (window["used_percent"] - first["windows"][name]["used_percent"]) / minutes
        if rate > 0:
            ceiling = plan["target"] - plan["reserve"] if name == "long" else 98
            ratios.append((ceiling - window["used_percent"]) / remaining / rate)
    scale = min(ratios)
    raw = max(0, min(plan["max_agents"], math.floor(agents * scale + .25)))
    # Growth is gradual; reductions may be immediate near a shared quota limit.
    count = min(raw, agents + 1)
    return {**verdict("run", count, "Coarse quota-rate estimate; includes other sessions and devices"),
            "scale": round(scale, 3)}


def metrics(db, run_id, kind, now=None):
    get_run(db, run_id)
    rows = recent(db, run_id)
    now = now or datetime.now(UTC)
    if not rows:
        return {"state": "unknown"}
    sample = rows[-1]
    base = {"observed_at": sample["at"].isoformat(),
            "stale": now - sample["at"] > timedelta(minutes=10)}
    if kind == "context":
        value = sample.get("context")
        return {**base, "context": value, "handoff_at_percent": 75,
                "stop_at_percent": 90}
    if kind == "cost":
        return {**base, "cost": sample.get("cost"),
                "meaning": "Latest session API-equivalent USD estimate, not subscription charge or quota; never sum snapshots"}
    return {**base, "windows": sample["windows"]}


def load_input(path):
    if path:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_INPUT + 1)
    else:
        raw = sys.stdin.buffer.read(MAX_INPUT + 1)
    if len(raw) > MAX_INPUT:
        raise ValueError("input exceeds 64000 bytes")
    return json.loads(raw.decode("utf-8-sig"), parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / ".agent-usage-pacing")
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("--provider", choices=("claude", "codex", "google"), required=True)
    plan.add_argument("--objective", required=True)
    plan.add_argument("--deadline", required=True, help="ISO date/time with offset")
    plan.add_argument("--target", type=float, default=90)
    plan.add_argument("--reserve", type=float, default=1)
    plan.add_argument("--max-agents", type=int, default=1)
    plan.add_argument("--wrap-minutes", type=int, default=30)
    for name in ("start", "status", "stop", "record", "pace", "usage", "context", "cost"):
        sub = commands.add_parser(name)
        sub.add_argument("run")
        if name == "start":
            sub.add_argument("--confirm", required=True, help="Only after separate human confirmation of this plan ID")
        if name == "record":
            source = sub.add_mutually_exclusive_group(required=True)
            source.add_argument("--file", type=Path, help="Sanitized numeric JSON only")
            source.add_argument("--claude-stdin", action="store_true")
            sub.add_argument("--observed-at", help="Actual reading time with offset; defaults to now")
        if name == "pace":
            sub.add_argument("--agents", type=int, default=0)
            sub.add_argument("--since", help="Time agent count last changed, with offset")
            sub.add_argument("--watch", type=int, help="Poll local data every N seconds (minimum 300); exit on advice change")
    args = parser.parse_args()
    try:
        with closing(database(args.root)) as db:
            if args.command == "plan":
                result = create_plan(db, args.provider, args.objective, args.deadline, args.target,
                                     args.max_agents, args.reserve, args.wrap_minutes)
            elif args.command == "start":
                result = confirm(db, args.run, args.confirm)
            elif args.command == "status":
                result = get_run(db, args.run)
            elif args.command == "stop":
                with db:
                    get_run(db, args.run)
                    db.execute("UPDATE runs SET state='stopped' WHERE id=?", (args.run,))
                result = get_run(db, args.run)
            elif args.command == "record":
                result = record(db, args.run, load_input(args.file), args.claude_stdin, args.observed_at)
            elif args.command == "pace":
                if args.watch is not None and args.watch < 300:
                    raise ValueError("watch interval must be at least 300 seconds")
                while True:
                    result = advice(db, args.run, args.agents, args.since)
                    print(json.dumps(result, allow_nan=False), flush=True)
                    if not args.watch or result["state"] not in ("measuring", "run") or result["recommended_agents"] != args.agents:
                        return 0
                    time.sleep(args.watch)
            else:
                result = metrics(db, args.run, args.command)
        print(json.dumps(result, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError, OSError, sqlite3.Error):
        # Input may contain private data: never echo it or raw parser exceptions.
        print(json.dumps({"error": "Invalid input, plan state or local database; check documented fields and limits"}), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
