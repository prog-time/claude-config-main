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
- If `{target}` is omitted, it is `develop` — the integration branch of every
  project. Do not fall back to `main` / `master`.
- `publish` accepts only `develop` as `{target}`. Any other target (`main`,
  `master`, …) → refuse: say that PRs from Claude Code always target `develop`
  and PRs into `main` are opened by humans. `desc` may describe any target.
- The repository is always the `origin` remote: pass
  `-R "$(gh repo view "$(git remote get-url origin)" --json nameWithOwner -q .nameWithOwner)"`
  to `gh`.
- If `{branch}` is omitted, use the current branch (`git branch --show-current`).

## Step 0 — Pre-Checks

1. Confirm the working directory is a git repo (`git rev-parse --git-dir`).
2. Read the relevant `git log` range (see `references/pr.md`). **Never invent
   commits** — classification comes only from real `git log` output.

## Rules (non-negotiable)

- **Never invent commits.** All classification must come from actual `git log`.
- **Never publish without confirmation.** `publish pr` must show the generated
  description and wait for the user's explicit "yes" before running `gh`.
- **Never open a PR into anything but `develop`.** Not even when asked; the
  `pr-base-guard` hook denies it anyway.
- **Auto-fill `Closes #{N}`** from the current branch (`^issues-(\d+)$`); if it
  does not match, leave it blank and warn the user.
- **Do not add a `## Checklist` section or a footer.**
- **Never skip `references/pr.md`** — it keeps output quality consistent.

## Examples

### Example 1 — Mode C (PR description)

**User:** git-agent desc pr issues-6

**Assistant:** *(target defaults to `develop`; runs
`git log origin/develop..issues-6 --oneline --no-merges`, loads
`references/pr.md`, classifies/consolidates commits, fills the PR template,
presents the result)*

### Example 2 — Mode F (publish PR)

**User:** git-agent publish pr issues-6 -> develop

**Assistant:** *(generates the description as in Mode C, shows it, asks "Create
the PR `issues-6 → develop` with this description? yes/no", waits for
confirmation, then runs `gh pr create -R {origin repo} --base develop --body "..."`)*

### Example 3 — Mode F into `main` (refused)

**User:** git-agent publish pr issues-6 -> main

**Assistant:** *(refuses: PRs from Claude Code always target `develop`; offers
`git-agent publish pr issues-6 -> develop` instead)*

## Edge Cases

- **Branch does not match `^issues-(\d+)$`** — generate the description anyway,
  but leave `Closes #` blank and warn that the issue number must be filled
  manually.
- **No commits between branch and target** — report that there is nothing to
  describe; do not fabricate a summary.
- **`gh` not authenticated (Mode F)** — show the generated description, report
  the `gh` error, and let the user authenticate and retry.
