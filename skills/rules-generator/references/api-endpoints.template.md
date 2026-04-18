# Template — `rules/api/endpoints.md`

Produce EXACTLY this content. This file mandates a single Swagger-backed
API contract; its rules apply regardless of project stack.

````markdown
# API Contract Rules

> Context: Read this file before adding, modifying, or deleting any HTTP endpoint.
> Version: 3.0

## 1. Core principle

The API is defined only by Swagger.

- Swagger is the contract
- Swagger is the documentation
- Swagger is the integration surface
- Swagger is the source of truth
- No parallel descriptions are allowed

If behavior exists in code but not in Swagger, it is a bug.

If Swagger exists but code differs, the implementation is a bug.

## 2. Single file rule (mandatory)

The entire API must be described in one file.

**Location:** `rules/api/openapi.yaml`

Correct

```text
rules/api/openapi.yaml
```

Incorrect

```text
rules/api/endpoints/*.yaml
rules/api/endpoints.md
docs/api.md
swagger-per-route/
```

## 3. Format rules (mandatory)

- OpenAPI 3.x only
- YAML preferred
- Must be machine-readable
- Must be valid
- Must load in Swagger UI
- Must import into Postman
- Must support client generation

```yaml
# Correct
openapi: 3.0.3
```

Incorrect: free-text Markdown, hand-written tables, partial specs

## 4. Completeness rules (mandatory)

Every endpoint must include:

- summary
- description
- tags
- operationId
- security
- parameters (path/query/header/cookie)
- requestBody schema
- all response statuses
- response schemas
- examples
- error formats
- business rule references
- side effects
- rate limits (if applicable)

Nothing may be implicit.

## 5. Path definition rules

```yaml
# Correct
paths:
  /users/{id}:
    get:
      summary: Get user by id
      description: Returns a single user resource
      operationId: getUserById
      tags: [Users]
```

```yaml
# Incorrect
paths:
  /users/{id}:
    get: {}
```

## 6. Schema rules

```yaml
# Correct
components:
  schemas:
    User:
      type: object
      required: [id, email]
      properties:
        id:
          type: integer
        email:
          type: string
```

```yaml
# Incorrect
schema:
  type: object
```

## 7. Response rules

```yaml
# Correct
responses:
  "200":
    description: Success
  "404":
    description: Not found
```

```yaml
# Incorrect
responses:
  "200": {}
```

## 8. Business rule linkage

```yaml
x-business-rules:
  - BR-001
  - BR-004
```

## 9. Side effects rules

```yaml
x-side-effects:
  - dispatch UserRegistered
  - enqueue SendWelcomeEmail
  - call Stripe API
```

Hidden side effects are forbidden.

## 10. Security rules

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
```

## 11. Validation rules (mandatory)

Before merging changes:

- Validate schema
- Lint spec
- Ensure Swagger UI loads
- Ensure Postman import works
- Ensure client generation succeeds

Suggested tools: `swagger-cli validate`, `spectral lint`, `openapi-generator`

## 12. Change workflow (mandatory)

1. Update Swagger
2. Validate spec
3. Generate clients/types
4. Implement code
5. Write tests

Never implement first.

## 13. AI-specific rules

- Never invent undocumented routes
- Never change behavior without updating Swagger
- Never guess schemas
- Always read Swagger first
- Treat Swagger as executable specification

## 14. Definition of done

- openapi.yaml updated
- Spec valid
- New routes documented
- Schemas defined
- Examples provided
- Security defined
- Business rules linked
- Side effects listed
- Clients regenerate successfully
- Tests pass

## Forbidden behaviors

- Markdown endpoint descriptions
- Per-endpoint files
- Missing schemas
- Missing examples
- Undocumented statuses
- Hidden side effects
- Code without spec
- Multiple Swagger files
- Divergence between code and spec

## Checklist

- [ ] Single openapi.yaml exists
- [ ] All routes documented
- [ ] All params typed
- [ ] All schemas defined
- [ ] Examples present
- [ ] Security defined
- [ ] Business rules linked
- [ ] Side effects listed
- [ ] Spec validates
- [ ] Matches real behavior

````
