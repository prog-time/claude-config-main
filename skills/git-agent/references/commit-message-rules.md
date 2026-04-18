# Commit Message Rules

Applies to Modes A (atomic commit workflow) and B (hook output).

## Rules — strictly enforced (all languages)

- **Single line** — subject line only. No body, no bullet points.
- **Max 72 characters** for the subject line, **including the
  `issues-{N}|` prefix**.
- **Mandatory `issues-{N}|` prefix** — see next section.
- **No conventional commit type prefix** — do not use `feat:`, `fix:`,
  `chore:` anywhere in the message (the issue prefix replaces them).
- **No full file paths** — file names only, and only when they add
  clarity.
- **No Markdown formatting** (`**`, `*`, `` ` ``, `#`, `-`).
- **Output only the commit message text** in Mode B — no explanation,
  no markdown, no quotes. The hook writes it directly to
  `COMMIT_EDITMSG`.

## Mandatory branch prefix (strict)

Every commit message **must** start with `issues-{N}|` where `{N}` is
the issue number extracted from the current branch.

- Resolve the branch: `git branch --show-current`.
- Extract `{N}` with regex `^issues-(\d+)$`.
- If the branch name does not match, **abort**. Do not coerce, do not
  ask the user for a number, do not fall back to no-prefix. The only
  valid resolution is to switch to an `issues-{N}` branch (or create
  one via `/task_complete`).
- The pipe `|` is the separator — no spaces around it.
- **One issue per prefix.** Never produce `issues-12,15|...`. If two
  issues are logically linked, stack the branches
  (`git switch -c issues-15 issues-12`) and commit each issue's work
  on its own branch.

### Abort message (Mode A)

```text
Error: commits require an 'issues-{N}' branch, got '{branch}'.
Run /task_complete with a task spec, or switch to an existing
'issues-{N}' branch.
```

### Abort message (Mode B — hook output)

Mode B cannot print human-readable errors because stdout becomes the
commit message. Output exactly this single line so the bad message is
visible in the editor and the user can abort:

```text
error: not on an issues-{N} branch
```

## English (`en`) — imperative mood, present tense

After the `issues-{N}|` prefix, start with a lowercase imperative verb:
`add`, `fix`, `update`, `remove`, `extract`, `handle`, `validate`,
`move`, `rename`, `improve`, `refactor`, `migrate`, `configure`,
`enable`, `disable`.

```text
issues-42|add password reset via email
issues-42|prevent duplicate job dispatch on retry
issues-43|extract profile update into separate action
issues-44|update composer dependencies
issues-45|fix duplicate job dispatch on retry
issues-46|remove deprecated payment adapter
```

## Russian (`ru`) — past tense, active voice, third person, subject omitted

After the `issues-{N}|` prefix use past-tense active forms: «добавил»,
«исправил», «изменил», «удалил», «вынес», «обновил», «переименовал»,
«улучшил», «настроил», «включил», «отключил».

- Do NOT use infinitive: wrong — «добавить», «исправить»
- Do NOT use passive voice: wrong — «добавлено», «исправлено»,
  «изменено»
- Subject is omitted — start directly with the verb after the prefix.

```text
issues-42|добавил сброс пароля через email
issues-45|исправил дублирование задач в очереди
issues-43|вынес обновление профиля в отдельный экшен
issues-44|обновил зависимости composer
issues-46|удалил устаревший адаптер платёжного шлюза
```

## Other languages

Follow the same pattern as Russian: past tense, active voice, third
person, subject omitted.

## Examples of bad commit messages (never produce these)

```text
feat(auth): add password reset            ← conventional-commit prefix
add password reset via email              ← missing issues-{N}| prefix
issues-12: add password reset             ← wrong separator (use |)
issues-12 | add password reset            ← spaces around | forbidden
issues-12,15|add password reset           ← multi-issue prefix forbidden
updated files                             ← too vague
update app/Services/UserService.php       ← full path
WIP                                       ← not a commit message
issues-12|добавить сброс пароля           ← infinitive (Russian)
issues-12|сброс пароля добавлен           ← passive voice (Russian)
```

## Self-Verification Before Output (Mode B)

- [ ] Current branch matches `^issues-(\d+)$` — if not, output the
      literal `error: not on an issues-{N} branch` and stop
- [ ] Message starts with `issues-{N}|` where `{N}` is the captured
      issue number (no spaces, single pipe)
- [ ] `git diff --cached` was read — message reflects actual staged
      changes
- [ ] Single line, max 72 characters **including** the `issues-{N}|`
      prefix
- [ ] Language matches the command argument (default English)
- [ ] No full file paths, no conventional-commit type prefix
- [ ] Output is the message text only — no extra words, no markdown,
      no quotes
