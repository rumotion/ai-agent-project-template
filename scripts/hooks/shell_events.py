"""Shared advisory shell event extraction; not an execution sandbox."""
from __future__ import annotations
import ast
import re
import shlex


def tool_input(event: dict) -> dict:
    for value in (event.get("tool_input"), event.get("input"), event.get("toolCall", {}).get("args") if isinstance(event.get("toolCall"), dict) else None):
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return {"input": value}
    return {}


def command(event: dict) -> str:
    data = tool_input(event)
    for key in ("command", "cmd", "script", "CommandLine", "commandLine", "chars"):
        value = data.get(key, event.get(key))
        if isinstance(value, str):
            return value
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            return " ".join(shlex.quote(v) for v in value)
    return ""


def program(word: str) -> str:
    name = word.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


def harmless_python(code: str) -> bool:
    """Allow literal print statements only; arbitrary inline code is opaque."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in tree.body:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            return False
        call = node.value
        if not isinstance(call.func, ast.Name) or call.func.id != "print" or call.keywords:
            return False
        if not all(isinstance(arg, ast.Constant) and isinstance(arg.value, (str, int, float, bool, type(None))) for arg in call.args):
            return False
    return bool(tree.body)


def shell_words(text: str) -> list:
    lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|<>")
    lexer.whitespace_split = True
    return list(lexer)


def write_paths(text: str) -> list:
    try:
        words = shell_words(text)
    except ValueError:
        # A malformed shell event cannot establish a safe write target.
        return []
    paths = []
    segments = [[]]
    for word in words:
        if word in (";", "&&", "||", "|", "&"):
            segments.append([])
        else:
            segments[-1].append(word)
    for words in segments:
        for i, word in enumerate(words[:-1]):
            if word in (">", ">>", ">|"):
                paths.append(words[i+1])
        if not words:
            continue
        name = program(words[0])
        args = words[1:]
        if name.startswith("python") and "-c" in args:
            try:
                tree = ast.parse(args[args.index("-c")+1])
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open" and node.args:
                        if isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                            paths.append(node.args[0].value)
            except (IndexError, SyntaxError):
                pass
        if name == "tee":
            paths.extend(v for v in args if not v.startswith("-"))
        if name in ("cp", "mv", "copy", "move", "copy-item", "move-item"):
            lower = [v.lower() for v in args]
            for flag in ("-t", "--target-directory", "-destination"):
                if flag in lower and lower.index(flag)+1 < len(args):
                    paths.append(args[lower.index(flag)+1])
            positional = [v for v in args if not v.startswith("-")]
            if positional:
                paths.append(positional[-1])
        if name in ("set-content", "add-content", "out-file"):
            lower = [v.lower() for v in args]
            for flag in ("-path", "-literalpath", "-filepath"):
                if flag in lower and lower.index(flag)+1 < len(args):
                    paths.append(args[lower.index(flag)+1])
            if args and not args[0].startswith("-"):
                paths.append(args[0])
    return paths
