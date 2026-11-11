# Что проверено в Resolve

Окружение проверок: DaVinci Resolve 21, macOS.

После каждой сверки с пользователем обновляй этот файл: переноси пункты из
«Требует проверки» в «Работает» или «Не работает» и записывай калибровочные
значения. Диагностический пакет: `scripts/make_test_pack.py`.

## Работает (проверено)

- Макрос `MacroOperator` + `InstanceInput` / `InstanceOutput`, загрузка из
  `Templates/Edit/Titles/<папка>/`.
- `TextPlus`: кириллица, цвет `Red1/Green1/Blue1/Alpha1`, `Center`, `Size`,
  якоря `HorizontalLeftCenterRight` / `VerticalTopCenterBottom`.
- `Background` со сплошным цветом и с `Type = FuID{"Vertical"}` (градиент
  `TopLeft*` → `BottomLeft*`).
- `RectangleMask` через `EffectMask` у Background, `CornerRadius`.
- `Merge` поверх прозрачного `Background` (`TopLeftAlpha = 0`): альфа
  сохраняется.
- Полная статичная карточка из 60+ нод, `Transform` с `UserControls`,
  публикация `Center` / `Size` и пользовательских слайдеров.
- Установка через unzip в Templates и перезапуск Resolve.

## Требует проверки

| # | Что | Тест | Ожидаемый результат |
|---|---|---|---|
| 1 | **Высота `RectangleMask`**. Текущая гипотеза: Height в долях **ширины** кадра (`MASK_UNIT = "width"`). Основание: 600×300 при Height = px/1080 вышел «квадратом» | Test 03, Test 05 | 03: прямоугольник ровно 2:1. 05: полоса **A** (оранжевая) ровно 4:1. Если 4:1 вышла B, поставить `MASK_UNIT = "height"` |
| 2 | Масштаб `Text+ Size` (`px / FRAME_W`) | Test 11 | Записать отношение высоты «H» к планке 100 px |
| 3 | `HorizontalJustificationNew = 0` выравнивает многострочный текст влево | Test 06 | 3 строки по левому краю |
| 4 | Выражения анимации: `time`, `comp.RenderEnd`, `iif`, `min`/`max`, `Point()`, ссылки на UserControls | Test 07 | Выезд и фейд в начале и в конце клипа |
| 5 | Ключевые кадры: `BezierSpline`, `XYPath` | Test 08 | Выезд и фейд только в начале |
| 6 | Shapes: `sRectangle`, `sEllipse`, `sMerge`, `sRender` (имена входов, единицы) | Test 09 | Прямоугольник 400×200 и круг |
| 7 | `RectangleMask.SoftEdge` (тень), `SoftGlow` | Test 10 | Мягкая тень, свечение |
| 8 | `publish_font`: Font + Style в одной ControlGroup | Test 12 | Шрифт и стиль рядом |
| 9 | Ссылка на `Node.Center.X` в выражении (`TxtPeriod`) | Pricing Card | Период стоит справа от цены и двигается вместе с ней |
| 10 | Превью `.png` рядом с `.setting` показывается в Effects Library | любой шаблон | Миниатюра вместо стандартной иконки |
| 11 | Шаблоны типа Effect (`main_input`) и Generator | — | — |
| 12 | Пути установки Windows / Linux | — | — |

Если выражения (п. 4) не работают, переключай шаблоны на `ANIM = "keys"`
(только появление). Если не работают и ключевые кадры, ставь `"static"`.

## Не работает / ограничения

- Перетаскивание `.drfx` в окно Resolve устанавливает шаблон ненадёжно.
  Используй unzip.
- `osascript -e 'quit app "DaVinci Resolve"'` при несохранённом проекте
  возвращает ошибку `-128`. Пользователь должен сам сохранить проект (Cmd+S)
  и закрыть Resolve (Cmd+Q).
- Text+ не переносит строки сам.
- Слот под картинку (Loader) в Title не реализован.
- Переходы (Transitions) не поддерживаются.

## Калибровка

| Параметр | Значение | Дата, версия |
|---|---|---|
| Text+ Size: высота «H» / Size в px | — | — |
| MASK_UNIT | width (гипотеза) | — |
