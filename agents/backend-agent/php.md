# Backend Profile — PHP (Laravel)

Stack-specific guidance for the `backend-agent` when the detected stack is
**PHP + Laravel**. This file is loaded on demand — the generic rules live
in `agents/backend-agent.md`.

Other PHP frameworks (Symfony, Slim, custom) are **not** supported by this
profile. If detected, stop and request a dedicated profile.

---

## Stack detection

Signals that confirm Laravel:
- `artisan` file at project root
- `app/Http/Controllers/` directory
- `composer.json` has `laravel/framework` in `require`
- `bootstrap/app.php`, `config/app.php`

Identify the major version from `composer.json` (`laravel/framework`
constraint). Laravel 10 and 11 have meaningful differences — Laravel 11
removed `app/Http/Kernel.php` and moved middleware registration to
`bootstrap/app.php`.

---

## Conventions

- **Style** — PSR-12 enforced via `laravel/pint`. Always run
  `vendor/bin/pint --test` before declaring complete.
- **Strict types** — declare `declare(strict_types=1);` at the top of every
  file you create or modify, unless the project explicitly opts out.
- **PSR-4 autoloading** — namespace according to `composer.json`
  `autoload.psr-4` (usually `App\\` → `app/`).
- **Dependency injection** — use the Laravel service container. Type-hint
  dependencies in constructors; bind interfaces to implementations in
  service providers. Never use `new Service()` for anything with
  collaborators.
- **Readonly DTOs** — use `readonly` classes (PHP 8.2+) or `readonly`
  properties for value objects.

---

## Request validation

- Create a `FormRequest` for every non-trivial endpoint:
  `php artisan make:request StoreOrderRequest`.
- Rules go in `rules()`; authorization in `authorize()`.
- Use `$request->validated()` in the controller — never reach into
  `$request->input()` for fields that should be validated.
- On failure, Laravel returns 422 — wrap the response into the project's
  error envelope via a custom exception handler (see "Error handling").

---

## Database & migrations

- **ORM** — Eloquent. Models live in `app/Models/`.
- **Migrations** — `php artisan make:migration create_orders_table`. Always
  fill both `up()` and `down()`.
- **Mass-assignment** — declare `$fillable` explicitly; never use
  `$guarded = []`.
- **Destructive changes** (drop column, type change on non-empty column)
  use expand-and-contract across two deployments:
  1. Ship new column nullable, backfill, switch reads/writes.
  2. In a later release, drop the old column.
- Never edit a migration that has already been applied anywhere — add a
  new one instead.
- For seeders: keep them idempotent (`updateOrCreate` or `firstOrCreate`).

---

## Error handling

- Map domain exceptions to HTTP responses in the exception handler:
  - Laravel 10 — `app/Exceptions/Handler.php`, override `render()`.
  - Laravel 11+ — `bootstrap/app.php`, use `->withExceptions(function ($e) { ... })`.
- Always return the project envelope:
  ```json
  { "error": { "code": "...", "message": "...", "details": [...] } }
  ```
- Log the internal cause via `Log::error($e)` with context.
- In production (`APP_DEBUG=false`) never leak stack traces. Verify with an
  integration test.

---

## Transactions

- Single-service flows — `DB::transaction(function () { ... })`. The
  closure should not perform external HTTP calls; if it must, keep them
  out of the transaction or use a job.
- For cross-service flows use an outbox table + queued job (see "Async /
  background work"), not a DB transaction held open during HTTP.
- `DB::transaction` retries on deadlock by default — the closure must be
  idempotent.

---

## Avoiding N+1

- Use `with('relation')` for eager loading.
- In non-production environments, enable
  `Model::preventLazyLoading(! $this->app->isProduction());` in
  `AppServiceProvider::boot()`. This surfaces N+1 as exceptions during
  tests and dev.
- Use `loadMissing()` / `loadCount()` when conditional loading is needed.

---

## Integrations

- **HTTP client** — Laravel's `Http` facade (built-in Guzzle wrapper):
  ```php
  Http::timeout(10)
      ->connectTimeout(3)
      ->retry(3, 200, throw: false)
      ->withHeaders(['Idempotency-Key' => $key])
      ->post($url, $payload);
  ```
- Never leave defaults — always set `timeout` and `connectTimeout`.
- Only retry idempotent calls; for writes, pass an idempotency key when
  the provider supports it (Stripe, Paddle, etc.).
- **Webhooks** — verify signatures before processing (Stripe, GitHub,
  etc.). Store a dedupe key (delivery id / event id) in a table for
  24–48h to reject replays.
- **Secrets** — load via `config()` backed by `.env`. Never access
  `env()` outside of `config/*.php` (it returns `null` after config
  cache).
- **Observability** — log external calls with correlation id, duration,
  and outcome. Emit a metric if the project uses one.

---

## Async / background work

- **Queued jobs** — `php artisan make:job ProcessOrder`. Default queue
  connection from `.env` (`QUEUE_CONNECTION=redis` is standard).
- **Dispatch** — `ProcessOrder::dispatch($order)`. Use `dispatchAfterResponse()`
  for work tied to the request lifecycle.
- **Batches & chains** — `Bus::batch([...])` / `Bus::chain([...])` for
  fan-out and sequential pipelines.
- **Scheduling** — `app/Console/Kernel.php` (Laravel 10) or
  `routes/console.php` (Laravel 11+).
- Synchronous handling only for work under ~300ms. Everything heavier
  goes to a queued job.

---

## Testing

- **PHPUnit** or **Pest** — match the project's choice.
- **Feature tests** — hit the HTTP kernel via `$this->postJson(...)`.
  Assert against the response envelope, not just status.
- **Database** — use `RefreshDatabase` trait (or `DatabaseTransactions`
  for speed); run against a dedicated test SQLite or MySQL.
- **Factories** — every model has a factory (`database/factories/`).
  Tests use factories, not raw inserts.
- Every new endpoint: happy-path + at least one 4xx test.
- Every new service method: unit test for happy and one failure case.

---

## Static analysis & commands

- `vendor/bin/pint --test` — style.
- `vendor/bin/phpstan analyse` (or `vendor/bin/larastan`) — static
  analysis; target level 7+.
- `vendor/bin/phpunit` / `vendor/bin/pest` — tests.
- `php artisan test --parallel` — full test suite if the project is set
  up for it.

Run all configured tools before reporting complete. Check `composer.json`
`scripts` section for project-specific aliases (`composer test`,
`composer lint`).

---

## Common gotchas

- `dd()` / `dump()` left in shipped code — grep before finishing.
- `env()` called outside `config/*.php` returns `null` in production
  (config cache).
- Mass-assignment with `$guarded = []` — an open invite for injection
  attacks via mass assignment. Always use `$fillable`.
- Eloquent's `Model::save()` doesn't return `false` on validation
  failures — validate upstream via `FormRequest`.
- Jobs serialize their parameters — don't pass Eloquent models with
  unsaved changes or heavy dependencies; pass ids instead.
- Laravel 11 removed `app/Http/Middleware/` — middleware goes into
  `bootstrap/app.php`. Don't copy Laravel 10 tutorials verbatim.
- Timezones — never rely on the server's default. Use
  `config('app.timezone')` (usually `UTC`); store UTC, convert at the
  edges.
