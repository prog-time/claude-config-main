# claude-config-template

> English: [README.md](README.md)

Шаблонный репозиторий для личной конфигурации [Claude Code](https://docs.claude.com/en/docs/claude-code).
Форкните его, наполните своими скилами и агентами — скелет и инструменты уже готовы.

Репозиторий намеренно **пустой**: здесь нет готовых скилов и агентов — только
структура каталогов, Makefile, линтер, скрипт установки и примеры-заглушки.
Всё содержимое добавляете вы.

## Требования

| Инструмент | Версия | Зачем |
|-----------|--------|-------|
| `claude` CLI | любая | основная среда исполнения |
| Python | 3.12+ | `scripts/lint_skills.py` и CI |
| `gh` CLI | любая | опционально, для скилов с интеграцией GitHub |

## Структура

```text
skills/      пользовательские скилы (SKILL.md + ресурсы)
agents/      сабагенты (отдельные .md с frontmatter)
commands/    slash-команды
mcp/         примеры конфигов MCP-серверов
hooks/       PreToolUse / PostToolUse и т. п.
docs/        соглашения, гайды, changelog
scripts/     утилиты: линтер, генератор нового скила
global/      файлы, которые ставятся прямо в ~/.claude: глобальный CLAUDE.md
```

Репозиторий монтируется в `~/.claude/` через симлинки. Любое изменение в репо
мгновенно подхватывается Claude — не нужно копировать файлы вручную.

## Первые шаги после форка

1. **Обновите LICENSE** — замените имя автора и год в строке `Copyright`.
2. **Установите** — запустите `make install`, чтобы создать симлинки в `~/.claude/`.
3. **Добавьте свои скилы** — используйте `make new-skill name=<slug> desc="..."`.
4. **Добавьте своих агентов** — создайте `.md`-файл в `agents/` с обязательным frontmatter (`name`, `description`); см. [`CONTRIBUTING.md`](CONTRIBUTING.md).
5. **Проверьте установку** — `make doctor` диагностирует симлинки, версии и конфиги.
6. **Проверьте файлы** — `make lint` валидирует frontmatter всех скилов и агентов.

## Быстрый старт

```bash
# Форкните репозиторий на GitHub, затем:
git clone git@github.com:<you>/claude-config.git ~/code/claude-config
cd ~/code/claude-config
make install        # симлинки в ~/.claude
make lint           # проверка SKILL.md и agents/*.md
```

Удаление:

```bash
make uninstall      # снимает только наши симлинки, встроенные скилы Anthropic не трогает
```

После удаления или переименования скила, агента или команды уберите оставшиеся ссылки:

```bash
make prune          # удаляет наши симлинки, цель которых пропала из репозитория
```

`install.sh` не ставит dot-файлы, `__pycache__`, `commands/README.md` и
`commands/*_example.md`. Иначе Claude Code показал бы последние два как слэш-команды.

## Боевой клон и клон для разработки

`make install` ставит в `~/.claude` ссылки на рабочее дерево того клона, из
которого его запустили. Какая ветка в нём выбрана, такой конфиг и получают все
сессии Claude. Переключение на ветку задачи меняет боевой конфиг. Поэтому нужны два клона:

```bash
# боевой: всегда на main, только он установлен
git clone git@github.com:<you>/claude-config.git ~/.claude-config-live
cd ~/.claude-config-live && make install

# для разработки: ветки, задачи, PR; не устанавливается
git clone git@github.com:<you>/claude-config.git ~/code/claude-config
```

После того как релиз попал в `main`, обновите боевой клон:

```bash
cd ~/.claude-config-live && git pull --ff-only && make prune
```

`make doctor` предупреждает, если `~/.claude` смотрит на клон не на `main` или с
незакоммиченными изменениями. Чтобы перенести установку, выполните `make uninstall`
в старом клоне, затем `make install` в боевом.

## Разработка нового скила

```bash
make new-skill name=my-skill desc="Короткое описание"
$EDITOR skills/my-skill/SKILL.md
make lint
```

Подробнее — в [`CONTRIBUTING.md`](CONTRIBUTING.md) и [`docs/conventions.md`](docs/conventions.md).

## CI

GitHub Actions запускает `scripts/lint_skills.py` на каждый push и PR — проверяет,
что у каждого `SKILL.md` валидный frontmatter и описание не превышает лимит.

## Лицензия

[MIT](LICENSE)
