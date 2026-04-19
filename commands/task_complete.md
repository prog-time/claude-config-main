---
description: Execute a task on the current issues-{N} branch via team-lead, then deliver via /task_submit
argument-hint: <tasks/TASK-*.md path | GitHub issue URL>
contract: _contract.md
---

# /task_complete

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Executes a task on an already-prepared `issues-{N}` branch:
resolves the task spec, hands it to the `team-lead` agent, then
delegates delivery (commits → push → PR) to `/task_submit`.

Branch preparation lives in `/task_branch`. Delivery mechanics live
in `/task_submit`. This command is the middle orchestrator.

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

### Step 2a — Resolve spec from GitHub URL

**Preconditions:** `input_kind == url`.
**Action:**

1. Match `task_source` against
   `https://github.com/{owner}/{repo}/issues/{N}`; capture `{N}` as
   `issue_number`.
2. Resolve `project` via `_shared/project-resolution.md`.
3. Call `mcp__mcp-github-issues__fetch_issue` with `project` and
   `issue: {N}`.
4. Use the issue body as `task_spec`.

**Capture:** `issue_number` (integer), `task_spec` (string,
verbatim issue body), `project` (string).

**Failure modes:**
- URL malformed → STOP with
  `error-templates.md#malformed-issue-url` (`url={task_source}`).
- MCP unavailable → STOP with
  `error-templates.md#mcp-not-connected`
  (`command=task_complete`).
- `fetch_issue` fails → STOP with
  `error-templates.md#mcp-call-failed`
  (`tool=fetch_issue`, `error=<verbatim>`).

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

**Preconditions:** `issue_number` captured.
**Action:** `git rev-parse --abbrev-ref HEAD`. Compare against
`issues-{issue_number}`.
**Capture:** none (implicit assertion).

**Failure modes:**
- Current branch is not exactly `issues-{issue_number}` → STOP with
  `error-templates.md#branch-mismatch`
  (`current=<branch>`, `expected=issues-{issue_number}`,
  `next_command=task_branch`, `argument_hint={task_source}`).
- Not a git repo → STOP with
  `error-templates.md#not-a-git-repo`.

**Invariants after:** current branch matches the Issue the task
refers to. This command never switches branches.

### Step 4 — Hand the task off to `team-lead`

**Preconditions:** `task_spec`, `issue_number`, current branch all
settled.
**Action:** invoke the `team-lead` agent via the Agent tool with a
self-contained prompt containing:

- **Task spec** — `task_spec` verbatim (no summarisation, no
  trimming).
- **Linked GitHub Issue** — `#{issue_number}` (and URL if known).
- **Current branch** — `issues-{issue_number}`.
- **Instructions** — plan and execute the pipeline per the
  `team-lead` spec; never invoke `agent-builder`; produce the
  Project Execution Report in its standard shape.

**Capture:** `team_lead_outcome` (`success` | `blocked` |
`partial`), `team_lead_report` (verbatim final report from the
agent).

**Failure modes:**
- The Agent tool itself errors (e.g., missing agent type, crash) →
  STOP with `error-templates.md#mcp-call-failed`
  (`tool=Agent[team-lead]`, `error=<verbatim>`). (Re-using the
  `mcp-call-failed` template for tool-call failures keeps one
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
Branch:        issues-{issue_number}
Pull Request:  {pr_url} — [{pr_tag}]
----
{team_lead_report}
```

**Blocked variant** (`team_lead_outcome` was `blocked` or
`partial`):

```
Task source:   {task_source}
GitHub Issue:  #{issue_number}
Branch:        issues-{issue_number}
Delivery:      skipped — team-lead outcome `{team_lead_outcome}`
----
{team_lead_report}
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Branch preparation is out of scope. This command never switches,
  pulls, or creates branches. If Step 3 fails, defer to
  `/task_branch`.
- Delivery is out of scope for the inline body. Commits, push, and
  PR always go through `/task_submit`. No parallel fallback.
- `task_spec` is passed to `team-lead` verbatim. No summarisation,
  no paraphrasing, no section trimming.
- Never invoke `agent-builder` from the `team-lead` pipeline.
- Never call `gh` CLI. Use `mcp-github-issues` tools only.
- Branch name is literal `issues-{N}`.
- Delivery only on `team_lead_outcome == success`. `blocked` and
  `partial` outcomes are reported, not recovered.
