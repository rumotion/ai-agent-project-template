# Context Compiler (`scripts/ctx.py`)

The Context Compiler turns the Memory Bank into a **compiled context artifact**
instead of a set of prose files each agent re-reads in its own order.

## Why

Every client reads `AGENTS.md` natively, then models re-read memory files in a
model-dependent order. That means: non-deterministic prefix order (worse
prompt-cache hit rates), per-client double-loading of duplicated rules, and
no hard cap on injected context size. The compiler fixes all three
mechanically:

1. **Deterministic output** — the same memory compiles to the same bytes
   (`sha256` reported on stderr / in `--json`), so repeated sessions hit the
   same prompt-cache prefix instead of paying for re-read variance.
2. **Per-client dedup notes** — each blob's header tells that client which
   files are already loaded (`AGENTS.md`, rules adapters) so it stops
   re-reading them.
3. **Hard budget with safe distillation** — over-budget blobs drop droppable
   records (preferences first, then facts, highest priority number first);
   **decision, risk, and status records are never dropped**; `--check` fails
   CI if the remainder still exceeds the cap.

## Typed records

Records are small Markdown files in `memory-bank/records/`:

```markdown
---
id: decision-boundary-enforcement   # kebab-case, unique
type: decision                      # fact | decision | risk | preference
priority: 1                         # 1 = keep-alive ... 5 = drop first
superseded_by:                      # optional: id of the replacing record
---
One concise sentence or paragraph. Long bodies are whitespace-normalized
and capped at 400 characters in the blob.
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
## Status        <- memory-bank/handoff.md front-matter (status, task, next_action, blocking_issues)
## Decisions     <- typed records, p1 first
## Risks
## Facts
## Preferences
```

## When to write a record vs. a Memory Bank file

- **Record**: durable, small, always-relevant knowledge (a decision and its
  rationale, a standing risk, a stable project fact). Compiled into every
  session's blob, budget-capped.
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
