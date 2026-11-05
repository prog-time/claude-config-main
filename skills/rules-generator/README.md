# rules-generator

Creates or audits `rules/`, a small, fixed-layout map of a project that a
person and Claude can both rely on. It works for any stack.

```text
rules/
├─ README.md            map: stack, run/test, "before you change → read"
├─ sync.yml             code paths behind each schema (used by rules-check)
├─ architecture/        C4 Context + Container (+ optional Component), Mermaid
├─ database/erd.md      ERD, Mermaid
└─ api/                 openapi.yaml (generated from code) + postman.json
```

Monorepos get a system level (`rules/` at the root: service map, C4 Context and
Container) and a service level (`{service}/rules/`: ERD, API, C4 Component).
The full specification is in [`references/layout.md`](references/layout.md).

The skill is a thin orchestrator. It picks the mode, the roots, and the layout,
then delegates analysis and writing to the
[`rules-writer`](../../agents/rules-writer.md) agent.

## Modes

- **`init`**: creates every missing file from real code. Never overwrites.
- **`audit`**: read-only. Lists missing files and diagrams that disagree with the
  code. It also points out an old-layout `rules/` (`process/`, `_meta/`, `domain/`).

## Usage

- "сгенерируй rules", "создай rules", "сделай C4 и ERD"
- "проверь rules", "audit rules against the code"

## Structure

- `SKILL.md`: triggers, workflow, rules
- `references/layout.md`: canonical layout and file rules
- `references/readme.template.md`: `rules/README.md` skeleton
- `references/sync.template.yml`: `rules/sync.yml` skeleton
- `references/diagrams.template.md`: C4, ERD, and ADR skeletons
- `references/api-generators.md`: code → OpenAPI per stack, OpenAPI → Postman

## Installation

Picked up automatically after `make install` at the repository root.
