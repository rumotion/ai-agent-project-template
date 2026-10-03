# Decisions

Record important project decisions here.

### 2026-08-20 — Build Automated Target Project Upgrader tool and modernize Spec-Driven Development (SDD)

Status: Accepted

Context: Upgrading existing derived projects to newer template versions was previously manual, error-prone, and required replicating files across multiple mirrored directories. Furthermore, 2026 agentic coding research shows that Spec-Driven Development with executable anchors and characterization test safety nets is essential to prevent "vibe coding" regressions.

Decision: Add `scripts/upgrade-target.py` as a deterministic standard-library Python CLI tool to upgrade any target repository with `--dry-run`, custom domain rules preservation, custom domain skills preservation, and automated post-upgrade validation. Modernize `workflows/spec-driven-development.md` and update `project-upgrader` skill and `upgrade-project.md` workflow across all 3 discovery trees.

Consequences: Users and agents can upgrade any target project safely in one command (`python scripts/upgrade-target.py --target <path>`) with zero manual drift. Target application code and custom domain skills remain 100% protected.

Related files: `scripts/upgrade-target.py`, `scripts/check-template.py`, `workflows/spec-driven-development.md`, `workflows/upgrade-project.md`, `.agents/skills/project-upgrader/SKILL.md`, `docs/upgrade-existing-project.md`, `scripts/README.md`

### 2026-08-20 — Adopt ARC-Skill cognitive doctrines (falsifiable predictions, escalation ladder, bimodal execution, refuted hypotheses ledger)

Status: Accepted

Context: ARC-Skill achieved a historic 100.00 RHAE on 25 ARC-AGI-3 games (183 levels) with unmodified Claude Code on Opus 5 across 115 compactions. Its core cognitive loop (predict before action, graded feedback, 4-tier problem-solving escalation, bimodal probe vs batch, and compaction-resistant refutation tracking) solves common failure modes in agentic coding (hallucinated passes, repeated dead ends, ungrounded edits).

Decision: Embed these principles into `AGENTS.md`, `docs/agent-loop.md`, `workflows/pre-edit-check.md`, `workflows/debug-issue.md`, `workflows/implement-task.md`, and `.agents/skills/karpathy-engineer/SKILL.md`. Maintain 100% mirror parity across all 3 workflow trees and all 3 skill trees. Keep FAST_INIT within the 9,500-char budget.

Consequences: Agents formulate falsifiable expectations before edits, escalate diagnostics through structured tiers, avoid batching speculative exploration, and track dead hypotheses in `activeContext.md` / `risks.md` to prevent re-testing disproven theories across compactions/handoffs.

Related files: `AGENTS.md`, `docs/agent-loop.md`, `workflows/pre-edit-check.md`, `workflows/debug-issue.md`, `workflows/implement-task.md`, `.agents/skills/karpathy-engineer/SKILL.md`, `memory-bank/activeContext.md`, `memory-bank/handoff.md`

### 2026-07-23 — Ship Phase 3 scaffolding without optional runtimes

Status: Accepted

Context: Research recommended native specialist roles, context compression,
provider memory, and emerging protocols, but the template must remain portable,
low-context, and zero-dependency.

Decision: Ship exactly one canonical read-only reviewer role with thin
Gemini/Codex/Claude adapters; add an offline manifest-based benchmark and
evidence threshold; keep provider memory advisory; track MCP, Agent Skills,
ACP, and A2A in dated documentation. Do not install or activate compression,
proxy, synchronization, or protocol runtimes without paired evidence and
separate approval.

Consequences: Advanced experiments are measurable and lazy-loaded. Validator
checks structural declarations only; native reviewer behavior remains a manual
pilot. FAST_INIT remains below the hard cap.

Related files: `docs/reviewer-role.md`, `.gemini/agents/reviewer.md`,
`.codex/agents/reviewer.toml`, `.claude/agents/reviewer.md`,
`benchmarks/context/`, `scripts/benchmark-context.py`,
`docs/context-memory-bridges.md`, `docs/protocol-watch.md`,
`docs/performance-experiments.md`

### 2026-07-23 — Implement Phase 2 Core Enhancements (portable subagent contract, workflows, shared hooks, inactive MCP examples)

Status: Accepted

