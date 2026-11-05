# `rules/` layout

The one layout every project uses. Names and paths are fixed; never rename them.

## Single project

```text
rules/
├─ README.md                    map: stack, run/test, "before you change → read"   always
├─ sync.yml                     code paths each schema describes                   always
├─ architecture/
│  ├─ c4-context.md             C4 L1: system, people, external systems            always
│  ├─ c4-container.md           C4 L2: apps, databases, queues, caches             always
│  └─ c4-component-{name}.md    C4 L3 for one complex container                    optional
├─ database/
│  └─ erd.md                    ERD; split into erd-{domain}.md past ~30 tables    if a database exists
├─ api/                                                                            if the project exposes an API
│  ├─ openapi.yaml              HTTP contract (OpenAPI 3.x; JSON content is fine)
│  └─ postman.json              generated from openapi.yaml, never edited by hand
├─ decisions/
│  └─ NNNN-{slug}.md            ADR: context, decision, consequences               optional
└─ glossary.md                  domain term → name in code                         optional
```

The contract in `api/` is in the API's own format: `openapi.yaml` + `postman.json`
for HTTP, `schema.graphql` for GraphQL, `*.proto` for gRPC (Postman imports the
last two directly, so no collection is stored for them).

## Monorepo or several services in one repository

Each diagram lives at the level it describes and is never duplicated.

```text
rules/                          system level
├─ README.md                    map of services: name → path → one line
├─ architecture/
│  ├─ c4-context.md             the whole system and the outside world
│  └─ c4-container.md           every service, database and queue on one diagram
├─ decisions/  glossary.md
{service-path}/rules/           service level, one per service
├─ README.md  sync.yml          sync.yml paths are relative to the service root
├─ architecture/c4-component.md only for a complex service
├─ database/erd.md
└─ api/openapi.yaml  postman.json
```

Services in separate repositories each get the single-project layout. Their
`c4-context.md` shows the neighbouring services as external systems.

## File rules

- Diagram files are minimal: an H1, one line saying what the diagram covers,
  one `mermaid` block. Nothing else.
- Every element comes from real code or config. Never invent one; if something
  is unknown, leave it out and report it.
- `rules/README.md` holds only project-specific facts and rules, at most ~40 lines.
  Conventions shared by every project stay in the global config, not here.
- No secrets, real personal data, or absolute home paths in any file.
