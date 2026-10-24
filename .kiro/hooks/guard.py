#!/usr/bin/env python3
"""preToolUse guard for project agents.

Reads the Kiro hook event (JSON) from stdin. Exit 2 blocks the tool call and
sends stderr back to the model; exit 0 allows it.
"""
import json
import os
import re
import sys

REPO = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))

SHELL_RULES = [
    (r"\bgit\s+push\b", "Agents never push. Commit locally; a human pushes."),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard is forbidden."),
    (r"\bgit\s+clean\s+-\w*f", "git clean -f is forbidden."),
    (r"\bgit\s+branch\s+-D\b", "git branch -D is forbidden."),
    (r"\bgit\s+(rebase|filter-branch|commit\s+--amend)\b", "History rewriting is forbidden."),
    (r"\bgit\s+add\s+(\.|-A|--all)(\s|$)", "Stage specific paths, not everything."),
    (r"--no-verify\b", "Do not skip git hooks."),
    (r"\bsudo\b", "No sudo."),
    (r"\brm\s+-\w*r\w*f?\s+(/|~|\.\.|\*|\.(\s|$))", "Broad recursive delete is forbidden."),
    (r"\b(pip|pip3)\s+install\b(?!.*(-r|--target|\.venv|venv))", "Install into a local venv, not globally."),
    (r"\bnpm\s+(install|i)\s+(-g|--global)\b", "No global npm installs."),
]


def block(msg: str) -> None:
    print(f"BLOCKED by .kiro/hooks/guard.py: {msg}", file=sys.stderr)
    sys.exit(2)


def check_shell(inp: dict) -> None:
    cmd = inp.get("command", "") or ""
    # Unless a venv is active, pip install is global.
    venv_active = bool(os.environ.get("VIRTUAL_ENV"))
    for pattern, msg in SHELL_RULES:
        if "pip" in pattern and venv_active:
            continue
        if re.search(pattern, cmd):
            block(f"{msg} (command: {cmd!r})")


def check_write(inp: dict, cwd: str) -> None:
    path = inp.get("path") or inp.get("file_path") or ""
    if not path:
        return
    full = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    rel = os.path.relpath(full, REPO)
    if rel.startswith(".."):
        block(f"Writes outside the repo are forbidden ({full}).")
    if rel == ".git" or rel.startswith(".git" + os.sep):
        block("Do not write inside .git/.")
    if re.match(r"^\.env(\..*)?$", os.path.basename(rel)):
        block("Do not write .env files; ask a human to add secrets.")
    if rel == ".gitignore":
        text = " ".join(str(inp.get(k, "")) for k in ("content", "newStr"))
        if re.search(r"(^|\s|/)\.kiro", text):
            block(".kiro must never be gitignored (hackathon disqualification rule).")


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # fail open on malformed events rather than wedging the agent
    tool = event.get("tool_name", "")
    tags = event.get("tool_tags") or []
    inp = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.getcwd()
    if tool in ("shell", "execute_bash", "execute_cmd") or "shell" in tags:
        check_shell(inp)
    elif tool in ("write", "fs_write") or "write" in tags:
        check_write(inp, cwd)
    sys.exit(0)


if __name__ == "__main__":
    main()
