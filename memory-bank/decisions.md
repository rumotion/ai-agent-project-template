# Decisions

Record important project decisions here.

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