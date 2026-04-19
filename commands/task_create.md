---
description: Create a task file in tasks/ and a linked GitHub Issue via mcp-github-issues in one pass
argument-hint: <task description>
contract: _contract.md
---

# /task_create

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Orchestrates end-to-end task creation: produces a TASK file via the
`task-writer` agent, then creates a matching GitHub Issue by
calling `mcp-github-issues` MCP tools directly, and writes the
Issue number back into the task file header.

See `_shared/workflow.md` for where `/task_create` sits in the
overall chain.

**Input:** `$ARGUMENTS` — free-form task description (feature / bug
/ refactor / spike intent).

## Workflow

### Step 1 — Create the task file via `task-writer`

**Preconditions:** `$ARGUMENTS` is non-empty.
**Action:** invoke the `task-writer` agent via the Agent tool with
`$ARGUMENTS` as the task description.

**Fallback path.** If the registered `task-writer` subagent type is
unavailable (e.g. `Agent type 'task-writer' not found`), re-invoke
with `subagent_type: "general-purpose"` and inline the spec. Locate
it in this order:

1. `agents/task-writer.md` (project-local)
2. `~/.claude/agents/task-writer.md` (global)

Brief the fallback agent:

> You are acting as the **task-writer** agent (its registered
> subagent type is unavailable in this session, so you're
> executing its spec directly). Follow the spec below verbatim —
> explore the project, classify type, pick estimate, fill every
> template section, write the file in one pass, no confirmation.
> Return only the task-writer's canonical 5-line output (Created /
> Title / Type / Estimate / Open questions).
>
> --- task-writer spec ---
> {contents of task-writer.md}
> --- end spec ---
>
> User's task description: `$ARGUMENTS`
> Today's date: {YYYY-MM-DD from the environment block}

**Capture:** `task_file` (path, shape
`tasks/TASK-YYYYMMDD-{slug}.md`), `task_title` (H1 after the
colon), `task_type` (`feature` | `bug` | `refactor` | `spike`),
`task_estimate` (`S` | `M` | `L`).

**Failure modes:**
- `$ARGUMENTS` is empty → STOP with
  `error-templates.md#usage-missing-args` (`command=task_create`,
  `argument_hint=<task description>`).
- Registered agent errors and the fallback spec is also missing →
  STOP with `error-templates.md#mcp-call-failed`
  (`tool=Agent[task-writer]`, `error=<verbatim>`).
- Agent returns no file on disk → STOP with the same template.

**Invariants after:** `task_file` exists on disk.

### Step 2 — Verify MCP connectivity

**Preconditions:** Step 1 succeeded.
**Action:** confirm the `mcp__mcp-github-issues__*` namespace is
callable.

**Failure modes:**
- Namespace unavailable → STOP with
  `error-templates.md#mcp-not-connected`
  (`command=task_create`). The task file from Step 1 stays on disk
  untouched.

### Step 3 — Resolve MCP project

**Preconditions:** MCP connected.
**Action:** apply `_shared/project-resolution.md`.
**Capture:** `project` (string key).

**Failure modes:** as defined in `_shared/project-resolution.md`.

### Step 4 — Prepare the Issue payload

**Preconditions:** `task_file` exists; `project` resolved.
**Action:**

1. Read `task_file` in full.
2. The **Issue title** is `task_title` (captured in Step 1).
3. The **Issue body** is the file contents verbatim, minus the H1
   title line. No summarisation, no reformatting, no wrapper
   text, no references back to the local path.
4. The **type** for the MCP is mapped from `task_type`:

   | task-writer `task_type` | MCP `type` |
   |---|---|
   | `feature`  | `feature` |
   | `bug`      | `bug`     |
   | `refactor` | `task`    |
   | `spike`    | `task`    |

**Capture:** `issue_title`, `issue_body`, `mcp_type`.

**Forbidden in `issue_body`:**
- Any reference, link, or mention of the local task file path
  (`See local task spec: tasks/...`, `Local file:`,
  `tasks/TASK-*`).
- Any phrase implying the canonical version lives elsewhere.

**Failure modes:** none — this is a pure transformation step; any
I/O failure surfaces in Step 5 or Step 6.

### Step 5 — Create the draft

**Preconditions:** payload ready (Step 4).
**Action:** call `mcp__mcp-github-issues__create_task_draft` with:

- `project` — `project`
- `title` — `issue_title`
- `context` — `issue_body`
- `type` — `mcp_type`
- `checklist` — `[]`
- `files` — `[]`

**Capture:** `draft_path` (absolute path returned by MCP).

**Failure modes:**
- MCP call fails → STOP with
  `error-templates.md#mcp-call-failed`
  (`tool=create_task_draft`, `error=<verbatim>`). `task_file`
  stays on disk.

### Step 6 — Publish the Issue

**Preconditions:** `draft_path` captured.
**Action:** call `mcp__mcp-github-issues__publish_issue` with
`project` and `draftFile=draft_path`. Do **not** ask the user to
confirm — this command is one-pass.
**Capture:** `issue_number` (integer), `issue_url` (string).

**Failure modes:**
- MCP call fails → STOP with
  `error-templates.md#mcp-call-failed`
  (`tool=publish_issue`, `error=<verbatim>`). `task_file` stays on
  disk. Mention `draft_path` in the STOP message so the user can
  retry publication manually.

### Step 7 — Record the Issue number in the task file

**Preconditions:** `issue_number` and `issue_url` captured.
**Action:** edit `task_file` to insert a new line immediately after
the `**Status:** todo` line:

```
**GitHub Issue:** #{issue_number} — {issue_url}
```

Use the Edit tool with an exact `old_string` / `new_string` match
on `**Status:** todo` plus the following blank line, inserting the
`**GitHub Issue:**` line between them. Do not modify any other
content.
**Capture:** none.

**Failure modes:**
- Edit fails (e.g., `**Status:**` line missing because the template
  was altered) → do **not** STOP. The Issue was already published.
  Emit the Step 8 report with a `Header update:` note asking the
  user to paste the line manually.

### Step 8 — Report

**Preconditions:** Steps 1–7 attempted.
**Action:** emit the `task_create` template from
`_shared/report-templates.md`:

```
Task file:     {task_file}
GitHub Issue:  #{issue_number} — {issue_url}
Type:          {task_type}
Estimate:      {task_estimate}
```

If Step 7 failed to edit the header, append after the report:

```

Header update: manual — insert
  **GitHub Issue:** #{issue_number} — {issue_url}
after `**Status:** todo` in {task_file}.
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Never fabricate an Issue number or URL. If MCP does not return
  them, STOP.
- Never duplicate the task file. `task-writer` writes once; this
  command only edits the header.
- Never delete the task file on any failure. The user may retry.
- Never commit or push. Commits and PRs are out of scope.
- Never fall back to `gh` CLI. MCP-only.
- Issue body mirrors the local task file verbatim. No links back to
  the local path.
- No interactive confirmation between draft and publish. One pass.
- `task-writer` is the template source of truth. This command does
  not reshape sections.
