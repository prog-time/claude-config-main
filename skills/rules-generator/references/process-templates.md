# Templates — `rules/process/*.md`

Six mandatory files. Each section below is the EXACT content for one output
file. When writing output, only copy the relevant section — do not combine
process files.

---

## 1. `rules/process/architecture-design.md`

```markdown
# Architecture Design Rules

> Purpose: Ensure every change starts with explicit design. Force the agent to think structurally before generating code.
> Context: Read this file before implementing any feature, refactor, schema change, or new module.
> Version: 1.0

## 1. Core principle

Design first. Code second.
- Never start with implementation
- Always define structure before details
- Always document boundaries
- Always minimize complexity

If design is missing → stop and design.

## 2. Mandatory pre-implementation steps

**Step 1 — Read context**
- Read rules/README.md
- Read architecture/overview.md
- Read relevant domain/*.md
- Read related source files
- Identify existing patterns to reuse

**Step 2 — Define the problem**
- State the goal in 1–3 sentences
- List non-goals explicitly
- Define success criteria
- Identify constraints (performance, security, compatibility)

**Step 3 — Propose a design**

Must include:
- Affected layers
- New/modified modules
- Public contracts
- Data model changes
- Risks and trade-offs

Do not write implementation yet.

**Step 4 — Validate the design**
- Check against architecture layer rules
- Check against existing conventions
- Check for duplication
- Check for simpler alternatives
- Prefer extending existing modules over creating new ones

Only after validation → implementation allowed.

## 3. Required design artifacts

**For new feature:** Component diagram, data model updates, API contract, test strategy

**For schema change:** ERD update, migration plan, backward compatibility notes, rollback strategy

**For refactor:** Before/after structure, risk assessment, no behavior changes allowed unless specified

**For cross-cutting concerns:** Explicit layer impact analysis

## 4. Diagram requirements

**Component example:**
\`\`\`mermaid
flowchart LR
    Controller --> Service
    Service --> Repository
    Repository --> Database
\`\`\`

**Sequence example:**
\`\`\`mermaid
sequenceDiagram
    Client->>API: POST /orders
    API->>Service: createOrder()
    Service->>DB: insert
    Service-->>Client: response
\`\`\`

Diagrams must reflect real structure, not hypothetical designs.

## 5. Layer boundary rules

- Controllers handle transport only
- Services contain business logic
- Repositories handle persistence only
- Domain must not depend on frameworks
- Infrastructure must not leak into domain

\`\`\`typescript
// Correct — controller delegates
export async function create(req, res) {
  await orderService.create(req.body)
}

// Incorrect — business logic inside controller
export async function create(req, res) {
  if (req.body.total > 1000) applyDiscount()
}
\`\`\`

## 6. Complexity control rules

- Prefer modifying existing modules
- Avoid new abstractions without clear need
- Avoid premature generalization
- Avoid speculative flexibility
- Do not introduce patterns "just in case"

Rule of thumb: If a solution needs more than 3 new files, reconsider the design.

## 7. AI generation limits

- Never generate an entire feature in one step
- Generate skeletons first
- Then implement one module at a time
- Review after each step
- Stop if output exceeds manageable size

Large monolithic generations are forbidden.

## 8. Consistency rules

\`\`\`typescript
// Correct — uses existing service pattern
class OrderService {}

// Incorrect — introduces random pattern
class OrderManagerFactoryBuilder {}
\`\`\`

## 9. Forbidden behaviors

- Coding before design
- Generating speculative architecture
- Introducing new frameworks without ADR
- Mixing layers
- Hidden schema changes
- Large "big bang" rewrites
- Copying patterns from unrelated projects

## 10. Definition of ready

Implementation may start only if:
- Problem is defined
- Scope is bounded
- Design exists
- Diagrams created
- Impacted files listed
- Risks identified
- Rules checked

If any item is missing → design is incomplete.

## Checklist

- [ ] Context files read
- [ ] Problem defined
- [ ] Design proposed
- [ ] Diagrams created
- [ ] Layers respected
- [ ] Complexity minimized
- [ ] No speculative abstractions
- [ ] Small incremental plan prepared
```

---

## 2. `rules/process/observability.md`

