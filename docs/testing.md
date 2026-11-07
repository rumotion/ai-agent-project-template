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

- FAST_INIT is at most 9,500 characters.
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
- Native hook examples use synthetically exercised event names and pass an explicit
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
- a FAST_INIT payload over 9,500 characters;
- a literal token or non-placeholder secret assignment.
- a machine-local file URI;
- a native hook event that omits its explicit client adapter.
- a reviewer adapter missing the v1 marker, canonical path, or declared
  read-only restriction;
- a benchmark manifest missing one of the five required scenario IDs;
- an empty/malformed manual usage record.

Keep fixtures outside the repository or restore them before full validation.

## CI and native smoke checks

CI runs fast, full and startup benchmark modes on Windows and Linux with
Python 3.9 and current Python 3.x. The full gate already includes compatibility
contracts and the context-harness self-test; CI does not repeat them through
`--compat` or another self-test invocation. The standalone commands remain
available for targeted local checks.

Before a tagged release, use the manual checklist in
[`agent-compatibility.md`](agent-compatibility.md) with installed Gemini CLI,
Codex, and Claude Code clients. Record client versions and any unavailable
entitlement; do not make paid model calls solely for structural CI.

Keep quick command references in `memory-bank/techContext.md`.

## Second-order regressions

Full validation also runs the context integrity, strict contract, push installer,
boundary refusal, adversarial shell and generated-adapter checks. Individual
commands are `scripts/verify-context.py`, `scripts/verify-contracts.py`,
`scripts/verify-backstop.py`, `scripts/verify-boundary.py`,
`scripts/hooks/verify-hardening.py`, and `scripts/gen-adapters.py --check`.
The full gate also runs `scripts/verify-continuity.py`: private checkpoint,
cross-client restore, dirty-input and branch changes, corrupt/scalar handoff,
interleaved edits, writer-lock refusal and visible hook-failure regressions.
`scripts/verify-records.py` covers read-back receipts, task selection over a
1,000-record archive, qualifier retention, immutable IDs, supersession, required
budget refusal and failed writes. Native recall remains a separate smoke check.
`scripts/verify-tasks.py` covers private task restart, dirty/add/delete inventories,
ignored explicit inputs, revision/attempt conflicts, parent-only acceptance,
changed review artifacts, dependencies, WIP/ownership (including queued blockers),
atomic failure preservation and bounded cross-process listing.
`scripts/verify-task-metrics.py` covers ordinary-task arithmetic and hard-budget
advice; it never activates pacing. `scripts/verify-recovery.py` combines required
decisions, qualifiers, handoff, receipts and multiple open tasks across fresh
processes and renderer switches. Its eight scenarios are synthetic; see
`docs/recovery-pilot.md` for the separately observed native scope and open gates.
`scripts/verify-antigravity-hooks.py` executes the configured commands from
`.agents` through shell and direct argv, with varied requested tool directories.
Its 12 cases check harmless listing, denials, explicit JSON, write_file/Path
aliases, conflicting-path protection and root-bounded metadata-only logging.
`scripts/verify-windows-hooks.py` executes Codex's configured PowerShell strings
from root/config/nested process directories in paths with spaces and brackets.
Four cases cover benign calls, sensitive patches, synthetic publishing denials
and log placement. They run on Windows and skip on other operating systems.
Neither suite calls a model or performs an actual publishing operation.
The continuity suite also checks client-specific startup renderers, diagnostic
commands and Codex lifecycle mapping. The Windows suite executes its startup
command from nested directories against a required-record fixture. Native
startup/resume/compact read-back is a separate bounded pilot, never a CI model
call; its markers are introduced after the previous turn to reject stale recall.
The dated native pilot also covers one reduced-threshold mid-turn tool
continuation and an explicit inert MCP mapping. Those are scoped manual
observations, not CI model calls or default MCP activation; see recovery-pilot.md.
After editing canonical skills/workflows, run `scripts/gen-adapters.py --write`
and review the generated diff. Tracked discovery files remain available in
fresh clones. Live client denials, Linux execution, actual Python 3.9 execution,
provider token/cache measurements and external containment require separate
host-specific evidence; synthetic fixtures do not establish them.

## Usage pacing regressions

`python scripts/verify-usage-pacing.py` uses temporary SQLite databases and
simulated timestamps. It exercises explicit plan confirmation, terminal stop,
stale/missing telemetry, rate measurement, count-change boundaries, short-window
constraints, quota reserves, resets, context handoff, sanitized statusline
ingestion, cost snapshot semantics, invalid input and concurrent writers.
Full validation runs it automatically. No model calls, credentials, quota use
or live client integration are needed. Live statusline wiring and background
completion notifications need a separate native-client smoke test.

Completion-board cases additionally cover dependency acceptance, WIP defaults,
review/blocked backpressure, unknown or insufficient completion costs across
all quota windows, the 50% estimate margin, context draining at 75%, stale or
invalid boards, mismatched run/worker counts and early queue completion.
These checks prove advisory decisions only, not native dispatch/cancellation.

## Template upgrade preservation

Run `python scripts/verify-upgrade.py` for temporary-project checks of domain
file/rule/memory preservation, idempotence, known-release baselines, local edits,
custom and retired skill helpers, external backups, rollback and concurrent
edits. The suite also uses a real local Git fetch/archive, commit mismatch,
archive traversal rejection and Windows junction redirection checks. A symlink
case is skipped when the Windows account cannot create links. The suite runs in
full template validation; it does not contact hosted GitHub/GitLab or use credentials.

Windows bootstrap checks also cover a real long-path initial commit and an
explicit failed-add result that prevents a misleading commit attempt. New
Windows repositories enable local core.longpaths; existing/global settings are
preserved. See the dated native/packaging follow-ups in recovery-pilot.md.
