# Changelog

All notable changes are recorded here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [SemVer](https://semver.org/).

## [1.0.0] — 2026-11-06

First release. It covers everything from the initial template to the current
config.

### Features

- **Task workflow on GitHub.** `/task_create`, `/task_branch`, `/task_complete`,
  `/task_submit`, `/task_abort` and `/task_sync` work through the `gh` CLI and the
  `origin` repository. Task branches are `issues-{N}` from `develop`, and PRs
  target `develop`.
- **Git skills.** `git-commit`, `git-pr` and `git-release` replace the old
  `git-agent`. A release closes the Issues it ships.
- **Hooks.** `pr-base-guard` denies PRs that do not target `develop`.
  `task-offer` offers to create a task for feature requests. `rules_check` warns
  when `rules/` schemas lag behind the code.
- **Project `rules/`.** `rules-generator` (`init` / `audit`) and the
  `rules-writer` agent produce one minimal layout for any stack: a README map,
  `sync.yml`, C4 and ERD in Mermaid, and an OpenAPI contract generated from code
  plus Postman. Monorepos are supported.
- **CI templates in `ci-setup`.** Git-process checks, `main` → `develop`
  sync, a canonical test/production deploy workflow, and a `rules-sync` workflow.
- **New skills:** `team-lead` (orchestrator), `issue-templates`, `humanizer`,
  `grill-me-estimate`, `youtube-script-writer`, `blog-article-writer`,
  `skill-creator`, `agent-builder`.
- **Agents** for backend, frontend, database, API design, DevOps, QA, tests,
  security, performance, dependencies, docs, specs and rules. The API, database
  and DevOps agents keep `rules/` schemas in step.
- **`install.sh --prune` / `make prune`** removes stale links. The global
  `CLAUDE.md` is tracked in `global/` and linked into `~/.claude`.

### Security

- Project `CLAUDE.md` with rules for a public repository: no secrets, a scan
  of the staged diff, revoke before cleanup, no personal data, safe hooks, and
  minimal Actions permissions.
- Absolute home paths were removed from the agents, and the lint workflow gets a
  read-only token.

### Maintenance

- Linters for skills, agents and commands, plus shellcheck, markdownlint and
  yamllint scripts, a pre-push check, and unit tests in CI.
- LICENSE is detected as MIT, with copyright held by ilya_lyashchuk.
- The `mcp-github-issues` dependency was dropped in favour of `gh`.
