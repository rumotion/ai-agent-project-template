# Active Context

## Phase summary: Production-readiness simulation Stage 2 (Codex) - 2026-11-09

- Status: Production upgrade & EGM drift simulation verified. Cleanup remains blocked by tool policy; this is not an unconditional completion sign-off.
- Reconciliation: No Git remotes; tracked worktree initially clean at `7af6c6d`. Legacy continuity doctor reported `degraded` (no validated resume receipt); task list was empty with no further pages.
- Peanuts review: `scripts/README.md` accepted under `docs/reviewer-role.md` and `.codex/agents/reviewer.toml`; Paraphrase-First completed, all five required sections checked against source, no findings. The documented fixture link resolves.
- Preservation: Compared current SHA-256 hashes with `pre-upgrade-hashes.json`. All five requested custom files (`README.md`, `src/auth/README.md`, `config/app-settings.json`, `memory-bank/projectbrief.md`, `AGENTS.md`) are byte-identical. The saved local-source report records 259 additions, two preserved files, and `AGENTS.md` as the sole preserved conflict. Seven of nine baseline files still match; auth/billing source differs after drift seeding. All three `./<subdir>/CONTEXT.md` links resolve; child contracts are leaves.
- Blind drift audit: Read four contracts sequentially and inspected source without running their Verification commands or changing fixtures. Missing Feature: `AuthService.rotate_token` is absent (`src/auth/service.py:35-90`). Logic Shortcut: `login` counts failures but never enforces lockout (`service.py:58-66`). Incomplete Model: `Invoice.due_date` is absent from both fields and `to_dict` (`src/billing/invoice.py:47-53,82-96`). Architectural Divergence: `finalize` invokes `_audit`, reading `LEDGER_AUDIT_LOG` and appending timestamped JSON to disk (`invoice.py:34-43,75`); this also violates `src/CONTEXT.md`. `src/api/CONTEXT.md`: `No drift detected.` Four distinct seeded discrepancies, five document-level findings; report emitted in chat first.
- Validation: Full `python scripts/check-template.py` passed (206 required files, 10 adapters, 24 skills across three trees); `python scripts/verify-upgrade.py` passed (23 tests, one skipped); `ctx.py compile --for gemini/claude/codex --check` and post-update `check-template.py --fast` passed. Root checks ran with the ignored simulation directories still present because cleanup was denied.
- Cleanup limitation: Both `.agent-logs/prod-sim-target` and `.agent-logs/prod-sim-backups` remain. Absolute paths were verified inside this workspace, with no reparse points. Automatic approval review rejected both the guarded deletion and explicit-literal-path retry as `blocked by policy`; no further deletion workaround attempted.
- Next: Remove the two simulation directories when policy permits. No source fixes, remote actions, dependency installs, or inline Python commands. Local-only; Pacing OFF.

## Phase summary: Production-readiness simulation Stage 1 (Claude) - 2026-11-09

- Outcome: The 4 prior reviewer findings are confirmed resolved. Three reviewer passes (`revise`, `revise`, `accept`) raised 14 new findings (4 medium, 10 low), all fixed in `scripts/README.md` and `workflows/drift-report.md` plus mirrors. Full record: `docs/audits/prod-readiness-2026-11/stage1-review.md`.
- Key corrections: eight `scripts/README.md` interface rows listed nonexistent flags/subcommands; the no-network invariant ignored the template `git fetch`; guard hooks exit `0` with a JSON deny payload, not `2`; `ctx.py record` does not update `00-index.md`; continuity/task/pacing state lives under the home directory, not `.agent-logs/`. `drift-report` now checks `Verification` commands statically and defines its default contract baseline.
- Upgrade simulation: `upgrade-target.py --apply-safe` on `.agent-logs/prod-sim-target` exited 2 with `AGENTS.md` the only conflict; 259 files added; all 9 custom files SHA-256 identical before and after (`.agent-logs/prod-sim-backups/pre-upgrade-hashes.json`).
- Refuted hypothesis: "commit `2d20606` leaves the three docs approvable" (reviewer returned `revise` on `scripts/README.md`).
- Verification: full `check-template.py` exit 0; `gen-adapters.py --check` passes.
- Next: Stage 2, Codex runs `workflows/drift-report.md` blind on `.agent-logs/prod-sim-target/src`. Seeded drifts are intentionally unrecorded. Local-only; Pacing OFF.

## Phase summary: Elephant-Goldfish Model (EGM) integration - 2026-11-09

