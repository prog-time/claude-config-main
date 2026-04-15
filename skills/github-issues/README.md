# github-issues

Manages GitHub Issues via the mcp-github-issues MCP server — creates drafts, publishes, closes, and comments.

## Installation

Picked up automatically after `make install` at the repository root.

## Requirements

The [`mcp-github-issues`](https://github.com/prog-time/mcp-github-issues)
MCP server must be registered in Claude Code (as `project-agent`). The
target repository must be listed in its `projects.yaml`.

## Usage

Example user requests that trigger the skill:

- `create an issue: login redirect loop after OAuth`
- `создай задачу — упал прод-билд из-за миграции`
- `close issue #42`
- `закрой задачу #38 — пофиксили в релизе v2.3.0`
- `comment on issue #17: reproduces only in Safari 17.4`
- `напиши комментарий в issue #5`
- `what issues are open in this project?`

For new issues the skill always goes through **draft → review → publish**:
the draft is written to `tasks/<project>/YYYY-MM-DD-<slug>.md` for you to
review before the issue is created on GitHub.
