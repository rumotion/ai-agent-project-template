# Scripts

Deterministic local scripts used by humans and agents. Standard library only — no installs required.

## Quick start (new users)

In a freshly cloned/copied template:

```bash
python scripts/init-fast.py
```

It will:

1. detect and detach inherited template remotes (making the project local-only and installing a pre-push block),
2. run `python scripts/check-template.py --fast`,
3. print the token cost of the FAST_INIT startup path,
4. print the FAST_INIT prompt to paste into a new agent context window.

## Included scripts

| Script | Purpose |
|---|---|
| `init-fast.py` | One-command bootstrap (detach template remotes + validate + benchmark + prompt). |
| `detach-remote.py` | Detaches inherited template remotes, installs pre-push block hook, makes repo local-only. |
| `upgrade-target.py` | Automated project upgrader tool; upgrades any target repo to latest template standard while preserving custom code, rules, and skills. |
| `check-template.py` | Template validator. Modes: `--fast` (lightweight), `--compat` (cross-agent contract), full (no flag), `--benchmark` (token cost only), `--check-remote` (remote audit). |
| `benchmark-context.py` | Offline manifest-based context measurement and sanitized paired-usage comparison; supports `--json` and `--self-test`. |
| `hooks/log-writes.py` | Passive write event logger (writes metadata to `.agent-logs/session.jsonl`). |
| `hooks/guard-sensitive-paths.py` | Client-aware path guard with verified Claude, Gemini, and Codex denial outputs. |
| `hooks/verify-fixtures.py` | Temp-only harness for normalized logs, redaction, malformed input, and native denial shapes. |

## Validator details

Full mode enforces:

- All files in the validator's required manifest are present.
- All adapter files reference `AGENTS.md`; Gemini, Claude, and Codex primary adapters match their exact thin-import forms.
- Startup/context size budgets respected, including a hard 9,500-character aggregate FAST_INIT ceiling.
- Canonical skill frontmatter is valid and all canonical/mirrored skill files across three trees are present (7 skills).
- Canonical workflow files and mirrors across three trees are present (10 workflows).
- `.gitignore` includes required safety patterns.
- Repository text scanned for secret-like content.
- SHA-256 hash equality across canonical and mirrored workflows and all three skill trees (zero drift).
- Hook fixture behavior, native hook adapter structure, and native MCP example structure.
- Native reviewer adapter markers/restrictions, dated advanced guidance, and
  the deterministic context-benchmark self-test.

## Rules

- Prefer simple, auditable scripts.
- Document inputs and side effects in the script's docstring.
- Do not store secrets in `scripts/`.
- Ask before adding scripts that call paid APIs or modify external systems.
