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
| Codex native sensitive-apply_patch guard | 0.167.0 | Passed scoped Windows stdio trial after command repair | PreToolUse status `blocked`, specific policy reason and absent inert file; per-thread runtime trust bypass |
| Codex automatic startup context | 0.167.0 | Passed 11 controls each at startup/resume/compact and 13 each for API clear/fork | Newly persisted named records and next action arrived through SessionStart; no manual fact packet, model tools, reroute or global change |
| Codex automatic pre-turn compaction | 0.167.0 | Passed 16 controls under a reduced invocation/thread threshold | New required body created after seed turn; automatic compaction, fresh callback and exact read-back observed in order; no manual compact RPC |
| Codex native model transition | 0.167.0 | Passed 13 assertions, gpt-6-astra to gpt-6.1-sol at xhigh | Same persisted thread; native switch warning and reported target model; exact facts/tasks/qualifier recovered without tools or reroute |
| Codex hash trust and native tool controls | 0.167.0 | Hash-trusted denial, safe patch/logger and Bash sensitive-write controls passed | Hash state and approved persisted CLI trust, no bypass; changed definition reports modified; native patch/logger/Bash controls passed |
| Gemini CLI | 0.52.0 | Version only; no model probe | Renderer fixtures do not establish native consumption |
| Codex app / Antigravity / IDE lifecycle | TBD | Unverified; Antigravity UI inspection was inconclusive | Window geometry/capture binding failed; CLI observations cannot certify these orchestration modes |

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

The earlier Codex CLI hook attempts remain **unverified**. Two bounded probes used the
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

### Codex Windows hook follow-up - 2026-11-06

The stdio follow-up separated discovery, trust and execution. Four enabled
project handlers were discovered as untrusted; all sources and copied scripts
were checked against the shipped fixture. Unrelated user MCP/plugin settings
were replaced only in the probe process after one configuration-parse failure.

| Observation | Native evidence | Outcome |
|---|---|---|
| Process-level trust-bypass flag alone | No hook event; completed fileChange and retained inert file | Failed activation baseline |
| Explicit per-thread runtime trust bypass, original Windows commands | PreToolUse `failed`, `hook exited with code 1`; completed fileChange and retained inert payload | Failed command baseline |
| Same runtime override, repaired Windows command bodies | PreToolUse `blocked` with the exact sensitive-path policy reason; inert file absent; turn completed | Passed sensitive-apply_patch route |

For this installed version only, the second and third trials used
`thread/start` with `config: {"bypass_hook_trust": true}` after vetting every
discovered source. The process flag alone did not establish execution in the
tested thread. This runtime override is a scoped probe input, not a persisted
trust decision or a portable recommendation for other versions.

The original nested PowerShell wrapper expanded `$root` before the inner command
received it. Local execution reproduced four failures. Removing that wrapper
and anchoring Git to the physical process directory also handles Windows
PowerShell's bracket-path provider-location mismatch. Four configured-command
cases now pass for benign calls, sensitive/publishing denials and logger output
from root/config/nested directories in paths with spaces and brackets.

Candidate source: `a98a7ab354a4abdb01a11599ccdcde075aee5b96`.
Hook configuration SHA-256:
`268dd76b65a0a3d11829092fc974c9a8e4d0064f886a23c556f48eeec8b47107`.
Eight private reconciliation assertions retain both failed baselines and the
repaired native result. The model remained `gpt-6-astra` with requested `xhigh`.
No model calls were repeated to recheck saved evidence. The example remains
inactive. Those initial trials did not certify interactive trust, native
shell/logger routes or desktop/cloud orchestration; later checks follow below.
Hook failures allowed these synthetic writes;
an error must never be treated as a successful policy denial.

### Native model transition and hash-trust follow-up - 2026-11-06

The next authorized follow-up intentionally selected two catalogued models for
one synthetic transition. This was a model-switch test, not a fallback after a
failed request. Both models advertised xhigh support. A gpt-6-astra seed turn
completed; a new process resumed the exact thread with gpt-6.1-sol and xhigh.
The native response reported the target model and emitted a model-switch warning.
All 13 checks passed: same thread, reported transition, conversation marker, full
required decision, exact next action, every open task, example qualifier, no
invented acceptance/compaction, no tools, no reroute, completed target turn and
unchanged global-config fingerprint. No tools were used to reconstruct recall.
This establishes one pair and direction only; other transitions remain untested.

