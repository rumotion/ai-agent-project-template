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

See `docs/use-from-github.md` for details, including when to keep or change the Git remote.

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

Run validation:

```bash
python scripts/check-template.py
```

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

## 5. Start with the low-context initialization prompt

Use this prompt first:

```text
Read AGENTS.md and memory-bank/startup.md only.

I am starting a new project from this template.

Project idea:
[describe the app, website, tool, or service you want]

Please inspect the empty/new repository, ask me any critical questions, then propose:
1. recommended stack,
2. initial folder structure,
3. setup commands,
4. first implementation plan,
5. Memory Bank updates needed.

Do not install dependencies or create files yet. Plan first.
```

Example:

```text
Read AGENTS.md and memory-bank/startup.md only.

I am starting a new project from this template.

Project idea:
A portfolio website for a 3D motion designer with a homepage, project gallery, about page, contact form, and CMS-ready project data.

Please inspect the empty/new repository, ask me any critical questions, then propose:
1. recommended stack,
2. initial folder structure,
3. setup commands,
4. first implementation plan,
5. Memory Bank updates needed.

Do not install dependencies or create files yet. Plan first.
```

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

## 8. Optional: initialize Git

If this is a new local folder that is not already a Git repo:

```bash
git init
git add .
git commit -m "Initial project from AI-agent template"
git checkout -b feature/app-foundation
```

Do not copy an old `.git/` directory into a public starter unless you intentionally want its history and remote URLs.

If you cloned the public template directly and want this to become your own independent GitHub project, create a new GitHub repo and then update the remote:

```bash
git remote set-url origin https://github.com/<your-owner>/<your-new-repo>.git
git push -u origin main
```

Before pushing publicly, run:

```bash
python scripts/check-template.py
```

## 9. Work feature by feature

For each feature, use this pattern:

```text
Read AGENTS.md and memory-bank/startup.md only.

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

## Key rule

Most tasks should start with:

```text
Read AGENTS.md and memory-bank/startup.md only.
```

This keeps context small. The agent should load deeper files only when needed.