# Start a New Project from This Template

Use this guide when you have an empty folder and want to create a new app, website, tool, or service from scratch.

This guide is intentionally outside the default startup path. Agents should read it only when a user asks how to begin a new project.

## 1. Get the template

Recommended GitHub path:

1. Open the public template repository on GitHub.
2. Click **Use this template**.
3. Create a new repository under your own account or organization.
4. Clone your new repository locally.

Alternative paths:

- `git clone https://github.com/<owner>/<repo>.git my-new-project`
- GitHub **Code > Download ZIP** if you want files without Git history.
- Local folder copy if you already have the template on disk.

See `docs/use-from-github.md` for details. **Important**: If cloning the template directly, the folder inherits the template's Git remotes. Run `python scripts/init-fast.py` to automatically detach the template remote and secure repository boundaries.

## 2. Check the template files

Create or open your new project folder, then copy this template's contents into it.

Your folder should contain files like:

```text
AGENTS.md
README.md
GEMINI.md
CLAUDE.md
memory-bank/
docs/
references/
assets/
workflows/
scripts/
.clinerules/
.cline/
.agents/
.mcp/
.gitignore
.clineignore
.env.example
```

Do not start by writing app code manually. First let the agent initialize project context.

Run fast bootstrap first:

```bash
python scripts/init-fast.py
```

This command:

1. detaches inherited template remotes and installs a pre-push block to keep the project local-only,
2. runs `python scripts/check-template.py --fast`, and
3. prints a short FAST_INIT prompt to paste into a new agent context window.

Use full validation (`python scripts/check-template.py`) when you need deep/publish checks.

## 3. Add starting resources, if you have them

For detailed guidance, see `docs/file-organization.md`.

- Put research PDFs, briefs, transcripts, text notes, and reference-only images in `references/`.
- Put source project assets such as images, logos, and content data in `assets/`.
- Put final runtime website/app files in `public/` or `src/assets/` only after the chosen stack creates those conventions.
- Keep durable project facts in `memory-bank/` and human-facing documentation in `docs/`.
- Do not commit private, licensed, secret, or very large files unless you explicitly intend to.

Example:

```text
references/docs/project-brief.pdf
references/media/inspiration-screenshot.png
assets/images/hero-source.png
assets/data/projects.json
```

## 4. Open the folder in your IDE

Open the new folder in Google Antigravity, VS Code, or another compatible IDE.

Configure your agent/model path:

- Cline: choose OpenRouter, OpenAI API, Anthropic, Gemini, or another supported provider.
- Google Antigravity: use the native agent/Gemini setup.
- VS Code OpenAI/Codex-style usage: use the official extension/sign-in or API-key path where supported, then point it at `AGENTS.md` as the canonical instruction file.
- ChatGPT subscription/Codex-style usage: use the official OpenAI/Codex IDE sign-in path where supported.

The template works regardless of provider. Provider choice affects billing/auth, not the template structure.
Keep provider credentials in your IDE, OS keychain, shell environment, or local `.env` files that are ignored by Git. Do not commit real keys or tokens.

## 5. Start with the FAST_INIT prompt

The easiest path is to run:

```bash
python scripts/init-fast.py
```

Then copy the printed prompt into a new context window.

If you want to paste manually, use:

```text
FAST_INIT + TOKEN_SAVER.
Follow AGENTS.md initialization modes exactly.
Use minimal turns and minimal narration.
Update only allowed Memory Bank files.
If resuming, also read memory-bank/handoff.md.
Keep unknowns as TBD.
Ask only critical questions before any escalation.
Return a short final summary.
```

**Switching models mid-project?** Update `memory-bank/handoff.md` first so the next model picks up cleanly. The protocol is in `workflows/handoff.md`.

## 6. Choose the stack

Common defaults:

| Project type | Good starting point |
|---|---|
| Simple website | Vite + React + TypeScript |
| Production website/app | Next.js + TypeScript |
| Dashboard/admin app | Next.js + TypeScript + Tailwind |
| Backend API | FastAPI, Fastify, .NET, or another appropriate backend |
| Full-stack app | Next.js plus selected database/auth/provider |

Example reply:

```text
Use Vite + React + TypeScript + Tailwind. Keep it simple and modern.
```

or:

```text
Use Next.js + TypeScript. I want this to become a production website later.
```

## 7. Approve implementation

After the plan looks good, tell the agent:

```text
Proceed with the approved plan. Create the app foundation, keep changes small, update the Memory Bank, and run the smallest useful verification command.
```

The agent should then:

1. create app files,
2. install dependencies only after approval,
3. set up the folder structure,
4. update relevant Memory Bank files,
5. run validation/build checks.

## 8. Git and Publishing Boundaries
 
All projects created from this template are **local-only by default**.
 
If this is a new local folder that is not already a Git repo:

```bash
git init
git add .
git commit -m "Initial project from AI-agent template"
git checkout -b feature/app-foundation
```

If you cloned the template directly, `python scripts/init-fast.py` (or `python scripts/detach-remote.py`) automatically removes inherited remotes and installs `.git/hooks/pre-push` to block accidental upstream pushes to the template.

When you are ready to publish the project to your own independent Git repository:

1. Create a NEW repository under your personal or organization account (never share the template repository).
2. Add your new remote:
   ```bash
   git remote add origin https://github.com/<your-owner>/<your-new-repo>.git
   ```
3. Remove the local pre-push block hook:
   ```bash
   rm .git/hooks/pre-push
   ```
4. Run validation before publishing:
   ```bash
   python scripts/check-template.py
   ```
5. Push to your repository:
   ```bash
   git push -u origin main
   ```

> [!CAUTION]
> Never point a project at the shared template repository, and never run `git push --force --mirror`. Confidential material must never enter a repository that is or ever was public.

## 9. Work feature by feature

For each feature, use this pattern:

```text
FAST_INIT + TOKEN_SAVER.

Follow AGENTS.md initialization modes exactly.
Use minimal turns and minimal narration.

Task:
[describe the feature or bug]

Inspect only relevant files, make a concise plan, then implement after approval. Keep changes small and update only relevant Memory Bank files.
```

Examples:

```text
Task: Add a responsive navigation bar with desktop and mobile menus.
```

```text
Task: Add a project gallery page that reads project data from a local JSON file.
```

```text
Task: Add a contact form UI. Do not connect backend/email yet.
```

## 10. Advanced: Parallelizing with Forking

Since this template uses an external `memory-bank/` instead of relying on in-chat history, you can "fork" conversations to run parallel agents on the same project:

1. Update `memory-bank/handoff.md` and `memory-bank/activeContext.md` in your current session.
2. Open a *new* agent context window in your IDE or a separate terminal.
3. Use the FAST_INIT prompt to start the new agent on a different sub-task.
4. Because the context is centralized in the files, both agents share the same project background without needing manual synchronization.

## Key rule

Most tasks should start with:

```text
FAST_INIT + TOKEN_SAVER.
```

This keeps context small. The agent should load deeper files only when needed.