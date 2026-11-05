---
description: Create a task file in tasks/ and a linked GitHub Issue via the gh CLI in one pass
argument-hint: <task description>
contract: _contract.md
---

# /task_create

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Orchestrates end-to-end task creation: produces a TASK file via the
`spec-writer` agent, validates that it matches the canonical format,
then creates a matching GitHub Issue with the `gh` CLI, and writes
the Issue number back into the task file header.

See `_shared/workflow.md` for where `/task_create` sits in the
overall chain.

**Input:** `$ARGUMENTS` — free-form task description (feature / bug
/ refactor / spike intent).

## Workflow

### Step 1 — Create the task file via `spec-writer`

**Preconditions:** `$ARGUMENTS` is non-empty.
**Action:** invoke the `spec-writer` agent via the Agent tool with
`$ARGUMENTS` as the task description.

**Fallback path.** If the registered `spec-writer` subagent type is
unavailable (e.g. `Agent type 'spec-writer' not found`), re-invoke
with `subagent_type: "general-purpose"` and inline the spec. Locate
it in this order:

1. `agents/spec-writer.md` (project-local)
2. `~/.claude/agents/spec-writer.md` (global)

Brief the fallback agent:

> You are acting as the **spec-writer** agent (its registered
> subagent type is unavailable in this session, so you're
> executing its spec directly). Follow the spec below verbatim —
> explore the project, classify type, pick estimate, fill every
> template section, write the file in one pass, no confirmation.
> Return only the spec-writer's canonical 5-line output (Created /
> Title / Type / Estimate / Open questions).
>
> --- spec-writer spec ---
> {contents of spec-writer.md}
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
  STOP with `error-templates.md#tool-call-failed`
  (`tool=Agent[spec-writer]`, `error=<verbatim>`).
- Agent returns no file on disk → STOP with the same template.

**Invariants after:** `task_file` exists on disk.

### Step 2 — Resolve the repo (gh preflight)

**Preconditions:** Step 1 succeeded.
**Action:** apply `_shared/repo-resolution.md`. This both confirms
`gh` is installed and authenticated and yields the target repo.
**Capture:** `repo_slug` (`owner/repo`).

**Failure modes:** as defined in `_shared/repo-resolution.md`
(`command=task_create`). The task file from Step 1 stays on disk
untouched.

### Step 3 — Validate the canonical format

**Preconditions:** `task_file` exists; `repo_slug` resolved.
**Action:** read `task_file` and confirm every required section of
the `spec-writer` template is present, so the Issue body will be
well-formed. Required:

- Header lines `**Type:**`, `**Size:**`, `**Status:**`.
- Section headers (verbatim): `## Что делаем`,
  `## Пользователь получает`, `## Готово когда`, `## Как делаем`,
  `## Файлы`, `## Не делаем в этой задаче`, `## Вопросы`,
  `## Связанные задачи`, `## Критерии приёмки (Definition of Done)`.

**Capture:** `missing_sections[]` (empty when valid).

**Failure modes:**
- One or more required sections absent → STOP with
  `error-templates.md#issue-format-invalid` (`path={task_file}`,
  `missing=<one "- {section}" line each>`). No Issue is created; the
  task file stays on disk so the user can fix it.

### Step 4 — Prepare the Issue payload

**Preconditions:** `task_file` exists; `repo_slug` resolved.
**Action:**

1. Read `task_file` in full.
2. The **Issue title** is `task_title` (captured in Step 1).
3. The **Issue body** is the file contents verbatim, minus the H1
   title line. Write it to a scratch file (e.g.
   `{scratchpad}/issue-body.md`) for `--body-file`. No
   summarisation, no reformatting, no wrapper text, no references
   back to the local path.
4. The **label** is mapped from `task_type`:

   | spec-writer `task_type` | gh `--label` |
   |---|---|
   | `feature`  | `enhancement` |
   | `bug`      | `bug`         |
   | `refactor` | `enhancement` |
   | `spike`    | `enhancement` |

