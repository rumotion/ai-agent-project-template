"""Local continuity inspection and private checkpoints; no network/model calls.

Receipts attest to observed local files, never user authority or model
consumption. A checkpoint has a single writer; stale locks require deliberate
operator reconciliation and are never removed automatically.
"""
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("project_context", HERE / "ctx.py")
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)
MAX_RECEIPT_BYTES = 65_536
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HASH_RE = re.compile(r"^[a-f0-9]{64}$")
SENSITIVE = re.compile(r"(?i)(^|/)(\.env(?:\..*)?|credentials\.json|token\.json|id_rsa.*|id_ed25519.*|\.git|\.ssh|\.aws)(/|$)|\.(pem|key|p12)$")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def project_id(root):
    return digest(os.path.normcase(str(root.resolve())).encode("utf-8"))


def default_receipt(root):
    return Path.home() / ".agent-continuity" / project_id(root) / "checkpoint.json"


def bounded_json(path):
    if path.is_symlink():
        raise ValueError("linked receipt")
    with path.open("rb") as handle:
        data = handle.read(MAX_RECEIPT_BYTES + 1)
    if len(data) > MAX_RECEIPT_BYTES:
        raise ValueError("receipt too large")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate receipt field")
            result[key] = value
        return result
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique)


def validate_input(relative):
    if (not isinstance(relative, str) or not relative or len(relative) > 240
            or "\\" in relative or ":" in relative
            or any(ord(c) < 32 for c in relative)
            or PurePosixPath(relative).is_absolute()
            or any(p in ("", "..", ".") for p in relative.split("/"))
            or SENSITIVE.search(relative)):
        raise ValueError("invalid or sensitive checkpoint input")


def git_state(root):
    def read(args):
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=10)
        return proc.stdout.strip() if proc.returncode == 0 else None
    top = read(["rev-parse", "--show-toplevel"])
    if top is None or Path(top).resolve() != root.resolve():
        raise ValueError("project must be its own Git worktree")
    return {"branch": read(["symbolic-ref", "--short", "HEAD"]) or "",
            "head": read(["rev-parse", "--verify", "HEAD"]) or ""}


