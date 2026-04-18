# Backend Profile — Python (FastAPI)

Stack-specific guidance for the `backend-agent` when the detected stack is
**Python + FastAPI**. This file is loaded on demand — the generic rules
live in `agents/backend-agent.md`.

Other Python frameworks (Django / DRF, Flask, Starlette-only, etc.) are
**not** supported by this profile. If detected, stop and request a
dedicated profile.

---

## Stack detection

Signals that confirm FastAPI:
- `from fastapi import FastAPI` and an `app = FastAPI(...)` instance
- `pyproject.toml` (or `requirements*.txt`) includes `fastapi` and typically
  `uvicorn` / `hypercorn`
- ASGI entrypoint (e.g. `app.main:app`) referenced in a Dockerfile, Procfile,
  or deployment config

Detect the dependency manager:
- `poetry.lock` → Poetry
- `uv.lock` → uv
- `pdm.lock` → pdm
- `requirements.txt` + no lockfile → pip

Identify the FastAPI and Pydantic versions from the lockfile — **Pydantic v1
and v2 differ significantly** (see "Common gotchas").

---

## Conventions

- **Python version** — match `pyproject.toml` `requires-python` /
  `.python-version`. Don't fall back to older syntax if the project
  targets 3.11+.
- **Type hints** — mandatory on every new function. Modern idioms:
  `list[int]`, `dict[str, X]`, `X | None`, `Self`, `TypedDict`, `Protocol`.
- **Style** — PEP 8 enforced via `ruff format` (or `black` on older
  projects). Imports organized by `ruff` / `isort`.
- **Async vs sync** — FastAPI endpoints should be `async def` when they
  perform I/O. A sync `def` endpoint runs in a thread pool and can block
  under load. Never mix blocking I/O (`requests`, sync SQLAlchemy) inside
  an `async def` handler.
- **Settings** — centralize config via `pydantic-settings` (`BaseSettings`),
  parsed once at startup. Never scatter `os.environ.get()` across modules.

---

## Request validation

- Pydantic models for every request body, query params group, and response.
- Use `response_model=...` on every route to enforce the output shape —
  this is non-negotiable, it's what keeps the API contract in sync with
  runtime behavior.
- Validation errors are returned by FastAPI as 422; **override the default
  handler** to wrap them into the project's error envelope (see "Error
  handling").
- For complex query parameters, group them in a Pydantic model with
  `Depends`:
  ```python
  class OrderFilters(BaseModel):
      status: str | None = None
      created_at_gte: datetime | None = None

  @app.get("/v1/orders")
  async def list_orders(filters: OrderFilters = Depends()): ...
  ```

---

## Database & migrations

- **ORM** — SQLAlchemy 2.x (async) is the typical choice with FastAPI.
  SQLModel is acceptable if the project standardizes on it.
- **Session** — one `AsyncSession` per request, injected via `Depends`.
  Don't cache sessions at module scope.
- **Migrations** — Alembic. Generate with
  `alembic revision --autogenerate -m "..."`. **Always review and edit**
  the generated ops — autogenerate misses things (indexes, server
  defaults, renames vs drop+add).
- Every migration has both `upgrade()` and `downgrade()`.
- Never edit a migration that has been applied anywhere — add a new one.
- Destructive changes use expand-and-contract across two deployments.

---

## Error handling

- Register exception handlers in the app factory:
  ```python
  @app.exception_handler(DomainError)
  async def domain_error_handler(request, exc):
      return JSONResponse(
          status_code=exc.status_code,
          content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
      )
  ```
- Override FastAPI's `RequestValidationError` handler to return the
  project envelope (default returns `{"detail": [...]}` which does not
  match the contract).
- Register a catch-all for `Exception` in production to avoid leaking
  tracebacks.
- Log the internal cause via `logging` / `structlog` / `loguru` (match
  project choice). Include request id / correlation id.

---

## Transactions

- **Async SQLAlchemy**:
  ```python
  async with session.begin():
      await session.execute(...)
      await session.execute(...)
  ```
- One transaction per unit of work. Don't hold it open across external
  HTTP calls — finish the DB work, commit, then call the outside world
  (or use an outbox pattern for cross-service consistency).
- For read-heavy endpoints, don't wrap single `SELECT`s in explicit
  transactions — the session's implicit behavior is sufficient.

---

## Avoiding N+1

