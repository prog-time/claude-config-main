---
name: git-agent
description: |
  Handles git commit and release workflows: creates atomic commits, generates
  commit messages for git hooks, writes Pull Request descriptions, writes
  Release Notes, updates CHANGELOG.md, and publishes PRs/releases via `gh`
  CLI. Use ALWAYS when the user says "commit", "commit ru", "commit en",
  "commit <file1> <file2>", "create a commit", "commit changes",
  "stage and commit", "закоммить", "сделай коммит", "закомми", "generate
  PR description", "write release notes", "update CHANGELOG", "сделай PR
  description", "релиз ноутс", or uses the compact command syntax:
  `git-agent desc commit [lang]`, `git-agent desc pr [branch] -> [target]`,
  `git-agent desc release {version}`, `git-agent desc changelog {version}`,
  `git-agent publish pr [branch] -> [target]`, `git-agent publish release
  {version}`. Do NOT use for: git pull/push/rebase/merge, managing GitHub
  issues, editing code, or writing a commit message as standalone text for
  the user to copy/paste outside a commit.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# git-agent

Single entry point for all commit and release workflows. Parse the
invocation first, then route to the correct mode.

## Mode Routing

Parse the user input, then pick exactly one mode:

| Invocation | Mode | Reference |
|---|---|---|
| `commit`, `commit <lang>`, `commit <file1> <file2>` | **A. Atomic commit workflow** — stage + commit | `references/commit-workflow.md` |
| `git-agent desc commit [lang]` | **B. Commit message only** (hook output) | `references/commit-message-rules.md` |
| `git-agent desc pr [branch] -> [target]` | **C. PR description** | `references/pr-and-release.md` |
| `git-agent desc release {version}` | **D. Release Notes** | `references/pr-and-release.md` |
| `git-agent desc changelog {version}` | **E. Release Notes + prepend CHANGELOG.md** | `references/pr-and-release.md` |
| `git-agent publish pr [branch] -> [target]` | **F. Generate PR + `gh pr create`** (asks confirmation) | `references/pr-and-release.md` |
| `git-agent publish release {version}` | **G. Generate release + `gh release create`** (asks confirmation) | `references/pr-and-release.md` |

Load the relevant reference file **only** when entering its mode — not
upfront. This keeps context lean.

## ABSOLUTE OUTPUT CONSTRAINT — Mode B only (`git-agent desc commit`)

When the user message starts with `git-agent desc commit`, your **entire
response** must be the raw commit message text — nothing before, nothing
after.

**FORBIDDEN** — never output any of these:

- Phrases like "Here is the commit message:", "Suggested commit message:",
  "Generated commit message:"
- Any introductory or trailing sentence
- Markdown: no `**bold**`, no `# headers`, no ` ``` ` fences, no bullets
- Quotes around the message

The output is captured by a git hook and written directly to
`COMMIT_EDITMSG`. Any extra text corrupts the commit.

**Correct output (the whole response):**

```
issues-42|add password reset via email
```

**Wrong output:**

```
Here is the generated commit message:

issues-42|add password reset via email
```

This constraint applies **only** to Mode B. Modes A and C–G produce
normal, explanatory output.

## Parsing Rules (all modes)

- `desc` = generate and show output only; do not publish.
- `publish` = generate, show, then publish after user confirmation.
- `{version}` — normalize to tag: `6` → `v6`; `2.3` → `v2.3.0`; `v2.3.0`
  stays as-is.
- `->` separates source branch from target branch.
- If `{target}` is omitted, resolve the default branch: try `main`, then
  `master` (`git branch -r | grep -E 'origin/(main|master)'`).
- If `{branch}` is omitted, use the current branch
  (`git branch --show-current`).
- For `git-agent desc commit`: the argument after `commit` is a language
  code if it matches ISO 639-1 (`ru`, `en`, `de`, `fr`, `es`). Otherwise
  default to English. File names are not passed on the command line —
  they come from `git diff --cached`.

## Step 0 — Common Pre-Checks

Before entering any mode:

1. Confirm the working directory is a git repo
   (`git rev-parse --git-dir`).
2. For commit modes (A, B): run `git branch --show-current` and match
   against `^issues-(\d+)$`. Capture `{N}`. **If the branch does not
   match, abort** — commits without an issue branch are forbidden. See
   Mode-specific abort messages below.
3. For commit modes (A, B): run `git diff --cached` (Mode B) or
   `git status` + `git diff` (Mode A) to read real changes.
4. For release/PR modes (C–G): read the relevant `git log` range. Never
   invent commits.

## Mode A — Atomic Commit Workflow

Full workflow: analyze changes, filter forbidden files, group into atomic
commits (max 3 files each), generate a message per group, run
`git add` + `git commit`.

Never output the commit message as standalone text — it must only appear
as the argument to `git commit -m "..."`. Go directly to the bash command,
no narration.

**Always read** `references/commit-workflow.md` before executing Mode A.
It contains:

- File filters (always-exclude and protected directories)
- Grouping rules (max 3 files, relatedness criteria)
- Author identity handling (no `Co-Authored-By`, no AI attribution)
- Message rules (delegates to `references/commit-message-rules.md`)
- Pre-commit hook behavior
- Error handling
- Pre-commit checklist

## Mode B — Commit Message Only (hook)

Pure output mode for a git hook. Read `references/commit-message-rules.md`
for per-language formatting rules.

Steps:

1. Resolve the current branch (`git branch --show-current`) and extract
   `{N}` via `^issues-(\d+)$`. If the branch does not match, output
   **exactly** this single line and stop:

   ```
   error: not on an issues-{N} branch
   ```

   No explanation, no multiline — the hook writes stdout directly to
   `COMMIT_EDITMSG`, so the user will see this string as the initial
   message and can abort the commit.
2. Detect language from the argument after `commit` (default `en`).
3. Run `git diff --cached` to read the staged diff.
4. Generate a single imperative message following the language rules,
   prepended with `issues-{N}|` (no spaces around the pipe).
5. Output only the message text. Nothing else. See absolute constraint
   above.

## Modes C–G — PR Descriptions, Release Notes, Publishing

Read `references/pr-and-release.md` for:

- Commit classification (conventional vs inferred)
- Noise filter (merges, WIP, typos, formatting, reverts)
- Consolidation rules (grouping, user-facing phrasing)
- PR description template
- Release Notes template
- CHANGELOG.md prepend rules
- Version bump guidance (major/minor/patch)
- `gh pr create` and `gh release create` invocation — always with
  user confirmation before publishing

## Rules (non-negotiable)

- **Every commit message is prefixed with `issues-{N}|`.** `{N}` is
  extracted from the current branch name (`^issues-(\d+)$`). If the
  branch does not match, abort — commits from other branches are
  forbidden. One issue per prefix; for linked tasks, stack branches
  (`git switch -c issues-15 issues-12`) rather than concatenating
  numbers.
- **Never invent commits.** All commit classification must come from
  actual `git log` or `git diff --cached` output.
- **Never publish without confirmation.** `publish pr` and `publish
  release` must show the generated content and wait for the user's
  explicit "yes" before running `gh`.
- **Never use `git add .` or `git add -A`** in Mode A. Stage files
  explicitly.
- **Never commit files from `tasks/`** in Mode A, even if tracked.
  Absolute prohibition.
- **Never stage `.idea/`, `data/`, `logs/`** unless the user explicitly
  names a file inside them.
- **Never use `--no-verify`** unless the user explicitly requests it.
- **Never add `Co-Authored-By` or any AI attribution** to commits. Use
  the repository's configured author only.
- **Never skip the reference file** for the active mode — it contains
  the details that keep output quality consistent.

## Examples

### Example 1 — Mode A (full commit workflow)

**User:** commit ru

**Assistant:** *(verifies current branch is `issues-{N}` — aborts if
not, reads `git status` + `git diff`, loads
`references/commit-workflow.md`, groups files into 1–3 atomic commits,
runs `git add` + `git commit -m "issues-{N}|..."` per group with
Russian messages, shows commit hashes and summary — no standalone
message text)*

### Example 2 — Mode B (hook output)

**User:** git-agent desc commit

*(current branch: `issues-42`)*

**Assistant:**

```
issues-42|add password reset via email
```

*(Nothing else. The whole response is the message line.)*

### Example 3 — Mode C (PR description)

**User:** git-agent desc pr issues-6 -> main

**Assistant:** *(runs `git log origin/main..issues-6 --oneline --no-merges`,
loads `references/pr-and-release.md`, classifies/consolidates commits,
fills the PR template, presents the result)*

### Example 4 — Mode G (publish release)

**User:** git-agent publish release 2.3

**Assistant:** *(normalizes `2.3` → `v2.3.0`, finds previous tag, generates
Release Notes, shows them, asks: "Create GitHub release `v2.3.0` with this
content? yes/no", waits for confirmation, then runs `gh release create v2.3.0 --notes "..."`)*

## Edge Cases

- **Not on `issues-{N}` branch in Mode A** — refuse immediately with
  the full abort message from `references/commit-workflow.md`. Do not
  offer to rename/switch branches; the user picks the next step.
- **Not on `issues-{N}` branch in Mode B** — output the literal
  `error: not on an issues-{N} branch` as the entire response. The
  hook writes this to `COMMIT_EDITMSG`; the user sees the error as
  the pre-filled commit message and aborts the commit.
- **No staged changes in Mode B** — output a single blank line? No —
  abort with a single-line error *before* Claude produces any content,
  because any other output contaminates the hook. Actually: if nothing
  is staged, the hook should not have been invoked. Output the literal
  message `no staged changes` (still a valid one-line string the hook
  will write) and let the user notice and abort.
- **No previous tag for release** — fall back to `git log --oneline
  --no-merges` (all commits) and note this in the output.
- **User names a file from `tasks/` for Mode A** — refuse and explain
  the `tasks/` prohibition, regardless of `.gitignore` state.
- **Pre-commit hook fails (Mode A)** — show hook output, identify the
  problem, ask the user whether to fix or skip. Do NOT silently bypass.
- **Ambiguous version bump** — default to patch and ask the user to
  confirm if any changes look like they could be features or breaking.
- **Detached HEAD** — warn the user before committing; commits may be
  lost.
- **`CHANGELOG.md` missing in Mode E** — create it with only the new
  entry; do not invent prior entries.
