"""Deterministic context and manual-usage benchmark for the agent template.

Python 3.9 standard library only. This script performs no network or model calls.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "benchmarks" / "context" / "scenarios.json"
REQUIRED_RUN_FIELDS = {
    "name",
    "input_tokens",
    "output_tokens",
    "thought_tokens",
    "cached_tokens",
    "tool_calls",
    "turns",
    "correctness_score",
    "clarity_score",
    "high_severity_findings",
    "privacy_concern",
}
COUNT_FIELDS = [
    "input_tokens",
    "output_tokens",
    "thought_tokens",
    "cached_tokens",
    "tool_calls",
    "turns",
    "high_severity_findings",
]
SCORE_FIELDS = ["correctness_score", "clarity_score"]
RUN_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class BenchmarkError(ValueError):
    """A user-correctable manifest or usage-record error."""


def read_json(path: Path, label: str) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as err:
        raise BenchmarkError("{} could not be read: {}".format(label, err))
    except ValueError as err:
        raise BenchmarkError("{} is not valid JSON: {}".format(label, err))
    if not isinstance(data, dict):
        raise BenchmarkError("{} must contain a JSON object".format(label))
    return data


def safe_repo_path(rel: str) -> Path:
    if not isinstance(rel, str) or not rel or "\x00" in rel:
        raise BenchmarkError("scenario file paths must be non-empty strings")
    candidate = Path(rel)
    if candidate.is_absolute() or rel.startswith(("/", "\\")):
        raise BenchmarkError("scenario file path must be repository-relative: {}".format(rel))
    if re.match(r"^[A-Za-z]:", rel):
        raise BenchmarkError("scenario file path must not contain a drive prefix: {}".format(rel))
    if ".." in candidate.parts:
        raise BenchmarkError("scenario file path must not escape the repository: {}".format(rel))
    resolved = (ROOT / candidate).resolve()
    if os.path.commonpath([str(ROOT.resolve()), str(resolved)]) != str(ROOT.resolve()):
        raise BenchmarkError("scenario file path escapes the repository: {}".format(rel))
    if not resolved.is_file():
        raise BenchmarkError("scenario file does not exist: {}".format(rel))
    return resolved


def load_manifest(path: Path) -> List[Dict[str, Any]]:
    data = read_json(path, "scenario manifest")
    if data.get("schema_version") != 1:
        raise BenchmarkError("scenario manifest schema_version must be 1")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise BenchmarkError("scenario manifest must contain a non-empty scenarios list")
    normalized: List[Dict[str, Any]] = []
    seen = set()
    for index, item in enumerate(scenarios):
        if not isinstance(item, dict):
            raise BenchmarkError("scenario {} must be an object".format(index))
        scenario_id = item.get("id")
        description = item.get("description")
        files = item.get("files")
        if not isinstance(scenario_id, str) or not scenario_id:
            raise BenchmarkError("scenario {} has no valid id".format(index))
        if scenario_id in seen:
            raise BenchmarkError("duplicate scenario id: {}".format(scenario_id))
        if not isinstance(description, str) or not description:
            raise BenchmarkError("scenario {} has no description".format(scenario_id))
        if not isinstance(files, list) or not files:
            raise BenchmarkError("scenario {} must list at least one file".format(scenario_id))
        for rel in files:
            if not isinstance(rel, str):
                raise BenchmarkError(
                    "scenario {} file entries must be strings".format(scenario_id)
                )
            safe_repo_path(rel)
        if len(files) != len(set(files)):
            raise BenchmarkError("scenario {} contains a duplicate file".format(scenario_id))
        seen.add(scenario_id)
        normalized.append({"id": scenario_id, "description": description, "files": files})
    return normalized


def measure_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    rows = []
    total_chars = 0
    for rel in scenario["files"]:
        try:
            chars = len(safe_repo_path(rel).read_text(encoding="utf-8"))
        except UnicodeError as err:
            raise BenchmarkError(
                "scenario file is not valid UTF-8 text: {} ({})".format(rel, err)
            )
        rows.append({"path": rel, "characters": chars, "estimated_tokens": chars // 4})
        total_chars += chars
    return {
        "id": scenario["id"],
        "description": scenario["description"],
        "files": rows,
        "characters": total_chars,
        "estimated_tokens": total_chars // 4,
    }


def validate_run(run: Any, index: int) -> Dict[str, Any]:
    if not isinstance(run, dict):
        raise BenchmarkError("usage run {} must be an object".format(index))
    missing = sorted(REQUIRED_RUN_FIELDS - set(run))
    if missing:
        raise BenchmarkError(
            "usage run {} is missing fields: {}".format(index, ", ".join(missing))
        )
    extra = sorted(set(run) - REQUIRED_RUN_FIELDS)
    if extra:
        raise BenchmarkError(
            "usage run {} contains unsupported fields: {}; "
            "records must contain totals only, never prompts".format(
                index, ", ".join(extra)
            )
        )
    name = run.get("name")
    if not isinstance(name, str) or not RUN_NAME_RE.fullmatch(name):
        raise BenchmarkError(
            "usage run {} name must be 1-64 letters, digits, dots, "
            "underscores, or hyphens".format(index)
        )
    clean = {field: run[field] for field in REQUIRED_RUN_FIELDS}
    clean["name"] = name.strip()
    for field in COUNT_FIELDS:
        value = run.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise BenchmarkError(
                "usage run {} field {} must be a non-negative integer".format(index, field)
            )
    for field in SCORE_FIELDS:
        value = run.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 5:
            raise BenchmarkError(
                "usage run {} field {} must be a number from 0 to 5".format(index, field)
            )
    if not isinstance(run.get("privacy_concern"), bool):
        raise BenchmarkError(
            "usage run {} field privacy_concern must be boolean".format(index)
        )
    if clean["cached_tokens"] > clean["input_tokens"]:
        raise BenchmarkError(
            "usage run {} cached_tokens cannot exceed input_tokens".format(index)
        )
    clean["total_tokens"] = (
        clean["input_tokens"] + clean["output_tokens"] + clean["thought_tokens"]
    )
    return clean


def load_usage(path: Path, scenario_id: str) -> List[Dict[str, Any]]:
    data = read_json(path, "usage record")
    if data.get("schema_version") != 1:
        raise BenchmarkError("usage record schema_version must be 1")
    if data.get("scenario") != scenario_id:
        raise BenchmarkError(
            "usage record scenario must match selected scenario '{}'".format(scenario_id)
        )
    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        raise BenchmarkError("usage record must contain a non-empty runs list")
    clean = [validate_run(run, index) for index, run in enumerate(runs)]
    names = [run["name"] for run in clean]
    if len(names) != len(set(names)):
        raise BenchmarkError("usage run names must be unique")
    if names.count("baseline") != 1:
        raise BenchmarkError("usage record must contain exactly one run named baseline")
    return clean


def compare_runs(
    runs: List[Dict[str, Any]], candidate_name: Optional[str]
) -> Dict[str, Any]:
    baseline = next(run for run in runs if run["name"] == "baseline")
    candidates = [run for run in runs if run["name"] != "baseline"]
    if candidate_name is None:
        if len(candidates) != 1:
            raise BenchmarkError(
                "--candidate is required when the usage record has multiple candidates"
            )
        candidate = candidates[0]
    else:
        matches = [run for run in candidates if run["name"] == candidate_name]
        if not matches:
            raise BenchmarkError("candidate run not found: {}".format(candidate_name))
        candidate = matches[0]
    if baseline["total_tokens"] <= 0:
        raise BenchmarkError("baseline total_tokens must be greater than zero")
    reduction = (
        (baseline["total_tokens"] - candidate["total_tokens"])
        / baseline["total_tokens"]
        * 100.0
    )
    criteria = {
        "token_reduction_at_least_10_percent": reduction >= 10.0 - 1e-9,
        "no_correctness_regression": (
            candidate["correctness_score"] >= baseline["correctness_score"]
        ),
        "no_high_severity_finding": candidate["high_severity_findings"] == 0,
        "no_privacy_concern": not candidate["privacy_concern"],
    }
    return {
        "baseline": baseline,
        "candidate": candidate,
        "token_reduction_percent": round(reduction, 2),
        "criteria": criteria,
        "verdict": "ADOPT" if all(criteria.values()) else "REJECT",
    }


def build_result(
    scenarios: List[Dict[str, Any]],
    selected_id: Optional[str],
    usage_path: Optional[Path],
    candidate_name: Optional[str],
) -> Dict[str, Any]:
    selected = scenarios
    if selected_id:
        selected = [scenario for scenario in scenarios if scenario["id"] == selected_id]
        if not selected:
            raise BenchmarkError("unknown scenario: {}".format(selected_id))
    if usage_path and not selected_id:
        raise BenchmarkError("--usage requires --scenario")
    measured = [measure_scenario(scenario) for scenario in selected]
    comparison = None
    verdict = "INSUFFICIENT_EVIDENCE"
    if usage_path:
        runs = load_usage(usage_path, selected_id or "")
        comparison = compare_runs(runs, candidate_name)
        verdict = comparison["verdict"]
    elif candidate_name:
        raise BenchmarkError("--candidate requires --usage")
    return {
        "schema_version": 1,
        "policy": {
            "minimum_token_reduction_percent": 10,
            "total_tokens_formula": "input_tokens + output_tokens + thought_tokens",
        },
        "scenarios": measured,
        "comparison": comparison,
        "verdict": verdict,
    }


def print_result(result: Dict[str, Any]) -> None:
    for scenario in result["scenarios"]:
        print("{}: {}".format(scenario["id"], scenario["description"]))
        for row in scenario["files"]:
            print(
                "  - {}: {} chars (~{} tokens)".format(
                    row["path"], row["characters"], row["estimated_tokens"]
                )
            )
        print(
            "  Total: {} chars (~{} tokens)".format(
                scenario["characters"], scenario["estimated_tokens"]
            )
        )
    comparison = result["comparison"]
    if comparison:
        print("Comparison:")
        print(
            "  baseline={} tokens; {}={} tokens; reduction={:.2f}%".format(
                comparison["baseline"]["total_tokens"],
                comparison["candidate"]["name"],
                comparison["candidate"]["total_tokens"],
                comparison["token_reduction_percent"],
            )
        )
        for name, passed in comparison["criteria"].items():
            print("  - {}: {}".format(name, "PASS" if passed else "FAIL"))
    print("Verdict: {}".format(result["verdict"]))


def run_self_test() -> None:
    scenarios = load_manifest(DEFAULT_MANIFEST)
    fast = next(item for item in scenarios if item["id"] == "fast-init")
    measured = measure_scenario(fast)

    validator_path = ROOT / "scripts" / "check-template.py"
    spec = importlib.util.spec_from_file_location("template_validator", str(validator_path))
    if spec is None or spec.loader is None:
        raise BenchmarkError("self-test could not load check-template.py")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    validator_chars, _ = validator.benchmark_startup()
    if fast["files"] != validator.BENCHMARK_FILES:
        raise BenchmarkError(
            "FAST_INIT manifest files do not match check-template.py BENCHMARK_FILES"
        )
    if measured["characters"] != validator_chars:
        raise BenchmarkError(
            "FAST_INIT mismatch: context benchmark={} check-template={}".format(
                measured["characters"], validator_chars
            )
        )

    baseline = {
        "name": "baseline",
        "input_tokens": 100,
        "output_tokens": 20,
        "thought_tokens": 10,
        "cached_tokens": 40,
        "tool_calls": 2,
        "turns": 2,
        "correctness_score": 5,
        "clarity_score": 5,
        "high_severity_findings": 0,
        "privacy_concern": False,
    }
    candidate = dict(baseline)
    candidate.update({"name": "candidate", "input_tokens": 75})
    good = compare_runs([validate_run(baseline, 0), validate_run(candidate, 1)], "candidate")
    if good["verdict"] != "ADOPT":
        raise BenchmarkError("self-test expected ADOPT for qualifying paired run")
    candidate["correctness_score"] = 4
    bad = compare_runs([validate_run(baseline, 0), validate_run(candidate, 1)], "candidate")
    if bad["verdict"] != "REJECT":
        raise BenchmarkError("self-test expected REJECT for correctness regression")
    malformed = dict(baseline)
    malformed.pop("turns")
    try:
        validate_run(malformed, 0)
    except BenchmarkError as err:
        if "turns" not in str(err):
            raise BenchmarkError("self-test malformed-record diagnostic was not useful")
    else:
        raise BenchmarkError("self-test accepted a malformed usage record")
    prompt_record = dict(baseline)
    prompt_record["prompt"] = "must not be echoed"
    try:
        validate_run(prompt_record, 0)
    except BenchmarkError as err:
        if "totals only" not in str(err):
            raise BenchmarkError("self-test prompt-field diagnostic was not useful")
    else:
        raise BenchmarkError("self-test accepted a prompt-bearing usage record")

    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_path = Path(temp_dir) / "invalid.json"
        invalid_path.write_text("{", encoding="utf-8")
        try:
            read_json(invalid_path, "usage record")
        except BenchmarkError as err:
            if "valid JSON" not in str(err):
                raise BenchmarkError("self-test malformed-JSON diagnostic was not useful")
        else:
            raise BenchmarkError("self-test accepted malformed JSON")

        empty_path = Path(temp_dir) / "empty.json"
        empty_path.write_text(
            json.dumps({"schema_version": 1, "scenario": "fast-init", "runs": []}),
            encoding="utf-8",
        )
        try:
            load_usage(empty_path, "fast-init")
        except BenchmarkError as err:
            if "non-empty runs list" not in str(err):
                raise BenchmarkError("self-test empty-record diagnostic was not useful")
        else:
            raise BenchmarkError("self-test accepted an empty usage record")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure explicit context scenarios and compare manual usage totals."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--scenario", help="Scenario id; omit to measure all scenarios.")
    parser.add_argument("--usage", type=Path, help="Sanitized manual usage JSON record.")
    parser.add_argument("--candidate", help="Named candidate run from the usage record.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic harness tests.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test:
            run_self_test()
            if args.json:
                print(json.dumps({"self_test": "PASS"}, sort_keys=True))
            else:
                print("Context benchmark self-test passed.")
            return 0
        scenarios = load_manifest(args.manifest)
        result = build_result(scenarios, args.scenario, args.usage, args.candidate)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print_result(result)
        return 0
    except BenchmarkError as err:
        print("error: {}".format(err), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
