---
name: skill-creator
description: |
  Creates a new Claude Code skill from scratch following the repository's authoring
  conventions. Use ALWAYS when the user says "create a skill", "new skill",
  "add a skill", "write a SKILL.md", "сделай скилл", "создай скил", "напиши скилл",
  "добавь скилл", or describes a repeatable workflow they want Claude to trigger on.
  Walks through scope definition, trigger design, file scaffolding, body writing,
  and trigger testing. Do NOT use for creating agents (use agents/ directly),
  slash commands (use commands/), or editing an existing skill (use Edit directly).
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Skill Creator

Guide the user through authoring a new skill end-to-end. A skill is a folder under
`skills/<name>/` with a `SKILL.md` whose `description` acts as the trigger Claude sees
in every conversation.

## Workflow

### Step 1 — Scope the skill

Ask the user three questions (skip any they already answered):

1. **What is the one task this skill does?** Enforce single-purpose. If the answer
   covers multiple tasks (e.g. "work with files — PDF, Word, Excel"), push back and
   suggest splitting into separate skills.
2. **When should Claude trigger it?** Collect 3–10 real user phrasings in every
   language they use. These become the trigger phrases in `description`.
3. **When should Claude NOT trigger it?** Collect explicit exclusions. These reduce
   false positives.

If the user cannot answer question 1 in one sentence, the scope is too broad — help
them narrow it before continuing.

### Step 2 — Pick a name

- `kebab-case`, short, matches the folder name.
- Reflects the task, not the implementation (e.g. `commit` not `git-stager`).
- Check for conflicts: run `ls skills/` and confirm the name is free.

### Step 3 — Scaffold the folder

Use the existing generator:

```bash
./scripts/new_skill.sh <name> "<short description>"
```

This creates `skills/<name>/` with `SKILL.md` and `README.md` stubs. Do not create
the folder manually — the generator enforces naming conventions.

### Step 4 — Write the `description`

This is the most important part. The description is the ONLY thing Claude sees in
every conversation — the body is loaded only after Claude decides to trigger.

Rules:

- **Include trigger phrases verbatim** — quote the user's words.
- **Be assertive** — prefer "Use ALWAYS when…" over "Use when…". Claude under-triggers
  skills by default.
- **Cover every language the user works in** — include Russian and English
  phrasings if both apply.
- **State exclusions** — "Do NOT use for X" prevents false positives.
- **Describe both what and when** — not just the action, but the signals.

Keep it under 1024 characters (the linter will catch overruns).

Bad: `Helps with git commits.`

Good: `Delegates git staging and commits to the commit agent. Use ALWAYS when the
user asks to commit changes, create a git commit, "save my work", or says "I'm done".
Supports: commit, commit ru, commit file1 file2. Do NOT use for git pull/push/rebase.`

### Step 5 — Write the body

Keep `SKILL.md` under 500 lines. Use progressive disclosure:

- **Body** — workflow, rules, critical examples. Loaded when the skill triggers.
- **`references/`** — deep-dive documentation, rarely-needed details. Loaded on
  explicit request.
- **`scripts/`** — executable code the skill calls.
- **`assets/`** — templates, fixtures, images.

Body structure:

1. One-paragraph purpose statement.
2. Numbered workflow steps — atomic, concrete, verifiable.
3. Rules section — "Do" and "Do NOT" lists beat prose.
4. 2–3 input/output examples with real user phrasings.
5. Edge cases — what to do when inputs are missing, ambiguous, or the user
   wants to batch operations.

For detailed authoring rules see `references/authoring-guide.md`.

### Step 6 — Test the triggers

Before declaring the skill done, test it against 5–10 realistic user phrasings:

1. **Positive tests** — phrasings that should trigger. Does the description contain
   enough signal?
2. **Negative tests** — related phrasings that should NOT trigger. Are exclusions
   explicit enough?

If a skill under-triggers, the description is too weak — make it more assertive and
add specific phrases. If it over-triggers, add explicit "Do NOT use for…" lines.

Run the linter:

```bash
make lint
```

This checks frontmatter validity, description length, and name/folder consistency.

### Step 7 — Offer to install and commit

After the skill passes `make lint`:

- Ask if the user wants to run `make install` to create the symlink in `~/.claude/`.
- Ask if the user wants to commit. If yes, suggest the message
  `feat(skills): add <name> skill` following Conventional Commits.

Do NOT run `git commit` or `make install` without explicit confirmation.

## Rules

- One skill = one task. Refuse to create multi-purpose skills.
- Never skip Step 1 (scope) — a vague skill will never trigger correctly.
- Always use `scripts/new_skill.sh` for scaffolding.
- Keep `SKILL.md` under 500 lines; move depth to `references/`.
- Description must include assertive triggers AND exclusions.
- Do not commit or install without user confirmation.

## Examples

### Example 1 — Narrow scope enforcement

**User:** создай скилл для работы с документами — pdf, word, excel

**Assistant:** This is three separate skills — Claude triggers best on single-purpose
skills. I'll create `pdf-tools` first. We can add `docx-tools` and `xlsx-tools`
afterwards. Which should we start with?

### Example 2 — Trigger design

**User:** create a skill that runs my test suite

**Assistant:** *(asks for phrasings)* Typical user phrases?

**User:** "run tests", "check tests", "запусти тесты", "прогони тесты"

**Assistant:** *(drafts description)*
`Runs the project test suite via the detected framework (pytest, jest, go test, etc).
Use ALWAYS when the user says "run tests", "check tests", "run the test suite",
"запусти тесты", "прогони тесты", or asks to verify a change passes. Do NOT use for
writing new tests (use test-writer agent) or debugging individual failures.`

### Example 3 — Scope too broad

**User:** скилл "помощник разработчика"

**Assistant:** Too broad — "developer helper" covers hundreds of workflows and would
either never trigger or trigger on everything. What is the single task you want to
automate? Examples: "commit changes", "create a task", "run tests".

## Edge Cases

- **Skill with same name exists** — ask the user to pick a different name or confirm
  they want to replace (in which case, use Edit, not this skill).
- **User wants a slash command, not a skill** — slash commands go in `commands/`.
  Suggest they check the Claude Code docs and handle that separately.
- **User wants an agent, not a skill** — agents go in `agents/` as single `.md`
  files. Point them to `agents/example.md` as a starting point.
- **User provides phrasings only in one language but works bilingually** — ask for
  the other language's phrasings explicitly. Missing translations cause the skill to
  silently fail on the other language.
