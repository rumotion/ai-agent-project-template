#!/usr/bin/env python3
"""Context Compiler: build a deterministic, budget-capped, cache-stable
startup blob from the typed Memory Bank.

Instead of every agent re-reading prose memory files in a model-dependent
order, `ctx.py compile` renders a single, byte-stable context blob from:

* `memory-bank/handoff.md` front-matter (status, task, next_action,
  blocking_issues), and
* typed records in `memory-bank/records/*.md`:

      ---
      id: kebab-case-id
      type: fact | decision | risk | preference
      priority: 1-5     # 1 = keep-alive, 5 = drop first when over budget
      superseded_by: optional-record-id
      ---

Section order is fixed (status -> decisions -> risks -> facts ->
preferences; then priority, then id). An over-budget blob drops droppable
records (preferences first, then facts, highest priority number first) but
never decision, risk, or status records. Output is deterministic: the same
memory compiles to the same bytes, so repeated sessions maximize
prompt-cache prefix hits instead of paying for re-read variance.

Usage:

    python scripts/ctx.py compile --for claude [--max-chars N] [--json] [--check]
    python scripts/ctx.py self-test

Exit codes: 0 ok, 1 over-budget or malformed records (in every compile mode; or
always in self-test failure), 2 usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]

TYPE_RANK = {"decision": 0, "risk": 1, "fact": 2, "preference": 3}
DROPPABLE_TYPES = {"fact", "preference"}
RECORD_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
REFERENCE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
DEFAULT_MAX_CHARS = 6_000
MAX_SOURCE_BYTES = 16_384
MAX_RECORDS = 10_000

CLIENT_NOTES = {
    "claude": "AGENTS.md is already imported via CLAUDE.md; do not re-read it.",
    "gemini": "AGENTS.md is already imported via GEMINI.md; do not re-read it.",
    "codex": "AGENTS.md is already loaded; do not re-read it.",
    "cline": "AGENTS.md and the .clinerules pointers are already loaded; do not re-read them.",
    "cursor": "AGENTS.md is already loaded via the rules adapter; do not re-read it.",
    "antigravity": "AGENTS.md and the .agents/rules are already loaded; do not re-read them.",
    "generic": "AGENTS.md is already in your context; do not re-read it.",
}


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    """Parse a minimal `key: value` front-matter block. Returns ({}, text) if absent."""
    lines = text.lstrip('\ufeff').splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        closing = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        raise ValueError('unterminated front matter')
    fields: Dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line != line.lstrip() or ":" not in line:
            raise ValueError("front matter supports single-line scalars only")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) or key in fields:
            raise ValueError("invalid or duplicate front-matter key")
        quoted = value.startswith(("\"", "'"))
        if value.startswith('"'):
            value = json.loads(value)
            if not isinstance(value, str):
                raise ValueError("front matter requires scalar strings")
        elif value.startswith("'"):
            if len(value) < 2 or not value.endswith("'"):
                raise ValueError("unterminated scalar quote")
            value = value[1:-1].replace("''", "'")
        if any(ord(c) < 32 for c in value):
            raise ValueError("control character in metadata")
        empty_optional_list = value == "[]" and key in ("files_modified", "blocking_issues")
        if not quoted and value.startswith(("|", ">", "[", "{", "&", "*", "!")) and not empty_optional_list:
            raise ValueError("unsupported front-matter structure")
        fields[key] = value
    body = "\n".join(lines[closing + 1:])
    return fields, body


def read_source_bytes(root: Path, relative: str, max_bytes: int = MAX_SOURCE_BYTES) -> bytes:
    """Bound reads and reject linked sources, including Windows junctions."""
    root = root.resolve()
    path = root / relative
    path.resolve().relative_to(root)
    cursor = root
    for part in Path(relative).parts:
        cursor = cursor / part
        attrs = cursor.lstat()
        if cursor.is_symlink() or getattr(attrs, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError("linked context source")
    if not stat.S_ISREG(attrs.st_mode):
        raise ValueError("context source must be a regular file")
    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("context source exceeds byte limit")
    return data


def read_source(root: Path, relative: str) -> str:
    return read_source_bytes(root, relative).decode("utf-8-sig")


def load_handoff_status(root: Path) -> Dict[str, str]:
    handoff = root / "memory-bank" / "handoff.md"
    status: Dict[str, str] = {}
    if not handoff.exists() and not handoff.is_symlink():
        return status
    fields, _ = parse_front_matter(read_source(root, "memory-bank/handoff.md"))
    if not fields or not fields.get("status", "").strip():
        raise ValueError("handoff requires scalar status")
    for key in ("status", "task", "next_action", "blocking_issues"):
        value = fields.get(key, "").strip()
        if value and value.lower() not in ("[]", "none", "tbd"):
            status[key] = value
    return status


def load_records(root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load and validate typed records. Returns (records, errors)."""
    records_dir = root / "memory-bank" / "records"
    records: List[Dict[str, Any]] = []
    errors: List[str] = []
    if not records_dir.is_dir():
        return records, ['missing memory-bank/records directory']
    paths = sorted(records_dir.glob("*.md"))
    if len(paths) > MAX_RECORDS:
        return [], ["record inventory exceeds 10000 entries"]
    for path in paths:
        try:
            raw = read_source_bytes(root, path.relative_to(root).as_posix())
            fields, body = parse_front_matter(raw.decode("utf-8-sig"))
            metadata = record_metadata(fields)
        except (OSError, ValueError):
            errors.append("{}: unreadable or malformed record".format(path.relative_to(root).as_posix()))
            continue
        rel = path.relative_to(root).as_posix()
        record_id = fields.get("id", "")
        record_type = fields.get("type", "")
        priority_raw = fields.get("priority", "")
        if not RECORD_ID_RE.fullmatch(record_id):
            errors.append("{}: front-matter needs a kebab-case `id`".format(rel))
            continue
        if record_type not in TYPE_RANK:
            errors.append("{}: `type` must be one of {}".format(rel, sorted(TYPE_RANK)))
            continue
        if not re.fullmatch(r"[1-5]", priority_raw):
            errors.append("{}: `priority` must be an integer 1-5".format(rel))
            continue
        if not body.strip():
            errors.append("{}: record body is empty".format(rel))
            continue
        records.append(
            {
                "id": record_id,
                "type": record_type,
                "priority": int(priority_raw),
                "superseded_by": fields.get("superseded_by", "").strip(),
                "body": " ".join(body.split()),
                "raw_body": body,
                "path": rel,
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                **metadata,
            }
        )
    return records, errors


