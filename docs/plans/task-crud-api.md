# План: REST API для CRUD задач

Статус: done
Гілка: feature-1
ADR: [0003](../adr/0003-task-crud-rest-api.md), [0001](../adr/0001-initial-setup.md), [0002](../adr/0002-python-3-14-and-persistence-foundation.md)

## Мета / не-цілі
Публічний REST API для керування задачами: створення, перегляд, оновлення, видалення, зміна статусу.
Не-цілі: автентифікація, обмеження на переходи між статусами, UI.

## Критерії приймання
- [x] Усі ендпоінти `/tasks` працюють і описані в OpenAPI (`/docs`, `/openapi.json`) — це джерело істини для контракту.
- [x] Неіснуюча задача → 404, невалідні доменні дані → 422.
- [x] `make lint` і `make test` проходять.

## Контракт
`POST /tasks` (201), `GET /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, `PATCH /tasks/{id}/status`, `DELETE /tasks/{id}` (204).
Список: фільтр `?status=`, пагінація `limit` (1–200, за замовчуванням 50) та `offset`; порядок стабільний — `created_at`, `id`.
Статус змінюється окремим ендпоінтом `PATCH /{id}/status`, а не через загальний `PATCH`.
Помилки: `TaskNotFoundError` → 404, `InvalidTaskError` → 422 (обидва `{"detail": "..."}`, обробники в `presentation/main.py`); 404 описано в OpenAPI через `ErrorResponse`; помилки валідації запиту — стандартні для FastAPI.
Контракт не дублюється в SPEC: джерело істини — OpenAPI.

## Кроки
- [x] 1. domain: сутність `Task`, `TaskNotFoundError`, `InvalidTaskError`.
- [x] 2. application: порт репозиторію, DTO (`application/dto.py`), use cases `CreateTask`, `GetTask`, `ListTasks`, `UpdateTask`, `ChangeTaskStatus`, `DeleteTask`.
- [x] 3. infrastructure: ORM-модель, SQLAlchemy-репозиторій, міграція `0001_create_tasks_table`.
- [x] 4. presentation: `task_router.py`, `task_schemas.py`, обробники помилок у `main.py`, DI.
- [x] 5. тести: unit use cases з фейковим репозиторієм; API-тести через `httpx.AsyncClient` + `ASGITransport` проти реального PostgreSQL.
- [x] 6. документація: опис маршрутів і 404 в OpenAPI, ADR 0003, виправлення ARCHITECTURE.

## Ризики / відкриті питання
- API-тести не покривають мережевий шар і запуск через uvicorn/Docker.
- Транзакційна межа в репозиторії: операція над кількома агрегатами потребуватиме unit of work.
