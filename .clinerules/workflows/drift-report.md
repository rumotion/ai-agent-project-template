# Workflow: Drift Report (Spec & Context vs. Code)

Compare checked-in design specifications, `Peanuts & Hay` module contracts (`docs/peanuts-and-hay.md`), and Memory Bank architecture docs (`memory-bank/systemPatterns.md`, `memory-bank/techContext.md`) against current source code to catch silent divergence. Adapted from the Elephant-Goldfish Model (`egm-drift-report`).

## When to use

- After implementing a multi-step feature or refactor against a specification.
- Periodically (e.g. weekly or before a milestone release) to prevent documentation rot.
- After running `workflows/bootstrap-context.md` to verify that generated module contracts match the code.

## Rules

- **Read-Only Audit First**: Do not create or edit tracked repository files (source code or documentation) during the scan. Present the drift report in chat first (or write to a repository file only when the user explicitly requests saving it) so the human or an authorized follow-up task decides whether to update the doc or fix the code.
- **Static Verification Check**: Do not execute `Verification` commands during the audit. Treat one as non-functional only when its entry point, referenced paths, or flags do not exist in the working tree; run it only if the user explicitly asks.
- **Signal Only**: Report **only discrepancies**. Do not list features or files that match. If a document matches the codebase completely, output `No drift detected.` for that document.

## Steps

1. **Identify Target Documents & Scope Gate**:
   - If the user specifies target files or directories, audit only those paths.
   - If no path is provided, default to the bounded baseline set: `memory-bank/systemPatterns.md`, `memory-bank/techContext.md`, and the module contracts (`README.md` or `CONTEXT.md`) at the repository root and in its first-level directories. A file counts as a contract only if it follows the `Peanuts & Hay` section structure; skip human-facing `README.md` files that do not.
   - **Scope Safety Gate**: If target resolution exceeds 10 documents (for example, auditing all of `docs/` plus nested contracts), pause and ask the user to confirm full-scan execution or narrow the target path before reading source trees.
2. **Sequential Document-to-Code Verification**:
   - Process target documents sequentially so tool output buffers stay small:
     a. **Extract Claims**: Read the document and list concrete file paths, public `Interface` symbols/functions, data models/schemas, CLI flags/exit codes, `Invariants`, `Side Effects`, and `Verification` commands.
     b. **Locate & Read Source**: Use search (`grep`/`rg` or glob) and file reads to inspect the current implementation in the working tree. Never rely on chat memory.
     c. **Classify Divergences**: Map every discrepancy (including `Peanuts & Hay` contract sections) into one of four drift categories:
        - **Missing Features**: Documented public `Interface` symbols, endpoints, CLI flags, or `Verification` commands that are absent or non-functional in the code.
        - **Incomplete Models**: Classes, structs, schemas, CLI exit codes, or JSON envelopes missing documented fields, defaults, or type constraints.
        - **Logic Shortcuts**: Broken or unimplemented `Invariants` (state, ordering, security, or concurrency rules), hardcoded values, skipped validations, or stubbed paths where dynamic enforcement was specified.
        - **Architectural Divergence**: Undocumented or mismatched `Side Effects` (database writes, network calls, filesystem mutations, environment reads, locks), undocumented public exports in a module contract, or implementation using different libraries/boundaries than documented.
3. **Emit Structured Report**:
   - Output the findings directly in chat by default (or write to `docs/audits/drift-report-<YYYY-MM-DD>.md` only if the user explicitly asks to persist the report file) using this exact structure:
     ```markdown
     # Drift Report — <YYYY-MM-DD>

     ## `<document-path>`
     - **[Missing Feature | Incomplete Model | Logic Shortcut | Architectural Divergence]** `<symbol or path>`: <concise evidence of doc claim vs. actual code at `file:line`>
     <!-- Or: No drift detected. -->
     ```
4. **Resolution Gate**:
   - Ask whether each reported divergence should be resolved by updating the documentation/Memory Bank (`docs-memory-maintainer`) or by scheduling a code fix (`workflows/implement-task.md`).
