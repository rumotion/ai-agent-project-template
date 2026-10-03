# Recommendation 1: truthful, default-local execution profiles

Status: implementable proposal. It is not applied to production scripts.
The supplied `push_backstop.py` is ready to copy to `scripts/push_backstop.py`.
It provides accident prevention only. A writer with shell access can bypass any
hook it owns; changing environment variable names does not fix that trust boundary.

## Immediate code integration

1. Add `scripts/push_backstop.py` to `REQUIRED_FILES` in
   `scripts/check-template.py:19` and `STANDARD_SCRIPTS` in
   `scripts/upgrade-target.py:103`. `new-project.py` already copies tracked files.
2. Replace `scripts/hooks/git/pre-push` with these exact LF bytes:

```sh
#!/bin/sh
# Local-only accident prevention; an external sandbox enforces adversarial isolation.
echo "PUSH BLOCKED - this repository is local-only (AGENTS.md)." >&2
exit 1
```

3. In `scripts/init-fast.py`, import `install` from `push_backstop`. Replace
   `install_push_backstop()` with:

```python
def install_push_backstop() -> None:
    install(ROOT)  # ValueError aborts init; do not print success without a hook.
```

4. In `scripts/new-project.py`, import the same helper and replace
   `install_push_backstop(target)` with:

```python
def install_push_backstop(target: Path) -> bool:
    install(target)
    return True
```

   Ensure failure returns nonzero from the CLI. A preserved unknown pre-push
   hook is a conflict, not successful installation. Existing detach-remote
   hooks are recognized by their exact trusted literal and preserved.
5. Remove the `CLAUDECODE`/`ALLOW_AGENT_PUSH` substring expectations from
   `check_git_backstop`. Read the actual Git blob as bytes:

```python
proc = subprocess.run(
    ["git", "cat-file", "blob", "HEAD:scripts/hooks/git/pre-push"],
    capture_output=True, cwd=str(ROOT),
)
if proc.returncode == 0 and b"\r" in proc.stdout:
    findings.append("committed pre-push blob contains CR bytes")
if path.read_bytes() != LOCAL_ONLY_HOOK:
    findings.append("working pre-push source differs from approved LF bytes")
```

   Import `LOCAL_ONLY_HOOK` from the shared helper. Validate both the source
   under review and the previous committed blob; never substitute HEAD's
   content for the working source. For archives with no Git blob, source-byte
   validation still runs. After committing, rerun the gate once to check the
   newly committed blob.
6. In `docs/hooks.md:68`, `CHANGELOG.md:18`, and the typed boundary record,
   replace the universal coverage assertion with: "The local pre-push hook
   prevents ordinary accidental pushes when installed and enabled. It does
   not constrain a process able to change Git config, use --no-verify,
   invoke send-pack, or execute an alternate network client."
   Keep the policy in AGENTS.md unchanged. Publishing needs the user's current
   instruction and a separately controlled release environment; the template
   does not supply a publish command or an environment-variable escape hatch.

## Medium-term enforcement contract

Add `scripts/boundary.py inspect --client NAME --json` and
`scripts/boundary.py verify --profile NAME`. Exit 0 only for a verified profile;
exit 1 for insufficient or bypassed controls; exit 2 for invalid invocation.
Every adapter must declare its client/version, all native shell/write/MCP tool
names, payload extractor, denial format, and evidence fixture. An untested
adapter returns `unverified`; it cannot be represented as enforced.

The inspection document must contain exactly:

```json
{
  "version": 1,
  "client": "codex",
  "profile": "advisory",
  "hook_path_resolved": true,
  "approved_hook_installed": true,
  "tool_events_verified": false,
  "egress_denied_outside_worker": false,
  "protected_paths_denied_outside_worker": false,
  "authority_outside_worker": false,
  "limitations": ["Git hooks can be disabled by the worker"]
}
```

Schema constraints: `additionalProperties: false`; require every shown key;
version integer enum [1]; client string maxLength 40; profile enum
[`advisory`, `contained-local`, `release`]; the six shown control fields are
booleans; limitations array maxItems 8, string items maxLength 160.

`contained-local` additionally requires all six controls true, fresh evidence
for the actual launcher and process tree, and immutable supervisor-owned
policy. Egress enforcement must cover TCP, UDP, child processes, native
HTTP/MCP connectors, and proxy escape paths. Sensitive inputs must be absent
from the worker mount, not merely regex-denied at writes. The supervisor must
not share ambient repository-publishing credentials with the worker.

Python stdlib can inspect controls and validate evidence. It cannot create a
portable hostile-process sandbox across Windows and POSIX. Use the host's
existing isolation capabilities through explicit per-platform launch adapters;
mark a platform unsupported until its negative tests pass. No dependency
installation is part of template initialization.

For an advisory profile, malformed JSON or unsupported tools yield a visible
coverage failure, while passive logging continues to fail open. For a
contained profile, the supervisor refuses dispatch if the authoritative
policy event cannot be decoded. A hook's exit code/native response alone is
not evidence that the client consumed the denial.

## Acceptance gates and costs

- Unit fixtures: the 24 remote-command cases and 12 sensitive-path cases in
  `probe.py` remain a documented advisory corpus; an isolated launch profile
  must prevent the actual operation even when its parser misses it.
- Disposable local Git tests: plain push denied with and without agent markers;
  override denied; a template destination denied; linked worktree hook installed;
  unknown existing hook preserved AND initialization fails; custom hooksPath
  fails explicitly; byte-exact LF checks reject CRLF.
- Live-client integration fixtures: a safe command executes; blocked commands
  do not execute; actual shell/edit/patch/MCP names are covered. Codex's current
  `exec_command`/`apply_patch` tools require evidence, not the old Bash/Shell
  example's assertion. Record fixture runner/client versions.
- Containment gate: synthetic loopback/blocked-egress, protected-file, config
  tampering, hook deletion, alias, and arbitrary Python tests. CI tests the
  launcher it actually uses; CI does not claim to prove every developer host.

Token cost: no startup prompt additions; diagnostics are lazy-loaded.
Ergonomics: humans publish in a separate authorized environment; custom hooks
need integration. Maintenance: small shared installer now; substantial native
launcher maintenance later. Portability: the hook/installer are portable
stdlib/POSIX-sh; security claims vary by verified host capability rather than
pretending all ten clients enforce the same boundary.
