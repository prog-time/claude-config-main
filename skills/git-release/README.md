# git-release

Writes Release Notes from git history, updates CHANGELOG.md, and optionally
publishes a GitHub Release via the `gh` CLI.

- **D — Release Notes** (`git-agent desc release {version}`): groups commits by
  category into the Release Notes template.
- **E — Release Notes + CHANGELOG** (`git-agent desc changelog {version}`): same,
  then prepends the entry to `CHANGELOG.md` (shows the diff first).
- **G — Publish Release** (`git-agent publish release {version}`): same as D,
  then runs `gh release create` after explicit confirmation.

## Triggers

- "write release notes", "generate release notes", "update CHANGELOG",
  "cut a release"
- "релиз ноутс", "сделай релиз", "обнови CHANGELOG"
- Compact: `git-agent desc release …`, `git-agent desc changelog …`,
  `git-agent publish release …`

## Does not trigger for

- Creating commits (use `git-commit`)
- PR descriptions (use `git-pr`)
- git pull / push / rebase / merge, or managing GitHub issues

## Key guarantees

- Never invents commits — classification is from real `git log` only.
- Version normalized to a tag (`6` → `v6`, `2.3` → `v2.3.0`); bump recommended,
  user confirms.
- CHANGELOG prepended (never overwritten); diff shown before writing.
- Never publishes without explicit confirmation.

## Installation

Picked up automatically after `make install` at the repository root.