Context: Gemini 3.6 Flash High executed Phase 2, followed by an independent
Codex review against first-party client hook documentation.

Decision: Keep the portable delegation/workflow additions; use shared stdlib
hook scripts with explicit native client adapters; activate verified Claude
guard/log mappings while leaving Gemini and Codex configs as inactive examples;
require behavior-level fixture assertions and native adapter validation.

Consequences: Delegation and evidence-grounded self-evaluation are portable.
Hook events and denial outputs remain client-correct. The stdlib validator now
checks 92 required files and rejects mirror drift, invalid hook mappings, and
machine-local file URIs without adding startup instructions.

Related files: `docs/subagent-contract.md`,
`.agents/skills/delegation-coordinator/`, `workflows/self-evaluate.md`,
`scripts/hooks/`, `.claude/settings.json`, `.gemini/settings.example.json`,
`.codex/hooks.example.json`, `scripts/check-template.py`

### 2026-07-23 — Standardize three-agent compatibility contracts

Status: Accepted

Context: Gemini, Codex, and Claude use different native skill and MCP discovery paths, while FAST_INIT has little remaining headroom.

Decision: Keep `AGENTS.md` canonical; use exact thin primary adapters; designate `.agents/skills/` as the canonical skill tree with byte-identical `.claude/skills/` and `.cline/skills/` mirrors; document MCP as client-specific; enforce these contracts, skill schema, SHA-256 parity, and a 7,600-character aggregate startup cap in the standard-library validator.

Consequences: The earlier decision naming `.cline/skills/` canonical is superseded. Cross-agent parity is testable without adding dependencies or startup context. Native hooks, MCP activation files, and subagents remain deferred and optional.

Related files: `GEMINI.md`, `CLAUDE.md`, `.codex/AGENTS.md`, `.agents/skills/`, `.claude/skills/`, `.cline/skills/`, `docs/agent-compatibility.md`, `scripts/check-template.py`

### 2026-05-09 — Add cross-model continuity layer

Status: Accepted

Context: User runs Gemini Ultra (Antigravity), Claude Teams, ChatGPT Teams, and OpenRouter free models on the same project. The Memory Bank had no contract for handing off mid-task between models.

Decision: Add `memory-bank/handoff.md` as a single rolling handoff pointer with a fixed schema, plus `workflows/handoff.md` for write/read procedure. AGENTS.md startup path includes handoff as step 3. FAST_INIT update list includes `handoff.md`.

Consequences: Any model can resume work from another model's stopping point in one extra small read. `handoff.md` is volatile; durable knowledge still lives in `activeContext.md`/`progress.md`.

Related files: `AGENTS.md`, `memory-bank/handoff.md`, `memory-bank/00-index.md`, `memory-bank/startup.md`, `workflows/handoff.md`

### 2026-05-09 — Add per-model context budgets and cache-stable file list

Status: Accepted

Context: One global FAST_INIT was too coarse for the mix of large-context (Gemini 1M), cache-friendly (Claude 200K), small-context (OpenRouter free), and turn-sensitive (ChatGPT 128K) models.

Decision: Rewrite `memory-bank/model-routing.md` with per-model budgets/tactics, a cache-stable file list (so Claude prompt-cache hits stay warm), Antigravity sub-agent notes, and concrete current defaults.

Consequences: Each model can be used near-optimally without changing the template. Avoids editing cache-stable files casually.

Related files: `memory-bank/model-routing.md`

### 2026-05-09 — Add Copilot, Cursor, and Codex adapters

Status: Accepted

Context: AGENTS.md is the canonical file across the OpenAI/Cursor agents standard, but additional ecosystems benefit from explicit one-line pointer files.

