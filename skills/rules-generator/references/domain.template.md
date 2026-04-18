# Template — `rules/domain/{domain-name}.md`

Produce one file per identified domain. Substitute the domain name,
concepts, business rules, and state machine with real values from Phase 0.
All business rules follow the `BR-NNN` format with an `_Enforced in:_` line
pointing at the real file path.

```markdown
# {Domain Name} Domain Rules

> Purpose: This file defines mandatory documentation and behavior rules for the {Domain} domain.
> Context: Read this file before modifying anything related to {Domain}.
> Version: 1.0

## 1. Core principle

Business logic must be explicit and centralized.

- Every rule must be documented
- Every invariant must be testable
- Every state change must be predictable
- Hidden business behavior is forbidden
- Code must never be the only source of truth

If a rule exists only in code, it is undocumented and unsafe.

## 2. What is this domain?

[2–3 sentences describing responsibility and boundaries]

### Key concepts

| Concept | Description |
|---|---|
| Order | A purchase request created by a user |
| Payment | Money transfer confirming an order |

## 3. Business rules

**BR-001** — An order can only be cancelled if its status is `pending` or `processing`.
_Enforced in:_ `app/Services/OrderService.ts @ cancel()`

**BR-002** — A user must verify their email before placing an order.
_Enforced in:_ `middleware/ensureEmailVerified.ts`

[Continue with BR-003, BR-004, ... for all real rules found in Phase 0]

## 4. State machine

[Include only if the domain has a status/state field]

\`\`\`mermaid
stateDiagram-v2
    [*] --> pending
    pending --> processing
    processing --> completed
    pending --> cancelled
\`\`\`

## 5. AI-specific rules

Because AI often spreads logic accidentally:
- Never invent undocumented business behavior
- Never duplicate rules in multiple places
- Always update this file when rules change
- Always add tests for every business rule
- Always check state machine consistency

## 6. Definition of done

A domain change is not complete until:
- Domain overview updated
- Concepts documented
- Business rules listed or updated
- State machine updated (if applicable)
- Events documented
- Integrations documented
- Tests cover rules
- No hidden logic introduced

## Forbidden behaviors
- Business rules only in code
- Unnumbered rules
- Implicit state transitions
- Direct DB mutations bypassing domain
- Undocumented events
- Hidden integrations
- Cross-domain coupling without documentation

## Checklist
- [ ] Overview written
- [ ] Key concepts defined
- [ ] All business rules documented and numbered
- [ ] Enforcement locations listed
- [ ] State machine documented (if applicable)
- [ ] Events documented
- [ ] Integrations documented
- [ ] Tests cover rules
- [ ] No forbidden behaviors
```
