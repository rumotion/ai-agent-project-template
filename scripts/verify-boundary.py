#!/usr/bin/env python3
"""Verify advisory inspection and refusal of unsupported stronger profiles."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import boundary
import importlib.util
from push_backstop import install


def main():
    root_source = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("validator", root_source / "scripts/validate-schemas.py")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    schema = validator.load_json(root_source / "schemas/boundary-inspection.schema.json")
    adapters = validator.load_json(root_source / "schemas/adapter-capabilities.json")["adapters"]
    assert {a["client"] for a in adapters} == set(boundary.CLIENTS)
    assert all(a["version"] is None and a["live_evidence"] is None for a in adapters)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        assert not boundary.verified(boundary.inspect(root, "codex"))
        install(root)
        for client in boundary.CLIENTS:
            document = boundary.inspect(root, client)
            assert not validator.validate(document, schema, "boundary")
            assert boundary.verified(document)
            assert not document["tool_events_verified"]
            for profile in ("contained-local", "release"):
                assert not boundary.verified(boundary.inspect(root, client, profile))
        cli = [sys.executable, str(Path(__file__).with_name("boundary.py")),
               "verify", "--root", str(root), "--json"]
        assert subprocess.run(cli, capture_output=True).returncode == 0
        assert subprocess.run(cli + ["--profile", "contained-local"], capture_output=True).returncode == 1
        subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", "custom"], check=True)
        assert not boundary.verified(boundary.inspect(root, "codex"))
    print(json.dumps({"clients_checked": len(boundary.CLIENTS), "unsupported_profiles_refused": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
