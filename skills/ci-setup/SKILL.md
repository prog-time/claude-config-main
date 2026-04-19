---
name: ci-setup
description: |
  Configures GitHub Actions CI for any project: detects the stack, fetches
  reference workflow patterns from https://github.com/prog-time/workflows,
  and generates `.github/workflows/*.yml` files where every check runs as
  its own independent job. Use ALWAYS when the user says "set up CI",
  "configure GitHub Actions", "add a CI pipeline", "generate workflow
  files", "audit the CI setup", "improve the workflow", "настрой CI",
  "добавь GitHub Actions", "сделай workflow", "настрой пайплайн",
  "проверь CI конфигурацию". Walks through stack detection, reference
  fetching, job graph planning, workflow generation, and optional audit
  of existing files. Do NOT use for: Docker or deployment scripts (use
  the `devops-agent`), running tests (use `qa-engineer`), or authoring
  GitHub Actions secrets/vars outside workflow files.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebFetch
---

# ci-setup

Generate or audit GitHub Actions workflows with the project's real stack
in mind. Every check is its own job. Dependencies are explicit via
`needs:`. Reference patterns come from a canonical external repo — never
invented.

## Workflow

### Step 1 — Detect the stack

Read project files to identify language, framework, package manager, and
test setup. Look for:

- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`,
  `composer.json`, `build.gradle`, `pom.xml` — language + package manager
- `CLAUDE.md`, `README.md`, `rules/`, `docs/` — conventions, existing
  CI expectations
- `.github/workflows/` — existing workflow files (read fully before
  touching)
- Test config: `jest.config.*`, `vitest.config.*`, `pytest.ini`,
  `phpunit.xml`, `cargo test`, `.eslintrc.*`, `mypy.ini`, etc.
- `Dockerfile`, `docker-compose.yml` — whether integration tests need
  services

Identify which checks apply based on what the project actually has:

| Signal | Check |
|---|---|
| Linter configured | `lint` job |
| Type checker (tsc, mypy, pyright) configured | `type-check` job |
| Unit tests present | `unit-test` job |
| Integration tests present (separate suite, needs DB/services) | `integration-test` job |
| Build step present (compile, bundle) | `build` job |
| Security scanner available or warranted | `security-scan` job |

### Step 2 — Fetch reference patterns (mandatory)

Before writing any YAML, fetch
<https://github.com/prog-time/workflows> and read every available example.

Extract:

- Job naming conventions (snake_case, kebab-case)
- Trigger patterns (`on: push`, `on: pull_request`, branch filters)
- Runner choices (`ubuntu-latest` vs specific versions)
- Checkout and setup step patterns (`actions/checkout`, language setup
  actions)
- `needs:` patterns and dependency chains
- Caching patterns for dependencies
- Project-type-specific patterns (Node, Python, Go, etc.)

If the fetch fails, report the error and ask the user whether to
proceed with standard GitHub Actions conventions as a fallback.

### Step 3 — Plan the job graph

Before writing YAML, produce the dependency plan. Example:

```text
Jobs:
  lint             — no dependencies
  type-check       — no dependencies
  unit-test        — needs: [lint]
  integration-test — needs: [unit-test]
  build            — needs: [unit-test, type-check]
  security-scan    — needs: [lint]
```

Show this plan to the user before generating files.

### Step 4 — Generate workflow files

Apply the job graph and reference patterns to produce
`.github/workflows/*.yml`. Rules:

- **One job per check** — no exceptions. Never combine lint + test,
  never combine type-check + build.
- **`needs:` for ordering** — every job that depends on another must
  declare it explicitly.
- **Runner** — follow the prog-time/workflows convention; default
  `ubuntu-latest`.
- **Triggers** — at minimum `on: [push, pull_request]`. Match the
  reference repo where applicable.
- **Caching** — include dependency caching (`actions/cache` or built-in
  language caching).
- **Step naming** — every step has a `name:` field.
- **Secrets** — never hardcode tokens or keys; use
  `${{ secrets.NAME }}`.
- **File naming** — follow the reference repo's convention.

### Step 5 — Audit existing workflows (if present)

If `.github/workflows/` already has files:

1. Read each file completely.
2. Identify jobs that combine multiple checks — split them.
3. Identify missing `needs:` — add them.
4. Identify missing jobs for checks the project supports — add them.
5. Preserve custom env vars, secrets, matrix builds, or manual triggers
   unless they conflict with the new structure.

### Step 6 — Verify before reporting

- Every generated YAML is syntactically valid (check indentation
  carefully).
- Every check has exactly one job.
- Every job needing ordering has a `needs:`.
- No secrets or tokens are hardcoded.
- Every step has a `name:`.

## Rules (non-negotiable)

- **Always fetch <https://github.com/prog-time/workflows> first.** No YAML
  may be generated before this fetch completes. If the fetch fails,
  stop and ask the user.
- **One job per check.** Lint is one job. Tests are one job (or
  separate if unit and integration are distinct suites). Build is one
  job. Type-check is one job. Security scan is one job. Never combine.
- **`needs:` reflects reality.** If job B cannot meaningfully run
  before job A, B must declare `needs: [A]`. Never leave dependency
  ordering implicit.
- **Never invent checks.** Only generate jobs for checks the project
  actually has.
- **No hardcoded secrets.** All tokens and credentials use
  `${{ secrets.NAME }}`.
- **Match prog-time/workflows naming and structure** wherever the
  reference repo provides a relevant example.

## Output Format

Produce a completion report:

```markdown
## CI Setup Complete

**Stack detected:** [language, framework, package manager]
**Reference source:** https://github.com/prog-time/workflows

### Job Graph

| Job | Depends on | Check |
|-----|------------|-------|
| lint | — | ESLint |
| type-check | — | TypeScript compiler |
| unit-test | lint | Jest unit suite |
| build | unit-test, type-check | Vite production build |

### Files Written

- .github/workflows/ci.yml — [brief description]

### Notes
[Assumptions made, checks not added and why, follow-up needed.]
```

Omit empty sections.

## Examples

### Example 1 — Fresh Node.js project

**User:** настрой CI для этого проекта

**Assistant:** *(detects Node.js + TypeScript + Vitest + ESLint, fetches
prog-time/workflows, proposes job graph `lint`, `type-check`,
`unit-test (needs: lint)`, `build (needs: unit-test, type-check)`,
writes `.github/workflows/ci.yml`, produces completion report)*

### Example 2 — Existing workflow with combined jobs

**User:** audit the current CI setup

**Assistant:** *(reads `.github/workflows/ci.yml`, finds `lint + test`
combined in one job, splits into two jobs with `test` depending on
`lint`, preserves existing secrets and triggers, reports diff)*

### Example 3 — Unknown stack

**User:** add GitHub Actions for this repo

**Assistant:** "I didn't find standard stack markers (`package.json`,
`pyproject.toml`, `go.mod`, etc.). What stack is this? Should I treat
it as a generic repository with only lint / security scan checks?"

## Edge Cases

- **prog-time/workflows fetch fails** — report the error, ask the user
  whether to proceed with standard GitHub Actions conventions.
- **Project has no test runner configured** — do not add a test job;
  note it in the report and suggest the user configure tests first.
- **Existing CI file uses a different naming convention** — ask the
  user whether to match prog-time/workflows or preserve the local
  convention.
- **Monorepo with multiple apps** — ask which app to configure, or
  propose a matrix workflow and confirm before generating.
- **Custom self-hosted runner in existing config** — preserve it;
  never rewrite runner choices without asking.
