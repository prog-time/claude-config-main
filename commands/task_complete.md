---
description: Execute a task on the current issues-{N} branch via the team-lead skill, then deliver via /task_submit
argument-hint: <tasks/TASK-*.md path | GitHub issue URL>
contract: _contract.md
---

# /task_complete

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Single entry point for task execution: prepares the `issues-{N}` branch
(by invoking `/task_branch`), resolves the task spec, hands it to the
`team-lead` skill, then delegates delivery (commits → push → PR) to
`/task_submit`.

Branch preparation is in scope through the `/task_branch` invocation in
Step 2.5. Delivery mechanics live in `/task_submit`. This command is the
single orchestrator for the full pipeline.

**Input:** `$ARGUMENTS` — either
- a local path like `tasks/TASK-YYYYMMDD-{slug}.md`, or
- a GitHub issue URL like `https://github.com/{owner}/{repo}/issues/{N}`.

## Workflow

### Step 1 — Classify the input

**Preconditions:** `$ARGUMENTS` is non-empty.
**Action:** inspect the shape of `$ARGUMENTS`:
- starts with `http://` / `https://` **or** contains `github.com/`
  → branch to Step 2a;
- otherwise → branch to Step 2b.

**Capture:** `task_source` (verbatim `$ARGUMENTS`), `input_kind`
(one of `url` | `file`).

**Failure modes:**
- `$ARGUMENTS` is empty → STOP with
  `error-templates.md#usage-missing-args` (`command=task_complete`,
  `argument_hint=<tasks/TASK-*.md path | GitHub issue URL>`).

### Step 2.5 — Invoke `/task_branch`

**Preconditions:** `task_source` captured (Step 1 complete).
**Action:** invoke `/task_branch` per `_contract.md` §2, passing
`task_source` verbatim as `$ARGUMENTS`. `/task_branch` classifies
the input, resolves `issue_number`, verifies the working tree,
syncs `develop`, and creates or re-enters `issues-{N}`. The current
branch is `issues-{N}` when `/task_branch` completes.

**Capture:** `branch_state` (`new` | `existing`) from the
`Branch:` field of `/task_branch`'s report.

**Failure modes:**
- `/task_branch` STOPs for any reason → STOP, surfacing its output
  verbatim. No inline fallback, per `_contract.md` §2.

**Invariants after:** current branch is exactly
`issues-{issue_number_from_branch}`; contains every commit on
`develop`.

### Step 2a — Resolve spec from GitHub URL

**Preconditions:** `input_kind == url`.
**Action:**

1. Match `task_source` against
   `https://github.com/{owner}/{repo}/issues/{N}`; capture `{N}` as
   `issue_number`.
2. Apply `_shared/repo-resolution.md` as the gh preflight (confirms
   `gh` is available and authenticated).
3. Fetch the issue body, passing the URL directly:
   `gh issue view {task_source} --json body --jq .body`.
4. Use the issue body as `task_spec`.

**Capture:** `issue_number` (integer), `task_spec` (string,
verbatim issue body).

**Failure modes:**
- URL malformed → STOP with
  `error-templates.md#malformed-issue-url` (`url={task_source}`).
- `gh` unavailable / unauthenticated → STOP with
  `error-templates.md#gh-not-available` (`command=task_complete`).
- `gh issue view` fails → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=gh issue view`, `error=<verbatim>`).

### Step 2b — Resolve spec from local file

**Preconditions:** `input_kind == file`.
**Action:**

1. Verify the file exists under `tasks/`.
2. Read it; the full contents are `task_spec`.
3. Extract `#{N}` from the `**GitHub Issue:**` header line (prefer
   `#N` group, fall back to the URL's trailing `N`).

**Capture:** `issue_number` (integer), `task_spec` (string,
verbatim file contents).

**Failure modes:**
- File missing or outside `tasks/` → STOP with
  `error-templates.md#missing-task-file` (`path={task_source}`).
- `**GitHub Issue:**` line absent and no `#N` extractable → STOP
  with `error-templates.md#missing-issue-number`.

### Step 3 — Verify the current branch

**Preconditions:** `issue_number` captured (Step 2a or 2b);
`branch_state` captured (Step 2.5).
**Action:** `git rev-parse --abbrev-ref HEAD`. Compare against
`issues-{issue_number}`.
**Capture:** none (implicit assertion).

**Failure modes:**
- Current branch is not exactly `issues-{issue_number}` → STOP with
  `error-templates.md#branch-mismatch`
  (`current=<branch>`, `expected=issues-{issue_number}`,
  `next_command=task_branch`, `argument_hint={task_source}`).
  (This gate is theoretically unreachable when Step 2.5 succeeded,
  but is kept for self-containment per `_contract.md` §6.)
- Not a git repo → STOP with
  `error-templates.md#not-a-git-repo`.

**Invariants after:** current branch matches the Issue the task
refers to. Branch switching is performed by `/task_branch` in
Step 2.5; this command performs no inline branch switching.

### Step 4 — Hand the task off to the `team-lead` skill

**Preconditions:** `task_spec`, `issue_number`, current branch all
settled.
**Action:** invoke the `team-lead` skill via the Skill tool with a
self-contained `args` payload containing:

- **Task spec** — `task_spec` verbatim (no summarisation, no
  trimming).
- **Linked GitHub Issue** — `#{issue_number}` (and URL if known).
- **Current branch** — `issues-{issue_number}`.
- **Instructions** — analyse the task, route it adaptively (one
  agent if simple, a chain if complex), delegate, and log per the
  `team-lead` spec; never invoke `agent-builder`; return the strict
  JSON result.

**Capture:** `team_lead_outcome` (`success` | `blocked` |
`partial`) from the top-level `outcome` in the skill's JSON output
(a top-level `error` object maps to `blocked`); `team_lead_report`
(the skill's JSON output verbatim).

**Failure modes:**
- The Skill tool itself errors (e.g., missing skill, crash) →
  STOP with `error-templates.md#tool-call-failed`
  (`tool=Skill[team-lead]`, `error=<verbatim>`). (Re-using the
  `tool-call-failed` template for tool-call failures keeps one
  failure shape.)

**Invariants after:** `team_lead_report` is captured; the decision
about delivery is deferred to Step 5.

### Step 5 — Decide delivery vs skip

**Preconditions:** `team_lead_outcome` captured.
**Action:** branch:

- `team_lead_outcome == "success"` → continue to Step 6.
- `team_lead_outcome in {"blocked", "partial"}` → skip Step 6,
  jump to Step 7 (Report) with a `blocked` header variant.

**Capture:** `deliver` (boolean).

**Failure modes:** none — this is a pure decision step.

### Step 6 — Deliver via `/task_submit`

**Preconditions:** `deliver == true`.
**Action:** invoke `/task_submit` per `_contract.md` §2, passing
the invocation-context variables:

- `issue_number_expected = issue_number`
- `team_lead_report = team_lead_report`

**Capture:** from `/task_submit`'s report:
- `pr_url` (string)
- `pr_tag` (`new` | `existing`)
- `pushed_count` (integer)

**Failure modes:**
- `/task_submit` STOPs at any of its own gates → STOP, surfacing
  its output verbatim. Never fall back to an inline delivery path
  — see `_contract.md` §2 and §5.

**Invariants after:** the PR exists on GitHub and `pr_url` points
at it.

### Step 7 — Report

**Preconditions:** Step 6 completed, or Step 5 skipped to here.
**Action:** emit the `task_complete` template from
`_shared/report-templates.md`.

**Success variant** (delivery happened):

```
Task source:   {task_source}
GitHub Issue:  #{issue_number}
Branch:        issues-{issue_number}   [{branch_state}]
Pull Request:  {pr_url} — [{pr_tag}]
----
{team_lead_report}
```

**Blocked variant** (`team_lead_outcome` was `blocked` or
`partial`):

```
Task source:   {task_source}
GitHub Issue:  #{issue_number}
Branch:        issues-{issue_number}   [{branch_state}]
Delivery:      skipped — team-lead outcome `{team_lead_outcome}`
----
{team_lead_report}
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Branch preparation is in scope through the `/task_branch`
  invocation in Step 2.5. This command never switches, pulls, or
  creates branches inline — all branch operations are delegated to
  `/task_branch`. The `branch-mismatch` gate in Step 3 is a
  defensive invariant, not a recovery path.
- Delivery is out of scope for the inline body. Commits, push, and
  PR always go through `/task_submit`. No parallel fallback.
- `task_spec` is passed to the `team-lead` skill verbatim. No
  summarisation, no paraphrasing, no section trimming.
- Never invoke `agent-builder` from the `team-lead` flow.
- GitHub access is `gh` CLI only, against the `origin`
  repository. No project registry.
- Branch name is literal `issues-{N}`.
- Delivery only on `team_lead_outcome == success`. `blocked` and
  `partial` outcomes are reported, not recovered.
