# Commands

Slash-commands that orchestrate the task lifecycle: create, branch,
execute, deliver, abort, sync.

## Foundation files (read these first)

| File | Purpose |
|---|---|
| [`_contract.md`](_contract.md) | Canonical semantics of STOP, invoke, capture, verbatim. Every command references it. |
| [`_shared/workflow.md`](_shared/workflow.md) | How the commands chain together. Diagrams and per-command contract matrix. |
| [`_shared/repo-resolution.md`](_shared/repo-resolution.md) | `gh`-based `owner/repo` resolution + gh preflight (shared by every command that touches GitHub). |
| [`_shared/error-templates.md`](_shared/error-templates.md) | Canonical STOP messages, keyed by identifier. |
| [`_shared/report-templates.md`](_shared/report-templates.md) | Canonical final-report layouts per command. |

## Command reference

| Command | Role | Input | Output |
|---|---|---|---|
| [`/task_create`](task_create.md) | Create task file + GitHub Issue | task description | `tasks/TASK-*.md` + Issue |
| [`/task_branch`](task_branch.md) | Prepare `issues-{N}` branch | task path or Issue URL | branch checked out |
| [`/task_complete`](task_complete.md) | Execute task end-to-end (team-lead skill + delivery) | task path or Issue URL | PR on GitHub |
| [`/task_submit`](task_submit.md) | Delivery-only: commits → push → PR | (branch-derived) | PR on GitHub |
| [`/task_abort`](task_abort.md) | Abandon a branch, comment the Issue | reason string | branch deleted, Issue commented |
| [`/task_sync`](task_sync.md) | Reconcile GitHub ↔ `github-tasks.json` ↔ `tasks/` | — | updated JSON + new task files |

## Utility commands

Contract-compliant commands outside the task lifecycle:

| Command | Role | Input | Output |
|---|---|---|---|
| [`/prog_time_writer`](prog_time_writer.md) | Generate a prog-time article (essay, senior-dev voice) seeded from snipp.ru and publish it as a WordPress draft | optional topic (`PHP`/`Laravel`/`Docker`/`Python`/`JavaScript`) | `.md` artifact + draft post on prog-time |

`/prog_time_writer` requires the `prog-time-writer` MCP server to be
registered (in `.mcp.json` or your `~/.claude` settings) and
connected. It sources an idea from snipp.ru, checks prog-time for
near-duplicates, writes the article via the `blog-article-writer`
skill, and publishes it as a draft — all WordPress access goes
through the MCP.

## Happy path

```
/task_create "<intent>"       # writes tasks/TASK-*.md + opens Issue #N
/task_branch tasks/TASK-*.md  # switches to issues-N, synced from develop
/task_complete tasks/TASK-*.md
    ├── team-lead skill routes to one agent
    └── /task_submit         # commits via git-commit, pushes, opens PR
```

Result: PR open on GitHub with `Closes #N`.

## Delivery-only path

When the task was done manually on the branch and `team-lead` is
not needed:

```
/task_create "<intent>"
/task_branch tasks/TASK-*.md
# ... user does the work ...
/task_submit
```

## Abandon path

```
# on branch issues-N
/task_abort "not worth pursuing — scope folded into #M"
```

## Periodic reconciliation

```
/task_sync     # e.g. from a cron or a scheduled agent
```

## What these commands will **not** do

- Switch branches silently. Only `/task_branch` and `/task_abort`
  touch branches.
- Force-push or force-delete remote branches. Never.
- Use a project-key registry. GitHub access goes through the `gh`
  CLI against the `origin` repository; if `gh` is missing or
  unauthenticated, the command STOPs and waits.
- Reopen / close GitHub Issues automatically.
- Rewrite `github-tasks.json` silently when it is malformed.
- Fabricate Issue numbers or PR URLs.

See `_contract.md` §5 for the full forbidden list.

## Extending the command set

Use [`task_example.md`](task_example.md) as a reference skeleton:
copy it, rename it to `commands/task_<your_command>.md`, and
replace the step bodies with your own logic. It demonstrates every
required element of the contract and passes
`python3 scripts/lint_commands.py` as-is.

A new command is contract-compliant when it:

1. Declares `contract: _contract.md` in its frontmatter.
2. Cites `_contract.md` in the first body paragraph.
3. Uses the step anatomy from `_contract.md` §6
   (`Preconditions / Action / Capture / Failure modes /
   Invariants after`).
4. References `_shared/error-templates.md` for every STOP message
   (add new keys there rather than inlining text).
5. References `_shared/repo-resolution.md` for GitHub repo
   resolution rather than inlining the algorithm.
6. Ends with a Report step using a template from
   `_shared/report-templates.md` (add a new section there if the
   command's shape is genuinely new).
7. Passes `python3 scripts/lint_commands.py`.