- Use `selectinload()` / `joinedload()` in the query:
  ```python
  stmt = select(Order).options(selectinload(Order.items))
  ```
- Enable SQLAlchemy's `echo=True` temporarily in dev to audit actual
  queries.
- Never iterate a result set and access `.some_relation` without
  preloading — that's the classic N+1.

---

## Integrations

- **HTTP client** — `httpx` (sync and async). `requests` only if the
  project already standardizes on it; avoid mixing.
- Always set explicit timeouts:
  ```python
  async with httpx.AsyncClient(
      timeout=httpx.Timeout(connect=3.0, read=10.0, write=10.0, pool=5.0),
  ) as client:
      ...
  ```
- **Retries** — use `tenacity` with exponential backoff and jitter.
  Retry only idempotent calls; for writes, pass an idempotency key when
  the provider supports it (Stripe, etc.).
- **Webhooks** — verify signatures before any processing. Dedupe by
  delivery id (or `event.id`) in a table for 24–48h.
- **Secrets** — load via `pydantic-settings`; type-check at startup.
- **Observability** — log external calls with correlation id, duration,
  status, outcome. Emit metrics via the project's telemetry lib.

---

## Async / background work

- **Task queue** — pick what the project already uses:
  - **Arq** — async-native Redis queue, fits FastAPI naturally.
  - **Taskiq** — async framework, supports multiple brokers.
  - **Celery** — broad ecosystem; acceptable if the project uses it.
  - **Dramatiq** / **RQ** — simpler Redis-backed alternatives.
- Define tasks in dedicated modules (`app/tasks/`), not inline in
  routes.
- Every task has explicit timeouts, retry policy, and an idempotency
  story (the queue may deliver twice).
- **Scheduling** — Arq's cron jobs / Taskiq scheduler / Celery beat.
- Synchronous handling only for work under ~300ms; everything heavier
  goes to a queue.

---

## Testing

- **pytest** is standard. Use `pytest-asyncio` for async tests.
- **HTTP tests** — `httpx.AsyncClient(app=app, base_url="http://test")`
  against the FastAPI app directly (faster than spinning up Uvicorn).
- **Database** — use a dedicated test DB or testcontainers. Never mock
  the session for integration tests that exercise SQL; use a real test
  DB with transaction rollback per test.
- **Fixtures** — fixtures for `app`, `client`, `db_session`, and sample
  data factories (`factory-boy` or a lightweight custom factory).
- Every new endpoint: happy-path + at least one 4xx test.
- Every new service function: unit test for happy and one failure case.

---

## Static analysis & commands

- **Type check** — `mypy` (with strict settings) or `pyright`. Must pass.
- **Lint + format** — `ruff check .` and `ruff format --check .`.
- **Tests** — `pytest -q`.
- **Migrations** — `alembic upgrade head` (dry run if the project has
  tooling for it) and verify the resulting schema matches the ORM.

Run all configured tools before reporting complete. Check
`pyproject.toml` `[tool.*]` sections and any `Makefile` / `justfile` for
project-specific aliases.

---

## Common gotchas

- `print()` left in shipped code — grep before finishing.
- Mutable default arguments (`def f(x=[])`) — never use; Ruff `B006`
  catches these.
- **Pydantic v1 vs v2** — `.dict()` vs `.model_dump()`, `.parse_obj()`
  vs `.model_validate()`, `Config` class vs `model_config`. Check the
  version before copying idioms.
- Mixing sync blocking I/O inside `async def` — blocks the event loop
  under Uvicorn. Use `httpx.AsyncClient` and async SQLAlchemy, not
  `requests` / sync Session.
- `Depends(...)` with default arguments — shared across requests if the
  dependency returns mutable state. Return new instances per call.
- SQLAlchemy 1.x vs 2.x — the `select()` API, `session.execute(stmt)`,
  and async patterns changed significantly. Check the major version.
- Forgetting `response_model=...` — the OpenAPI schema desyncs from the
  actual payload. Always set it.
- Timezone-naive vs aware datetimes — always store UTC with `tzinfo`;
  never rely on the server's local time. Pydantic v2 distinguishes
  `AwareDatetime` vs `NaiveDatetime` — use `AwareDatetime` on the wire.
- Running migrations in entrypoint scripts — causes race conditions
  with multiple replicas. Run migrations as a separate deploy step.
