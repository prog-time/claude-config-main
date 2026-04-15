---
name: github-issues
description: |
  Manages GitHub Issues of the current project via the mcp-github-issues MCP
  server (exposed as "project-agent"). Creates drafts and publishes them as
  issues, closes existing issues, and posts comments. Use ALWAYS when the user
  says "create an issue", "open an issue", "close issue #N", "comment on issue",
  "add a task to the project", "создай задачу", "открой issue", "заведи issue",
  "закрой задачу", "закрой issue #N", "напиши комментарий к задаче",
  "прокомментируй issue", "добавь комментарий в issue", or asks to
  list/show/fetch issues in the project. Resolves the target project from
  projects.yaml by matching the current repository. Do NOT use for: pull
  requests, branch/PR creation, releases, arbitrary gh CLI calls, editing
  labels/milestones for their own sake, or any GitHub operation outside the
  Issues scope. Do NOT use if mcp-github-issues MCP is not connected — fall
  back to telling the user how to register it.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Edit
---

# github-issues

Orchestrates the `mcp-github-issues` MCP server (registered in Claude Code as
`project-agent`) to manage issues in the **current project's repository**.
Every operation runs through MCP tools — never via `gh` CLI, `curl`, or direct
GitHub API calls.

## Available MCP tools

These are provided by the `project-agent` MCP server. Call them as
`mcp__project-agent__<tool>`:

| Tool                | Purpose                                                  |
|---------------------|----------------------------------------------------------|
| `list_projects`     | List projects defined in `projects.yaml`                 |
| `list_issues`       | List issues in a project (state / label / assignee)      |
| `fetch_issue`       | Fetch full issue context (body + comments)               |
| `create_task_draft` | Save a structured draft `.md` locally (NOT on GitHub)    |
| `list_drafts`       | List unpublished drafts for a project                    |
| `publish_issue`     | Publish a draft as a GitHub Issue                        |
| `add_comment`       | Post a comment on an existing issue                      |
| `update_issue`      | Change state/title/assignee/labels (closing = state)     |

If `mcp__project-agent__*` tools are not available in the current session,
stop and tell the user:

```
The mcp-github-issues MCP server is not connected. Register it with:
  ./mcp.sh setup            # from the mcp-github-issues repo
Then reload this session.
```

## Order of operations

Follow this sequence for every request:

1. **Resolve the project** — figure out which key in `projects.yaml` matches
   the current repository (see Step 1).
2. **Interpret the intent** — create, close, or comment (see Steps 2–4).
3. **Call MCP tools** — never touch the GitHub API directly.
4. **Report the result** — show the issue URL / draft path / comment link.

## Step 1 — Resolve the project

The MCP requires a `project` argument that must match a key in
`projects.yaml`. Resolve it like this:

1. Call `mcp__project-agent__list_projects` — this returns every configured
   project with its `owner`, `repo`, and `tasksDir`.
2. Inspect the current repository:
   ```bash
   git remote get-url origin
   basename "$(git rev-parse --show-toplevel)"
   ```
3. Match a project when **either** is true:
   - `owner/repo` from `projects.yaml` appears in the `origin` URL, or
   - The repo folder name equals the project's `repo` field.
4. If exactly one match — use it silently.
5. If multiple matches — ask the user which one, listing the candidates.
6. If zero matches — do NOT invent a project name. Ask the user:
   ```
   No project in projects.yaml matches this repository
   (origin: <url>). Which project should I use?
   Available: <comma-separated keys from list_projects>
   ```
7. If `list_projects` returns an empty list — stop and tell the user to add
   their repo to `projects.yaml` first.

Cache the resolved `project` value for the whole conversation — do not call
`list_projects` repeatedly.

## Step 2 — Creating an issue

The MCP enforces a **draft → review → publish** flow. Respect it.

### 2a. Draft

Call `mcp__project-agent__create_task_draft` with:

- `project` — resolved key
- `title` — concise, imperative; no type prefixes
- `context` — WHY the task exists, not just WHAT; quote user words where
  possible
- `files` — affected paths if the user mentioned or you inferred them
- `checklist` — actionable items; omit if the user gave no scope signal
- `assignee` — only if the user asked
- `type` — `bug` | `feature` | `task` (default `task`)

The tool returns a local path like
`tasks/<project>/YYYY-MM-DD-<slug>.md`. Show that path and the rendered
Markdown body to the user. **Do not auto-publish.**

### 2b. Wait for review

Ask: *"Draft saved to `<path>`. Review it and confirm when I should publish,
or tell me what to change."*

If the user asks for edits:
- Small edits → use the `Edit` tool on the draft file directly.
- Large rewrites → call `create_task_draft` again with new inputs; then
  offer to delete the old draft via `Bash` (`rm <path>`) only after explicit
  user confirmation.

### 2c. Publish

Only after explicit user approval ("publish", "ок, публикуй", "go ahead",
"залей", "create it"), call `mcp__project-agent__publish_issue` with:

- `project` — resolved key
- `draftFile` — absolute path returned by `create_task_draft`
- `assignee` / `type` — only if the user changed them at publish time

