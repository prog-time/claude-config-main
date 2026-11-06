---
name: git-commit
description: |
  Creates git commits on an issues-{N} branch: analyzes changes, groups them
  into atomic commits, and generates the commit message — including the raw
  message-only output a git hook needs. Use ALWAYS when the user says
  "commit", "commit ru", "commit en", "commit <file1> <file2>", "create a
  commit", "commit changes", "stage and commit", "закоммить", "сделай коммит",
  "закомми", or uses the compact syntax `git-agent desc commit [lang]`. Do NOT
  use for: PR descriptions (use git-pr), release notes / CHANGELOG (use
  git-release), git pull/push/rebase/merge, managing GitHub issues, editing
  code, or writing a commit message as standalone text to paste outside a
  commit.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# git-commit

Entry point for commit workflows. Parse the invocation first, then route to
the correct mode.

## Mode Routing

| Invocation | Mode | Reference |
|---|---|---|
| `commit` / `commit <lang>` / `commit <files>` | **A. Atomic commit workflow** | `references/commit-workflow.md` |
| `git-agent desc commit [lang]` | **B. Commit message only** (hook) | `references/commit-message-rules.md` |

Load the relevant reference file **only** when entering its mode — not upfront.

## ABSOLUTE OUTPUT CONSTRAINT — Mode B only (`git-agent desc commit`)

When the user message starts with `git-agent desc commit`, your **entire
response** must be the raw commit message text — nothing before, nothing after.

**FORBIDDEN** — never output any of these:

- Phrases like "Here is the commit message:", "Suggested commit message:",
  "Generated commit message:"
- Any introductory or trailing sentence
- Markdown: no `**bold**`, no `# headers`, no ` ``` ` fences, no bullets
- Quotes around the message

The output is captured by a git hook and written directly to `COMMIT_EDITMSG`.
Any extra text corrupts the commit.

**Correct output (the whole response):**

```text
issues-42|add password reset via email
```

**Wrong output:**

```text
Here is the generated commit message:

issues-42|add password reset via email
```

This constraint applies **only** to Mode B. Mode A produces normal, explanatory
output.

## Parsing Rules

- `desc` = generate and show output only; do not commit.
- For `git-agent desc commit`: the argument after `commit` is a language code
  if it matches ISO 639-1 (`ru`, `en`, `de`, `fr`, `es`). Otherwise default to
  English. File names are not passed on the command line — they come from
  `git diff --cached`.

## Step 0 — Common Pre-Checks

Before entering any mode:

1. Confirm the working directory is a git repo (`git rev-parse --git-dir`).
2. Run `git branch --show-current` and match against `^issues-(\d+)$`. Capture
   `{N}`. **If the branch does not match, abort** — commits without an issue
   branch are forbidden. See the mode-specific abort behavior below.
3. Read real changes: `git diff --cached` (Mode B) or `git status` + `git diff`
   (Mode A). Never invent changes.

## Mode A — Atomic Commit Workflow

Full workflow: analyze changes, filter forbidden files, group into atomic
commits (max 3 files each, except one mechanical change), generate a message per group, run `git add` +
`git commit`.

Never output the commit message as standalone text — it must only appear as the
argument to `git commit -m "..."`. Go directly to the bash command, no
narration.

**Always read** `references/commit-workflow.md` before executing Mode A. It
contains:

- File filters (always-exclude and protected directories)
- Grouping rules (max 3 files, mechanical-change exception, relatedness)
- Author identity handling (no `Co-Authored-By`, no AI attribution)
- Message rules (delegates to `references/commit-message-rules.md`)
- Pre-commit hook behavior
- Error handling
- Pre-commit checklist

## Mode B — Commit Message Only (hook)

Pure output mode for a git hook. Read `references/commit-message-rules.md` for
per-language formatting rules.

Steps:

1. Resolve the current branch (`git branch --show-current`) and extract `{N}`
   via `^issues-(\d+)$`. If the branch does not match, output **exactly** this
   single line and stop:

   ```text
   error: not on an issues-{N} branch
   ```

   No explanation, no multiline — the hook writes stdout directly to
   `COMMIT_EDITMSG`, so the user sees this string as the initial message and can
   abort the commit.
2. Detect language from the argument after `commit` (default `en`).
3. Run `git diff --cached` to read the staged diff.
4. Generate a single imperative message following the language rules, prepended
   with `issues-{N}|` (no spaces around the pipe).
5. Output only the message text. Nothing else. See the absolute constraint
   above.

## Rules (non-negotiable)

- **Every commit message is prefixed with `issues-{N}|`.** `{N}` is extracted
  from the current branch name (`^issues-(\d+)$`). If the branch does not match,
  abort — commits from other branches are forbidden. One issue per prefix; for
  linked tasks, stack branches (`git switch -c issues-15 issues-12`) rather than
  concatenating numbers.
- **Never invent changes.** Everything comes from actual `git diff --cached` /
  `git status` output.
- **Never use `git add .` or `git add -A`** in Mode A. Stage files explicitly.
- **Never commit files from `tasks/`** in Mode A, even if tracked. Absolute
  prohibition.
- **Never stage `.idea/`, `data/`, `logs/`** unless the user explicitly names a
  file inside them.
- **Never use `--no-verify`** unless the user explicitly requests it.
- **Never add `Co-Authored-By` or any AI attribution** to commits. Use the
  repository's configured author only.
- **Never skip the reference file** for the active mode — it contains the
  details that keep output quality consistent.

## Examples

### Example 1 — Mode A (full commit workflow)

**User:** commit ru

**Assistant:** *(verifies current branch is `issues-{N}` — aborts if not, reads
`git status` + `git diff`, loads `references/commit-workflow.md`, groups files
into 1–3 atomic commits, runs `git add` + `git commit -m "issues-{N}|..."` per
group with Russian messages, shows commit hashes and summary — no standalone
message text)*

### Example 2 — Mode B (hook output)

**User:** git-agent desc commit

*(current branch: `issues-42`)*

**Assistant:**

```text
issues-42|add password reset via email
```

Nothing else. The whole response is the message line.

## Edge Cases

- **Not on `issues-{N}` branch in Mode A** — refuse immediately with the full
  abort message from `references/commit-workflow.md`. Do not offer to
  rename/switch branches; the user picks the next step.
- **Not on `issues-{N}` branch in Mode B** — output the literal
  `error: not on an issues-{N} branch` as the entire response. The hook writes
  this to `COMMIT_EDITMSG`; the user sees the error as the pre-filled commit
  message and aborts the commit.
- **No staged changes in Mode B** — output the literal single line
  `error: no staged changes` as the entire response, and stop. (A non-message
  string is fine here: the hook writes it to `COMMIT_EDITMSG`, the user sees it
  and aborts. Same shape as the branch-mismatch error — one line, no prose.)
- **User names a file from `tasks/` for Mode A** — refuse and explain the
  `tasks/` prohibition, regardless of `.gitignore` state.
- **Pre-commit hook fails (Mode A)** — show hook output, identify the problem,
  ask the user whether to fix or skip. Do NOT silently bypass.
- **Detached HEAD** — warn the user before committing; commits may be lost.