```markdown
# Observability Rules

> Purpose: Guarantee that every feature is observable in production.
> Prevent "black box" systems that cannot be debugged after deployment.
> Context: Read this file before implementing any endpoint, background job, integration, or infrastructure change.
> Version: 1.0

## 1. Core principle

If you cannot observe it, you cannot operate it.

- Every flow must produce logs
- Every service must expose health signals
- Every critical action must be measurable
- Every failure must be traceable
- Silent failures are forbidden

## 2. Structured logging rules

\`\`\`typescript
// Correct — structured log
logger.info("order_created", {
  orderId: order.id,
  userId: user.id,
  total: order.total
})

// Incorrect — unstructured and useless
console.log("created order")
\`\`\`

**Mandatory rules:**
- Use structured logs (JSON or key-value)
- Include timestamps automatically
- Include correlation/request ID
- Include severity level
- Include domain context (user_id, order_id, job_id, etc.)
- Never use free-form string logs only
- Never log sensitive data

## 3. Log level conventions

| Level | Use |
|-------|-----|
| `debug` | development diagnostics only |
| `info` | business events (created, updated, started) |
| `warn` | recoverable issues |
| `error` | failures that affect functionality |
| `fatal` | system cannot continue |

- Do not log everything as error
- Do not log business events as debug
- Production must not rely on debug logs

## 4. Request tracing rules

\`\`\`typescript
// Correct
req.context.requestId = uuid()
logger.info("processing_order", { requestId })

// Incorrect — no traceability
logger.info("processing_order")
\`\`\`

## 5. Metrics rules

\`\`\`typescript
// Correct
metrics.counter("orders_created_total").inc()
metrics.histogram("order_processing_ms").observe(duration)

// Incorrect
console.log("processing took 123ms")
\`\`\`

Must track: request count, error count, latency, job duration, external API latency, queue size, DB query time.

## 6. Health check rules

Required endpoints:
- `/health/live` — process is alive
- `/health/ready` — dependencies available
- `/health/startup` — startup completed (if applicable)

\`\`\`json
// Correct
{ "status": "ok" }

// Incorrect
{ "status": "ok", "users": [...full dataset...] }
\`\`\`

## 7. Error tracking rules

\`\`\`typescript
// Correct
try {
  await service.process()
} catch (err) {
  logger.error("processing_failed", { err })
  throw err
}

// Incorrect — silent failure
try {
  await service.process()
} catch (err) {}
\`\`\`

## 8. AI-specific observability rules

- Always add logs for new flows
- Always add metrics for new endpoints
- Always instrument async jobs
- Never introduce silent catch blocks
- Never swallow exceptions

## 9. Sensitive data rules

Never log: passwords, tokens, secrets, full payload dumps, personal data (unless explicitly required).

## 10. Definition of done

A feature is not complete unless:
- Logs added for main flows
- Errors logged properly
- Metrics added
- Health checks unaffected
- Failures traceable by request ID

## Forbidden behaviors

- Console-only logging
- Silent catch blocks
- Logging entire objects blindly
- Logging secrets
- No metrics for critical paths
- No health checks
- Relying on manual debugging only

## Checklist
- [ ] Structured logs used
- [ ] Proper log levels applied
- [ ] Request IDs propagated
- [ ] Metrics added
- [ ] Health endpoints intact
- [ ] Errors tracked centrally
- [ ] No sensitive data logged
- [ ] No silent failures
- [ ] New flows observable in production
```

---

## 3. `rules/process/ai-workflow.md`

```markdown
# AI Workflow Rules

> Purpose: Constrain AI behaviour to prevent unsafe or low-quality changes and to make results deterministic across agents.
> Context: Read this file before performing any modification, refactor, migration, or feature implementation.
> Version: 1.0

## 1. Core principle

The agent must behave like a careful mid-level engineer, not an auto-generator.
- Always analyze before coding
- Always design before implementing
- Always test before finishing
- Never generate large changes blindly
- Never modify files you did not read

## 2. Mandatory development lifecycle

**Step 1 — Understand**
- Read rules/README.md
- Read relevant domain files
- Read related code before proposing changes
- Identify existing patterns to follow

**Step 2 — Design**
- Propose architecture or schema changes first
- List impacted files
- Identify risks and edge cases
- Do not write code yet

**Step 3 — Implement**
- Make the smallest possible change
- Follow existing conventions exactly
- Reuse existing abstractions
- Avoid introducing new patterns unless required

**Step 4 — Verify**
- Run linters
- Run tests
- Add missing tests
- Validate types and contracts
- Check for security issues

**Step 5 — Document**
- Update relevant rules/*.md
- Update README if behaviour changed
- Update API docs if endpoints changed
- Update schema docs if DB changed

The task is not complete until documentation is updated.

## 3. Scope control rules

\`\`\`php
// Correct — minimal targeted change
public function cancel(Order $order): void
{
    $order->update(['status' => 'cancelled']);
}

// Incorrect — mixes refactor with feature
public function cancel(Order $order)
{
    // rewrote repository, renamed services, changed architecture,
    // and also cancelled the order
}
\`\`\`

## 4. Generation size limits

- Prefer small iterations over big outputs
- Never generate more than one module at a time
- Never create more than 300–500 lines of new code without review
- Break large features into subtasks

Reason: large generations increase hallucination risk.

## 5. Safety rules

\`\`\`
// Correct — uses existing field from schema
user.emailVerifiedAt

// Incorrect — hallucinated field
user.emailVerified   // does not exist
\`\`\`

- Never invent database columns that do not exist
- Never invent API fields not defined in schema
- Never guess business logic
- If unsure, ask or search the codebase
- Do not fabricate dependencies or packages

## 6. Test-first expectations

- Add or update tests for every behaviour change
- Bug fixes must include regression tests
- New features must include happy path + edge cases
- Do not rely only on manual reasoning

## 7. Documentation coupling rules

Every change must update rules. Failure to update documentation means the task is incomplete.

## 8. Forbidden behaviors

- Generating entire applications from scratch without notes
- Editing files without reading them first
- Ignoring existing conventions
- Silent schema changes
- Skipping tests
- Skipping documentation
- Making speculative optimizations

## Checklist

- [ ] Relevant rules files read
- [ ] Existing code inspected
- [ ] Design proposed before implementation
- [ ] Minimal change applied
- [ ] Tests added or updated
- [ ] Linters pass
- [ ] Documentation updated
- [ ] No hallucinated fields or APIs introduced
```

