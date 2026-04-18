# skill-creator

A meta-skill that walks you through authoring a new Claude Code skill end-to-end:
scope definition, trigger design, scaffolding, body writing, and trigger testing.

## Triggers

- "create a skill", "new skill", "add a skill", "write a SKILL.md"
- "создай скилл", "сделай скилл", "напиши скилл", "добавь скилл"
- Any description of a repeatable workflow the user wants Claude to trigger on.

## Does not trigger for

- Creating **agents** — use `agents/` directly (see `agents/example.md`).
- Creating **slash commands** — use `commands/`.
- Editing an **existing** skill — use Edit directly.

## Dependencies

- `scripts/new_skill.sh` — used for folder scaffolding.
- `make lint` — runs after the skill body is written.

## What it produces

A fully-formed `skills/<name>/` folder with:

- `SKILL.md` — frontmatter with assertive triggers + exclusions, body under 500 lines.
- `README.md` — human-facing description.
- Optional `references/`, `scripts/`, `assets/` as the workflow requires.

## Reference material

See [`references/authoring-guide.md`](references/authoring-guide.md) for the full
authoring rules, anti-patterns, and pre-publish checklist.
