---
description: Commit, push, and open a PR for the current issues-{N} branch via git-agent and mcp-github-issues
argument-hint: (no arguments)
contract: _contract.md
---

# /task_submit

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Finalises work on an `issues-{N}` branch: verifies the branch name,
produces commits through `git-agent`, pushes to origin, opens a
Pull Request via `mcp-github-issues`, and reports the PR URL.

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
  did; used as the PR body source when present.
- `issue_number_expected` — integer; when present, Step 1 must
  match this exact number, not just any `issues-{N}` pattern.

Absent these, `/task_submit` falls back to standalone behaviour
(body from commit log, any `issues-{N}` accepted).

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
**Action:** fetch remote state and compute the ahead-of-origin
count:

```bash
git fetch origin issues-{N}
git rev-list --count origin/issues-{N}..HEAD   # or HEAD if no remote
```

Treat a missing `origin/issues-{N}` as ahead-count equal to total
commit count (remote will be created on push).
**Capture:** `ahead_count` (integer ≥ 0),
`remote_exists` (boolean), `tree_dirty` (result of
`git status --porcelain` being non-empty).

**Failure modes:**
- `git fetch` network / auth failure → STOP with
  `error-templates.md#push-rejected` (`branch=issues-{N}`,
  `error=<verbatim>`). (The template fits the recovery wording.)

**Invariants after:** caller knows whether Step 3 needs to run.

### Step 3 — Create commits via `git-agent`

**Preconditions:** Step 2 captured `tree_dirty` and `ahead_count`.
**Action:** decide based on state:

- `tree_dirty == true` → invoke the `git-agent` skill to produce
  atomic commit(s). `git-agent` decides staging granularity,
  message content, and language (default unless overridden by the
  invocation context).
- `tree_dirty == false` and `ahead_count > 0` → **skip** this step
  (commits are already on the branch, just need pushing).
- `tree_dirty == false` and `ahead_count == 0` → STOP with
  `error-templates.md#nothing-to-submit` (`branch=issues-{N}`).

**Capture:** `commits_added` (integer — number of new commits
created by `git-agent`, or `0` if skipped).

**Failure modes:**
- `git-agent` fails to produce a commit (hook rejection, signing
  error, lint failure) → STOP with
  `error-templates.md#commit-failed` (`error=<verbatim>`). Never
  retry with `--no-verify`.

**Invariants after:** working tree is clean; branch has at least
one commit not on `origin/issues-{N}`.

### Step 4 — Push the branch

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

### Step 5 — Resolve the MCP project

**Preconditions:** push succeeded.
**Action:** apply the algorithm from
`_shared/project-resolution.md`.
**Capture:** `project` (string key).

**Failure modes:** as defined in `_shared/project-resolution.md`.
MCP unavailable → STOP with
`error-templates.md#mcp-not-connected` (`command=task_submit`).

### Step 6 — Check for an existing PR

**Preconditions:** `project` resolved.
**Action:** list PRs on the project whose `head` equals
`issues-{issue_number}`. If `mcp-github-issues` exposes a direct
PR-listing tool, use it; otherwise, attempt creation in Step 7 and
let the MCP reject duplicates.
**Capture:** `existing_pr_url` (string or empty),
`pr_state` (`existing` | empty).

**Failure modes:**
- MCP call fails with something other than "not found" → STOP with
  `error-templates.md#mcp-call-failed`.

### Step 7 — Open the Pull Request (if needed)

**Preconditions:** Step 6 captured `pr_state`.
**Action:**

- If `pr_state == "existing"` → set `pr_url = existing_pr_url` and
  skip to Step 8.
- Otherwise → call the `mcp-github-issues` PR-creation tool with:
  - **head:** `issues-{N}` (current branch)
  - **base:** `main`
  - **title:** derived from the GitHub Issue title
    (`mcp__mcp-github-issues__fetch_issue`, `issue: {N}`)
  - **body:** chosen per invocation context:
    - `team_lead_report` present → use its summary (first paragraph
      or an explicitly marked `## Summary` section).
    - otherwise → generate from `git log origin/main..HEAD
      --pretty='- %s'`.
    - always append a final line: `Closes #{issue_number}`.

**Capture:** `pr_url` (string), `pr_tag` (`new` if just created,
`existing` if reused).

**Failure modes:**
- MCP reports a duplicate PR error → re-query the project, capture
  the existing URL, set `pr_tag = "existing"`, continue to Step 8.
  Do not open a duplicate.
- Any other MCP error → STOP with
  `error-templates.md#pr-create-failed` (`error=<verbatim>`).

**Invariants after:** `pr_url` is non-empty and points at a PR
whose head is `issues-{issue_number}` and whose base is `main`.

### Step 8 — Report

**Preconditions:** Steps 1–7 completed.
**Action:** emit the `task_submit` template from
`_shared/report-templates.md`:

```
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
- Commits always go through `git-agent`. No inline `git commit`, no
  `--no-verify`.
- Never force-push. A rejected push is a STOP.
- PRs always go through `mcp-github-issues`. Never `gh pr create`.
- Base branch is always `main`.
- Never open a duplicate PR for the same head branch.
- `/task_submit` is delivery-only. It does not run the task
  pipeline. Full execution belongs to `/task_complete`.
