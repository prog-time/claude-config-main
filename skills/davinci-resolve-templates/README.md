# davinci-resolve-templates

Генерирует шаблоны DaVinci Resolve (Fusion `.setting` → `.drfx`) по картинке
или описанию: титры, плашки, lower thirds, карточки, генераторы с
редактируемыми параметрами в Inspector. Перед генерацией задаёт вопросы
в стиле Grill Me, после генерации устанавливает шаблон в отдельную группу.

## Installation

Скилл подключается после `make install` в корне репозитория.

Опционально: Pillow для анализа картинок и превью
(`python3 -m pip install --user pillow`) и `luac` для проверки синтаксиса.

## Usage

- «сделай шаблон для DaVinci по этому скриншоту»
- «lower third для Resolve с именем и должностью»
- «make a DaVinci Resolve title template from this image»

## Layout

```
SKILL.md
references/   questions.md, design-rules.md, setting-format.md, verified.md, examples/
scripts/      fusion_lib.py, generate.py, analyze_image.py, pack_drfx.py,
              install_macos.sh, make_test_pack.py
templates/    pricing_card.py — пример спецификации
```

Быстрая проверка:

```bash
python3 scripts/generate.py templates/pricing_card.py --out out --pack
python3 scripts/make_test_pack.py --out out/tests
```
