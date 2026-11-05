# Context continuity and quota efficiency audit

Date: 2026-11-05. Baseline: local commit `88cb0b9`, template v1.2.1.
Scope: deep audit and implementation planning, prompted by a user-supplied
social-media article about Claude/Codex harnesses. No runtime fixes are included.

## Conclusion

Keep the existing template. It already has most of the useful *policies* in
the article: small startup context, portable memory, bounded review, verification,
local commits, conservative delegation and optional quota pacing. The highest
value improvement is making continuity observable and testable across those
components. Installing another complete framework would duplicate substantial
existing machinery before resolving these integration gaps.

Passing template validation does not establish that a native client loaded the
right state, preserved a new decision, or recovered every unfinished task. The
audit reproduced gaps in all three areas. Reliability should mean explicit
acceptance tests and visible degraded operation, not an unconditional promise
of perfect memory, exact quota savings, or unlimited autonomous sessions.

The phased proposal is in [implementation-plan.md](implementation-plan.md).

## Evidence and limits

| Check | Observed result |
|---|---|
| Working tree before audit | Clean; no configured Git remotes |
| `python scripts/check-template.py` | PASS; 167 required files, 10 adapters, 22 skills in three trees, 17 context budgets |
| FAST_INIT aggregate | 8,511 / 9,500 characters; 11 above the 8,500 advisory target |
| Compiled Codex projection | 1,381 characters; three typed records; no dropped records |
| Token counts | Character estimates only; no provider token/quota/cache measurements |
| Local executables | Codex CLI 0.142.0; Claude Code 2.1.116; Gemini CLI 0.52.0; Python 3.13.9 |
| Windows command discovery | Bare Claude/Gemini commands selected blocked PowerShell wrappers; their `.cmd` launchers returned versions without policy changes |
| Additional probes | Ten Boolean observations reproduced in temporary fixtures; see [results.json](results.json) |
| Native session behavior | Not exercised; installed version is not proof of app orchestration or hook delivery |

The current full gate includes context integrity, hook fixtures, adversarial
guard checks, envelope validation, pacing and upgrade regressions. This audit
does not replace those tests or assert a new hosted CI result. It examined the
startup/compiler/hook flow, memory workflows, task contracts, pacing design,
benchmark definitions, CI orchestration and relevant generator interfaces.
It was not a new line-by-line security audit of every upgrader or media tool.

Reproduce the additional observations with:

```powershell
python docs/audits/context-continuity-2026-11/probe.py
```

Exit zero means this audit probe executed, not that the observed weaknesses
are acceptable. It is deliberately outside the regression gate. Source hashes
in its output identify the inspected implementations. Fixtures are temporary,
synthetic and contain no user transcript. The pasted article and its author's
personal information are not copied into this repository. The original post
URL, first-comment prompt, author's harness code and measurement logs were not
provided; their empirical claims cannot be independently validated here.

## Findings

Priorities describe implementation order: P1 threatens reliable continuity;
P2 improves correctness/efficiency of the operating contract; P3 is optional
product/process work. They are not vulnerability severity ratings.

### F01 — P1: recording a decision does not ensure it will be restored

`scripts/hooks/session-context.py:20` directs decisions to `decisions.md` and
risks to `risks.md`. `workflows/update-memory-bank.md` and the memory maintainer
skill primarily direct writes to prose files. However, `scripts/ctx.py:99`
compiles typed records, and its status loader reads only four handoff fields.
The probe writes an explicit decision to `decisions.md`; it is absent from
the projection. Manual discovery can still recover it, but automatic restoration
does not establish coverage. Only three typed records currently exist.

Create one documented write path with stable IDs, source references, explicit
scope and inclusion receipts. Preserve qualifications and supersession. Distinguish
user decisions, examples, preferences, hypotheses and authorization; one must
not silently become another. A durable decision receipt should identify its
actual stored location and whether it is required in the current task packet.

### F02 — P1: the pre-compaction hook is a reminder, not a checkpoint

