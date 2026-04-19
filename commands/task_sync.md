---
description: Sync GitHub Issues with local github-tasks.json — create missing local tasks, comment on done ones
argument-hint: (no arguments)
contract: _contract.md
---

# /task_sync

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Reconciles GitHub Issues of the current repository with a local
state file `github-tasks.json` at the repo root, materialises
missing `tasks/*.md` files for open issues, and posts a
one-paragraph "what was done" comment on issues marked `done`.

**`github-tasks.json` is the single source of truth** for what
this command acts on. `/task_sync` does not decide issue status on
its own — `status: 'open' | 'done'` is written by other commands /
agents.

No arguments.

## Workflow

### Step 1 — Ensure `github-tasks.json` exists

**Preconditions:** inside a git repo.
**Action:** check for `github-tasks.json` at the repo root
(`git rev-parse --show-toplevel`).
- Exists → read & parse.
- Missing → create with exactly `{}`.
**Capture:** `state` (parsed JSON object).

**Failure modes:**
- File exists but is malformed JSON → STOP with
  `error-templates.md#json-malformed`
  (`path=github-tasks.json`, `error=<verbatim>`). Never rewrite
  silently.
- Not a git repo → STOP with
  `error-templates.md#not-a-git-repo`.

### Step 2 — Verify MCP connectivity

**Preconditions:** `state` loaded.
**Action:** confirm the `mcp__mcp-github-issues__*` namespace.

**Failure modes:**
- Unavailable → STOP with
  `error-templates.md#mcp-not-connected`
  (`command=task_sync`).

### Step 3 — Resolve MCP project

**Preconditions:** MCP connected (Step 2).
**Action:** apply `_shared/project-resolution.md`.
**Capture:** `project` (string key).
**Failure modes:** as defined in `_shared/project-resolution.md`.

### Step 4 — Fetch open issues

**Preconditions:** `project` resolved.
**Action:** call `mcp__mcp-github-issues__list_issues` with
`project` and filter `is:open`.
**Capture:** `open_issues` (array; may be empty).

**Failure modes:**
- MCP call fails → STOP with
  `error-templates.md#mcp-call-failed`
  (`tool=list_issues`, `error=<verbatim>`).
- Empty list → **do not STOP.** Skip Step 5 and continue at
  Step 6 (existing JSON records still need processing).

### Step 5 — Add missing issues to `state`

**Preconditions:** `open_issues` non-empty.
**Action:** for each issue, build
`url = https://github.com/{owner}/{repo}/issues/{N}`. Then:

- If `url` is already a key in `state` → **skip; never modify the
  existing record** (no status update, no `local` overwrite, no
  flag changes). This rule applies **only** to Step 5.
- Otherwise → insert:

  ```json
  "{url}": { "status": "open", "local": "" }
  ```

Save `state` to disk after the loop.
**Capture:** `added_count` (integer).
**Failure modes:** none — every iteration either inserts or
skips; no individual insertion can fail independently.

### Step 6 — Post "done" comments (idempotent)

**Preconditions:** `state` reflects Step 5.
**Action:** for each record where `status == "done"`:

1. `close == true` → skip silently (comment already posted).
2. `local == "" or missing` → skip; append to `skipped_records`:
   `#{N} — no local file`. Do not fabricate a comment, do not use
   the Issue body as a fallback.
3. Otherwise:
   - Read the file at `local` (relative to repo root).
   - File missing on disk → append to `skipped_records`:
     `#{N} — local file missing`. Skip.
   - Generate a single paragraph (2–5 sentences) framed as "what
     was done", using the task's description sections
     (`## Что делаем`, `## Готово когда`, `## Как делаем`).
     Free-form prose, no bullets, no headers.
   - Call `mcp__mcp-github-issues__add_comment`.
   - Success → set `close: true` on the record, save `state`.
   - Failure → append to `errors`: `#{N} — <MCP error>`. Do **not**
     set `close: true` so the next run retries.

**Capture:** `comments_posted`, `comments_skipped` (count),
`skipped_records[]`, `errors[]`.

This step **never closes the GitHub issue**. It only comments.

**Failure modes:** per-record `add_comment` failures are collected
into `errors[]` (not STOP). The step as a whole cannot fail — it
either posts or records an error and moves on.

### Step 7 — Find open records missing local files

**Preconditions:** Step 6 completed.
**Action:** for each record where `status == "open"`:

1. `local` non-empty and file exists → skip (nothing to do).
2. `local` non-empty but file missing → append to `notes`:
   `#{N} — local path recorded but file missing`. Do not re-create;
   the user may have moved it on purpose.
3. `local == ""` → mark for Step 8.

