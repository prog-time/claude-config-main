# Mode A — Atomic Commit Workflow

Load this file when handling `commit`, `commit <lang>`, `commit <file1>
<file2>`, "create a commit", "stage and commit", "закоммить", "сделай
коммит".

## Order of Operations (strict)

1. **Resolve branch** — `git branch --show-current`, extract `{N}` —
   abort if the branch is not `issues-{N}`
2. **Resolve author** — read `git config user.name` + `git config user.email`
3. **Analyze changes** — `git status` + `git diff`
4. **Filter files** — exclude forbidden and irrelevant files
5. **Group files** — split into atomic commit groups
6. **Determine type** — identify the change type for each group
7. **Commit each group** — `git add <files>` →
   `git commit -m "issues-{N}|<message>"`

## Step 1 — Resolve Branch (strict)

Read the current branch:

```bash
git branch --show-current
```

Match against the regex `^issues-(\d+)$`. The captured number becomes
the **mandatory prefix** `issues-{N}|` for every commit message
generated in this session.

If the branch name does not match, **abort immediately**:

```text
Error: commits require an 'issues-{N}' branch, got '{branch}'.
Run /task_complete with a task spec, or switch to an existing
'issues-{N}' branch.
```

Do NOT offer to rename the branch, checkout another branch, or fall
back to a prefix-less commit. The user must switch contexts explicitly.

### Stacked branches for related issues

If two issues are logically linked and need to build on each other, do
not concatenate numbers. Stack the branches:

```bash
git switch -c issues-12        # from main
# ... commits prefixed issues-12| ...
git switch -c issues-15 issues-12  # from issues-12
# ... commits prefixed issues-15| ...
```

Each commit carries exactly one issue number in its prefix — the
number of the branch it lives on.

## Step 2 — Resolve Author Identity

```bash
git config user.name
git config user.email
```

Use this identity for every commit. Never override or modify it.

If `user.name` or `user.email` is empty — warn and abort:

```text
Warning: git author is not configured in this repository.
Run:
  git config user.name "Your Name"
  git config user.email "you@example.com"
Commit aborted.
```

Do NOT add `Co-Authored-By`, `--author`, or any other identity attribution
that would associate the commit with Claude or any AI tool. The commit
must appear as if created by the repository's configured author only.

## Step 3 — Analyze Changes

Always run both:

```bash
git status
git diff
```

If specific files were provided — inspect only their diff:

```bash
git diff -- file1 file2
```

Do not proceed without reading the diff. The commit message must reflect
actual changes, not assumptions.

## Step 4 — Filter Files

**Never add:**

- `tasks/` — **STRICTLY FORBIDDEN.** Never commit any file from `tasks/`,
  even if tracked or not in `.gitignore`. No exceptions.
- `node_modules/`, `dist/`, `build/`, `.tmp`, `.cache`
- `.env`, `.env.*`
- `.DS_Store`, `Thumbs.db`
- Lock files unless they changed meaningfully
- Any file that looks like a build or generated artifact

If a file looks generated — do not add it, even if it changed.

If the user explicitly asks to commit a file from `tasks/` — refuse and
explain that `tasks/` files are never committed regardless of
`.gitignore` state.

### Protected Directories

Never stage or commit files from the directories below unless the user
explicitly names them in their message (e.g. "commit data/export.csv").
An override requires an explicit per-file or per-directory request — a
general "commit everything" instruction does NOT count as an override.

```text
.idea/
data/
logs/
```

Never use:

```bash
git add .
git add -A
```

Always add files explicitly:

```bash
git add src/auth/login.ts src/auth/token.ts
```

## Step 5 — Group Files

### Core Rules (non-negotiable)

1. **Maximum 3 files per commit — hard limit.** If a logical group has
   4+ files, split it into smaller commits. No exceptions.
2. **Only related files in one commit.** Files are related if they
   implement the same atomic change together (e.g. a service and its
   direct test). If you need to think hard about whether two files are
   related — they are not.
3. **Every unrelated file gets its own commit.**
4. **Smaller is better.** Prefer 1–2 files per commit over 3.

### How to Group

1. Start with the most cohesive pair: a file and its direct test, or two
   files that implement the same thing.
2. A group may have 1, 2, or at most 3 files — never more.
3. Any file that does not fit goes into the next group or its own
   commit.
4. Repeat until all files are assigned.

**Valid reasons to group:**

- A module and its direct unit test
- A controller and the route that registers it
- Two closely related model files for the same entity

**Always split into separate commits:**

