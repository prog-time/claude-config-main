# Shared — Repo Resolution

Canonical answer to two questions every command that touches GitHub
asks: **which repository** and **which branch PRs go into**.

- **Repository = the `origin` remote.** Always. Not `upstream`, not
  whatever `gh` picks as its default remote, not a project registry.
- **Integration branch = `develop`.** Task branches are cut from
  `origin/develop` and every Pull Request targets `develop`. `main` is
  never a PR base from Claude Code — PRs into `main` are opened by
  humans. A PreToolUse hook (`hooks/pr-base-guard.py`) denies any
  `gh pr create` / MCP PR call whose base is not `develop`.

## Preconditions

- `gh` is installed and authenticated. If not, STOP with
  `error-templates.md#gh-not-available` (caller supplies `{command}`).
- `git` is usable in the current working directory.

## Algorithm

### Step R.1 — Read the `origin` URL

**Action:** `git remote get-url origin`.
**Capture:** `origin_url`.

**Failure modes:**
- Not inside a git repo → STOP with
  `error-templates.md#not-a-git-repo`.
- No `origin` remote, or `origin_url` does not point at `github.com`
  → STOP with `error-templates.md#origin-not-github`
  (`origin_url=<value or "none">`).

### Step R.2 — Resolve the repo slug from `origin`

**Action:** let `gh` canonicalise the slug of exactly that remote:

```bash
gh repo view "{origin_url}" --json nameWithOwner -q .nameWithOwner
```

**Capture:** `repo_slug` (shape `owner/repo`).

**Failure modes:**
- `gh` is missing or unauthenticated → STOP with
  `error-templates.md#gh-not-available` (`{command}`).
- Any other `gh repo view` error → STOP with
  `error-templates.md#tool-call-failed` (`tool=gh repo view`,
  `error=<verbatim>`).

## Invariants after

- `repo_slug` is a non-empty `owner/repo` string naming the `origin`
  repository.
- **Every** subsequent `gh` call in the command passes
  `-R {repo_slug}`. Never rely on `gh`'s implicit remote choice: with
  several remotes (`origin` + `upstream`) it may pick the wrong one.
- Every PR call passes `--base develop`; every branch sync uses
  `origin/develop`.

## Caching

Within a single command invocation, resolve `repo_slug` **at most
once** and reuse it for every subsequent step. Do not re-resolve per
call.

## Forbidden

- Reintroducing a project-key registry or a `projects.yaml` lookup.
- Resolving the repo from any remote other than `origin`.
- Hand-parsing `owner/repo` out of `origin_url` — `gh repo view`
  returns it canonically (case, renames, redirects).
- Opening, retargeting, or suggesting a PR with base `main`.
