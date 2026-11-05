#!/usr/bin/env python3
"""PreToolUse hook: Pull Requests opened from Claude Code may only target `develop`.

Checks every way Claude can open or retarget a PR:
  - Bash: `gh pr create`, `gh pr edit --base`, `gh api .../pulls`
  - MCP:  any `*pull_request*` tool that carries a `base`
A missing base is denied too: `gh pr create` and the MCP tools fall back to
`main` (the repo default branch) when no base is given.
"""

import json
import os
import re
import shlex
import sys

ALLOWED_BASE = "develop"
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")"}


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{reason} Pull Requests from Claude Code must target "
                f"`{ALLOWED_BASE}`; PRs into `main` are opened by humans only."
            ),
        }
    }))
    sys.exit(0)


def segments(command):
    """Yield the argv of each simple command, split on newlines and shell operators."""
    for line in command.replace("\\\n", " ").splitlines():
        try:
            lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
            lexer.whitespace_split = True
            tokens = list(lexer)
        except ValueError:
            tokens = line.split()
        seg = []
        for tok in tokens:
            if tok in SEPARATORS:
                if seg:
                    yield seg
                seg = []
            else:
                seg.append(tok)
        if seg:
            yield seg


def flag_values(args, long_flag, short_flag=None):
    """Values of `--flag v`, `--flag=v`, `-f v`, `-fv`."""
    values = []
    for i, arg in enumerate(args):
        nxt = args[i + 1] if i + 1 < len(args) else None
        if arg == long_flag or (short_flag and arg == short_flag):
            if nxt is not None:
                values.append(nxt)
        elif arg.startswith(long_flag + "="):
            values.append(arg[len(long_flag) + 1:])
        elif short_flag and arg.startswith(short_flag) and not arg.startswith("--"):
            values.append(arg[len(short_flag):])
    return values


def check_gh(args):
    if args[:2] == ["pr", "create"]:
        bases = flag_values(args, "--base", "-B")
        if not bases:
            deny("`gh pr create` has no `--base`, so gh would target the default branch (usually `main`). Add `--base develop`.")
        bad = [b for b in bases if b != ALLOWED_BASE]
        if bad:
            deny(f"`gh pr create --base {bad[0]}` is not allowed.")
    elif args[:2] == ["pr", "edit"]:
        bad = [b for b in flag_values(args, "--base", "-B") if b != ALLOWED_BASE]
        if bad:
            deny(f"`gh pr edit --base {bad[0]}` is not allowed.")
    elif args[:1] == ["api"]:
        endpoint = next((a for a in args[1:] if re.search(r"repos/[^/\s]+/[^/\s]+/pulls(/\d+)?/?$", a)), None)
        if endpoint is None:
            return
        fields = flag_values(args, "--field", "-F") + flag_values(args, "--raw-field", "-f")
        bases = [f.split("=", 1)[1] for f in fields if f.startswith("base=")]
        bad = [b for b in bases if b != ALLOWED_BASE]
        if bad:
            deny(f"`gh api {endpoint}` with `base={bad[0]}` is not allowed.")
        creating = re.search(r"/pulls/?$", endpoint) and (fields or flag_values(args, "--input"))
        if creating and not bases:
            deny(f"`gh api {endpoint}` creates a PR without a verifiable `base=develop` field. Use `gh pr create --base develop`.")


def main():
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}

    if tool == "Bash":
        for seg in segments(tool_input.get("command", "")):
            idx = next((i for i, tok in enumerate(seg) if os.path.basename(tok) == "gh"), None)
            if idx is not None:
                check_gh(seg[idx + 1:])
    elif tool.startswith("mcp__") and "pull_request" in tool:
        base = tool_input.get("base")
        if "create" in tool and base is None:
            deny(f"`{tool}` has no `base`, so it would target `main`. Pass `base: \"develop\"`.")
        if base is not None and base != ALLOWED_BASE:
            deny(f"`{tool}` with `base: \"{base}\"` is not allowed.")


if __name__ == "__main__":
    main()
