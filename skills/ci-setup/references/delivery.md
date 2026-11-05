# Delivery model (every project)

Load this file whenever a project deploys anywhere, and always when
generating or auditing a deploy workflow.

## The rules

| Environment | When it deploys | How |
|---|---|---|
| `test` | Automatically, when the `CI` workflow finishes **green on a push to `main`** | `workflow_run` on `CI`, `branches: [main]`, `conclusion == 'success'`, `event == 'push'` |
| `production` | On a **`v*` tag** push (`git tag v1.0.0 && git push --tags`), or **manually** via *Run workflow* | `push: tags: ['v*']` + `workflow_dispatch`, job `environment: production` |

Branch flow that feeds it: task branches → PR into `develop` → humans
merge `develop` into `main` → CI on `main` → `test` → tag `v*` →
`production`.

`production` approval: enable **Required reviewers** on the
`production` environment (Settings → Environments → production). The
deploy job then waits with a *Review deployments* button. This is a
repository setting, not YAML — list it in the report as a manual step.

## Canonical file

Start from `templates/deploy.yml` in this skill
(`~/.claude/skills/ci-setup/templates/deploy.yml` once installed).
Copy it to `.github/workflows/deploy.yml` and change only:

- `__DEPLOY_COMMAND__` → the project's real deploy command, taking the
  environment name (`test` / `production`) as its argument. Find it in
  `Makefile`, `deploy/`, `scripts/`, `package.json` scripts, existing
  workflows. **Never invent one** — if none exists, ask the user or
  hand off to `devops-agent` and leave the workflow unwritten.
- Deploy-step `env:` / `secrets` the command needs, as
  `${{ secrets.NAME }}` / `${{ vars.NAME }}` scoped to the environment.
- Extra setup steps the deploy command needs (language runtime, CLI).

Keep everything else: triggers, `if:` conditions, `verify-release`
gates, `concurrency` groups, environment names.

## Requirements on the CI workflow

- `name: CI` exactly — `workflow_run` matches by name.
- Triggers include `push` to `main` (and `develop`) and `pull_request`
  into `develop`:

  ```yaml
  on:
    push:
      branches: [main, develop]
    pull_request:
      branches: [develop]
  ```

- CI must not deploy. Deploys live only in `deploy.yml`.

## Invariants (check them in an audit)

1. Nothing deploys from `develop` or from feature branches.
2. `test` deploys only after a **successful** CI run on a **push** to
   `main`, checking out `workflow_run.head_sha` (the commit CI tested,
   not whatever `main` is now).
3. `production` deploys only from a ref whose commit is on `main` and
   has a green `CI` push run (`verify-release` job). The `verify-release`
   job runs *before* the approval gate so reviewers only see verified
   releases.
4. Each environment has its own `concurrency` group with
   `cancel-in-progress: false` — a deploy is never cancelled midway.
5. `deploy.yml` exists on the repository's default branch —
   `workflow_run` only fires for workflow files on the default branch.

## Manual steps to report

- Create environments `test` and `production` (Settings → Environments).
- On `production`: enable Required reviewers; optionally restrict
  *Deployment branches and tags* to `v*` tags and `main`.
- Add the deploy secrets to the matching environment, not to the repo.
