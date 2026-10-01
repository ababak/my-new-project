# ADR 0002: Python 3.14 та фундамент персистентності

## Статус
Прийнято — 2026-10-01

## Контекст
Перед реалізацією CRUD бракувало інфраструктурної основи: Alembic не був ініціалізований, не було налаштувань, engine/session та тестового середовища з БД.

## Рішення
- **Python 3.14** у Docker (`python:3.14-slim`) та локальному `.venv`; `requires-python` лишається `>=3.12`.
- **Налаштування** — `infrastructure/settings.py` (`pydantic-settings`, змінна `DATABASE_URL`). У compose для контейнера `api` хост БД перевизначається на `db`.
- **Персистентність** — `infrastructure/db/` (`Base`, `create_engine`, `create_session_factory`); сесія надається через `presentation/dependencies.py::get_session`.
- **Alembic** (async-шаблон) у `infrastructure/db/migrations/`; `env.py` бере URL з settings і `Base.metadata`.
- **Тести з реальним PostgreSQL** — окрема БД `<POSTGRES_DB>_test` (створюється автоматично) у тому ж compose-сервісі `db`. Кожен тест виконується в транзакції з rollback (savepoint). Схема створюється через `Base.metadata.create_all`, не через Alembic.
- `make test` і `make migrate` піднімають `db` через `docker compose up -d --wait db`.

## Наслідки
- Тести `domain`/`application` і далі можуть використовувати фейкові репозиторії; інтеграційні тести репозиторіїв ходять у реальний Postgres.
- Міграції не перевіряються тестами (схема через `create_all`) — розбіжність моделей і міграцій потрібно ловити окремо.
- Для `make test` потрібен запущений Docker і файл `.env` (копія `.env.example`).
