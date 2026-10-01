# ADR 0003: REST API для CRUD задач

## Статус
Прийнято — 2026-10-01

## Контекст
Фундамент персистентності (ADR 0002) готовий; потрібен публічний API для керування задачами в межах Clean Architecture (ADR 0001).

## Рішення
- **Ресурс `/tasks`** (`presentation/task_router.py`): `POST` (201), `GET` список, `GET /{id}`, `PATCH /{id}`, `PATCH /{id}/status`, `DELETE /{id}` (204). Повний контракт — в OpenAPI (`/docs`, `/openapi.json`), у SPEC він не дублюється.
- **Use case на операцію** (`CreateTask`, `GetTask`, `ListTasks`, `UpdateTask`, `ChangeTaskStatus`, `DeleteTask`), кожен з єдиним методом `execute()`; вхідні дані — DTO в `application/dto.py`.
- **Часткове оновлення через `PATCH`**: відсутнє поле означає «не змінювати» (sentinel `UNSET`), `description: null` очищає опис, `title: null` відхиляється (422).
- **Статус змінюється окремим ендпоінтом** `PATCH /{id}/status`, а не через загальний `PATCH`.
- **Список**: фільтр `?status=`, пагінація `limit` (1–200, за замовчуванням 50) та `offset`; порядок стабільний — `created_at`, `id`.
- **Помилки**: `TaskNotFoundError` → 404, `InvalidTaskError` → 422 (обидва `{"detail": "..."}`, обробники в `presentation/main.py`); 404 описано в OpenAPI через `ErrorResponse`. Помилки валідації запиту лишаються стандартними для FastAPI.
- **Репозиторій** (`infrastructure/db/task_repository.py`) робить `commit` у кожному методі запису; транзакція одна на операцію.
- **Тести**: unit-тести use cases з фейковим репозиторієм; API-тести через `httpx.AsyncClient` + `ASGITransport` проти реального PostgreSQL з rollback після кожного тесту.

## Наслідки
- Немає окремого ендпоінта «complete»: завершення задачі — це `PATCH /{id}/status` зі `status: "done"`.
- Допустимі переходи між статусами не обмежені — будь-який статус можна встановити з будь-якого.
- Транзакційна межа в репозиторії означає, що операція, яка змінює кілька агрегатів, потребуватиме винесення `commit` (наприклад, у unit of work).
- API-тести не покривають мережевий шар і запуск через uvicorn/Docker.