`scripts/hooks/session-context.py:93` emits `PreCompact.additionalContext`; it
does not write durable state. The probe confirms unchanged fixture files after
the hook runs. The current Claude reference lists context-injection events
without PreCompact and documents different compaction control semantics. Thus
delivery of this reminder, and an opportunity for the model to act on it before
compaction, are unproven. A matching JSON fixture cannot prove either behavior.
[Claude hook reference](https://code.claude.com/docs/en/hooks).

Persist at meaningful task transitions while context is available. Use a
compaction hook only for a verified mechanical checkpoint/receipt check and
bounded diagnostics. Test startup and recovery in the actual installed client.
Do not turn every automatic compaction into an indefinite blocking loop.

### F03 — P1: handoff validation permits silent loss of status

`scripts/ctx.py:86` accepts a missing handoff, a prose-only handoff, old dates
and unrelated branch metadata without reporting a continuity problem. A YAML
block scalar is accepted as the literal `|`, omitting its actual blocker text.
Only the documented minimal scalar subset is understood, but unsupported
structures are not rejected. The source-byte limit applied to records does
not apply to handoff; the probe accepts a handoff over 20,000 bytes.

Missing handoff can be legitimate on a fresh project; distinguish fresh startup
from resume. Require and validate task identity, revision, base state, evidence
pointers and next action when resuming. Check branch/worktree and dirty-state
changes without treating any age or new commit as automatic invalidation.
Use explicit schemas or reject unsupported syntax before projecting it.

### F04 — P1: one rolling handoff cannot inventory multiple workstreams

`workflows/handoff.md:23` explicitly says the recent task wins. Parent-only
Memory Bank writes protect one delegation tree, not two independently launched
lead sessions. There is no durable task/attempt ledger, atomic ownership claim
or restart reconciliation. The repository already acknowledges this in
`docs/subagent-contract.md:130` and `docs/local-agent-mail.md`.

Retain the tiny handoff as an index, with task-specific state behind it. Start
with one coordinator and a durable list of open work; add transactional claims
and a native dispatcher only when concurrent independent sessions are needed.
A mailbox is optional transport, not the authoritative task store.

### F05 — P1: startup has no verified health receipt

`scripts/hooks/session-context.py:94` catches every unexpected exception and
returns zero without output. A synthetic exception reproduces silent failure.
Normal malformed-record cases do produce diagnostics; the gap is unexpected
failure and proof of delivery. Codex/Gemini hook files are inactive examples;
only Claude has a wired lifecycle injection. Existing boundary inspection
describes safety controls, not successful continuity loading.

Add `ready / degraded / blocked` continuity status, with version, repository,
task, compiler hash and a bounded receipt. The manual path must remain usable.
Missing optional hooks should not stop ordinary work; missing essential task
constraints should stop dependent edits until recovered. Current OpenAI docs
also distinguish local command hooks from cloud orchestration, so local tools
alone do not imply a local hook runtime.
[OpenAI hooks](https://learn.chatgpt.com/docs/hooks).

### F06 — P2: the archive and the startup working set are conflated

`scripts/ctx.py:209` always keeps every active decision and risk. Fifty synthetic
decision records produce a 9,399-character projection against the 6,000 limit.
The CLI correctly rejects that projection; this is safe behavior, but it does
not scale to the article's hundreds of decisions. Increasing the cap just moves
the problem into every session.

Separate mandatory global constraints, task-required records and retrievable
history. Use explicit task links/tags and deterministic selection first; no
vector database is necessary. Never drop a required decision to obtain a pass.
Return included/omitted IDs and reasons. Over-budget mandatory context must
produce a visible recovery action, not partial success.

### F07 — P2: file-size checks do not measure actual startup overhead

`benchmarks/context/scenarios.json` names static file sets. These do not include
all injected hook bytes, global rules, skill catalogs, plugin schemas or repeated
tool reads. The 8,511-character count is useful for regression control but is
not the observed token cost of this session. The compiler's own token estimate
correctly says it is unmeasured. Active context/progress also retain substantial
historical narrative that can make broad reads expensive.

Maintain the file budget; measure actual supported-client startup and recovery
separately. Archive completed narrative behind an index. Optimize total cost
per accepted task, including reviews, repairs and restore reads.

### F08 — P2: older guidance contradicts newer implementation

- `docs/context-hygiene.md:85` asserts a universal five-minute cache lifetime;
  `memory-bank/model-routing.md` explicitly warns against universal lifetimes.
- The same hygiene guide generalizes cache savings and eager loading of every
  MCP schema; client/tool discovery behavior must be established per surface.
- `docs/context-compiler.md:37` says bodies are capped at 400 characters; the
  implementation retains complete normalized bodies. Its early diagram places
  status first, whereas implementation and later documentation put it last.
- `docs/context-memory-bridges.md:33` conflates filesystem survival, discovery,
  cross-machine transport and Git tracking. An uncommitted or ignored file can
  persist and be readable by another local client; a commit alone does not
  transfer it to another computer. Never infer publication permission from
  continuity requirements.

Resolve the documentation contradictions without adding more root rules.
Provider caching has model-specific retention and eligibility; API caching
documentation does not establish subscription quota savings.
[OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).

### F09 — P2: CI repeats the expensive full gate

`.github/workflows/validate.yml:27` runs full validation, followed by `--compat`.
In `scripts/check-template.py:1028`, `compat_mode` changes the success label but
does not narrow the non-fast checks. Both calls therefore run the full suite,
including hardening, pacing and upgrade checks. The benchmark self-test is also
run inside each full gate and explicitly afterwards.

Preserve coverage while scheduling expensive suites once per matrix job. Keep
a compatibility entry point for targeted use, or remove its duplicate CI step
until its scope is intentionally split. This reduces deterministic compute and
waiting; no provider-token saving has been measured.

### F10 — P2: quota advice is not a per-task spending boundary

The pacing implementation already provides explicit activation, stale-data
checks, multi-window limits, reserves, WIP control and completion-package
estimates. It is intentionally OFF by default. Its database and manual board
do not measure all agent actions or stop native processes. Codex/Google sources
are manual fallbacks; no live quota experiment was performed.

Add ordinary-task checkpoints and optional measured cost reporting without
activating quota maximization. Keep context occupancy, token use, account quota
and monetary cost separate. Claude documents rate-limit and model fields in
statusline data, but availability depends on version/account; estimated session
dollars need not match the bill. Installed-version detection must precede relying
on any new field. [Claude statusline](https://code.claude.com/docs/en/statusline).

### F11 — P2: completion evidence needs an explicit target environment

The template has success checks and independent review policy, but no shared
completion-level schema. `docs/deployment.md` is a placeholder, appropriate for
a generic template. The article's production-only definition conflicts with
local-only tasks, audits and this repository's current publication boundary.

Use separate implementation, verification, acceptance and deployment fields.
For an application, define relevant UI/API/MCP paths, environment and rollback.
For this task, completion means a reviewed audit/plan with evidence, not a
production deployment. Deployment authority is never implied by a done label.

### F12 — P3: feedback closure and cross-session attribution are incomplete

Phase summaries and refuted hypotheses exist, but there is no dedicated linkage
from feedback to decision, task, acceptance evidence and closure. The passive
write logger stores tool/path/action metadata without session identity; it
cannot reconstruct a conversation's decisions or distinguish concurrent writers.
Retrospective actions therefore depend on manual prose discipline.

Add a small feedback/action register and optional local correlation IDs. A write
log remains observability, not product memory. Keep raw user feedback, personal
details and account/permission receipts out of this public-history repository.

## What to take from the article

| Proposal | Disposition for this template |
|---|---|
| Shared durable context | Keep; close the write-to-restore gap |
| Exact feedback and qualifications | Adopt with private source storage, typed interpretation and reviewed exports |
| Product vision | Expand existing productContext with success/non-goals/approved examples; lazy-load |
| One startup page | Adopt as a bounded task projection; preserve canonical root instructions |
| Per-task budgets | Adapt to observed metrics and explicit limits; unknown stays unknown |
| Handoff before 80% | Use as a heuristic only; checkpoint at milestones even without occupancy telemetry |
| Different-model review | Use selectively; separate context and evidence matter more than brand |
| Maximum two review rounds | Already present; enforce through task status and evidence |
| Evidence before declaring failure | Already present; link failed hypotheses to the task |
| Done means production | Replace with task-specific acceptance/environment fields |
| Retrospective starts with old actions | Adopt; close prior actions before proposing more rules |
| Reuse existing solutions first | Already present; apply to this harness improvement too |
| Multiple orchestrators | Defer; one lead/two open tasks remains the default |
| Autonomous deployment after approval | Project-specific opt-in; no change to local-only template policy |
| Design references and standards | Optional application workflow, with approved examples and visual checks |
| External test server | Defer until resource measurements justify it and data boundaries are defined |
| Separate product/development quotas | Document for deployed applications; keep distinct account/pool identities |
| Harness health check | Adopt with explicit degraded recovery instead of unconditional global shutdown |
| Fixed model hierarchy and subscription names | Do not copy; verify exact client/model/entitlement per task |
| Every failure becomes another permanent rule | Replace with regression evidence and periodic removal of obsolete rules |

The author's 17 compactions, 75% overnight usage, 93-98% cache reuse, 40x model
comparison and output-volume improvements are anecdotes without supplied logs
or controlled baselines. They motivate tests; they are not predicted outcomes
for this repository. Continued reasoning quality also depends on task framing,
tools, model capability and external-system behavior.

The inspected [gstack upstream](https://github.com/garrytan/gstack) supplies
product-framing and review workflows, with different host support levels. Borrow
the narrow practice of clarifying outcomes and comparing implementation options.
Do not install its full skill set or shipping automation for this audit.

## Delivery boundary

This work creates an audit, a phased plan, reproducible observations and concise
operational memory. Runtime scripts, hooks, client configuration and quota
activation are unchanged. No model benchmark, dependency installation, remote
publication or deployment is implied. The remaining native checks are explicit
work items, not fabricated passes.
