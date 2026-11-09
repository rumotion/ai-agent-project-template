# Workflow: Bootstrap Context (Peanuts & Hay)

Generate or refresh bottom-up directory context contracts (`README.md` or `CONTEXT.md`) across a repository or subtree so sessions can navigate module boundaries, invariants, and side effects without loading raw source code into startup context. See `docs/peanuts-and-hay.md` for templates and the Re-Implementation Standard.

## When to use

- Onboarding an agent onto an existing multi-directory codebase.
- After adding a new subsystem or package whose boundaries are not yet indexed.
- When agents repeatedly grep or read large source files just to discover public interfaces and test commands.

## Steps

1. **Choose Target & Contract Filename**:
   - Confirm target root `path` (default: repository source root, e.g. `src/` or `.`) and `target_filename` (`README.md` by default, or `CONTEXT.md` when human-facing `README.md` files must not be modified).
   - Inspect root manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`) to determine the default `VerificationCommand`.
2. **Incremental BFS Discovery & Safety Gate**:
   - List directories level-by-level (skipping `.git`, `.venv`, `venv`, `node_modules`, `dist`, `build`, `__pycache__`, `.agent-logs`).
   - **Mandatory Safety Gate**: If more than 15 directories require contracts, stop and ask the user to approve full-tree execution or narrow the scope before writing files or spawning subagents.
3. **Bottom-Up Extraction (Leaf "Peanuts" First)**:
   - For each leaf directory containing source files, inspect its public exports/interfaces, state invariants, external side effects (DB, network, disk, locks), and test command.
   - Exclude private helpers, loop syntax, and internal variables (Zero-Assumption / Re-Implementation Standard).
   - Write `<dir>/<target_filename>` using the **Peanuts** template in `docs/peanuts-and-hay.md`. Preserve existing human titles/introductory notes when updating an existing file.
4. **Roll Up Parent & Root Blueprints ("Hay")**:
   - Move bottom-up through intermediate directories and the target root, summarizing child contracts and linking each child via a valid relative path (`./<subdir>/<target_filename>`).
5. **Ground-Truth & Link Audit**:
   - Re-read every created or modified contract file. Verify that:
     - every cited symbol, route, flag, or table exists in the code;
     - every relative link resolves to an existing file on disk;
     - zero functional source files were modified (`git status --short`).
6. **Optional Index & Drift Check**:
   - Reference the root blueprint in `memory-bank/00-index.md` or `memory-bank/systemPatterns.md` if appropriate, and offer to run `workflows/drift-report.md` to verify zero doc-to-code divergence.
