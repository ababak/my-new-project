# SPEC — Task Management API

## Goals
- REST API для управління задачами (CRUD: створення, перегляд, оновлення, видалення, зміна статусу).
- Чітке розділення шарів за Clean Architecture для тестованості та незалежності від фреймворків.
- Розгортання через Docker (API + PostgreSQL) з відтворюваним локальним середовищем.

## Non-goals
- Автентифікація/авторизація користувачів (окрема майбутня ітерація).
- Фронтенд або UI — лише API.
- Багатокористувацька/multi-tenant модель даних.

## Technical decisions
- FastAPI як презентаційний фреймворк, SQLAlchemy 2.0 (async) + Alembic для персистентності.
- Залежності між шарами — лише всередину (`domain` ← `application` ← `infrastructure`/`presentation`).
- Типізація — `pyright` (strict), лінт/формат — `ruff`, тести — `pytest`.

## Acceptance criteria
- `make dev` піднімає API та PostgreSQL, `/health` повертає 200.
- `make test` проходить без помилок; `make migrate` застосовує міграції до чистої БД.
- `domain` не має жодних імпортів з FastAPI/SQLAlchemy/Pydantic.
