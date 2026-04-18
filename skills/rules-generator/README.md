# rules-generator

Analyzes an existing codebase and generates a complete `rules/` directory
that serves as a persistent AI knowledge base: master README, meta rules,
database schema docs, one domain file per business domain, an API contract
file, and six process files (architecture, observability, AI workflow,
CI/CD, security, testing).

The skill reads migrations, models, services, routes, policies, jobs, and
`.env.example` during a mandatory Phase 0 analysis, then produces all files
in one pass using the templates under `references/`. Nothing is invented —
every rule, table, and domain comes from real evidence in the code.

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
