# API contract generators

The contract is generated from code. Read this file only during `init` and `audit`.

## Choosing `api.generate`

1. Find the framework in the dependency manifest.
2. Use a generator from the table **only if it is already a project dependency**.
   Never add one on your own: suggest it in the report instead.
3. Check the command against the installed version (`--help`, the package docs
   in `vendor/` or `node_modules/`) and point its output at `rules/api/openapi.yaml`.
   JSON output is fine: JSON is valid YAML.
4. Run the command once. If it fails, leave `generate: ""`, write `openapi.yaml`
   by hand from the routes, and report the failure.

| Stack | Generator (must already be installed) | Typical command |
|---|---|---|
| Python · FastAPI | built in | `python -c "import json,<module>; print(json.dumps(<module>.app.openapi()))" > rules/api/openapi.yaml` |
| Python · Django REST | drf-spectacular | `python manage.py spectacular --file rules/api/openapi.yaml` |
| Node · NestJS | @nestjs/swagger | project script that calls `SwaggerModule.createDocument` and writes the file |
| Node · Express/Koa | tsoa, swagger-jsdoc | `npx tsoa spec` with `outputDirectory: rules/api` |
| Java/Kotlin · Spring | springdoc-openapi (Maven/Gradle plugin) | plugin goal with `outputDir` = `rules/api` |
| .NET · ASP.NET Core | Swashbuckle CLI | `dotnet swagger tofile --yaml --output rules/api/openapi.yaml <dll> v1` |
| Go | swaggo/swag, huma | `swag init -o rules/api --outputTypes yaml` (OpenAPI 2.0) |
| PHP · Laravel | dedoc/scramble, knuckleswtf/scribe | `php artisan scramble:export --path=rules/api/openapi.yaml` |
| PHP · Symfony | NelmioApiDocBundle | `bin/console nelmio:apidoc:dump --format=yaml > rules/api/openapi.yaml` |
| Ruby · Rails | rswag | `rake rswag:specs:swaggerize` with the output in `rules/api` |
| GraphQL (any) | server schema printer | print the SDL to `rules/api/schema.graphql` |
| gRPC (any) | — | `.proto` files are the contract; copy or symlink them into `rules/api/` |

Not listed or nothing installed: `generate: ""`. Claude keeps `openapi.yaml` in
step with the routes by hand.

## Postman collection

Every stack, after `openapi.yaml` exists:

```bash
npx -y openapi-to-postmanv2 -s rules/api/openapi.yaml -o rules/api/postman.json -p
```

Postman environments, if needed, go in `rules/api/postman.env.example.json` with
placeholders only, such as `<BASE_URL>` and `<TOKEN>`.
