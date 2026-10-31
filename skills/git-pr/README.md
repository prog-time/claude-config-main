# git-pr

Writes Pull Request descriptions from the branch's real commits and, optionally,
publishes the PR via the `gh` CLI.

- **C — PR description** (`git-agent desc pr [branch] -> [target]`): classifies
  and consolidates commits, fills the PR template (Summary, Linked issues,
  Notes), auto-fills `Closes #{N}` from the branch.
- **F — Publish PR** (`git-agent publish pr [branch] -> [target]`): same, then
  runs `gh pr create` after explicit confirmation.

## Triggers

- "generate PR description", "write a PR description", "describe this PR",
  "open a PR"
- "сделай PR description", "опиши PR", "создай PR"
- Compact: `git-agent desc pr …`, `git-agent publish pr …`

## Does not trigger for

- Creating commits (use `git-commit`)
- Release notes / CHANGELOG (use `git-release`)
- git pull / push / rebase / merge, or managing GitHub issues

## Key guarantees

- Never invents commits — classification is from real `git log` only.
- Never publishes without explicit confirmation.
- MCP footer appended verbatim; no checklist in the PR body.

## Installation

Picked up automatically after `make install` at the repository root.
