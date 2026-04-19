# Template — `rules/README.md`

Use this template to produce the master orchestrator file. Adapt to the
project's real domains and structure. Produce EXACTLY the content below,
with real values substituted.

```markdown
# Rules Directory — Master Orchestrator

> **Purpose:** Serve as the single entry point for AI agents to understand all mandatory rules,
> dependencies, and execution order.
> **Context:** Read this file first.
> Follow the steps exactly before touching any code, schema, or documentation.
> **Version:** 1.0

## 1. Core Principle

Before any task:

1. Understand the rules directory structure
2. Identify which files are relevant to your task
3. Follow rules strictly in order
4. Produce complete and auditable output

> The agent **must never skip reading any required file**.
> All domain, process, and meta rules are part of the source of truth.

## 2. Directory Overview

\`\`\`
rules/
├─ README.md                        ← You are here
├─ _meta/
│  └─ how-to-write-rules.md         ← File structure and writing standards
├─ database/
│  └─ schema.md                     ← Database schema documentation
├─ domain/
│  └─ {domain-name}.md              ← Business domain rules (one per domain)
├─ api/
│  └─ endpoints.md                  ← API contract rules
├─ process/
│  ├─ architecture-design.md        ← Design before implementation
│  ├─ observability.md              ← Logging, metrics, monitoring
│  ├─ ai-workflow.md                ← AI agent lifecycle rules
│  ├─ ci-cd.md                      ← CI/CD and pipeline rules
│  ├─ security.md                   ← Security and safe coding rules
│  └─ testing-strategy.md           ← Test strategy and coverage rules
\`\`\`

## 3. Reading & Execution Order

When performing a task, the AI agent **must follow this sequence**:

| # | File | Purpose |
|---|------|---------|
| 1 | `_meta/how-to-write-rules.md` | Understand formatting, structure, and standards |
| 2 | `process/architecture-design.md` | Pre-implementation design. Document diagrams and layers |
| 3 | `process/ai-workflow.md` | Review lifecycle rules: understand, design, implement, verify, document |
| 4 | `database/schema.md` | Read database schema before touching migrations, tables, or relations |
| 5 | `domain/{domain-name}.md` | Read all relevant domains to understand business rules, state machines, invariants |
| 6 | `api/endpoints.md` | Understand API contracts. Do not implement endpoints not defined in Swagger |
| 7 | `process/observability.md` | Ensure logs, metrics, health checks, and request tracing will be included |
| 8 | `process/ci-cd.md` | Validate pipeline rules. Ensure automated testing and deployment constraints |
| 9 | `process/security.md` | Read security rules before modifying auth, input handling, or secrets |
| 10 | `process/testing-strategy.md` | Ensure tests will cover all changes and critical paths |

> **Rule:** Never implement before design and lifecycle steps are confirmed.

## 4. Self-Verification

Before reporting task completion, the agent **must check**:

- [ ] All relevant rules files read and applied
- [ ] Design artifacts exist if required
- [ ] Database, domain, API changes validated against rules
- [ ] Logging, metrics, and observability confirmed
- [ ] CI/CD compliance verified
- [ ] Security rules enforced
- [ ] Tests created or updated as mandated
- [ ] No forbidden behaviors introduced
- [ ] Documentation updated in `rules/` as needed

## 5. Reporting / Task Output

At the end of a task, the AI agent **must produce a structured report**:

1. **Files affected** — List all files touched
2. **Rules read** — Confirm each relevant rules file was read
3. **Design artifacts** — Include diagrams, impact analysis, or placeholders
4. **Verification checks** — List all checklist items passed
5. **Deviations** — Document any items skipped or marked `_Not applicable_`
6. **Summary** — State task completion, blockers, and next steps

**Example:**

\`\`\`json
{
  "task": "Add new Order workflow",
  "files_affected": ["services/OrderService.ts", "domain/order.md"],
  "rules_read": [
    "process/architecture-design.md",
    "domain/order.md",
    "api/endpoints.md"
  ],
  "design_artifacts": ["component-diagram.png", "ERD-update.md"],
  "verification_checks": [
    "Design approved",
    "Tests created",
    "CI/CD passed"
  ],
  "deviations": ["None"],
  "summary": "Task complete and ready for merge"
}
\`\`\`

## 6. Best Practices

- Always create placeholders for non-existent domains or files
- Never assume defaults — follow explicit rules
- Stop immediately if a required rules file is missing
- Maintain consistency with existing code and rules
- Incremental and verifiable steps are mandatory

## Agent Entry Point Summary

| Step | Action |
|------|--------|
| 1 | Read this `README.md` first |
| 2 | Follow the reading & execution order strictly |
| 3 | Apply rules and document all steps |
| 4 | Verify using checklist in Section 4 |
| 5 | Produce structured task report as in Section 5 |
```
