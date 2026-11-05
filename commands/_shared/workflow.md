# Shared — Command Workflow Overview

This file is the authoritative description of how the `/task_*`
commands chain together. Each command's body references it rather
than restating the whole flow.

## Canonical flow (happy path)

```
┌───────────────┐     ┌────────────────────────────────────────┐
│ /task_create  │ ──▶ │ /task_complete                         │
│ (spec + issue)│     │  ├─ auto-invokes /task_branch          │
│               │     │  │   (issues-{N} prepared here)        │
│               │     │  ├─ team-lead skill (routes to 1 agent)│
│               │     │  └─ /task_submit (commits → PR)        │
└───────────────┘     └────────────────────┬───────────────────┘
                                           │
                                           ▼
                                 ┌─────────────────┐
                                 │   PR on GitHub  │
                                 └─────────────────┘
```

`/task_branch` can also be invoked manually (standalone) at any
time — it remains a self-contained command. When invoked from inside
`/task_complete`, it is called automatically in Step 2.5.

Delivery-only shortcut (work done manually on the branch):

```
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│ /task_create │ ──▶ │ /task_branch │ ──▶ │  /task_submit  │
└──────────────┘     └──────────────┘     └────────┬───────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │   PR on GitHub  │
                                         └─────────────────┘
```

Abort branch:

```
┌──────────────┐     work in progress, no PR wanted
│ /task_abort  │ ──▶ delete branch, comment issue, update state
└──────────────┘
```

Periodic reconciliation (cron or manual):

```
┌────────────┐    GitHub Issues ↔ tasks/ ↔ github-tasks.json
│ /task_sync │
└────────────┘
```

## Per-command contract matrix

| Command | Inputs | Reads | Writes | Invokes | Idempotent? |
|---|---|---|---|---|---|
| `/task_create` | task description | task file (format gate) | `tasks/*.md`, GitHub Issue, `github-tasks.json` record | `spec-writer` agent, `gh` CLI | No (creates every time) |
| `/task_branch` | URL or task-file path | task file, git state | git branch | — | Yes (re-enters existing branch) |
| `/task_complete` | URL or task-file path | task file, git state, GitHub (`gh`) | nothing directly (delegates) | `/task_branch`, `team-lead` skill, `/task_submit` | Yes (branch re-enter + team-lead + submit all idempotent) |
| `/task_submit` | (branch-derived) | git state, GitHub (`gh`), task file | commits, remote branch, PR | `git-commit` skill, `gh` CLI | Yes (reuses existing PR) |
| `/task_abort` | (branch-derived) | git state, GitHub (`gh`), `github-tasks.json` | deletes branch, comments Issue, updates JSON | `gh` CLI | Yes |
| `/task_sync` | — | GitHub (`gh`), `github-tasks.json`, `tasks/` | `github-tasks.json`, new `tasks/*.md`, Issue comments | `gh` CLI | Yes |

## State channels

Every cross-command data flow is one of the following — nothing
else is allowed (see `_contract.md` §8):

1. **`$ARGUMENTS`** — user-typed input. Commands that accept a task
   reference use the same shape: `<tasks/TASK-*.md path | GitHub
   issue URL>`.
2. **Git branch name.** Canonical name `issues-{N}`; everything
   after the hyphen is the **Issue number** as a positive integer.
3. **Task-file header.** Line `**GitHub Issue:** #{N} — {url}`
   immediately after `**Status:** todo`.
4. **`github-tasks.json`.** Single JSON object keyed by full Issue
   URL. Managed by `/task_sync` and `/task_abort`; `/task_create`
   only inserts the record for the Issue it just opened. Other
   commands do not touch it.
5. **GitHub state.** Issues, comments, PRs via the `gh` CLI,
   targeting the `origin` repository (`owner/repo` from
   `_shared/repo-resolution.md`). No project registry.
6. **Sub-command outputs.** When one command invokes another
   (`/task_complete` → `/task_submit`), only the fields the parent
   explicitly captures are used.

## Preconditions by command

| Command | Must hold before running |
|---|---|
| `/task_create` | `gh` available & authenticated; `tasks/` exists or can be created |
| `/task_branch` | Clean working tree; `origin/develop` exists; input resolves to an Issue number |
| `/task_complete` | `gh` available & authenticated if input is a URL; clean working tree and synced `develop` are verified by `/task_branch` (Step 2.5) |
| `/task_submit` | Currently on `issues-{N}`; `gh` available & authenticated |
| `/task_abort` | Currently on `issues-{N}` OR Issue number passed explicitly |
| `/task_sync` | `gh` available & authenticated |

## Non-goals (explicitly out of scope)

- **Inline branch switching** — `/task_complete` delegates all
  branch preparation to `/task_branch` (Step 2.5); it never switches
  branches itself. `/task_submit` refuses to operate on the wrong
  branch and does not "fix" it. Only `/task_branch` and `/task_abort`
  directly manipulate the branch state.
- **Force-push recovery.** Never. Any push rejection is a STOP.
- **Project-key registry.** Removed. GitHub access goes through the
  `gh` CLI against the `origin` repository; if `gh` is missing or
  unauthenticated, STOP.
- **Reopening / closing GitHub Issues.** `/task_sync` comments only.
  `/task_abort` comments + (optionally) closes explicitly. No other
  command mutates Issue state.
- **Automatic status transitions in task files.** The `**Status:**`
  field in `tasks/*.md` is informational and currently
  unmaintained; the live status lives in `github-tasks.json`.

## Invocation-context signals

When `/task_complete` invokes `/task_submit`, the invoked command
receives additional context that changes two decisions:

- **Branch re-check** — `/task_submit` still performs the check
  (cheap, and the contract says each command is self-contained),
  but the failure message points at `/task_complete`, not at
  `/task_create`.
- **PR body source** — when the caller is `/task_complete` and a
  `team_lead_report` is available, `/task_submit` uses its summary
  as the PR body. Otherwise it generates the body from
  `git log origin/develop..HEAD`.

This signal is passed as a named variable in the invocation prompt;
see `/task_complete`'s delivery step for the exact shape.
