"""Validate the AI-agent project template structure.

This script intentionally uses only the Python standard library so it can run in a freshly copied template.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "GEMINI.md",
    "CLAUDE.md",
    "README.md",
    "docs/antigravity-master-prompt.md",
    "docs/agent-skill-ecosystem.md",
    "docs/api.md",
    "docs/file-organization.md",
    "docs/start-new-project.md",
    "docs/use-from-github.md",
    ".gitignore",
    ".clineignore",
    ".env.example",
    "memory-bank/00-index.md",
    "memory-bank/startup.md",
    "memory-bank/projectbrief.md",
    "memory-bank/activeContext.md",
    "memory-bank/progress.md",
    "memory-bank/techContext.md",
    ".clinerules/00-master.md",
    ".clinerules/10-memory-bank.md",
    ".clinerules/40-testing.md",
    ".agents/rules/00-master.md",
    ".agents/rules/10-memory-bank.md",
    ".cline/skills/project-planner/SKILL.md",
    ".cline/skills/karpathy-engineer/SKILL.md",
    ".agents/skills/project-planner/SKILL.md",
    ".agents/skills/karpathy-engineer/SKILL.md",
    "workflows/plan-task.md",
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
]

ADAPTER_FILES = [
    "GEMINI.md",
    "CLAUDE.md",
    ".clinerules/00-master.md",
    ".agents/rules/00-master.md",
]

CONTEXT_BUDGETS = {
    "AGENTS.md": 3_500,
    "memory-bank/startup.md": 900,
    "memory-bank/00-index.md": 1_600,
    "GEMINI.md": 700,
    "CLAUDE.md": 700,
    ".clinerules/00-master.md": 700,
    ".clinerules/10-memory-bank.md": 700,
    ".agents/rules/00-master.md": 800,
    ".agents/rules/10-memory-bank.md": 800,
}

REQUIRED_GITIGNORE_PATTERNS = [
    ".env",
    ".env.*",
    "!.env.example",
    "env/credentials.json",
    "env/token.json",
    "*.pem",
    "*.key",
]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "__pycache__",
    "dist",
    "build",
    "out",
    "coverage",
    ".next",
    ".nuxt",
    ".cache",
    ".turbo",
    ".pytest_cache",
    ".mypy_cache",
}

TEXT_SUFFIXES = {
    ".example",
    ".gitignore",
    ".json",
    ".md",
    ".py",
    ".txt",
}

ASSIGNMENT_RE = re.compile(r"(?i)^\s*([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*)\s*[:=]\s*(.+?)\s*$")
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
LOCAL_PATH_RE = re.compile(r"(?i)([A-Z]:\\Users\\|/Users/|/home/)")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
TOKEN_VALUE_RE = re.compile(r"(?i)\b(ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,})\b")
SCANNER_SOURCE_PATTERNS = {
    ASSIGNMENT_RE.pattern,
    EMAIL_RE.pattern,
    LOCAL_PATH_RE.pattern,
    PRIVATE_KEY_RE.pattern,
    TOKEN_VALUE_RE.pattern,
}


def is_text_file(path: Path) -> bool:
    if path.name in {".gitignore", ".clineignore"}:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AI-agent project template structure.")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run a lightweight validation for FAST_INIT workflows.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fast_mode = args.fast

    required_files = FAST_REQUIRED_FILES if fast_mode else REQUIRED_FILES

    missing = [path for path in required_files if not (ROOT / path).is_file()]
    bad_adapters = []
    oversized = []
    sensitive_findings = [] if fast_mode else scan_sensitive_content()
    missing_gitignore_patterns = check_gitignore()

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

    if missing or bad_adapters or oversized or sensitive_findings or missing_gitignore_patterns:
        if missing:
            print("Missing required files:")
            for path in missing:
                print(f"  - {path}")
        if bad_adapters:
            print("Adapter files that do not reference AGENTS.md:")
            for path in bad_adapters:
                print(f"  - {path}")
        if oversized:
            print("Files exceeding startup/context budget:")
            for path, size, max_chars in oversized:
                print(f"  - {path}: {size} chars > {max_chars} chars")
        if sensitive_findings:
            print("Potential security-sensitive content:")
            for path, line_number, category in sensitive_findings:
                print(f"  - {path}:{line_number}: {category}")
        if missing_gitignore_patterns:
            print("Missing required .gitignore patterns:")
            for pattern in missing_gitignore_patterns:
                print(f"  - {pattern}")
        return 1

    if fast_mode:
        print("Template FAST validation passed.")
        print("Mode: --fast (lightweight startup/integration checks)")
    else:
        print("Template validation passed.")
        print("Mode: full")

    print(f"Checked {len(required_files)} required files and {len(ADAPTER_FILES)} adapters.")
    print(f"Checked {len(CONTEXT_BUDGETS)} startup/context budgets.")
    if fast_mode:
        print("Checked .gitignore safety patterns.")
        print("Skipped repository-wide secret hygiene scan in fast mode.")
    else:
        print("Checked public-template secret hygiene and .gitignore safety patterns.")
    return 0


if __name__ == "__main__":
    sys.exit(main())