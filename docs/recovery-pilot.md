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

Windows, existing subscription authentication, no API-key environment or quota
pacing. Initial probes used installed clients; the later Codex 0.167.0 trial used
a separately approved isolated installation with primary install/PATH/global
settings preserved. Raw inputs/outputs stay outside Git; the
fixture contains only synthetic project facts. Authentication output was filtered
to method/status, never retained as public identity/credential material.

| Surface | Installed version | Observed result | Scope |
|---|---|---|---|
| Claude Code noninteractive CLI | 2.1.116 | Passed all six supplied-packet checks | One fresh process reconstructed required decision, qualifier, next step, both open task states and the absence of acceptance/compaction evidence |
| Claude Code project SessionStart hook | 2.1.116 | Passed six startup checks | Hook lifecycle events contained a unique synthetic marker; the model quoted that decision/next step with tools disabled and recognized the missing complete task ledger |
| Codex noninteractive CLI | 0.142.0 | Failed before a valid recovery answer | Isolated CLI default requested `gpt-5.5`; error markers included `model_not_found` and unsupported request |
| Codex with the existing configured model/effort repeated explicitly | 0.142.0 | Failed before a valid recovery answer | Requested `gpt-6-astra`/`xhigh`; markers included unknown model/unsupported request. No alternative model was substituted |
| Codex isolated CLI with the same model/effort | 0.167.0 | Passed all six supplied-packet checks | Human-approved isolated release; primary installation/PATH/defaults preserved |
| Codex stdio app-server, fresh process and manual compaction | 0.167.0 | Passed six recall checks after restart and six after compaction | Same native thread; completed `contextCompaction` item observed; reported model `gpt-6-astra` |
| Claude CLI fresh process and manual compaction | 2.1.116 | Native boundaries observed; initial recall 6/7, targeted full-body follow-up 7/7 | Original omitted marker sentence is retained as a failed exact-fidelity assertion |
| Claude native sensitive-Write guard | 2.1.116 | Passed three assertions | Actual Write request, native hook denial and absent inert fixture file |
| Gemini CLI | 0.52.0 | Version only; no model probe | Renderer fixtures do not establish native consumption |
| Codex app / Antigravity / IDE lifecycle | TBD | Not probed | CLI observations cannot certify these orchestration modes |

Claude JSON reported model-usage keys `claude-haiku-4-5-20251001` and
`claude-sonnet-4-6`; these are observed usage labels, not an inferred worker split.
The original Codex 0.142.0 probes returned no successful-model evidence. The supplied-packet probes used manually supplied
compiled context, task summaries and the local receipt. Their native hooks and
actual compaction were not exercised.

The separate Claude SessionStart probe copied the shipped hook/compiler and
SessionStart command into a disposable fixture. The question contained no decision
body or marker, and tools were disabled. `hook_started`/`hook_response` events and
the final model answer both carried the unique decision marker. It recovered the
next step and example qualifier, correctly reported that the projection lacks
the complete task ledger, and made no compaction claim. This verifies one CLI
startup route only. It does not update every future doctor's `native_delivery`
field or certify another process. Adapter capability entries now record the
separately observed native routes below. Startup
delivery is not a denial/containment test.

The initial Codex probe ignored user configuration for isolation; the configured
retry preserved the existing model/effort as per-invocation arguments. No global
defaults changed. CLI defaults and a native app's selected model are distinct.
The failures are recorded as native availability gaps, not successful recovery.

## Native follow-up: restart, compaction and denial

The original source basis was template commit `8a57d19`; the Codex 0.167.0
follow-up used `72846dd` after a record-metadata whitespace correction. These are
development-workstation observations, not certifications of copies or later runs.

Claude retained a conversation-only random marker and the complete two-task
board across an actual process exit and explicit `--resume`. The marker/board
were supplied only in the first turn; they were not stored in project records
or repeated in recall questions. Project decisions/next action were re-delivered
through the shipped SessionStart hook. A real `/compact` emitted `compact_boundary`
and hook events; post-compaction recall preserved the conversation marker, next
action, task states, example qualifier and absence of parent acceptance.

Both initial recall questions returned the main decision sentence but omitted
its second marker sentence: six of seven checks passed, so those strict runs
remain failed. One focused follow-up requested the **complete raw body, every
sentence including markers**, without supplying the answer. All seven checks
then passed after the observed compaction. This demonstrates recoverability with
an explicit source-read-back request, not automatic exact quotation. Never relax
an equality check to erase the initial omission.

