---
name: git-pr
description: |
  Writes Pull Request descriptions from the branch's real commits and,
  optionally, publishes the PR via the `gh` CLI. Use ALWAYS when the user says
  "generate PR description", "write a PR description", "describe this PR",
  "open a PR", "сделай PR description", "опиши PR", "создай PR", or uses the
  compact syntax `git-agent desc pr [branch] -> [target]` or `git-agent publish
  pr [branch] -> [target]`. Do NOT use for: creating commits (use git-commit),
  release notes / CHANGELOG (use git-release), git pull/push/rebase/merge, or
  managing GitHub issues.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# git-pr

Generate (and optionally publish) Pull Request descriptions. Parse the
invocation first, then route to the correct mode.

## Mode Routing

| Invocation | Mode |
|---|---|
| `git-agent desc pr [branch] -> [target]` | **C. PR description** (show only) |
| `git-agent publish pr [branch] -> [target]` | **F. PR + `gh pr create`** (asks first) |

**Always read `references/pr.md`** before producing output — it holds commit
classification, the noise filter, the PR template, auto-fill rules, and the
`gh pr create` invocation.

## Parsing Rules

- `desc` = generate and show output only; do not publish.
- `publish` = generate, show, then publish **after** explicit user confirmation.
- `->` separates source branch from target branch.
- If `{target}` is omitted, resolve the default branch: try `main`, then
  `master` (`git branch -r | grep -E 'origin/(main|master)'`).
- If `{branch}` is omitted, use the current branch (`git branch --show-current`).

## Step 0 — Pre-Checks

1. Confirm the working directory is a git repo (`git rev-parse --git-dir`).
2. Read the relevant `git log` range (see `references/pr.md`). **Never invent
   commits** — classification comes only from real `git log` output.

## Rules (non-negotiable)

- **Never invent commits.** All classification must come from actual `git log`.
- **Never publish without confirmation.** `publish pr` must show the generated
  description and wait for the user's explicit "yes" before running `gh`.
- **Auto-fill `Closes #{N}`** from the current branch (`^issues-(\d+)$`); if it
  does not match, leave it blank and warn the user.
- **Append the MCP footer verbatim** and emit the checklist with empty boxes.
- **Never skip `references/pr.md`** — it keeps output quality consistent.

## Examples

### Example 1 — Mode C (PR description)

**User:** git-agent desc pr issues-6 -> main

**Assistant:** *(runs `git log origin/main..issues-6 --oneline --no-merges`,
loads `references/pr.md`, classifies/consolidates commits, fills the PR
template, presents the result)*

### Example 2 — Mode F (publish PR)

**User:** git-agent publish pr issues-6 -> main

**Assistant:** *(generates the description as in Mode C, shows it, asks "Create
the PR `issues-6 → main` with this description? yes/no", waits for confirmation,
then runs `gh pr create --base main --body "..."`)*

## Edge Cases

- **Branch does not match `^issues-(\d+)$`** — generate the description anyway,
  but leave `Closes #` blank and warn that the issue number must be filled
  manually.
- **No commits between branch and target** — report that there is nothing to
  describe; do not fabricate a summary.
- **`gh` not authenticated (Mode F)** — show the generated description, report
  the `gh` error, and let the user authenticate and retry.
