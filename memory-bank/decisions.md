# Decisions

Record important project decisions here.

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

## Decision template

### YYYY-MM-DD — Decision title

Status: Proposed / Accepted / Rejected / Superseded

Context:

Decision:

Consequences:

Related files: