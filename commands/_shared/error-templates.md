# Shared — Error Templates

Canonical STOP messages. Every command's Failure mode references a
key from this file instead of formulating the text ad-hoc. Placeholders
in `{curly_braces}` are substituted by the caller; everything else
is emitted verbatim (see `_contract.md` §4).

When a step references a key here, the emitted message is:

1. The fenced block under that key, with placeholders substituted.
2. Followed, if the template permits, by the underlying tool error
   in a nested code fence labelled `error`.

No other wrapping, no preamble, no "Here is the error:" prefix.

---

## `mcp-not-connected`

Placeholders: `{command}`.

```
mcp-github-issues is not connected. Register it in .mcp.json or
~/.claude/settings.json and retry /{command}.
```

## `mcp-call-failed`

Placeholders: `{tool}`, `{error}`.

```
MCP call `{tool}` failed. The command cannot continue.

error:
{error}
```

## `not-a-git-repo`

No placeholders.

```
Current directory is not inside a git repository. Run /task_* from
a checked-out repo.
```

## `projects-yaml-empty`

No placeholders.

```
mcp-github-issues returned an empty project list. Add this repo to
projects.yaml (or the MCP's project registry) and retry.
```

## `project-not-found`

Placeholders: `{repo_basename}`, `{projects_list}` (newline-separated
`- {key} — {owner}/{repo}` lines).

```
No project in the mcp-github-issues registry matches this repo
(`{repo_basename}`). Available projects:

{projects_list}

Re-run with a project key explicitly, or add this repo to the
registry and retry.
```

## `usage-missing-args`

Placeholders: `{command}`, `{argument_hint}`.

```
Usage: /{command} {argument_hint}
```

## `malformed-issue-url`

Placeholders: `{url}`.

```
The URL `{url}` does not match
`https://github.com/{{owner}}/{{repo}}/issues/{{N}}`. Fix the URL
and retry.
```

## `missing-issue-number`

No placeholders.

```
This task file has no linked GitHub Issue. Run /task_create again,
or add a line

  **GitHub Issue:** #N — <url>

immediately after the `**Status:** todo` line (third line of the
task header block) and retry.
```

## `missing-task-file`

Placeholders: `{path}`.

```
Task file `{path}` does not exist or is not inside tasks/. Check
the path and retry.
```

## `dirty-tree`

Placeholders: `{command}`, `{status_output}`.

```
Working tree is dirty. Commit or stash changes, then retry /{command}.

git status:
{status_output}
```

## `main-switch-failed`

Placeholders: `{error}`.

```
Failed to switch to `main`.

error:
{error}
```

## `main-pull-failed`

Placeholders: `{error}`.

```
`git pull origin main` did not complete cleanly. Resolve the
conflict or rejected update manually, then retry.

error:
{error}
```

## `branch-create-failed`

Placeholders: `{branch}`, `{error}`.

```
Failed to create branch `{branch}`.

error:
{error}
```

## `merge-conflict`

Placeholders: `{branch}`, `{error}`.

```
`git merge main` into `{branch}` produced a conflict. Resolve
manually (or `git merge --abort` to bail) and retry.

error:
{error}
```

## `branch-mismatch`

Placeholders: `{current}`, `{expected}`, `{next_command}`,
`{argument_hint}`.

```
Current branch is `{current}`, expected `{expected}`.
Run /{next_command} {argument_hint} first to prepare the branch,
then retry.
```

## `branch-not-issues`

Placeholders: `{current}`.

```
Current branch `{current}` does not match `issues-{N}`.
Run /task_create to open a GitHub Issue, then /task_branch to
prepare the branch, then retry.
```

## `nothing-to-submit`

Placeholders: `{branch}`.

```
Nothing to submit: working tree is clean and `{branch}` is in sync
with origin.
```

## `commit-failed`

Placeholders: `{error}`.

```
`git-agent` could not produce a commit. Fix the underlying issue
(lint, hook, signing) and retry — do not bypass with --no-verify.

error:
{error}
```

## `push-rejected`

Placeholders: `{branch}`, `{error}`.

```
`git push -u origin {branch}` was rejected. Resolve divergence
manually (pull / rebase) and retry. This command never force-pushes.

error:
{error}
```

## `pr-create-failed`

Placeholders: `{error}`.

```
Opening the Pull Request via mcp-github-issues failed.

error:
{error}
```

## `team-lead-blocked`

Placeholders: `{outcome}` (either `blocked` or `partial`).

```
team-lead pipeline ended with outcome `{outcome}`. Delivery
(commits, push, PR) is skipped. Inspect the pipeline report below
and decide how to proceed manually.
```

## `json-malformed`

Placeholders: `{path}`, `{error}`.

```
`{path}` is not valid JSON. Fix the file by hand and retry — this
command will not rewrite it silently.

error:
{error}
```

## `closed-issue`

Placeholders: `{N}`, `{command}`.

```
Issue #{N} is closed on GitHub. /{command} will not operate on
closed issues. Reopen the issue or pick a different one.
```
