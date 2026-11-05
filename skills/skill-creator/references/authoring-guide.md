# Skill Authoring Guide

Full reference for writing high-quality Claude Code skills. Read this when the
`SKILL.md` workflow is not enough.

## 1. File structure

Every skill is a folder with a mandatory `SKILL.md`:

```text
my-skill/
├── SKILL.md              # required
├── references/           # optional: extra docs, loaded on demand
├── scripts/              # optional: executable code
└── assets/               # optional: templates, fonts, fixtures
```

`SKILL.md` starts with YAML frontmatter:

```yaml
---
name: my-skill
description: |
  When and why to use this skill.
  This is the primary trigger — Claude uses it to decide whether to read the skill.
---
```

## 2. `description` is the most important part

`description` is the only thing Claude sees in every conversation. The body of
`SKILL.md` is loaded only after Claude has decided to trigger the skill.

Rules for a good `description`:

- **Include concrete trigger phrases** — "create a task", "commit", "make a Word doc".
- **Describe both what the skill does and when to use it** — both aspects.
- **Be assertive** — Claude tends to under-trigger skills. Prefer "Use ALWAYS
  when…" over "Use when…".
- **State when NOT to use it** — this reduces false positives.

Bad:

> Helps with git commits.

Good:

> Delegates git staging and commits to the `commit` agent. Use ALWAYS when the user
> asks to commit changes, create a git commit, "save my work", or says "I'm done".
> Supports: `commit`, `commit ru`, `commit file1 file2`.

## 3. Progressive disclosure

Three loading levels — use them deliberately:

| Level              | What               | Always in context? |
|--------------------|--------------------|--------------------|
| Metadata           | `name` + `description` | Yes            |
| `SKILL.md` body    | Instructions       | Only when triggered |
| Bundled resources  | `references/`, `scripts/` | On explicit request |

Takeaway: keep `SKILL.md` compact (under 500 lines). Push depth into `references/`.
Push executable code into `scripts/`.

## 4. Principle of least surprise

A Claude reading the skill must know exactly what to do. Avoid:

- ambiguous instructions;
- skipped steps;
- assumptions about context.

Every step — concrete, atomic, verifiable.

## 5. Skills are point-tools, not swiss-army knives

One skill = one task. Do not try to build a "do-everything" skill.

- **Bad:** a `file-tools` skill that handles PDF, Word, Excel, images.
- **Good:** separate `pdf`, `docx`, `xlsx` skills — each with its own description
  and logic.

## 6. Iterate via testing

Skill creation loop:

1. Draft `SKILL.md`.
2. Invent 5–10 test prompts (realistic user phrasings).
3. Check — does the skill trigger on them?
4. Check — does the skill NOT trigger on unrelated prompts?
5. Tighten the description and body.
6. Repeat.

## 7. Pre-publish checklist

- [ ] `description` contains concrete trigger phrases.
- [ ] `description` contains explicit "when NOT to use" lines.
- [ ] `description` uses the literal `|` block, not folded `>`.
- [ ] `allowed-tools` is declared with a minimal (least-privilege) set.
- [ ] `SKILL.md` is under 500 lines.
- [ ] Long references are moved to `references/`.
- [ ] Every step in the body is concrete and unambiguous.
- [ ] The skill has been tested against realistic prompts.
- [ ] Folder name matches `name` in frontmatter.
- [ ] `make lint` passes with no warnings.

## 8. Common mistakes

| Mistake                    | Fix                                           |
|----------------------------|-----------------------------------------------|
| `description` too broad    | Add concrete phrases and explicit exclusions. |
| `SKILL.md` too long        | Move depth into `references/`.                |
| No examples                | Add 2–3 input/output examples inline.         |
| Skill does not trigger     | Make the description more assertive.          |
| Skill triggers on everything | Add explicit "Do NOT use for…" lines.       |
