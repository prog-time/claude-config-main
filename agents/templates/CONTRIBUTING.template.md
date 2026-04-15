# Contributing to [Project Name]

Thank you for your interest in contributing! This guide will help you get started, even if this is your first time contributing to an open-source project.

---

## How Can I Help?

There are many ways to contribute — you don't need to be a programmer:

- **Report a bug** — found something broken? [Open an issue](#reporting-bugs)
- **Suggest an improvement** — have an idea? [Tell us about it](#suggesting-improvements)
- **Fix a bug or add a feature** — know how to code? [Submit a pull request](#submitting-changes)
- **Improve documentation** — spotted a typo or unclear instructions? PRs for docs are always welcome
- **Answer questions** — help other users in [Discussions](https://github.com/OWNER/REPO/discussions) or [Issues](https://github.com/OWNER/REPO/issues)

---

## Reporting Bugs

Before reporting, please check if the issue already exists in the [issue tracker](https://github.com/OWNER/REPO/issues).

When creating a new issue, include:

1. **What you expected to happen**
2. **What actually happened**
3. **Steps to reproduce** — the exact sequence of actions someone else can follow to see the same problem
4. **Your environment** — OS, PHP/Node version, database type and version
5. **Error messages** — copy the full text, not just a screenshot

<!--
    If your project has an issue template, reference it here:
    Use the [Bug Report template](https://github.com/OWNER/REPO/issues/new?template=bug_report.md).
-->

---

## Suggesting Improvements

Open a [new issue](https://github.com/OWNER/REPO/issues/new) and describe:

1. **The problem you're trying to solve** — what's inconvenient or missing?
2. **Your proposed solution** — how should it work from the user's perspective?
3. **Alternatives you considered** — did you think of other approaches?

---

## Submitting Changes

### First time?

If you've never contributed to an open-source project, here's a step-by-step guide:

**1. Fork the repository**

Click the "Fork" button in the top right corner of the [project page](https://github.com/OWNER/REPO). This creates your own copy.

**2. Clone your fork**

```bash
git clone https://github.com/YOUR-USERNAME/REPO.git
cd REPO
```

**3. Create a branch**

<!--
    Branch naming convention — adapt to your project.
    The format below matches git-hooks style: {type}/{task-id}_{description}
    Adjust if your project uses a different convention.
-->

```bash
git checkout -b feature/issue-123_short_description
```

Branch names must follow the pattern: `{type}/{task-id}_{description}`, where type is `feature`, `bugfix`, `hotfix`, or `docs`.

**4. Make your changes**

Follow the [development setup](#development-setup) below to get the project running locally.

**5. Run the quality checks before committing**

Your code must pass all automated checks before you commit. The project uses git hooks that run these checks automatically, but you should also run them manually to catch issues early. See the [Code Quality](#code-quality-requirements) section below for details.

**6. Commit your changes**

```bash
git add .
git commit -m "Fix: brief description of what you changed"
```

<!--
    If your project uses conventional commits, document the format here:
    
    We use conventional commit messages:
    - `fix: ...` for bug fixes
    - `feat: ...` for new features  
    - `docs: ...` for documentation changes
    - `test: ...` for test changes
-->

**7. Push and create a pull request**

```bash
git push origin feature/issue-123_short_description
```

Then go to your fork on GitHub and click "Compare & pull request".

### Pull request guidelines

- Keep changes focused — one PR per fix or feature
- Write a clear description of what you changed and why
- If your PR fixes an issue, add `Closes #123` in the description
- All linters and static analyzers must pass — CI will block the merge otherwise
- Tests are mandatory (see [Testing Requirements](#testing-requirements))

---

## Development Setup

<!--
    Copy and adapt the installation steps from your README.
    Add any extra steps needed for development (e.g., seeding test data).
-->

**1. Install dependencies**

```bash
composer install
npm install
```

**2. Set up the environment**

```bash
cp .env.example .env
php artisan key:generate
```

**3. Create the database and seed test data**

```bash
php artisan migrate --seed
```

**4. Run the development server**

```bash
php artisan serve
```

<!--
    Adapt the commands above to your actual stack.
    Add any additional setup steps (Docker, queues, etc.).
-->

---

## Code Quality Requirements

This project enforces strict code quality standards through automated tools. These tools run locally via git hooks and remotely in CI. Your pull request will not be merged if any check fails.

### Linters (code style)

Linters check that your code follows the project's formatting rules. They run automatically on every commit via git hooks, and again in CI on every pull request.

<!--
    List the linters your project actually uses.
    Below is the full set from git-hooks — remove the ones that don't apply.
-->

| Language | Tool | What it does | Command |
|----------|------|-------------|---------|
| PHP | [Laravel Pint](https://laravel.com/docs/pint) | Fixes code style automatically (PSR-12 based) | `vendor/bin/pint` |
| JavaScript/TypeScript | [ESLint](https://eslint.org/) | Finds and fixes JS/TS code problems | `npx eslint --fix .` |
| JavaScript/TypeScript | [Prettier](https://prettier.io/) | Formats code consistently | `npx prettier --write .` |
| CSS/SCSS/Less | [Stylelint](https://stylelint.io/) | Validates CSS style rules | `npx stylelint "**/*.css"` |
| HTML | [HTMLHint](https://htmlhint.com/) | Checks HTML for common mistakes | `npx htmlhint "**/*.html"` |
| Markdown | [markdownlint](https://github.com/DavidAnson/markdownlint) | Validates Markdown formatting | `npx markdownlint "**/*.md"` |
| YAML | [yamllint](https://github.com/adrienverge/yamllint) | Validates YAML files | `yamllint .` |
| Shell | [ShellCheck](https://www.shellcheck.net/) | Finds bugs in shell scripts | `shellcheck script.sh` |
| Docker | [Hadolint](https://github.com/hadolint/hadolint) | Lints Dockerfiles for best practices | `hadolint Dockerfile` |

**How Pint works:** when you commit PHP files, Pint runs automatically. If it finds style issues, it fixes them and stages the corrected files. You don't need to do anything manually — just commit again if Pint made changes.

### Static analyzers

Static analyzers catch bugs, type errors, and potential runtime problems without running the code. They check your code more deeply than linters.

<!--
    List the analyzers your project actually uses.
-->

| Language | Tool | What it does | Command |
|----------|------|-------------|---------|
| PHP | [PHPStan](https://phpstan.org/) | Finds type errors, undefined methods, unreachable code | `vendor/bin/phpstan analyse` |
| TypeScript | [tsc](https://www.typescriptlang.org/) | TypeScript type checker | `npx tsc --noEmit` |
| Python | [Mypy](https://mypy-lang.org/) | Static type checking for Python | `mypy app/` |

**How PHPStan works on this project:** the project uses progressive error reduction. PHPStan tracks the error count for each file. Your commit is allowed only if the number of errors decreased by at least 1 (default mode) or reached zero (strict mode). This means you don't have to fix every legacy issue at once — just make things better than they were.

### Running all checks locally

Before pushing, run the full check suite to make sure everything passes:

```bash
# PHP
vendor/bin/pint --test                  # Check style (no auto-fix)
vendor/bin/phpstan analyse              # Static analysis

# JavaScript / TypeScript
npx eslint .                            # Lint JS/TS
npx prettier --check .                  # Check formatting
npx tsc --noEmit                        # Type check

# Python
flake8 app/                             # Lint Python
mypy app/                               # Type check Python
```

<!--
    Adapt the commands to your actual project structure.
    If the project runs in Docker, show the Docker variants too:
    
    # Docker variants (if applicable)
    docker compose exec app vendor/bin/phpstan analyse
    docker compose exec app vendor/bin/pint --test
-->

### What happens in CI

When you open a pull request, GitHub Actions automatically runs:

1. **ShellCheck** — validates all shell scripts
2. **Linters** — checks code style for all changed files
3. **Static analyzers** — type checking and bug detection
4. **Tests** — the full test suite

If any step fails, the PR cannot be merged. Check the "Actions" tab in your PR to see what went wrong.

---

## Testing Requirements

Every new feature or bug fix **must** include automated tests. This is not optional — pull requests without tests will not be merged.

### Coverage target

The project targets **90% test coverage** for all new code. This means:

- Every public method must be tested
- Every significant code path (success, failure, edge cases) must have a test
- Exceptions: controllers, models, DTOs, enums, migrations, and seeders are excluded from coverage requirements (they are tested indirectly through feature/integration tests)

### How to write tests

<!--
    Adapt to your actual test framework and conventions.
-->

```bash
# Run the full test suite
php artisan test

# Run with coverage report
php artisan test --coverage

# Run a specific test
php artisan test --filter=UserServiceTest
```

**Test file location:** for every class in `app/`, there must be a corresponding test file in `tests/Unit/`. The naming convention is:

```
app/Services/UserService.php       → tests/Unit/Services/UserServiceTest.php
app/Actions/CreateOrderAction.php  → tests/Unit/Actions/CreateOrderActionTest.php
```

The project has an automated check (`find_test.sh`) that validates test file existence for every modified PHP class. If your class doesn't have a test, the commit will be blocked.

### What makes a good test

- **Test behavior, not implementation** — verify what the code does, not how it does it
- **One assertion per concept** — each test should verify one specific thing
- **Descriptive names** — `test_user_cannot_register_with_duplicate_email` is better than `test_registration_2`
- **Use factories and seeders** — don't hardcode test data
- **Test edge cases** — empty inputs, boundary values, null values, large datasets

---

## Branch Strategy

<!--
    Describe your branching model.
    The format below matches git-hooks branch naming convention.
-->

- `main` — stable release branch, always deployable
- Feature branches follow the naming pattern: `{type}/{task-id}_{description}`
  - `feature/dev-123_user_auth` — new feature
  - `bugfix/issue-456_fix_login` — bug fix
  - `hotfix/prod-789_critical_patch` — urgent production fix
  - `docs/dev-101_update_readme` — documentation changes
- All changes go through pull requests — direct pushes to `main` are not allowed
- Commit messages are automatically prefixed with the task ID from the branch name

---

## Questions?

If you're unsure about anything, open a [Discussion](https://github.com/OWNER/REPO/discussions) or ask in the related issue. There are no stupid questions — we're happy to help.
