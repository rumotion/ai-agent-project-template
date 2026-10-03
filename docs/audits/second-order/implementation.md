# Implementation follow-up ? 2026-10-03

The report and results describe the original `6ea5081` audit snapshot. They are
historical evidence. The user subsequently authorized production implementation.

| Recommendation | Implemented | Remaining evidence or platform work |
|---|---|---|
| Default-local boundary | Shared unconditional installer, raw byte gate, linked-worktree resolution, conflict failures, boundary inspect/verify | External supervisor-owned containment and release launchers unsupported |
| Context integrity | Unique IDs/metadata, acyclic same-type supersession, BOM, full bodies, bounded sources, every-mode failure, no partial output | Native Python 3.9 runtime checked by configured CI, not measured locally |
| Envelope gates | Closed dialect, path/scope semantics, paired task/result validation, independent byte cap and optional trusted token gate | Dispatcher leases, real tool enforcement and isolation not supplied |
| Adversarial coverage | 24 remote and 12 sensitive cases plus payload aliases, installer and context regressions in full validation | Ten-client inventory explicitly lacks live native execution/denial evidence |
| Context economics | Durable prefix, volatile suffix, compiled SessionStart, prefix hash/version, unmeasured-token fields | Provider tokens/cache savings require actual sanitized usage records |
| Mirror generation | Check/write generator for all tracked canonical workflow/skill mirrors | Cline rule slimming requires live read-order evidence |
| Task transactions | Existing future design retained | Supervisor-owned ledger/launcher is a multi-week platform implementation |

Run `python scripts/check-template.py` for the integrated structural/regression
gate. Inspect current advisory controls with `scripts/boundary.py inspect --json`.
`contained-local` and `release` deliberately fail verification rather than
claiming protection from worker-writable hooks. Ordinary accidental pushes are
blocked locally; no external network or protected-input isolation is established.

No dependencies were installed, no project was published, and no remote was
added. Canonical adapters stay tracked for fresh clones. Startup ceilings remain
9,500 aggregate characters with an 8,500 advisory target. Token estimates are
heuristic; no provider savings or native client behavior are fabricated.

## Verification evidence

- Full template gate passed: 160 required files, 10 adapters, 17 context budgets.
- Context integrity: 15 cases, including all client renderers and stable prefixes.
- Advisory guard corpus: 24 remote, 12 sensitive cases and payload aliases.
- Contract dialect/path/pairing/telemetry and schema-valid UTF-8 byte overflow pass.
- Push installer: 11 checks on Windows, including linked worktrees, preserved
  conflicts, nested-project rejection and actual Git-provided sh runtime denial
  with clean, agent-marker and override environments. No Git push was executed.
  POSIX executable-mode repair is conditional in CI and was not verified locally.
- Fresh-project creation, full target validation, init and zero remotes pass.
  Upgrade passes while preserving domain bytes; unknown hooks are preserved and
  CLI failure includes the conflict diagnostic. All fixture projects were local
  temporary directories, with no external network destination.
- Adapter missing/drift/regeneration/idempotence fixtures pass. Boundary schema
  and ten-client inventory pass; unsupported profiles return failure.
- Python 3.9 grammar passes for 25 changed Python files; actual local runtime is
  newer. Configured CI covers Windows/Linux and Python 3.9/current.
- Separate-context review was unavailable in the local environment. Manual integration review and mechanical checks completed; no
  independent-review acceptance is claimed.

## Portable audit provenance

Historical commit IDs identify the local audit snapshot; unpublished operational
history is not part of public release ancestry. `baseline-ctx.txt` preserves the
reviewed compiler source so `verify-proposal.py` can reproduce the exact frozen
patch without fetching that local history. The original results remain historical
observations; current production regressions live in `scripts/verify-*.py`.
