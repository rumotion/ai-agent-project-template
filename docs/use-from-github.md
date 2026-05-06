# Use This Template from GitHub

This template can be used directly from a public GitHub repository. You do not need to copy the folder from disk.

## Best option: Use this template

If the repository is marked as a GitHub Template repository:

1. Open the template repository on GitHub.
2. Click **Use this template**.
3. Create a new repository under your own account or organization.
4. Clone your new repository locally.
5. Run validation:

   ```bash
   python scripts/check-template.py
   ```

6. Open the folder in VS Code, Google Antigravity, Cline, or another compatible IDE.
7. Ask your agent to initialize the copied project using `AGENTS.md` and `memory-bank/startup.md`.

This is the cleanest path because the new project gets its own repository without inheriting the template repository's Git history.

## Clone the template directly

Use this when you want a local copy of the template itself or want to branch from it:

```bash
git clone https://github.com/<owner>/<repo>.git my-new-project
cd my-new-project
python scripts/check-template.py
```

After cloning, decide whether this folder should remain connected to the template repository:

- Keep `origin` if you want to pull template updates.
- Change `origin` if this should become your own independent project repository.

To change the remote after creating your own GitHub repository:

```bash
git remote set-url origin https://github.com/<your-owner>/<your-new-repo>.git
git push -u origin main
```

## Download without Git history

Use GitHub's **Code > Download ZIP** option when you only want the files and do not want the template Git history.

After extracting:

```bash
cd my-new-project
git init
python scripts/check-template.py
```

Then create your first commit only after reviewing the files and initializing project-specific context.

## Advanced: pull into an existing project

Pulling or merging this template into an existing project is possible but riskier than starting from a template or clone.

Before merging into an existing project:

1. Commit or back up all existing work.
2. Review overlapping files such as `README.md`, `.gitignore`, `AGENTS.md`, and `docs/`.
3. Merge selectively rather than blindly overwriting project-specific files.

Example advanced flow:

```bash
git remote add template https://github.com/<owner>/<repo>.git
git fetch template
git checkout template/main -- AGENTS.md memory-bank docs workflows scripts
```

Adjust the file list for your project. Do not run broad checkout or merge commands unless you understand what will be overwritten.

## Are you ready after cloning?

After using **Use this template**, cloning, or downloading ZIP, the folder is ready for agent-assisted initialization when:

1. `python scripts/check-template.py` passes.
2. You open the folder in your IDE.
3. You give the agent a project idea and ask it to initialize the Memory Bank.

Start with this prompt:

```text
Read AGENTS.md and memory-bank/startup.md only.

I created this project from the public AI Agent Project Template.

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

## Publishing this template

For maintainers publishing this template:

1. Run `python scripts/check-template.py`.
2. Confirm no secrets, private files, or unintended `.git/` history are included.
3. Push to a public GitHub repository.
4. In GitHub repository settings, enable **Template repository** so users can create clean copies.
