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

## `gh-not-available`

Placeholders: `{command}`.

```
GitHub CLI (`gh`) is not available or not authenticated. Install it
and run `gh auth login`, then retry /{command}.
```

## `tool-call-failed`

Placeholders: `{tool}`, `{error}`.

```
`{tool}` failed. The command cannot continue.

error:
{error}
```

## `not-a-git-repo`

No placeholders.

```
Current directory is not inside a git repository. Run /task_* from
a checked-out repo.
```

## `origin-not-github`

Placeholders: `{origin_url}`.

```
The `origin` remote is `{origin_url}`, not a GitHub repository.
The project repository is always `origin`: add or fix it with
`git remote add origin <github url>` / `git remote set-url origin
<github url>` and retry.
```

## `issue-repo-mismatch`

Placeholders: `{url}`, `{repo_slug}`.

```
Issue `{url}` belongs to a different repository than `origin`
(`{repo_slug}`). Open the Issue in `{repo_slug}`, or run the command
from that repository's checkout.
```

## `develop-missing`

No placeholders.

```
`origin/develop` does not exist. Every Pull Request targets
`develop`, so create it first (e.g. `git switch -c develop
origin/main && git push -u origin develop`) and retry.
```

## `issue-format-invalid`

Placeholders: `{path}`, `{missing}` (newline-separated `- {section}`
lines).

```
Task file `{path}` is missing required sections, so the GitHub Issue
would not match the canonical format. Missing:

{missing}

Fix the task file (or re-run /task_create so spec-writer regenerates
it) and retry.
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

## `develop-switch-failed`

Placeholders: `{error}`.

```
Failed to switch to `develop`.

error:
{error}
```

## `develop-pull-failed`

Placeholders: `{error}`.

```
`git pull origin develop` did not complete cleanly. Resolve the
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
`git merge develop` into `{branch}` produced a conflict. Resolve
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
`git-commit` could not produce a commit. Fix the underlying issue
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
Opening the Pull Request via `gh pr create` failed.

error:
{error}
```

## `team-lead-blocked`

Placeholders: `{outcome}` (either `blocked` or `partial`).

```
team-lead skill ended with outcome `{outcome}`. Delivery
(commits, push, PR) is skipped. Inspect the team-lead result below
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

## `prog-time-not-connected`

Placeholders: `{command}`.

```
prog-time-writer MCP is not connected. Register it in .mcp.json (or
your ~/.claude settings) and reconnect, then retry /{command}.
```

## `topic-not-allowed`

Placeholders: `{topic}`, `{allowed}`.

```
`{topic}` is not a supported topic. Pass one of: {allowed}
(or no argument to auto-pick), then retry.
```

## `no-sites`

No placeholders.

```
prog-time-writer returned an empty site list. Configure at least one
WordPress site on the MCP server and retry.
```

## `snipp-unreachable`

Placeholders: `{error}`.

```
Could not source an idea from snipp.ru. The command needs at least
one usable idea in the allowed topics before it writes anything.

error:
{error}
```

## `all-candidates-duplicate`

Placeholders: `{collisions}` (newline-separated
`- {candidate title} → {existing post title} ({url})` lines).

```
Every candidate idea already has a near-duplicate on prog-time.
Nothing was written or published. Collisions:

{collisions}

Re-run later, or pass a different topic, to seed fresh ideas.
```

## `category-not-found`

Placeholders: `{topic}`, `{site}`.

```
No category on `{site}` matches the topic `{topic}`. Create the
category on the WordPress site (or pick a different topic) and retry.
```

## `article-generation-failed`

Placeholders: `{error}`.

```
The blog-article-writer skill did not produce a readable article
file. Nothing was published.

error:
{error}
```

## `unexpected-post-status`

Placeholders: `{status}`.

```
publish_post returned status `{status}`, expected `draft`. The post
was not in the expected state; this command will not edit, delete,
or re-publish it. Inspect the post on prog-time and resolve manually.
```
