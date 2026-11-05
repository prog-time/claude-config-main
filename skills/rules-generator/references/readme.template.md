# Template — `rules/README.md`

Fill every `<…>` from the code. Delete a map row whose file does not exist.
Keep the result under ~40 lines.

```markdown
# <Project name>

<One sentence: what the system does and for whom.>

- Stack: <language, framework, database, infrastructure>
- Run: `<command>` · Test: `<command>`
- Entry points: `<path>` (<what it is>), `<path>` (<what it is>)

## Before you change…

| Area | Read first | Keep in sync |
|---|---|---|
| Services, infrastructure, integrations | `architecture/c4-container.md` | `c4-context.md`, `c4-container.md` |
| Database structure | `database/erd.md` | `database/erd.md` |
| API | `api/openapi.yaml` | run `api.generate` from `sync.yml`, or edit `openapi.yaml`; then regenerate `postman.json` |

`sync.yml` lists the code paths behind each schema. `rules-check` warns when one
changes without the other.

## Project rules

- <Only rules specific to this project that a newcomer would get wrong. At most 10.>
```

Monorepo system level: replace the table's paths with the service map:

```markdown
## Services

| Service | Path | What it does |
|---|---|---|
| <name> | `<path>` | <one line> — rules in `<path>/rules/` |
```
