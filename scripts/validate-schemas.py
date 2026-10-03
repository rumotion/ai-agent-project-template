#!/usr/bin/env python3
"""Validate the portable subagent contract schemas and example envelopes.

Implements the small JSON Schema subset the contract uses (type, required,
properties, additionalProperties, items, enum, minItems, maxItems,
minLength, maxLength, minimum, maximum, pattern) with the Python standard
library only, so CI and fresh clones can enforce the portable subagent
contract without installing the `jsonschema` package.

Usage:

    python scripts/validate-schemas.py                       # validate examples
    python scripts/validate-schemas.py --self-test           # deterministic harness
    python scripts/validate-schemas.py --schema <schema.json> --instance <file>

Exit codes: 0 valid, 1 invalid, 2 usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List
from contract_checks import MAX_ENVELOPE_BYTES, task_errors, result_errors


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
SCHEMAS = {
    "task": SCHEMA_DIR / "subagent-task.schema.json",
    "result": SCHEMA_DIR / "subagent-result.schema.json",
}
EXAMPLES = {
    "task": SCHEMA_DIR / "examples" / "task-valid.json",
    "result": SCHEMA_DIR / "examples" / "result-valid.json",
}


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    if len(raw) > MAX_ENVELOPE_BYTES:
        raise ValueError("JSON document exceeds byte limit")
    def unique(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise ValueError("duplicate JSON property")
            data[key] = value
        return data
    def nonfinite(value):
        raise ValueError("nonfinite JSON number")
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique, parse_constant=nonfinite)


KEYWORDS = {"$schema", "$id", "title", "description", "type", "required",
            "properties", "additionalProperties", "items", "enum", "const",
            "minItems", "maxItems", "minLength", "maxLength", "minimum",
            "maximum", "pattern", "uniqueItems"}


def schema_errors(schema: Any, where: str = "schema") -> List[str]:
    if not isinstance(schema, dict):
        return [where + ": schema must be an object"]
    errors = [where + ": unsupported keyword " + k for k in schema if k not in KEYWORDS]
    if "type" in schema and (not isinstance(schema["type"], str) or schema["type"] not in {"object", "array", "string", "integer", "number", "boolean", "null"}):
        errors.append(where + ": unsupported type")
    for keyword in ("minItems", "maxItems", "minLength", "maxLength"):
        if keyword in schema and (type(schema[keyword]) is not int or schema[keyword] < 0):
            errors.append(where + ": invalid " + keyword)
    if "required" in schema and (not isinstance(schema["required"], list) or not all(isinstance(k, str) for k in schema["required"])):
        errors.append(where + ": invalid required")
    if "additionalProperties" in schema and type(schema["additionalProperties"]) is not bool:
        errors.append(where + ": additionalProperties must be boolean")
    if "enum" in schema and (not isinstance(schema["enum"], list) or not schema["enum"]):
        errors.append(where + ": enum must be a nonempty array")
    if "uniqueItems" in schema and type(schema["uniqueItems"]) is not bool:
        errors.append(where + ": uniqueItems must be boolean")
    for keyword in ("minimum", "maximum"):
        if keyword in schema and (type(schema[keyword]) not in (int, float) or (isinstance(schema[keyword], float) and not math.isfinite(schema[keyword]))):
            errors.append(where + ": invalid numeric bound")
    if "pattern" in schema:
        try:
            re.compile(schema["pattern"])
        except (TypeError, re.error):
            errors.append(where + ": invalid pattern")
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        errors.append(where + ": properties must be an object")
    else:
        for key, value in properties.items():
            errors.extend(schema_errors(value, where + "." + key))
    if "items" in schema:
        errors.extend(schema_errors(schema["items"], where + "[]"))
    return errors


def validate(instance: Any, schema: Dict[str, Any], where: str) -> List[str]:
    """Validate one instance against the supported schema subset."""
    errors: List[str] = schema_errors(schema)
    if errors:
        return errors
    if "const" in schema and (instance != schema["const"] or isinstance(instance, bool) != isinstance(schema["const"], bool)):
        return [where + ": const mismatch"]

    if "enum" in schema and not any(instance == value and isinstance(instance, bool) == isinstance(value, bool) for value in schema["enum"]):
        errors.append("{}: {!r} not in enum {}".format(where, instance, schema["enum"]))
        return errors

    expected = schema.get("type")
    if expected:
        checks = {
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "null": lambda v: v is None,
        }
        if expected not in checks:
            errors.append("{}: validator does not support type {!r}".format(where, expected))
            return errors
        if not checks[expected](instance):
            errors.append("{}: expected {}, got {}".format(where, expected, type(instance).__name__))
            return errors

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append("{}: shorter than minLength {}".format(where, schema["minLength"]))
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append("{}: longer than maxLength {}".format(where, schema["maxLength"]))
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append("{}: does not match pattern {}".format(where, schema["pattern"]))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if isinstance(instance, float) and not math.isfinite(instance):
            return [where + ": number must be finite"]
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append("{}: below minimum {}".format(where, schema["minimum"]))
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append("{}: above maximum {}".format(where, schema["maximum"]))

    if isinstance(instance, list):
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in instance}) != len(instance):
            errors.append(where + ": duplicate array items")
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append("{}: fewer than minItems {}".format(where, schema["minItems"]))
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append("{}: more than maxItems {}".format(where, schema["maxItems"]))
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], "{}[{}]".format(where, index)))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("{}: missing required property {!r}".format(where, key))
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate(value, properties[key], "{}.{}".format(where, key)))
            elif schema.get("additionalProperties") is False:
                errors.append("{}: additional property {!r} not allowed".format(where, key))

    return errors


def validate_examples() -> List[str]:
    errors: List[str] = []
    for kind in ("task", "result"):
        schema_path = SCHEMAS[kind]
        example_path = EXAMPLES[kind]
        if not schema_path.is_file():
            errors.append("missing schema {}".format(schema_path.name))
            continue
        if not example_path.is_file():
            errors.append("missing example {}".format(example_path.name))
            continue
        try:
            schema = load_json(schema_path)
            example = load_json(example_path)
        except ValueError as err:
            errors.append("{}: invalid JSON: {}".format(schema_path.name, err))
            continue
        if not isinstance(schema, dict) or schema.get("$id") != schema_path.name:
            errors.append("{}: $id must equal the file name".format(schema_path.name))
            continue
        found = validate(example, schema, kind)
        errors.extend(found)
        if not found:
            errors.extend(task_errors(example) if kind == "task" else result_errors(example))
    if not errors:
        errors.extend(result_errors(load_json(EXAMPLES["result"]), load_json(EXAMPLES["task"])))
    return errors


def run_self_test() -> None:
    schema = load_json(SCHEMAS["task"])
    valid = load_json(EXAMPLES["task"])

    def expect_errors(instance: Any, needle: str) -> None:
        found = validate(instance, schema, "self-test")
        assert any(needle in e for e in found), "expected error containing {!r}, got {}".format(needle, found)

    assert not validate(valid, schema, "self-test"), "valid example must validate"

    missing = dict(valid)
    missing.pop("budget")
    expect_errors(missing, "required property")

    bad_type = dict(valid)
    bad_type["read_only"] = "yes"
    expect_errors(bad_type, "expected boolean")

    bad_enum = dict(valid)
    bad_enum["isolation"] = {
        "context_policy": "whatever",
        "mask_secrets": True,
        "memory_bank_writes": "parent-only",
    }
    expect_errors(bad_enum, "not in enum")

    bad_pattern = dict(valid)
    bad_pattern["task_id"] = "Bad Task Id"
    expect_errors(bad_pattern, "pattern")

    bad_extra = dict(valid)
    bad_extra["surprise"] = 1
    expect_errors(bad_extra, "additional property")

    bad_range = dict(valid)
    bad_range["budget"] = {"max_turns": 500, "max_repairs": 2, "max_output_tokens": 2000}
    expect_errors(bad_range, "above maximum")

    empty_paths = dict(valid)
    empty_paths["owned_paths"] = []
    assert not validate(empty_paths, schema, "read-only"), "empty ownership is valid for reviewers"

    nested_extra = dict(valid)
    nested_extra["budget"] = {"max_turns": 10, "max_repairs": 1, "max_output_tokens": 100, "oops": 1}
    expect_errors(nested_extra, "additional property 'oops'")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run deterministic harness tests.")
    parser.add_argument("--schema", type=Path, help="Validate one instance against this schema file.")
    parser.add_argument("--instance", type=Path, help="Instance JSON file (requires --schema).")
    parser.add_argument("--task", type=Path, help="Dispatched task for result consistency checks.")
    parser.add_argument("--root", type=Path, help="Workspace for path/symlink containment checks.")
    parser.add_argument("--output-tokens", type=int, help="Trusted provider output-token telemetry.")
    parser.add_argument("--require-usage", action="store_true", help="Require trusted token telemetry with --task.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if (args.require_usage or args.output_tokens is not None or args.task) and (
            not args.task or not args.schema or not args.instance):
        print("error: paired usage checks require --task, --schema and --instance", file=sys.stderr)
        return 2
    if args.output_tokens is not None and args.output_tokens < 0:
        print("error: --output-tokens must be nonnegative", file=sys.stderr)
        return 2

    if args.self_test:
        try:
            run_self_test()
        except (AssertionError, OSError, ValueError) as err:
            print("FAIL: {}".format(err), file=sys.stderr)
            return 1
        print("Subagent schema validator self-test passed.")
        return 0

    if args.schema or args.instance:
        if not args.schema or not args.instance:
            print("error: --schema and --instance must be used together", file=sys.stderr)
            return 2
        try:
            schema = load_json(args.schema)
            instance = load_json(args.instance)
        except (OSError, ValueError) as err:
            print("error: {}".format(err), file=sys.stderr)
            return 2
        errors = validate(instance, schema, "instance")
        if not errors and schema.get("$id") == "subagent-task.schema.json":
            errors.extend(task_errors(instance, args.root))
        if not errors and schema.get("$id") == "subagent-result.schema.json":
            try:
                task = load_json(args.task) if args.task else None
                if task is not None:
                    errors.extend(validate(task, load_json(SCHEMAS["task"]), "task"))
                    if not errors:
                        errors.extend(task_errors(task, args.root))
                if not errors:
                    errors.extend(result_errors(instance, task, args.root, args.output_tokens, args.require_usage))
            except (OSError, ValueError) as error:
                print("error: {}".format(error), file=sys.stderr)
                return 2
        if errors:
            print("Instance violates {}:".format(args.schema.name), file=sys.stderr)
            for error in errors:
                print("  - {}".format(error), file=sys.stderr)
            return 1
        print("Instance validates against {}.".format(args.schema.name))
        return 0

    errors = validate_examples()
    if errors:
        print("Subagent contract schema violations:", file=sys.stderr)
        for error in errors:
            print("  - {}".format(error), file=sys.stderr)
        return 1
    print("Subagent contract schemas and examples validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