def record_metadata(fields: Dict[str, str]) -> Dict[str, Any]:
    scope = fields.get("scope", "global")
    category = fields.get("category", fields.get("type", ""))
    tasks_raw = fields.get("tasks", "")
    tasks = tasks_raw.split(",") if tasks_raw else []
    if scope not in ("global", "task", "archive"):
        raise ValueError("unknown record scope")
    if len(tasks) > 32 or len(set(tasks)) != len(tasks) or any(not REFERENCE_RE.fullmatch(item) for item in tasks):
        raise ValueError("invalid task references")
    if (scope == "task" and not tasks) or (scope != "task" and tasks):
        raise ValueError("task references require task scope")
    if category != fields.get("type") and not (fields.get("type") == "fact" and category in ("example", "hypothesis")):
        raise ValueError("record category conflicts with its type")
    source = fields.get("source_ref", "")
    if source and not REFERENCE_RE.fullmatch(source):
        raise ValueError("source_ref must be an opaque bounded ID")
    return {"scope": scope, "category": category, "tasks": tasks, "source_ref": source}


def get_record(root: Path, record_id: str) -> Dict[str, Any]:
    records, errors = load_records(root)
    if errors:
        raise ValueError("record archive is malformed")
    active_records(records)
    found = [record for record in records if record["id"] == record_id]
    if len(found) != 1:
        raise ValueError("record ID not found")
    return found[0]