A separate trial supplied vetted hashes through one per-invocation hooks.state
TOML table. Four discovered handlers became trusted, including in the loaded
thread. Native PreToolUse blocked the inert patch without a trust-bypass flag or
runtime bypass override. Modifying one command changed its hash and produced
trustStatus modified; the other three stayed trusted. The first harness expected
untrusted instead of the installed schema's modified enum, so its failed report
is retained. Offline reconciliation corrected the enum assertion against captured
native metadata; it did not repeat a model call or erase that failed assertion.
An earlier dotted-key override was also retained as a failed setup: the CLI
warned that the path-like key was unrecognized. Passing the complete state table
was recognized. Do not interpret an ignored setting as an approved hook.

Two further native controls passed with the same scoped hash state: a safe patch
created its exact inert line and completed PostToolUse logging at the project
root; a shell write selected the Bash matcher branch and was denied by the
sensitive-path guard. No publishing operation was attempted. The native logger
contained metadata for the allowed patch, not file contents.

The standard CLI startup review and hook browser were observed through a PTY:
three PreToolUse handlers and one PostToolUse handler were installed, zero were
active and all four required review without the invocation's hash pins. After
explicit human approval, the native Trust all action persisted exactly four
trusted_hash records for this fixture and the browser showed all four active.
Before/after checks confirmed every other semantic user-config value unchanged.
The initial PowerShell-based launcher had stripped quoted TOML arguments; its
failed setup was replaced by structured subprocess argv before UI inspection.

A fresh app-server process then discovered four trusted handlers with no hash
state override and no trust-bypass flag or runtime override. All nine controls
passed, including the loaded thread's trust state, native PreToolUse blocked
reason, absent inert file, completed turn and no additional config change.
This verifies the normal persisted CLI trust route for this fixture only; it
does not activate hooks in another project or certify desktop/IDE orchestration.

Source revision: `55d35c3f5802dd2b3f732e62ca96b6b76f83977a`. Raw logs and failed baselines remain private;
only sanitized assertions enter this report. Global model/effort and PATH were
not changed. These observations do not certify desktop/cloud orchestration,
other tool/model routes, external containment or provider token savings.

### Automatic Codex startup delivery - 2026-11-06

Baseline regressions exposed two implementation gaps: the shared helper ignored
--client and always rendered Claude context, and the inactive Codex example had
no SessionStart mapping. Client-aware rendering and client-specific diagnostics
now preserve explicit Claude behavior; unknown clients use generic notes.
The Codex example adds synchronous startup/resume/clear/compact/fork mapping,
explicit Git-root selection and additionalContextLimit 0 for the already-capped
payload (6,000 projection characters; at most 8,000 with notes). This delivers
full bounded text instead of a spill preview. Existing guards are unchanged.

The native 0.167.0 trial copied the exact candidate into a synthetic Git project
with spaces and brackets and started from a nested asset directory. Each phase
introduced a new immutable required decision, unique marker and changed next
action after the previous phase. Questions named the record ID but contained
none of its body or marker. The observed SessionStart output and model answer
both contained the full current body. All 11 controls passed independently at
startup, same-thread fresh-process resume and after a completed native
contextCompaction item. Model tool use, reroutes, invented acceptance and an
invented complete task ledger were rejected. The model/effort stayed at the
configured gpt-6-astra/xhigh. Native clear/fork delivery remains untested.

Only per-invocation trust was used for the five handlers in this new fixture.
The four previously approved persisted fixture trust records and all user
configuration bytes remained unchanged. No real-project Codex hook file was
activated. This restores last-persisted project facts; it does not save an
unwritten conversation or inject the complete open-task ledger.

Candidate source: `7fc3a1d9f50695b751498de354f2b95e4c71ac85`. Captured Windows
artifact bytes match the Git source after line-ending normalization. Callback
hashes and three exact read-backs were reconciled privately without repeating
model calls. The baseline failures remain recorded. Local gates passed:
21 continuity cases, five configured Windows cases, legacy hook fixtures,
full 189-file validation, Python 3.9 syntax and fresh-project/upgrade-surface
smoke. The isolated critic accepted with all 327 frozen file hashes unchanged.
These observations establish one Windows stdio/model/effort route, not desktop
or cloud orchestration.

### Codex API clear/fork follow-up - 2026-11-06

The installed 0.167.0 schema supports thread/start sessionStartSource clear and
thread/fork. A fresh synthetic project used the exact inactive example and
canonical helper from source `5673283a40bb824ec3ad7d21115eac73b8b493f3`, with
spaces/brackets in its path and a nested process directory. The first request
explicitly selected clear. After that turn completed, a new required record and
next action were persisted before forking the synthetic parent. The response
reported a distinct child ID and the expected forkedFromId.

Each boundary produced a completed native SessionStart callback containing the
new full body and an exact model read-back; 13 controls per phase passed. Prompts
named the required record but supplied neither its body nor unique marker.
The model used no tools, reroute, invented acceptance or complete-ledger claim.
Configured gpt-6-astra/xhigh, all global config bytes and the four previously
approved fixture trust records were preserved. Trust for the five copied
handlers was invocation-only. No implementation repair or real-project
activation was necessary.

