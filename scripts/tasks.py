"""Private cooperative task ledger; no dispatch, command execution or authority.

Uses existing portable envelopes and coordinator-declared verification. File
audits cover Git-eligible tracked/untracked files, not ignored files or external
processes. Native stop/ownership enforcement is deliberately not supplied.
"""
from datetime import datetime, timezone
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

import continuity
from contract_checks import allowed_write, relative_path, result_errors, task_errors

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("envelope_validator", HERE / "validate-schemas.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
STATES = {"queued", "running", "review", "accepted", "blocked", "cancelled"}
OPEN = {"running", "review", "blocked"}
MAX_TASKS = 1000
MAX_FILES = 10000
MAX_INVENTORY_BYTES = 2_097_152
SCHEMAS = {kind: json.loads((HERE.parent / ("schemas/subagent-" + kind + ".schema.json")).read_text(encoding="utf-8")) for kind in ("task", "result")}
STATE_SCHEMA = json.loads((HERE.parent / "schemas/task-state.schema.json").read_text(encoding="utf-8"))


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def atomic_json(path, value, limit=continuity.MAX_RECEIPT_BYTES):
    data = encoded(value)
    if len(data) > limit:
        raise ValueError("private document exceeds bound")
    fd, name = tempfile.mkstemp(prefix=".task-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def private_directory(root, path):
    path = Path(path).absolute()
    try:
        path.resolve().relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("task state must be outside project")
    for candidate in (path, *path.parents):
        if candidate.is_symlink() or (candidate.exists() and getattr(candidate.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("linked task storage")
    return path


def envelope(value, kind, root):
    errors = validator.validate(value, SCHEMAS[kind], kind)
    if not errors and kind == "task":
        # Input existence is checked only at admission; a valid task may delete
        # an input later. Continue enforcing canonical paths and link scope.
        errors += task_errors(value)
        for key in ("owned_paths", "forbidden_paths", "inputs"):
            for name in value.get(key, []):
                relative_path(name, root, allow_glob=key != "inputs")
    if errors:
        raise ValueError("invalid portable envelope")


def inventory(root, inputs=()):
    state = continuity.git_state(root)
    proc = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root, capture_output=True, timeout=20, check=True)
    names = sorted(set(filter(None, proc.stdout.decode("utf-8").split("\0"))) | set(inputs))
    if len(names) > MAX_FILES or len({name.casefold() for name in names}) != len(names):
        raise ValueError("inventory too large or case-ambiguous")
    files = {}
    total = 0
    for name in names:
        relative_path(name, root)
        if continuity.SENSITIVE.search(name) and Path(name).name != ".env.example":
            raise ValueError("sensitive tracked input requires manual reconciliation")
        path = root / name
        if not path.exists() and not path.is_symlink():
            continue
        data = continuity.compiler.read_source_bytes(root, name, 1_048_576)
        total += len(data)
        if total > 67_108_864:
            raise ValueError("inventory byte budget exceeded")
        files[name] = continuity.digest(data + (":" + str(path.stat().st_mode & 0o777)).encode("ascii"))
    if state != continuity.git_state(root):
        raise ValueError("Git state changed during inventory")
    return {"files": files, "git": state}


def changed_files(before, after):
    return {name: "added" if name not in before else "deleted" if name not in after else "modified"
            for name in before.keys() | after.keys() if before.get(name) != after.get(name)}


def overlaps(left, right):
    # Conservative: uncertain glob intersections retain ownership rather than
    # pretending to provide exact path-lease enforcement.
    def prefix(pattern):
        return re.split(r"[*?\[]", pattern.casefold(), maxsplit=1)[0]
    return any(prefix(a).startswith(prefix(b)) or prefix(b).startswith(prefix(a)) for a in left for b in right)


class TaskStore:
    def __init__(self, root, state_dir=None):
        self.root = Path(root).resolve()
        self.project = continuity.project_id(self.root)
        self.directory = private_directory(self.root, state_dir or continuity.default_receipt(self.root).parent / "tasks")

    def _path(self, task_id):
        if not isinstance(task_id, str) or not continuity.ID_RE.fullmatch(task_id):
            raise ValueError("invalid task ID")
        return self.directory / (task_id + ".task.json")

    def read(self, task_id):
        value = continuity.bounded_json(self._path(task_id))
        if validator.validate(value, STATE_SCHEMA, "state"):
            raise ValueError("invalid task-state schema")
        required = {"schema_version", "project_id", "task", "owner", "revision", "state", "attempt", "attempt_id", "depends_on", "baseline_sha256", "review_sha256", "history", "next_action"}
        if (not isinstance(value, dict) or not required.issubset(value)
                or set(value) - required - {"result", "parent_verification"}
                or type(value["schema_version"]) is not int or value["schema_version"] != 1
                or value["project_id"] != self.project or value["state"] not in STATES
                or type(value["revision"]) is not int or value["revision"] < 1
                or type(value["attempt"]) is not int or value["attempt"] < 0
                or not isinstance(value["owner"], str) or not continuity.ID_RE.fullmatch(value["owner"])
                or not isinstance(value["history"], list) or len(value["history"]) > 32):
            raise ValueError("invalid task state")
        envelope(value["task"], "task", self.root)
        if value["task"]["task_id"] != task_id:
            raise ValueError("task identity mismatch")
        deps = value["depends_on"]
        if not isinstance(deps, list) or len(deps) > 32 or any(not isinstance(dep, str) or not continuity.ID_RE.fullmatch(dep) for dep in deps) or len(set(deps)) != len(deps) or task_id in deps:
            raise ValueError("invalid dependency identities")
        for key in ("baseline_sha256", "review_sha256"):
            if not isinstance(value[key], str) or (value[key] and not continuity.HASH_RE.fullmatch(value[key])):
                raise ValueError("invalid task evidence digest")
        if not isinstance(value["attempt_id"], str) or (value["attempt_id"] and not re.fullmatch(r"[a-f0-9]{32}", value["attempt_id"])):
            raise ValueError("invalid attempt identity")
        history = value["history"]
        if len(history) != value["revision"]:
            raise ValueError("task history does not match revision")
        for index, event in enumerate(history, 1):
            if (not isinstance(event, dict) or set(event) != {"action", "revision", "at"}
                    or type(event["revision"]) is not int or event["revision"] != index
                    or event["action"] not in {"create", "start", "submit", "accept", "block", "cancel", "note"}
                    or not isinstance(event["at"], str) or not event["at"]):
                raise ValueError("invalid task history")
        expected_action = {"queued": "create", "running": "start", "review": "submit", "accepted": "accept", "blocked": "block", "cancelled": "cancel"}[value["state"]]
        actions = [item["action"] for item in history if item["action"] != "note"]
        if not actions or actions[0] != "create" or actions[-1] != expected_action:
            raise ValueError("task state contradicts history")
        if not isinstance(value["next_action"], str) or not value["next_action"].strip() or len(value["next_action"]) > 300:
            raise ValueError("invalid next action")
        if value["attempt"] > value["task"]["budget"]["max_repairs"] + 1:
            raise ValueError("task attempt budget exceeded")
        if value["attempt"] == 0:
            if value["state"] not in {"queued", "blocked", "cancelled"} or value["attempt_id"] or value["baseline_sha256"] or value["review_sha256"] or "result" in value:
                raise ValueError("task lacks required attempt evidence")
        elif not value["attempt_id"] or not value["baseline_sha256"]:
            raise ValueError("attempt evidence missing")
        if value["state"] in {"review", "accepted"} and (not value["review_sha256"] or "result" not in value):
            raise ValueError("review evidence missing")
        if value["state"] == "running" and (value["review_sha256"] or "result" in value):
            raise ValueError("running attempt retains stale evidence")
        for key in ("result", "parent_verification"):
            if key in value:
                envelope(value[key], "result", self.root)
                if result_errors(value[key], value["task"], self.root) or value[key]["status"] != "completed":
                    raise ValueError("invalid saved verification")
        if (value["state"] == "accepted") != ("parent_verification" in value):
            raise ValueError("acceptance lacks parent verification")
        return value

    def all(self):
        paths = sorted(self.directory.glob("*.task.json"))
        if len(paths) > MAX_TASKS:
            raise ValueError("task capacity exceeded")
        values = {path.name[:-10]: self.read(path.name[:-10]) for path in paths}
        # Topological check is iterative, including on manually corrupted state.
        remaining = {tid: set(task["depends_on"]) for tid, task in values.items()}
        if any(not deps.issubset(values) for deps in remaining.values()):
            raise ValueError("missing dependency")
        while remaining:
            ready = {tid for tid, deps in remaining.items() if not deps}
            if not ready:
                raise ValueError("dependency cycle")
            remaining = {tid: deps - ready for tid, deps in remaining.items() if tid not in ready}
        return values

    def _save(self, value, action):
        value["history"].append({"action": action, "revision": value["revision"], "at": datetime.now(timezone.utc).isoformat()})
        if len(value["history"]) > 32:
            raise ValueError("task history capacity reached")
        atomic_json(self._path(value["task"]["task_id"]), value)
        return self.summary(value)

    @staticmethod
    def summary(value):
        return {key: value[key] for key in ("owner", "revision", "state", "attempt", "attempt_id", "depends_on", "review_sha256", "next_action")} | {"task_id": value["task"]["task_id"], "objective": value["task"]["objective"]}

    def create(self, task, owner="lead", depends_on=()):
        envelope(task, "task", self.root)
        if not continuity.ID_RE.fullmatch(owner):
            raise ValueError("invalid owner")
        task_id = task["task_id"]
        self.directory.mkdir(parents=True, exist_ok=True)
        with continuity.write_lock(self.directory / "registry.json"):
            existing = self.all()
            if len(existing) >= MAX_TASKS or self._path(task_id).exists() or self._path(task_id).is_symlink():
                raise ValueError("task capacity or identity collision")
            if len(depends_on) > 32 or len(set(depends_on)) != len(depends_on) or any(dep not in existing for dep in depends_on):
                raise ValueError("dependencies must already exist")
            for relative in task.get("inputs", []):
                if not (self.root / relative).is_file():
                    raise ValueError("missing concrete input")
            value = {"schema_version": 1, "project_id": self.project, "task": task,
                     "owner": owner, "revision": 1, "state": "queued", "attempt": 0,
                     "attempt_id": "", "depends_on": list(depends_on), "baseline_sha256": "",
                     "review_sha256": "", "history": [], "next_action": (task.get("expected_output", "").strip() or task["objective"].strip())[:300]}
            if not value["next_action"]:
                raise ValueError("empty task objective")
            return self._save(value, "create")

    def _baseline_path(self, value):
        return self.directory / (value["task"]["task_id"] + "." + value["attempt_id"] + ".inventory.json")

    def _baseline(self, value):
        path = self._baseline_path(value)
        if path.is_symlink():
            raise ValueError("linked baseline")
        with path.open("rb") as handle:
            raw = handle.read(MAX_INVENTORY_BYTES + 1)
        if len(raw) > MAX_INVENTORY_BYTES or continuity.digest(raw) != value["baseline_sha256"]:
            raise ValueError("baseline missing or changed")
        parsed = json.loads(raw.decode("utf-8"))
        if not isinstance(parsed, dict) or set(parsed) != {"files", "git"} or not isinstance(parsed["files"], dict):
            raise ValueError("invalid baseline")
        return parsed

    def transition(self, task_id, action, revision, owner="lead", attempt_id=None,
                   result=None, verification=None, stopped=False, next_action=None):
        with continuity.write_lock(self.directory / "registry.json"):
            tasks = self.all()
            value = tasks[task_id]
            if type(revision) is not int or revision != value["revision"] or owner != value["owner"]:
                raise ValueError("stale revision or owner mismatch")
            task = value["task"]
            state = value["state"]
            if action == "start":
                if state not in ("queued", "blocked") or (state == "blocked" and not stopped):
                    raise ValueError("start requires queued state or reconciled stopped attempt")
                if any(tasks[dep]["state"] != "accepted" for dep in value["depends_on"]):
                    raise ValueError("dependency not accepted")
                others = [item for tid, item in tasks.items() if tid != task_id and item["state"] in OPEN]
                if any(item["state"] == "running" for item in others) or len(others) >= 2:
                    raise ValueError("one running worker and two open tasks maximum")
                if any(overlaps(task["owned_paths"], item["task"]["owned_paths"]) for item in others):
                    raise ValueError("owned paths conflict")
                if value["attempt"] >= task["budget"]["max_repairs"] + 1:
                    raise ValueError("repair budget exhausted")
                value.update(state="running", attempt=value["attempt"] + 1, attempt_id=uuid.uuid4().hex,
                             review_sha256="")
                value.pop("result", None)
                value.pop("parent_verification", None)
                baseline = inventory(self.root, task.get("inputs", []))
                raw = encoded(baseline)
                path = self._baseline_path(value)
                if path.exists() or path.is_symlink():
                    raise ValueError("attempt baseline collision")
                atomic_json(path, baseline, MAX_INVENTORY_BYTES)
                value["baseline_sha256"] = continuity.digest(raw)
            elif action in ("submit", "accept"):
                expected = "running" if action == "submit" else "review"
                if state != expected or not attempt_id or attempt_id != value["attempt_id"]:
                    raise ValueError("wrong state or stale attempt")
                current = inventory(self.root, task.get("inputs", []))
                baseline = self._baseline(value)
                changes = changed_files(baseline["files"], current["files"])
                if any(not allowed_write(name, task, self.root) for name in changes):
                    raise ValueError("observed out-of-scope write; preserve and reconcile")
                artifact = continuity.digest(encoded(current))
                candidate = result if action == "submit" else verification
                envelope(candidate, "result", self.root)
                if result_errors(candidate, task, self.root) or candidate["status"] != "completed":
                    raise ValueError("unsuccessful or invalid result evidence")
                declared = {item["path"]: item["action"] for item in candidate["files_changed"]}
                if len(declared) != len(candidate["files_changed"]) or declared != changes:
                    raise ValueError("declared writes differ from observed changes")
                if action == "submit":
                    value.update(state="review", review_sha256=artifact, result=candidate)
                else:
                    if artifact != value["review_sha256"]:
                        raise ValueError("review artifacts changed; reverify before acceptance")
                    value.update(state="accepted", parent_verification=candidate)
            elif action in ("block", "cancel"):
                if state in ("accepted", "cancelled") or (state != "queued" and (not stopped or attempt_id != value["attempt_id"])):
                    raise ValueError("terminal state or missing stop reconciliation")
                if action == "block" and state not in OPEN:
                    others = [item for tid, item in tasks.items() if tid != task_id and item["state"] in OPEN]
                    if len(others) >= 2 or any(overlaps(task["owned_paths"], item["task"]["owned_paths"]) for item in others):
                        raise ValueError("open-task capacity or ownership conflict")
                value["state"] = "blocked" if action == "block" else "cancelled"
            elif action == "note":
                if state in {"accepted", "cancelled"} or not isinstance(next_action, str) or not next_action.strip() or len(next_action) > 300:
                    raise ValueError("invalid task checkpoint note")
                value["next_action"] = next_action
            else:
                raise ValueError("unsupported transition")
            value["revision"] += 1
            return self._save(value, action)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE.parent)
    parser.add_argument("--state-dir", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--envelope", type=Path, required=True)
    create.add_argument("--depends-on", action="append", default=[])
    listing = sub.add_parser("list")
    listing.add_argument("--offset", type=int, default=0)
    listing.add_argument("--all", action="store_true")
    for action in ("start", "submit", "accept", "block", "cancel", "show", "note"):
        command = sub.add_parser(action)
        command.add_argument("task_id")
        if action == "show":
            command.add_argument("--details", action="store_true")
        if action != "show":
            command.add_argument("--revision", type=int, required=True)
            command.add_argument("--attempt")
            command.add_argument("--result", type=Path)
            command.add_argument("--verification", type=Path)
            command.add_argument("--stopped", action="store_true")
            command.add_argument("--owner", default="lead")
            command.add_argument("--next-action")
    create.add_argument("--owner", default="lead")
    args = parser.parse_args()
    try:
        store = TaskStore(args.root, args.state_dir)
        if args.command == "create":
            output = store.create(continuity.bounded_json(args.envelope), args.owner, args.depends_on)
        elif args.command == "show":
            value = store.read(args.task_id)
            output = value if args.details else store.summary(value)
        elif args.command == "list":
            if args.offset < 0:
                raise ValueError("invalid cursor")
            items = sorted((item for item in store.all().values() if args.all or item["state"] not in {"accepted", "cancelled"}), key=lambda item: item["task"]["task_id"])
            output = {"tasks": [store.summary(item) for item in items[args.offset:args.offset + 32]],
                      "next_offset": args.offset + 32 if len(items) > args.offset + 32 else None}
        else:
            output = store.transition(args.task_id, args.command, args.revision, args.owner, args.attempt,
                                      continuity.bounded_json(args.result) if args.result else None,
                                      continuity.bounded_json(args.verification) if args.verification else None,
                                      args.stopped, args.next_action)
        code = 0
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError):
        output, code = {"status": "blocked", "issue": "task_operation_refused; inspect revision, scope, dependency, evidence and writer state"}, 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
