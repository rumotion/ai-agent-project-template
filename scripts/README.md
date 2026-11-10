# Scripts

## Overview

Deterministic local CLI scripts, safety hooks, and regression suites used by humans and agents across Gemini/Antigravity, Claude Code, Codex, and Cline. Standard library only (Python 3.9+) — no package installs required for template operation.

## Quick start (new users)

In a freshly cloned/copied template:

```bash
python scripts/init-fast.py
```

It will:

1. detect and detach inherited template remotes (making the project local-only and installing a pre-push block),
2. run `python scripts/check-template.py --fast`,
3. print the token cost of the FAST_INIT startup path,
4. print the FAST_INIT prompt to paste into a new agent context window.

## Interface

- **Invocation & Exit Semantics**: Run via `python scripts/<script>.py [options]` from the repository root. Unless noted otherwise, CLI entry points exit `0` on success/verification pass, `1` on validation/policy refusal or test failure, and `2` on invalid CLI arguments or blocked hook operations where required by the host client protocol.
- **Subdirectories**:
  - [`hooks/fixtures/`](./hooks/fixtures/README.md) — deterministic JSON hook payload fixtures and verification harness inputs.

### Included scripts

| Script | Purpose & Key Interface |
|---|---|
| `init-fast.py` | One-command bootstrap (`python scripts/init-fast.py`): detaches inherited template remotes, installs `pre-push` backstop, runs `--fast` check, and prints `FAST_INIT` cost + starter prompt. |
| `new-project.py` | Scaffolds a fresh project copy (`--name`, `--dest`, `--stack`, `--init-git`, `--force`), resets starter `README.md`/`VERSION`/`CHANGELOG.md`/`memory-bank/`, and initializes a local-only Git repo. |
| `detach-remote.py` | Detaches inherited template remotes (`--dry-run`, `--force`), installs `pre-push` block hook, and makes the repository local-only. |
| `push_backstop.py` | Shared library and installer (`install(root)`) for the unconditional POSIX `sh` `.git/hooks/pre-push` block; rejects LF/custom-hooksPath conflicts without clobbering user hooks. |
| `check-template.py` | Template validator. Modes: full (default, no flag), `--fast` (lightweight startup/budget check), `--compat` (cross-agent adapter/mirror contract), `--benchmark` (token cost), `--check-remote` (remote audit). |
| `gen-adapters.py` | Generates or verifies byte-identical workflow and skill mirrors across `.agents/`, `.claude/`, `.cline/`, and `.clinerules/` (`--write` to sync, `--check` to verify zero SHA-256 drift). |
| `upgrade-target.py` | Upgrades an existing project from a local path or GitHub/GitLab source (`--source`, `--target`, `--ref`, `--pin-sha`, `--dry-run`, `--backup-dir`) with SHA pinning, conflict preservation, and backups. |
| `template_upgrade.py` | Standard-library Git transport, explicit-path planning, and transactional file update engine backing `upgrade-target.py`; never executes upstream code. |
| `ctx.py` | Context Compiler (`compile --for <gemini\|claude\|codex\|cline\|cursor\|windsurf\|copilot> [--task <id>] [--check]`, `record`, `self-test`): builds deterministic, budget-capped startup projections from `memory-bank/records/`. |
| `continuity.py` | Local continuity state inspector and private milestone checkpointer (`doctor [--mode legacy\|strict]`, `checkpoint`, `restore`); zero model calls. See `docs/continuity.md`. |
| `tasks.py` | Durable private task board (`list`, `create`, `start`, `complete`, `review`, `accept`, `audit`) enforcing revision/attempt gates, owned-path scope, and parent acceptance. |
| `task_metrics.py`, `usage_math.py` | Sanitized task token/cost accounting, high-water reset detection, and hard-budget checks while keeping quota pacing `OFF` by default. |
| `routing_policy.py` | Offline worker/advisor/checkpoint escalation advice (`evaluate`, `--json`) with receipt binding; never dispatches agents or alters model defaults. See `docs/adaptive-model-routing.md`. |
| `boundary.py` | Inspects and verifies advisory client containment boundaries (`inspect --client <name> --json`, `verify --root <path> [--profile <name>]`); refuses unsupported `contained-local`/`release` profiles (`exit 1`). |
| `contract_checks.py` | Validates portable subagent task/result envelopes (`MAX_ENVELOPE_BYTES = 64_000`), relative path bounds, owned vs. forbidden write scopes, and verification evidence. |
| `validate-schemas.py` | Closed JSON Schema validator for `schemas/*.json` (`task-envelope`, `result-envelope`, `boundary-inspection`, `adapter-capabilities`, `context-record`). |
| `benchmark-context.py` | Offline manifest-based context measurement and sanitized paired-usage comparison (`--json`, `--self-test`). |
| `usage-pacing.py` | Optional human-confirmed quota pacing planner (`status`, `plan`, `record`, `--db`); makes no API calls and stays `OFF` until explicitly confirmed. See `docs/usage-pacing.md`. |
| `transcribe_local_large_v3.py` | Local GPU-first media transcription helper (`faster-whisper` `large-v3`, `cuda/float16` -> `cuda/int8_float16` -> CPU chunked) emitting local `.txt` and `.srt` transcripts. |
| `hooks/antigravity-dispatch.py` | Quote-free Antigravity hook launcher anchored relative to `.agents/` so event working directories cannot hijack script resolution. |
| `hooks/session-context.py` | Client-aware bounded `SessionStart` context injector for Claude Code and opt-in Codex hooks. |
| `hooks/log-writes.py` | Passive post-write event logger appending workspace-bounded metadata to `.agent-logs/session.jsonl`. |
| `hooks/guard-sensitive-paths.py` | Pre-tool path guard blocking edits/redirections to `.env`, keys, credentials, and protected paths across Claude, Gemini/Antigravity, and Codex. |
| `hooks/guard-remote-ops.py` | Pre-tool command guard blocking `git push`, `gh repo create/pr/release`, Git plumbing push routes, and inline interpreter (`python -c`) bypasses. |
| `hooks/shell_events.py` | Shared shell command tokenizer and redirection/path extractor used by pre-tool security guards. |
| `hooks/git/pre-push` | POSIX `sh` push backstop blocking `git push` even in clients without a native hook runtime. |
| `verify-upgrade.py`, `verify-antigravity-hooks.py`, `verify-windows-hooks.py`, `verify-usage-pacing.py`, `verify-continuity.py`, `verify-records.py`, `verify-tasks.py`, `verify-task-metrics.py`, `verify-routing-policy.py`, `verify-recovery.py`, `verify-backstop.py`, `verify-boundary.py`, `verify-context.py`, `verify-contracts.py`, `hooks/verify-fixtures.py`, `hooks/verify-hardening.py` | Deterministic offline regression suites executed by `python scripts/check-template.py` (full mode) to verify upgrades, hooks, boundaries, context compilation, task envelopes, and recovery. |

