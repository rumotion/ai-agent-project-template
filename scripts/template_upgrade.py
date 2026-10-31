"""Conservative template transport and file updates. No third-party dependencies.

Only explicit manifest paths are candidates. Unknown/local changes are conflicts.
Backups and reports live outside the project; no upstream code is executed here.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tarfile
import tempfile
from urllib.parse import urlsplit

STATE = ".template-upstream.json"


def linked(path):
    if path.is_symlink():
        return True
    # Path.is_junction is unavailable on Python 3.9. Detect Windows reparse
    # points too, including junctions that redirect to another project path.
    try:
        return bool(getattr(path.lstat(), "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
    except FileNotFoundError:
        return False


def digest(data):
    # Git line-ending conversion should not create spurious local conflicts.
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def checked_path(root, relative):
    parts = PurePosixPath(relative).parts
    if (not parts or PurePosixPath(relative).is_absolute() or "\\" in relative
            or any(p in ("..", ".git") or ":" in p for p in parts)):
        raise ValueError("Unsafe manifest path")
    path = root
    for part in parts:
        path = path / part
        if linked(path):
            raise ValueError("Linked path is unsupported: " + relative)
    path.resolve().relative_to(root.resolve())
    return path


def load_state(target):
    path = checked_path(target, STATE)
    if not path.exists():
        return {"schema": 1, "files": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(state, dict) or state.get("schema") != 1
            or not isinstance(state.get("source", {}), dict)
            or not isinstance(state.get("files"), dict)
            or any(not isinstance(k, str) or not isinstance(v, str)
                   or not re.fullmatch(r"[a-f0-9]{64}", v)
                   for k, v in state["files"].items())):
        raise ValueError("Invalid template upstream state")
    if any(not isinstance(v, str) for v in state.get("source", {}).values()):
        raise ValueError("Invalid template source metadata")
    return state


def with_baseline(state, candidates):
    """Adopt only file hashes from an explicitly selected trusted older release."""
    result = dict(state, files=dict(state["files"]))
    for relative, data in candidates.items():
        result["files"].setdefault(relative, digest(data))
    return result


def validate_url(url):
    # Permit GitHub, GitLab and self-hosted GitLab. Reject credentials in HTTPS
    # URLs, Git's executable remote helpers, local transports and option injection.
    if not isinstance(url, str) or any(c.isspace() for c in url):
        raise ValueError("Use an HTTPS or SSH repository URL without credentials")
    if re.fullmatch(r"git@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+", url):
        return url
    parsed = urlsplit(url)
    if (parsed.scheme not in ("https", "ssh") or not parsed.hostname
            or parsed.password or parsed.query or parsed.fragment
            or (parsed.username and not (parsed.scheme == "ssh" and parsed.username == "git"))
            or not parsed.path.strip("/")):
        raise ValueError("Use an HTTPS or SSH repository URL without credentials")
    return url


def git(args, cwd):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(["git", *args], cwd=cwd, env=env,
                            capture_output=True, timeout=120)
    if result.returncode:
        # Do not echo credential helpers, private URLs, or server diagnostics.
        raise ValueError("Git source read failed; check repository access and ref locally")
    return result.stdout


def extract_archive(data, destination):
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        members = archive.getmembers()
        if sum(m.size for m in members) > 50_000_000:
            raise ValueError("Template archive exceeds 50 MB")
        for member in members:
            path = checked_path(destination, member.name)
            if not (member.isfile() or member.isdir()):
                raise ValueError("Template archive contains links or special files")
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.extractfile(member).read())


@contextmanager
def source_tree(url, ref="HEAD", expect_commit=None):
    validate_url(url)
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_./-]*", ref) or ".." in ref:
        raise ValueError("Invalid Git ref")
    if expect_commit and not re.fullmatch(r"[a-fA-F0-9]{40,64}", expect_commit):
        raise ValueError("Expected commit must be a full SHA")
    with tempfile.TemporaryDirectory(prefix="template-source-") as folder:
        root = Path(folder)
        # A bare fetch/archive avoids checkout filters, hooks and submodules.
        git(["init", "--bare", "."], root)
        git(["-c", "core.hooksPath=/dev/null", "fetch", "--depth=1", "--no-tags",
             "--", url, ref], root)
        commit = git(["rev-parse", "FETCH_HEAD^{commit}"], root).decode().strip()
        if expect_commit and commit.lower() != expect_commit.lower():
            raise ValueError("Upstream moved since preview; repeat the dry-run")
        destination = root / "source"
        destination.mkdir()
        extract_archive(git(["archive", "--format=tar", commit], root), destination)
        for required in ("AGENTS.md", "scripts/upgrade-target.py", "workflows/upgrade-project.md"):
            if not checked_path(destination, required).is_file():
                raise ValueError("Source is not an AI Agent Project Template")
        yield destination, {"url": url, "ref": ref, "commit": commit}


def plan_upgrade(target, candidates, state):
    plan = []
    for relative, data in sorted(candidates.items()):
        try:
            path = checked_path(target, relative)
            if path.exists() and not path.is_file():
                raise ValueError("Destination is not a regular file")
            before = path.read_bytes() if path.exists() else None
            old_hash = digest(before) if before is not None else None
            if before is None:
                action = "add"
            elif old_hash == digest(data):
                action = "unchanged"
            elif relative.startswith("memory-bank/"):
                action = "preserve"
            elif state["files"].get(relative) == old_hash:
                action = "update"
            else:
                action = "conflict"
            plan.append({"path": relative, "action": action, "before": old_hash,
                         "after": digest(data)})
        except ValueError:
            plan.append({"path": relative, "action": "conflict", "reason": "unsafe destination"})
    # A custom skill owns its whole directory, including supporting files.
    blocked = set()
    groups = set()
    for entry in plan:
        parts = PurePosixPath(entry["path"]).parts
        if len(parts) >= 4 and parts[1] == "skills":
            group = "/".join(parts[:3])
            groups.add(group)
            if entry["action"] == "conflict":
                blocked.add(group)
    for group in groups - blocked:
        directory = checked_path(target, group)
        if directory.is_dir():
            for path in directory.rglob("*"):
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                relative = path.relative_to(target).as_posix()
                if linked(path):
                    blocked.add(group)
                elif path.is_file() and relative not in candidates:
                    installed = state["files"].get(relative)
                    if installed is None or digest(path.read_bytes()) != installed:
                        blocked.add(group)
    for entry in plan:
        if any(entry["path"].startswith(group + "/") for group in blocked):
            entry["action"] = "conflict"
    return plan


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=".template-write-", dir=str(path.parent))
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def apply_plan(target, candidates, state, plan, source, apply_safe=False, backup_parent=None):
    target = target.resolve()
    conflicts = [p for p in plan if p["action"] == "conflict"]
    if conflicts and not apply_safe:
        return 1, ["Conflicts; no files changed: " + ", ".join(p["path"] for p in conflicts)]
    updates = [p for p in plan if p["action"] in ("add", "update")]
    new_state = {"schema": 1, "source": source, "files": dict(state["files"])}
    for entry in plan:
        if entry["action"] in ("add", "update", "unchanged"):
            new_state["files"][entry["path"]] = entry["after"]
    metadata = (json.dumps(new_state, indent=2, sort_keys=True) + "\n").encode()
    state_path = checked_path(target, STATE)
    if not updates and state_path.is_file() and state_path.read_bytes() == metadata:
        return (2 if conflicts else 0), ["No changes", *["Conflict: " + p["path"] for p in conflicts]]
    parent = Path(backup_parent or tempfile.gettempdir()).resolve()
    if parent == target or target in parent.parents:
        raise ValueError("Backup directory must be outside target; use --backup-dir")
    backup = Path(tempfile.mkdtemp(prefix="template-upgrade-", dir=str(parent)))
    report = {"source": source, "target": str(target), "plan": plan, "status": "prepared"}
    (backup / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    written = []
    try:
        writes = [(p["path"], candidates[p["path"]], p["before"]) for p in updates]
        previous_state = state_path.read_bytes() if state_path.exists() else None
        writes.append((STATE, metadata, digest(previous_state) if previous_state is not None else None))
        for relative, data, expected in writes:
            path = checked_path(target, relative)
            before = path.read_bytes() if path.exists() else None
            if (digest(before) if before is not None else None) != expected:
                raise ValueError("Target changed after preview: " + relative)
            if before is not None:
                saved = backup / "files" / relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(before)
            atomic_write(path, data)
            written.append((relative, before))
        report["status"] = "applied_with_conflicts" if conflicts else "applied"
    except Exception:
        for relative, before in reversed(written):
            path = checked_path(target, relative)
            if before is None:
                path.unlink()
            else:
                atomic_write(path, before)
        report["status"] = "rolled_back"
        raise
    finally:
        (backup / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return (2 if conflicts else 0), ["Backup/report: " + str(backup),
                                   *[p["action"] + ": " + p["path"] for p in updates + conflicts]]
