# RiskLesson backend

FastAPI + PostgreSQL + SQLAlchemy 2.0 + Alembic. Стек и обоснование выбора — см. `../CLAUDE.md`, раздел «Стек».
Модель данных — `../docs/process_full_v4.md`, раздел 5; текущая реализация — `app/models/`.

## Локальный запуск

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заполнить DATABASE_URL / ANTHROPIC_API_KEY

alembic upgrade head
uvicorn app.main:app --reload
```

## Статус схемы

Первая миграция (`alembic/versions/2c4bfa7498a7_initial_schema.py`) реализует все 7 сущностей раздела 5
(`User`, `Project`/`ProjectRole`, `Risk`, `Action`, `Lesson`, `RiskDependency`, `AuditLog`) и проверена
циклом `upgrade → downgrade → upgrade` на реальном PostgreSQL 16.

Отступления от буквального текста раздела 5, требующие подтверждения перед импортом seed-данных
(15 рисков ЦГП-2 / 10 уроков БВН) — подробно прокомментированы прямо в коде моделей:

- `app/models/risk.py` — добавлено поле `merged_into_risk_id` (нет в разделе 5, но без него не
  реализовать ветку «Архивирован (объединён с [ID])» из раздела 3).
- `app/models/action.py` — `planned_date`/`forecast_actual_date`/`cost` сделаны `String`, а не
  `Date`/`Numeric`: реальные seed-данные содержат «июн.26», «Фазы 3, 4», «tbd», а не парсящиеся
  даты/числа. `assignee_id` остаётся одиночным (как в разделе 5), хотя часть реальных мероприятий
  перечисляет нескольких исполнителей одной строкой — решение по этому расхождению не принято.
- `app/models/lesson.py` — `source_risk_id` добавлен как отдельное структурированное поле (сам
  раздел 4.6 прямо это рекомендует, в реальном Excel-шаблоне такого поля физически нет).