---

## 4. `rules/process/ci-cd.md`

```markdown
# CI/CD Rules

> Purpose: Ensure every change passes automated checks and deployments consistently.
> Guarantee that AI-generated code is validated and deployable before reaching production.
> Context: Read this file before touching any CI/CD pipeline, merge request, or deployment process.
> Version: 1.0

## 1. Core principle

Every change must pass automated checks before merging or deploying.

- CI/CD is not optional
- No manual deployments without pipeline completion
- Broken pipelines must be fixed immediately
- Never disable checks to speed up delivery

## 2. Pipeline stages

**2.1 Pre-commit / local checks**
- Run linters
- Run type-checks
- Run unit tests
- Run static analysis
- Fail early if any error occurs

**2.2 Continuous Integration (CI)**

Triggered on every push or pull request. Must include:
- Build verification
- All automated tests (unit + integration)
- Coverage report
- Security scans (SAST)

No merge without CI passing.

**2.3 Continuous Delivery / Deployment (CD)**

- Deploy to staging environment automatically if CI passes
- Run smoke tests on staging
- Notify team/agent of success/failure
- Production deployment requires manual approval

## 3. Rules for AI involvement

- AI must never merge directly into protected branches
- AI may propose pipeline updates only after analyzing current CI/CD configs
- AI must validate YAML/JSON configuration syntax before any commit
- AI-generated steps must adhere to existing tooling (GitHub Actions, Docker, etc.)

## 4. Forbidden actions

- Skipping tests or linters
- Writing deploy scripts that bypass approvals
- Changing secrets inline in code
- Hardcoding environment variables
- Ignoring failed jobs

## 5. Examples

\`\`\`yaml
# Correct — pipeline runs tests then deploys to staging
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm test

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy-staging.sh
\`\`\`

\`\`\`yaml
# Incorrect — deploy before tests
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy-production.sh
\`\`\`

## Checklist before merging

- [ ] Linting passes
- [ ] All tests pass
- [ ] Coverage threshold met
- [ ] Security scans completed
- [ ] Staging deployment succeeded
- [ ] No speculative changes or secrets committed
- [ ] Rules documentation updated if pipeline changed
```

---

## 5. `rules/process/security.md`

