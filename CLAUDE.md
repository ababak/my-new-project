# CLAUDE.md — Task Management API

## Стек
Python 3.12 · FastAPI · PostgreSQL · SQLAlchemy 2.0 (async) · Alembic · Docker · `uv` (пакети) · `pytest` (тести) · `ruff` (лінт/формат) · `pyright` (типізація) · `import-linter` (перевірка шарів)

## Архітектура: Clean Architecture

### Шари та правило залежностей
```
presentation  ──┐
infrastructure ─┼──▶ application ──▶ domain
```
- **domain/** — entities, value objects, доменні винятки. Не залежить ні від чого (жодних сторонніх бібліотек, жодного FastAPI/SQLAlchemy).
- **application/** — use cases, DTO, порти (інтерфейси репозиторіїв/сервісів). Залежить лише від `domain`.
- **infrastructure/** — реалізації портів: SQLAlchemy-репозиторії, зовнішні сервіси, конфігурація БД. Залежить від `application` + `domain`.
- **presentation/** — FastAPI роутери, схеми запиту/відповіді (Pydantic), DI-обв'язка. Залежить від `application` + `domain`.

**Правило:** стрілки залежностей йдуть тільки всередину (до `domain`). Зовнішній шар ніколи не імпортується внутрішнім. `domain` та `application` нічого не знають про FastAPI, SQLAlchemy чи PostgreSQL. Виняток: `presentation` може напряму імпортувати `infrastructure` для DI-обв'язки (composition root), але не навпаки — `infrastructure` ніколи не імпортує `presentation`.

Це правило перевіряється автоматично (`import-linter`, контракти в `pyproject.toml`), а не лише на словах — `make lint` впаде, якщо його порушити.

## Конвенції
- Іменування: `snake_case` для файлів/функцій, `PascalCase` для класів.
- Кожен use case — окремий клас з одним публічним методом `execute()`.
- Взаємодія з БД лише через інтерфейси (порти), визначені в `application`, реалізовані в `infrastructure`.
- Pydantic-схеми (presentation) ніколи не використовуються як доменні моделі.
- Типізація обов'язкова для всіх публічних функцій/методів; перевірка — `pyright` у strict-режимі.
- Один модуль — одна відповідальність (Single Responsibility).

## Команди
```bash
make dev       # підняти API + PostgreSQL через docker-compose
make test      # запустити pytest
make migrate   # застосувати alembic-міграції
make lint     # ruff check + pyright + import-linter (шари)
make format    # ruff format
```

## Обмеження для агента
- Не додавати залежності в `domain`, окрім стандартної бібліотеки Python.
- Не писати SQL/ORM-код напряму в `presentation` чи `application`.
- Секрети/production-креденшали не передавати в bash-команди та не комітити.
