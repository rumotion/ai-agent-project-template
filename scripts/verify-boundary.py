#!/usr/bin/env python3
"""Verify advisory inspection and refusal of unsupported stronger profiles."""
from pathlib import Path
from copy import deepcopy
from datetime import date
import json
import re
import subprocess
import sys
import tempfile
import boundary
import importlib.util
from push_backstop import install


def verify_capability_declarations(root, adapters):
    """Validate declared evidence metadata, never certify native behavior."""
    assert len(adapters) == len(boundary.CLIENTS)
    assert {entry["client"] for entry in adapters} == set(boundary.CLIENTS)
    for entry in adapters:
        status = entry["status"]
        assert status in {"synthetic-only", "unverified", "unverified-active", "live-smoke-partial"}
        if status != "live-smoke-partial":
            assert entry["version"] is None and entry["live_evidence"] is None
            assert not any(entry.get(key) for key in ("observed_at", "source_revision", "live_checks", "unverified_checks"))
            continue
        assert isinstance(entry["version"], str) and re.fullmatch(r"\d+\.\d+\.\d+", entry["version"])
        date.fromisoformat(entry["observed_at"])
        assert re.fullmatch(r"[a-f0-9]{40}", entry["source_revision"])
        report = entry["live_evidence"]
        assert isinstance(report, str) and report.startswith("docs/") and report.endswith(".md")
        assert "\\" not in report and not any(part in {"", ".", ".."} for part in report.split("/"))
        path = (root / report).resolve()
        path.relative_to(root.resolve())
        assert path.is_file()
        for key in ("live_checks", "unverified_checks"):
            values = entry[key]
            assert isinstance(values, list) and 1 <= len(values) <= 8
            assert all(isinstance(value, str) and 1 <= len(value) <= 200 for value in values)


def main():
    root_source = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("validator", root_source / "scripts/validate-schemas.py")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    schema = validator.load_json(root_source / "schemas/boundary-inspection.schema.json")
    adapters = validator.load_json(root_source / "schemas/adapter-capabilities.json")["adapters"]
    verify_capability_declarations(root_source, adapters)
    # Unknown is a valid default for a copied project; regressions must not
    # force a project to retain positive native claims merely to pass CI.
    unknown = deepcopy(adapters)
    for entry in unknown:
        entry.update(status="unverified", version=None, live_evidence=None)
        for key in ("observed_at", "source_revision", "live_checks", "unverified_checks"):
            entry.pop(key, None)
    verify_capability_declarations(root_source, unknown)
    declared = deepcopy(unknown)
    live_index = 0
    declared[live_index].update(status="live-smoke-partial", version="1.0.0",
                                live_evidence="docs/recovery-pilot.md", observed_at="2026-11-06",
                                source_revision="a" * 40, live_checks=["Synthetic declaration fixture"],
                                unverified_checks=["Not a native test"])
    verify_capability_declarations(root_source, declared)
    for key, invalid in (("version", None), ("observed_at", "invalid"),
                         ("source_revision", "unknown"), ("live_evidence", "../outside.md"),
                         ("live_checks", []), ("unverified_checks", [])):
        malformed = deepcopy(declared)
        malformed[live_index][key] = invalid
        try:
            verify_capability_declarations(root_source, malformed)
        except (AssertionError, TypeError, ValueError, KeyError):
            pass
        else:
            raise AssertionError("invalid native evidence declaration accepted: " + key)
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
