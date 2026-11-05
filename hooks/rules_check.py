#!/usr/bin/env python3
"""Check that rules/ schemas change together with the code they describe.

Every `rules/sync.yml` in the repository maps a section (api, database,
architecture) to code globs. When a change touches a section's code but not
its schema files, that is drift.

Modes:
  --hook              PostToolUse hook: after a `git commit` run by Claude, warn
                      about drift in that commit. Never blocks; silent when fine.
  --staged            check staged changes (exit 1 on drift).
  --range A..B        check a commit range, e.g. origin/develop...HEAD (CI, exit 1).
  --verify-generated  re-run api.generate and fail if the contract differs (CI).

A commit message line `Rules-Skip: <section> — <reason>` skips that section.
Stdlib only, so it runs anywhere Python 3.8+ is available.
"""

import json
import os
import re
import shlex
import subprocess
import sys

SCHEMA_GLOBS = {
    "api": ["rules/api/**"],
    "database": ["rules/database/**"],
    "architecture": ["rules/architecture/**"],
}
SKIP_RE = re.compile(r"^Rules-Skip:\s*([a-z, ]+)", re.IGNORECASE | re.MULTILINE)
PRUNE_DIRS = {".git", "node_modules", "vendor", ".venv", "venv", "dist", "build"}


def git(root, *args, check=True):
    res = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or f"git {' '.join(args)} failed")
    return res.stdout


def parse_sync(text):
    """Parse the flat YAML subset used by sync.yml: section -> key -> scalar | [str]."""
    data, section, key = {}, None, None
    for raw in text.splitlines():
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()
        if indent == 0 and body.endswith(":"):
            section, key = body[:-1], None
            data[section] = {}
        elif section and body.startswith("- ") and key:
            data[section].setdefault(key, [])
            if isinstance(data[section][key], list):
                data[section][key].append(body[2:].strip().strip("\"'"))
        elif section and ":" in body:
            key, _, value = body.partition(":")
            key, value = key.strip(), value.strip()
            data[section][key] = value.strip("\"'") if value else []
    return data


def glob_to_re(pattern):
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + r"\Z")


def matches(path, globs):
    return any(glob_to_re(g).match(path) for g in globs)


def find_sync_files(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        if os.path.basename(dirpath) == "rules" and "sync.yml" in filenames:
            found.append(os.path.join(dirpath, "sync.yml"))
    return sorted(found)


def check(root, changed, skipped):
    """Return drift messages for the changed paths (relative to the repo root)."""
    problems = []
    for sync_path in find_sync_files(root):
        base = os.path.relpath(os.path.dirname(os.path.dirname(sync_path)), root)
        prefix = "" if base == "." else base.rstrip("/") + "/"
        local = [p[len(prefix):] for p in changed if p.startswith(prefix)]
        with open(sync_path, encoding="utf-8") as fh:
            sync = parse_sync(fh.read())
        for section, conf in sync.items():
            if section not in SCHEMA_GLOBS or section in skipped:
                continue
            code_globs = conf.get("paths") or []
            if isinstance(code_globs, str):
                code_globs = [code_globs]
            code_hits = [p for p in local if not p.startswith("rules/") and matches(p, code_globs)]
            if not code_hits or any(matches(p, SCHEMA_GLOBS[section]) for p in local):
                continue
            schema = f"{prefix}rules/{section}/"
            hint = "run api.generate from sync.yml" if section == "api" and conf.get("generate") else f"update {schema}"
            more = f" (+{len(code_hits) - 1} more)" if len(code_hits) > 1 else ""
            problems.append(
                f"rules-check: {section} code changed ({prefix}{code_hits[0]}{more}) "
                f"but {schema} did not — {hint}, or add 'Rules-Skip: {section} — <reason>'."
            )
    return problems


def skipped_sections(message):
    out = set()
    for match in SKIP_RE.finditer(message or ""):
        out.update(s.strip().lower() for s in match.group(1).split(",") if s.strip())
    return out


def verify_generated(root):
    """Re-run each api.generate and report contracts that differ from the committed ones."""
    problems = []
    for sync_path in find_sync_files(root):
        base = os.path.dirname(os.path.dirname(sync_path))
        with open(sync_path, encoding="utf-8") as fh:
            api = parse_sync(fh.read()).get("api") or {}
        command = api.get("generate")
        if not command or not isinstance(command, str):
            continue
        res = subprocess.run(command, shell=True, cwd=base, capture_output=True, text=True)
        if res.returncode != 0:
            problems.append(f"rules-check: api.generate failed in {base}: {res.stderr.strip()[-300:]}")
            continue
        contract = os.path.join(base, "rules", "api")
        if git(root, "status", "--porcelain", "--", contract).strip():
            problems.append(f"rules-check: {os.path.relpath(contract, root)} is out of date — run api.generate and commit")
    return problems


def is_git_commit(command):
    for part in re.split(r"&&|\|\||;|\n", command or ""):
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.splitlines()
        if "git" in tokens:
            rest = tokens[tokens.index("git") + 1:]
            while rest[:1] and rest[0].startswith("-"):
                rest = rest[2:] if rest[0] in ("-C", "-c") else rest[1:]
            if rest[:1] == ["commit"]:
                return True
    return False


def run_hook():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    if data.get("tool_name") != "Bash" or not is_git_commit((data.get("tool_input") or {}).get("command")):
        return 0
    cwd = data.get("cwd") or os.getcwd()
    try:
        root = git(cwd, "rev-parse", "--show-toplevel").strip()
        if not find_sync_files(root):
            return 0
        changed = git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "HEAD").splitlines()
        problems = check(root, changed, skipped_sections(git(root, "log", "-1", "--format=%B")))
    except (RuntimeError, OSError):
        return 0
    if problems:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(problems),
        }}))
    return 0


def main(argv):
    if "--hook" in argv:
        return run_hook()
    root = git(os.getcwd(), "rev-parse", "--show-toplevel").strip()
    if "--verify-generated" in argv:
        problems = verify_generated(root)
    elif "--range" in argv:
        rng = argv[argv.index("--range") + 1]
        changed = git(root, "diff", "--name-only", rng).splitlines()
        log_range = rng.replace("...", "..")
        problems = check(root, changed, skipped_sections(git(root, "log", "--format=%B", log_range)))
    elif "--staged" in argv:
        problems = check(root, git(root, "diff", "--cached", "--name-only").splitlines(), set())
    else:
        print(__doc__.strip())
        return 2
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