Report the returned issue URL. The label is applied automatically from
`type` by the MCP (`bug` → `bug`, `feature` → `enhancement`, `task` →
`task`). Do NOT add duplicate labels via `update_issue`.

## Step 3 — Closing an issue

Parse the issue reference the user gave — it may be a number (`#42`, `42`)
or a full URL. Pass it as-is to the MCP; the server accepts both forms.

Call `mcp__project-agent__update_issue` with:

- `project` — resolved key
- `issue` — the number or URL
- `state: "closed"`

Only touch other fields (`title`, `assignee`, `add_labels`, `remove_labels`)
if the user asked for them in the same request.

If the user wants to leave a closing comment alongside closing, post it
**first** via `add_comment`, then call `update_issue` — this matches the
chronological order on the GitHub timeline.

### Reopening

If the user says "reopen issue #N", call `update_issue` with
`state: "open"`. Same project-resolution rules apply.

## Step 4 — Commenting on an issue

Call `mcp__project-agent__add_comment` with:

- `project` — resolved key
- `issue` — number or URL, as given
- `body` — the comment text; Markdown is supported

Preserve the user's exact wording when they dictate the comment. If they
describe the content in free form ("напиши, что баг воспроизводится только в
Safari"), draft the comment, show it, and ask for confirmation before
sending.

If the comment references code, include inline code fences / file paths so
the comment is useful without extra context.

## Step 5 — Listing / fetching (support operations)

When the user asks what's open, what's assigned to them, or wants full
context before acting:

- `list_issues` — filter by `state`, `label`, `assignee`; default
  `state: "open"`, `limit: 30`.
- `fetch_issue` — use before commenting or closing if the user's request is
  ambiguous ("close the login bug" — you must find which issue that is).

Never fabricate issue numbers. If you cannot resolve a reference, call
`list_issues` with a relevant filter and ask the user to pick.

## Rules

**Do:**

- Resolve the project from `projects.yaml` via `list_projects` on the first
  MCP call of the conversation.
- Respect the draft → review → publish flow for new issues.
- Pass issue references (number or URL) verbatim to the MCP.
- Show the resulting issue/comment URL or draft path after every successful
  operation.
- Surface MCP error messages verbatim — they are already structured.

**Do NOT:**

- Call `gh`, `curl`, or any direct GitHub API — always use the MCP.
- Publish a draft without explicit user approval.
- Invent a `project` key that is not in `projects.yaml`.
- Batch unrelated operations into one request (one action at a time unless
  the user asked for a batch).
- Add `Co-Authored-By`, signatures, or "generated by" footers to issue
  bodies or comments — the MCP already prepends a generated-by badge where
  it applies.
- Commit anything under `tasks/` (the `commit` skill already forbids it;
  drafts are meant to stay local).

## Examples

### Example 1 — Create a bug from a short description

**User:** создай issue: логин ломается после OAuth, редиректит обратно на
/login. Файл — `src/auth/callback.ts`.

**Assistant:**
1. `list_projects` → matches current repo to project `api`.
2. `create_task_draft` with `type: "bug"`, `title: "Fix login redirect loop
   after OAuth"`, `context: "<user quote + inferred details>"`,
   `files: ["src/auth/callback.ts"]`,
   `checklist: ["Reproduce locally", "Inspect session/token handling",
   "Add regression test"]`.
3. Shows draft path + rendered body. Asks for confirmation.

**User:** ок, публикуй

**Assistant:**
1. `publish_issue` with the draft path.
2. Reports: `Issue #42 created — https://github.com/acme/api/issues/42`.

### Example 2 — Close with a closing comment

**User:** close #38, it was shipped in v2.3.0

**Assistant:**
1. `add_comment` on issue `38` with body
   `Shipped in v2.3.0 — closing.`.
2. `update_issue` on issue `38` with `state: "closed"`.
3. Reports both URLs.

### Example 3 — Ambiguous close request

**User:** закрой задачу про падающие тесты

**Assistant:**
1. `list_issues` with `state: "open"` and lists candidates containing
   "test" / "падают" / "flaky".
2. Asks the user to pick a number — does NOT guess.

### Example 4 — Comment verbatim

**User:** напиши в issue #17 комментарий: "Воспроизводится только в Safari
17.4, в Chrome и Firefox всё ок."

**Assistant:**
1. `add_comment` on `17` with the exact text.
2. Reports the comment URL.

## Edge cases

- **No `projects.yaml` entry for the current repo** — ask the user; never
  guess. Offer to show existing keys from `list_projects`.
- **Repo has no `origin` remote** — ask the user explicitly which project to
  use.
- **MCP returns an auth / 404 error** — surface it verbatim; suggest
  checking the token in `.env` and that it has `repo` scope.
- **User asks to edit an already-published issue body** — `update_issue`
  does not edit the body (only state/title/assignee/labels). Tell the user
  this and offer to post a comment with the correction instead.
- **User asks to delete an issue** — GitHub's API doesn't support deletion
  via tokens. Tell the user and offer to close it with an explanatory
  comment.
- **Batch requests** ("close #10, #11, #12") — execute sequentially,
  reporting each. Stop on the first error and ask how to proceed.
