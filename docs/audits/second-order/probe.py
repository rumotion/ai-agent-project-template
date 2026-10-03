#!/usr/bin/env python3
"""Read-only baseline probes; payloads are inspected, never sent to a remote.

Run from any directory: python docs/audits/second-order/probe.py
Temporary repositories and synthetic memory contain no real secrets.
"""
from __future__ import annotations

import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def main():
    remote = module("remote_guard", "scripts/hooks/guard-remote-ops.py")
    sensitive = module("sensitive_guard", "scripts/hooks/guard-sensitive-paths.py")
    ctx = module("context_compiler", "scripts/ctx.py")
    schemas = module("contract_validator", "scripts/validate-schemas.py")
    out = {"baseline": "6ea5081", "remote": [], "sensitive": [], "context": [], "schemas": [], "pre_push": []}
    cases = [
        ("comment-heredoc", "# <<EOF\ngit push", True),
        ("quoted-heredoc-opener", "printf '%s\\n' '<<EOF'\ngit push", True),
        ("expanding-heredoc", "cat <<EOF\n$(git push)\nEOF", True),
        ("quoted-heredoc-data", "cat <<'EOF'\ngit push\nEOF", False),
        ("wrapper-options", "env -i git push", True),
        ("wrapper-path", "/usr/bin/env git push", True),
        ("timeout-wrapper", "timeout 10 git push", True),
        ("function-prefix", "f() { git push; }; f", True),
        ("git-alias", "git -c alias.pp=push pp", True),
        ("hook-config-write", "git config core.hooksPath /dev/null", True),
        ("git-config-env", "git --config-env=alias.pp=PUSH_ALIAS pp", True),
        ("hub-push", "hub push", True),
        ("gh-stdin-post", "gh api repos/o/r/issues --input payload.json", True),
        ("gh-upper-field", "gh api repos/o/r/issues -F title=x", True),
        ("gh-graphql-mutation", "gh api graphql --input mutation.json", True),
        ("gh-comment", "gh issue comment 1 --body x", True),
        ("gh-raw-read-false-positive", "gh api -X GET search/issues -f q=repo:o/r", False),
        ("python-exe-version", 'python3.9 -c "import os; os.system(\'git push\')"', True),
        ("python-split-code", 'python -c "import subprocess; subprocess.run([\'git\', \'pu\'+\'sh\'])"', True),
        ("print-code-false-positive", 'python -c "print(\'git push\')"', False),
        ("remote-config-read-false-positive", "git config --get remote.origin.url", False),
        ("quoted-program-false-positive", 'git" "push', False),
        ("ordinary-push", "git -c core.hooksPath=/dev/null push", True),
    ]
    nested = "git push"
    import shlex
    for _ in range(7):
        nested = "sh -c " + shlex.quote(nested)
    cases.append(("depth-cap", nested, True))
    for name, command, expected in cases:
        got = remote.is_blocked(command)
        out["remote"].append({"id": name, "command": command, "expected_block": expected, "blocked": got, "defect": got != expected})
    sensitive_cases = [
        ("redirection-cmd-key", {"cmd": "echo demo > .env"}, True),
        ("redirection-commandline-key", {"CommandLine": "echo demo > .env"}, True),
        ("cp-options", {"command": "cp -f src .env"}, True),
        ("tee-options", {"command": "printf demo | tee --append .env"}, True),
        ("tee-multiple", {"command": "printf demo | tee notes.txt .env"}, True),
        ("quoted-space-path", {"command": 'echo demo > "private dir/.env"'}, True),
        ("powershell-set-content", {"command": "Set-Content -LiteralPath .env -Value demo"}, True),
        ("python-write", {"command": 'python -c "open(\'.env\',\'w\').write(\'demo\')"'}, True),
        ("trailing-command-punctuation", {"command": "echo demo > secret.key; echo done"}, True),
        ("path-normalization-fp", {"file_path": ".env/../safe.txt"}, False),
        ("quoted-data-fp", {"command": "printf '%s' 'example > .env'"}, False),
        ("starter-policy-restriction", {"command": "cp examples/sample .env.example"}, True),
    ]
    for name, event_input, expected in sensitive_cases:
        paths = sensitive.extract_paths({"tool_input": event_input})
        got = any(sensitive.is_sensitive(path) for path in paths)
        out["sensitive"].append({"id": name, "input": event_input, "paths": paths, "expected_block": expected, "blocked": got, "defect": got != expected})

    def record(rid, kind="risk", body="Keep this risk", superseded="", priority="1"):
        return "---\nid: {}\ntype: {}\npriority: {}\nsuperseded_by: {}\n---\n{}\n".format(rid, kind, priority, superseded, body)

    context_cases = [
        ("duplicate-id", [record("same"), record("same", body="Contradictory risk")]),
        ("cycle", [record("a", superseded="b"), record("b", superseded="a")]),
        ("self-supersede", [record("a", superseded="a")]),
        ("missing-successor", [record("a", superseded="missing")]),
        ("bom-record", ["\ufeff" + record("a")]),
        ("empty-front-matter", ["---\n---\nbody"]),
        ("duplicate-key", [record("a").replace("type: risk", "type: decision\ntype: fact")]),
        ("unicode-body", [record("a", body="風險🙂" * 150)]),
        ("unicode-digit", [record("a", priority="¹")]),
        ("semantic-truncation", [record("a", kind="decision", body="x" * 401 + " NEVER PUBLISH")]),
        ("drop-successor", [record("old", kind="decision", superseded="new"), record("new", kind="fact", body="replacement" * 40)]),
    ]
    with tempfile.TemporaryDirectory(prefix="second-order-memory-") as tmp:
        root = Path(tmp)
        records = root / "memory-bank" / "records"
        records.mkdir(parents=True)
        for name, contents in context_cases:
            for path in records.glob("*.md"):
                path.unlink()
            for index, content in enumerate(contents):
                (records / (str(index) + ".md")).write_text(content, encoding="utf-8")
            try:
                result = ctx.compile_context(root, "claude", 350 if name == "drop-successor" else 6000)
                result.pop("blob_sha256")
                out["context"].append({"id": name, "result": result})
            except Exception as err:
                out["context"].append({"id": name, "exception": type(err).__name__, "message": str(err)})
            if name in ("unicode-body", "unicode-digit"):
                proc = subprocess.run([sys.executable, str(ROOT / "scripts/ctx.py"), "compile", "--root", str(root), "--for", "claude", "--check"], text=True, capture_output=True)
                out["context"][-1]["cli_exit_code"] = proc.returncode
                out["context"][-1]["cli_last_error"] = proc.stderr.splitlines()[-1] if proc.stderr else ""
        for path in records.glob("*.md"):
            path.unlink()
        (records / "a.md").write_text(record("a"), encoding="utf-8")
        handoff = root / "memory-bank" / "handoff.md"
        handoff.write_text("\ufeff---\nstatus: blocked\nblocking_issues: critical\n---\n", encoding="utf-8")
        out["context"].append({"id": "bom-handoff", "status": ctx.load_handoff_status(root)})
        handoff.write_text("---\nstatus: before\n---\n", encoding="utf-8")
        before = ctx.compile_context(root, "claude", 6000)["blob"]
        handoff.write_text("---\nstatus: after\n---\n", encoding="utf-8")
        after = ctx.compile_context(root, "claude", 6000)["blob"]
        prefix = os.path.commonprefix([before, after])
        out["context"].append({"id": "status-prefix-churn", "common_prefix_chars": len(prefix), "total_chars": len(before)})
        out["context"].append({"id": "missing-root", "result": ctx.compile_context(root / "absent", "claude", 6000)})

    task_schema = schemas.load_json(ROOT / "schemas/subagent-task.schema.json")
    task = schemas.load_json(ROOT / "schemas/examples/task-valid.json")
    for name, edits in [
        ("path-traversal", {"owned_paths": ["../../outside"], "inputs": ["SECRET_TEXT=demo"]}),
        ("memory-worker", {"owned_paths": ["memory-bank/handoff.md"]}),
        ("contradictory-paths", {"owned_paths": ["src/a.py"], "forbidden_paths": ["src/a.py"]}),
        ("false-masking", {"isolation": {"context_policy": "envelope-only", "mask_secrets": False, "memory_bank_writes": "parent-only"}}),
        ("read-only-empty-owner", {"read_only": True, "owned_paths": []}),
    ]:
        value = copy.deepcopy(task)
        value.update(edits)
        out["schemas"].append({"id": name, "errors": schemas.validate(value, task_schema, "task")})
    for name, value, schema in [
        ("unsupported-const", "wrong", {"type": "string", "const": "right"}),
        ("number-bounds", 99.5, {"type": "number", "maximum": 1}),
        ("nonfinite-number", float("nan"), {"type": "number", "maximum": 1}),
    ]:
        out["schemas"].append({"id": name, "errors": schemas.validate(value, schema, "probe")})
    result_schema = schemas.load_json(ROOT / "schemas/subagent-result.schema.json")
    result = schemas.load_json(ROOT / "schemas/examples/result-valid.json")
    result["summary"] = "word " * 150
    result["files_changed"] = [{"path": "x" * 10000, "action": "modified"}] * 50
    out["schemas"].append({"id": "uncapped-result", "summary_words": 150, "serialized_chars": len(json.dumps(result)), "errors": schemas.validate(result, result_schema, "result")})

    git = Path(shutil.which("git") or "git")
    sh_candidates = [git.parent.parent / "bin/sh.exe", git.parent / "sh.exe"]
    sh = next((str(p) for p in sh_candidates if p.is_file()), shutil.which("sh"))
    out["environment"] = {"python": sys.version.split()[0], "platform": sys.platform, "sh": sh}
    if sh:
        base_env = dict(os.environ)
        markers = "CLAUDECODE CURSOR_AGENT_ID GEMINI_CLI COPILOT_AGENT ROO_CODE CODEX_SANDBOX AGENT AGENT_ID ALLOW_AGENT_PUSH".split()
        for marker in markers:
            base_env.pop(marker, None)
        for name, updates, url in [
            ("human", {}, "https://example.invalid/project"),
            ("agent", {"CLAUDECODE": "1"}, "https://example.invalid/project"),
            ("template", {}, "https://example.invalid/ai-agent-project-template"),
            ("escape-template", {"CLAUDECODE": "1", "ALLOW_AGENT_PUSH": "1"}, "https://example.invalid/ai-agent-project-template"),
            ("unlisted-client", {"WINDSURF_AGENT": "1"}, "https://example.invalid/project"),
        ]:
            proc = subprocess.run([sh, str(ROOT / "scripts/hooks/git/pre-push"), "origin", url], env=dict(base_env, **updates), input="", text=True, capture_output=True)
            out["pre_push"].append({"id": name, "exit_code": proc.returncode})
        # A shell function records invocation. No real git command runs.
        shell = "git() { printf 'MOCK_GIT:%s\\n' \"$*\"; };\n"
        for name in ("comment-heredoc", "quoted-heredoc-opener", "expanding-heredoc", "quoted-program-false-positive"):
            command = next(command for cid, command, _ in cases if cid == name)
            proc = subprocess.run([sh, "-c", shell + command], text=True, capture_output=True)
            out.setdefault("shell_semantics", []).append({"id": name, "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
    # End-to-end Git proof uses only newly created synthetic repositories on disk.
    with tempfile.TemporaryDirectory(prefix="second-order-git-") as tmp:
        fixture = Path(tmp)
        source = fixture / "source"
        bare = fixture / "receiver.git"
        source.mkdir()
        def run_git(args, cwd=source, env=None):
            return subprocess.run([str(git)] + args, cwd=cwd, env=env, text=True, capture_output=True)
        run_git(["init", "--bare", str(bare)], fixture).check_returncode()
        run_git(["init"]).check_returncode()
        (source / "demo.txt").write_text("synthetic audit fixture\n", encoding="utf-8")
        run_git(["add", "demo.txt"]).check_returncode()
        run_git(["-c", "user.name=Audit Fixture", "-c", "user.email=audit@example.com", "commit", "-m", "fixture"]).check_returncode()
        hook = source / ".git" / "hooks" / "pre-push"
        hook.write_bytes((ROOT / "scripts/hooks/git/pre-push").read_bytes().replace(b"\r\n", b"\n"))
        hook.chmod(0o755)
        env = dict(os.environ, CLAUDECODE="1")
        env.pop("ALLOW_AGENT_PUSH", None)
        local_cases = [
            ("normal-agent", ["push", str(bare), "HEAD:refs/heads/normal"]),
            ("alias-and-hooksPath", ["-c", "alias.pp=push", "-c", "core.hooksPath=/dev/null", "pp", str(bare), "HEAD:refs/heads/alias"]),
            ("alias-and-no-verify", ["-c", "alias.pp=push", "pp", "--no-verify", str(bare), "HEAD:refs/heads/noverify"]),
            ("send-pack", ["send-pack", str(bare), "HEAD:refs/heads/plumbing"]),
        ]
        for name, args in local_cases:
            got = run_git(args, env=env)
            command = "git " + " ".join(args)
            out.setdefault("local_git", []).append({"id": name, "exit_code": got.returncode, "guard_blocked": remote.is_blocked(command), "stderr": got.stderr.replace(str(fixture), "<temporary-fixture>")})
        # Installer assumes .git is a directory; worktrees use a .git file.
        init = module("fast_init", "scripts/init-fast.py")
        worktree = fixture / "worktree"
        run_git(["worktree", "add", "-b", "audit-worktree", str(worktree)]).check_returncode()
        (worktree / "scripts/hooks/git").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts/hooks/git/pre-push", worktree / "scripts/hooks/git/pre-push")
        hook.unlink()  # only our synthetic hook, to observe installation
        init.ROOT = worktree
        init.install_push_backstop()
        out["installers"] = [{"id": "linked-worktree", "dot_git_is_file": (worktree / ".git").is_file(), "hook_installed": hook.exists()}]
        init.ROOT = source
        (source / "scripts/hooks/git").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts/hooks/git/pre-push", source / "scripts/hooks/git/pre-push")
        hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        init.install_push_backstop()
        out["installers"].append({"id": "existing-permissive-hook", "preserved_permissive": "exit 0" in hook.read_text(encoding="utf-8")})
        crlf = b"#!/bin/sh\r\nexit 1\r\n"
        hashed = subprocess.run([str(git), "hash-object", "-w", "--stdin"], cwd=source, input=crlf, capture_output=True, check=True).stdout.decode().strip()
        raw = subprocess.run([str(git), "cat-file", "blob", hashed], cwd=source, capture_output=True, check=True).stdout
        normalized = run_git(["cat-file", "blob", hashed]).stdout
        out["lf_gate"] = {"committed_blob_has_cr": b"\r" in raw, "text_mode_has_cr": "\r" in normalized}
        project = fixture / "new-project"
        author_env = dict(os.environ, GIT_AUTHOR_NAME="Audit Fixture", GIT_AUTHOR_EMAIL="audit@example.com", GIT_COMMITTER_NAME="Audit Fixture", GIT_COMMITTER_EMAIL="audit@example.com")
        created = subprocess.run([sys.executable, str(ROOT / "scripts/new-project.py"), str(project), "--name", "Audit Fixture"], env=author_env, text=True, capture_output=True)
        out["new_project"] = {"exit_code": created.returncode, "hook_exists": (project / ".git/hooks/pre-push").is_file(), "records": sorted(p.name for p in (project / "memory-bank/records").glob("*.md")), "active_mcp": [p for p in (".mcp.json", ".vscode/mcp.json", ".agents/mcp_config.json") if (project / p).exists()]}
    # Syntax compatibility is necessary, not a claim of a Python 3.9 runtime run.
    changed = subprocess.run(["git", "diff", "--name-only", "dc09876", "6ea5081", "--", "*.py"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    syntax_errors = []
    for relative in changed:
        try:
            ast.parse((ROOT / relative).read_text(encoding="utf-8"), feature_version=(3, 9))
        except SyntaxError as err:
            syntax_errors.append({"path": relative, "line": err.lineno, "error": str(err)})
    out["python39_syntax"] = {"files": len(changed), "errors": syntax_errors}
    print(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    main()