- Refactoring vs. new functionality
- Bug fix vs. unrelated change
- Config/dependency update vs. application code
- Formatting-only change vs. semantic change
- Any file that is only loosely related to the others

### When NOT to Commit

- There are no meaningful changes
- Only whitespace or formatting changed with no semantic edits
- The changes are unclear or look accidental
- The file looks generated

## Step 6 — Generate Commit Message

Analyze the diff of the specific group and generate a single-line
message. Apply the per-language rules in
`references/commit-message-rules.md`.

Prepend the `issues-{N}|` prefix captured in Step 1 — no spaces around
`|`. The prefix counts toward the 72-character limit.

**Default language — English. Non-negotiable.** If the user has not
specified a language (e.g. `commit ru`, `commit de`), the message must
be English. No exceptions. Never infer a language from file contents,
project locale, or prior conversation context.

## Step 7 — Execute Commit

For each group:

```bash
git add src/auth/login.ts src/auth/token.ts
git commit -m "issues-42|implement login token generation"
```

Do NOT use `--no-verify` unless the user explicitly requests it.

If a pre-commit hook fails:

- Show the hook output
- Identify the problem (linting error, failing test, etc.)
- Ask the user whether to fix the issue or skip the hook
- Do NOT silently bypass the hook

After a successful commit, show:

- Short commit hash
- Commit message
- Summary: files changed, insertions, deletions

## Example

Changes:

```text
src/auth/login.ts         — new functionality
src/auth/token.ts         — new functionality
tests/auth/login.test.ts  — test for login.ts
src/utils/format.ts       — refactoring, unrelated to auth
```

**Commit 1** — new auth functionality:

```bash
git add src/auth/login.ts src/auth/token.ts tests/auth/login.test.ts
git commit -m "issues-42|implement login token generation"
```

**Commit 2** — utility refactoring:

```bash
git add src/utils/format.ts
git commit -m "issues-42|refactor format utilities"
```

## Error Handling

Always print a clear error message. Never fail silently.

| Situation | Message |
|-----------|---------|
| Branch is not `issues-{N}` | `Error: commits require 'issues-{N}' branch. Switch or run /task_complete.` |
| No changes to commit | `Error: nothing to commit. Run 'git status' to see the current state.` |
| Only whitespace changes | `Error: only whitespace changes detected — skipping commit.` |
| File not found when staging | `Error: file not found: {filename} — skipping. Continuing.` |
| Pre-commit hook failure | `Error: pre-commit hook failed. Fix or ask to skip.` |
| Commit rejected (protected branch) | `Error: commit rejected — branch '{branch}' may be protected.` |
| Detached HEAD | `Warning: repository is in detached HEAD state. Committing may result in lost work.` |
| git command not found | `Error: git is not installed or not in PATH.` |
| Staging failed | `Error: failed to stage {filename}.\n{git error output}` |
| Commit command failed | `Error: git commit failed.\n{git error output}` |

After printing the error:

- For recoverable errors (missing file, whitespace-only) — continue
  with remaining files/groups.
- For blocking errors (hook failure, rejected commit) — stop and wait
  for the user's decision.
- Always show the raw git error output alongside the human-readable
  message.

## Pre-Commit Checklist

- [ ] Current branch matches `^issues-(\d+)$` — otherwise aborted in
      Step 1
- [ ] Every message starts with `issues-{N}|` matching the captured
      branch number (no spaces, single pipe, one issue only)
- [ ] `git status` and `git diff` have been read
- [ ] No files from `tasks/` are staged — absolute prohibition
- [ ] No files from `.idea/`, `data/`, or `logs/` are staged — unless
      the user explicitly named them
- [ ] Forbidden files are excluded
- [ ] `git add .` and `git add -A` were not used
- [ ] Every commit contains **3 files or fewer**
- [ ] Every file in a commit is **directly related** to the others
- [ ] Every unrelated file has been assigned its own separate commit
- [ ] Commit size was minimized — 1–2 files preferred over 3
- [ ] No mixed change types within a single commit
- [ ] Language is English unless the user explicitly specified another
- [ ] Message reflects actual changes from the diff
- [ ] Single line, max 72 characters **including** the `issues-{N}|`
      prefix
- [ ] No conventional-commit type prefix (`feat:`, `fix:`, etc.)
- [ ] Commit message was passed directly to `git commit -m` — never
      announced or presented to the user as text
- [ ] No phrase like "Here is the suggested commit message:", "I will
      use:", or any narration before the git command
- [ ] Commit message contains no Markdown formatting
