# Use This Template from GitHub

This template can be used directly from a public GitHub repository. You do not need to copy the folder from disk.

## Best option: Use this template

If the repository is marked as a GitHub Template repository:

1. Open the template repository on GitHub.
2. Click **Use this template**.
3. Create a new repository under your own account or organization.
4. Clone your new repository locally.
5. Run fast bootstrap:

   ```bash
   python scripts/init-fast.py
   ```

   This runs `check-template.py --fast` and prints a short prompt for a new agent context window.

6. Open the folder in VS Code, Google Antigravity, Cline, or another compatible IDE.
7. Paste the printed FAST_INIT prompt into a new context window.

This is the cleanest path because the new project gets its own repository without inheriting the template repository's Git history.

## Clone the template directly

Use this when you want a local copy of the template:

```bash
git clone https://github.com/<owner>/<repo>.git my-new-project
cd my-new-project
python scripts/init-fast.py
```

`git clone` copies the remote configuration, so the new folder initially points at the **template's own repository**.

When you run `python scripts/init-fast.py` (or `python scripts/detach-remote.py`), it automatically secures the repository boundaries:

1. Removes inherited template remotes (`origin`, `ai-agent-project-template`).
2. Installs a local `.git/hooks/pre-push` block that refuses pushes.
3. Leaves your local Git history intact while ensuring the project is **local-only by default**.

To publish to your own independent GitHub repository later:

1. Create a NEW repository under your account (never share the template repository).
2. Add your project's remote:
   ```bash
   git remote add origin https://github.com/<your-owner>/<your-new-repo>.git
   ```
3. Remove the push block:
   ```bash
   rm .git/hooks/pre-push
   ```
4. Push your commits:
   ```bash
   git push -u origin main
   ```

## Download without Git history

Use GitHub's **Code > Download ZIP** option when you only want the files and do not want the template Git history.

After extracting:

```bash
cd my-new-project
git init
python scripts/init-fast.py
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

1. `python scripts/init-fast.py` passes (validation + token benchmark + prompt).
2. You open the folder in your IDE.
3. You paste the printed FAST_INIT prompt into a fresh agent context window and describe your project idea.

The printed prompt:

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

If you switch models mid-project, update `memory-bank/handoff.md` first so the next model picks up cleanly. See `workflows/handoff.md` for the protocol.

## Publishing this template

For maintainers publishing this template:

1. Run `python scripts/check-template.py` (full mode).
2. Optionally run `python scripts/check-template.py --fast` during routine maintenance.
3. Confirm no secrets, private files, or unintended `.git/` history are included.
4. Add a `LICENSE` file appropriate for your distribution (MIT, Apache-2.0, etc.) — not included by default.
5. Push to a public GitHub repository.
6. In repository settings, enable **Template repository** so users can create clean copies via **Use this template**.
