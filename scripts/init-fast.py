"""FAST_INIT helper for freshly copied template repositories.

Runs lightweight template validation, prints a token-cost benchmark for the
FAST_INIT startup path, and prints a short initialization prompt to paste into
a coding agent.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

FAST_PROMPT = """FAST_INIT (default mode per AGENTS.md).
Follow AGENTS.md initialization modes exactly (FAST_INIT; DEEP_AUDIT only on request).
Use minimal turns and minimal narration.
Update only allowed Memory Bank files.
If resuming, also read memory-bank/handoff.md.
Keep unknowns as TBD; escalate only when facts cannot be verified.
Commit each verified plan step atomically (Conventional Commits).
Return a short final summary."""


def _configure_stdout_utf8() -> None:
    # Windows consoles often default to cp1251/cp1252 and crash on non-ASCII.
    # Force UTF-8 on stdout/stderr where supported (Python 3.7+).
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def safe_print(text: str) -> None:
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", "ascii") or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"), flush=True)


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT).returncode


def handle_remotes(keep_remote: bool = False) -> None:
    if keep_remote:
        safe_print("Keeping git remotes (--keep-remote specified).\n")
        return

    # Check if inherited template remotes are present
    check_code = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "detach-remote.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).returncode

    if check_code == 1:
        safe_print("Inherited template remote detected. Securing repository boundaries...")
        run([sys.executable, str(ROOT / "scripts" / "detach-remote.py")])
        safe_print("")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FAST_INIT helper for freshly copied template repositories.")
    parser.add_argument(
        "--keep-remote",
        action="store_true",
        help="Keep inherited template remotes (for template repository maintainers only).",
    )
    return parser.parse_args()


def main() -> int:
    _configure_stdout_utf8()
    args = parse_args()

    safe_print("== FAST_INIT bootstrap ==")
    handle_remotes(keep_remote=args.keep_remote)

    safe_print("Running lightweight template validation...\n")
    code = run([sys.executable, str(ROOT / "scripts" / "check-template.py"), "--fast"])
    if code != 0:
        safe_print("\nFast validation failed. Fix issues above before initialization.")
        return code

    safe_print("")
    run([sys.executable, str(ROOT / "scripts" / "check-template.py"), "--benchmark"])

    safe_print("\nValidation succeeded.\n")
    safe_print("=" * 60)
    safe_print("WELCOME TO THE AI AGENT PROJECT TEMPLATE")
    safe_print("=" * 60)
    safe_print("What this template gives you out of the box:")
    safe_print(" * One canonical instruction file (AGENTS.md) read by every model")
    safe_print("   (Claude, Gemini, ChatGPT/Codex, Cline, Roo Code, Cursor, Windsurf,")
    safe_print("   Copilot, Aider, Antigravity) - no per-tool rewrites.")
    safe_print(" * Repository boundary security: projects are local-only by default")
    safe_print("   with automatic push-blocks preventing accidental upstream pushes.")
    safe_print(" * Shared Memory Bank for cross-session and cross-model continuity")
    safe_print("   (handoff.md lets one model pick up where another left off).")
    safe_print(" * FAST_INIT bootstrap (~2.2K tokens) so agents skip the usual")
    safe_print("   5K-80K token \"read the whole repo\" warm-up.")
    safe_print(" * Agentic execution loop: Plan - Execute - Verify - Commit -")
    safe_print("   Reflect with atomic step-commits (docs/agent-loop.md).")
    safe_print(" * Drift-proof mirrors of workflows and skills (SHA-256 checked).")
    safe_print(" * Zero-dependency validator (Python stdlib only).")
    safe_print(" * Reusable workflows + skills (plan, implement, debug, refactor,")
    safe_print("   handoff, critic-review, autonomous-agent) ready to lazy-load.")
    safe_print(" * Client-specific MCP guidance + opt-in hooks (docs/hooks.md).")
    safe_print(" * Proactive power-ups: agents will suggest Graphify, Calibration,")
    safe_print("   or steering prompts (/align, /devil, /burst) as your project")
    safe_print("   grows. See docs/toolbox.md for the full list.")
    safe_print("")
    safe_print("Next: paste the prompt below into a fresh agent context window.")
    safe_print("=" * 60)

    safe_print("\nPaste this into a new agent context window:\n")
    safe_print("---")
    safe_print(FAST_PROMPT)
    safe_print("---")
    return 0


if __name__ == "__main__":
    sys.exit(main())

