# Template — `rules/database/schema.md`

Produce EXACTLY this structure. Replace the ERD, tables, columns, and enums
with real values reconstructed from migrations during Phase 0.

```markdown
# Database Schema

> Purpose: This file defines mandatory standards for documenting the database schema. It ensures that AI agents and developers fully understand data structure, relationships, and constraints before making changes.
> Context: Read this file before creating or modifying tables, columns, indexes, or migrations.
> Version: 1.0

## 1. Core principle

The database is the source of truth.
- Every table must be documented
- Every column must be explained
- Every relationship must be explicit
- Hidden or implicit behavior is forbidden
- Schema changes without documentation are forbidden

## 2. ERD (Mermaid diagram)

\`\`\`erDiagram
    USERS {
        bigint id PK
        string name
        string email UK
        string password
        enum status
        timestamp email_verified_at
        timestamps
    }
    ORDERS {
        bigint id PK
        bigint user_id FK
        decimal total
        enum status
        timestamps
    }
    USERS ||--o{ ORDERS : "has many"
\`\`\`

[Replace with the real ERD built from the actual migration files]

## 3. Table documentation

[One section per table — example template:]

### `users`
Stores application users and authentication data.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `bigint` | No | auto | Primary key |
| `email` | `string` | No | — | Unique login identifier |

**Indexes:**
- PRIMARY on `id`
- UNIQUE on `email` — prevents duplicates

## 4. Enum inventory

[List every enum column and all its values — example:]

**orders.status**
- `pending` — created but not paid
- `paid` — payment successful
- `shipped` — sent to customer
- `cancelled` — user or system cancelled

## 5. Change management rules

Schema updates must follow this strict process:
1. Update ERD first
2. Update table docs
3. Update enums/indexes
4. Then write migration
5. Then write tests

Never merge migrations without documentation updates.

## 6. Definition of done

A schema change is not complete until:
- ERD updated
- Table documented
- Columns documented
- Indexes documented
- Enums listed
- Soft deletes justified

## Forbidden behaviors
- Undocumented tables
- Missing column descriptions
- Raw SQL dumps instead of documentation
- Implicit relationships
- Magic enum values
- Schema changes without ERD updates

## Checklist
- [ ] ERD diagram present
- [ ] Every table documented
- [ ] Every column documented
- [ ] Indexes explained
- [ ] Soft deletes justified
- [ ] Enums fully listed
- [ ] Docs updated before migration
- [ ] No forbidden behaviors
```
