---
name: rules-generator
description: |
  Creates or audits a project's `rules/` directory, which has the same minimal
  layout in every project and stack: a README map, sync.yml, C4 diagrams
  (Mermaid), an ERD (Mermaid), and the API contract (OpenAPI generated from
  code, plus a Postman collection). Monorepos get a system level and a service
  level. The skill runs pre-checks, then delegates the code analysis and the
  writing to the `rules-writer` agent. Use ALWAYS when the user says "generate
  rules", "create a rules/ directory", "audit rules", "check rules against the
  code", "make C4/ERD diagrams for this project", "document the codebase for AI
  agents", "сгенерируй rules", "создай rules", "проверь rules", "сделай C4",
  "сделай ERD", "документируй проект для AI". Do NOT use for: editing a single
  diagram after a code change (edit it directly), README/CHANGELOG (use
  docs-quality), blog posts, or creating skills/agents.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Agent
---

# Rules Generator

A thin orchestrator. It picks the mode and the roots, then delegates to the
`rules-writer` agent, which analyzes the code and writes the files in an
isolated context. The skill never writes `rules/` files itself.

The canonical layout and templates live in `references/`:

- `layout.md`: the layout, naming, and file rules. This is the source of truth.
- `readme.template.md`, `sync.template.yml`, `diagrams.template.md`: file skeletons.
- `api-generators.md`: how to pick the code → OpenAPI command and build the Postman collection.

## Modes

| Mode | When | What happens |
|---|---|---|
| `init` | user asks to create or generate | creates every missing file from the layout; **never overwrites** an existing file |
| `audit` | user asks to check, or `rules/` already exists | read-only: lists missing files and diagrams that disagree with the code |

To regenerate a file, the user deletes it and runs `init` again.

## Workflow

1. **Resolve `template_dir`.** It is the absolute path of this skill's `references/`.
2. **Resolve `target_root`.** Use `git rev-parse --show-toplevel`. If the directory is not a git repo, use the CWD and warn.
3. **Pick the mode.** An explicit request wins. Otherwise: no `rules/` → `init`; `rules/` exists → `audit`, then offer `init` to fill the gaps it found.
   If `rules/` contains the old layout (`process/`, `_meta/`, `domain/`, `database/schema.md`, `api/endpoints.md`), run `audit`. Its report says what to keep, for example project-specific rules that move to `rules/README.md`. Delete nothing.
4. **Detect the shape.** If there are several deployable services (several manifests under `apps/`, `services/`, `packages/`, or several services in docker-compose), it is a monorepo. Pass `layout: monorepo` and the list of service roots. Do not ask unless the service list is ambiguous.
5. **Delegate.** Invoke the `rules-writer` agent with `template_dir`, `target_root`, `mode`, `layout` (`single` or `monorepo`), `services[]`, and the user's request verbatim.
6. **Relay** the agent's JSON report as a short summary: files created, generators chosen or suggested, gaps, deviations. Surface errors verbatim and do not write files as a fallback.

## Rules

- Never write or overwrite `rules/` files from the skill. The agent writes, and only in `init`.
- Never add dependencies (generators, CLIs) to the project. The agent only suggests them.
- Do not invoke `agent-builder`.

## Examples

**User:** сгенерируй rules для проекта → no `rules/`, single service → `init`, `layout: single`.

**User:** проверь, что схемы актуальны → `audit`. Relay the list of drift items.

**User:** сделай C4 и ERD для этого монорепо → `init`, `layout: monorepo`, `services: [apps/api, apps/worker]`.
