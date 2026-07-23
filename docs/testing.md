# Testing

The template uses deterministic, standard-library-only structural validation.
Model quality and hosted-client availability are not CI requirements.

## Local verification

Run after changes to instructions, skills, Memory Bank startup files, MCP
guidance, or adapters:

```bash
python scripts/check-template.py --fast
python scripts/check-template.py --compat
python scripts/check-template.py --benchmark
python scripts/benchmark-context.py --self-test
python scripts/benchmark-context.py --scenario fast-init
```

Before release, also run:

```bash
python -m py_compile scripts/check-template.py
python -m py_compile scripts/benchmark-context.py
python -m compileall -q scripts/hooks
python scripts/hooks/verify-fixtures.py
python scripts/check-template.py
python scripts/init-fast.py
git diff --check
```

Expected invariants:

- FAST_INIT is at most 7,600 characters.
- `GEMINI.md`, `CLAUDE.md`, and `.codex/AGENTS.md` are exact thin adapters.
- Every canonical `.agents/skills/*/SKILL.md` has valid minimal frontmatter.
- Canonical skills and `.claude/skills` / `.cline/skills` mirrors have equal
  SHA-256 hashes.
- Gemini, Codex, and Claude MCP paths appear in the compatibility contract.
- The three native reviewer adapters contain `reviewer-contract: v1`, point to
  `docs/reviewer-role.md`, and declare their strongest verified read-only
  restrictions. These checks are structural, not behavioral proof.
- The context harness self-test passes and its FAST_INIT count equals the
  validator's count.
- Native hook examples use verified event names and pass an explicit
  `--client` value to the shared scripts.
- Hook fixtures write only to a temporary directory and prove normalized
  output, path redaction, malformed-input handling, and denial JSON.
- Secret-like values are absent from repository text and config examples.

## Regression cases

When changing the validator, exercise both passing and failing behavior. A
temporary fixture should prove that validation rejects:

- a primary adapter with an extra policy line;
- a skill with a missing or mismatched `name` or empty `description`;
- a changed skill mirror;
- a FAST_INIT payload over 7,600 characters;
- a literal token or non-placeholder secret assignment.
- a machine-local file URI;
- a native hook event that omits its explicit client adapter.
- a reviewer adapter missing the v1 marker, canonical path, or declared
  read-only restriction;
- a benchmark manifest missing one of the five required scenario IDs;
- an empty/malformed manual usage record.

Keep fixtures outside the repository or restore them before full validation.

## CI and native smoke checks

CI runs fast, full, compatibility, startup benchmark, and context-harness
self-test modes on Windows and Linux with Python 3.9 and the current Python 3.x
release.

Before a tagged release, use the manual checklist in
[`agent-compatibility.md`](agent-compatibility.md) with installed Gemini CLI,
Codex, and Claude Code clients. Record client versions and any unavailable
entitlement; do not make paid model calls solely for structural CI.

Keep quick command references in `memory-bank/techContext.md`.