- Outcome: Local adapters, mirrors, and deterministic checks pass for Gemini/Antigravity, Claude Code, and Codex; Cline mirrors also pass. These checks do not establish native runtime delivery.
- Key decisions: Adopted EGM mechanisms (`Peanuts & Hay` bottom-up module contracts, `Paraphrase-First` comprehension gate, `Zero-Decision Rule` for plans/specs, `Zoom-Out` mandatory codebase reuse search, `Contradiction Gate` in cognitive harness, `drift-report` workflow, and 24,000-byte skill body cap) natively into the template without external plugin dependencies. Source: `decision-egm-context-contracts`.
- Refuted hypotheses: Expanding `.agents/rules/30-cognitive-harness.md` with verbose prose would fit the 1,800-char budget (measured 1,820 chars; tightened to 1,731 chars).
- Files modified: `AGENTS.md`, `memory-bank/00-index.md`, `docs/peanuts-and-hay.md`, `docs/reviewer-role.md`, `docs/agent-skill-ecosystem.md`, `docs/agent-compatibility.md`, `workflows/critic-review.md`, `workflows/spec-driven-development.md`, `workflows/plan-task.md`, `workflows/bootstrap-context.md`, `workflows/drift-report.md`, `.agents/rules/30-cognitive-harness.md`, skill/workflow mirrors across `.agents/`, `.claude/`, `.cline/`, `.clinerules/`, `scripts/README.md`, `scripts/check-template.py`, `scripts/upgrade-target.py`, `scripts/verify-upgrade.py`.
- Verification (Gemini, Claude, Codex, 2026-11-09): Full `check-template.py` passed (206 files, 10 adapters, 24 skills across 3 trees); `verify-upgrade.py` passed (23 tests, 1 skipped); `gen-adapters.py --check` and `ctx.py compile --for gemini/claude/codex --check` passed.
- Review resolution: Resolved all four Claude `paraphrase:` / Zero-Decision doc findings in `docs/peanuts-and-hay.md` (`<target_filename>` link placeholders) and `workflows/drift-report.md` (bounded default + 10-doc scope gate, explicit `Interface`/`Invariants`/`Side Effects`/`Verification` drift category mapping, and read-only chat-first report output), and upgraded `scripts/README.md` from a partial catalog into a full `Peanuts` module contract (`Overview`, `Interface`, `Invariants`, `Side Effects`, `Verification`).
- Continuity: Legacy doctor returned the expected degraded status; task inventory was empty with no further pages. Handoff reconciled across Gemini, Claude, and Codex; private receipts stay outside the repository.
- Open items: Offline checks verify on-disk adapter/contract integrity; live runtime prompt delivery remains a separate observation class.
- Next: Ready for next user task; keep repository local-only. Pacing OFF.

## v1.3.1 publication complete - 2026-11-09

- Published `main` and annotated tag `v1.3.1` at `e5e0c17` and set `v1.3.1` as
  the Latest GitHub release (`docs/releases/v1.3.1.md`).
- Hosted CI run `42687265436` passed all four `ubuntu-24.04` and `windows-latest`
  (`py3.9` and `py3.x`) jobs.
- Repository description, README, SVG hero (`RELEASE 1.3.1`) and upgrade guides
  are live. Local push backstop and private archive refs remain intact. Pacing OFF.

## v1.3.1 hosted Windows path-alias fix - 2026-11-09

- Published `v1.3.0` at `772661d`. Hosted run `42685239684` passed both Ubuntu
  24.04 jobs (`py3.9`/`py3.x`) and exposed a Windows 8.3 short-path alias
  mismatch (`RUNNER~1` vs `runneradmin`) in `scripts/hooks/log-writes.py`.
- Added `resolve_path` in `scripts/hooks/log-writes.py` to resolve the deepest
  existing ancestor directory before `commonpath` checks, plus a Windows junction
  alias regression in `scripts/verify-antigravity-hooks.py`.
- Keep published tag `v1.3.0` unchanged; promoted `VERSION`, `CHANGELOG.md`,
  `README.md`, `assets/images/hero-template.svg` and `docs/releases/v1.3.1.md`
  to `1.3.1`. Full 193-file validation and security audit pass. Pacing OFF.

## v1.3.0 release preparation and security audit - 2026-11-09

- Promoted `VERSION` and `CHANGELOG.md` to `1.3.0`; added `docs/releases/v1.3.0.md`
  and refreshed `README.md`, `assets/images/hero-template.svg` and
  `docs/public-release-review.md`.
- Outgoing security audit covered all 333 tracked files, 30 outgoing commits
  since `v1.2.1` (`90509d9`) and 264+ outgoing Git blobs. Zero credentials,
  private keys, tokens, personal paths, local file URIs, non-noreply emails or
  Cyrillic strings found. All outgoing commits use `rumotion` GitHub no-reply.
