"""Run canonical hooks from the Antigravity customization directory.

The configured file path is relative to the customization directory. Handler
imports use this file's directory, never event payloads. Existing Gemini-format
guard decisions remain unchanged; benign calls defer to normal platform policy.
"""
from contextlib import redirect_stdout
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HANDLERS = ("guard-remote-ops.py", "guard-sensitive-paths.py", "log-writes.py")


def dispatch(handler):
    try:
        spec = importlib.util.spec_from_file_location("canonical_hook", HERE / handler)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = io.StringIO()
        with redirect_stdout(output):
            if handler == "log-writes.py":
                code = module.main("gemini", workspace_root=str(HERE.parents[1]))
            else:
                code = module.main("gemini")
        if code not in (None, 0):
            raise ValueError("canonical hook failed")
        text = output.getvalue().strip()
        result = json.loads(text) if text else ({} if handler == "log-writes.py" else {"decision": "allow"})
        if not isinstance(result, dict):
            raise ValueError("invalid hook output")
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception:
        # No local paths, event arguments or user content in diagnostics.
        sys.stderr.write("repository_hook_unavailable\n")
        if handler == "log-writes.py":
            print("{}")
            return 0
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handler", choices=HANDLERS)
    parser.add_argument("--client", choices=("gemini",), required=True)
    args = parser.parse_args()
    return dispatch(args.handler)


if __name__ == "__main__":
    sys.exit(main())
