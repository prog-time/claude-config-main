# issue-templates

Copies the team's base GitHub Issue Forms into a project's
`.github/ISSUE_TEMPLATE/`, verbatim, so the project can edit them as its
own source of truth.

## Installation

Picked up automatically after `make install` at the repository root.

## Usage

Run it from inside the target project:

> добавь шаблоны задач
> set up issue templates in this project

The skill copies the bundled set (`bug_report`, `feature_request`,
`enhancement`, `question`, `documentation` + `config.yml`) into
`.github/ISSUE_TEMPLATE/`, never overwriting existing files without
asking, and reports what was copied or skipped.

## What ships in the box

The canonical templates live in `assets/ISSUE_TEMPLATE/`. They are
GitHub **Issue Forms** (`.yml`) written in Russian; the language of the
templates is the language tasks get authored in. Edit them per project
after seeding.