**Capture:** `issue_title`, `body_file` (path), `issue_label`.

**Forbidden in `issue_body`:**
- Any reference, link, or mention of the local task file path
  (`See local task spec: tasks/...`, `Local file:`,
  `tasks/TASK-*`).
- Any phrase implying the canonical version lives elsewhere.

**Failure modes:** none — this is a pure transformation step; any
I/O failure surfaces in Step 5 or Step 6.

### Step 5 — Create the Issue

**Preconditions:** payload ready (Step 4).
**Action:** create the Issue in one pass — do **not** ask the user
to confirm:

```bash
gh issue create -R {repo_slug} --title "{issue_title}" --body-file {body_file} --label {issue_label}
```

`gh` prints the new Issue URL on stdout. Capture it as `issue_url`
and parse `issue_number` from the trailing `/issues/{N}`.

**Label fallback.** If `gh` fails *only* because the label does not
exist in the repo (`could not add label: '<label>' not found`),
retry the same command **without** `--label`. Record
`label_applied = false` for the Step 8 note. Any other failure is a
STOP.

**Capture:** `issue_number` (integer), `issue_url` (string),
`label_applied` (boolean).

**Failure modes:**
- `gh issue create` fails for any reason other than a missing label
  → STOP with `error-templates.md#tool-call-failed`
  (`tool=gh issue create`, `error=<verbatim>`). `task_file` stays on
  disk so the user can retry.

### Step 6 — Record the Issue number in the task file

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
  was altered) → do **not** STOP. The Issue was already created.
  Emit the Step 8 report with a `Header update:` note asking the
  user to paste the line manually.

### Step 7 — Register the task in `github-tasks.json`

**Preconditions:** `issue_url` captured; `task_file` exists.
**Action:** at the repo root (`git rev-parse --show-toplevel`):

- `github-tasks.json` **missing** → create it containing only this
  record.
- **Present and valid** → if `issue_url` is not a key, insert the
  record; if it is a key with empty `local`, set `local` only;
  otherwise leave the record untouched.

```json
"{issue_url}": { "status": "open", "local": "{task_file}" }
```

This links the Issue to its task file so `/task_sync` does not
materialise a second `TASK-*-github-{N}.md` for it.
**Capture:** `json_state` (`updated` | `failed`).

**Failure modes:**
- File exists but is malformed JSON, or the write fails → do
  **not** STOP (the Issue already exists) and never rewrite the file
  silently. Set `json_state = "failed"` and emit the Step 8 report
  with a `JSON record:` note.

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

If Step 6 failed to edit the header, append after the report:

```

Header update: manual — insert
  **GitHub Issue:** #{issue_number} — {issue_url}
after `**Status:** todo` in {task_file}.
```

If the label was dropped in Step 5 (`label_applied == false`),
append:

```

Label: skipped — `{issue_label}` does not exist in {repo_slug}.
Create the label and re-label the Issue manually if needed.
```

If Step 7 failed (`json_state == "failed"`), append:

```

JSON record: manual — add
  "{issue_url}": { "status": "open", "local": "{task_file}" }
to github-tasks.json (the file is malformed or could not be written).
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Never fabricate an Issue number or URL. If `gh` does not return
  them, STOP.
- Never duplicate the task file. `spec-writer` writes once; this
  command only edits the header.
- Never delete the task file on any failure. The user may retry.
- Never commit or push. Commits and PRs are out of scope.
- `github-tasks.json` is only ever extended (Step 7): never change
  an existing record's `status` or a non-empty `local`.
- GitHub access is `gh` CLI only. The Issue targets the `origin`
  repository (`repo_slug`); never reintroduce a project registry.
- Issue body mirrors the local task file verbatim. No links back to
  the local path.
- Format gate (Step 3) is mandatory: a task file missing canonical
  sections never becomes an Issue.
- One pass: no interactive confirmation before creating the Issue.
- `spec-writer` is the template source of truth. This command does
  not reshape sections.
