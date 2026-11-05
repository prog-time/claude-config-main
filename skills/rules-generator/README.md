# rules-generator

A thin **orchestrator** skill. It generates a complete `rules/` AI knowledge
base — master README, meta rules, database schema docs, one domain file per
business domain, an API contract file, and six process files (architecture,
observability, AI workflow, CI/CD, security, testing) — but it does **not** do
the work itself.

The skill handles the orchestration-level concerns (resolve the template
directory, resolve the project root, check for an existing `rules/`, monorepo
prompt) and then delegates the codebase analysis and file generation to the
**`rules-writer` agent** via the Agent tool, relaying its JSON report. The agent
runs the mandatory Phase 0 analysis (migrations, models, services, routes,
policies, jobs, `.env.example`) and writes every file from the templates under
`references/` in an isolated context. Nothing is invented — every extracted rule,
table, and domain comes from real evidence in the code; the six `process/` files
are adopted conventions, flagged as such.

Because the work lives in an agent, `rules/` generation is also routable as a
stage by the `team-lead` orchestrator.

## Installation

Picked up automatically after `make install` at the repository root.

## Usage

Trigger phrases (English and Russian):

- "generate rules for this project"
- "create a rules/ directory"
- "document the codebase for AI agents"
- "set up an AI knowledge base"
- "сгенерируй rules"
- "создай rules"
- "документируй проект для AI"

## Structure

- `SKILL.md` — trigger description, workflow, rules
- `references/rules-readme.template.md` — master `rules/README.md` template
- `references/how-to-write-rules.template.md` — `_meta/` template
- `references/database-schema.template.md` — `database/schema.md` template
- `references/domain.template.md` — per-domain template
- `references/api-endpoints.template.md` — `api/endpoints.md` template
- `references/process-templates.md` — all six process templates in one file

Templates are loaded on demand — only when the skill is about to write the
corresponding output file — to keep the conversation context small.
