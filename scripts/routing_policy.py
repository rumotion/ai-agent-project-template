"""Offline, advisory worker/advisor routing; no dispatch or action authority."""
import argparse
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 32768
ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SHA = re.compile(r"^[a-f0-9]{64}$")


def fields(value, allowed, required):
    if not isinstance(value, dict) or set(value) - set(allowed) or not set(required) <= set(value):
        raise ValueError("invalid fields")


def validate(data):
    required = {"schema_version", "task_id", "task_revision", "attempt_id", "artifact_sha256", "checkpoint",
                "material", "permission", "evidence_current", "model_available",
                "advisor_available", "budget", "hard_budget", "verification", "retry_count", "errors"}
    fields(data, required | {"advisor_requested", "advisor_receipts"}, required)
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("invalid version")
    for key in ("task_id", "attempt_id"):
        if not isinstance(data[key], str) or not ID.fullmatch(data[key]):
            raise ValueError("invalid identity")
    if not isinstance(data["artifact_sha256"], str) or not SHA.fullmatch(data["artifact_sha256"]):
        raise ValueError("invalid artifact")
    if type(data["task_revision"]) is not int or not 1 <= data["task_revision"] <= 10**12:
        raise ValueError("invalid task revision")
    for key in ("material", "evidence_current", "model_available", "advisor_available", "hard_budget"):
        if type(data[key]) is not bool:
            raise ValueError("invalid flag")
    if type(data.get("advisor_requested", False)) is not bool:
        raise ValueError("invalid request")
    for key, choices in {"checkpoint": {"routine", "plan", "completion"},
                         "permission": {"allowed", "denied", "unknown"},
                         "budget": {"ready", "hold", "unknown"},
                         "verification": {"passed", "failed", "unknown"}}.items():
        if not isinstance(data[key], str) or data[key] not in choices:
            raise ValueError("invalid state")
    if type(data["retry_count"]) is not int or not 0 <= data["retry_count"] <= 1000:
        raise ValueError("invalid retry count")
    if not isinstance(data["errors"], list) or len(data["errors"]) > 32:
        raise ValueError("invalid error history")
    seen = set()
    for error in data["errors"]:
        required_error = {"task_id", "task_revision", "attempt_id", "event_id", "kind", "signature"}
        fields(error, required_error, required_error)
        for key in ("task_id", "attempt_id", "event_id"):
            if not isinstance(error[key], str) or not ID.fullmatch(error[key]):
                raise ValueError("invalid error identity")
        if error["kind"] not in ("logic", "transient", "permission"):
            raise ValueError("invalid error kind")
        if type(error["task_revision"]) is not int or not 1 <= error["task_revision"] <= 10**12:
            raise ValueError("invalid error revision")
        identity = tuple(error[key] for key in ("task_id", "task_revision", "attempt_id", "event_id"))
        if identity in seen:
            raise ValueError("duplicate error event")
        seen.add(identity)
        if not isinstance(error["signature"], str) or not SHA.fullmatch(error["signature"]):
            raise ValueError("invalid error signature")
    receipts = data.get("advisor_receipts", [])
    if not isinstance(receipts, list) or len(receipts) > 8:
        raise ValueError("invalid review history")
    for receipt in receipts:
        required_receipt = {"task_id", "task_revision", "attempt_id", "artifact_sha256", "checkpoint", "verdict"}
        fields(receipt, required_receipt | {"error_signature", "error_count", "error_event_id"}, required_receipt)
        for key in ("task_id", "attempt_id"):
            if not isinstance(receipt[key], str) or not ID.fullmatch(receipt[key]):
                raise ValueError("invalid receipt identity")
        for key in ("artifact_sha256", "error_signature"):
            if key in receipt and (not isinstance(receipt[key], str) or not SHA.fullmatch(receipt[key])):
                raise ValueError("invalid receipt fingerprint")
        if type(receipt["task_revision"]) is not int or not 1 <= receipt["task_revision"] <= 10**12:
            raise ValueError("invalid receipt revision")
        if receipt["checkpoint"] not in ("plan", "completion", "error", "requested") or receipt["verdict"] not in ("accept", "revise"):
            raise ValueError("invalid receipt state")
        if receipt["checkpoint"] == "error" and ("error_signature" not in receipt or type(receipt.get("error_count")) is not int or not 2 <= receipt["error_count"] <= 32
                                               or not isinstance(receipt.get("error_event_id"), str) or not ID.fullmatch(receipt["error_event_id"])):
            raise ValueError("missing reviewed error")
        if receipt["checkpoint"] != "error" and any(key in receipt for key in ("error_signature", "error_count", "error_event_id")):
            raise ValueError("unexpected reviewed error")


def advice(route, reason):
    return {"schema_version": 1, "route": route, "reason": reason,
            "advisory_only": True, "authorizes_action": False,
            "dispatch_performed": False, "acceptance_performed": False}


def decide(data):
    """Consume coordinator declarations, never provider attestation or permission."""
    validate(data)
    if data["permission"] != "allowed":
        return advice("hold", "permission_unavailable")
    if not data["evidence_current"]:
        return advice("hold", "stale_evidence")
    if data["budget"] == "hold" or (data["hard_budget"] and data["budget"] != "ready"):
        return advice("hold", "budget_unavailable")
    if not data["model_available"]:
        return advice("hold", "model_unavailable")
    errors = [item for item in data["errors"] if
              all(item[key] == data[key] for key in ("task_id", "task_revision", "attempt_id"))]
    latest = errors[-1] if errors else None
    if latest and latest["kind"] == "permission":
        return advice("hold", "permission_denial")
    if latest and latest["kind"] == "transient":
        return advice("retry", "transient_backoff") if data["retry_count"] < 3 else advice("hold", "retry_limit")
    checkpoints = []
    error_count = sum(item["kind"] == "logic" and item["signature"] == latest["signature"] for item in errors) if latest and latest["kind"] == "logic" else 0
    if error_count >= 2:
        checkpoints.append("error")
    if data["checkpoint"] in ("plan", "completion") and data["material"]:
        checkpoints.append(data["checkpoint"])
    if data.get("advisor_requested", False):
        checkpoints.append("requested")
    for checkpoint in checkpoints:
        matches = [receipt for receipt in data.get("advisor_receipts", []) if
                   all(receipt.get(key) == data[key] for key in ("task_id", "task_revision", "attempt_id", "artifact_sha256"))
                   and receipt["checkpoint"] == checkpoint
                   and (checkpoint != "error" or (receipt["error_signature"] == latest["signature"] and receipt["error_count"] == error_count
                                                  and receipt["error_event_id"] == latest["event_id"]))]
        if not matches:
            return advice("advisor", checkpoint + "_review_required") if data["advisor_available"] else advice("hold", "advisor_unavailable")
        if any(receipt["verdict"] == "revise" for receipt in matches):
            return advice("worker", "apply_advisor_findings")
    if data["checkpoint"] == "completion":
        return advice("parent_review", "checks_and_advice_ready") if data["verification"] == "passed" else advice("worker", "verification_required")
    return advice("worker", "continue_within_existing_scope")


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate field")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Explicit sanitized observation JSON; no discovery")
    args = parser.parse_args()
    try:
        if args.input.is_symlink():
            raise ValueError("linked input")
        with args.input.open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("oversized input")
        result = decide(json.loads(raw.decode("utf-8"), object_pairs_hook=unique))
        code = 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        result, code = advice("hold", "invalid_observation"), 2
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
