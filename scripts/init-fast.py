"""FAST_INIT helper for freshly copied template repositories.

Runs lightweight template validation and prints a short initialization prompt
that users can paste into their coding agent.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

FAST_PROMPT = """FAST_INIT + TOKEN_SAVER.
Follow AGENTS.md initialization modes exactly.
Use minimal turns and minimal narration.
Update only allowed Memory Bank files.
Keep unknowns as TBD.
Ask only critical questions before any escalation.
Return a short final summary."""


def run_fast_validation() -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / "check-template.py"), "--fast"]
    completed = subprocess.run(cmd, cwd=ROOT)
    return completed.returncode


def main() -> int:
    print("== FAST_INIT bootstrap ==", flush=True)
    print("Running lightweight template validation...\n", flush=True)

    code = run_fast_validation()
    if code != 0:
        print("\nFast validation failed. Fix issues above before initialization.")
        return code

    print("\nValidation succeeded.")
    print("\nPaste this into a new agent context window:\n")
    print("---")
    print(FAST_PROMPT)
    print("---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