def source_digest(root, inputs):
    if not isinstance(inputs, list) or len(inputs) > 64 or len(set(inputs)) != len(inputs):
        raise ValueError("invalid checkpoint inputs")
    values = {}
    required = ["AGENTS.md", "memory-bank/handoff.md"]
    for name in sorted(set(required + inputs)):
        validate_input(name)
        # Inputs use the same bounded, link-rejecting reader as project memory.
        values[name] = digest(compiler.read_source_bytes(root, name, 1_048_576 if name in inputs else compiler.MAX_SOURCE_BYTES))
    record_paths = sorted((root / "memory-bank/records").glob("*.md"))
    if len(record_paths) > 10_000:
        raise ValueError("record inventory too large")
    for path in record_paths:
        relative = path.relative_to(root).as_posix()
        values[relative] = digest(compiler.read_source_bytes(root, relative))
    return digest(json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def observe_checkpoint_sources(root, client, inputs):
    before = source_digest(root, inputs)
    projection = compiler.compile_context(root, client, compiler.DEFAULT_MAX_CHARS)
    status = compiler.load_handoff_status(root)
    if projection["malformed"] or projection["over_budget"] or any(not status.get(key) for key in ("status", "task", "next_action")):
        raise ValueError("checkpoint requires valid context and complete handoff")
    state = git_state(root)
    after = source_digest(root, inputs)
    if before != after or state != git_state(root):
        raise ValueError("checkpoint sources changed during observation")
    return after, state, projection


def validate_receipt(value):
    expected = {"schema_version", "project_id", "task_id", "revision", "created_at", "inputs", "source_sha256", "git"}
    if not isinstance(value, dict) or set(value) != expected or type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("invalid receipt version or fields")
    if not isinstance(value["task_id"], str) or not ID_RE.fullmatch(value["task_id"]):
        raise ValueError("invalid receipt task")
    if type(value["revision"]) is not int or value["revision"] < 1:
        raise ValueError("invalid receipt revision")
    for key in ("project_id", "source_sha256"):
        if not isinstance(value[key], str) or not HASH_RE.fullmatch(value[key]):
            raise ValueError("invalid receipt digest")
    inputs = value["inputs"]
    if not isinstance(inputs, list) or len(inputs) > 64 or any(not isinstance(p, str) for p in inputs) or len(set(inputs)) != len(inputs):
        raise ValueError("invalid receipt inputs")
    for item in inputs:
        validate_input(item)
    state = value["git"]
    if not isinstance(state, dict) or set(state) != {"branch", "head"} or any(not isinstance(v, str) or len(v) > 240 for v in state.values()):
        raise ValueError("invalid receipt Git state")
    if not isinstance(value["created_at"], str):
        raise ValueError("invalid receipt time")
    created = datetime.fromisoformat(value["created_at"].replace("Z", "+00:00"))
    if created.tzinfo is None or created > datetime.now(timezone.utc) + timedelta(seconds=60):
        raise ValueError("invalid receipt time")
    return value


@contextmanager
def write_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(".lock")
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("checkpoint writer lock exists; reconcile before retry") from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def checkpoint(root, client, task_id, inputs, receipt_path):
    root = Path(root).resolve()
    receipt_path = Path(receipt_path)
    try:
        receipt_path.resolve().relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("checkpoint storage must be outside the project")
    cursor = receipt_path.absolute()
    for parent in (cursor, *cursor.parents):
        if parent.is_symlink() or (parent.exists() and getattr(parent.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("linked checkpoint storage")
    if not isinstance(task_id, str) or not ID_RE.fullmatch(task_id):
        raise ValueError("invalid task ID")
    with write_lock(receipt_path):
        revision = 1
        if receipt_path.exists():
            previous = validate_receipt(bounded_json(receipt_path))
            if previous["project_id"] != project_id(root):
                raise ValueError("checkpoint project mismatch")
            revision = previous["revision"] + 1
        fingerprint, state, _ = observe_checkpoint_sources(root, client, inputs)
        value = {"schema_version": 1, "project_id": project_id(root), "task_id": task_id,
                 "revision": revision, "created_at": datetime.now(timezone.utc).isoformat(),
                 "inputs": inputs, "source_sha256": fingerprint, "git": state}
        validate_receipt(value)
        data = json.dumps(value, indent=2, sort_keys=True).encode("utf-8")
        if len(data) > MAX_RECEIPT_BYTES:
            raise ValueError("checkpoint too large")
        fd, temporary = tempfile.mkstemp(prefix=".checkpoint-", dir=str(receipt_path.parent))
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, receipt_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return value


def doctor(root, client="generic", mode="legacy", receipt_path=None):
    root = Path(root).resolve()
    response = {"schema_version": 1, "status": "blocked", "scope": "local_projection_only",
                "mode": mode, "client": client, "native_delivery": "unknown",
                "observed_model": None, "observed_effort": None, "issues": [],
                "recovery": "Inspect project instructions and handoff; recover missing state before dependent edits."}
    try:
        if mode not in ("fresh", "legacy", "resume") or client not in compiler.CLIENT_NOTES:
            raise ValueError("unsupported inspection mode or client")
        compiler.read_source(root, "AGENTS.md")
        projection = compiler.compile_context(root, client, compiler.DEFAULT_MAX_CHARS)
        response["projection"] = {"sha256": projection["blob_sha256"], "chars": projection["chars"],
                                  "included_count": len(projection["included"])}
        if projection["malformed"] or projection["over_budget"]:
            response["issues"].append("invalid_or_over_budget_projection")
            return response
        if mode == "fresh":
            response.update(status="ready", recovery="Establish the task and acceptance criteria; checkpoint after meaningful progress.")
        elif mode == "legacy":
            response.update(status="degraded", issues=["legacy_state_has_no_validated_resume_receipt"],
                            recovery="Read the handoff and verify repository state; create a private checkpoint after reconciliation.")
        else:
            receipt = validate_receipt(bounded_json(Path(receipt_path) if receipt_path else default_receipt(root)))
            if receipt["project_id"] != project_id(root):
                raise ValueError("project mismatch")
            fingerprint, state, projection = observe_checkpoint_sources(root, client, receipt["inputs"])
            if receipt["git"] != state or receipt["source_sha256"] != fingerprint:
                response["issues"].append("checkpoint_inputs_or_git_state_changed")
                return response
            response.update(status="ready", task_id=receipt["task_id"], revision=receipt["revision"],
                            recovery="Resume the named task; revalidate evidence before claiming acceptance.")
    except (OSError, ValueError, TypeError, subprocess.SubprocessError):
        response["issues"].append("continuity_state_unavailable_or_invalid")
    return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE.parent)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("doctor")
    inspect.add_argument("--mode", choices=("fresh", "legacy", "resume"), default="legacy")
    save = sub.add_parser("checkpoint")
    save.add_argument("--task-id", required=True)
    save.add_argument("--input", action="append", default=[])
    for command in (inspect, save):
        command.add_argument("--client", choices=sorted(compiler.CLIENT_NOTES), default="generic")
        command.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.command == "doctor":
        result = doctor(args.root, args.client, args.mode, args.receipt)
        code = 1 if result["status"] == "blocked" else 0
    else:
        try:
            value = checkpoint(args.root, args.client, args.task_id, args.input, args.receipt or default_receipt(args.root))
            result = {"status": "checkpointed", "task_id": value["task_id"], "revision": value["revision"],
                      "source_sha256": value["source_sha256"], "native_delivery": "unknown"}
            code = 0
        except (OSError, ValueError, TypeError, subprocess.SubprocessError):
            result, code = {"status": "blocked", "issues": ["checkpoint_failed; inspect inputs and writer lock"]}, 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
