# Peanuts and Hay: Bottom-Up Codebase Context Contracts

Adapted from the **Elephant-Goldfish Model (EGM)** (`google/elephant-goldfish-model`), the **Peanuts and Hay** hierarchy gives coding agents ("Elephants") a compact, verified map of an existing or growing codebase without loading raw source files during startup.

## Core Concept

- **Peanuts (Leaf Component Contracts)**: Concise package/directory contract files (`README.md`, or `CONTEXT.md` when human-facing `README.md` files must remain untouched) that document *only* observable module boundaries.
- **Hay (Parent & Root Blueprints)**: High-altitude index files that roll up child contracts into subsystem boundaries and global invariants.

Together with `memory-bank/00-index.md`, this hierarchy lets an agent locate the right module in 1-2 file reads while preserving the strict `FAST_INIT` token budget.

---

## The Re-Implementation Standard (Zero-Assumption Rule)

A component contract passes if a fresh engineer or isolated AI session ("Goldfish") can understand or re-implement functionally equivalent module behavior using the contract, without guessing parameter defaults, error handling, or hidden side effects.

- **Include**: Public interfaces (signatures, types, routes, CLI flags, exit codes), state/call invariants, external side effects (database writes, network calls, filesystem mutations, locks), and the exact verification command.
- **Exclude**: Internal syntax, loops, local variable names, and private helper functions.

---

## Templates

Replace `<target_filename>` in all templates below with `README.md` (default) or `CONTEXT.md` (when preserving existing human-facing `README.md` files). Keep `<target_filename>` consistent across parent and child links in the same tree.

### 1. Leaf Component Contract ("Peanuts")

```markdown
# <Component or Package Name>

## Overview
<1-3 sentences on the component's architectural responsibility.>

## Interface
- `<symbol / function / class / endpoint>` — <inputs, outputs, defaults, error/exit semantics, and contract>
- Subdirectories: [`<subdir>/`](./<subdir>/<target_filename>) — <relative links to child contracts, if any>

## Invariants
- <State, ordering, security, or concurrency invariant that callers and edits must preserve>

## Side Effects
- <Database, network, disk, process, environment, or lock side effects; or "None (pure)">

## Verification
- Run: `<smallest deterministic test command>`
```

### 2. Intermediate Directory Blueprint

```markdown
# <Directory Name>

## Overview
<Factual summary of the subsystem grouped under this directory.>

## Subdirectories & Boundaries
- [`<subdir>/`](./<subdir>/<target_filename>) — <1-line summary of child contract and role>
```

### 3. Repository or Subsystem Root Blueprint ("Hay")

```markdown
# <Project or Subsystem Name> Blueprint

## System Overview
<High-altitude architectural overview and data flow.>

## Subdirectories & System Boundaries
- [`<subdir>/`](./<subdir>/<target_filename>) — <Summary of child contract and boundary>

## Global Invariants
- <Cross-cutting constraints spanning multiple components>

## Global Side Effects
- <Shared databases, external APIs, queues, or storage backends>

## System Verification
- Run: `<repository test or validation command>`
```

---

## Execution & Safety Rules

When running `workflows/bootstrap-context.md`:

1. **Documentation-Only Scope**: Never modify functional source code, configs, or dependencies while bootstrapping context contracts.
2. **Incremental BFS Discovery**: Traverse directories level-by-level (BFS), ignoring `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `__pycache__`, and `.agent-logs`. Never run unbounded recursive dumps (`find .` or `ls -R`) on an uninspected tree.
3. **Subdirectory Safety Gate**: If discovery finds more than 15 target directories, pause and ask the user to confirm full-tree generation or narrow the target path before spawning workers or writing files.
4. **Contract Grounding & Link Verification**: Every symbol, invariant, side effect, and relative link (`./<subdir>/<target_filename>`) must be verified against the actual filesystem and source files before completion.
5. **Drift Monitoring**: Pair with `workflows/drift-report.md` to detect when code changes diverge from checked-in contracts or specifications.