Decision: Add `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, and `.codex/AGENTS.md` as thin adapters. Validator enforces all adapters reference `AGENTS.md`.

Consequences: Copilot, Cursor, and Codex CLI/sub-agents pick up canonical rules natively. No new dependencies.

Related files: `.github/copilot-instructions.md`, `.cursor/rules/agents.mdc`, `.codex/AGENTS.md`, `scripts/check-template.py`

### 2026-05-09 — Enforce zero drift between mirrored workflows and skills

Status: Accepted

Context: `workflows/`, `.clinerules/workflows/`, and `.agents/workflows/` had drifted in places. Same risk for skills.

Decision: Use `workflows/` as canonical for workflows and `.cline/skills/` as canonical for skills. Synced all mirrors. Validator computes SHA-256 hashes and fails on any drift in full-mode.

Consequences: Tool-specific paths preserved; drift impossible without test failure.

Related files: `scripts/check-template.py`, `workflows/`, `.clinerules/workflows/`, `.agents/workflows/`, `.cline/skills/`, `.agents/skills/`

### 2026-05-09 — Add token benchmark to validator and bootstrap

Status: Accepted

Context: The improvement brief asked for a measurable startup-path size metric. Users need a single command to see "what does FAST_INIT cost me" in chars/tokens.

Decision: Add `python scripts/check-template.py --benchmark` and include benchmark output in `scripts/init-fast.py`. Uses chars/4 heuristic.

Consequences: Token cost visible in 1 command without external libraries. Heuristic is approximate but stable across runs and models.

Related files: `scripts/check-template.py`, `scripts/init-fast.py`

### 2026-05-07 — Adopt balanced initialization model (FAST_INIT default, DEEP_AUDIT explicit)

Status: Accepted

Context: Initialization on copied projects consumed excessive tokens when agents interpreted broad prompts as permission for deep repository inspection.

Decision: Add explicit initialization modes in `AGENTS.md`, make `FAST_INIT` the default for low-token initialization, define strict read/update boundaries, and reserve `DEEP_AUDIT` for explicit full-review requests or verified escalation needs.

Consequences: Multi-agent support remains intact while default initialization becomes significantly cheaper and more predictable. Deep inspection remains available when required.

Related files: `AGENTS.md`, `README.md`, `workflows/init-lite.md`, `memory-bank/model-routing.md`, `memory-bank/startup.md`, `memory-bank/systemPatterns.md`

### 2026-05-07 — Add optional fast validator mode for FAST_INIT workflows

Status: Accepted

Context: Full template validation is valuable for publish readiness but heavier than needed during routine low-token initialization workflows.

Decision: Add `--fast` mode to `scripts/check-template.py` that validates core startup/integration requirements, adapter pointers, context budgets, and required `.gitignore` patterns while skipping repository-wide secret hygiene scanning.

Consequences: Maintainers can run cheap validation during FAST_INIT-style work, while preserving full validation for release/publication checks.

Related files: `scripts/check-template.py`, `README.md`, `memory-bank/techContext.md`, `memory-bank/progress.md`, `memory-bank/activeContext.md`

### 2026-05-07 — Add one-command FAST_INIT bootstrap helper

Status: Accepted

Context: Even with improved policies, users still needed to run a command and manually copy a longer initialization prompt.

Decision: Add `scripts/init-fast.py` to run `check-template.py --fast` and print a concise ready-to-paste FAST_INIT prompt for new context windows.

Consequences: Fresh-start initialization is faster and easier, reducing user friction and accidental prompt drift.

Related files: `scripts/init-fast.py`, `README.md`, `scripts/README.md`, `memory-bank/techContext.md`, `memory-bank/progress.md`, `memory-bank/activeContext.md`

### 2026-05-07 — Initialize copied repository as template baseline before product specialization

Status: Accepted

Context: This repository was initialized from the master AI Agent Project Template and required Memory Bank grounding with accurate current facts.

Decision: Treat the current repository state as a template-baseline project (not yet product-specialized), update Memory Bank files with verified template facts, and keep unknown product-specific details as `TBD` until requirements are provided.

Consequences: Agents can work immediately with accurate operational context while avoiding invented product assumptions; next planning step must define actual product scope and stack.

Related files: `memory-bank/projectbrief.md`, `memory-bank/productContext.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`

### 2026-05-06 — Optimize startup context with lazy loading

Status: Accepted

Context: The initial `AGENTS.md` and Memory Bank startup files used too much context before agents reached project source files.

Decision: Keep `AGENTS.md` compact, add `memory-bank/startup.md`, and lazy-load all deeper docs, workflows, skills, and Memory Bank files only when relevant.

Consequences: First-start overhead is much smaller, preserving context for actual project code.

Related files: `AGENTS.md`, `memory-bank/startup.md`, `memory-bank/00-index.md`, `scripts/check-template.py`

### 2026-05-06 — Distill Karpathy-style engineering behavior into a small skill

Status: Accepted

Context: Karpathy-style guidance is useful but too verbose to embed in full startup context.

Decision: Put the four core principles in `AGENTS.md` and add `karpathy-engineer` as a concise optional skill for coding/debugging/refactoring.

Consequences: Agents get better engineering defaults without large prompt overhead.

Related files: `AGENTS.md`, `.cline/skills/karpathy-engineer/SKILL.md`, `.agents/skills/karpathy-engineer/SKILL.md`

### 2026-05-06 — Use AGENTS.md as canonical instruction file

Status: Accepted

Context: The previous template used `GEMINI.md` as the main command file and `ops/`, `resources/`, and `env/` as the primary structure.

Decision: Use `AGENTS.md` as the single model-agnostic instruction file. Keep `GEMINI.md`, `CLAUDE.md`, `.clinerules/`, and `.agents/rules/` as thin adapters.

Consequences: Cline, Google Antigravity, Gemini, Claude, Codex/OpenAI-style agents, and OpenRouter-backed workflows can share one consistent source of truth.

Related files: `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `.clinerules/00-master.md`, `.agents/rules/00-master.md`

### 2026-05-06 — Replace legacy ops/resources/env structure

Status: Accepted

Context: The previous structure was useful but narrowly framed around Python resources, ops documents, and a committed `env/` folder.

Decision: Use `workflows/`, `scripts/`, `.mcp/`, `.env.example`, `.gitignore`, and `.clineignore` instead.

Consequences: The template is more conventional, stack-agnostic, safer for secrets, and easier for multiple coding agents to understand.

Related files: `workflows/`, `scripts/`, `.mcp/`, `.env.example`, `.gitignore`, `.clineignore`

### 2026-09-05 — Enforce repository boundaries at the tool boundary, not in prose

Status: Accepted

Context: `AGENTS.md` forbade publishing without explicit human instruction, but
`docs/agent-loop.md`, `CONVENTIONS.md`, and `workflows/implement-task.md` (plus
both mirrors) instructed the agent to `git push` on phase/milestone completion.
Lazy-loading any of those files told the agent to do exactly what the canonical
rule forbids. In a derived project that has not run `scripts/detach-remote.py`,
that transmits to the shared template remote — the failure the template calls
unrecoverable for confidential work.

Decision: Align all five files with `AGENTS.md`, and add
`scripts/hooks/guard-remote-ops.py` as a `PreToolUse` denial for publishing
commands. Keep the prose rule and the `.claude/settings.json` deny list as
independent layers.

Consequences: The rule now holds even if an agent skips, misreads, or compacts
away the instruction. The guard parses commands (token-walk over shell
segments, heredoc bodies stripped) rather than pattern-matching, so
`git -C dir push` is caught while `git log --grep=push` and commit messages
mentioning the verb are not. It is defense in depth, not a sandbox: a
sufficiently indirect invocation can still evade it, which is why the other two
layers remain.

Related files: `scripts/hooks/guard-remote-ops.py`, `.claude/settings.json`,
`docs/agent-loop.md`, `CONVENTIONS.md`, `workflows/implement-task.md`

### 2026-09-05 — Make FAST_INIT deterministic via SessionStart

Status: Accepted

Context: The startup path depended on the model choosing to read
`memory-bank/startup.md`. Anthropic's context-engineering guidance favors
just-in-time retrieval plus structured note-taking persisted outside the
context window; the template had the files but no mechanism.

Decision: Add `scripts/hooks/session-context.py`. `SessionStart` injects the
startup path (plus `handoff.md` when resuming); `PreCompact` reminds the agent
to flush durable state before the transcript is summarized away.

Consequences: Startup context is loaded without spending model reasoning on
remembering to do it, and continuity survives compaction. Injection is
size-capped (4k/file, 8k total) so it cannot defeat the FAST_INIT budget. The
hooks are Claude-only today; the prose instructions remain the portable
fallback and were not removed.

Related files: `scripts/hooks/session-context.py`, `.claude/settings.json`,
`docs/hooks.md`

### 2026-09-05 — Reject OmniRoute; three of four circulated plugins already covered

Status: Accepted

