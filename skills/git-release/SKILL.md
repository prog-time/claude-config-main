---
name: git-release
description: |
  Writes Release Notes from git history, updates CHANGELOG.md, and optionally
  publishes a GitHub Release via the `gh` CLI, closing the open Issues that
  release completes. Use ALWAYS when the user says
  "write release notes", "generate release notes", "update CHANGELOG", "cut a
  release", "релиз ноутс", "сделай релиз", "обнови CHANGELOG", or uses the
  compact syntax `git-agent desc release {version}`, `git-agent desc changelog
  {version}`, or `git-agent publish release {version}`. Do NOT use for: creating
  commits (use git-commit), PR descriptions (use git-pr), git
  pull/push/rebase/merge, or managing GitHub issues outside a release.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# git-release

Generate Release Notes, update CHANGELOG.md, and optionally publish a GitHub
Release. Parse the invocation first, then route to the correct mode.

## Mode Routing

| Invocation | Mode |
|---|---|
| `git-agent desc release {version}` | **D. Release Notes** (show only) |
| `git-agent desc changelog {version}` | **E. Release Notes + CHANGELOG** |
| `git-agent publish release {version}` | **G. Release + `gh release create` + close completed Issues** (asks first) |

**Always read `references/release.md`** before producing output — it holds
commit classification, the noise filter, the Release Notes template, CHANGELOG
rules, version-bump guidance, the `gh release create` invocation, and the Issue
audit.

## Parsing Rules

- `desc` = generate and show output only; do not publish.
- `publish` = generate, show, then publish **after** explicit user confirmation.
- `{version}` — normalize to a tag: `6` → `v6`; `2.3` → `v2.3.0`; `v2.3.0` stays
  as-is.

## Step 0 — Pre-Checks

1. Confirm the working directory is a git repo (`git rev-parse --git-dir`).
2. Run `git fetch origin --tags`, resolve the previous tag, and read the
   relevant `git log` range up to `origin/main`, never `HEAD`: a release ships
   `main`, whichever branch is checked out (see `references/release.md`).
   **Never invent commits.**

## Rules (non-negotiable)

- **Never invent commits.** All classification must come from actual `git log`.
- **Never publish without confirmation.** `publish release` must show the
  generated notes and wait for the user's explicit "yes" before running `gh`.
- **Mode E shows the CHANGELOG diff before writing.** Never overwrite history;
  prepend the new entry. If `CHANGELOG.md` is missing, create it with only the
  new entry — do not invent prior entries.
- **State the version-bump recommendation and let the user confirm.**
- **Publishing a release deploys to production.** `gh release create v*`
  pushes a `v*` tag, and every project's deploy workflow ships `v*` tags to
  production. The confirmation question must say so, and the release is always
  cut from `main` in the `origin` repo:
  `gh release create {tag} -R {origin repo} --target main --notes-file …`.
  Never create or push a `v*` tag on anything but a `main` commit.
- **Mode G audits every open Issue.** The Issues it would close are listed in
  the release confirmation, so one "yes" covers both. Close them only after
  `gh release create` succeeds. Modes D and E never close anything.
- **Never close an Issue without evidence.** If completion is uncertain, leave
  it open and report why.
- **Never skip `references/release.md`** — it keeps output quality consistent.

## Examples

### Example 1 — Mode D (release notes)

**User:** git-agent desc release 2.3

**Assistant:** *(normalizes `2.3` → `v2.3.0`, finds the previous tag, runs
`git log {last_tag}..origin/main --oneline --no-merges`, loads `references/release.md`,
groups commits by category, presents the Release Notes)*

### Example 2 — Mode G (publish release)

**User:** git-agent publish release 2.3

**Assistant:** *(generates the notes as in Mode D, audits the open Issues, shows
the notes and the Issues to close, asks "Create GitHub release `v2.3.0` from
`main` with this content and close these Issues? The `v2.3.0` tag triggers the
production deploy. yes/no", waits for confirmation, runs
`gh release create v2.3.0 -R {origin repo} --target main --notes "..."`, then
closes the listed Issues)*

## Edge Cases

- **No previous tag** — fall back to `git log origin/main --oneline --no-merges`
  (all commits) and note this in the output.
- **Nothing since the previous tag** — report that `main` has nothing to
  release and that `develop` must reach `main` first (a human opens that PR). Do
  not fabricate notes.
- **Ambiguous version bump** — default to patch and ask the user to confirm if
  any changes look like features or breaking changes.
- **`CHANGELOG.md` missing in Mode E** — create it with only the new entry; do
  not invent prior entries.
- **`gh` not authenticated (Mode G)** — show the generated notes, report the
  `gh` error, and let the user authenticate and retry.
- **Draft release** — nothing ships, so skip the Issue audit and close nothing.
- **`gh release create` fails** — close nothing.
- **An Issue fails to close** — keep going with the rest and report the failure;
  the release stands.
