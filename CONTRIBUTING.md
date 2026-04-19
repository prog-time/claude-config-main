# Contributing

This guide is for anyone who wants to add a skill, an agent, or fix something
in the repository template itself. If you maintain a personal fork, do whatever
works for you; the rules below apply to contributions to the shared template.

## Adding a skill

### 1. Create the structure

```bash
make new-skill name=my-skill desc="Short description of what the skill does"
```

The generator will create `skills/my-skill/SKILL.md` and `skills/my-skill/README.md`
with the required boilerplate.

### 2. Fill in SKILL.md

Minimal frontmatter:

```yaml
---
name: my-skill
description: >
  What the skill does and WHEN to trigger it. Write it as a set of trigger
  signals.
---
```

The full frontmatter specification is in [`docs/conventions.md`](docs/conventions.md).

### 3. Fill in README.md

The goal is to explain the skill to a human in 30 seconds: what it does, how
to invoke it, what its dependencies are. Do not copy text from SKILL.md.

### 4. Validate

```bash
make lint
```

The linter checks frontmatter and scans files for accidentally hardcoded
values (paths, tokens, emails). No errors means it is ready to commit.

---

## Adding an agent

There is no generator for agents. Create the file manually:

```bash
$EDITOR agents/my-agent.md
```

Required frontmatter fields:

```yaml
---
name: my-agent
description: >
  What the agent does. Used by Claude when selecting a sub-agent.
tools: Bash, Read, Grep
model: sonnet
---
```

The full specification is in [`docs/conventions.md`](docs/conventions.md).

### Agent with private resources (optional)

Claude Code only discovers agents from `.md` files at the **top level** of
`agents/` — subdirectories are never scanned. When an agent needs private
resources (stack profiles, prompt snippets, reference material loaded on
demand), use the **"agent + subdirectory of the same name"** pattern:

```text
agents/my-agent.md           # the agent definition (discovered by Claude)
agents/my-agent/             # private resources, loaded by the agent itself via Read
  profile-a.md
  profile-b.md
```

The `.md` file must stay at the top level; the sibling directory holds
everything else. Example: `agents/backend-agent.md` +
`agents/backend-agent/{php,python}.md`.

Shared export assets that an agent copies into *other* projects
(README/CHANGELOG/PR templates) do not belong under `agents/` — they live
in the repo-root [`templates/`](templates/) directory.

---

## Local workflow (full cycle)

```bash
# Create a skill
make new-skill name=my-skill desc="Description"

# Edit
$EDITOR skills/my-skill/SKILL.md
$EDITOR skills/my-skill/README.md

# Validate frontmatter
make lint

# Commit
git add skills/my-skill
git commit -m "feat(skills): add my-skill"
```

---

## Frontmatter requirements (summary)

| Field | Skill (`SKILL.md`) | Agent (`agents/*.md`) |
|-------|--------------------|-----------------------|
| `name` | required, matches directory name | required, matches file name |
| `description` | required, ≤ 1024 characters | required |
| `model` | optional | optional |
| `allowed-tools` / `tools` | optional | optional (recommended) |

Full specification: [`docs/conventions.md`](docs/conventions.md).

---

## CI

GitHub Actions runs `scripts/lint_skills.py` on every push and PR.

Reproduce locally:

```bash
make lint           # standard check
make check          # lint + dry-run install
```

---

## What should NOT go into the template

- Specific production skills and agents — only example stubs.
- Personal paths, tokens, emails, URLs of specific repositories.
- Links to removed skills (`commit`, `task-creator`, `team-lead-router`).