**Capture:** `to_materialise[]`.
**Failure modes:** none — pure bookkeeping scan.

### Step 8 — Materialise missing local files

**Preconditions:** `to_materialise[]` populated.
**Action:** for each record marked:

1. Extract `{N}` from the URL key (`/issues/(\d+)$`).
2. Determine filename — **deterministic, no slug:**
   `tasks/TASK-{YYYYMMDD-today}-github-{N}.md`.
3. If a file matching `tasks/TASK-*-github-{N}.md` already exists
   (any date prefix) → reuse it as-is; jump to Step 9.
4. Fetch issue via `mcp__mcp-github-issues__fetch_issue`.
5. Map `Type` from labels (first match wins):

   | Label         | `Type`     |
   |---------------|------------|
   | `bug`         | `bug`      |
   | `enhancement` | `feature`  |
   | `task`        | `refactor` |
   | *(none)*      | `feature`  |

6. Write the file:

   ```markdown
   # TASK-{YYYYMMDD-today}-github-{N}: {issue title verbatim}

   **Type:** {mapped type}  
   **Size:** M  
   **Status:** todo

   **GitHub Issue:** #{N} — {full URL}

   {issue body verbatim}
   ```

   - `Type` and `Size` lines end with two trailing spaces.
   - `Size` is hardcoded `M` (GitHub Issues carry no size).
   - Issue body is verbatim — no sectioning, no trimming.

**Capture:** `files_created`, `files_already_present` (counts).

**Failure modes:**
- `fetch_issue` fails → append to `errors[]`:
  `#{N} — fetch_issue: <verbatim>`. Skip this record; do not STOP
  the whole command.
- Filesystem write fails → append to `errors[]`:
  `#{N} — write failed: <verbatim>`. Skip.

### Step 9 — Record local paths in `state`

**Preconditions:** Step 8 finished.
**Action:** for each record from Step 8 (created or reused),
set `local = "tasks/TASK-{YYYYMMDD-today}-github-{N}.md"`. Save
`state`.

This step **is** allowed to edit existing records (the Step-5
prohibition is scoped to Step 5 only).
**Capture:** `paths_updated` (integer).
**Failure modes:** none — the JSON write is atomic per record; any
malformed JSON would have already STOPed at Step 1.

### Step 10 — Report

**Preconditions:** Steps 1–9 completed (some may have been skipped
when `open_issues` was empty).
**Action:** emit the `task_sync` template from
`_shared/report-templates.md`:

```
/task_sync — done

Project: {owner/repo}

From GitHub: {len(open_issues)} open issues fetched
Added to github-tasks.json: {added_count}

Comments posted: {comments_posted}
Comments skipped: {comments_skipped}
  {skipped_records, one per line}

Local files created: {files_created}
Local files already present: {files_already_present}
Local paths updated in JSON: {paths_updated}

Notes:
  - Size: M hardcoded on files materialised from GitHub (the Issue
    carries no size metadata).
  {extra notes from Step 7, if any}

Errors:
  {errors, one per line — omit the section if empty}
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- `github-tasks.json` is the source of truth. Never infer `status`
  from git history, PR state, or branch merges.
- Step 5 is write-once. Existing JSON records are never modified
  there, regardless of what GitHub says. Steps 6 and 9 are
  allowed to edit records.
- Never close GitHub issues. Comments only.
- Never fabricate comment text. Missing `local` → skip with log.
- Never overwrite existing local task files. Reuse by
  `TASK-*-github-{N}.md` glob.
- Never use `gh` CLI. MCP-only.
- Filename slug comes from issue number, not title.
- JSON uses double quotes. Real JSON, not JSON5.
- `close: true` is the commented-flag. Set only after a successful
  `add_comment`; skipped forever unless manually reset.

## Edge cases

- **Empty `open_issues`** — skip Step 5, continue at Step 6.
- **Issue URL in JSON but not in GitHub's open list** — the issue
  may be closed on GitHub. `/task_sync` does not reconcile this;
  the record stays in JSON with its existing status.
- **`status: "done"` with `local: ""`** — skipped with a log line.
  Surfaced, not auto-healed.
- **`status: "done"`, `local` points at a now-missing file** —
  skipped with an error line. History matters for the summary; do
  not re-create.
- **Filename collision across dates** — impossible if issue numbers
  are unique per repo. `TASK-*-github-{N}.md` glob treats any
  existing file as "already present".
- **MCP rate limit in Step 6** — log the error verbatim, leave
  `close` unset, continue to the next record. No sleeping, no
  retry.
- **Repo has no `origin` remote** — project resolution falls back
  to matching by folder name (see
  `_shared/project-resolution.md`).