- Full 193-file template validation, 10 adapters, 17 context budgets, 22 skills
  across 3 trees, and 15 hardening/recovery suites pass. Pacing remains OFF.

## Follow-up local closeout - 2026-11-07

- R1 policy integrated with native Flash writer/Argon advisor: six parent tests,
  stable 1.5.3 executable/hash/settings, advisor -> parent_review; no auto-accept.
- Thirty packet runs/15 pairs completed. Initial 24/30 exact matches and separate
  30/30 semantic state-label reconciliation retained. Native counter median was
  19.2% lower in fixtures; version/cache/quality limits keep adoption insufficient.
- New CLI process resumed an own conversation and read fresh exact file/action.
  No cold IDE/backend/default-threshold/standalone certification or fleet enabled.
- Bounded follow-up packages complete locally; unsupported/conditional extensions
  remain explicit in docs/continuity-followup-plan.md. No publication/pacing.

## R1 offline routing policy - 2026-11-07

- Added stdlib-only routing advice: mandatory material plan/completion review,
  repeated logic-error escalation, bounded transient retry and explicit holds.
- Receipts bind task revision/attempt/artifact/checkpoint and latest error event;
  old error advice cannot release a new failure or replace completion review.
- 24 targeted checks, full 193-file gate, fresh/preservation packaging and
  isolated review pass. No native dispatcher, permission grant or default change.

## Native IDE and CLI advisor pilot - 2026-11-07

- User granted fixture trust manually. Native IDE file-tool denial/audit and a
  distinct conversation's fresh full-body/example/next-action recovery passed.
  UI model: Gemini 4 Argon High; serving ID absent from trace. No cold-restart,
  terminal, compaction, standalone App or universal native claim.
- CLI 1.5.2 Flash Medium fixed one synthetic file; Argon High reviewed the frozen
  artifact with zero tools/writes. Six parent tests passed; settings unchanged.
  Scripted completion checkpoint only; no production router or savings claim.
- Reports: docs/recovery-pilot.md and docs/continuity-followup-plan.md. Raw own
  traces/setup corrections remain private; no household data used. Next: offline
  routing policy, then separately bounded native/paired trials. Pacing OFF.

## Native follow-up and adaptive routing - 2026-11-07

- App/Gemini fixture is open in installed Antigravity IDE; manual folder trust
  is pending. No native App success inferred; no security prompt bypassed.
- Official advisor/subagent/API research and a staged implementation proposal
  cover Claude, Codex, Gemini and Antigravity. Installed Claude 2.1.116 is older
  than documented Haiku 5.5 requirements; no update/default/service activation.
- Shared index saves 915 characters; Home FAST 8,367/9,500, all seven compiled
  results identical and other project files unchanged. Provider savings unknown.
- Plan: docs/continuity-followup-plan.md; architecture: docs/adaptive-model-routing.md.
  Native follow-ups/paired measurements remain open. Pacing OFF; local-only.
- Full 191-file gate, fresh/preservation packaging and isolated review passed;
  final acceptance updates only this operational note and progress summary.

## Late native/packaging repairs - 2026-11-07

- Native Antigravity CLI 1.1.8/Claude Sonnet exposed write_file/Path gaps; fixed
  mapping, denial and private audit metadata. Listing/text/PNG and sensitive
  denial now observed; App/Gemini/IDE remain unverified.
- Fixed failed-add diagnostics and new-Windows-repo local long-path support.
  12 adapter/five Windows cases, 13 backstop checks, legacy/hardening, full
  189-file gate and fresh/preservation packaging passed. Failed baselines retained.
- Runtime review accepted; code 516e0e615f89e99fc160d9917009899ebb783b42. Globals unchanged;
  no dependency install/publishing. Final scoped report remains authoritative.

## Phase summary: original plan local closeout - 2026-11-06

- Outcome: COMPLETE for the declared minimum scope; native support stays partial.
- Mid-turn auto continuation passed 16 controls. Explicit inert MCP mapping
  observed allow/two canonical denials; original harness failures retained and
  reconciled offline. No shipped default/global config activation.
- Full 189-file gate and fresh/preservation packaging passed. Existing domain
  files/assets preserved. Old-session handoff rollback was detected and repaired;
  one-writer/source refresh guidance added. No native fencing claimed.
- Phase 8 and efficiency adoption remain conditional; app/IDE/default routes
  explicitly unverified. Report: docs/audits/context-continuity-2026-11/completion-report.md.
- Next: use the verified template; extend support only with a scoped new task.
  Pacing OFF; local-only. No background worker or publication.

## Handoff budgets and source freshness - 2026-11-06

