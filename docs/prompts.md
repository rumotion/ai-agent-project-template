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

## Switch models / pause work

```text
We are pausing or switching to another model. Update memory-bank/handoff.md with: timestamp, model, branch, current task, last concrete action, next concrete step, files touched, blockers. Keep it under 30 lines. Do not append history; overwrite.
```

## Resume work

```text
Resume from where the previous session left off. Read AGENTS.md, memory-bank/startup.md, and memory-bank/handoff.md only. Verify branch and last action against git status, then continue from "Next concrete step".
```

## Calibrate (Continuous Self-Improvement)

```text
/calibrate
Review this completed session to identify my preferences, repeated corrections, and style. Update the appropriate Memory Bank files or `.clinerules`/`.agents/rules/` so that future interactions are automatically aligned with these needs.
```

## Align (Clarification & Intent Mapping)

```text
/align
Before taking any action or writing code, ask me 3-5 specific clarifying questions about my intent, constraints, and success criteria for this task. Wait for my answers before proceeding.
```

## Devil's Advocate (Critical Analysis)

```text
/devil
Take a contrarian view on the proposed plan. Highlight flaws, security risks, scalability issues, or UX problems that I might have overlooked. Be brutally honest and avoid "yes-man" behavior.
```

## Burst (Iterative Divergence)

```text
/burst
Generate 3 distinct, mutually exclusive approaches to solving this problem. Do not write the full implementation for any of them yet. Just present the high-level architecture and pros/cons for each so I can choose the best path.
```