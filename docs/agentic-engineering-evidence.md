# Evidence for the continuity implementation

Reviewed 2026-11-05. This is a focused primary-source review across industrial
engineering reports, software-engineering experiments and multi-agent research.
It extends the initial article-triggered audit; it is not an exhaustive
systematic review or a claim that historical benchmark results describe current
models. No social-media productivity claim is used as an acceptance target.

## Sources and decisions

| Primary source | Evidence and limits | Application to this template |
|---|---|---|
| [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), 2025-11-26 | Engineering experiments identify premature completion and undocumented partial work across sessions. This is a vendor case study, not a controlled comparison of all harnesses. | Small verified increments, persistent progress/evidence, explicit incomplete work, startup reconciliation. |
| [Anthropic: Effective context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents), 2025-09-29 | Advocates concise relevant context and just-in-time retrieval through lightweight references. General engineering guidance; no universal context size or cache saving follows. | Separate required constraints from retrievable archive; preserve source IDs and qualifications. |
| [Anthropic: Multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system), 2025-06-13 | Parallel agents benefit independent broad research queries in their internal evaluation, with substantial token overhead. Research performance does not establish shared-worktree coding performance. | Delegate bounded independent work; retain one coordinator and explicit ownership/acceptance. Scale only after measured benefit. |
| [OpenAI: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), 2026-02-23 | A documented long-run experiment uses durable specification, milestone validation and status artifacts. One experiment is not a reliability or cost guarantee. | Persist spec/plan/status; make each milestone demonstrable and recoverable. |
| [SWE-agent](https://arxiv.org/abs/2405.15793v3), 2024-11-11 revision | Studies agent-computer interface design for repository navigation, edits and execution. Evaluation concerns specific tasks/models from its period. | Invest in bounded, structured tool outputs, actionable diagnostics and appropriate checks; larger prompts alone are insufficient. |
| [Agentless](https://arxiv.org/abs/2407.01489v2), 2024-10-29 revision | Demonstrates a simple localization/repair/validation pipeline on benchmark repair tasks. Its results do not imply all development should be non-agentic. | Preserve a simple sequential baseline. Do not add orchestration, a vector store or more agents without a concrete unmet requirement. |
| [MAST: Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657v3), 2025-10-26 revision | Empirical trace analysis groups failures around system design, inter-agent alignment and task verification. Taxonomy is diagnostic; it does not prove any one mechanism prevents all failures. | Test ownership, stale state, handoff completeness, termination and independent acceptance as separate invariants. |
| [METR: experienced developer productivity experiment](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/), 2025-07-10 | Randomized study of experienced contributors using early-2025 tools found slowdown in that setting. It is not a forecast of current tools or novice/greenfield work. | Measure accepted useful tasks, rework and human time rather than perceived speed, code volume or agent count. |
| [METR: experiment-design update](https://metr.org/blog/2026-02-24-uplift-update/), 2026-02-24 | Follow-up explains selection and time-accounting biases that weaken its newer productivity estimate, including concurrent-agent use. | Report uncertainty and scope. Separate task elapsed time, human active time and shared-account cost; do not publish a universal speedup. |

## Synthesis and changes to the plan

These are engineering inferences from the sources, to be tested locally:

1. Reliability needs observable environment state and acceptance evidence as
   well as memory. A compiler receipt proves rendering, not model consumption.
2. Simpler execution is the baseline. Durable task state should be useful for
   one coordinator before any fleet runtime is added.
3. A clean restart must recover required decisions and unfinished work while
   recognizing missing evidence. Compaction alone cannot certify that outcome.
4. Context selection must be deterministic and explicit for required constraints.
   Historical records should remain addressable without all entering startup.
5. Store local telemetry and raw feedback privately; reviewed project records
   and bounded exports have different retention/transport requirements.
6. Measure total accepted-task cost, including restoration, reviews and repairs.
   Keep historical papers, current vendor documentation, synthetic regressions
   and live client evidence clearly separated.

The eight-phase audit plan remains directionally valid. Implementation starts
with removing duplicate work, validating restoration and connecting record
writes to projection. Broad fleet supervision and cross-machine transport stay
conditional on an actual use case and measured advantage.

## Acceptance evidence hierarchy

Use repository-specific behavioral checks for each implementation decision.
Schemas establish shape, negative fixtures exercise known failure paths, and
client smoke tests establish native delivery for a named version/surface.
Neither a passing fixture nor a second model's opinion establishes production
behavior. A complete change must keep meaningful verification, error handling,
security and accessibility where applicable.

Remaining research questions: which native event can safely deliver each
client's recovery packet; actual model-consumption receipts where exposed;
measured quality/cost on this user's tasks; and the point at which parallel
implementation pays for its coordination. These require experiments rather
than more unsupported root instructions.
