---
description: Abandon an issues-{N} branch — delete it locally, comment the Issue with a reason, update github-tasks.json
argument-hint: "<reason>" (free-form)
contract: _contract.md
---

# /task_abort

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Canonical way to walk away from a task:

1. delete the local `issues-{N}` branch,
2. post a one-paragraph comment on the GitHub Issue explaining why,
3. flip the record in `github-tasks.json` so `/task_sync` leaves it
   alone.

Does **not** close the GitHub Issue. Does **not** force-delete
un-pushed work — the user decides whether the branch was worth
keeping.

**Input:** `$ARGUMENTS` — free-form reason (one sentence or
paragraph). Passed verbatim into the Issue comment.

## Workflow

### Step 1 — Require a reason

**Preconditions:** none.
**Action:** check `$ARGUMENTS`.
**Capture:** `reason` (verbatim string).

**Failure modes:**
- `$ARGUMENTS` is empty → STOP with
  `error-templates.md#usage-missing-args` (`command=task_abort`,
  `argument_hint="<reason>"`).

### Step 2 — Verify the current branch

**Preconditions:** inside a git repo.
**Action:** `git rev-parse --abbrev-ref HEAD`. Match against
`issues-{N}` strict pattern (positive integer).
**Capture:** `issue_number` (integer), `branch` (string).

**Failure modes:**
- Branch does not match → STOP with
  `error-templates.md#branch-not-issues` (`current=<branch>`).
- Not a git repo → STOP with
  `error-templates.md#not-a-git-repo`.

### Step 3 — Check for unpushed work and confirm

**Preconditions:** on `issues-{N}`.
**Action:** check whether the remote branch exists, then compute
the unpushed count and tree state:

```bash
git ls-remote --exit-code --heads origin issues-{N}
git status --porcelain
```

- Exit `0` → run `git fetch origin issues-{N}` and
  `git rev-list --count origin/issues-{N}..HEAD`.
- Exit `2` (no such ref) → do **not** fetch the branch; run
  `git rev-list --count origin/develop..HEAD` (every commit on the
  branch is local-only).

If the branch has local-only commits **or** the working tree is
dirty, ask the user exactly:

```
Branch `issues-{N}` has unpushed commits or uncommitted changes.
They will be lost when the branch is deleted. Continue? (yes/no)
```

Wait for a `yes` response. Anything else → STOP silently (no error
template; this is a user-choice abort, not a failure).

**Capture:** `ahead_count`, `tree_dirty`, `user_confirmed`
(boolean).

**Failure modes:**
- `git ls-remote` exits with anything other than `0` or `2`, or
  `git fetch` fails → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=git ls-remote` or `tool=git fetch`, `error=<verbatim>`).

### Step 4 — Resolve the repo (gh preflight)

**Preconditions:** user confirmed (or nothing unpushed).
**Action:** apply `_shared/repo-resolution.md`. This confirms `gh`
is available and authenticated and yields the target repo.
**Capture:** `repo_slug` (`owner/repo`).

**Failure modes:** as defined in `_shared/repo-resolution.md`
(`command=task_abort`).

### Step 5 — Comment the Issue

**Preconditions:** `repo_slug` resolved.
**Action:** post the comment on the Issue:

```bash
gh issue comment {issue_number} -R {repo_slug} --body "/task_abort: {reason}"
```

The `/task_abort:` prefix is deliberate — it lets humans and future
`/task_sync` runs recognise the record.

**Capture:** `comment_posted` (boolean).

**Failure modes:**
- `gh issue comment` fails → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=gh issue comment`, `error=<verbatim>`). Do **not** proceed
  to Step 6; the branch is still on disk.

**Invariants after:** the Issue has a comment explaining why the
branch is being abandoned.

### Step 6 — Delete the local branch

**Preconditions:** comment posted.
**Action:** sequentially

```bash
git switch develop
git branch -D issues-{N}
```

`-D` (force) is justified here: the user already confirmed loss of
unpushed work in Step 3. This is the one place in the command set
where force-delete is permitted.

**Capture:** `branch_deleted` (boolean).

**Failure modes:**
- `git switch develop` fails → STOP with
  `error-templates.md#develop-switch-failed` (`error=<verbatim>`).
- `git branch -D` fails → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=git branch -D`, `error=<verbatim>`).

**Invariants after:** local branch `issues-{N}` no longer exists;
`origin/issues-{N}` is untouched (the user can restore from remote
if needed).

### Step 7 — Update `github-tasks.json` (if present)

**Preconditions:** branch deleted.
**Action:** check for `github-tasks.json` at repo root.

- **Missing** → record `json_state = "absent"`. Skip.
- **Present and valid** → locate the record whose key ends with
  `/issues/{issue_number}`. Set:

  ```json
  "status": "done",
  "close": true
  ```

  Leave `local` untouched so the task file stays linked. Save.
  `json_state = "updated"`.

**Capture:** `json_state` (`updated` | `absent`).

**Failure modes:**
- File exists but is malformed JSON → STOP with
  `error-templates.md#json-malformed`
  (`path=github-tasks.json`, `error=<verbatim>`). Do not rewrite
  silently. Note: the branch is already gone and the comment is
  posted; the user must reconcile the JSON by hand.

### Step 8 — Report

**Preconditions:** Steps 1–7 completed (or Step 7 skipped because
JSON was absent).
**Action:** emit the `task_abort` template from
`_shared/report-templates.md`:

```
Branch:        issues-{issue_number} — deleted
GitHub Issue:  #{issue_number} — commented
Reason:        {reason}
JSON record:   {json_state}
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Never close the GitHub Issue. Comment only.
- Never delete `origin/issues-{N}`. Only the local branch.
- Never skip the reason. `$ARGUMENTS` is mandatory.
- Step 3 confirmation is non-negotiable when there is unpushed or
  uncommitted work. No `--yes` flag.
- Force-delete (`git branch -D`) is allowed **only in Step 6**, and
  only after Step 3 confirmation.
- GitHub access is `gh` CLI only, against the `origin`
  repository. No project registry.
- Never `--force` push or rewrite remote history.
