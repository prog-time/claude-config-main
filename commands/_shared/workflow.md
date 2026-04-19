# Shared — Command Workflow Overview

This file is the authoritative description of how the `/task_*`
commands chain together. Each command's body references it rather
than restating the whole flow.

## Canonical flow (happy path)

```
┌───────────────┐     ┌──────────────┐     ┌────────────────┐
│ /task_create  │ ──▶ │ /task_branch │ ──▶ │ /task_complete │
│ (spec + issue)│     │ (issues-{N}) │     │ (team-lead +   │
│               │     │              │     │  /task_submit) │
└───────────────┘     └──────────────┘     └────────┬───────┘
                                                    │
                                                    ▼
                                          ┌─────────────────┐
                                          │   PR on GitHub  │
                                          └─────────────────┘
```

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
| `/task_create` | task description | project registry | `tasks/*.md`, GitHub Issue | `task-writer` agent, MCP | No (creates every time) |
| `/task_branch` | URL or task-file path | task file, git state | git branch | — | Yes (re-enters existing branch) |
| `/task_complete` | URL or task-file path | task file, git state, MCP | nothing directly (delegates) | `team-lead`, `/task_submit` | Yes (team-lead + submit both idempotent) |
| `/task_submit` | (branch-derived) | git state, MCP, task file | commits, remote branch, PR | `git-agent` skill, MCP | Yes (reuses existing PR) |
| `/task_abort` | (branch-derived) | git state, MCP, `github-tasks.json` | deletes branch, comments Issue, updates JSON | MCP | Yes |
| `/task_sync` | — | GitHub, `github-tasks.json`, `tasks/` | `github-tasks.json`, new `tasks/*.md`, Issue comments | MCP | Yes |

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
   URL. Managed by `/task_sync` (and `/task_abort`); other commands
   do not touch it.
5. **GitHub state.** Issues, comments, PRs via
   `mcp__mcp-github-issues__*`. No `gh` CLI, ever.
6. **Sub-command outputs.** When one command invokes another
   (`/task_complete` → `/task_submit`), only the fields the parent
   explicitly captures are used.

## Preconditions by command

| Command | Must hold before running |
|---|---|
| `/task_create` | MCP connected; `tasks/` exists or can be created |
| `/task_branch` | Clean working tree; `main` branch exists; input resolves to an Issue number |
| `/task_complete` | Currently on `issues-{N}` (the same `{N}` as the input resolves to); MCP connected if input is a URL |
| `/task_submit` | Currently on `issues-{N}`; MCP connected |
| `/task_abort` | Currently on `issues-{N}` OR Issue number passed explicitly |
| `/task_sync` | MCP connected |

## Non-goals (explicitly out of scope)

- **Automatic branch switching** — only `/task_branch` and
  `/task_abort` touch branches. `/task_complete` and `/task_submit`
  refuse to operate on the wrong branch; they do not "fix" it.
- **Force-push recovery.** Never. Any push rejection is a STOP.
- **`gh` CLI fallback.** Never. If MCP is unavailable, STOP.
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
  `git log origin/main..HEAD`.

This signal is passed as a named variable in the invocation prompt;
see `/task_complete`'s delivery step for the exact shape.