Context: A social post recommended four plugins. All four are real and their
star counts verified against the GitHub API on 2026-09-05.

Decision: Do not adopt OmniRoute — it is a gateway that routes prompts and code
through a third-party endpoint ("150+ free" providers) and bundles Caveman
compression the catalog already flags as possibly net-negative. Ponytail
duplicates the existing `karpathy-engineer` doctrine. Graphify was already
catalogued; recorded the verified caveat that docs/PDFs/images are sent to a
model even though code is parsed locally. `addyosmani/agent-skills` is the best
fit but should be cherry-picked, not bulk-installed, to avoid duplicating the
seven shipped skills.

Consequences: Quota failover stays with `memory-bank/model-routing.md`.
Confidential work is not routed through third-party inference.

Related files: `docs/third-party-integrations.md`

### 2026-09-05 — Ship `.rules` for Zed; no adapter for Amp, opencode, or Warp

Status: Accepted

Context: A prior research note (`tmp/deep_research_claude.md.md`) listed Amp,
opencode, Zed, and Warp as missing adapters. First-party documentation checked
2026-09-05 shows Amp, opencode, and Warp read root `AGENTS.md` natively, so
adapters for them would be noise. Zed does support `AGENTS.md`, but resolves
project instructions **first match wins** over `.rules`, `.cursorrules`,
`.windsurfrules`, `.clinerules`, `.github/copilot-instructions.md`, `AGENT.md`,
`AGENTS.md`, ... This template ships three filenames that outrank `AGENTS.md`,
so Zed stopped at `.windsurfrules` and never read the canonical file.

Decision: Ship `.rules` — Zed's highest-priority filename — as a pointer to
`AGENTS.md`. Add no adapter for Amp, opencode, or Warp. Record all four in
`docs/agent-compatibility.md` with sources.

Consequences: Zed resolution is deterministic in one hop. The template stays at
the smallest adapter set that is actually required. This also surfaced a
property worth keeping: because every adapter is a pointer naming `AGENTS.md`,
a shadowed resolution still redirects to the canonical file — an adapter
carrying independent policy would silently fork the rules. The validator's
existing "every adapter must name AGENTS.md" check is what preserves that.

Related files: `.rules`, `docs/agent-compatibility.md`,
`scripts/check-template.py`, `README.md`

### 2026-10-03 — Audit fixes: MCP off by default, git-level push backstop, schema-validated subagent contract, Context Compiler

Status: Accepted

Context: An adversarial architectural audit found the shipped git MCP server exposes `git_push` outside the PreToolUse matchers (a one-call boundary bypass); `guard-remote-ops.py` was defeated by `git send-pack`, `gh api` write calls, and interpreter/code-runner indirection; the sensitive-path guard ignored shell redirection targets; clients without hook runtimes (Cline, Roo Code, Cursor, Copilot, Windsurf) had no enforcement layer; and the subagent contract was unvalidatable free text with no context isolation, output caps, or write-scope audit.

Decision: Remove all active MCP configs (opt-in via the `.mcp/` catalog with documented security rationale); harden both guards and register the sensitive-path guard on shell matchers; add an agent-aware POSIX sh `pre-push` hook at the git layer (env-marker detection, template-upstream deny, `ALLOW_AGENT_PUSH` escape hatch, never clobbering detach-remote's stronger block); replace the free-text subagent envelopes with machine-validated JSON schemas enforced in CI; add `scripts/ctx.py`, a deterministic budget-capped Context Compiler over typed `memory-bank/records/`.

Consequences: The publishing boundary now holds across all clients at the git layer; delegation is validated, isolated, and context-bounded; startup context becomes a reproducible, cache-stable artifact. Trade-off accepted: fail-closed code-runner scans deny harmless one-liners that merely mention `git push` in interpreted code strings.

Related files: `scripts/hooks/guard-remote-ops.py`, `scripts/hooks/guard-sensitive-paths.py`, `scripts/hooks/git/pre-push`, `schemas/`, `scripts/validate-schemas.py`, `scripts/ctx.py`, `docs/hooks.md`, `docs/subagent-contract.md`, `docs/context-compiler.md`

## Decision template

### YYYY-MM-DD — Decision title

Status: Proposed / Accepted / Rejected / Superseded

Context:

Decision:

Consequences:

Related files:
