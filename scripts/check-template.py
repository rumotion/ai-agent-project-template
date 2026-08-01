"""Validate the AI-agent project template structure.

Standard-library only so it runs in a freshly copied template without installs.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "LICENSE",
    "GEMINI.md",
    "CLAUDE.md",
    "CONVENTIONS.md",
    ".windsurfrules",
    "README.md",
    "docs/antigravity-master-prompt.md",
    "docs/agent-skill-ecosystem.md",
    "docs/agent-compatibility.md",
    "docs/agent-loop.md",
    "docs/hooks.md",
    "docs/api.md",
    "docs/file-organization.md",
    "docs/per-tool-setup.md",
    "docs/start-new-project.md",
    "docs/use-from-github.md",
    "docs/subagent-contract.md",
    "docs/reviewer-role.md",
    "docs/context-memory-bridges.md",
    "docs/protocol-watch.md",
    "docs/performance-experiments.md",
    "benchmarks/context/README.md",
    "benchmarks/context/scenarios.json",
    "scripts/benchmark-context.py",
    ".gemini/agents/reviewer.md",
    ".codex/agents/reviewer.toml",
    ".claude/agents/reviewer.md",
    ".gitignore",
    ".clineignore",
    ".env.example",
    ".github/copilot-instructions.md",
    ".cursor/rules/agents.mdc",
    ".codex/AGENTS.md",
    "memory-bank/00-index.md",
    "memory-bank/startup.md",
    "memory-bank/handoff.md",
    "memory-bank/reminders.md",
    "memory-bank/projectbrief.md",
    "memory-bank/activeContext.md",
    "memory-bank/progress.md",
    "memory-bank/techContext.md",
    "memory-bank/model-routing.md",
    ".clinerules/00-master.md",
    ".clinerules/10-memory-bank.md",
    ".clinerules/40-testing.md",
    ".agents/rules/00-master.md",
    ".agents/rules/10-memory-bank.md",
    ".agents/skills/project-planner/SKILL.md",
    ".agents/skills/karpathy-engineer/SKILL.md",
    ".agents/skills/code-reviewer/SKILL.md",
    ".agents/skills/test-strategist/SKILL.md",
    ".agents/skills/docs-memory-maintainer/SKILL.md",
    ".agents/skills/delegation-coordinator/SKILL.md",
    ".claude/skills/project-planner/SKILL.md",
    ".claude/skills/karpathy-engineer/SKILL.md",
    ".claude/skills/code-reviewer/SKILL.md",
    ".claude/skills/test-strategist/SKILL.md",
    ".claude/skills/docs-memory-maintainer/SKILL.md",
    ".claude/skills/delegation-coordinator/SKILL.md",
    ".cline/skills/project-planner/SKILL.md",
    ".cline/skills/karpathy-engineer/SKILL.md",
    ".cline/skills/code-reviewer/SKILL.md",
    ".cline/skills/test-strategist/SKILL.md",
    ".cline/skills/docs-memory-maintainer/SKILL.md",
    ".cline/skills/delegation-coordinator/SKILL.md",
    "workflows/plan-task.md",
    "workflows/handoff.md",
    "workflows/critic-review.md",
    "workflows/autonomous-agent.md",
    "workflows/pre-edit-check.md",
    "workflows/spec-driven-development.md",
    "workflows/self-evaluate.md",
    ".agents/workflows/plan-task.md",
    ".agents/workflows/implement-task.md",
    ".agents/workflows/debug-issue.md",
    ".agents/workflows/refactor-safely.md",
    ".agents/workflows/update-memory-bank.md",
    ".agents/workflows/handoff.md",
    ".agents/workflows/pre-edit-check.md",
    ".agents/workflows/spec-driven-development.md",
    ".agents/workflows/self-evaluate.md",
    ".clinerules/workflows/plan-task.md",
    ".clinerules/workflows/implement-task.md",
    ".clinerules/workflows/debug-issue.md",
    ".clinerules/workflows/refactor-safely.md",
    ".clinerules/workflows/update-memory-bank.md",
    ".clinerules/workflows/handoff.md",
    ".clinerules/workflows/pre-edit-check.md",
    ".clinerules/workflows/spec-driven-development.md",
    ".clinerules/workflows/self-evaluate.md",
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
    ".mcp/README.md",
    "references/.gitkeep",
    "references/docs/.gitkeep",
    "references/media/.gitkeep",
    "assets/.gitkeep",
    "assets/images/.gitkeep",
    "assets/data/.gitkeep",
]

FAST_REQUIRED_FILES = [
    "AGENTS.md",
    "GEMINI.md",
    "CLAUDE.md",
    "README.md",
    ".gitignore",
    ".clineignore",
    ".env.example",
    "memory-bank/startup.md",
    "memory-bank/00-index.md",
    "memory-bank/handoff.md",
]

ADAPTER_FILES = [
    "GEMINI.md",
    "CLAUDE.md",
    "CONVENTIONS.md",
    ".windsurfrules",
    ".clinerules/00-master.md",
    ".agents/rules/00-master.md",
    ".github/copilot-instructions.md",
    ".cursor/rules/agents.mdc",
    ".codex/AGENTS.md",
]

PRIMARY_ADAPTER_CONTENT = {
    "GEMINI.md": "@AGENTS.md",
    "CLAUDE.md": "@AGENTS.md",
    ".codex/AGENTS.md": "Read `../AGENTS.md`; it is canonical.",
}

CONTEXT_BUDGETS = {
    "AGENTS.md": 4_700,
    "memory-bank/startup.md": 900,
    "memory-bank/00-index.md": 1_600,
    "memory-bank/handoff.md": 1_200,
    "GEMINI.md": 700,
    "CLAUDE.md": 700,
    "CONVENTIONS.md": 700,
    ".windsurfrules": 500,
    ".clinerules/00-master.md": 700,
    ".clinerules/10-memory-bank.md": 700,
    ".agents/rules/00-master.md": 800,
    ".agents/rules/10-memory-bank.md": 800,
    ".github/copilot-instructions.md": 600,
    ".cursor/rules/agents.mdc": 700,
    ".codex/AGENTS.md": 600,
}

REQUIRED_GITIGNORE_PATTERNS = [
    ".env",
    ".env.*",
    "!.env.example",
    "env/credentials.json",
    "env/token.json",
    "*.pem",
    "*.key",
    ".agent-benchmarks/",
]

WORKFLOW_CANONICAL = "workflows"
WORKFLOW_MIRRORS = [".clinerules/workflows", ".agents/workflows"]
WORKFLOW_FILES = [
    "plan-task.md",
    "implement-task.md",
    "debug-issue.md",
    "refactor-safely.md",
    "update-memory-bank.md",
    "handoff.md",
    "pre-edit-check.md",
    "spec-driven-development.md",
    "self-evaluate.md",
]

SKILL_CANONICAL = ".agents/skills"
SKILL_MIRRORS = [".claude/skills", ".cline/skills"]
SKILL_NAMES = [
    "project-planner",
    "karpathy-engineer",
    "code-reviewer",
    "test-strategist",
    "docs-memory-maintainer",
    "delegation-coordinator",
]

FAST_INIT_MAX_CHARS = 7_600
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LAST_VERIFIED_RE = re.compile(r"(?m)^last_verified:\s*\d{4}-\d{2}-\d{2}\s*$")
REVIEWER_MARKER = "reviewer-contract: v1"
REVIEWER_CONTRACT = "docs/reviewer-role.md"
REVIEWER_ADAPTERS = {
    ".gemini/agents/reviewer.md": [
        REVIEWER_MARKER,
        REVIEWER_CONTRACT,
        "read_file",
        "grep_search",
        "glob",
        "list_directory",
    ],
    ".codex/agents/reviewer.toml": [
        REVIEWER_MARKER,
        REVIEWER_CONTRACT,
        'sandbox_mode = "read-only"',
    ],
    ".claude/agents/reviewer.md": [
        REVIEWER_MARKER,
        REVIEWER_CONTRACT,
        "tools: Read, Glob, Grep",
        "permissionMode: plan",
    ],
}
REVIEWER_ROLE_DIRS = {
    ".gemini/agents": {".md"},
    ".codex/agents": {".toml"},
    ".claude/agents": {".md"},
}
CONTEXT_SCENARIO_IDS = {
    "fast-init",
    "research-synthesis",
    "routine-code-edit",
    "code-review",
    "cross-model-handoff",
}

# Files counted by the FAST_INIT token benchmark.
# Mirrors AGENTS.md FAST_INIT read list: README is intentionally excluded
# (human-facing; agents have AGENTS.md). handoff.md is counted
# unconditionally as the conservative worst case (read only when resuming).
BENCHMARK_FILES = [
    "AGENTS.md",
    "memory-bank/startup.md",
    "memory-bank/00-index.md",
    "memory-bank/handoff.md",
]

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "vendor", "__pycache__",
    "dist", "build", "out", "coverage", ".next", ".nuxt", ".cache",
    ".turbo", ".pytest_cache", ".mypy_cache", ".agent-logs", "graphify-out",
    "tmp", "temp",
}

TEXT_SUFFIXES = {
    ".example", ".gitignore", ".json", ".md", ".mdc", ".py", ".toml",
    ".txt", ".yaml", ".yml",
}

ASSIGNMENT_RE = re.compile(r"(?i)^\s*([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*)\s*[:=]\s*(.+?)\s*$")
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
LOCAL_PATH_RE = re.compile(r"(?i)([A-Z]:\\Users\\|/Users/|/home/)")
FILE_URI_RE = re.compile(r"(?i)\bfile://")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
TOKEN_VALUE_RE = re.compile(r"(?i)\b(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,})\b")
SCANNER_SOURCE_PATTERNS = {
    ASSIGNMENT_RE.pattern, EMAIL_RE.pattern, LOCAL_PATH_RE.pattern,
    FILE_URI_RE.pattern,
    PRIVATE_KEY_RE.pattern, TOKEN_VALUE_RE.pattern,
}


def is_text_file(path: Path) -> bool:
    if path.name in {".gitignore", ".clineignore", "LICENSE"}:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def iter_template_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if is_text_file(path):
            files.append(path)
    return files


def placeholder_or_empty(value: str) -> bool:
    value = value.strip().strip('"\'')
    if not value:
        return True
    if value.startswith("${") and value.endswith("}"):
        return True
    return value in {"TBD", "<placeholder>", "[placeholder]", "your-value-here"}


def is_scanner_source_line(line: str) -> bool:
    return any(pattern in line for pattern in SCANNER_SOURCE_PATTERNS)


def scan_sensitive_content() -> list[tuple[str, int, str]]:
    findings: list[tuple[str, int, str]] = []
    for path in iter_template_files():
        rel_path = path.relative_to(ROOT).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, 1):
            if rel_path == "scripts/check-template.py" and is_scanner_source_line(line):
                continue
            if PRIVATE_KEY_RE.search(line):
                findings.append((rel_path, line_number, "private key marker"))
            if TOKEN_VALUE_RE.search(line):
                findings.append((rel_path, line_number, "token-like value"))
            if LOCAL_PATH_RE.search(line):
                findings.append((rel_path, line_number, "local user path"))
            if FILE_URI_RE.search(line):
                findings.append((rel_path, line_number, "local file URI"))
            if EMAIL_RE.search(line) and "example.com" not in line.lower():
                findings.append((rel_path, line_number, "email address"))
            assignment = ASSIGNMENT_RE.match(line)
            if assignment and not placeholder_or_empty(assignment.group(2)):
                findings.append((rel_path, line_number, "non-empty secret-like assignment"))
    return findings


def check_gitignore() -> list[str]:
    gitignore = ROOT / ".gitignore"
    if not gitignore.is_file():
        return REQUIRED_GITIGNORE_PATTERNS
    patterns = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    return [pattern for pattern in REQUIRED_GITIGNORE_PATTERNS if pattern not in patterns]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_mirror_drift() -> list[str]:
    """Workflow and skill mirrors must match canonical content byte-for-byte."""
    drift: list[str] = []
    for mirror in WORKFLOW_MIRRORS:
        for fname in WORKFLOW_FILES:
            src = ROOT / WORKFLOW_CANONICAL / fname
            dst = ROOT / mirror / fname
            if not src.is_file() or not dst.is_file():
                continue
            if file_hash(src) != file_hash(dst):
                drift.append(f"{mirror}/{fname} differs from {WORKFLOW_CANONICAL}/{fname}")
    for mirror in SKILL_MIRRORS:
        for skill in SKILL_NAMES:
            src = ROOT / SKILL_CANONICAL / skill / "SKILL.md"
            dst = ROOT / mirror / skill / "SKILL.md"
            if not src.is_file() or not dst.is_file():
                continue
            if file_hash(src) != file_hash(dst):
                drift.append(f"{mirror}/{skill}/SKILL.md differs from {SKILL_CANONICAL}/{skill}/SKILL.md")
    return drift


def parse_skill_frontmatter(path: Path) -> Optional[tuple[dict[str, str], str]]:
    """Parse the small scalar subset required by the Agent Skills spec."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None

    fields: dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")
    body = "\n".join(lines[closing + 1:]).strip()
    return fields, body


def check_skill_schema() -> list[str]:
    findings: list[str] = []
    for skill in SKILL_NAMES:
        path = ROOT / SKILL_CANONICAL / skill / "SKILL.md"
        if not path.is_file():
            continue
        parsed = parse_skill_frontmatter(path)
        rel = path.relative_to(ROOT).as_posix()
        if parsed is None:
            findings.append(f"{rel}: missing or malformed YAML frontmatter")
            continue
        fields, body = parsed
        name = fields.get("name", "")
        description = fields.get("description", "")
        if name != skill:
            findings.append(f"{rel}: name must match parent directory ({skill})")
        if not SKILL_NAME_RE.fullmatch(name) or len(name) > 64:
            findings.append(f"{rel}: invalid Agent Skills name")
        if not description or len(description) > 1_024:
            findings.append(f"{rel}: description must be 1-1024 characters")
        if not body:
            findings.append(f"{rel}: instruction body is empty")
    return findings


def check_primary_adapters() -> list[str]:
    findings: list[str] = []
    for rel, expected in PRIMARY_ADAPTER_CONTENT.items():
        path = ROOT / rel
        if path.is_file() and path.read_text(encoding="utf-8").splitlines() != [expected]:
            findings.append(f"{rel}: must contain only the canonical pointer/import")
    return findings


def check_compatibility_contract() -> list[str]:
    findings: list[str] = []
    path = ROOT / "docs/agent-compatibility.md"
    if not path.is_file():
        return findings
    content = path.read_text(encoding="utf-8")
    if not LAST_VERIFIED_RE.search(content):
        findings.append("docs/agent-compatibility.md: missing ISO last_verified date")
    required_terms = [
        ".agents/skills",
        ".claude/skills",
        ".gemini/settings.json",
        ".codex/config.toml",
        ".mcp.json",
        "docs/reviewer-role.md",
        "docs/protocol-watch.md",
    ]
    for term in required_terms:
        if term not in content:
            findings.append(f"docs/agent-compatibility.md: missing {term}")
    return findings


def check_reviewer_contract() -> list[str]:
    """Check adapter declarations; runtime read-only behavior still needs a pilot."""
    findings: list[str] = []
    contract_path = ROOT / REVIEWER_CONTRACT
    if contract_path.is_file():
        content = contract_path.read_text(encoding="utf-8")
        for term in [
            "reviewer_contract: v1",
            "read-only",
            "frozen artifact",
            "severity:",
            "location:",
            "evidence:",
            "recommended_fix:",
            "verdict: accept | revise",
        ]:
            if term not in content:
                findings.append(f"{REVIEWER_CONTRACT}: missing {term}")

    for rel_path, required_terms in REVIEWER_ADAPTERS.items():
        path = ROOT / rel_path
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for term in required_terms:
            if term not in content:
                findings.append(f"{rel_path}: missing {term}")

        if rel_path.endswith(".md"):
            lines = content.splitlines()
            if not lines or lines[0].strip() != "---":
                findings.append(f"{rel_path}: missing YAML frontmatter")
                continue
            try:
                closing = next(
                    index
                    for index, line in enumerate(lines[1:], 1)
                    if line.strip() == "---"
                )
            except StopIteration:
                findings.append(f"{rel_path}: unclosed YAML frontmatter")
                continue
            header = "\n".join(lines[1:closing])
            if not re.search(r"(?m)^name:\s*reviewer\s*$", header):
                findings.append(f"{rel_path}: frontmatter name must be reviewer")
            if not re.search(r"(?m)^description:\s*\S", header):
                findings.append(f"{rel_path}: frontmatter description is required")
            if len(re.findall(r"(?m)^tools:\s*", header)) != 1:
                findings.append(f"{rel_path}: expected exactly one tools declaration")
            if rel_path.startswith(".gemini/"):
                if not re.search(r"(?m)^kind:\s*local\s*$", header):
                    findings.append(f"{rel_path}: kind must be local")
                forbidden = [
                    tool
                    for tool in ["write_file", "replace", "run_shell_command", "shell"]
                    if re.search(rf"(?im)^\s*-\s*{re.escape(tool)}\s*$", header)
                ]
                if forbidden:
                    findings.append(
                        f"{rel_path}: write/command tools are forbidden: "
                        f"{', '.join(forbidden)}"
                    )
            if rel_path.startswith(".claude/"):
                if len(re.findall(r"(?m)^permissionMode:\s*", header)) != 1:
                    findings.append(
                        f"{rel_path}: expected exactly one permissionMode declaration"
                    )

        if rel_path.endswith(".toml"):
            if len(re.findall(r"(?m)^name\s*=", content)) != 1:
                findings.append(f"{rel_path}: expected exactly one name assignment")
            if not re.search(r'(?m)^name\s*=\s*"reviewer"\s*$', content):
                findings.append(f"{rel_path}: name must be reviewer")
            if len(re.findall(r"(?m)^sandbox_mode\s*=", content)) != 1:
                findings.append(
                    f"{rel_path}: expected exactly one sandbox_mode assignment"
                )
            if content.count('developer_instructions = """') != 1:
                findings.append(
                    f"{rel_path}: expected one multiline developer_instructions value"
                )
            if content.count('"""') != 2:
                findings.append(
                    f"{rel_path}: developer_instructions multiline string is unbalanced"
                )

    for rel_dir, suffixes in REVIEWER_ROLE_DIRS.items():
        directory = ROOT / rel_dir
        if not directory.is_dir():
            continue
        role_files = {
            path.name
            for path in directory.iterdir()
            if path.is_file() and path.suffix in suffixes
        }
        expected = {
            Path(path).name
            for path in REVIEWER_ADAPTERS
            if str(Path(path).parent).replace("\\", "/") == rel_dir
        }
        if role_files != expected:
            findings.append(
                f"{rel_dir}: expected exactly one reviewer role; "
                f"found {', '.join(sorted(role_files)) or 'none'}"
            )
    return findings


