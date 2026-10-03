#!/usr/bin/env python3
"""Block outbound publishing commands that were not explicitly authorized.

`AGENTS.md` -> "Repository boundaries" forbids pushing, publishing, or syncing
without an explicit human instruction. That rule was prose-only; an agent that
skipped or forgot it could still transmit a local repository. This hook makes
the rule deterministic at the tool boundary.

Blocked: `git push` and plumbing equivalents (`git send-pack`), remote
mutation (`git remote add|set-url`, `git config remote.*.url`), publishing
through interpreter or code-runner indirection (`sh -c "git push"`,
`python -c "...git push..."`), and `gh pr|repo|release|issue|gist create`,
`gh api` with write-method flags, `gh secret set`, `gh release upload`.
Reads and local commits are untouched.

Follows the repository hook safety contract: standard library only, malformed
input fails open, and denial reasons never echo the command or its arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from typing import Dict, List
from shell_events import command as event_command, program as program_name, harmless_python


# Heredoc bodies are data, not commands. Without stripping them, writing a
# commit message or document that merely mentions `git push` would be denied.
HEREDOC_OPEN_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

# `git` global options that may precede the subcommand. Those taking a separate
# value are listed so the value word is skipped, not mistaken for the verb.
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

# Subcommands that transmit to, repoint at, or serve a remote. `send-pack` is
# the plumbing command `git push` execs; `daemon`/`http-backend` serve the
# repository over the network.
GIT_PUBLISHING_SUBCOMMANDS = {
    "push", "send-pack", "send-email", "request-pull", "svn", "p4",
    "daemon", "http-backend", "update-server-info",
}

# `git config remote.<name>.url|pushurl` repoints a remote like
# `remote set-url` does.
GIT_CONFIG_REMOTE_RE = re.compile(r"(?i)^remote\.[^.\s]+\.(url|pushurl)$")

# `gh <group> create` publishes; raw `gh api` writes need a method/field flag.
GH_PUBLISHING_GROUPS = {"pr", "repo", "release", "issue", "gist"}

# Write-method or field flags on `gh api` (POST is implied by -f/--field).
GH_METHOD_RE = re.compile(
    r"(?i)(?:-\s*x|--method)\s*=?\s*[\"']?(post|put|patch|delete)\b"
    r"|--field\b|(?<![\w-])-f\b"
)

# Wrappers that precede the real program (`sudo git push`, `env VAR=1 git push`).
WRAPPER_PROGRAMS = {"sudo", "command", "env", "nohup", "time", "exec", "nice", "xargs", "watch"}

# Interpreters whose `-c` argument is itself a command line; re-inspect it.
INTERPRETER_PROGRAMS = {"sh", "bash", "zsh", "dash", "ksh", "fish", "csh", "tcsh", "pwsh", "powershell", "cmd"}

# Programs that execute code strings; scan the string for publishing intent.
# Fail-closed: the guard cannot parse code semantics, so a one-liner that
# merely mentions `git push` is denied too.
CODE_PROGRAMS = {"python", "python3", "perl", "ruby", "node", "deno", "php"}
CODE_GIT_PUBLISH_RE = re.compile(
    r"(?i)\bgit\b[^a-z0-9]{0,8}\b"
    r"(push|send-pack|send-email|request-pull|svn|p4|daemon|http-backend)\b"
)
CODE_GH_API_RE = re.compile(r"(?i)\bgh\b[^a-z0-9]{0,8}\bapi\b")
CODE_METHOD_RE = re.compile(r"(?i)-x[^a-z0-9]{0,8}(post|put|patch|delete)\b")

DENIAL_REASON = (
    "Publishing is denied by repository policy (AGENTS.md -> Repository "
    "boundaries). Pushing, remote changes, and PR/repo creation require an "
    "explicit human instruction in the current conversation. Commit locally "
    "instead, then ask."
)


def parse_event(raw_input: str) -> Dict[str, object]:
    if not raw_input or not raw_input.strip():
        return {}
    try:
        data = json.loads(raw_input)
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def extract_command(event: Dict[str, object]) -> str:
    return event_command(event)


def strip_heredocs(command: str) -> str:
    lines = command.splitlines()
    kept = []
    index = 0
    while index < len(lines):
        line = lines[index]
        kept.append(line)
        index += 1
        try:
            lexer = shlex.shlex(line, posix=False, punctuation_chars="<>")
            lexer.whitespace_split = True
            words = list(lexer)
        except ValueError:
            continue
        openers = []
        for i, word in enumerate(words[:-1]):
            if word == "<<":
                delimiter = words[i+1].lstrip("-")
                quoted = delimiter.startswith((chr(39), chr(34)))
                openers.append((delimiter.strip(chr(39)+chr(34)), quoted))
        for terminator, quoted in openers:
            body = []
            while index < len(lines) and lines[index].strip() != terminator:
                body.append(lines[index])
                index += 1
            index += 1
            # Expanding heredocs execute substitutions even inside quote characters.
            # Opaque substitutions are conservatively denied, not discarded as data.
            if not quoted and any("$(" in value or "`" in value for value in body):
                kept.append("git push")
    return "\n".join(kept)


def split_segments(command: str) -> List[str]:
    """Split a command line on chain operators, respecting shell quoting.

    A naive regex split would cut `git commit -m "docs; git push"` (false
    positive) and shred `python -c "import os; os.system('git push')"`
    (false negative). This scanner only splits on `;`, `|`, `&`, newline,
    `$(`, and backticks that appear OUTSIDE quotes; `$(` and backticks
    inside double quotes still split because command substitution executes
    there in POSIX shells. Single-quoted content is literal data.
    """
    command = strip_heredocs(command)
    segments: List[str] = []
    current: List[str] = []
    quote = ""
    index = 0
    length = len(command)
    while index < length:
        char = command[index]
        if quote == "'":
            current.append(char)
            if char == "'":
                quote = ""
            index += 1
            continue
        if quote == '"':
            # `$(` and backticks still execute inside double quotes.
            if char == "$" and command[index:index + 2] == "$(":
                segments.append("".join(current))
                current = []
                index += 2
                continue
            if char == "`":
                segments.append("".join(current))
                current = []
                index += 1
                continue
            current.append(char)
            if char == "\\" and index + 1 < length:
                current.append(command[index + 1])
                index += 2
                continue
            if char == '"':
                quote = ""
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            index += 1
            continue
        if char == "\\" and index + 1 < length:
            current.append(char)
            current.append(command[index + 1])
            index += 2
            continue
        pair = command[index:index + 2]
        if pair in {"||", "&&"} or pair == "$(":
            segments.append("".join(current))
            current = []
            index += 2
            continue
        if char in ";|&\n`(){}":
            segments.append("".join(current))
            current = []
            index += 1
            continue
        current.append(char)
        index += 1
    segments.append("".join(current))
    return [segment for segment in (seg.strip() for seg in segments) if segment]


def split_words(segment: str) -> List[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        # Unbalanced quotes: fall back to whitespace splitting rather than
        # silently treating the segment as empty (which would allow it).
        return segment.split()


def _normalize_words(words: List[str]) -> List[str]:
    # Preserve argument boundaries: git" "push is one executable name.
    return words


def _code_argument(rest: List[str]) -> str:
    """Skip leading flags; return the command/code string after -c/-e."""
    args = list(rest)
    while args and args[0].startswith("-"):
        flag = args[0].lower()
        args = args[1:]
        if flag in {"-c", "-e"} or flag.startswith(("--command", "--eval")):
            break
    return " ".join(args)


def _strip_git_globals(words: List[str]) -> List[str]:
    """Drop `git` global options so words[0] becomes the subcommand."""
    index = 0
    while index < len(words):
        word = words[index]
        if not word.startswith("-"):
            break
        name = word.split("=", 1)[0]
        # `--git-dir=x` carries its value inline; `-C x` consumes the next word.
        if name in GIT_GLOBAL_WITH_VALUE and "=" not in word:
            index += 2
        else:
            index += 1
    return words[index:]


def segment_is_blocked(segment: str, depth: int = 0) -> bool:
    words = _normalize_words(split_words(segment))
    if not words:
        return False

    value_flags = {"-u", "--unset", "-g", "-n", "--interval", "-k", "--kill-after", "-s", "--signal", "-I", "-U", "--user", "-C", "--chdir"}
    safe_flags = {"-i", "--ignore-environment", "--", "-a", "-E", "-H", "--no-preserve-root"}
    while words:
        name = program_name(words[0])
        if "=" in words[0] and not words[0].startswith("-"):
            words = words[1:]
            continue
        if name not in WRAPPER_PROGRAMS and name != "timeout":
            break
        words = words[1:]
        while words and words[0].startswith("-"):
            flag = words.pop(0)
            if flag in value_flags:
                if not words:
                    return True
                words.pop(0)
            elif flag not in safe_flags:
                return True  # unsupported wrapper grammar is opaque
        if name == "timeout" and words:
            words = words[1:]
    if not words:
        return False
    program = program_name(words[0])
    rest = words[1:]

    if program in INTERPRETER_PROGRAMS:
        # The interpreter's argument is itself a command line
        # (`sh -c "git push"`); re-inspect it with the same rules.
        return is_blocked(_code_argument(rest), depth + 1)

    if program in CODE_PROGRAMS or re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", program):
        if any(flag.lower() in ("-c", "-e", "--eval", "--command") for flag in rest):
            code = _code_argument(rest)
            return not (program.startswith("python") and harmless_python(code))
        return False  # file execution remains advisory/uninspected

    if program in {"git", "hub"}:
        if any(rest[i-1] == "-c" and re.match(r"(?:alias\.|core\.hooksPath)", value.split("=",1)[0], re.I) for i, value in enumerate(rest) if i > 0):
            return True
        if any(value.startswith("--config-env=alias.") or value.startswith("--config-env=core.hooksPath=") for value in rest):
            return True
        rest = _strip_git_globals(rest)
        if not rest:
            return False
        subcommand = rest[0].lower().rstrip(")\"")
        if subcommand in GIT_PUBLISHING_SUBCOMMANDS:
            return True
        if subcommand == "remote" and any(
            arg.lower() in {"add", "set-url"} for arg in rest[1:]
        ):
            return True
        if subcommand == "config":
            reading = any(v in {"--get", "--get-all", "--get-regexp", "--list", "-l", "get", "list"} for v in rest[1:])
            if reading:
                return False
            return any(GIT_CONFIG_REMOTE_RE.match(v) or re.match(r"(?i)^(alias\.|core\.hooksPath$)", v) for v in rest[1:])
        local_commands = {"status", "diff", "log", "show", "add", "commit", "branch", "tag", "checkout", "switch", "restore", "reset", "clean", "rm", "mv", "merge", "rebase", "cherry-pick", "revert", "stash", "rev-parse", "rev-list", "ls-files", "ls-tree", "cat-file", "hash-object", "worktree", "init", "fetch", "pull", "clone", "remote", "help", "version", "describe", "check-ignore", "check-attr", "for-each-ref", "diff-tree", "diff-index", "symbolic-ref", "update-ref", "config", "apply", "am", "bisect", "blame", "grep", "archive", "bundle", "gc", "fsck", "reflog", "shortlog"}
        return subcommand not in local_commands

    if program == "gh":
        if not rest:
            return False
        head = rest[0].lower()
        if head in GH_PUBLISHING_GROUPS and any(
            arg.lower() in {"create", "edit", "comment", "delete", "merge", "close", "reopen", "sync"} for arg in rest[1:]
        ):
            return True
        if head == "api":
            method = None
            for i, arg in enumerate(rest):
                if arg in {"-X", "--method"} and i+1 < len(rest):
                    method = rest[i+1].upper()
                elif arg.startswith("--method="):
                    method = arg.split("=",1)[1].upper()
            if "graphql" in rest and any(v.startswith("--input") for v in rest):
                return True
            if method is not None:
                return method not in {"GET", "HEAD"}
            return bool(GH_METHOD_RE.search(segment) or any(v.startswith("--input") for v in rest))
        if (
            head in {"secret", "release"}
            and len(rest) > 1
            and rest[1].lower() in {"set", "upload"}
        ):
            return True
        return False

    return False


def is_blocked(command: object, depth: int = 0) -> bool:
    if depth > 5:
        return True  # opaque nesting cannot establish a safe command
    if not isinstance(command, str) or not command:
        return False
    return any(
        segment_is_blocked(segment, depth) for segment in split_segments(command)
    )


def denial_for(client: str) -> Dict[str, object]:
    if client == "gemini":
        return {"decision": "deny", "reason": DENIAL_REASON}
    if client in {"claude", "codex"}:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": DENIAL_REASON,
            }
        }
    return {
        "status": "unsupported",
        "reason": "No verified blocking contract is configured for this client.",
    }


def main(client: str = "unknown") -> int:
    try:
        event = parse_event(sys.stdin.read())
        if is_blocked(extract_command(event)):
            sys.stdout.write(json.dumps(denial_for(client), sort_keys=True) + "\n")
    except Exception:
        # A malformed event must not accidentally block all tool use.
        pass
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client",
        choices=("claude", "codex", "gemini", "unknown"),
        default="unknown",
        help="Native hook adapter supplying the event.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    sys.exit(main(arguments.client))
