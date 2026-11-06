"""Upgrade an existing target project to the latest AI Agent Project Template version.

Standard-library only so it runs in fresh environments without installs.
Updates explicit framework files using installed hashes; unknown/local changes
are conflicts. Does not merge project rules or execute downloaded validators.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]

STANDARD_SKILLS = [
    "project-planner",
    "karpathy-engineer",
    "code-reviewer",
    "test-strategist",
    "docs-memory-maintainer",
    "delegation-coordinator",
    "project-upgrader",
    "human-voice-drafting",
    "local-media-transcription",
    "sharepoint-teams-video-transcript-downloader",
    "storm-research",
    "usage-pacing",
]

STANDARD_WORKFLOWS = [
    "plan-task.md",
    "implement-task.md",
    "debug-issue.md",
    "refactor-safely.md",
    "update-memory-bank.md",
    "handoff.md",
    "pre-edit-check.md",
    "spec-driven-development.md",
    "self-evaluate.md",
    "upgrade-project.md",
]

STANDARD_SKILLS += [Path(name).stem for name in STANDARD_WORKFLOWS]

STANDARD_ADAPTER_FILES = [
    "GEMINI.md",
    "CLAUDE.md",
    "CONVENTIONS.md",
    ".rules",
    ".windsurfrules",
    ".codex/AGENTS.md",
    ".cursor/rules/agents.mdc",
    ".github/copilot-instructions.md",
    ".clinerules/00-master.md",
    ".clinerules/10-memory-bank.md",
    ".clinerules/40-testing.md",
    ".agents/rules/00-master.md",
    ".agents/rules/10-memory-bank.md",
    ".agents/rules/30-cognitive-harness.md",
]

STANDARD_REVIEWER_FILES = [
    ".gemini/agents/reviewer.md",
    ".codex/agents/reviewer.toml",
    ".claude/agents/reviewer.md",
]

STANDARD_HOOK_FILES = [
    "scripts/hooks/log-writes.py",
    "scripts/hooks/guard-sensitive-paths.py",
    "scripts/hooks/guard-remote-ops.py",
    "scripts/hooks/shell_events.py",
    "scripts/hooks/verify-hardening.py",
    "scripts/hooks/fixtures/adversarial.json",
    "scripts/hooks/session-context.py",
    "scripts/hooks/verify-fixtures.py",
    "scripts/hooks/git/pre-push",
    "scripts/hooks/fixtures/README.md",
    "scripts/hooks/fixtures/claude-write.json",
    "scripts/hooks/fixtures/claude-sensitive.json",
    "scripts/hooks/fixtures/claude-malformed.json",
    "scripts/hooks/fixtures/gemini-write.json",
    "scripts/hooks/fixtures/gemini-sensitive.json",
    "scripts/hooks/fixtures/gemini-malformed.json",
    "scripts/hooks/fixtures/codex-write.json",
    "scripts/hooks/fixtures/codex-sensitive.json",
    "scripts/hooks/fixtures/codex-malformed.json",
    "scripts/hooks/fixtures/claude-push.json",
    "scripts/hooks/fixtures/claude-shell-safe.json",
    "scripts/hooks/fixtures/gemini-push.json",
    "scripts/hooks/fixtures/gemini-shell-safe.json",
    "scripts/hooks/fixtures/codex-push.json",
    "scripts/hooks/fixtures/codex-shell-safe.json",
    ".codex/hooks.example.json",
    ".gemini/settings.example.json",
    ".codex/config.example.toml",
    ".agents/hooks.json",
]

STANDARD_SCRIPTS = [
    "scripts/check-template.py",
    "scripts/init-fast.py",
    "scripts/new-project.py",
    "scripts/detach-remote.py",
    "scripts/benchmark-context.py",
    "scripts/transcribe_local_large_v3.py",
    "scripts/usage-pacing.py",
    "scripts/verify-usage-pacing.py",
    "scripts/validate-schemas.py",
    "scripts/ctx.py",
    "scripts/continuity.py",
    "scripts/verify-continuity.py",
    "scripts/verify-records.py",
    "scripts/tasks.py",
    "scripts/verify-tasks.py",
    "schemas/task-state.schema.json",
    "docs/task-ledger.md",
    "scripts/task_metrics.py",
    "scripts/usage_math.py",
    "scripts/verify-task-metrics.py",
    "docs/task-measurements.md",
    "scripts/verify-recovery.py",
    "benchmarks/context/recovery-scenarios.json",
    "docs/recovery-pilot.md",
    "docs/feedback-closure.md",
    "docs/product-acceptance.md",
    "schemas/continuity-receipt.schema.json",
    "schemas/context-record.schema.json",
    "docs/continuity.md",
    "scripts/push_backstop.py",
    "scripts/verify-context.py",
    "scripts/verify-backstop.py",
    "scripts/contract_checks.py",
    "scripts/verify-contracts.py",
    "scripts/boundary.py",
    "scripts/verify-boundary.py",
    "scripts/hooks/antigravity-dispatch.py",
    "scripts/verify-antigravity-hooks.py",
    "scripts/gen-adapters.py",
    "schemas/boundary-inspection.schema.json",
    "schemas/adapter-capabilities.json",
    "scripts/upgrade-target.py",
    "scripts/template_upgrade.py",
    "scripts/verify-upgrade.py",
    "scripts/README.md",
]

STANDARD_BENCHMARKS = [
    "benchmarks/context/README.md",
    "benchmarks/context/scenarios.json",
]

STANDARD_DOCS = [
    "assets/LLM_PROJECT_HARNESS.md",
    "docs/prompts.md",
    "workflows/build-graph.md",
    "workflows/calibrate.md",
    "workflows/critic-review.md",
    "docs/court-skill-assessment.md",
    "docs/antigravity-master-prompt.md",
    "docs/agent-skill-ecosystem.md",
    "docs/agent-compatibility.md",
    "docs/agent-loop.md",
    "docs/usage-pacing.md",
    "docs/local-agent-mail.md",
    "docs/ai-market-review-2026-10.md",
    "docs/hooks.md",
    "docs/api.md",
    "docs/file-organization.md",
    "docs/per-tool-setup.md",
    "docs/start-new-project.md",
    "docs/upgrade-existing-project.md",
    "docs/use-from-github.md",
    "docs/subagent-contract.md",
    "docs/reviewer-role.md",
    "docs/context-memory-bridges.md",
    "docs/protocol-watch.md",
    "docs/performance-experiments.md",
    "docs/context-compiler.md",
    "schemas/subagent-task.schema.json",
    "schemas/subagent-result.schema.json",
    "schemas/examples/task-valid.json",
    "schemas/examples/result-valid.json",
]


from template_upgrade import (apply_plan, checked_path, load_state,
                              plan_upgrade, source_tree, with_baseline)


def candidates_from(source):
    """Explicit template surface, never application manifests or active configs."""
    files = {}
    paths = ["AGENTS.md", *STANDARD_ADAPTER_FILES, *STANDARD_REVIEWER_FILES,
             *STANDARD_HOOK_FILES, *STANDARD_SCRIPTS, *STANDARD_BENCHMARKS, *STANDARD_DOCS]
    for relative in paths:
        path = checked_path(source, relative)
        if path.is_file():
            files[relative] = path.read_bytes()
    for tree in ("workflows", ".agents/workflows", ".clinerules/workflows"):
        for name in STANDARD_WORKFLOWS:
            path = checked_path(source, "workflows/" + name)
            if path.is_file():
                files[tree + "/" + name] = path.read_bytes()
    for name in STANDARD_SKILLS:
        directory = checked_path(source, ".agents/skills/" + name)
        for path in sorted(directory.rglob("*")) if directory.is_dir() else []:
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            checked_path(source, path.relative_to(source).as_posix())
            if path.is_file():
                for tree in (".agents/skills", ".claude/skills", ".cline/skills"):
                    files[tree + "/" + name + "/" + path.relative_to(directory).as_posix()] = path.read_bytes()
    # Initialize missing project context with neutral stubs, never template history.
    for name in ("startup", "handoff", "projectbrief", "activeContext", "progress", "techContext"):
        files["memory-bank/" + name + ".md"] = ("# " + name + "\n\nProject context: TBD.\n").encode()
    for name in ("00-index.md", "reminders.md", "model-routing.md"):
        path = checked_path(source, "memory-bank/" + name)
        if path.is_file():
            files["memory-bank/" + name] = path.read_bytes()
    return files


def upgrade_project(target_dir, dry_run=False, verbose=False, source=None,
                    metadata=None, apply_safe=False, baseline=None, backup_parent=None):
    target = target_dir.resolve()
    source = (source or TEMPLATE_ROOT).resolve()
    if not target.is_dir() or target == source:
        return 1, ["Target must be an existing directory distinct from source; no files changed"]
    state = load_state(target)
    if baseline is not None:
        state = with_baseline(state, candidates_from(baseline))
    candidates = candidates_from(source)
    plan = plan_upgrade(target, candidates, state)
    if dry_run:
        return 0, [json.dumps({"source": metadata or {"kind": "local"}, "plan": plan}, indent=2)]
    return apply_plan(target, candidates, state, plan, metadata or {"kind": "local"}, apply_safe, backup_parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", "-t", type=Path, required=True)
    parser.add_argument("--source", help="Template repository HTTPS/SSH URL (GitHub/GitLab)")
    parser.add_argument("--ref", help="Branch, tag or SHA; default HEAD or saved ref")
    parser.add_argument("--expect-commit", help="Require the exact SHA printed by dry-run")
    parser.add_argument("--baseline-ref", help="Known previous template tag/SHA for first upgrade of a legacy project")
    parser.add_argument("--backup-dir", type=Path, help="Existing external directory for backup/report runs (default system temp)")
    parser.add_argument("--skip-validation", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply-safe", action="store_true", help="Apply safe files; preserve and report conflicts (exit 2)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    try:
        target = args.target.resolve()
        if not target.is_dir():
            raise ValueError("Target directory does not exist")
        saved = load_state(target).get("source", {})
        url = args.source or saved.get("url")
        ref = args.ref or (saved.get("ref", "HEAD") if not args.source or args.source == saved.get("url") else "HEAD")
        if url:
            with source_tree(url, ref, args.expect_commit) as (source, metadata):
                if args.baseline_ref:
                    with source_tree(url, args.baseline_ref) as (baseline, old_metadata):
                        metadata["baseline_commit"] = old_metadata["commit"]
                        code, messages = upgrade_project(target, args.dry_run, args.verbose,
                                                        source, metadata, args.apply_safe, baseline, args.backup_dir)
                else:
                    code, messages = upgrade_project(target, args.dry_run, args.verbose,
                                                    source, metadata, args.apply_safe, backup_parent=args.backup_dir)
        else:
            if args.ref or args.expect_commit or args.baseline_ref:
                raise ValueError("Git refs require a remote source")
            code, messages = upgrade_project(target, args.dry_run, args.verbose,
                                            apply_safe=args.apply_safe, backup_parent=args.backup_dir)
        for message in messages:
            print(message)
        return code
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        # Avoid printing server/JSON payloads that may contain private data.
        print("Upgrade failed: " + (str(error) if type(error) is ValueError else type(error).__name__), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
