---
description: Commit, push, and open a PR for the current issues-{N} branch via git-commit and the gh CLI
argument-hint: (no arguments)
contract: _contract.md
---

# /task_submit

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Finalises work on an `issues-{N}` branch: verifies the branch name,
produces commits through `git-commit`, pushes to origin, opens a
Pull Request via the `gh` CLI, and reports the PR URL.

Unlike `/task_complete`, this command **does not execute the task
pipeline** — it assumes the work is already done on the current
branch and only handles delivery.

See `_shared/workflow.md` for how `/task_submit` fits into the full
flow.

## Invocation context

`/task_submit` may run standalone or as a sub-command of
`/task_complete`. The caller can pass optional context variables in
the invocation prompt:

- `team_lead_report` — free-form text summarising what the pipeline
  did; used as the source of the PR body's `## Summary` when present.
- `issue_number_expected` — integer; when present, Step 1 must
  match this exact number, not just any `issues-{N}` pattern.

Absent these, `/task_submit` falls back to standalone behaviour
(summary from commit log, any `issues-{N}` accepted).

## Workflow

### Step 1 — Verify the branch

**Preconditions:** inside a git repo.
**Action:** `git rev-parse --abbrev-ref HEAD`. Match against
`issues-{N}` strict pattern (positive integer).
**Capture:** `issue_number` (integer `{N}`), `branch` (string).

**Failure modes:**

- Branch does not match `issues-{N}` → STOP with
  `error-templates.md#branch-not-issues` (`current=<branch>`).
- `issue_number_expected` was supplied and differs from `{N}` →
  STOP with `error-templates.md#branch-mismatch`
  (`current=<branch>`, `expected=issues-{issue_number_expected}`,
  `next_command=task_branch`,
  `argument_hint=<original input>`).
- Not a git repo → STOP with
  `error-templates.md#not-a-git-repo`.

**Invariants after:** current branch equals `issues-{issue_number}`.

### Step 2 — Detect unpushed work

**Preconditions:** branch verified (Step 1).
**Action:** check whether the remote branch exists, then compute
the ahead-of-origin count:

```bash
git ls-remote --exit-code --heads origin issues-{N}
```

- Exit `0` → `remote_exists = true`; run
  `git fetch origin issues-{N}` and
  `git rev-list --count origin/issues-{N}..HEAD`.
- Exit `2` (no such ref) → `remote_exists = false`; do **not**
  fetch the branch (it would fail with `couldn't find remote ref`).
  Run `git rev-list --count origin/develop..HEAD` — the remote branch
  will be created on push.

**Capture:** `ahead_count` (integer ≥ 0),
`remote_exists` (boolean), `tree_dirty` (result of
`git status --porcelain` being non-empty).

**Failure modes:**

- `git ls-remote` exits with anything other than `0` or `2`, or
  `git fetch` fails (network / auth) → STOP with
  `error-templates.md#tool-call-failed` (`tool=git ls-remote` or
  `tool=git fetch`, `error=<verbatim>`).

**Invariants after:** caller knows whether Step 3 needs to run.

### Step 3 — Create commits via `git-commit`

**Preconditions:** Step 2 captured `tree_dirty` and `ahead_count`.
**Action:** decide based on state:

- `tree_dirty == true` → invoke the `git-commit` skill to produce
  atomic commit(s). `git-commit` decides staging granularity,
  message content, and language (default unless overridden by the
  invocation context).
- `tree_dirty == false` and `ahead_count > 0` → **skip** this step
  (commits are already on the branch, just need pushing).
- `tree_dirty == false` and `ahead_count == 0` → STOP with
  `error-templates.md#nothing-to-submit` (`branch=issues-{N}`).

**Capture:** `commits_added` (integer — number of new commits
created by `git-commit`, or `0` if skipped).

**Failure modes:**

- `git-commit` fails to produce a commit (hook rejection, signing
  error, lint failure) → STOP with
  `error-templates.md#commit-failed` (`error=<verbatim>`). Never
  retry with `--no-verify`.

**Invariants after:** working tree is clean; branch has at least
one commit not on `origin/issues-{N}`.

### Step 4 — Run linting checks

**Preconditions:** working tree clean (Step 3 complete).
**Action:** check whether `linting/pre-push-check.sh` exists in the
repo root:

```bash
bash linting/pre-push-check.sh
```

- Script **present** → run it. Capture its exit code.
- Script **absent** → skip this step silently (`lint_status = skipped`).

**Capture:** `lint_status` (`passed` | `skipped`).

**Failure modes:**

- Script exits non-zero → STOP with message verbatim:

  ```text
  Linting failed. Fix the issues reported above, then retry /task_submit.
  Do not push with known lint errors.
  ```

**Invariants after:** code passes all linting checks, or no linting
script is present.

### Step 5 — Push the branch

**Preconditions:** working tree clean; at least one unpushed
commit.
**Action:**