Saved requests, responses and events were reconciled without another model
call: two callbacks, two distinct exact bodies, the explicit clear request and
fork lineage. Candidate bytes match the recorded Git source after line-ending
normalization. This closes the API clear/fork delivery gap on this single
Windows stdio route. It does not establish interactive /clear, IDE reset,
automatic compaction, other providers or external containment.

First-party references: [hook lifecycle sources](https://learn.chatgpt.com/docs/hooks)
and [app-server fork semantics](https://learn.chatgpt.com/docs/app-server).
Installed schemas and actual events establish the tested version's behavior;
the docs alone are not the acceptance evidence.

### Automatic pre-turn compaction follow-up - 2026-11-06

The exact candidate from source `3f235d3e150bd5560a335350fd8cc200f7496386`
was exercised on the earlier synthetic fork, using the same nested Windows path
and configured gpt-6-astra/xhigh. model_auto_compact_token_limit was reduced to
1 only for the new process/thread. No thread/compact/start request was sent.
This forces a small automatic-compaction trial without filling a real session
or changing the user's default threshold.

Preflight of the prior native trace refuted an immediate-callback assumption:
resume SessionStart runs after turn/start. A short seed turn therefore confirmed
the previous persisted body before a new immutable required decision and next
action were written. The second prompt named that record but supplied none of
its body or marker. The new body was absent from the seed events and every
outbound request, preventing prior injection from satisfying the fresh-data check.

All 16 controls passed. In the target turn, compaction started at event index 2,
completed at 5, the fresh SessionStart callback completed at 7, and the exact
model answer completed at 101. Both the required body and next action matched.
The example remained an example, acceptance and ledger completeness were not
invented, and there were no model tools or reroutes. The seed and target each
had one completed automatic contextCompaction item. All global config bytes and
four approved trust entries were preserved; the five fixture handlers used
invocation-only hash trust. No implementation repair or project activation
was needed.

Replay reconciled the saved event lists as ordered subsequences of the raw
native stream, the three captured requests, exact model answer and three
candidate/source artifacts after line-ending normalization. No model call was
repeated during reconciliation. This establishes reduced-threshold automatic
pre-turn delivery on one Windows stdio route. Default thresholds, mid-turn tool
continuation, IDE/desktop/cloud, autosave and complete task-ledger delivery
remain unverified.

References: [automatic-compaction configuration](https://learn.chatgpt.com/docs/config-file/config-reference)
and [SessionStart compaction lifecycle](https://learn.chatgpt.com/docs/hooks).
Native captures establish this scoped result; documentation alone does not.

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

- Other model transitions, remaining tool routes and app/IDE orchestration
  remain unverified. Normal persisted CLI trust was verified after explicit
  approval for four fixture records; other user-config values were preserved. Actual restart/compaction now have bounded
  Claude CLI and Codex stdio evidence. Sensitive writes now have scoped Claude
  Write and Codex apply_patch/Bash sensitive-write evidence; the allowed Codex
  patch logger was also observed. MCP and native publishing-denial routes remain open.
  Automatic startup delivery now has bounded Claude CLI and Codex stdio
  startup/resume/compact evidence, with the API clear/fork follow-up above.
  Reduced-threshold automatic pre-turn delivery is observed above. Interactive
  reset, mid-turn tool continuation and other lifecycle surfaces remain unverified.
  Manual recovery remains the portable fallback; listing open tasks is still
  required because the startup projection does not include the complete ledger.
- Antigravity UI journal inspection was attempted read-only. The driver reported
  unavailable input geometry, then screenshot and accessibility identified
  different windows. No journal assertion, reload or native hook-consumption
  success is inferred. A later read-only attempt restored the minimized app
  and initially matched screenshot/accessibility. An off-screen journal action
  was rejected; the next screenshot showed the desktop instead. Further input
  stopped. This is not native hook-consumption evidence; recover consistent
  targeting before additional app actions.
- Use the approved isolated Codex 0.167.0 executable explicitly for these probes;
  the main 0.142.0 installation remains unchanged. The separate synthetic model
  transition above was intentional; global upgrades/default changes and silent
  model substitutions were not performed. Re-check actual capability.
- No matched baseline/candidate provider benchmark was run. Static character
  reduction is not token/cache savings. For efficiency adoption, retain the
  existing >=10% measured total-token policy without correctness/privacy regressions.
  Begin an authorized pilot with five task types and three paired runs per type,
  alternating order and separating cold/warm cache/model/effort conditions.
- Reliability fixes stand on deterministic evidence even when savings are
  unmeasured. None of these observations authorizes deployment or more concurrency.
