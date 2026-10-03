#!/usr/bin/env python3
"""Check or regenerate tracked workflow/skill mirrors from canonical sources."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def pairs(root: Path):
    spec = importlib.util.spec_from_file_location("template_check", ROOT / "scripts/check-template.py")
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    for name in contract.WORKFLOW_FILES:
        for mirror in contract.WORKFLOW_MIRRORS:
            yield root / contract.WORKFLOW_CANONICAL / name, root / mirror / name
    for name in contract.SKILL_NAMES:
        directory = root / contract.SKILL_CANONICAL / name
        for source in sorted(directory.rglob("*")):
            if "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            if source.is_symlink():
                raise ValueError("symlink canonical source is unsupported")
            if source.is_file():
                for mirror in contract.SKILL_MIRRORS:
                    yield source, root / mirror / name / source.relative_to(directory)


def generate(root: Path, write: bool = False) -> list:
    root = root.resolve()
    changes = []
    # Validate every destination before writing any file.
    entries = list(pairs(root))
    for source, target in entries:
        source.resolve().relative_to(root)
        target.resolve().relative_to(root)
        if source.is_symlink() or target.is_symlink():
            raise ValueError("symlink adapter paths are unsupported")
        if not source.is_file():
            raise ValueError("missing canonical source: " + str(source.relative_to(root)))
    for source, target in entries:
        expected = source.read_bytes()
        if not target.is_file() or target.read_bytes() != expected:
            changes.append(target.relative_to(root).as_posix())
            if write:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(expected)
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        changes = generate(args.root, args.write)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    for path in changes:
        print(("Generated: " if args.write else "Drift: ") + path)
    if not changes:
        print("Canonical adapter mirrors verified.")
    return 0 if args.write or not changes else 1


if __name__ == "__main__":
    sys.exit(main())
