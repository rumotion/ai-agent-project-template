#!/usr/bin/env python3
"""Generate an exact proposed diff without changing scripts/ctx.py."""
from __future__ import annotations
import ast
import difflib
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
original = (HERE / "baseline-ctx.txt").read_text(encoding="utf-8")
updated = original


def replace_function(name, content):
    global updated
    pattern = r"(?ms)^def " + re.escape(name) + r"\(.*?(?=^def |\Z)"
    updated, count = re.subn(pattern, lambda _: content.strip() + "\n\n\n", updated, count=1)
    assert count == 1, name


updated = updated.replace("BODY_SNIPPET_CHARS = 400", "MAX_SOURCE_BYTES = 16_384")
updated = updated.replace("    lines = text.splitlines()", "    lines = text.lstrip('\\ufeff').splitlines()", 1)
updated = updated.replace("    except StopIteration:\n        return {}, text", "    except StopIteration:\n        raise ValueError('unterminated front matter')", 1)
updated = updated.replace("            fields[key.strip()] = value.strip()", "            key = key.strip()\n            if key in fields:\n                raise ValueError('duplicate front-matter key')\n            fields[key] = value.strip()", 1)
updated = updated.replace('encoding="utf-8", errors="replace"', 'encoding="utf-8-sig"')
updated = updated.replace("    if not records_dir.is_dir():\n        return records, errors", "    if not records_dir.is_dir():\n        return records, ['missing memory-bank/records directory']", 1)
updated = updated.replace('        fields, body = parse_front_matter(path.read_text(encoding="utf-8-sig"))', '''        try:
            if path.is_symlink() or path.stat().st_size > MAX_SOURCE_BYTES:
                raise ValueError("record is a symlink or exceeds source byte limit")
            fields, body = parse_front_matter(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            errors.append("{}: unreadable or malformed record".format(path.relative_to(root).as_posix()))
            continue''', 1)
updated = updated.replace('if not priority_raw.isdigit() or not 1 <= int(priority_raw) <= 5:', 'if not re.fullmatch(r"[1-5]", priority_raw):', 1)
updated = updated.replace('"body": " ".join(body.split())[:BODY_SNIPPET_CHARS],', '"body": " ".join(body.split()),', 1)

replace_function("active_records", '''
def active_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Require a unique, acyclic, same-type supersession graph."""
    by_id: Dict[str, Dict[str, Any]] = {}
    for record in records:
        rid = record["id"]
        if rid in by_id:
            raise ValueError("duplicate record id")
        by_id[rid] = record
    for record in records:
        target = record["superseded_by"]
        if target:
            if target not in by_id or target == record["id"]:
                raise ValueError("missing successor or self supersession")
            if by_id[target]["type"] != record["type"]:
                raise ValueError("supersession must preserve record type")
    done = set()
    for rid in by_id:
        chain = set()
        cursor = rid
        while cursor and cursor not in done:
            if cursor in chain:
                raise ValueError("supersession cycle")
            chain.add(cursor)
            cursor = by_id[cursor]["superseded_by"]
        done.update(chain)
    return ([r for r in records if not r["superseded_by"]],
            [r for r in records if r["superseded_by"]])
''')

replace_function("compile_context", '''
def compile_context(root: Path, client: str, max_chars: int) -> Dict[str, Any]:
    status: Dict[str, str] = {}
    records: List[Dict[str, Any]] = []
    errors: List[str] = []
    active: List[Dict[str, Any]] = []
    superseded: List[Dict[str, Any]] = []
    if max_chars < 1:
        errors.append("max_chars must be positive")
    try:
        status = load_handoff_status(root)
        records, record_errors = load_records(root)
        errors.extend(record_errors)
        if not errors:
            active, superseded = active_records(records)
    except (OSError, ValueError):
        errors.append("invalid handoff or supersession graph")
    if errors:
        blob, kept, dropped, over_budget = "", [], [], False
    else:
        blob, kept, dropped, over_budget = distill(client, status, active, max_chars)
    return {
        "client": client, "blob": blob,
        "blob_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
        "chars": len(blob), "est_tokens": len(blob) // 4,
        "max_chars": max_chars, "included": [r["id"] for r in kept],
        "dropped": [r["id"] for r in dropped],
        "superseded": [r["id"] for r in superseded],
        "malformed": errors, "over_budget": over_budget,
    }
''')

updated = updated.replace('        first = compile_context(root, "claude", DEFAULT_MAX_CHARS)', '''        invalid = compile_context(root, "claude", DEFAULT_MAX_CHARS)
        assert invalid["malformed"] and invalid["blob"] == ""
        (records_dir / "z-bad.md").unlink()
        first = compile_context(root, "claude", DEFAULT_MAX_CHARS)''', 1)
updated = updated.replace('assert len(first["malformed"]) == 1 and "z-bad.md" in first["malformed"][0]', 'assert not first["malformed"]', 1)
updated = updated.replace('    if args.json:\n', '''    if result["malformed"] or result["over_budget"]:
        # Machine mode preserves diagnostics, but never emits usable invalid context.
        result["blob"] = ""
        result["blob_sha256"] = hashlib.sha256(b"").hexdigest()
        result["projected_chars"] = result["chars"]
        result["chars"] = 0
        result["est_tokens"] = 0
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("ctx: invalid or over-budget context; inspect --json diagnostics", file=sys.stderr)
        return 1

    if args.json:
''', 1)
updated = updated.replace('Exit codes: 0 ok, 1 over-budget or malformed records (with --check; or\n', 'Exit codes: 0 ok, 1 over-budget or malformed records (in every compile mode; or\n')
updated = updated.replace('if records are malformed or the blob is still over budget after distillation.', 'on validation failure (retained for CLI compatibility).')
updated = updated.replace('    args = parse_args()\n', '''    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
''', 1)
ast.parse(updated, feature_version=(3, 9))
diff = "".join(difflib.unified_diff(original.splitlines(keepends=True), updated.splitlines(keepends=True), fromfile="a/scripts/ctx.py", tofile="b/scripts/ctx.py"))
if __name__ == "__main__":
    (HERE / "context-integrity.patch").write_text(diff, encoding="utf-8", newline="\n")
    print("Generated context-integrity.patch; production compiler unchanged.")