def store_record(root: Path, record_id: str, record_type: str, body: str,
                 scope: str = "global", task_ids=None, category=None,
                 source_ref: str = "", priority: int = 1) -> Dict[str, Any]:
    """Create a reviewed immutable record and return a read-back receipt."""
    root = root.resolve()
    if not RECORD_ID_RE.fullmatch(record_id) or record_type not in TYPE_RANK or type(priority) is not int or priority not in range(1, 6):
        raise ValueError("invalid record identity, type or priority")
    if not isinstance(body, str) or not body.strip() or not REFERENCE_RE.fullmatch(source_ref):
        raise ValueError("record requires a body and opaque source reference")
    if task_ids is not None and (not isinstance(task_ids, list) or any(not isinstance(item, str) for item in task_ids)):
        raise ValueError("invalid task references")
    fields = {"id": record_id, "type": record_type, "priority": str(priority),
              "scope": scope, "tasks": ",".join(task_ids or []),
              "category": category or record_type, "source_ref": source_ref}
    record_metadata(fields)
    raw = ("---\n" + "\n".join(key + ":" + (" " + value if value else "") for key, value in fields.items()) + "\n---\n" + body + ("" if body.endswith("\n") else "\n")).encode("utf-8")
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("record exceeds source byte limit")
    directory = root / "memory-bank/records"
    directory.resolve().relative_to(root)
    for path in (root / "memory-bank", directory):
        if path.exists() and (path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("linked record directory")
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / ".record-write.lock"
    try:
        lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("record writer lock exists; reconcile first") from None
    temporary = None
    try:
        os.close(lock_fd)
        records, errors = load_records(root)
        if errors:
            raise ValueError("existing archive malformed")
        active_records(records)
        if len(records) >= MAX_RECORDS:
            raise ValueError("record capacity reached; preserve and reconcile archive")
        target = directory / (record_id + ".md")
        collision = any(path.name.casefold() == target.name.casefold() for path in directory.iterdir())
        if collision or any(record["id"] == record_id for record in records):
            raise ValueError("record ID already exists; preserve history")
        fd, temporary = tempfile.mkstemp(prefix=".record-", suffix=".tmp", dir=str(directory))
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        stored = get_record(root, record_id)
        if stored["source_sha256"] != hashlib.sha256(raw).hexdigest():
            raise ValueError("record read-back mismatch")
        projection_task = (task_ids or [None])[0]
        result = compile_context(root, "generic", DEFAULT_MAX_CHARS, task_id=projection_task)
        return {"stored": True, "id": record_id, "path": stored["path"],
                "source_sha256": stored["source_sha256"], "scope": scope,
                "category": stored["category"], "projection_task": result["task_id"],
                "included": not (result["malformed"] or result["over_budget"]) and record_id in result["included"],
                "projection_state": "blocked" if result["malformed"] or result["over_budget"] else "valid"}
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
        lock.unlink()


def active_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Require a unique, acyclic, same-type supersession graph."""
    by_id: Dict[str, Dict[str, Any]] = {}
    for record in records:
        rid = record["id"]
        if rid in by_id:
            raise ValueError("duplicate record id")
        by_id[rid] = record
    for record in records:
        target = record["superseded_by"]
        if target:
            if target not in by_id or target == record["id"]:
                raise ValueError("missing successor or self supersession")
            if by_id[target]["type"] != record["type"]:
                raise ValueError("supersession must preserve record type")
            if by_id[target].get("category") != record.get("category"):
                raise ValueError("supersession must preserve category")
    done = set()
    for rid in by_id:
        chain = set()
        cursor = rid
        while cursor and cursor not in done:
            if cursor in chain:
                raise ValueError("supersession cycle")
            chain.add(cursor)
            cursor = by_id[cursor]["superseded_by"]
        done.update(chain)
    return ([r for r in records if not r["superseded_by"]],
            [r for r in records if r["superseded_by"]])


def render_blob(status: Dict[str, str], records: List[Dict[str, Any]]) -> str:
    """Render the deterministic blob body (status + typed records)."""
    lines: List[str] = []
    if status:
        lines.append("## Status")
        for key in ("status", "task", "next_action", "blocking_issues"):
            if key in status:
                lines.append("{}: {}".format(key.replace("_", " "), status[key]))
        lines.append("")
    for record_type in ("decision", "risk", "fact", "preference"):
        group = [r for r in records if r["type"] == record_type]
        if not group:
            continue
        lines.append("## {}s".format(record_type.capitalize()))
        for record in group:
            labels = []
            if record.get("category", record_type) != record_type:
                labels.append(record["category"])
            if record.get("source_ref"):
                labels.append("source=" + record["source_ref"])
            tag = " [" + "; ".join(labels) + "]" if labels else ""
            lines.append(
                "- {id} p{priority}{tag}: {body}".format(
                    id=record["id"], priority=record["priority"], tag=tag, body=record["body"]
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def build_blob(client: str, status: Dict[str, str], records: List[Dict[str, Any]]) -> str:
    note = CLIENT_NOTES.get(client, CLIENT_NOTES["generic"])
    header = (
        "# Compiled project context (for {})\n"
        "# Validated projection of source records; current user instructions take precedence.\n"
        "# {}\n"
    ).format(client, note)
    # Global guidance is stable across tasks; selected task/archive records and
    # current status form a dynamic suffix, without claiming provider savings.
    global_records = [r for r in records if r.get("scope", "global") == "global"]
    task_records = [r for r in records if r.get("scope", "global") != "global"]
    task_body = "## Task context\n" + render_blob({}, task_records) if task_records else ""
    body = "\n\n".join(part for part in (render_blob({}, global_records), task_body, render_blob(status, [])) if part)
    if not body:
        return header.rstrip()
    return header + "\n" + body + "\n"


def distill(
    client: str,
    status: Dict[str, str],
    records: List[Dict[str, Any]],
    max_chars: int,
    required_ids=None,
) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]], bool]:
    """Drop droppable records (worst first) until the blob fits the budget.

    Returns (blob, kept, dropped, over_budget). Decision, risk, and status
    records are never dropped; if the blob still exceeds max_chars the
    result is over_budget and the caller decides how harshly to fail.
    """
    kept = sorted(records, key=lambda r: (TYPE_RANK[r["type"]], r["priority"], r["id"]))
    dropped: List[Dict[str, Any]] = []
    blob = build_blob(client, status, kept)
    while len(blob) > max_chars:
        candidates = [r for r in kept if r["type"] in DROPPABLE_TYPES and r["id"] not in (required_ids or [])]
        if not candidates:
            return blob, kept, dropped, True
        worst = max(candidates, key=lambda r: (TYPE_RANK[r["type"]], r["priority"], r["id"]))
        kept.remove(worst)
        dropped.append(worst)
        blob = build_blob(client, status, kept)
    return blob, kept, dropped, False


def compile_context(root: Path, client: str, max_chars: int, task_id=None, required_ids=None) -> Dict[str, Any]:
    status: Dict[str, str] = {}
    records: List[Dict[str, Any]] = []
    errors: List[str] = []
    active: List[Dict[str, Any]] = []
    superseded: List[Dict[str, Any]] = []
    excluded: List[str] = []
    required = set()
    if max_chars < 1:
        errors.append("max_chars must be positive")
    try:
        if required_ids is not None and not isinstance(required_ids, (list, tuple, set)):
            raise ValueError("required IDs must be a collection")
        required.update(required_ids or [])
        status = load_handoff_status(root)
        if (root / "memory-bank/handoff.md").exists():
            handoff, _ = parse_front_matter(read_source(root, "memory-bank/handoff.md"))
            task_id = task_id or handoff.get("task_id") or None
            required.update(filter(None, handoff.get("required_records", "").split(",")))
        if task_id is not None and not REFERENCE_RE.fullmatch(task_id):
            raise ValueError("invalid task identity")
        if len(required) > 64 or any(not isinstance(item, str) or not RECORD_ID_RE.fullmatch(item) for item in required):
            raise ValueError("invalid required record IDs")
        records, record_errors = load_records(root)
        errors.extend(record_errors)
        if not errors:
            active, superseded = active_records(records)
            if not required.issubset({record["id"] for record in active}):
                raise ValueError("required record missing or superseded")
            selected = []
            for record in active:
                matches_task = task_id is not None and record["scope"] == "task" and task_id in record["tasks"]
                if record["scope"] == "global" or matches_task or record["id"] in required:
                    selected.append(record)
                    if matches_task:
                        required.add(record["id"])
                else:
                    excluded.append(record["id"])
            active = selected
    except (OSError, ValueError, TypeError):
        errors.append("invalid handoff or supersession graph")
    if errors:
        blob, kept, dropped, over_budget = "", [], [], False
    else:
        blob, kept, dropped, over_budget = distill(client, status, active, max_chars, required)
    return {
        "client": client, "blob": blob,
        "blob_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
        "chars": len(blob), "est_tokens": len(blob) // 4,
        "render_version": 3,
        "stable_prefix_chars": len(build_blob(client, {}, [r for r in kept if r["scope"] == "global"])) if not errors else 0,
        "stable_prefix_sha256": hashlib.sha256(build_blob(client, {}, [r for r in kept if r["scope"] == "global"]).encode("utf-8")).hexdigest() if not errors else None,
        "measured_tokens": None,
        "token_measurement": "unmeasured; est_tokens is a characters/4 heuristic",
        "max_chars": max_chars, "included": [r["id"] for r in kept],
        "dropped": [r["id"] for r in dropped],
        "superseded": [r["id"] for r in superseded],
        "malformed": errors, "over_budget": over_budget,
        "continuity_state": "blocked" if errors or over_budget else "degraded",
        "continuity_note": "Projection validation is not a resume receipt; use continuity.py doctor.",
        "task_id": task_id, "required_ids": sorted(required),
        "excluded": sorted(excluded), "exclusion_reason": "scope_not_selected",
        "source_hashes": {r["id"]: r["source_sha256"] for r in kept},
    }


def run_self_test() -> None:
    import tempfile

    def record(rid: str, rtype: str, priority: int, body: str, superseded_by: str = "") -> str:
        return "---\nid: {}\ntype: {}\npriority: {}\nsuperseded_by: {}\n---\n{}\n".format(
            rid, rtype, priority, superseded_by, body
        )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        records_dir = root / "memory-bank" / "records"
        records_dir.mkdir(parents=True)
        (root / "memory-bank" / "handoff.md").write_text(
            "---\nstatus: self-test\nnext_action: verify compiler\n---\n\n# Handoff\n",
            encoding="utf-8",
        )
        (records_dir / "a-decision.md").write_text(
            record("a-decision", "decision", 1, "Keep decisions forever"), encoding="utf-8"
        )
        (records_dir / "b-risk.md").write_text(
            record("b-risk", "risk", 1, "Risks stay too"), encoding="utf-8"
        )
        (records_dir / "c-fact.md").write_text(
            record("c-fact", "fact", 1, "Important fact that survives"), encoding="utf-8"
        )
        (records_dir / "d-fact.md").write_text(
            record("d-fact", "fact", 5, "Droppable fact"), encoding="utf-8"
        )
        (records_dir / "e-pref.md").write_text(
            record("e-pref", "preference", 5, "Droppable preference"), encoding="utf-8"
        )
        (records_dir / "f-old.md").write_text(
            record("f-old", "fact", 3, "Old fact", superseded_by="c-fact"), encoding="utf-8"
        )
        (records_dir / "z-bad.md").write_text(
            "---\nid: Bad Id\ntype: thought\npriority: 9\n---\nbroken", encoding="utf-8"
        )

        invalid = compile_context(root, "claude", DEFAULT_MAX_CHARS)
        assert invalid["malformed"] and invalid["blob"] == ""
        (records_dir / "z-bad.md").unlink()
        first = compile_context(root, "claude", DEFAULT_MAX_CHARS)
        second = compile_context(root, "claude", DEFAULT_MAX_CHARS)
        assert first["blob"] == second["blob"], "compile must be deterministic"
        assert first["blob_sha256"] == second["blob_sha256"]

        blob = first["blob"]
        assert (
            blob.index("## Decisions")
            < blob.index("## Risks")
            < blob.index("## Facts")
            < blob.index("## Status")
        ), "section order must be fixed"
        assert "f-old" not in blob, "superseded record must be excluded"
        assert "c-fact" in blob, "successor record must be included"
        assert not first["malformed"]
        assert "e-pref" in blob, "nothing should drop while under budget"
        assert "do not re-read" in blob, "client dedup note missing"

        tiny = compile_context(root, "claude", 420)
        assert "e-pref" not in tiny["blob"], "preferences must drop first"
        assert "d-fact" not in tiny["blob"], "priority-5 facts must drop before priority-1"
        assert "a-decision" in tiny["blob"] and "b-risk" in tiny["blob"], "decisions/risks never drop"
        assert not tiny["over_budget"], "fits once droppables are gone"

        cramped = compile_context(root, "claude", 240)
        assert cramped["over_budget"], "non-droppable remainder must be flagged over budget"
        assert "a-decision" in cramped["blob"] and "b-risk" in cramped["blob"], "decisions/risks never drop"

        # Unknown client is rejected by argparse choices, not a crash.
        try:
            result = compile_context(root, "not-a-client", DEFAULT_MAX_CHARS)
            assert "do not re-read" in result["blob"], "unknown clients fall back to generic note"
        except (KeyError, SystemExit):
            raise AssertionError("unknown client must not raise")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile", help="Compile the deterministic context blob.")
    compile_parser.add_argument("--for", dest="client", required=True, choices=sorted(CLIENT_NOTES))
    compile_parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    compile_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    compile_parser.add_argument("--task-id")
    compile_parser.add_argument("--require", action="append", default=[])
    compile_parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 on validation failure (retained for CLI compatibility).",
    )
    compile_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root override (used by tooling; defaults to this repo).",
    )
    sub.add_parser("self-test", help="Run the deterministic harness tests.")
    record = sub.add_parser("record", help="Create a reviewed record with a read-back receipt.")
    record.add_argument("--root", type=Path, default=ROOT)
    record.add_argument("--id", required=True)
    record.add_argument("--type", choices=sorted(TYPE_RANK), required=True)
    record.add_argument("--category")
    record.add_argument("--scope", choices=("global", "task", "archive"), default="global")
    record.add_argument("--task-id", action="append", default=[])
    record.add_argument("--source-ref", required=True)
    record.add_argument("--priority", type=int, default=1)
    record.add_argument("--body-file", type=Path, required=True)
    show = sub.add_parser("show", help="Retrieve a complete record by ID.")
    show.add_argument("--root", type=Path, default=ROOT)
    show.add_argument("--id", required=True)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()

    if args.command == "self-test":
        try:
            run_self_test()
        except AssertionError as err:
            print("FAIL: {}".format(err), file=sys.stderr)
            return 1
        print("Context compiler self-test passed.")
        return 0

    if args.command in ("record", "show"):
        try:
            if args.command == "show":
                result = get_record(args.root, args.id)
            else:
                if (args.body_file.is_symlink() or not stat.S_ISREG(args.body_file.stat().st_mode)
                        or re.search(r"(?i)^(\.env(?:\..*)?|credentials\.json|token\.json|id_rsa.*|id_ed25519.*)$|\.(pem|key|p12)$", args.body_file.name)):
                    raise ValueError("unsafe body source")
                with args.body_file.open("rb") as handle:
                    raw = handle.read(MAX_SOURCE_BYTES + 1)
                if len(raw) > MAX_SOURCE_BYTES:
                    raise ValueError("body source too large")
                result = store_record(args.root, args.id, args.type, raw.decode("utf-8-sig"),
                                      args.scope, args.task_id, args.category, args.source_ref, args.priority)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 1 if result.get("projection_state") == "blocked" else 0
        except (OSError, ValueError, TypeError):
            print(json.dumps({"error": "record_operation_failed", "recovery": "Inspect record identity, source, scope and writer lock; preserve existing data."}))
            return 1

    root = args.root if args.root is not None else ROOT
    result = compile_context(root, args.client, args.max_chars, args.task_id, args.require)

    if result["malformed"] or result["over_budget"]:
        # Machine mode preserves diagnostics, but never emits usable invalid context.
        result["blob"] = ""
        result["blob_sha256"] = hashlib.sha256(b"").hexdigest()
        result["projected_chars"] = result["chars"]
        result["chars"] = 0
        result["est_tokens"] = 0
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("ctx: invalid or over-budget context; inspect --json diagnostics", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["blob"], end="" if result["blob"].endswith("\n") else "\n")
        print(
            "ctx: {} chars (~{} tokens), sha256 {}, {} included, {} dropped, {} superseded".format(
                result["chars"],
                result["est_tokens"],
                result["blob_sha256"][:12],
                len(result["included"]),
                len(result["dropped"]),
                len(result["superseded"]),
            ),
            file=sys.stderr,
        )
        for error in result["malformed"]:
            print("ctx: malformed: {}".format(error), file=sys.stderr)

    if args.check and (result["malformed"] or result["over_budget"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
