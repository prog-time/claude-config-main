---
name: issue-templates
description: |
  Seeds a project's .github/ISSUE_TEMPLATE/ with the team's base GitHub
  Issue Forms (bug report, feature request, enhancement, question,
  documentation) plus config.yml, copying them verbatim from this skill's
  bundled set so the project can then edit them as its own source of
  truth. Use ALWAYS when the user says "add issue templates", "set up
  issue templates", "bootstrap issue templates", "copy issue templates
  into this project", "добавь шаблоны задач", "настрой шаблоны Issues",
  "перенеси базовые шаблоны в проект", "установи шаблоны Issues",
  "залей шаблоны задач". Creates .github/ISSUE_TEMPLATE/ if missing,
  copies each .yml form plus config.yml one-to-one, never overwrites an
  existing file without asking, and reports what was copied or skipped.
  Do NOT use for: generating CI workflows (use ci-setup), creating
  skills or agents, generating rules/ docs (use rules-generator), or
  writing a task spec / opening an Issue (that is /task_create).
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# issue-templates

Copies the team's **base GitHub Issue Forms** into the current project's
`.github/ISSUE_TEMPLATE/`, verbatim. After seeding, the project owns the
templates: the user edits them, and from then on **those project files
are the source of truth** (GitHub's issue chooser and `/task_create` both
read them).

The language of the templates is intentional: tasks are authored in the
language the templates are written in. The bundled base set is Russian;
a project may translate or replace it freely after seeding.

## Source of truth (what gets copied)

The canonical set lives **next to this file**, in
`assets/ISSUE_TEMPLATE/`:

- `bug_report.yml` — баг-репорт
- `feature_request.yml` — запрос новой фичи
- `enhancement.yml` — улучшение существующего
- `question.yml` — вопрос
- `documentation.yml` — документация
- `config.yml` — `blank_issues_enabled` + опциональные `contact_links`

These are GitHub **Issue Forms** (structured `.yml`), so `required`
fields enforce the format at creation time.

## When it triggers

- The user wants to add / install / bootstrap issue templates in a repo.
- A new project needs the standard task templates before issues are filed.

Do **not** trigger to author a single issue, generate CI, or write rules.

## What to do

### Step 1 — Locate the source

The source directory is this skill's own `assets/ISSUE_TEMPLATE/`
(resolve the directory containing this `SKILL.md`, then `assets/ISSUE_TEMPLATE`).
List the files there; that exact set is what gets copied. Never inline or
regenerate the contents — copy the real files **one-to-one**.

### Step 2 — Resolve the target project

Run `git rev-parse --show-toplevel` to find the project root.

- Success → target is `<root>/.github/ISSUE_TEMPLATE/`.
- Not a git repo → use the current working directory as the root and warn
  the user that the location was inferred from CWD.

### Step 3 — Create the directory if missing

Create `.github/ISSUE_TEMPLATE/` if it does not already exist. Note in the
report whether the directory was created or already present.

### Step 4 — Copy each file (never clobber silently)

For every file in the source set:

- Target file **absent** → copy it verbatim.
- Target file **present** → do **not** overwrite. Ask the user per file
  (overwrite / skip), defaulting to **skip**. Treat skipped files as a
  deliberate keep of the project's existing version.

Copy bytes as-is. Do not reformat, translate, or "improve" the YAML.

### Step 5 — Report

Emit a short summary:

```
Issue templates → <root>/.github/ISSUE_TEMPLATE/

Directory:  created | already existed
Copied:     <list of filenames, or "none">
Skipped:    <filename — reason (already existed), or "none">

Next: edit the copied templates to fit this project. The edited files are
now this project's source of truth (chooser + /task_create read them).
The template language sets the language tasks are written in.
```

## Rules (non-negotiable)

- Copy verbatim. The skill is a one-to-one transfer, not a generator.
- Never overwrite an existing template without explicit confirmation.
- Never delete or rename files already in the project.
- Target is always `.github/ISSUE_TEMPLATE/` at the project root.
- Do not create the Issue itself or run `/task_create` — that is a
  separate command.
