# Shared — MCP Project Resolution

Canonical algorithm for mapping the current repository to a
`project` key accepted by `mcp__mcp-github-issues__*` tools. Every
command that makes MCP calls must reference this file rather than
inline the steps.

## Preconditions

- `mcp__mcp-github-issues__*` namespace is available. If not, STOP
  with `error-templates.md#mcp-not-connected` (caller supplies
  `{command}`).
- `git` is usable in the current working directory.

## Algorithm

### Step R.1 — Inventory available projects

**Action:** call `mcp__mcp-github-issues__list_projects`.

**Capture:** `projects[]` (array of entries with at least `key`,
`owner`, `repo` fields).

**Failure modes:**
- MCP call fails → STOP with `error-templates.md#mcp-call-failed`,
  passing the verbatim MCP error.
- `projects[]` is empty → STOP with
  `error-templates.md#projects-yaml-empty`.

### Step R.2 — Resolve the local repo identity

**Action:** run

```bash
git remote get-url origin
basename "$(git rev-parse --show-toplevel)"
```

**Capture:**
- `origin_url` (may be empty if no `origin` remote).
- `repo_basename` (folder name of the repo root).

**Failure modes:**
- `git rev-parse --show-toplevel` fails (not a git repo) → STOP with
  `error-templates.md#not-a-git-repo`.
- `git remote get-url origin` fails → treat `origin_url` as empty
  and continue. This is **not** a STOP condition.

### Step R.3 — Match a project entry

Iterate `projects[]` and collect `matches[]` where **either** holds:

- `{owner}/{repo}` from the entry appears as a substring of
  `origin_url`, OR
- `entry.repo == repo_basename`.

**Capture:** `matches[]` (subset of `projects[]`).

### Step R.4 — Decide

**Preconditions:** `matches[]` populated from Step R.3.

**Action:** branch on the count:

- **Exactly one match** → `project = matches[0].key`. Done.
- **Zero matches** → STOP with
  `error-templates.md#project-not-found`, enumerate `projects[]`
  so the user can pick.
- **Multiple matches** → ask the user which `key` to use, offering
  `matches[]` as the shortlist. Wait for the reply; do not pick
  silently.

**Capture:** `project` (string key).

## Invariants after

- `project` is a key that exists in `projects[]`.
- The user was never prompted unless Step R.4 genuinely had
  ambiguity. Exactly-one-match is silent.

## Caching

Within a single command invocation, call this algorithm **at most
once** and reuse `project` for every subsequent MCP call. Do not
re-resolve per step.

## Forbidden

- Inventing a `project` key that is not in `projects[]`.
- Falling back to `gh` CLI or GraphQL to look up the repo.
- Skipping Step R.2 because "the URL already tells us owner/repo".
  Project keys are decided by the MCP registry, not by the URL.
