# Templates — diagram files

Each file is exactly: H1, one line, one `mermaid` block. Replace every element
with real ones from the code. Element ids are short snake_case; labels are what
people call the thing.

## `architecture/c4-context.md`

````markdown
# C4 Context

Who uses the system and which external systems it talks to.

```mermaid
C4Context
  Person(user, "<Role>", "<what they do>")
  System(app, "<System>", "<what it does>")
  System_Ext(ext, "<External system>", "<what it provides>")
  Rel(user, app, "<uses>", "<HTTPS>")
  Rel(app, ext, "<calls>", "<protocol>")
```
````

## `architecture/c4-container.md`

````markdown
# C4 Container

Deployable parts of the system and how they communicate.

```mermaid
C4Container
  Person(user, "<Role>")
  System_Boundary(app, "<System>") {
    Container(api, "<API>", "<language, framework>", "<responsibility>")
    ContainerDb(db, "<Database>", "<engine>", "<what it stores>")
    ContainerQueue(queue, "<Queue>", "<engine>", "<what flows through it>")
  }
  System_Ext(ext, "<External system>")
  Rel(user, api, "<uses>", "<HTTPS/JSON>")
  Rel(api, db, "<reads/writes>", "<driver>")
  Rel(api, ext, "<calls>", "<protocol>")
```
````

## `architecture/c4-component-{name}.md` (optional)

````markdown
# C4 Component — <container>

Main components inside <container> and their dependencies.

```mermaid
C4Component
  Container_Boundary(api, "<API>") {
    Component(auth, "<Auth>", "<module/class>", "<responsibility>")
    Component(orders, "<Orders>", "<module/class>", "<responsibility>")
  }
  ContainerDb(db, "<Database>", "<engine>")
  Rel(orders, db, "<reads/writes>")
  Rel(orders, auth, "<checks access>")
```
````

## `database/erd.md`

Every table, every column with type and key markers (`PK`, `FK`, `UK`), and every
relationship. Enum values go in the column comment. Pivot tables are included.

````markdown
# ERD

All tables, columns and relationships of <database>.

```mermaid
erDiagram
  users ||--o{ orders : places
  users {
    bigint id PK
    string email UK
  }
  orders {
    bigint id PK
    bigint user_id FK
    string status "new|paid|shipped"
  }
```
````

## `decisions/NNNN-{slug}.md` (optional)

```markdown
# NNNN. <Decision>

- Context: <what forced a choice>
- Decision: <what was chosen>
- Consequences: <what it costs, what it rules out>
```
