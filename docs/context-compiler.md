# Context Compiler (`scripts/ctx.py`)

The Context Compiler turns the Memory Bank into a **compiled context artifact**
instead of a set of prose files each agent re-reads in its own order.

Native recall is not an exact source read-back. A model can quote the main
decision while omitting a second sentence even when both were delivered. When
literal text or a qualifier matters, retrieve `ctx.py show --id ID`, inspect the
complete `raw_body`/`source_sha256`, and verify it against the saved source before
acceptance. For native probes, request the complete raw body including every
sentence/marker; keep failed assertions rather than relaxing an equality check.

## Why

Clients load project instructions through their supported adapters. The
compiler provides deterministic, bounded project data for startup and recovery:

1. **Deterministic output** — the same memory compiles to the same bytes
   (`sha256` reported on stderr / in `--json`). Stable bytes permit prefix
   reuse; actual provider cache hits and savings still need measurement.
2. **Per-client dedup notes** — each blob's header tells that client which
   files its adapter should have loaded. This is a deduplication hint, not
   proof that the native client loaded them or followed the hint.
3. **Hard budget with safe distillation** — over-budget blobs drop droppable
   records (preferences first, then facts, highest priority number first);
   **selected decisions, risks, task requirements and status are never dropped**; `--check` fails
   CI if the remainder still exceeds the cap.

## Typed records

Records are small Markdown files in `memory-bank/records/`:

```markdown
---
id: decision-boundary-enforcement
type: decision
priority: 1
superseded_by:
---
One concise sentence or paragraph. Complete bodies are whitespace-normalized;
the projection budget applies to the whole result, without body truncation.
```

## Usage

```bash
python scripts/ctx.py compile --for claude            # blob to stdout, metrics to stderr
python scripts/ctx.py compile --for cline --json      # machine-readable result
python scripts/ctx.py compile --for claude --check    # exit 1 on malformed/over-budget (CI)
python scripts/ctx.py self-test                       # deterministic harness
```

Clients: `claude`, `gemini`, `codex`, `cline`, `cursor`, `antigravity`,
`generic`. Blob composition (fixed order):

```
# Compiled project context (for <client>)   + dedup note
## Decisions     <- typed records, p1 first
## Risks
## Facts
## Preferences
## Status        <- memory-bank/handoff.md front-matter (status, task, next_action, blocking_issues)
```

## When to write a record vs. a Memory Bank file

- **Record**: durable reviewed knowledge with explicit global/task/archive
  scope. Legacy records default to global. Task/archive selection is described
  below; required records cannot be removed to obtain a budget pass.
- **Memory Bank file** (e.g. `activeContext.md`, `progress.md`): narrative
  working state an agent lazy-loads on demand via `00-index.md`. Not compiled.

Supersede a record (`superseded_by: <new-id>`) instead of deleting it when a
decision is reversed — the chain stays auditable in git.

## CI enforcement

`scripts/check-template.py` (full mode) runs `ctx.py self-test` and a
`--check` compile; `.github/workflows/validate.yml` mirrors this. A record
with a bad `id`, unknown `type`, or out-of-range `priority` fails validation.

## Startup integration and measurement

Claude SessionStart now uses the compiler API instead of reading and truncating
startup files. Durable records precede the handoff status suffix. JSON output
includes `render_version`, `stable_prefix_chars`, and `stable_prefix_sha256`;
regressions prove that changing status preserves that prefix. The instruction
header identifies the projection as project data subordinate to current user
instructions. Other clients can use the same CLI projection.

Record identities and metadata must be unique. Supersession must be acyclic,
refer to an existing record, and preserve its type. UTF-8/BOM is supported;
symlink records and sources over 16,384 bytes are rejected. Complete normalized
bodies are retained. Malformed or protected-over-budget projections fail every
CLI mode and emit no partial blob. Lower-priority preferences/facts may still be
dropped according to the documented distillation policy.

`est_tokens` uses a characters/4 heuristic, not a tokenizer. `measured_tokens`
is null until provider telemetry is supplied; no cache hit or token savings
have been measured. `benchmark-context.py` accepts sanitized usage records for
before/after comparisons. Stable bytes alone do not prove provider cache reuse.
The separate FAST_INIT aggregate remains capped at 9,500 characters, with an
8,500-character advisory target; no startup padding is introduced.

## Record capture and task selection

```powershell
python scripts/ctx.py record --id approved-layout --type decision --scope task --task-id dashboard --source-ref feedback-42 --body-file reviewed-note.txt
python scripts/ctx.py compile --for codex --task-id dashboard --require approved-layout --json
python scripts/ctx.py show --id approved-layout
```

Review/sanitize the body before capture. Raw private feedback stays outside
public repositories. `source_ref` is an opaque ID, not an imported path or a
grant of authority. Creation requires a unique ID and returns its stored path,
read-back SHA-256, category, selected task and actual inclusion state. Existing
records are never overwritten. Preserve reversals with a new record and explicit
same-category supersession; an old required ID fails instead of silently
switching meaning. `show` retrieves both active and superseded records.

Optional record fields:

| Field | Meaning |
|---|---|
| `scope` | `global` (legacy default), `task`, or `archive` |
| `tasks` | Comma-separated task IDs; required only for task scope |
| `category` | Matches type, or `example`/`hypothesis` on a fact record |
| `source_ref` | Opaque source ID; required by the capture command |

Task IDs and source references use lowercase letters, digits, dots, underscores
and hyphens, up to 64 characters. Record IDs remain kebab-case. A handoff can
bind `task_id` and comma-separated `required_records`; explicit CLI requirements
are added to those, never used to override them. Task-matched records are
required even when their type would otherwise be droppable. Archive records
remain retrievable without entering unrelated startup packets.

JSON projection receipts include `task_id`, `required_ids`, `excluded` IDs,
the exclusion reason and hashes of included sources. Missing/superseded required
IDs or invalid metadata produce no usable projection. `stored: true` with
`projection_state: blocked` means capture succeeded but the packet needs
reconciliation; do not retry under another ID or discard the record.
Global records precede a task-context suffix. The stable-prefix metrics cover
only retained global guidance, so a task switch does not itself rewrite that
prefix; actual provider cache reuse remains unmeasured.

Creation uses a cooperative exclusive writer lock, temporary file, fsync,
atomic replacement and read-back verification. A stale writer lock requires
manual reconciliation. These controls are not authenticated ownership or
hostile-process containment. The archive is bounded to 10,000 records, each
at most 16,384 source bytes. Schema shape is in
`schemas/context-record.schema.json`; runtime checks add semantic constraints.

Test with `python scripts/verify-records.py`. Fixtures include a 1,000-record
archive, qualifier/indentation preservation, required-budget refusal, duplicate
IDs, write failure, supersession and cross-process capture/restore. They do not
measure model recall or provider savings.
