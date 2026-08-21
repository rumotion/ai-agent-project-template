"""Upgrade an existing target project to the latest AI Agent Project Template version.

Standard-library only so it runs in fresh environments without installs.
Safely updates workflows, skills, multi-agent adapters, safety hooks, documentation,
and validators while strictly preserving project domain code, custom rules, and domain skills.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import List, Set, Tuple


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]

STANDARD_SKILLS = [
    "project-planner",
    "karpathy-engineer",
    "code-reviewer",
    "test-strategist",
    "docs-memory-maintainer",
    "delegation-coordinator",
    "project-upgrader",
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

STANDARD_ADAPTER_FILES = [
    "GEMINI.md",
    "CLAUDE.md",
    "CONVENTIONS.md",
    ".windsurfrules",
    ".codex/AGENTS.md",
    ".cursor/rules/agents.mdc",
    ".github/copilot-instructions.md",
    ".clinerules/00-master.md",
    ".clinerules/10-memory-bank.md",
    ".clinerules/40-testing.md",
    ".agents/rules/00-master.md",
    ".agents/rules/10-memory-bank.md",
]

STANDARD_REVIEWER_FILES = [
    ".gemini/agents/reviewer.md",
    ".codex/agents/reviewer.toml",
    ".claude/agents/reviewer.md",
]

STANDARD_HOOK_FILES = [
    "scripts/hooks/log-writes.py",
    "scripts/hooks/guard-sensitive-paths.py",
    "scripts/hooks/verify-fixtures.py",
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
    ".claude/settings.json",
    ".codex/hooks.example.json",
    ".gemini/settings.example.json",
    ".codex/config.example.toml",
]

STANDARD_SCRIPTS = [
    "scripts/check-template.py",
    "scripts/init-fast.py",
    "scripts/detach-remote.py",
    "scripts/benchmark-context.py",
    "scripts/upgrade-target.py",
    "scripts/README.md",
]

STANDARD_BENCHMARKS = [
    "benchmarks/context/README.md",
    "benchmarks/context/scenarios.json",
]

STANDARD_DOCS = [
    "docs/antigravity-master-prompt.md",
    "docs/agent-skill-ecosystem.md",
    "docs/agent-compatibility.md",
    "docs/agent-loop.md",
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
]


def copy_file_safe(src: Path, dst: Path, dry_run: bool = False) -> bool:
    """Copy a file, creating parent directories as needed. Returns True if changed."""
    if not src.exists():
        return False
    
    if dst.exists():
        src_bytes = src.read_bytes()
        dst_bytes = dst.read_bytes()
        if src_bytes == dst_bytes:
            return False
    
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return True


def merge_agents_md(src_agents: Path, dst_agents: Path, dry_run: bool = False) -> bool:
    """Merge template AGENTS.md with target AGENTS.md, preserving custom rules."""
    template_content = src_agents.read_text(encoding="utf-8")
    
    if not dst_agents.exists():
        if not dry_run:
            dst_agents.write_text(template_content, encoding="utf-8")
        return True
    
    target_content = dst_agents.read_text(encoding="utf-8")
    if target_content == template_content:
        return False
    
    # Check if target has custom rules section
    custom_rules_match = re.search(r"### Custom Rules\s*\n(.*?)(?=\n## |\Z)", target_content, re.DOTALL)
    if custom_rules_match:
        custom_rules_text = custom_rules_match.group(1).strip()
        # Inject into template_content under Core rules -> General or dedicated Custom Rules section
        if "### Custom Rules" not in template_content:
            replacement = f"### Custom Rules\n\n{custom_rules_text}\n\n### General"
            template_content = template_content.replace("### General", replacement, 1)
    
    if not dry_run:
        dst_agents.write_text(template_content, encoding="utf-8")
    return True


def upgrade_project(target_dir: Path, dry_run: bool = False, verbose: bool = False) -> Tuple[int, List[str]]:
    """Execute the project upgrade."""
    target_dir = target_dir.resolve()
    if not target_dir.exists():
        print(f"Error: Target directory does not exist: {target_dir}", file=sys.stderr)
        return 1, []
    
    actions = []
    print(f"[{'DRY-RUN' if dry_run else 'UPGRADE'}] Target: {target_dir}")
    print(f"Source template: {TEMPLATE_ROOT}")
    
    # 1. Update AGENTS.md
    if merge_agents_md(TEMPLATE_ROOT / "AGENTS.md", target_dir / "AGENTS.md", dry_run=dry_run):
        actions.append("Updated AGENTS.md (preserved custom rules)")
    
    # 2. Multi-Agent Adapters
    for rel_path in STANDARD_ADAPTER_FILES:
        src = TEMPLATE_ROOT / rel_path
        dst = target_dir / rel_path
        if copy_file_safe(src, dst, dry_run=dry_run):
            actions.append(f"Synced adapter: {rel_path}")
    
    # 3. Workflows across 3 trees
    workflow_trees = ["workflows", ".agents/workflows", ".clinerules/workflows"]
    for tree in workflow_trees:
        for wf in STANDARD_WORKFLOWS:
            src = TEMPLATE_ROOT / "workflows" / wf
            dst = target_dir / tree / wf
            if copy_file_safe(src, dst, dry_run=dry_run):
                actions.append(f"Synced workflow: {tree}/{wf}")
    
    # 4. Standard Skills across 3 trees
    skill_trees = [".agents/skills", ".claude/skills", ".cline/skills"]
    for tree in skill_trees:
        for skill in STANDARD_SKILLS:
            skill_src_dir = TEMPLATE_ROOT / ".agents/skills" / skill
            skill_dst_dir = target_dir / tree / skill
            if skill_src_dir.exists():
                for root, _, files in os.walk(skill_src_dir):
                    rel_root = Path(root).relative_to(skill_src_dir)
                    for file in files:
                        src_file = Path(root) / file
                        dst_file = skill_dst_dir / rel_root / file
                        if copy_file_safe(src_file, dst_file, dry_run=dry_run):
                            actions.append(f"Synced skill file: {tree}/{skill}/{rel_root / file}")
    
    # 5. Reviewer Contracts
    for rel_path in STANDARD_REVIEWER_FILES:
        src = TEMPLATE_ROOT / rel_path
        dst = target_dir / rel_path
        if copy_file_safe(src, dst, dry_run=dry_run):
            actions.append(f"Synced reviewer contract: {rel_path}")
    
    # 6. Safety Hooks & Examples
    for rel_path in STANDARD_HOOK_FILES:
        src = TEMPLATE_ROOT / rel_path
        dst = target_dir / rel_path
        if copy_file_safe(src, dst, dry_run=dry_run):
            actions.append(f"Synced hook/config: {rel_path}")
    
    # 7. Standard Scripts & Benchmarks
    for rel_path in STANDARD_SCRIPTS + STANDARD_BENCHMARKS:
        src = TEMPLATE_ROOT / rel_path
        dst = target_dir / rel_path
        if copy_file_safe(src, dst, dry_run=dry_run):
            actions.append(f"Synced script/benchmark: {rel_path}")
    
    # 8. Documentation
    for rel_path in STANDARD_DOCS:
        src = TEMPLATE_ROOT / rel_path
        dst = target_dir / rel_path
        if copy_file_safe(src, dst, dry_run=dry_run):
            actions.append(f"Synced doc: {rel_path}")
    
    # 9. Memory Bank template schemas
    mb_template_files = [
        "memory-bank/00-index.md",
        "memory-bank/startup.md",
        "memory-bank/reminders.md",
        "memory-bank/model-routing.md",
    ]
    for rel_path in mb_template_files:
        src = TEMPLATE_ROOT / rel_path
        dst = target_dir / rel_path
        if copy_file_safe(src, dst, dry_run=dry_run):
            actions.append(f"Synced memory-bank schema: {rel_path}")
    
    # Ensure handoff.md exists if missing
    target_handoff = target_dir / "memory-bank/handoff.md"
    if not target_handoff.exists():
        if copy_file_safe(TEMPLATE_ROOT / "memory-bank/handoff.md", target_handoff, dry_run=dry_run):
            actions.append("Initialized memory-bank/handoff.md")
    
    # 10. Required .gitignore safety patterns
    target_gitignore = target_dir / ".gitignore"
    if target_gitignore.exists():
        gitignore_content = target_gitignore.read_text(encoding="utf-8")
        needed_patterns = [".env", ".env.*", "!.env.example", ".agent-benchmarks/", ".agent-logs/"]
        missing_patterns = [p for p in needed_patterns if p not in gitignore_content]
        if missing_patterns:
            new_content = gitignore_content.rstrip() + "\n\n# Agentic safety patterns\n" + "\n".join(missing_patterns) + "\n"
            if not dry_run:
                target_gitignore.write_text(new_content, encoding="utf-8")
            actions.append(f"Added {len(missing_patterns)} missing safety patterns to .gitignore")
    
    return 0, actions


def run_target_validation(target_dir: Path) -> int:
    """Run check-template.py --fast in target project."""
    check_script = target_dir / "scripts/check-template.py"
    if not check_script.exists():
        print("Warning: Target check-template.py not found, skipping validation.")
        return 0
    
    print("\n--- Running Target Template Validation ---")
    cmd = [sys.executable, str(check_script), "--fast"]
    result = subprocess.run(cmd, cwd=str(target_dir))
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upgrade a target repository to the latest AI Agent Project Template standard."
    )
    parser.add_argument(
        "--target",
        "-t",
        type=Path,
        required=True,
        help="Path to the target project directory to upgrade.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying any files.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip post-upgrade template verification in target.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose details of all actions.",
    )
    
    args = parser.parse_args()
    target_path = args.target.resolve()
    
    code, actions = upgrade_project(target_path, dry_run=args.dry_run, verbose=args.verbose)
    if code != 0:
        return code
    
    print(f"\nUpgrade complete! Total modifications: {len(actions)}")
    if args.verbose or args.dry_run:
        for action in actions:
            print(f"  - {action}")
    
    if not args.dry_run and not args.skip_validation:
        val_code = run_target_validation(target_path)
        if val_code != 0:
            print("\nWarning: Target validation returned non-zero exit code.", file=sys.stderr)
            return val_code
        print("\nTarget validation passed cleanly.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
