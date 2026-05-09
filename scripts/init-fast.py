"""FAST_INIT helper for freshly copied template repositories.

Runs lightweight template validation, prints a token-cost benchmark for the
FAST_INIT startup path, and prints a short initialization prompt to paste into
a coding agent.
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
If resuming, also read memory-bank/handoff.md.
Keep unknowns as TBD.
Ask only critical questions before any escalation.
Return a short final summary."""


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT).returncode


def main() -> int:
    print("== FAST_INIT bootstrap ==", flush=True)
    print("Running lightweight template validation...\n", flush=True)
    code = run([sys.executable, str(ROOT / "scripts" / "check-template.py"), "--fast"])
    if code != 0:
        print("\nFast validation failed. Fix issues above before initialization.", flush=True)
        return code

    print("", flush=True)
    run([sys.executable, str(ROOT / "scripts" / "check-template.py"), "--benchmark"])

    print("\nValidation succeeded.", flush=True)
    print("\nPaste this into a new agent context window:\n", flush=True)
    print("---", flush=True)
    print(FAST_PROMPT, flush=True)
    print("---", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
