# git-agent

Single entry point for all git commit and release workflows in this
config. Replaces the previous `commit` skill and the `git-agent` agent.

## Supported modes

| Invocation | What it does |
|---|---|
| `commit`, `commit ru`, `commit <files>` | Stage + commit files as atomic groups (max 3 per commit) |
| `git-agent desc commit [lang]` | Output a single commit message line (for git hooks) |
| `git-agent desc pr [branch] -> [target]` | Generate a PR description |
| `git-agent desc release {version}` | Generate Release Notes for a version |
| `git-agent desc changelog {version}` | Generate Release Notes + prepend to `CHANGELOG.md` |
| `git-agent publish pr [branch] -> [target]` | Generate PR + `gh pr create` (after confirmation) |
| `git-agent publish release {version}` | Generate release + `gh release create` (after confirmation) |

## Triggers (natural language)

- "commit", "commit ru", "commit changes", "stage and commit"
- "закоммить", "сделай коммит", "закомми"
- "generate PR description", "write release notes", "update CHANGELOG"
- "сделай PR description", "релиз ноутс"

## Does not trigger for

- `git pull` / `git push` / `git rebase` / `git merge`
- Managing GitHub issues
- Editing code
- Writing commit messages as standalone text for copy/paste

## Structure

- `SKILL.md` — mode routing, absolute constraints, parsing rules
- `references/commit-workflow.md` — atomic commit workflow (Mode A)
- `references/commit-message-rules.md` — per-language message rules
  (Modes A and B)
- `references/pr-and-release.md` — classification, templates,
  publishing (Modes C–G)

References are loaded only when the corresponding mode is active.

## Installation

Picked up automatically after `make install` at the repository root.
