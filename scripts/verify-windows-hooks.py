"""Execute shipped Codex Windows hook commands in disposable Git projects."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(os.name == "nt", "Windows hook commands require Windows")
class WindowsHookTests(unittest.TestCase):
    def setUp(self):
        self.shell = shutil.which("powershell") or shutil.which("pwsh")
        self.assertIsNotNone(self.shell, "PowerShell is required for Windows hooks")
        self.temp = tempfile.TemporaryDirectory(prefix="windows-hook-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project with spaces [case]"
        (self.root / ".codex").mkdir(parents=True)
        (self.root / "assets/nested").mkdir(parents=True)
        shutil.copytree(ROOT / "scripts/hooks", self.root / "scripts/hooks",
                        ignore=shutil.ignore_patterns("__pycache__"))
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(self.root)], check=True)
        self.config = json.loads((ROOT / ".codex/hooks.example.json").read_text(encoding="utf-8"))["hooks"]
        self.cwds = (self.root, self.root / ".codex", self.root / "assets/nested")

    def run_hook(self, hook, event, cwd):
        event = dict(event)
        event.setdefault("cwd", str(self.root))
        result = subprocess.run([self.shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", hook["commandWindows"]],
                                cwd=cwd, input=json.dumps(event), capture_output=True,
                                text=True, encoding="utf-8", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout) if result.stdout.strip() else None

    def test_benign_calls_from_root_config_and_nested_directories(self):
        event = {"tool_name": "Bash", "tool_input": {"command": "dir assets"}}
        for cwd in self.cwds:
            for group in self.config["PreToolUse"]:
                for hook in group["hooks"]:
                    self.assertIsNone(self.run_hook(hook, event, cwd))

    def test_sensitive_patch_denied_before_any_write(self):
        event = {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Add File: guard-fixture/token.json\n+{}\n*** End Patch"}}
        hook = self.config["PreToolUse"][0]["hooks"][0]
        for cwd in self.cwds:
            result = self.run_hook(hook, event, cwd)["hookSpecificOutput"]
            self.assertEqual(result["permissionDecision"], "deny")
            self.assertEqual(result["permissionDecisionReason"], "Access to a sensitive path is denied by repository policy.")
        self.assertFalse((self.root / "guard-fixture/token.json").exists())

    def test_synthetic_publish_denied_without_running_command(self):
        event = {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}}
        hook = self.config["PreToolUse"][1]["hooks"][0]
        for cwd in self.cwds:
            result = self.run_hook(hook, event, cwd)["hookSpecificOutput"]
            self.assertEqual(result["permissionDecision"], "deny")

    def test_logger_anchors_output_at_project_root(self):
        event = {"tool_name": "Write", "hook_event_name": "PostToolUse",
                 "tool_input": {"file_path": "docs/note.md"}}
        group = self.config["PostToolUse"][0]
        self.assertRegex(event["tool_name"], group["matcher"])
        hook = group["hooks"][0]
        for cwd in self.cwds:
            self.assertIsNone(self.run_hook(hook, event, cwd))
        records = [json.loads(line) for line in (self.root / ".agent-logs/session.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(records), 3)
        self.assertTrue(all(record["path"] == "docs/note.md" for record in records))
        for cwd in self.cwds[1:]:
            self.assertFalse((cwd / ".agent-logs").exists())

    def test_startup_command_uses_git_root_from_nested_directories(self):
        shutil.copyfile(ROOT / "scripts/ctx.py", self.root / "scripts/ctx.py")
        records = self.root / "memory-bank/records"
        records.mkdir(parents=True)
        body = "Bootstrap the current root context. Keep the marker sentence complete."
        (records / "decision-bootstrap.md").write_text(
            "---\nid: decision-bootstrap\ntype: decision\npriority: 1\nscope: task\n"
            "tasks: windows-startup\ncategory: decision\nsource_ref: windows-fixture\n---\n" + body + "\n", encoding="utf-8")
        (self.root / "memory-bank/handoff.md").write_text(
            "---\nstatus: testing\ntask: Windows startup\ntask_id: windows-startup\n"
            "required_records: decision-bootstrap\nnext_action: Verify current startup context.\n---\n", encoding="utf-8")
        hook = self.config["SessionStart"][0]["hooks"][0]
        for cwd in self.cwds:
            event = {"hook_event_name": "SessionStart", "source": "startup", "cwd": str(cwd)}
            output = self.run_hook(hook, event, cwd)["hookSpecificOutput"]
            self.assertEqual(output["hookEventName"], "SessionStart")
            self.assertIn(body, output["additionalContext"])
            self.assertIn("Verify current startup context.", output["additionalContext"])
            self.assertIn("AGENTS.md is already loaded; do not re-read it.", output["additionalContext"])
            self.assertNotIn("CLAUDE.md", output["additionalContext"])
            self.assertLessEqual(len(output["additionalContext"]), 8000)


if __name__ == "__main__":
    unittest.main()