```markdown
# Security Rules

> Purpose: Ensure every change is secure by default.
> Prevent common classes of vulnerabilities frequently introduced by AI-generated code.
> Context: Read this file before implementing any feature that touches authentication,
> input handling, database queries, external APIs, or configuration.
> Version: 1.0

## 1. Core principle

Security is not optional or deferred.
- Always secure by default
- Always validate external input
- Always enforce authorization explicitly
- Never trust generated code blindly
- Never assume a route or service is internal-only

## 2. Input validation rules

\`\`\`typescript
// Correct — validated DTO
const input = CreateUserSchema.parse(req.body)
userService.create(input)

// Incorrect — raw request passed directly
userService.create(req.body)
\`\`\`

Applies to: HTTP requests, CLI arguments, queue payloads, events, third-party APIs, files, environment variables.

## 3. Authentication rules

- Every protected route must require authentication
- Authentication must happen in middleware/guards only
- Never implement auth logic inside controllers or services
- Tokens must have expiration
- Sessions must be httpOnly + secure
- Never log tokens or passwords

## 4. Authorization rules

\`\`\`typescript
// Correct — policy-based
orderPolicy.canCancel(user, order)

// Incorrect — hardcoded role
if (user.role === "admin") cancelOrder()
\`\`\`

- Every sensitive action must check permissions
- Use policies/guards, not inline role checks
- Deny by default
- Avoid "admin bypass" logic

## 5. Database safety rules

\`\`\`sql
-- Correct — parameterized
SELECT * FROM users WHERE email = ?

-- Incorrect — injection risk
SELECT * FROM users WHERE email = '${email}'
\`\`\`

## 6. Secrets management rules

\`\`\`typescript
// Correct
const key = process.env.STRIPE_API_KEY

// Incorrect
const key = "sk_live_123456"
\`\`\`

## 7. Dependency security rules

- Lock dependency versions
- Run dependency vulnerability scans in CI
- Remove unused packages
- Avoid abandoned libraries
- Prefer standard libraries when possible

## 8. AI-specific safety rules

- Never invent security mechanisms
- Never guess cryptography implementations
- Never design custom auth or crypto
- Use established libraries only
- Never fabricate fields like `isAdmin` or `isSecure`
- If unsure, stop and ask instead of guessing

Reason: hallucinated security logic is dangerous.

## 9. Logging and data exposure rules

\`\`\`typescript
// Correct
{ "error": "Unauthorized" }

// Incorrect
{ "error": "Unauthorized", "stack": ".../src/auth.ts:42", "token": "abc123" }
\`\`\`

## 10. Security checks required before merge

- Lint
- Tests
- Static analysis
- Dependency scan
- Security review of new endpoints
- Validation rules added for new inputs

If any step fails → do not merge.

## Forbidden behaviors
- Disabling validation for convenience
- Skipping auth on "internal" routes
- Hardcoding credentials
- Writing custom crypto
- Trusting client-side validation only
- Catching and ignoring security errors silently
- Merging with known vulnerabilities

## Checklist
- [ ] All inputs validated
- [ ] Auth required where needed
- [ ] Authorization enforced via policies
- [ ] No raw SQL concatenation
- [ ] No secrets in code
- [ ] Dependencies scanned
- [ ] Logs contain no sensitive data
- [ ] Tests cover security-critical paths
- [ ] No invented or speculative security logic
```

---

## 6. `rules/process/testing-strategy.md`

```markdown
# Testing Strategy Rules

> Purpose: Guarantee that every change is tested adequately before merging. Prevent regressions and silent failures in production.
> Context: Read this file before writing any code that affects behavior, APIs, database, or business logic.
> Version: 1.0

## 1. Core principle

Test everything that can fail, and fail fast.

- Unit tests for individual components
- Integration tests for service interactions
- End-to-end tests for critical user flows
- Regression tests for previously fixed bugs
- Test-driven mindset: design tests before implementation

## 2. Test hierarchy rules

**2.1 Unit tests**
- Cover single methods/functions
- Fast, deterministic, no external dependencies

**2.2 Integration tests**
- Cover interaction between services, database, and APIs
- Mock only external systems

**2.3 End-to-end tests**
- Cover full user workflows
- Use staging environment only
- Simulate realistic scenarios

## 3. Test coverage rules

- Minimum 80% coverage per module
- Critical paths: 100%
- Always cover edge cases
- Cover error handling and validation
- Coverage measured automatically in CI
- Low coverage fails pipeline

## 4. Test data rules

- Always use factories or fixtures
- Do not rely on existing production data
- Reset database between tests
- Avoid network calls in unit tests
- Seed realistic test data for integration and e2e tests
- Document seed data used

## 5. Test naming rules

\`\`\`typescript
// Correct
test("user cannot place order without verified email", () => { ... })

// Incorrect
test("test1", () => { ... })
\`\`\`

## 6. Forbidden test patterns

- Silent assertions (expect statements without checks)
- Tests that rely on timing (sleep, delays) unless unavoidable
- Hardcoded IDs or environment data
- Ignoring failed tests
- Skipping tests without documented reason
- Mocking critical logic excessively

## 7. AI-specific test rules

AI-generated code must include:
- Unit tests for every new module
- Integration tests for every new service
- Edge case coverage for business rules
- Regression tests for any changed behavior
- Test scaffolding reviewed before implementation

## 8. CI/CD integration rules

- All tests must run in CI
- Pull requests blocked if tests fail
- Coverage thresholds enforced automatically
- New tests must be included in coverage report

## 9. Test-driven development rules

- Prefer TDD for new features
- Define test cases first
- Implementation only after tests exist
- Refactor safely under passing tests
- Document assumptions in tests

## 10. Definition of done

A change is not complete until:
- Unit, integration, and e2e tests exist as required
- All tests pass locally and in CI
- Coverage thresholds met
- Edge cases tested
- No ignored or skipped tests
- Documentation updated if tests introduce new contracts

## Checklist

- [ ] Unit tests created
- [ ] Integration tests created
- [ ] E2E tests created if required
- [ ] Critical paths covered 100%
- [ ] Edge cases tested
- [ ] Database fixtures/factories used
- [ ] Tests run in CI and passed
- [ ] Coverage thresholds met
- [ ] Test names descriptive and consistent
- [ ] No forbidden patterns used
- [ ] Documentation updated if necessary
```