- Writer guidance now matches the 1,200-character validator cap, reconciles
  stale required records and checks FAST/compiler output before checkpointing.
- Downstream budget had already been shortened by another client. Replaced
  its obsolete initial fact through explicit supersession; original body and
  domain documents/assets preserved. Seven renderers and FAST pass.
- One review repair restored two existing prose lines after implicit Windows
  decoding; explicit UTF-8 and exact baseline comparisons protect untouched text.
- Generic smoke covers line/character mismatch and stale required-ID refusal.
  No compiler/validator behavior or native-delivery claims changed. Details:
  docs/continuity-workplan.md. Pacing OFF; local-only.

## Automatic pre-turn compaction - 2026-11-06

- Reduced invocation/thread threshold triggered automatic compaction without a
  manual compact RPC. A new record written after the seed turn was delivered
  by the fresh callback and read back exactly; 16 controls passed.
- Resume callbacks are deferred until turn/start; the seed prevents earlier
  injection from satisfying a fresh-data check. Saved-event replay/source match
  passed without another model call. Global config/four trust records unchanged.
- Remaining: default thresholds, mid-turn tool continuation, app/IDE/reset and
  MCP/publishing-denial routes. No real-project activation or autosave claim.
  Evidence: docs/recovery-pilot.md. Pacing OFF; local-only.

## Codex API clear/fork follow-up - 2026-11-06

- Explicit API clear and persisted-thread fork delivered distinct new required
  bodies/next actions; 13 controls each passed. Fork ID/parent lineage observed.
- Exact candidate/source bytes reconciled; global config/four approved trust
  records unchanged. No implementation repair or real-project activation.
- Antigravity restored-window observation was followed by a rejected off-screen
  action and desktop capture; no native hook success inferred. Remaining:
  stable app/IDE targeting, interactive reset, automatic compaction and MCP/
  publishing-denial routes. Evidence: docs/recovery-pilot.md. Pacing OFF.

## Codex automatic startup delivery - 2026-11-06

- Fixed ignored --client routing and added opt-in SessionStart mapping with
  Git-root selection and full delivery of the capped projection.
- Native startup/resume/compact each delivered a new required body and next
  action without a manual packet or model tools; 11 controls per phase passed.
- Global config and four approved trust records preserved. No real-project
  activation or conversation autosave. Clear/fork and desktop/cloud remain open.
- 21 continuity/five Windows cases, full 189-file gate, legacy hooks, fresh-project
  and upgrade smoke, Python 3.9 syntax and isolated review passed (327 hashes stable).
  Source/provenance: docs/recovery-pilot.md. Pacing OFF; local-only.

## Native model/trust/tool follow-up - 2026-11-06

- Native gpt-6-astra to gpt-6.1-sol transition at xhigh passed all 13 checks in
  the same persisted thread; exact facts/tasks/qualifier recovered without tools.
- Hash-trusted patch denial, allowed patch/root logger and Bash sensitive-write
  controls passed without bypass. Changed command reports modified. Retain the
  earlier ignored-key setup and incorrect-enum assertion; offline reconciliation.
- Human approved four fixture trust records. Native CLI persisted exactly four;
  fresh-process denial/trust passed nine checks without pins or bypass. Other
  semantic user settings preserved. Current-process verification remains separate.
- Open: remaining UI/model/tool routes; docs/recovery-pilot.md. Pacing OFF.

## Codex Windows native hook repair - 2026-11-06

- Discovered-but-untrusted hooks did not run with the process flag alone.
  A per-thread runtime override exposed exit1 from nested PowerShell commands;
  native inert writes completed. Failed baselines are retained, not accepted.
- Direct Windows bodies plus physical-CWD Git lookup fix variable expansion and
  bracket-path startup. Native PreToolUse now blocks the inert apply_patch with
  its exact policy reason; file absent. Model/effort and global defaults preserved.
- Four Windows cases, full 189-file gate, fresh-project/upgrade smoke and Python 3.9
  syntax passed. Isolated review accepted after one evidence/fixture repair;
  all 327 frozen hashes unchanged. Downstream user-file hashes preserved.
- Remaining native trust/model-switch/UI/tool-route gaps: docs/recovery-pilot.md.
  Do not repeat passed probes. Pacing OFF; no publication.
- Antigravity UI journal attempt is inconclusive: geometry unavailable, then
  capture/accessibility window mismatch. Re-establish the target before input.

## Antigravity hook launch repair - 2026-11-06

- Baseline reproduced: canonical hook command exits0 from project root but
  exits2/missing-script from `.agents`; a relative script path blocks benign
  terminal calls before the policy code runs. Asset access was not prohibited.
