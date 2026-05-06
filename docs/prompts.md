# Prompts

First-time setup guide: `docs/start-new-project.md`.

## Initialize a copied project

```text
Initialize this project from the master agent template. Read AGENTS.md and memory-bank/startup.md first. Inspect the repository, fill Memory Bank files with accurate facts, keep unknowns as TBD, and propose project-specific rules, skills, workflows, or ignore patterns only if useful.
```

## Initialize a project created from GitHub

```text
Read AGENTS.md and memory-bank/startup.md only.

I created this project from the public AI Agent Project Template using GitHub template/clone/download.

Project idea:
[describe the app, website, tool, or service]

Please inspect the repository, ask critical questions, then propose:
1. recommended stack,
2. initial folder structure,
3. setup commands,
4. first implementation plan,
5. Memory Bank updates needed.

Do not install dependencies or create app files yet. Plan first.
```

For the full Google Antigravity/Cline/ChatGPT Team initialization prompt, see `docs/antigravity-master-prompt.md`.

## Start a low-context task

```text
Read AGENTS.md and memory-bank/startup.md only. Then inspect only the files required for this task:
[task description]
```

## Start a task

```text
Read AGENTS.md and the Memory Bank first, then plan this task:
[task description]
```

## Update memory

```text
Update the Memory Bank based on this task. Keep updates concise and only change relevant files.
```