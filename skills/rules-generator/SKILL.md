---
name: rules-generator
description: |
  Analyzes an existing codebase end-to-end and generates a complete `rules/`
  documentation system as a persistent AI knowledge base (README, _meta,
  database/schema, one file per business domain, api/endpoints, and all six
  process files). Use ALWAYS when the user says "generate rules", "generate
  rules for this project", "create a rules/ directory", "document the codebase
  for AI agents", "set up an AI knowledge base", "сгенерируй rules",
  "создай rules", "построй rules/", "документируй проект для AI", "сделай
  AI knowledge base", or asks to bootstrap AI-ready project documentation
  derived from real code. Walks through Phase 0 analysis (migrations, models,
  routes, services, policies, jobs, events, .env), builds an internal
  inventory, then emits all mandatory files in one pass using the templates
  in `references/`. Do NOT use for: editing a single existing rules file
  (use Edit), writing a README or CHANGELOG (use docs-quality), authoring
  blog posts (use blog-article-writer), or creating skills/agents.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Rules Generator

Analyze the project's real code and produce a complete, evidence-based
`rules/` directory that serves as the project's persistent AI knowledge base.

Every rule, table, column, domain, and route in the output must come from
real evidence in the codebase. Never invent content. If a concept does not
exist in the project, still create the corresponding file and mark it
`_Not applicable — [reason]_`.

## Workflow

### Step 1 — Phase 0 Analysis (mandatory before any file is written)

Read the project in this order and build an internal inventory. Do not
create any output file until this phase is complete.

1. `CLAUDE.md`, `README.md`, `docs/`, existing `rules/` — project context
2. `composer.json` / `package.json` / `pyproject.toml` / `go.mod` — framework,
   language version, key dependencies
3. All migration files — reconstruct the full database schema
4. All model / entity files — relationships, scopes, casts, business rules
5. All service / action / use-case classes — business logic
6. All route / controller files — map the complete API and web surface
7. All policy / gate / middleware definitions — authorization rules
8. All job, event, listener, notification classes — async flows
9. Existing tests — understand intended behaviour
10. `.env.example` — configuration surface

Internal inventory to produce before writing:

- Tables (name + columns + indexes + enums)
- Business domains (name + boundary + key concepts)
- API routes grouped by domain
- Async flows (jobs, events, listeners)
- Authorization rules (policies, gates, middleware)
- Stack details (framework, language, ORM, database)

### Step 2 — Create the mandatory directory structure

```
rules/
├─ README.md
├─ _meta/
│  └─ how-to-write-rules.md
├─ database/
│  └─ schema.md
├─ domain/
│  └─ {domain-name}.md   (one file per identified domain)
├─ api/
│  └─ endpoints.md
└─ process/
   ├─ architecture-design.md
   ├─ observability.md
   ├─ ai-workflow.md
   ├─ ci-cd.md
   ├─ security.md
   └─ testing-strategy.md
```

Naming: lowercase, hyphenated filenames; one file per domain, named after
the domain (e.g. `orders.md`, `billing.md`).

### Step 3 — Write every file from the templates in `references/`

Load the correct template from `references/` and fill in real content from
Phase 0. Never copy placeholder text literally.

| Output file | Template |
|---|---|
| `rules/README.md` | `references/rules-readme.template.md` |
| `rules/_meta/how-to-write-rules.md` | `references/how-to-write-rules.template.md` |
| `rules/database/schema.md` | `references/database-schema.template.md` |
| `rules/domain/{name}.md` | `references/domain.template.md` |
| `rules/api/endpoints.md` | `references/api-endpoints.template.md` |
| `rules/process/*.md` | `references/process-templates.md` (6 sections) |

Read each template only when you are about to write the corresponding
output file — do not pre-load all templates at once. This keeps context
small on small projects and allows interruption mid-way.

### Step 4 — Emit the completion report

After all files are written, output this JSON report with real values:

```json
{
  "phase": "complete",
  "files_created": [],
  "domains_identified": [],
  "tables_documented": [],
  "business_rules_found": [],
  "deviations": [],
  "summary": ""
}
```

`deviations` lists every file marked `_Not applicable_` and the reason.
`summary` is a one-paragraph plain-text summary.

## Rules

- **Phase 0 first** — never create or write any file before the full
  codebase analysis is complete.
- **No invented content** — every rule, table, column, and domain must be
  derived from real evidence in the codebase.
- **No skipped files** — all mandatory files must be created; mark
  inapplicable content with `_Not applicable — [reason]_` but still create
  the file.
- **No mixed concerns** — never combine unrelated domains in one file.
- **Exact naming** — file and directory names must match the canonical
  structure exactly: lowercase, hyphenated.
- **One domain per file** — do not collapse multiple domains into one file.
- **Mermaid diagrams required** — include an `erDiagram` in
  `database/schema.md` and a `stateDiagram-v2` in each domain file that has
  a status/state field.
- **Business rules numbered** — all business rules in domain files follow
  the `BR-NNN` format, with `_Enforced in:_` pointing at the real file path.
- **Do NOT pre-load all templates** — read `references/*.md` only when
  about to write the corresponding output file.
- **Never commit or run destructive commands** without user confirmation.

## Examples

### Example 1 — Standard bootstrap

**User:** сгенерируй rules для этого проекта

**Assistant:** *(runs Phase 0 across migrations, models, routes, services)*
"Found Laravel 11 stack, 14 tables, 4 domains (users, orders, billing,
notifications), 37 API routes. Proceeding to write rules/."
*(writes all mandatory files using templates in `references/`, outputs the
JSON report)*

### Example 2 — No database project

**User:** document this CLI tool for AI agents

**Assistant:** *(Phase 0 finds no migrations/models)* "This project has no
database layer. I'll still create `rules/database/schema.md` marked
`_Not applicable — no persistent data store_` and record it in the
`deviations` array of the final report."

### Example 3 — Existing rules/ present

**User:** create a rules/ directory

**Assistant:** "`rules/` already exists with 8 files. Do you want me to
overwrite, only create missing ones, or abort?" *(wait for confirmation
before writing)*

## Edge Cases

- **`rules/` already exists** — ask the user whether to overwrite, fill
  gaps only, or abort. Never silently overwrite.
- **Monorepo with multiple apps** — ask which app to document, or produce
  one `rules/` per app under each app's root.
- **Zero business logic found (static site / docs repo)** — create minimal
  structure, mark most domain/process files `_Not applicable_`, list all
  deviations.
- **Framework not recognized** — report the detected stack and ask the user
  to confirm before proceeding; do not guess conventions.
- **User requests partial output** (only schema, only API) — refuse; this
  skill produces the complete mandatory structure. For targeted edits,
  point the user at Edit.
