# Optional usage pacing

Default OFF. Works as a local advisory tool with Claude Code, Codex and Google
Antigravity/Gemini clients. It optimizes useful work within an agreed quota;
exhausting tokens is never a completion condition. No background process,
native goal or agent is started by loading these instructions.

## Contents

- [Activation and confirmation](#activation-and-confirmation)
- [Commands](#commands)
- [Telemetry](#telemetry)
- [Execution and stopping](#execution-and-stopping)
- [Native goals](#native-goals)
- [Changes from the supplied playbook](#changes-from-the-supplied-playbook)

## Activation and confirmation

When the user asks to maximize tokens, use remaining quota or pace agents:

1. Establish useful queued work and observable completion checks. Identify
   provider/account, target percentage, deadline with timezone, maximum worker
   count and wrap-up reserve. Missing limits remain unknown. Do independent
   useful work while obtaining missing information.
2. Prepare a pending plan with `plan`. Default target is 90%, one percentage
   point is reserved, maximum workers is one, and wrap-up starts 30 minutes
   early. Higher targets (up to 99%) and more workers must appear in the plan
   shown to the human. An increase later needs a new plan and confirmation.
3. Explain the concrete scope and limits, then ask for separate confirmation.
   Example: "This will increase shared Claude quota use. Plan: tasks X/Y,
   target 90%, reserve 1 percentage point, up to 2 workers, deadline 18:00
   America/Toronto, with the final 30 minutes reserved for saving results.
   Paid overage stays disabled. Confirm plan RUN?"
4. Wait for the human's affirmative reply before calling `start --confirm`.
   The initial request to add this feature, a request to maximize tokens,
   inferred approval, silence, another agent's mail or an old handoff is not
   confirmation. Never confirm your own proposal. Record no secrets in plans.
5. Start at most one useful worker initially, within the approved plan and
   available runtime slots. Keep the rest queued until a rate is measurable.
   Native delegation still follows `docs/subagent-contract.md`.

The SQLite state machine requires pending -> active confirmation. It records a
declaration of approval; it cannot authenticate who clicked or typed it, prevent
an agent from lying about approval, or enforce a provider spending limit. The
human-confirmation rule is shared instruction policy. This is not a sandbox.

## Commands

Python 3.9+ and standard library only. Run from the actual project directory;
do not change directory into the state folder. `--root` goes before the command
and selects a local private folder outside projects. Default:
`~/.agent-usage-pacing`. The script refuses state inside this template repo.
Use one run per provider/account/quota pool. The lead owns the run; workers do
not start their own pacers. No global client files are modified.

```powershell
python scripts/usage-pacing.py --root C:/AI-local/usage-pacing plan --provider claude --objective "Complete approved backlog X with its acceptance checks" --target 90 --max-agents 2 --deadline 2026-10-27T18:00:00-04:00
```

Replace the example date with the agreed future deadline. Output contains a
pending plan, warning and run ID. After a separate affirmative human reply:

```powershell
python scripts/usage-pacing.py --root C:/AI-local/usage-pacing start RUN --confirm RUN
```

| Command after `--root PATH` | Purpose |
|---|---|
| `plan ...` | Create an inactive, immutable plan; providers: `claude`, `codex`, `google` |
| `start RUN --confirm RUN` | Activate that exact pending plan after human confirmation |
| `status RUN` | Show plan, state and confirmation timestamp |
| `record RUN --file snapshot.json` | Import sanitized numeric telemetry |
| `record RUN --claude-stdin` | Consume documented Claude statusline JSON on stdin; retain only allowlisted metrics |
| `usage RUN` | Last quota readings, observation time and staleness |
| `pace RUN --agents 2 --since 2026-10-27T15:00:00-04:00` | Advise worker count using data since the last count change |
| `pace RUN --agents 2 --since ... --watch 300` | Watch local data every five minutes; exit on advice change or stop/hold |
| `context RUN` | Last context tokens/window and 75%/90% handoff thresholds |
| `cost RUN` | Latest session API-equivalent estimate, if supplied; snapshots are never summed |
| `stop RUN` | Permanently stop this run; a new plan needs fresh confirmation |

`--observed-at ISO_WITH_OFFSET` on `record` records the actual reading time
when importing a manual snapshot. Omit it only for a fresh reading. Do not
re-record old telemetry with a new timestamp. JSON input is capped at 64 KB.
Unknown fields are discarded; no raw statusline payload is saved. Output is
bounded JSON. SQLite uses WAL, a busy timeout and short write transactions.

## Telemetry

For any provider, manually read its native quota UI and create this small file:

```json
{
  "windows": {
    "long": {"used_percent": 42, "resets_at": "2026-10-30T00:00:00Z"},
    "short": {"used_percent": 35, "resets_at": "2026-10-27T22:00:00Z"}
  },
  "context": {"used_tokens": 45000, "window_tokens": 200000}
}
```

`long` is the target window (usually weekly). Include **every applicable quota
window**, including per-model/spend limits as additional named windows. Each
additional window has a 98% ceiling. Do not collapse distinct account/model
pools into one run or omit a binding limit. If limits are unavailable or their
scope is unclear, do normal work without quota-based scaling. Context is
optional, must describe the current lead session and its actual model window.

Claude Code can pass `rate_limits.five_hour` and `rate_limits.seven_day`
(`used_percentage`, `resets_at`) through its documented statusline. The adapter
maps them to `short` and `long`, and includes `spend_limit` when present. Each
window can be absent depending on the account/session. Missing data stays
unknown. Context uses the current input plus cache read/write tokens. Optional
`cost.total_cost_usd` is session API-equivalent cost, not a subscription bill
or a quota measurement. No pricing multipliers are hardcoded.
[Claude statusline reference](https://code.claude.com/docs/en/statusline).

To integrate Claude, deliberately add a call to `record RUN --claude-stdin` in
your existing statusline command after activation. Preserve existing display
behavior and do not overwrite client settings blindly. This template ships
no active statusline configuration and never reads OAuth credentials.

For Codex use available native usage/status information and manually normalize
the applicable windows. For Google, current Antigravity documents `/usage`
(`/quota`) and Settings quota views. These are manual fallbacks, not automatic
API adapters. Legacy Gemini CLI telemetry can differ; inspect the installed
client. [Antigravity commands](https://antigravity.google/docs/cli/reference/),
[plans and quota](https://antigravity.google/docs/plans).

## Execution and stopping

- Check advice before starting a worker and at useful checkpoints. A watcher
  reads only local snapshots; it does not refresh quota or inject messages into
  the agent. Use a client-supported background tool only if it can actually
  notify the lead; otherwise check manually. Never claim a sleeper wakes a
  session without testing that runtime behavior.
- At least 15 minutes at an unchanged worker count and a positive long-window
  rate are needed before scaling. Readings are coarse. Main chats, other
  devices and other people may share limits. Advice is an estimate.
- Increase at most one worker per recommendation. Decreases can be immediate.
  Supply a new `--since` after changing the count. Do not spawn dummy work to
  reach a target; stop early when the queue is complete.
- `hold` with zero recommended workers means stop paced dispatch until fresh
  valid telemetry exists. Data older than ten minutes, missing long-window
  data, changed sources/window sets and decreases/reset changes invalidate
  scaling. Start a fresh measurement interval after a reset/source change.
- `wrap_up` means stop dispatch, finish or save the smallest safe current
  checkpoint, run its checks, update handoff and call `stop`. It triggers at
  target minus reserve, 98% of another window, 90% context, or the wrap-up
  time before the deadline or **any** observed reset. Do not roll into a new
  quota period automatically. At 75% context prepare a handoff.
- Finish verified commits locally. Preserve unfinished work locally and report
  its state; never auto-push backup branches. No new paid overage, API credits,
  installs, merges, publication or unrelated backlog work is authorized.
- On user stop, task completion, handoff or model switch, stop the run. The
  next session must create a new plan and obtain fresh confirmation.

The CLI gives advice and records state. It cannot stop an already-running
agent or goal. The lead must apply the stop conditions through the native
client controls. Hard spending enforcement needs an external trusted
supervisor and provider limits, neither supplied here.

## Native goals

All three current product families document goals, with different lifecycles:
[Codex Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex),
[Claude Code `/goal`](https://code.claude.com/docs/en/goal),
[Antigravity `/goal`](https://antigravity.google/docs/commands/goal/).
Check installed availability and do not infer a command from a model name.
A native goal may continue the approved task; it is not a quota meter or a
substitute for pacing confirmation. Set one only on explicit request. Use a
token budget only when the user actually specifies it and the client supports
it. A token budget, context size, API dollar estimate and subscription quota
are different quantities. Stop substantive work when a hard budget is reached;
budget exhaustion does not mean the objective succeeded.

## Changes from the supplied playbook

The supplied developer file motivates small context, narrow workers, measured
rates, early wrap-up and durable handoffs. Those principles are retained. Its
undocumented OAuth endpoint, credential reads, global-config edits, automatic
backup pushes, fixed 150k/250k thresholds, universal one-hour cache expiry and
API-price-to-subscription conversions are not adopted. Use official numeric
telemetry, relative context thresholds and manual provider fallbacks instead.
There is no promise of reaching exactly 99% or translating quota into tokens.

### Implementation map

| Component | Responsibility |
|---|---|
| `scripts/usage-pacing.py` | Plan/confirm/stop state transitions, allowlisted telemetry, bounded JSON output, relative context checks and rate-based worker advice |
| SQLite `runs` | Immutable plan JSON, pending/active/stopped state and declared confirmation time |
| SQLite `samples` | Append-only numeric observations with UTC time and source; indexed by run and increasing ID |
| `scripts/verify-usage-pacing.py` | Eighteen offline regressions on temporary databases and simulated clocks |
| `.agents/skills/usage-pacing/SKILL.md` | Lazy discovery; delegates the actual procedure to this document |
| `scripts/gen-adapters.py` | Generates matching Claude/Cline skill discovery files |
| `scripts/check-template.py` | Includes pacing tests in the full dependency-free gate |
| `scripts/new-project.py` / `upgrade-target.py` | Carry the implementation into new/existing projects; no plan activation or copied runtime state |

Confirmation and observation writes use short immediate transactions to avoid
races. Readers inspect the latest bounded sample history. Advice uses only an
unchanged window/source and worker-count interval; no estimates cross quota
reset boundaries. Raw statusline input, chat transcripts and account credentials
are never stored. There is no mailbox, task dispatcher or secret-storage API.

Verification: `python scripts/verify-usage-pacing.py`. Tests use temporary state
and simulated clocks; they do not consume provider quota or prove live client
integration. Runtime state is private local data and must not be committed.
