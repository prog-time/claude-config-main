---
description: Verify a clean tree, sync main, and create or re-enter the issues-{N} branch for a task
argument-hint: <tasks/TASK-*.md path | GitHub issue URL>
contract: _contract.md
---

# /task_branch

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Prepares the git branch for a task: resolves the Issue number from
the input, verifies the working tree is clean, fetches and syncs
`main`, then creates or re-enters the canonical `issues-{N}`
branch.

Does **not** run the task pipeline — that belongs to
`/task_complete`. See `_shared/workflow.md` for the full chain.

This command may be invoked standalone by the user, or automatically
from `/task_complete` Step 2.5. Both paths are supported; the
behaviour is identical in either context.

**Input:** `$ARGUMENTS` — either
- a local path like `tasks/TASK-YYYYMMDD-{slug}.md`, or
- a GitHub issue URL like `https://github.com/{owner}/{repo}/issues/{N}`.

## Workflow

### Step 1 — Classify the input

**Preconditions:** `$ARGUMENTS` is non-empty.
**Action:** inspect the shape of `$ARGUMENTS`:
- starts with `http://` / `https://` **or** contains `github.com/`
  → branch to Step 1a;
- otherwise → branch to Step 1b.

**Capture:** `task_source` (verbatim `$ARGUMENTS`), `input_kind`
(one of `url` | `file`).

**Failure modes:**
- `$ARGUMENTS` is empty → STOP with
  `error-templates.md#usage-missing-args` (`command=task_branch`,
  `argument_hint=<tasks/TASK-*.md path | GitHub issue URL>`).

### Step 1a — Resolve Issue number from URL

**Preconditions:** `input_kind == url`.
**Action:** match `task_source` against
`https://github.com/{owner}/{repo}/issues/{N}` (strict).
**Capture:** `issue_number` (integer `{N}`).

**Failure modes:**
- URL does not match → STOP with
  `error-templates.md#malformed-issue-url` (`url={task_source}`).

**Invariants after:** `issue_number ≥ 1`. No MCP call is made here;
spec resolution is deferred to `/task_complete`.

### Step 1b — Resolve Issue number from local file

**Preconditions:** `input_kind == file`.
**Action:** verify the file exists under `tasks/`; read it; extract
`#{N}` from the `**GitHub Issue:**` header line (prefer the `#N`
group, fall back to the trailing URL's `N`).
**Capture:** `issue_number` (integer `{N}`).

**Failure modes:**
- File missing or outside `tasks/` → STOP with
  `error-templates.md#missing-task-file` (`path={task_source}`).
- `**GitHub Issue:**` line absent and no `#N` extractable → STOP
  with `error-templates.md#missing-issue-number`.

### Step 2 — Verify the working tree is clean

**Preconditions:** none beyond being inside a git repo.
**Action:** `git status --porcelain`.
**Capture:** none.

**Failure modes:**
- Output is non-empty → STOP with
  `error-templates.md#dirty-tree` (`command=task_branch`,
  `status_output=<verbatim output>`).
- Not inside a git repo → STOP with
  `error-templates.md#not-a-git-repo`.

**Invariants after:** `git status --porcelain` is empty.

### Step 3 — Sync `main`

**Preconditions:** clean working tree (Step 2).
**Action:** run sequentially

```bash
git switch main
git fetch origin
git pull --ff-only origin main
```

The `git fetch origin` is deliberate — it also refreshes
`origin/issues-{N}`, which Step 4 consults. `--ff-only` refuses
divergence silently; recovery is the user's decision.
**Capture:** none.

**Failure modes:**
- `git switch main` fails → STOP with
  `error-templates.md#main-switch-failed` (`error=<verbatim>`).
- `git pull --ff-only origin main` rejects non-fast-forward or
  produces any error → STOP with
  `error-templates.md#main-pull-failed` (`error=<verbatim>`).

**Invariants after:** local `main` equals `origin/main`; remote
refs are up to date, including `origin/issues-{issue_number}` if it
exists.

### Step 4 — Create or re-enter `issues-{N}`

**Preconditions:** on `main`, remote refs fresh (Step 3).
**Action:** determine whether the branch already exists (locally or
remotely):

```bash
git show-ref --verify --quiet refs/heads/issues-{N}
git show-ref --verify --quiet refs/remotes/origin/issues-{N}
```

Then:

- **Neither local nor remote** → `git switch -c issues-{N}`.
  `branch_state = "new"`.
- **Local exists** (regardless of remote) → `git switch issues-{N}`
  then `git merge --ff-only main`; if that fails,
  `git merge main`.
  `branch_state = "existing"`.
- **Only remote exists** → `git switch -c issues-{N} origin/issues-{N}`
  to track it, then `git merge --ff-only main` (or regular merge on
  failure).
  `branch_state = "existing"`.

**Capture:** `branch_state` (`new` | `existing`).

**Failure modes:**
- `git switch -c` fails for any reason other than "already exists"
  → STOP with `error-templates.md#branch-create-failed`
  (`branch=issues-{N}`, `error=<verbatim>`).
- Merge produces a conflict → STOP with
  `error-templates.md#merge-conflict` (`branch=issues-{N}`,
  `error=<verbatim>`). Do not auto-abort.

**Invariants after:** current branch is exactly `issues-{N}`;
contains every commit on `main`.

### Step 5 — Report

**Preconditions:** Steps 1–4 completed.
**Action:** emit the `task_branch` template from
`_shared/report-templates.md`:

```
Task source:   {task_source}
GitHub Issue:  #{issue_number}
Branch:        issues-{issue_number}   [{branch_state}]
Next:          /task_complete {task_source}
```

The `Next:` line always points at `/task_complete` — the
`/task_submit` alternative is documented in
`_shared/workflow.md` and is the user's call, not this command's
suggestion. When this command is invoked automatically from inside
`/task_complete` Step 2.5, the `Next:` line is tautological but is
still emitted per `_contract.md` §7 ("Reports are the last thing the
command emits"); the parent captures only `branch_state` and ignores
the `Next:` field.
**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Branch name is literal `issues-{N}`. No slugs, no prefixes.
- No auto-stash, auto-commit, `reset --hard`, `merge --abort`, or
  other destructive recovery.
- No MCP call. `/task_branch` does not need the Issue body — only
  the number.
- No pipeline. `team-lead`, commits, push, and PR are out of scope.
- Remote branch `issues-{N}` is tracked, never overwritten.