- Refuted: a single-line inline bootstrap is portable after shell tests pass.
  User runtime and direct-argv regression both produced an unterminated string.
- Repair uses a quote-free file argument relative to `.agents`, with sibling
  imports anchored at the dispatcher. Event CWD never selects executable code.
  Existing denials and explicit benign deferral to platform policy remain.
- Eight regressions now cover direct argv and shell launches, separate tool CWDs,
  log placement and guard failures. Downstream user-file hashes are preserved.
- Full 188-file gate, fresh-project/upgrade smoke and Python 3.9 syntax passed.
  Isolated critic accepted; the frozen 326-file inventory stayed unchanged.
- Native UI must reload the changed workspace hooks; no claim of automatic
  current-process containment. Do not repeat completed native lifecycle probes.

## Native follow-up checkpoint - 2026-11-06

- Scoped checks COMPLETE; broad native coverage remains PARTIAL. Approved isolated
  Codex 0.167.0 archive verified; configured gpt-6-astra/xhigh preserved. Six CLI,
  six fresh-process stdio recall and six post-contextCompaction checks passed.
- Claude2.1.116 real resume/compact observed; initial quotation omitted a second
  marker sentence (6/7). Full-body clarification after compaction passed7/7.
  Native Write attempt/deny/absent-file checks passed. Original failures retained.
- Codex denial remains unverified: bounded exec probes did not expose the required
  native policy reason. Trust-bypass warnings/file absence are not proof.
- Checks: full186-file gate, fresh-project declaration/mirror/FAST smoke,
  Python 3.9 syntax and isolated review accepted after one documentation repair;
  frozen324-file inventories unchanged. Unknown defaults remain valid in CI.
- Native capability task parent-accepted against unchanged inventory. Remaining
  lifecycle task names model switch, denial/trust and untested interfaces; do
  not repeat passed probes. No global PATH/model edits, pacing or publication.

## Native follow-up and record formatting - 2026-11-06

- Fresh-project use exposed trailing whitespace in empty global-record task
  metadata. Formatter now emits a clean empty scalar; 16 capture tests, 15
  compiler checks and an actual staged Git whitespace gate pass.
- Native follow-up is in progress. Claude restart/compact boundary and Write
  denial observed; an initial exact-body marker omission required a focused
  full-source request, which passed. Detailed evidence will be recorded separately.
- Human approved isolated Codex 0.167.0; official archive SHA-256 verified.
  New catalog contains the existing configured model; no default/PATH edits.

## Continuity implementation: phase 7 and disposition - 2026-11-06

- Outcome: core phases1-7 COMPLETE locally; native phase6 evidence PARTIAL;
  phase8 conditional/deferred without measured fleet need. No publication.
- Feedback/source -> reviewed decision -> task input -> independent parent
  verification/acceptance is documented and tested; examples stay qualified.
  Optional environment acceptance avoids mandatory product interviews/deployment.
- Resume now lists every open-task page alongside handoff/doctor. Eight integrated
  cases, full186-file gate, mirrors, Python 3.9 syntax, new-project and upgrade
  surface smoke passed; isolated review accepted with unchanged324-file inventory.
- Open native evidence is queued privately as native-codex-capability and
  native-lifecycle-gates. No workers, installs, global edits or pacing activation.
- Reference: docs/continuity-workplan.md and docs/recovery-pilot.md. Before any
  native follow-up, inspect changed capabilities; do not repeat unchanged failures.

## Continuity implementation: phase 6 - 2026-11-06

- Outcome: offline recovery COMPLETE; native verification PARTIAL. Seven
  integrated cases, repeated fresh-process cycles, full 184-file gate, new-project
  smoke, Python 3.9 syntax and isolated source/evidence review passed.
- Claude2.1.116 passed supplied-packet and real SessionStart marker recall with
  tools disabled. It recognized the missing complete task board. Codex0.142.0
  failed default and configured-model requests; Gemini0.52.0 was version-only.
- Refuted hypothesis: the CLI default matches the app-selected model. Neither
  default nor configured retry produced a valid Codex answer. No substitutions.
- Open: real compaction/restart/denials, other surfaces and paired efficiency
  evidence. Details: docs/recovery-pilot.md. No installs or global settings edits.
- Next: phase7 feedback/acceptance closure and explicit runtime disposition.

## Continuity implementation: phase 5 - 2026-11-06

- Outcome: COMPLETE locally. Ordinary task counters, provenance, disjoint
  actor/segment totals, unknown handling and hard-budget advice work with pacing
  OFF. Benchmark supports inclusive reasoning without double counting cache.