def check_advanced_docs() -> list[str]:
    findings: list[str] = []
    dated_docs = [
        "docs/context-memory-bridges.md",
        "docs/protocol-watch.md",
    ]
    for rel_path in dated_docs:
        path = ROOT / rel_path
        if path.is_file() and not LAST_VERIFIED_RE.search(
            path.read_text(encoding="utf-8")
        ):
            findings.append(f"{rel_path}: missing ISO last_verified date")

    protocol_path = ROOT / "docs/protocol-watch.md"
    if protocol_path.is_file():
        content = protocol_path.read_text(encoding="utf-8")
        for term in ["MCP", "Agent Skills", "ACP", "A2A", "Adoption trigger"]:
            if term not in content:
                findings.append(f"docs/protocol-watch.md: missing {term}")
    return findings


def check_context_benchmark() -> list[str]:
    import json
    import subprocess

    findings: list[str] = []
    manifest_path = ROOT / "benchmarks" / "context" / "scenarios.json"
    script_path = ROOT / "scripts" / "benchmark-context.py"
    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            scenarios = data.get("scenarios", []) if isinstance(data, dict) else []
            ids = {
                item.get("id")
                for item in scenarios
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            missing_ids = sorted(CONTEXT_SCENARIO_IDS - ids)
            if data.get("schema_version") != 1:
                findings.append(
                    "benchmarks/context/scenarios.json: schema_version must be 1"
                )
            for scenario_id in missing_ids:
                findings.append(
                    f"benchmarks/context/scenarios.json: missing scenario {scenario_id}"
                )
        except (OSError, ValueError) as err:
            findings.append(
                f"benchmarks/context/scenarios.json: JSON parse error: {err}"
            )

    if script_path.is_file():
        content = script_path.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*(?:from|import)\s+(?:socket|urllib|http|requests)\b", content):
            findings.append(
                "scripts/benchmark-context.py: network library import is forbidden"
            )
        proc = subprocess.run(
            [sys.executable, str(script_path), "--self-test"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        if proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip()
            findings.append(
                "scripts/benchmark-context.py --self-test failed with "
                f"exit code {proc.returncode}: {detail}"
            )
    return findings


def check_hook_fixtures() -> list[str]:
    findings: list[str] = []
    verify_script = ROOT / "scripts" / "hooks" / "verify-fixtures.py"
    if not verify_script.is_file():
        findings.append("Missing required script scripts/hooks/verify-fixtures.py")
        return findings
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(verify_script)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        findings.append(f"scripts/hooks/verify-fixtures.py failed with exit code {proc.returncode}:\n{proc.stderr.strip()}")
    return findings


def check_hook_examples() -> list[str]:
    """Validate native hook adapter structure and explicit client routing."""
    import json

    findings: list[str] = []
    contracts = [
        (
            ".claude/settings.json",
            "claude",
            {
                "PreToolUse": "guard-sensitive-paths.py",
                "PostToolUse": "log-writes.py",
            },
        ),
        (
            ".gemini/settings.example.json",
            "gemini",
            {
                "BeforeTool": "guard-sensitive-paths.py",
                "AfterTool": "log-writes.py",
            },
        ),
        (
            ".codex/hooks.example.json",
            "codex",
            {
                "PreToolUse": "guard-sensitive-paths.py",
                "PostToolUse": "log-writes.py",
            },
        ),
    ]

    for rel_path, client, expected_events in contracts:
        path = ROOT / rel_path
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            findings.append(f"{rel_path}: JSON parse error: {err}")
            continue
        hooks = data.get("hooks") if isinstance(data, dict) else None
        if not isinstance(hooks, dict):
            findings.append(f"{rel_path}: missing object 'hooks'")
            continue

        for event_name, script_name in expected_events.items():
            groups = hooks.get(event_name)
            if not isinstance(groups, list) or not groups:
                findings.append(f"{rel_path}: missing hook event '{event_name}'")
                continue
            commands = []
            for group in groups:
                if not isinstance(group, dict):
                    continue
                handlers = group.get("hooks")
                if not isinstance(handlers, list):
                    continue
                for handler in handlers:
                    if isinstance(handler, dict):
                        command = handler.get("command")
                        if isinstance(command, str):
                            commands.append(command)
            if not any(
                script_name in command and f"--client {client}" in command
                for command in commands
            ):
                findings.append(
                    f"{rel_path}: '{event_name}' must call {script_name} "
                    f"with --client {client}"
                )
            if script_name == "log-writes.py" and not any(
                script_name in command and "--workspace-root" in command
                for command in commands
            ):
                findings.append(
                    f"{rel_path}: '{event_name}' must give log-writes.py "
                    "an explicit --workspace-root"
                )
    return findings


def check_mcp_examples() -> list[str]:
    findings: list[str] = []
    import json
    gemini_path = ROOT / ".gemini/settings.example.json"
    if gemini_path.is_file():
        try:
            data = json.loads(gemini_path.read_text(encoding="utf-8"))
            if "mcpServers" not in data:
                findings.append(".gemini/settings.example.json: missing 'mcpServers' key")
            else:
                servers = data.get("mcpServers", {})
                for expected in ["filesystem", "git", "memory"]:
                    if expected not in servers:
                        findings.append(f".gemini/settings.example.json: missing server '{expected}'")
        except Exception as err:
            findings.append(f".gemini/settings.example.json: JSON parse error: {err}")

    codex_path = ROOT / ".codex/config.example.toml"
    if codex_path.is_file():
        content = codex_path.read_text(encoding="utf-8")
        section_re = re.compile(
            r"(?ms)^\[(mcp_servers\.[A-Za-z0-9_-]+)\]\s*(.*?)(?=^\[|\Z)"
        )
        sections = {name: body for name, body in section_re.findall(content)}
        for server in ["filesystem", "git", "memory"]:
            section = f"mcp_servers.{server}"
            body = sections.get(section)
            if body is None:
                findings.append(
                    f".codex/config.example.toml: missing section '[{section}]'"
                )
                continue
            if not re.search(r'(?m)^command\s*=\s*"[^"]+"\s*$', body):
                findings.append(
                    f".codex/config.example.toml: [{section}] missing string command"
                )
            if not re.search(r"(?m)^args\s*=\s*\[.*\]\s*$", body):
                findings.append(
                    f".codex/config.example.toml: [{section}] missing args array"
                )

    return findings


def benchmark_startup() -> tuple[int, list[tuple[str, int, int]]]:
    """Return (total_chars, [(path, chars, est_tokens)]). Uses chars/4 heuristic."""
    rows: list[tuple[str, int, int]] = []
    total_chars = 0
    for rel in BENCHMARK_FILES:
        path = ROOT / rel
        if not path.is_file():
            continue
        chars = len(path.read_text(encoding="utf-8"))
        rows.append((rel, chars, chars // 4))
        total_chars += chars
    return total_chars, rows


def print_benchmark() -> None:
    total_chars, rows = benchmark_startup()
    print("FAST_INIT startup-path size:")
    for rel, chars, tokens in rows:
        print(f"  - {rel}: {chars} chars (~{tokens} tokens)")
    print(f"  Total: {total_chars} chars (~{total_chars // 4} tokens)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AI-agent project template structure.")
    parser.add_argument("--fast", action="store_true", help="Lightweight FAST_INIT validation.")
    parser.add_argument("--compat", action="store_true", help="Validate Gemini/Codex/Claude compatibility contracts.")
    parser.add_argument("--benchmark", action="store_true", help="Print FAST_INIT startup-path token estimate and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.benchmark and not args.fast and not args.compat:
        print_benchmark()
        return 0

    fast_mode = args.fast
    compat_mode = args.compat
    required_files = FAST_REQUIRED_FILES if fast_mode else REQUIRED_FILES

    missing = [path for path in required_files if not (ROOT / path).is_file()]
    bad_adapters = []
    primary_adapter_findings = check_primary_adapters()
    oversized = []
    sensitive_findings = [] if fast_mode else scan_sensitive_content()
    missing_gitignore_patterns = check_gitignore()
    drift = [] if fast_mode else check_mirror_drift()
    skill_findings = [] if fast_mode else check_skill_schema()
    compatibility_findings = [] if fast_mode else check_compatibility_contract()
    reviewer_findings = [] if fast_mode else check_reviewer_contract()
    advanced_doc_findings = [] if fast_mode else check_advanced_docs()
    context_benchmark_findings = [] if fast_mode else check_context_benchmark()
    hook_findings = [] if fast_mode else (
        check_hook_fixtures() + check_hook_examples()
    )
    mcp_findings = [] if fast_mode else check_mcp_examples()
    startup_chars, _ = benchmark_startup()
    startup_excess = max(0, startup_chars - FAST_INIT_MAX_CHARS)

    for path in ADAPTER_FILES:
        file_path = ROOT / path
        if file_path.is_file() and "AGENTS.md" not in file_path.read_text(encoding="utf-8"):
            bad_adapters.append(path)

    for path, max_chars in CONTEXT_BUDGETS.items():
        file_path = ROOT / path
        if file_path.is_file():
            size = len(file_path.read_text(encoding="utf-8"))
            if size > max_chars:
                oversized.append((path, size, max_chars))

    if (
        missing
        or bad_adapters
        or primary_adapter_findings
        or oversized
        or startup_excess
        or sensitive_findings
        or missing_gitignore_patterns
        or drift
        or skill_findings
        or compatibility_findings
        or reviewer_findings
        or advanced_doc_findings
        or context_benchmark_findings
        or hook_findings
        or mcp_findings
    ):
        if missing:
            print("Missing required files:")
            for path in missing:
                print(f"  - {path}")
        if bad_adapters:
            print("Adapter files that do not reference AGENTS.md:")
            for path in bad_adapters:
                print(f"  - {path}")
        if primary_adapter_findings:
            print("Primary adapter contract violations:")
            for finding in primary_adapter_findings:
                print(f"  - {finding}")
        if oversized:
            print("Files exceeding startup/context budget:")
            for path, size, max_chars in oversized:
                print(f"  - {path}: {size} chars > {max_chars} chars")
        if startup_excess:
            print("FAST_INIT aggregate budget exceeded:")
            print(f"  - {startup_chars} chars > {FAST_INIT_MAX_CHARS} chars by {startup_excess} (~{startup_excess // 4} tokens)")
        if sensitive_findings:
            print("Potential security-sensitive content:")
            for path, line_number, category in sensitive_findings:
                print(f"  - {path}:{line_number}: {category}")
        if missing_gitignore_patterns:
            print("Missing required .gitignore patterns:")
            for pattern in missing_gitignore_patterns:
                print(f"  - {pattern}")
        if drift:
            print("Mirror drift detected (canonical vs mirror):")
            for entry in drift:
                print(f"  - {entry}")
        if skill_findings:
            print("Agent Skills schema violations:")
            for finding in skill_findings:
                print(f"  - {finding}")
        if compatibility_findings:
            print("Cross-agent compatibility violations:")
            for finding in compatibility_findings:
                print(f"  - {finding}")
        if reviewer_findings:
            print("Native reviewer contract violations:")
            for finding in reviewer_findings:
                print(f"  - {finding}")
        if advanced_doc_findings:
            print("Advanced guidance violations:")
            for finding in advanced_doc_findings:
                print(f"  - {finding}")
        if context_benchmark_findings:
            print("Context benchmark violations:")
            for finding in context_benchmark_findings:
                print(f"  - {finding}")
        if hook_findings:
            print("Hook validation failures:")
            for finding in hook_findings:
                print(f"  - {finding}")
        if mcp_findings:
            print("Native MCP example violations:")
            for finding in mcp_findings:
                print(f"  - {finding}")
        return 1

    if fast_mode:
        print("Template FAST validation passed.")
        print("Mode: --fast (lightweight startup/integration checks)")
    elif compat_mode:
        print("Template compatibility validation passed.")
        print("Mode: --compat (Gemini/Codex/Claude contracts)")
    else:
        print("Template validation passed.")
        print("Mode: full")

    print(f"Checked {len(required_files)} required files and {len(ADAPTER_FILES)} adapters.")
    print(f"Checked {len(CONTEXT_BUDGETS)} startup/context budgets.")
    print(f"Checked FAST_INIT aggregate budget ({startup_chars}/{FAST_INIT_MAX_CHARS} chars).")
    if fast_mode:
        print("Checked .gitignore safety patterns.")
        print("Skipped repository-wide secret hygiene scan and mirror-drift check in fast mode.")
    else:
        print(f"Checked {len(SKILL_NAMES)} Agent Skills across {1 + len(SKILL_MIRRORS)} discovery trees.")
        print("Checked public-template secret hygiene, compatibility/reviewer contracts, hook adapters, context benchmark, .gitignore safety patterns, and mirror-drift.")
        print()
        print_benchmark()
    return 0


if __name__ == "__main__":
    sys.exit(main())