## Invariants

- **Stdlib-Only Core**: All template validators, context compilers, upgraders, and hooks use only the Python 3.9+ standard library (`transcribe_local_large_v3.py` is an optional local media utility).
- **Local-Only Boundary**: No script transmits repository data or calls external APIs; `hooks/guard-remote-ops.py` and `hooks/git/pre-push` block remote git publishing unless explicitly authorized by the human.
- **Read-Only Check Modes**: `check-template.py`, `gen-adapters.py --check`, `ctx.py compile --check`, `boundary.py inspect`, and `continuity.py doctor` never mutate tracked repository files.
- **Zero-Drift Mirrors & Budgets**: Canonical skills (`.agents/skills/`, `<= 24,000` bytes per `SKILL.md`) and workflows (`workflows/`) must stay SHA-256 identical to their mirrors across `.claude/`, `.cline/`, `.agents/workflows/`, and `.clinerules/workflows/`, and aggregate `FAST_INIT` startup context must remain `<= 9,500` characters.

## Side Effects

- **Git Config & Hook Installation**: `init-fast.py`, `detach-remote.py`, `new-project.py`, and `push_backstop.py` update local `.git/config` (removing inherited template `origin` and setting local `core.longpaths=true` on Windows) and write `.git/hooks/pre-push`.
- **Tracked Mirror & Record Updates**: `gen-adapters.py --write` writes mirrored workflow/skill files; `ctx.py record` writes typed markdown records under `memory-bank/records/` and updates `memory-bank/00-index.md`; `upgrade-target.py` writes external backups before updating framework files.
- **Private Untracked Logs & State**: `continuity.py`, `tasks.py`, `usage-pacing.py`, and `hooks/log-writes.py` read/write untracked local state under `.agent-logs/`. Verification scripts (`verify-*.py`) use isolated `tempfile.TemporaryDirectory()` fixtures and leave the working tree clean.

## Verification

- Fast startup & budget check: `python scripts/check-template.py --fast`
- Cross-client adapter & mirror check: `python scripts/check-template.py --compat` and `python scripts/gen-adapters.py --check`
- Full template & regression gate: `python scripts/check-template.py`

## Validator details

Full mode enforces:

- All files in the validator's required manifest are present.
- All adapter files reference `AGENTS.md`; Gemini, Claude, and Codex primary adapters match their exact thin-import forms.
- Startup/context size budgets respected, including a hard 9,500-character aggregate FAST_INIT ceiling.
- Canonical skill frontmatter is valid, each skill body is within the 24,000-byte load ceiling, and all configured skills/workflow entry points across three trees are present.
- Canonical workflow files and mirrors across three trees are present (12 workflows).
- `.gitignore` includes required safety patterns.
- Repository text scanned for secret-like content.
- SHA-256 hash equality across canonical and mirrored workflows and all three skill trees (zero drift).
- Hook fixture behavior, native hook adapter structure, and native MCP example structure.
- Native reviewer adapter markers/restrictions (including `paraphrase:`), dated advanced guidance, and
  the deterministic context-benchmark self-test.

## Rules

- Prefer simple, auditable scripts.
- Document inputs and side effects in the script's docstring.
- Do not store secrets in `scripts/`.
- Ask before adding scripts that call paid APIs or modify external systems.

Regenerate tracked skill/workflow mirrors with `python scripts/gen-adapters.py --write`; verify with `--check`. Inspect advisory boundaries with `python scripts/boundary.py inspect --client codex --json`. Stronger containment/release profiles are unsupported and fail verification. Full template validation includes the second-order regression scripts.

New Windows projects enable repository-local Git long-path support during
bootstrap. A failed git add is reported before commit; no global Git setting
is changed. The backstop suite exercises both cases.
