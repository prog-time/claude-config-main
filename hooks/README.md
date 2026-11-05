# Hooks

Global Claude Code hooks shared by every project. `install.sh` symlinks
each file into `~/.claude/hooks/`; registering them in
`~/.claude/settings.json` is a manual step (snippet below).

| Hook | Event | What it does |
|---|---|---|
| [`pr-base-guard.py`](pr-base-guard.py) | `PreToolUse` (`Bash`, `mcp__*pull_request*`) | Denies any PR whose base is not `develop`: `gh pr create` without `--base` or with another base, `gh pr edit --base`, `gh api …/pulls`, and MCP `create_pull_request` calls. |
| [`task-offer.sh`](task-offer.sh) | `UserPromptSubmit` | If the project has a GitHub `origin`, tells Claude to ask «Создать задачу в репозитории {owner/repo}?» before implementing a request that looks like new functionality. Skipped for slash commands and on `issues-{N}` branches. |

## Conventions the hooks enforce

- **Repository = `origin`.** Every `gh` call gets `-R <owner/repo>` of
  `origin`; other remotes are ignored.
- **PR base = `develop`.** Task branches are cut from `origin/develop`;
  PRs into `main` are opened by humans only. A project without
  `origin/develop` must create it first.

The same rules are stated for the model in `~/.claude/CLAUDE.md` and in
`commands/_shared/repo-resolution.md`; the hook is the hard stop.

## Registration

Merge into `~/.claude/settings.json` (keep existing keys):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|mcp__.*pull_request.*",
        "hooks": [
          { "type": "command", "command": "python3 -I ~/.claude/hooks/pr-base-guard.py", "timeout": 10 }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/task-offer.sh", "timeout": 10 }
        ]
      }
    ]
  }
}
```

Then open `/hooks` once (or restart Claude Code) so the new config is
loaded.

## Testing

Both hooks read the event JSON on stdin, so they can be tested without
Claude Code:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"gh pr create --base main"}}' \
  | python3 -I hooks/pr-base-guard.py        # → permissionDecision: deny

echo "{\"prompt\":\"add CSV export\",\"cwd\":\"$PWD\"}" | hooks/task-offer.sh
```