The Claude denial probe allowed only the Write tool in a disposable fixture.
It attempted one write of inert `{"fixture":true}` to `guard-fixture/token.json`;
the native hook emitted a deny decision and the file remained absent. This
does not test real credentials, remote publishing, all tool paths or containment.

Codex 0.142.0's catalog contained only older model entries and lacked the selected
model. Official [model guidance](https://learn.chatgpt.com/docs/models) records
GPT-5.5's retirement from ChatGPT-authenticated Codex on 2026-10-14. No model
request was repeated until capability changed. The human approved an isolated
official 0.167.0 Windows x64 release; its 206,477,744-byte archive matched published
SHA-256 `94b51ca84648a6923784ef71f06e2feb1e10796ddb3f5d033ccb0fbe8daa2f16`.
No global install/PATH/model change was made. The main PATH CLI remains0.142.0.

The isolated catalog includes `gpt-6-astra`, but a catalog is not entitlement
proof. A completed CLI turn using that model and the existing `xhigh` effort
passed all six supplied-packet checks. A separate stdio app-server trial started
a thread, stored a conversation-only marker and packet, ended the process,
resumed that exact thread in a new process, and passed all six recall checks.
`thread/compact/start` completed a native `contextCompaction` item; a subsequent
turn passed the same six checks. The reported model was `gpt-6-astra`; model and
effort were preserved. No goal, native dispatcher or quota-pacing plan was created.
See the [app-server protocol](https://learn.chatgpt.com/docs/app-server).

Adapter metadata now records dated **partial** checks, source revisions and
remaining gaps for Claude/Codex. Offline validation checks declaration structure;
`boundary.py` still reports `tool_events_verified: false` for the current process.
Historical observations cannot authenticate or certify a new runtime.

The Codex hook attempt remains **unverified**. Two bounded CLI probes used the
vetted shipped example with per-invocation hook-trust bypass in disposable
fixtures (first read-only, then workspace-write). Files remained absent, but the
exec JSON stream did not expose the specific native policy reason needed by the
probe. Startup trust-bypass warnings are not PreToolUse-consumption evidence.
No guard pass or guard defect is inferred from an absent file or model prose.
Normal interactive hook review/trust was not tested; no persistent trust entry
or real-project hook configuration was changed. Stop rather than retrying the
same observability gap. The hook JSON's `commandWindows` key was separately
checked against the official current
[config schema](https://developers.openai.com/codex/config-schema.json); that is
structural evidence.

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
   Specify a string containing the complete record body, every sentence/marker;
   separate semantic recall from exact source fidelity.
   Six explicit assertions must pass. Capture failures as failures. Stop after
   a bounded capability diagnosis; never cycle through models until one works.
5. A separate opt-in native lifecycle trial must observe the installed surface's
   actual event, delivered context and subsequent recall. Test restart, real
   compaction and model switch separately. Do not infer them from step 4.

First-party references checked for the probe:
[Codex noninteractive mode](https://learn.chatgpt.com/docs/non-interactive-mode),
[Claude programmatic mode](https://code.claude.com/docs/en/headless).
Installed help confirmed the flags used. Supplied-packet probes used ephemeral/no
session persistence, project-only configuration where supported and no MCP tools.
Lifecycle trials deliberately persisted their own synthetic native sessions/threads
to test explicit resume in a new process and actual manual compaction. They did
not resume unrelated user sessions or change global configuration.
Claude bare mode was not used because documented bare mode excludes subscription
login. Documentation alone does not prove the installed client's behavior.

## Remaining gates

- Native model switching, interactive hook trust, other tool routes and app/IDE
  orchestration remain unverified. Actual restart/compaction now have bounded
  Claude CLI and Codex stdio evidence; the sensitive-Write denial is Claude-only.
  Startup delivery outside the single tested Claude CLI route is unverified.
  Manual recovery remains the portable fallback; listing open tasks is still
  required because the startup projection does not include the complete ledger.
- Use the approved isolated Codex 0.167.0 executable explicitly for these probes;
  the main 0.142.0 installation remains unchanged. Global upgrades and model
  substitutions were not authorized or performed. Re-check actual capability.
- No matched baseline/candidate provider benchmark was run. Static character
  reduction is not token/cache savings. For efficiency adoption, retain the
  existing >=10% measured total-token policy without correctness/privacy regressions.
  Begin an authorized pilot with five task types and three paired runs per type,
  alternating order and separating cold/warm cache/model/effort conditions.
- Reliability fixes stand on deterministic evidence even when savings are
  unmeasured. None of these observations authorizes deployment or more concurrency.
