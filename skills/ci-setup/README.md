# ci-setup

Configures GitHub Actions CI by detecting the project's stack, fetching
reference workflow patterns from the canonical
[prog-time/workflows](https://github.com/prog-time/workflows) repo, and
generating `.github/workflows/*.yml` with exactly one job per check
(lint, type-check, unit-test, integration-test, build, security-scan).

## Triggers

- "set up CI"
- "configure GitHub Actions"
- "add a CI pipeline"
- "generate workflow files"
- "audit the CI setup"
- "настрой CI", "добавь GitHub Actions", "сделай workflow"

## Does not trigger for

- Docker / deployment scripts (use `devops-agent`)
- Running tests (use `qa-engineer`)
- Managing GitHub Actions secrets outside workflow files

## What it produces

- One `.github/workflows/*.yml` file per workflow
- One job per check with explicit `needs:` dependencies
- Dependency caching included by default
- No hardcoded secrets — only `${{ secrets.NAME }}` references
- A completion report with detected stack + job graph

## Installation

Picked up automatically after `make install` at the repository root.
