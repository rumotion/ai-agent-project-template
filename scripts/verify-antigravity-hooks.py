"""Execute configured file hooks with shell and direct-argv Windows launch paths."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class HookPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hook-launch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project with spaces [case]"
        (self.root / ".agents").mkdir(parents=True)
        (self.root / "assets/nested").mkdir(parents=True)
        (self.root / "AGENTS.md").write_text("Synthetic project.\n", encoding="utf-8")
        shutil.copytree(ROOT / "scripts/hooks", self.root / "scripts/hooks", ignore=shutil.ignore_patterns("__pycache__"))
        self.config = json.loads((ROOT / ".agents/hooks.json").read_text(encoding="utf-8"))["boundary-guard"]
        self.cwds = (self.root, self.root / ".agents", self.root / "assets/nested")

    def run_hook(self, command, cwd, event, shell=False):
        # Command is trusted checked-in configuration; event strings stay stdin.
        event = json.loads(json.dumps(event))
        event.setdefault("cwd", str(cwd))
        if event.get("toolCall", {}).get("name") == "run_command":
            event["toolCall"]["args"].setdefault("Cwd", str(cwd))
        result = subprocess.run(command if shell else command.split(), cwd=self.root / ".agents",
                                input=json.dumps(event), shell=shell,
                                capture_output=True, text=True, encoding="utf-8", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_directory_listing_allowed_from_every_cwd(self):
        event = {"toolCall": {"name": "run_command", "args": {"CommandLine": "dir assets"}}}
        for cwd in self.cwds:
            for hook in self.config["PreToolUse"][0]["hooks"]:
                for shell in (False, True):
                    self.assertEqual(self.run_hook(hook["command"], cwd, event, shell), {"decision": "allow"})

    def test_configuration_has_no_inline_code_or_quoted_arguments(self):
        for groups in self.config.values():
            for group in groups:
                for hook in group["hooks"]:
                    command = hook["command"]
                    self.assertNotIn("-c", command.split())
                    self.assertFalse(any(char in command for char in '\r\n\"\''))

    def test_canonical_file_launch_from_any_cwd(self):
        script = self.root / "scripts/hooks/antigravity-dispatch.py"
        for cwd in self.cwds:
            result = subprocess.run([sys.executable, str(script), "guard-remote-ops.py", "--client", "gemini"],
                                    cwd=cwd, input="{}", capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"decision": "allow"})

    def test_publishing_guard_still_denies_synthetic_event(self):
        event = {"toolCall": {"name": "run_command", "args": {"CommandLine": "git push origin main"}}}
        command = self.config["PreToolUse"][0]["hooks"][0]["command"]
        for cwd in self.cwds:
            self.assertEqual(self.run_hook(command, cwd, event)["decision"], "deny")

    def test_sensitive_write_still_denied(self):
        event = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": str(self.root / "token.json")}}}
        command = self.config["PreToolUse"][1]["hooks"][0]["command"]
        for cwd in self.cwds:
            self.assertEqual(self.run_hook(command, cwd, event)["decision"], "deny")
        self.assertFalse((self.root / "token.json").exists())

    def test_native_cli_write_alias_is_mapped_without_losing_old_names(self):
        names = ("write_file", "write_to_file", "replace_file_content", "multi_replace_file_content")
        for event in ("PreToolUse", "PostToolUse"):
            for name in names:
                self.assertTrue(any(re.fullmatch(group["matcher"], name) for group in self.config[event]), name)

    def test_native_cli_path_field_denies_sensitive_and_allows_benign(self):
        command = self.config["PreToolUse"][1]["hooks"][0]["command"]
        for cwd in self.cwds:
            event = {"toolCall": {"name": "write_file", "args": {"Path": str(self.root / "inert/token.json"), "Content": "private-fixture"}}}
            self.assertEqual(self.run_hook(command, cwd, event)["decision"], "deny")
            event["toolCall"]["args"]["Path"] = str(self.root / "docs/note.md")
            self.assertEqual(self.run_hook(command, cwd, event), {"decision": "allow"})

    def test_native_cli_logger_preserves_role_path_and_redaction(self):
        command = self.config["PostToolUse"][0]["hooks"][0]["command"]
        for cwd in self.cwds:
            event = {"toolCall": {"name": "write_file", "args": {"Path": str(self.root / "docs/note.md"), "Content": "never-log-this-body"}},
                     "workspacePaths": [str(self.root)]}
            self.assertEqual(self.run_hook(command, cwd, event), {})
        raw = (self.root / ".agent-logs/session.jsonl").read_text(encoding="utf-8")
        records = [json.loads(line) for line in raw.splitlines()]
        self.assertEqual(len(records), 3)
        self.assertTrue(all(r["tool"] == "write_file" and r["event"] == "post_tool_use" and r["path"] == "docs/note.md" and r["action"] == "write" for r in records))
        self.assertNotIn("never-log-this-body", raw)
        self.assertNotIn(str(self.root), raw)
        self.assertNotIn(str(self.root.resolve()), raw)
        if sys.platform == "win32":
            alias = Path(self.temp.name) / "RUNNERTEMP~1"
            subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(self.root)],
                           check=True, capture_output=True)
            event = {"toolCall": {"name": "write_file", "args": {"Path": str(alias / "docs/note.md"), "Content": "secret"}}}
            self.assertEqual(self.run_hook(command, alias, event), {})
            latest = json.loads((self.root / ".agent-logs/session.jsonl").read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(latest["path"], "docs/note.md")

    def test_conflicting_path_alias_cannot_hide_sensitive_target(self):
        command = self.config["PreToolUse"][1]["hooks"][0]["command"]
        for args in ({"Path": "inert/token.json", "file_path": "docs/note.md"},
                     {"Path": "docs/note.md", "file_path": "inert/token.json"}):
            event = {"toolCall": {"name": "write_file", "args": args}}
            self.assertEqual(self.run_hook(command, self.root, event)["decision"], "deny")

    def test_logger_returns_json_and_uses_project_root(self):
        event = {"tool_name": "write_to_file", "hook_event_name": "PostToolUse", "cwd": str(self.root),
                 "tool_input": {"TargetFile": str(self.root / "note.md")}}
        command = self.config["PostToolUse"][0]["hooks"][0]["command"]
        for cwd in self.cwds:
            self.assertEqual(self.run_hook(command, cwd, event), {})
        lines = (self.root / ".agent-logs/session.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3)
        self.assertFalse((self.root / ".agents/.agent-logs").exists())

    def test_payload_cwd_cannot_select_hook_code(self):
        event = {"cwd": str(self.root / "untrusted"), "toolCall": {"name": "run_command", "args": {"CommandLine": "dir assets"}}}
        command = self.config["PreToolUse"][0]["hooks"][0]["command"]
        self.assertEqual(self.run_hook(command, self.root / ".agents", event), {"decision": "allow"})

    def test_missing_guard_reports_redacted_failure(self):
        (self.root / "scripts/hooks/guard-remote-ops.py").unlink()
        command = self.config["PreToolUse"][0]["hooks"][0]["command"]
        result = subprocess.run(command.split(), cwd=self.root / ".agents", input="{}", shell=False,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr.strip(), "repository_hook_unavailable")


if __name__ == "__main__":
    unittest.main()