```bash
git push -u origin issues-{N}
```

**Capture:** `pushed_count` — recompute after push as the number
of commits just delivered (equal to Step 2 `ahead_count` plus
`commits_added`).

**Failure modes:**

- `non-fast-forward` / rejected push → STOP with
  `error-templates.md#push-rejected` (`branch=issues-{N}`,
  `error=<verbatim>`). Never `--force` or `--force-with-lease`.
- Network / auth failure → STOP with the same template.

**Invariants after:** `origin/issues-{issue_number}` equals local
`HEAD`.

### Step 6 — Resolve the repo (gh preflight)

**Preconditions:** push succeeded.
**Action:** apply `_shared/repo-resolution.md`. This confirms `gh`
is available and authenticated and yields the target repo.
**Capture:** `repo_slug` (`owner/repo`).

**Failure modes:** as defined in `_shared/repo-resolution.md`
(`command=task_submit`).

### Step 7 — Check for an existing PR

**Preconditions:** `repo_slug` resolved.
**Action:** list any open PR whose head equals
`issues-{issue_number}`, whatever its base:

```bash
gh pr list -R {repo_slug} --head issues-{N} --state open \
  --json url,baseRefName --jq '.[0] // empty'
```

**Capture:** `existing_pr_url` (string or empty),
`existing_pr_base` (string or empty),
`pr_state` (`existing` if non-empty | empty).

**Failure modes:**

- `gh pr list` fails (auth/network) → STOP with
  `error-templates.md#tool-call-failed` (`tool=gh pr list`,
  `error=<verbatim>`).
- An open PR exists but `existing_pr_base != "develop"` → STOP with
  message verbatim:

  ```text
  Open PR {existing_pr_url} for issues-{N} targets `{existing_pr_base}`.
  Pull Requests from Claude Code must target `develop`. Retarget it
  (`gh pr edit {existing_pr_url} --base develop`) or close it, then
  retry /task_submit.
  ```

### Step 8 — Open the Pull Request (if needed)

**Preconditions:** Step 7 captured `pr_state`.
**Action:**

- If `pr_state == "existing"` → set `pr_url = existing_pr_url`,
  `pr_tag = "existing"`, and skip to Step 9.
- Otherwise → create it:
  - **title:** the GitHub Issue title, from
    `gh issue view {N} -R {repo_slug} --json title --jq .title`.
  - **body:** read `~/.claude/skills/git-pr/references/pr.md` and fill
    its PR Description Template, consolidation rules, and auto-fill
    rules, so every generated PR has the same shape. Source of
    `## Summary`, per invocation context:
    - `team_lead_report` present → its summary (first paragraph or an
      explicitly marked `## Summary` section).
    - otherwise → the commits in `git log origin/develop..HEAD`.

    `## Linked issues` carries `Closes #{issue_number}`.
  - write the body to a scratch file and run:

    ```bash
    gh pr create -R {repo_slug} --head issues-{N} --base develop \
      --title "{title}" --body-file {body_file}
    ```

  `Closes #N` closes the Issue only when the PR is merged into the
  repo's default branch; with `develop` as base it acts as a link
  until `develop` is released into `main`.

  `gh` prints the PR URL on stdout; capture it as `pr_url`.

**Capture:** `pr_url` (string), `pr_tag` (`new` if just created,
`existing` if reused).

**Failure modes:**

- `gh` reports a PR already exists for this head → re-run the Step 7
  query, capture the existing URL, set `pr_tag = "existing"`,
  continue to Step 9. Do not open a duplicate.
- Any other `gh pr create` error → STOP with
  `error-templates.md#pr-create-failed` (`error=<verbatim>`).

**Invariants after:** `pr_url` is non-empty and points at a PR
whose head is `issues-{issue_number}` and whose base is `develop`.

### Step 9 — Report

**Preconditions:** Steps 1–8 completed.
**Action:** emit the `task_submit` template from
`_shared/report-templates.md`:

```text
Branch:        issues-{issue_number}
GitHub Issue:  #{issue_number}
Commits:       {pushed_count} pushed
Pull Request:  {pr_url} — [{pr_tag}]
```

When running under `/task_complete`, this report is consumed by the
caller and re-wrapped — but it is still emitted in this exact
shape.

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Branch gate is strict: only `issues-{N}` where `{N}` is a
  positive integer.
- Never fabricate an Issue number, never rename the branch.
- Commits always go through `git-commit`. No inline `git commit`, no
  `--no-verify`.
- Never force-push. A rejected push is a STOP.
- PRs always go through the `gh` CLI (`gh pr create -R {repo_slug}`)
  against the `origin` repository. No project registry.
- Base branch is always `develop`. Never open or retarget a PR into
  `main` — `hooks/pr-base-guard.py` denies it anyway.
- Never open a duplicate PR for the same head branch.
- `/task_submit` is delivery-only. It does not run the task
  pipeline. Full execution belongs to `/task_complete`.
