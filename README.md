# AI Agent Project Template

A copyable starter template for projects developed with Cline, Google Antigravity, Gemini, Claude, ChatGPT/Codex-style agents, OpenRouter-backed models, and VS Code-compatible AI tooling.

## Design principle

`AGENTS.md` is the single canonical instruction file. Every adapter file points back to it so different models share one source of truth.

The default startup path is intentionally tiny: read `AGENTS.md`, then `memory-bank/startup.md`, then lazy-load only task-relevant context.

## Included systems

- Canonical model-agnostic instructions: `AGENTS.md`
- Tool adapters: `GEMINI.md`, `CLAUDE.md`, `.clinerules/`, `.agents/`
- Durable context: `memory-bank/`
- Low-context startup memory: `memory-bank/startup.md`
- Reusable procedures: `workflows/`
- Agent skills: `.cline/skills/`, `.agents/skills/`
- Documentation stubs: `docs/`
- Deterministic scripts: `scripts/`
- MCP placeholder config: `.mcp/`
- Reference/project asset folders: `references/` and `assets/`

## Tool compatibility

- Google Antigravity: start from `AGENTS.md`, then use `.agents/` rules, workflows, and skills only when relevant.
- VS Code OpenAI/Codex-style extensions: use the official extension/sign-in or API-key flow where supported, and point the agent at `AGENTS.md` as the canonical project instruction file.
- Cline, Gemini, Claude, and OpenRouter-backed tools: use their normal provider auth outside the repo; keep credentials in local environment settings, never in committed files.

## New project flow

For a beginner-friendly walkthrough, see `docs/start-new-project.md`.
For GitHub template, clone, ZIP download, and advanced pull/merge workflows, see `docs/use-from-github.md`.

1. Create a project from this template by using GitHub **Use this template**, cloning the repo, downloading ZIP, or copying the folder locally.
2. Initialize Git if desired:

   ```bash
   git init
   ```

3. Ask your agent:

   ```text
   Initialize this project from the master agent template. Read AGENTS.md and memory-bank/startup.md first. Inspect the repository, fill Memory Bank files with accurate facts, keep unknowns as TBD, and propose project-specific rules, skills, workflows, or ignore patterns only if useful.
   ```

4. Start work from a focused branch or task prompt.

## Use from GitHub

Recommended public workflow:

1. Mark this repository as a GitHub **Template repository**.
2. Users click **Use this template** to create their own clean repository.
3. They clone their new repository, run `python scripts/check-template.py`, then initialize project-specific Memory Bank files with their agent.

Direct `git clone` also works, but it keeps the template Git history and `origin` remote until the user changes it. Pulling this template into an existing project is advanced and should be done selectively after committing current work.

## Where to put project files

Use `docs/file-organization.md` for the full guide.

- Put research PDFs, text notes, briefs, transcripts, and reference-only images in `references/`.
- Put source project assets such as images and content data in `assets/`.
- Put runtime website/app files in the stack's standard folder, usually `public/` or `src/assets/`, after that stack exists.
- Put durable project facts and decisions in `memory-bank/`, not as raw reference dumps.
- Keep secrets, private files, and large generated outputs out of Git unless intentionally approved.

## Validation

Run:

```bash
python scripts/check-template.py
```

The validator checks required template files, confirms adapter files reference `AGENTS.md`, enforces startup/context size budgets, checks required ignore patterns, and scans template text for common public-repository secret hygiene issues.

Before publishing a copy publicly:

1. Run `python scripts/check-template.py`.
2. Confirm `.env` and local credential files are not tracked.
3. Do not copy another project's `.git/` directory unless you intentionally want its history and remotes.
4. Keep real provider API keys, OAuth tokens, MCP credentials, and deployment secrets outside the repository.

## Master prompt

Use `docs/antigravity-master-prompt.md` for the detailed Google Antigravity/Cline/ChatGPT Team initialization prompt.