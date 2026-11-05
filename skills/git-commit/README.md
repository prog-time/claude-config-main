# git-commit

Creates git commits on an `issues-{N}` branch. Two modes:

- **A — Atomic commit workflow** (`commit`, `commit ru`, `закоммить`): analyzes
  changes, groups them into atomic commits (max 3 files each), generates a
  message per group, and runs `git add` + `git commit`.
- **B — Commit message only** (`git-agent desc commit [lang]`): pure raw-output
  mode for a git hook — the entire response is the commit message line, written
  straight to `COMMIT_EDITMSG`.

## Triggers

- "commit", "commit ru", "commit en", "commit <files>"
- "create a commit", "stage and commit"
- "закоммить", "сделай коммит", "закомми"
- Compact: `git-agent desc commit [lang]`

## Does not trigger for

- PR descriptions (use `git-pr`)
- Release notes / CHANGELOG (use `git-release`)
- git pull / push / rebase / merge
- A commit message as standalone text to paste outside a commit

## Key guarantees

- Every message is prefixed `issues-{N}|` from the branch name; commits off an
  `issues-{N}` branch are refused.
- Explicit staging only — never `git add .`; never commits `tasks/`,
  `.idea/`, `data/`, `logs/`.
- No `Co-Authored-By` / AI attribution; no `--no-verify` unless asked.

## Installation

Picked up automatically after `make install` at the repository root.

## Note on the compact syntax

`git-agent desc commit` is kept verbatim as a trigger because it is wired into a
git hook and the global commit-message constraint. The skill is named
`git-commit`, but that legacy invocation still routes here.
