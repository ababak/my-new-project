# План: фундамент персистентності

Статус: done
Гілка: main
ADR: [0002](../adr/0002-python-3-14-and-persistence-foundation.md)

## Мета / не-цілі
Підготувати інфраструктурну основу перед CRUD: налаштування, async-сесія, міграції, тестове середовище з БД.
Не-ціль: доменні сутності та API.

## Критерії приймання
- [x] `make migrate` застосовує міграції до чистої БД.
- [x] `make test` піднімає PostgreSQL і проходить.
- [x] `domain` не імпортує сторонні бібліотеки.

## Кроки
- [x] 1. Python 3.14 у Dockerfile та локальному `.venv`.
- [x] 2. `infrastructure/settings.py` (`pydantic-settings`, `DATABASE_URL`); у compose для `api` хост БД — `db`.
- [x] 3. `infrastructure/db/` — `Base`, `create_engine`, `create_session_factory`.
- [x] 4. `presentation/dependencies.py::get_session`.
- [x] 5. Alembic (async-шаблон) у `infrastructure/db/migrations/`; `env.py` бере URL із settings і `Base.metadata`.
- [x] 6. Тестова БД `<POSTGRES_DB>_test` у сервісі `db`; тест у транзакції з rollback (savepoint).
- [x] 7. `make test` і `make migrate` піднімають `db` через `docker compose up -d --wait db`.

## Ризики / відкриті питання
- Міграції не покриті тестами (схема тестів через `create_all`).
- `make test` потребує Docker і `.env` (копія `.env.example`).
