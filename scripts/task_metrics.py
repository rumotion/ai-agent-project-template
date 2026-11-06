"""Offline ordinary-task measurements; no pacing activation, discovery or calls.

Reads an explicit sanitized JSON file and prints bounded advice. Measurements
are caller declarations, not provider attestation or a spending controller.
"""
from datetime import datetime, timedelta, timezone
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

import continuity
from usage_math import token_total

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pacing_metrics", HERE / "usage-pacing.py")
pacing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pacing)
COUNTERS = {"tool_calls", "restore_reads", "review_rounds", "test_runs"}
LIMITS = {"elapsed_seconds", "tool_calls", "total_tokens"}
LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}$")


def count(value):
    if value is not None and (type(value) is not int or not 0 <= value <= 10**12):
        raise ValueError("invalid cumulative count")
    return value


def fields(value, allowed, required=()):
    if not isinstance(value, dict) or set(value) - set(allowed) or not set(required).issubset(value):
        raise ValueError("invalid measurement fields")


def label(value, nullable=False):
    if nullable and value is None:
        return
    if not isinstance(value, str) or not LABEL.fullmatch(value):
        raise ValueError("invalid opaque label")


def report(data, now=None):
    now = now or datetime.now(timezone.utc)
    fields(data, {"task_id", "observed_at", "completed", "actors", "elapsed_seconds", "snapshots", "limits", "remaining", "no_progress_calls", "repeated_hypotheses", "context", "context_checkpoint_ratio"},
           {"task_id", "observed_at", "completed", "actors", "snapshots"})
    if not isinstance(data["task_id"], str) or not continuity.ID_RE.fullmatch(data["task_id"]) or type(data["completed"]) is not bool:
        raise ValueError("invalid task identity or completion")
    at = pacing.timestamp(data["observed_at"])
    if at > now:
        raise ValueError("future observation")
    snapshots = data["snapshots"]
    if not isinstance(snapshots, list) or len(snapshots) > 64:
        raise ValueError("at most 64 sanitized snapshots")
    actors = data["actors"]
    if not isinstance(actors, dict) or not 1 <= len(actors) <= 32 or list(actors.values()).count("main") != 1:
        raise ValueError("declare all actors with exactly one main")
    for actor, role in actors.items():
        label(actor)
        if role not in {"main", "worker"}:
            raise ValueError("invalid declared role")
    latest, actor_last, high_water, gaps = {}, {}, {}, set()
    for sample in snapshots:
        fields(sample, {"actor", "segment", "role", "scope", "source", "started_at", "observed_at", "model", "effort", "counters", "tokens", "closed"},
               {"actor", "segment", "role", "scope", "source", "started_at", "observed_at", "model", "effort", "counters"})
        for key in ("actor", "segment"):
            label(sample[key])
        for key in ("model", "effort"):
            label(sample[key], nullable=True)
        if type(sample.get("closed", False)) is not bool:
            raise ValueError("invalid segment closure")
        if sample["role"] not in {"main", "worker"} or sample["scope"] not in {"task", "session", "account"} or sample["source"] not in {"manual", "native", "synthetic"}:
            raise ValueError("invalid observation provenance")
        seen = pacing.timestamp(sample["observed_at"])
        started = pacing.timestamp(sample["started_at"])
        if seen > at or started > seen:
            raise ValueError("snapshot newer than report")
        fields(sample["counters"], COUNTERS)
        for value in sample["counters"].values():
            count(value)
        raw = sample.get("tokens", {})
        fields(raw, {"input_tokens", "output_tokens", "thought_tokens", "cached_tokens", "thought_in_output"})
        total = token_total(raw.get("input_tokens"), raw.get("output_tokens"), raw.get("thought_tokens"), raw.get("cached_tokens"), raw.get("thought_in_output", False))
        actor = sample["actor"]
        if actor not in actors or actors[actor] != sample["role"]:
            raise ValueError("undeclared actor or role changed")
        key = actor, sample["segment"]
        previous = latest.get(key)
        last = actor_last.get(actor)
        if last and (seen <= last["at"] or (key != last["key"] and (previous or started < last["at"]))):
            raise ValueError("overlapping or reopened actor segment")
        if previous:
            old = previous["sample"]
            if old.get("closed", False):
                raise ValueError("closed segment cannot receive another snapshot")
            if any(sample[name] != old[name] for name in ("started_at", "model", "effort", "scope", "source")):
                raise ValueError("changed observation basis requires a new segment")
            if raw.get("thought_in_output", False) != old.get("tokens", {}).get("thought_in_output", False):
                raise ValueError("changed token basis requires a new segment")
        water = high_water.setdefault(key, {})
        for name, after in dict(sample["counters"], **{name: raw.get(name) for name in ("input_tokens", "output_tokens", "thought_tokens", "cached_tokens")}).items():
            if after is not None:
                if name in water and after < water[name]:
                    raise ValueError("cumulative reset requires a new segment")
                water[name] = after
        latest[key] = {"sample": sample, "at": seen, "total": total}
        actor_last[actor] = {"key": key, "at": seen}
    if not latest:
        gaps.add("no_task_measurements")
    totals = {}
    roles = {}
    for role in ("main", "worker"):
        entries = [entry for entry in latest.values() if entry["sample"]["role"] == role]
        missing_actor = any(actor not in actor_last for actor in actors if actors[actor] == role)
        if missing_actor:
            gaps.add("missing_actor_measurements")
        values = {}
        for name in COUNTERS | {"total_tokens"}:
            parts = []
            for entry in entries:
                sample = entry["sample"]
                usable = sample["scope"] == "task" and (sample.get("closed", False) or now - entry["at"] <= timedelta(minutes=10))
                if not usable:
                    gaps.add("stale_or_non_task_scope")
                value = entry["total"] if name == "total_tokens" else sample["counters"].get(name)
                parts.append(value if usable else None)
            values[name] = sum(parts) if entries and not missing_actor and all(value is not None for value in parts) else None
        roles[role] = values
    for name in COUNTERS | {"total_tokens"}:
        # Aggregate each role once; actor-level segments were summed above.
        parts = [roles[role][name] for role in set(actors.values())]
        totals[name] = sum(parts) if parts and all(value is not None for value in parts) else None
    totals["elapsed_seconds"] = count(data.get("elapsed_seconds")) if now - at <= timedelta(minutes=10) else None
    if any(total is None for total in totals.values()):
        gaps.add("incomplete_task_totals")
    limits, remaining = data.get("limits", {}), data.get("remaining", {})
    fields(limits, LIMITS)
    fields(remaining, LIMITS)
    for value in list(limits.values()) + list(remaining.values()):
        count(value)
    if any(value is None for value in limits.values()):
        raise ValueError("hard limits must be numeric")
    action, reasons = "continue", []
    for name, limit in limits.items():
        used, estimate = totals[name], remaining.get(name)
        if used is None or (not data["completed"] and estimate is None):
            action = "hold"
            reasons.append("hard_budget_unverifiable:" + name)
        elif used > limit or (not data["completed"] and used + estimate > limit):
            action = "hold"
            reasons.append("hard_budget_exceeded_or_projected:" + name)
        elif used == limit and not data["completed"]:
            action = "hold"
            reasons.append("hard_budget_reached:" + name)
    if now - at > timedelta(minutes=10) and not data["completed"]:
        action = "hold"
        reasons.append("stale_progress_checkpoint")
    no_progress, repeated = data.get("no_progress_calls", 0), data.get("repeated_hypotheses", 0)
    count(no_progress); count(repeated)
    if no_progress is None or repeated is None:
        raise ValueError("progress counters must be numeric")
    context = data.get("context")
    pressure = None
    threshold = pacing.number(data.get("context_checkpoint_ratio", .75), .1, 1)
    if context is not None:
        fields(context, {"used_tokens", "window_tokens"}, {"used_tokens", "window_tokens"})
        clean = pacing.normalize({"context": context})["context"]
        pressure = clean["used_tokens"] / clean["window_tokens"]
    if action != "hold":
        if data["completed"]:
            action, reasons = "complete", ["stop_on_verified_completion_declaration"]
        elif no_progress >= 5 or repeated >= 2 or pressure is not None and pressure >= threshold:
            action, reasons = "checkpoint", ["review_progress_hypotheses_or_context; save_next_action"]
    return {"task_id": data["task_id"], "action": action, "reasons": reasons, "totals": totals,
            "by_role": roles, "gaps": sorted(gaps), "context_ratio": pressure,
            "observed_models": sorted({entry["sample"]["model"] for entry in latest.values() if entry["sample"]["model"] is not None}),
            "unknown_model_or_effort": any(entry["sample"]["model"] is None or entry["sample"]["effort"] is None for entry in latest.values()) or not latest,
            "measurements": [{key: entry["sample"].get(key) for key in ("actor", "segment", "source", "scope", "observed_at", "model", "effort", "closed")} for entry in latest.values()],
            "pacing_activated": False, "advisory_only": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args()
    try:
        value, code = report(continuity.bounded_json(args.file)), 0
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        value, code = {"action": "hold", "issue": "invalid_sanitized_task_measurements"}, 1
    print(json.dumps(value, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
