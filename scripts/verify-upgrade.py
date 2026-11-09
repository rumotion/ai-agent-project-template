"""Offline preservation, transaction and real Git transport regressions."""
from __future__ import annotations

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import template_upgrade as engine

spec = importlib.util.spec_from_file_location("upgrader", Path(__file__).with_name("upgrade-target.py"))
upgrade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upgrade)


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "project"
        self.target.mkdir()

    def snapshot(self):
        return {p.relative_to(self.target).as_posix(): p.read_bytes()
                for p in self.target.rglob("*") if p.is_file()}

    def apply(self, candidates, safe=False):
        state = engine.load_state(self.target)
        plan = engine.plan_upgrade(self.target, candidates, state)
        return engine.apply_plan(self.target, candidates, state, plan,
                                 {"kind": "local"}, safe, str(self.root))

    def test_dry_run_does_not_change_target(self):
        before = self.snapshot()
        code, messages = upgrade.upgrade_project(self.target, dry_run=True)
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(messages[0])["plan"])
        self.assertEqual(self.snapshot(), before)

    def test_domain_rules_memory_and_active_configs_are_preserved(self):
        fixtures = {"app.py": b"domain", "tests/test_domain.py": b"tests",
                    "package.json": b"project dependencies", ".env": b"TBD",
                    ".claude/settings.json": b"project hooks", ".vscode/tasks.json": b"build",
                    "AGENTS.md": b"# Database safety\nNever drop production tables.\n",
                    "memory-bank/startup.md": b"Project Alpha", "memory-bank/handoff.md": b"Resume Alpha"}
        for relative, data in fixtures.items():
            path = self.target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        code, _ = upgrade.upgrade_project(self.target, apply_safe=True)
        self.assertEqual(code, 2)
        for relative, data in fixtures.items():
            self.assertEqual((self.target / relative).read_bytes(), data, relative)

    def test_conflicts_stop_before_any_write(self):
        (self.target / "AGENTS.md").write_text("custom instructions", encoding="utf-8")
        before = self.snapshot()
        code, messages = upgrade.upgrade_project(self.target)
        self.assertEqual(code, 1)
        self.assertIn("no files changed", messages[0])
        self.assertEqual(before, self.snapshot())

    def test_repeat_is_idempotent_and_managed_files_update(self):
        self.assertEqual(self.apply({"docs/tool.md": b"one\n"})[0], 0)
        before = self.snapshot()
        code, messages = self.apply({"docs/tool.md": b"one\n"})
        self.assertEqual((code, messages), (0, ["No changes"]))
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.apply({"docs/tool.md": b"two\n"})[0], 0)
        self.assertEqual((self.target / "docs/tool.md").read_bytes(), b"two\n")

    def test_local_edit_is_never_overwritten(self):
        self.apply({"docs/tool.md": b"one"})
        (self.target / "docs/tool.md").write_bytes(b"local change")
        before = self.snapshot()
        self.assertEqual(self.apply({"docs/tool.md": b"upstream change"})[0], 1)
        self.assertEqual(self.snapshot(), before)

    def test_legacy_baseline_updates_exact_old_files_only(self):
        candidates = {"AGENTS.md": b"new rules", "docs/tool.md": b"new tool"}
        (self.target / "AGENTS.md").write_bytes(b"old rules plus project rules")
        (self.target / "docs").mkdir()
        (self.target / "docs/tool.md").write_bytes(b"old tool")
        state = engine.with_baseline(engine.load_state(self.target),
                                     {"AGENTS.md": b"old rules", "docs/tool.md": b"old tool"})
        plan = engine.plan_upgrade(self.target, candidates, state)
        self.assertEqual({p["path"]: p["action"] for p in plan},
                         {"AGENTS.md": "conflict", "docs/tool.md": "update"})
        code, _ = engine.apply_plan(self.target, candidates, state, plan,
                                    {"kind": "local"}, True, str(self.root))
        self.assertEqual(code, 2)
        self.assertEqual((self.target / "AGENTS.md").read_bytes(), b"old rules plus project rules")
        self.assertEqual((self.target / "docs/tool.md").read_bytes(), b"new tool")

    def test_line_endings_do_not_produce_false_conflicts(self):
        (self.target / "CLAUDE.md").write_bytes(b"@AGENTS.md\r\n")
        self.assertEqual(self.apply({"CLAUDE.md": b"@AGENTS.md\n"})[0], 0)
        self.assertEqual(self.apply({"CLAUDE.md": b"@new.md\n"})[0], 0)

    def test_custom_skill_supporting_files_not_injected(self):
        directory = self.target / ".agents/skills/usage-pacing"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_bytes(b"my custom skill")
        code, _ = self.apply({".agents/skills/usage-pacing/SKILL.md": b"upstream",
                             ".agents/skills/usage-pacing/helper.py": b"code"}, safe=True)
        self.assertEqual(code, 2)
        self.assertFalse((directory / "helper.py").exists())

    def test_custom_extra_skill_file_preserves_entire_skill(self):
        directory = self.target / ".agents/skills/usage-pacing"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_bytes(b"standard skill")
        (directory / "custom.md").write_bytes(b"project-specific guidance")
        candidates = {".agents/skills/usage-pacing/SKILL.md": b"standard skill",
                      ".agents/skills/usage-pacing/helper.py": b"new helper"}
        code, _ = self.apply(candidates, safe=True)
        self.assertEqual(code, 2)
        self.assertFalse((directory / "helper.py").exists())

    def test_customized_retired_helper_preserves_entire_skill(self):
        prefix = ".agents/skills/project-planner/"
        self.apply({prefix + "SKILL.md": b"old", prefix + "helper.py": b"original helper"})
        (self.target / (prefix + "helper.py")).write_bytes(b"project helper")
        code, _ = self.apply({prefix + "SKILL.md": b"new", prefix + "new.py": b"new helper"}, safe=True)
        self.assertEqual(code, 2)
        self.assertEqual((self.target / (prefix + "SKILL.md")).read_bytes(), b"old")
        self.assertFalse((self.target / (prefix + "new.py")).exists())

    def test_inventory_includes_referenced_framework_dependencies(self):
        candidates = upgrade.candidates_from(upgrade.TEMPLATE_ROOT)
        for relative in ("scripts/transcribe_local_large_v3.py", "assets/LLM_PROJECT_HARNESS.md",
                         "docs/prompts.md", "docs/peanuts-and-hay.md", "workflows/build-graph.md",
                         "workflows/calibrate.md", "workflows/bootstrap-context.md",
                         "workflows/drift-report.md", ".agents/skills/bootstrap-context/SKILL.md",
                         ".claude/skills/bootstrap-context/SKILL.md", ".agents/skills/drift-report/SKILL.md",
                         ".claude/skills/drift-report/SKILL.md"):
            self.assertIn(relative, candidates)

    def test_backup_inside_target_is_rejected_before_writing(self):
        state = engine.load_state(self.target)
        candidates = {"AGENTS.md": b"rules"}
        plan = engine.plan_upgrade(self.target, candidates, state)
        with self.assertRaisesRegex(ValueError, "outside target"):
            engine.apply_plan(self.target, candidates, state, plan, {"kind": "local"},
                              backup_parent=str(self.target))
        self.assertEqual(self.snapshot(), {})

    def test_backup_guard_resolves_both_sides_of_path_comparison(self):
        alias = self.target / ".." / self.target.name
        state = engine.load_state(self.target)
        candidates = {"AGENTS.md": b"rules"}
        plan = engine.plan_upgrade(alias, candidates, state)
        with self.assertRaisesRegex(ValueError, "outside target"):
            engine.apply_plan(alias, candidates, state, plan, {"kind": "local"},
                              backup_parent=str(self.target.resolve()))
        self.assertEqual(self.snapshot(), {})

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_windows_junction_cannot_redirect_within_project(self):
        real = self.target / "application"
        real.mkdir()
        junction = self.target / "docs"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(real)],
                                capture_output=True)
        if result.returncode:
            self.skipTest("junction creation unavailable")
        plan = engine.plan_upgrade(self.target, {"docs/code.py": b"do not inject"}, {"files": {}})
        self.assertEqual(plan[0]["action"], "conflict")
        self.assertFalse(list(real.iterdir()))

    def test_state_retains_remote_source_without_credentials(self):
        source = {"url": "https://gitlab.example.com/team/template.git", "ref": "main", "commit": "a" * 40}
        candidates = {"AGENTS.md": b"rules"}
        state = engine.load_state(self.target)
        plan = engine.plan_upgrade(self.target, candidates, state)
        engine.apply_plan(self.target, candidates, state, plan, source, backup_parent=str(self.root))
        self.assertEqual(engine.load_state(self.target)["source"], source)

    def test_missing_memory_does_not_inherit_template_project_history(self):
        candidates = upgrade.candidates_from(upgrade.TEMPLATE_ROOT)
        for name in ("startup", "handoff", "projectbrief", "activeContext", "progress", "techContext"):
            self.assertIn(b"TBD", candidates["memory-bank/" + name + ".md"])
        self.assertNotIn("README.md", candidates)
        self.assertNotIn("VERSION", candidates)
        self.assertNotIn(".claude/settings.json", candidates)

    def test_backup_contains_original_bytes_outside_project(self):
        self.apply({"docs/tool.md": b"one"})
        code, messages = self.apply({"docs/tool.md": b"two"})
        backup = Path(messages[0].removeprefix("Backup/report: "))
        self.assertEqual(code, 0)
        self.assertNotIn(self.target, backup.parents)
        self.assertEqual((backup / "files/docs/tool.md").read_bytes(), b"one")
        self.assertEqual(json.loads((backup / "report.json").read_text())["status"], "applied")

    def test_write_failure_rolls_back_modified_and_new_files(self):
        self.apply({"a.md": b"one"})
        before = self.snapshot()
        original = engine.atomic_write
        calls = []
        def fail_once(path, data):
            calls.append(path)
            if len(calls) == 3:
                raise OSError("simulated disk failure")
            original(path, data)
        with patch.object(engine, "atomic_write", side_effect=fail_once):
            with self.assertRaises(OSError):
                self.apply({"a.md": b"two", "b.md": b"new"})
        self.assertEqual(self.snapshot(), before)

    def test_edit_after_plan_is_detected(self):
        self.apply({"a.md": b"one"})
        state = engine.load_state(self.target)
        candidates = {"a.md": b"two"}
        plan = engine.plan_upgrade(self.target, candidates, state)
        (self.target / "a.md").write_bytes(b"concurrent edit")
        with self.assertRaisesRegex(ValueError, "changed after preview"):
            engine.apply_plan(self.target, candidates, state, plan, {"kind": "local"}, backup_parent=str(self.root))
        self.assertEqual((self.target / "a.md").read_bytes(), b"concurrent edit")

    def test_bad_state_and_linked_destination_fail_closed(self):
        (self.target / engine.STATE).write_text('{"schema": 99}', encoding="utf-8")
        with self.assertRaises(ValueError):
            engine.load_state(self.target)
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.target / "docs").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks unavailable on this Windows account")
        plan = engine.plan_upgrade(self.target, {"docs/a.md": b"test"}, {"files": {}})
        self.assertEqual(plan[0]["action"], "conflict")
        self.assertFalse(list(outside.iterdir()))

    def test_transport_urls(self):
        for url in ("https://github.com/owner/template", "https://gitlab.com/group/sub/template.git",
                    "https://gitlab.example.com/group/template", "git@gitlab.example.com:owner/template.git",
                    "ssh://git@gitlab.example.com/group/template.git"):
            self.assertEqual(engine.validate_url(url), url)
        for url in ("https://user:password" + "@" + "github.com/o/r", "file:" + "/" * 3 + "repo", "ext::command",
                    "--upload-pack=command", "https://github.com/o/r?token=TBD"):
            with self.assertRaises(ValueError):
                engine.validate_url(url)

    def test_archive_rejects_traversal_and_links(self):
        for name, member_type in (("../escape", tarfile.REGTYPE), ("link", tarfile.SYMTYPE),
                                  ("C:/escape", tarfile.REGTYPE), (".git/config", tarfile.REGTYPE)):
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode="w") as archive:
                info = tarfile.TarInfo(name)
                info.type = member_type
                archive.addfile(info)
            with self.assertRaises(ValueError):
                engine.extract_archive(stream.getvalue(), self.target)

    def test_real_git_fetch_archive_and_pin_mismatch(self):
        repo = self.root / "upstream"
        repo.mkdir()
        # This is an isolated fixture with no external remotes or credentials.
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL)
        git("remote", "-v") if (repo / ".git").exists() else None
        git("init")
        for relative in ("AGENTS.md", "scripts/upgrade-target.py", "workflows/upgrade-project.md"):
            path = repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture", encoding="utf-8")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "fixture")
        sha = git("rev-parse", "HEAD").decode().strip()
        with patch.object(engine, "validate_url"):
            with engine.source_tree(str(repo), expect_commit=sha) as (source, metadata):
                self.assertEqual(metadata["commit"], sha)
                self.assertEqual((source / "AGENTS.md").read_text(), "fixture")
            with self.assertRaisesRegex(ValueError, "moved since preview"):
                with engine.source_tree(str(repo), expect_commit="0" * 40):
                    self.fail("mismatched pin was accepted")


if __name__ == "__main__":
    unittest.main()
