# Recovery evidence and native pilot

Verification date: 2026-11-06. The following evidence levels are deliberately
separate. No test establishes universal model reliability or a token-saving claim.

## Deterministic recovery gate

Run `python scripts/verify-recovery.py`. The portable scenario inventory is
`benchmarks/context/recovery-scenarios.json`. Eight integration cases cover:
fresh-process recovery of required decisions, example qualifiers, the exact next
step and all open tasks; five repeated projection/ledger process cycles; Codex,
Claude and Gemini renderer switching; interrupted review/dependency gating;
superseded required decisions; corrupted receipts; and missing receipts/results.
The phase 7 trace additionally links feedback source, exact decision input and
separately observed worker/parent checks to the accepted artifact digest while
preserving the example category.

These tests use disposable Git projects and synthetic facts. They exercise real
file parsing, private receipts, task transitions and separate Python processes.
They do not run a native model or simulate its reasoning/compaction behavior.
Individual corruption/race/ownership/budget cases remain in the focused suites.

## Observed workstation probes

Windows, existing subscription authentication, no API-key environment, installs,
global settings edits or quota pacing. Raw inputs/outputs stay outside Git; the
fixture contains only synthetic project facts. Authentication output was filtered
to method/status, never retained as public identity/credential material.

| Surface | Installed version | Observed result | Scope |
|---|---|---|---|
| Claude Code noninteractive CLI | 2.1.116 | Passed all six supplied-packet checks | One fresh process reconstructed required decision, qualifier, next step, both open task states and the absence of acceptance/compaction evidence |
| Claude Code project SessionStart hook | 2.1.116 | Passed six startup checks | Hook lifecycle events contained a unique synthetic marker; the model quoted that decision/next step with tools disabled and recognized the missing complete task ledger |
| Codex noninteractive CLI | 0.142.0 | Failed before a valid recovery answer | Isolated CLI default requested `gpt-5.5`; error markers included `model_not_found` and unsupported request |
| Codex with the existing configured model/effort repeated explicitly | 0.142.0 | Failed before a valid recovery answer | Requested `gpt-6-astra`/`xhigh`; markers included unknown model/unsupported request. No alternative model was substituted |
| Gemini CLI | 0.52.0 | Version only; no model probe | Renderer fixtures do not establish native consumption |
| Codex app / Antigravity / IDE lifecycle | TBD | Not probed | CLI observations cannot certify these orchestration modes |

Claude JSON reported model-usage keys `claude-haiku-4-5-20251001` and
`claude-sonnet-4-6`; these are observed usage labels, not an inferred worker split.
Codex returned no successful-model evidence. The supplied-packet probes used manually supplied
compiled context, task summaries and the local receipt. Their native hooks and
actual compaction were not exercised.

The separate Claude SessionStart probe copied the shipped hook/compiler and
SessionStart command into a disposable fixture. The question contained no decision
body or marker, and tools were disabled. `hook_started`/`hook_response` events and
the final model answer both carried the unique decision marker. It recovered the
next step and example qualifier, correctly reported that the projection lacks
the complete task ledger, and made no compaction claim. This verifies one CLI
startup route only. It does not update every future doctor's `native_delivery`
field or certify another process. Adapter denial capability entries remain
unchanged: startup delivery is not a denial/containment test.

The initial Codex probe ignored user configuration for isolation; the configured
retry preserved the existing model/effort as per-invocation arguments. No global
defaults changed. CLI defaults and a native app's selected model are distinct.
The failures are recorded as native availability gaps, not successful recovery.

## Repeatable manual pilot

1. Use a disposable project with a required decision, an explicitly labeled
   example, a next action and two open tasks, one dependent on parent acceptance.
   The `make_fixture` helper in `verify-recovery.py` provides these synthetic facts.
2. Compile with `ctx.py compile --for CLIENT --json`; require a valid bounded
   projection. List every page of `tasks.py list`; inspect `doctor --mode resume`
   using the matching private checkpoint. Save exact inputs privately.
3. Confirm the installed CLI's help/auth method without printing credentials.
   Use an existing authorized subscription only. Inspect current first-party
   documentation and installed flags: never copy a new flag into an old client
   without checking it. Do not change the user's model/effort or global settings.
4. Start a fresh, bounded, read-only process and manually supply the packet.
   Ask for the required decision and next action verbatim; all open task states;
   whether the example is a requirement; whether acceptance/compaction is proven.
   Six explicit assertions must pass. Capture failures as failures. Stop after
   a bounded capability diagnosis; never cycle through models until one works.
5. A separate opt-in native lifecycle trial must observe the installed surface's
   actual event, delivered context and subsequent recall. Test restart, real
   compaction and model switch separately. Do not infer them from step 4.

First-party references checked for the probe:
[Codex noninteractive mode](https://learn.chatgpt.com/docs/non-interactive-mode),
[Claude programmatic mode](https://code.claude.com/docs/en/headless).
Installed help confirmed the flags used. The private probes used ephemeral/no
session persistence, project-only configuration where supported and no MCP tools.
Claude bare mode was not used because documented bare mode excludes subscription
login. Documentation alone does not prove the installed client's behavior.

## Remaining gates

- Actual native compaction/restart and denial checks remain unverified. Startup
  delivery outside the single tested Claude CLI route is also unverified.
  Manual recovery remains the portable fallback; listing open tasks is still
  required because the startup projection does not include the complete ledger.
- Codex CLI needs a separately resolved client/model capability mismatch before
  claiming native supplied-packet recovery. No install or model change was made.
- No matched baseline/candidate provider benchmark was run. Static character
  reduction is not token/cache savings. For efficiency adoption, retain the
  existing >=10% measured total-token policy without correctness/privacy regressions.
  Begin an authorized pilot with five task types and three paired runs per type,
  alternating order and separating cold/warm cache/model/effort conditions.
- Reliability fixes stand on deterministic evidence even when savings are
  unmeasured. None of these observations authorizes deployment or more concurrency.
