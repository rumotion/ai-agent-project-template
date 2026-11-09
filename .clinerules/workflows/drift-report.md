# Workflow: Drift Report (Spec & Context vs. Code)

Compare checked-in design specifications, `Peanuts & Hay` module contracts (`docs/peanuts-and-hay.md`), and Memory Bank architecture docs (`memory-bank/systemPatterns.md`, `memory-bank/techContext.md`) against current source code to catch silent divergence. Adapted from the Elephant-Goldfish Model (`egm-drift-report`).

## When to use

- After implementing a multi-step feature or refactor against a specification.
- Periodically (e.g. weekly or before a milestone release) to prevent documentation rot.
- After running `workflows/bootstrap-context.md` to verify that generated module contracts match the code.

## Rules

- **Read-Only Audit First**: Do not silently edit production code or documentation during the scan. Produce the drift report first so the human (or an explicitly authorized follow-up task) decides whether to update the doc or fix the code.
- **Signal Only**: Report **only discrepancies**. Do not list features or files that match. If a document matches the codebase completely, output `No drift detected.` for that document.

## Steps

1. **Identify Target Documents**:
   - Use the user-specified directory/files, or default to active specs (`docs/`), module contracts (`README.md` / `CONTEXT.md`), and `memory-bank/systemPatterns.md` + `memory-bank/techContext.md`.
2. **Sequential Document-to-Code Verification**:
   - Process target documents sequentially so tool output buffers stay small:
     a. **Extract Claims**: Read the document and list concrete file paths, public symbols/functions, data models/schemas, invariants, CLI flags, and verification commands.
     b. **Locate & Read Source**: Use search (`grep`/`rg` or glob) and file reads to inspect the current implementation in the working tree. Never rely on chat memory.
     c. **Classify Divergences**: Check for four drift categories:
        - **Missing Features**: Behavior, endpoints, or commands described in the doc but absent in the code.
        - **Incomplete Models**: Classes, structs, schemas, or JSON envelopes missing documented fields or constraints.
        - **Logic Shortcuts**: Hardcoded values, skipped validations, or stubbed paths where dynamic logic was specified.
        - **Architectural Divergence**: Implementation using different libraries, boundaries, ownership rules, or side effects than documented (or undocumented public exports in a module contract).
3. **Emit Structured Report**:
   - Write findings to a workspace report file (or present concisely if small) using this exact structure:
     ```markdown
     # Drift Report — <YYYY-MM-DD>

     ## `<document-path>`
     - **[Missing Feature | Incomplete Model | Logic Shortcut | Architectural Divergence]** `<symbol or path>`: <concise evidence of doc claim vs. actual code at `file:line`>
     <!-- Or: No drift detected. -->
     ```
4. **Resolution Gate**:
   - Ask whether each reported divergence should be resolved by updating the documentation/Memory Bank (`docs-memory-maintainer`) or by scheduling a code fix (`workflows/implement-task.md`).