- Checks: 17 metric tests, 34 pacing tests, benchmark self-test, full 181-file
  gate, fresh-project smoke, Python 3.9 syntax and isolated acceptance.
- Refuted hypothesis: adjacent readings suffice to detect resets. Four red
  regressions showed a null/omitted reading hid earlier known usage; per-field
  high-water validation fixes this while preserving latest unknown totals.
- Next: phase 6 integrated recovery and narrowly labeled native evidence.

## Continuity implementation: phase 4 - 2026-11-06

- Outcome: COMPLETE locally. Private durable tasks preserve attempts, revisions,
  next actions and separate parent acceptance; dependencies and inventory scope
  gates reject stale or mismatched evidence. Native supervision remains absent.
- Checks: 22 task tests, full 177-file gate, Python 3.9 syntax, fresh-project
  smoke and isolated acceptance; frozen review inventories remained unchanged.
- Refuted hypothesis: limiting start transitions bounds open work. Critic found
  queued blockers bypassing admission; both capacity and ownership now have
  preservation regressions. New-project smoke requires tracked artifacts.
- Next: phase 5 ordinary task measurements; pacing stays OFF.

## Continuity implementation: phase 3 - 2026-11-05

- Outcome: COMPLETE locally. Atomic record capture/read-back, task/archive
  selection, explicit source/category and mandatory-ID protection are wired
  into canonical memory workflows and generated mirrors.
- Checks: 16 record tests (including 1,000-record archive), 15 compiler cases,
  18 restore tests/full 173-file gate, new-project roundtrip and isolated review.
- Refuted hypotheses: task-specific records could share the old prefix metric
  (task-switch regression required a global-only prefix); post-write capacity
  validation preserved usability (review caught overflow; refusal now precedes
  publication and preserves every existing byte).
- Next: phase 4 durable task manifests; docs/continuity-workplan.md. Remaining
  core implementation is authorized; native measurements remain unverified.

## Continuity implementation: phase 2 - 2026-11-05

- Outcome: COMPLETE locally. Added strict bounded source parsing, private
  checkpoint/doctor CLI, visible hook failures and manual recovery guidance.
- Removed the unverified active PreCompact notice; no native delivery claim.
- Checks: 18 restoration tests, 15 compiler cases, hooks, full 171-file gate,
  Python 3.9 syntax and new-project smoke. Reviewer accepted after one repair.
- Refuted hypothesis: matching hashes imply complete resume state. Reviewer
  found empty collections, interleaved writes and malformed-event fallback;
  regressions reproduce the gaps and pass after correction.
- Next: phase 3 record writes and task projections; docs/continuity-workplan.md.

## Continuity implementation: phase 1 - 2026-11-05

- User authorized phased implementation and broader research. Nine primary
  sources and limitations are mapped in docs/agentic-engineering-evidence.md.
- Corrected context/cache/durability claims and the historical hook guarantee;
  CI schedules the full gate once, retaining its compatibility and self-tests.
- Full gate and CI schedule/coverage assertions passed. No runtime activation.
- Next: strict restoration diagnostics; state in docs/continuity-workplan.md.

## Phase summary: continuity audit and plan - 2026-11-05

- Outcome: COMPLETE for audit/planning; runtime implementation not started.
- Reviewed the supplied harness article against compiler, hooks, memory,
  delegation, quota advice and CI; recorded 12 findings and eight phases in
  docs/audits/context-continuity-2026-11/.
- Refuted hypothesis: a green structural gate proves recovery. Temporary
  probes reproduced silent status/decision gaps and a reminder-only checkpoint.
- Checks: full gate passed before/after audit artifacts; ten Boolean probe
  observations reproduced; saved hashes/results, Python 3.9 syntax and links
  verified. Isolated static critic accepted; 302-file inventory unchanged.
- Open: native lifecycle tests and provider cost measurements; no runtime fixes,
  installs, quota activation, model calls for benchmarks or publication.
- Next: implement proposed phases 1-3 when requested; retain local-only scope.

## v1.2.1 publication complete - 2026-10-31

- Published main/tag v1.2.1 at 90509d9 and the English release as Latest.
- Hosted run 41240580039 passed all four Ubuntu 24.04/Windows, Python 3.9/current
  jobs. The earlier v1.2.0 tag remains unchanged; its draft was retargeted.
- Final 298-file tree, all outgoing blobs/commit metadata and annotated tag
  metadata passed content review for credentials, IPs, personal paths and
  Cyrillic. Publishing used GitHub no-reply metadata and an exact two-ref gate.
- Release body is 199 English words with a ready-to-paste existing-project
  upgrade prompt. README overview and repository description are updated.
- Published-tag smoke preserved application behavior and custom rules; the
  earlier smoke also verified existing memory and a distinct application origin.
- Local push protection/private refs remain preserved. No company project was
  modified. Pacing stays OFF. Publication receipt is recorded locally.


## v1.2.1 hosted compatibility fix - 2026-10-31

- v1.2.0 main/tag were published at 3888530 after local full/compatibility checks
  and a clean 297-file/33-blob outgoing audit. Release remains a draft.
- Hosted run 41240230952 found two independent issues: ubuntu-latest moved to
  Ubuntu 26.04 without Python 3.9 builds; Windows temporary-path aliases exposed
  a direct engine API comparison between resolved and unresolved paths.
- Refuted hypothesis: local checks plus Python 3.9 grammar implied hosted matrix
  compatibility. A focused alias regression fails the old engine and passes
  after canonicalizing both sides. Python build manifest confirms Ubuntu 24.04.
- Keep the published v1.2.0 tag unchanged; publish the correction as v1.2.1 and
  retarget the draft. Existing-project smoke passed against the v1.2.0 tag,
  preserving app checks, custom rules, memory and a distinct application origin.
- Pending: corrected full checks, audit and all four hosted jobs before Latest.


## v1.2.0 publication preparation - 2026-10-31

- User explicitly authorized a new GitHub release and English-only public material.
- Scope: version/release notes, existing-project upgrade prompt, refreshed SVG
  overview and source/content/metadata review before exact main/tag publication.
- Public base: fc9d91b (v1.1.1). Local push protection and unrelated private refs
  remain intact; publication uses an isolated repository and exact-ref gate.
- Removed corrupted Cyrillic Unicode fixtures in favor of English text and
  Unicode symbols. Context integrity and 22 upgrade scenarios still pass
  (one unavailable Windows symlink case skipped; junction case passes).
- Pending: full release checks, outgoing-object security audit and hosted CI.


## Remote preservation upgrades - 2026-10-31

- Scope: GitHub/GitLab source reads, SHA-pinned previews, remembered file hashes,
  legacy baselines, preserved conflicts and external backup/report transactions.
- Replaced unsafe overwrite/regex rule extraction; application files, active
  settings and existing project memory remain outside automatic updates.
- Latest workflow can bootstrap older projects from a URL; source credentials
  use existing Git authentication. No dependency installs or publication.
- court-skill inspected without execution/vendoring; adopted evidence and
  reversal conditions in critic guidance, not its default 17-agent trial.
- Refuted hypotheses: the old merge preserved every custom rule (regex omitted
  arbitrary sections); hash membership alone proved a retired helper unchanged
  (critic found customized retired files). Preservation regressions cover both.
- Checks so far: 22 upgrade regressions (one unavailable Windows symlink case
  skipped; junction regression passes), 34 pacing regressions, FAST validation,
  skill schema, mirrors and Python 3.9 grammar. GitHub preview at fc9d91b wrote
  zero target files. Hosted GitLab/private authentication remains untested.
- Outcome: COMPLETE locally. Full validation and final critic acceptance pass;
  before/after content inventories confirm read-only review. No publication.
- Changed: upgrader/engine/tests, skill and workflow mirrors, source/upgrade
  guides, README/changelog, critic assessment and operational memory.


## v1.1.1 publication - 2026-10-29

- User explicitly authorized GitHub publication and a patch release with a short description.
- Published main/tag v1.1.1 at fc9d91b and the English release as Latest. Hosted run 40966241837 passed all four Windows/Linux, Python 3.9/current jobs.
- Outgoing audit covered two commits and 20 text blobs with no sensitive-pattern findings; commit/tag metadata use GitHub no-reply. Release notes are 110 words.
- Local push block and private refs were preserved using an isolated publication repository with an exact two-ref gate. Pacing stays OFF.
- Refuted hypothesis: an explicit tag refspec alone prevented auto-following other public tags. The exact-ref gate stopped the first attempt before push; adding --no-tags restricted the successful fetch.

## Phase summary: completion-first coordination - 2026-10-29

- Outcome: COMPLETE for advisory admission and coordination policy; native fleet runtime remains future work.
- Decisions: one worker/two open tasks by default; no recursive spawning; parent acceptance releases dependencies; drain reviews/blockers and 75% context.
- Admission: fresh run-bound board, matching worker count, acyclic dependencies and entire required package costs with a 50% estimate margin across time/all quota windows.
- Refuted hypothesis: funding only the dispatched task was sufficient; critic probes showed downstream integration could overrun. Full-package reservation and regressions address this.
- Files: pacing CLI/tests, delegation contract/skill mirrors, root guidance, testing docs and changelog.
- Checks: 34 offline regressions; full/compatibility gates, context self-test, Python 3.9 grammar and independent read-only critic acceptance. Parent confirmed unchanged tracked-file hashes after review.
- Open: durable task/attempt ledger, atomic path leases and one tested native dispatch/cancellation adapter; see docs/subagent-contract.md.
- Pacing remains OFF. No real worker fleet or provider quota run started; no push/publication authorized.

## v1.1.0 release packaging — 2026-10-26

- Outcome: COMPLETE. Published v1.1.0 as Latest at 1e9ca6e; hosted run 40432331642 passed all four jobs.
- Repository description and README overview are updated; the release includes English notes and PNG/SVG visual assets.
- Current user authorized a visible versioned GitHub release and English description/visual updates.
- VERSION/changelog promoted to 1.1.0; README prioritizes new capabilities and links to release notes.
- Expanded the native SVG overview with a highlighted new-in-1.1 row. Chrome rendering produced a 2400x1520 PNG with no embedded metadata or text overflow.
- Release assets are derived only from public template content. Company repositories are outside this work unit.
- Full validation and outgoing content/metadata review precede the main/tag push; native client guarantees are unchanged.

## Publication and English starter verification — 2026-10-26

- Published reviewed main at 5f46a66; hosted run 40409209097 passed Windows/Linux and Python 3.9/current.
- Reviewed 291 tracked files, 39 outgoing text blobs and commit metadata; no checked sensitive-pattern findings. The public commit excludes unpublished non-no-reply metadata and prior local-only history.
- Repository documentation and commit messages are English. Fixed corrupted separators in generated README/Memory Bank stubs; fresh generated Markdown and Python 3.9 grammar checks pass.
- Full local validation passes after the generator fix. Native-client behavior remains unverified; pacing remains OFF.
- Company project state is maintained separately and is not a public-template input.

## Publication preparation — 2026-10-26

- Current user explicitly authorized a reviewed GitHub main push.
- Documented the implementation and Unreleased changes; no new release/tag requested.
- Outgoing source content passed initial pattern review; unpublished non-no-reply author metadata is excluded from the public commit ancestry and retained locally.
- Full validation and a final outgoing-object audit precede the main-only push.
- Separate company-project context must stay outside this public repository.

## Phase summary: current-client review and optional pacing — 2026-10-26

- Outcome: COMPLETE; verified locally, no publication authorized.
- Decisions: verification-first proportional plans; thin workflow skills for current Antigravity; quota pacing OFF until separate human confirmation.
- Evidence: supplied Gemini summary and developer playbook checked against official sources; full Gemini artifact/video timestamps unavailable/unverified.
- Refuted hypotheses: fixed first-100-lines truncation is not a universal skill rule; native goals do not measure subscription quota; legacy Gemini hooks are not current Antigravity payloads.
- Files: root guidance, workflows/skill discovery, routing/hooks docs, market/mail assessments, pacing CLI/tests and upgrade manifests.
- Checks: full gate passes (165 required files, 22 skills/3 trees); 18 pacing/integration regressions; Python 3.9 grammar; disposable fresh-project creation/upgrade/mirrors pass.
- Open: live client smoke tests and provider measurements; local mail intentionally optional, Ponytail uninstalled.
- Pacing: no real run activated; tests use disposable databases. Template origin detached and push block preserved; nothing published.

## v1.0.0 release completion - 2026-10-03

- Updated README, native SVG hero, release notes and changelog to match current behavior.
- Public Memory Bank contains template facts only. Unrelated project notes and
  unpublished operational history are excluded from the public release ancestry.
- Preserved implementation history locally; the release snapshot advances existing
  public main without rewriting published commits. New metadata uses GitHub no-reply.
- Pattern review covers tracked files, historical blobs, outgoing objects and
  author metadata. Ignored logs, caches and local scratch are not release inputs.
- Published v1.0.0 at ae5b1ad after local validation. Hosted CI run 37156383241
  passed all four Windows/Linux and Python 3.9/current jobs.
- Outgoing review covered 100 unique text blobs before retaining existing CI;
  no credential, private-key, email or unrelated-project matches were found.
- Repository description, documentation link, topics and native SVG landing page
  are updated. GitHub secret scanning and push protection are enabled.
- Local push protection was preserved during the explicitly authorized push.
- Native containment, live client denials and provider cache savings remain unverified.

## Refuted hypotheses

- Worker-writable hooks were not a universal publishing boundary. They prevent
  ordinary accidents; external supervisor controls are not supplied.
- Comparing durable prefixes across clients ignored client-specific notes. Tests
  now compare status changes within each renderer.
