# grill-me-estimate

Grill-me интервью для оценки стоимости разработки ПО. Допрашивает
пользователя по одному вопросу (с рекомендуемым ответом на каждый), пока
задача не разложена на подзадачи до 8 ч, затем считает смету: PERT,
коэффициенты ускорения от Claude Code, буфер риска, итог в рублях по
фиксированной ставке 910 ₽/ч (150 000 ₽/мес). Смета сохраняется в
`estimates/<slug>-<YYYY-MM-DD>.md`.

## Triggers

- «grill me», «грильни меня», «оцени задачу», «оцени стоимость»
- «сколько стоит сделать», «сколько займёт», «посчитай смету», «оценка трудозатрат»
- "estimate this task", "how much would it cost", "cost estimate"
- Описание фичи/проекта с вопросом «сколько по времени / по деньгам»

## Does not trigger for

- Декомпозиция на тикеты без оценки (use `tech-lead`)
- Создание задачи / Issue (use `/task_create`)
- Оценка не-разработческой работы (статьи, видео)

## Structure

- `SKILL.md` — workflow допроса, условие остановки, правила
- `references/estimation-model.md` — ставка, PERT, коэффициенты Claude Code, буферы, пример
- `assets/estimate.md.template` — формат итоговой сметы

## Installation

Picked up automatically after `make install` at the repository root.
