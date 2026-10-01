# План: REST API для CRUD нотаток

Статус: draft
Гілка: feature-2
ADR: —

## Мета / не-цілі
Окремі нотатки (заголовок + текст), які можна створювати, переглядати, оновлювати, видаляти та шукати. Нотатки не пов'язані із задачами (Tasks розробляються в `feature-1`).
Не-цілі: автентифікація, зв'язок із Tasks, soft delete, повнотекстовий пошук (ранжування), нові залежності.

## Критерії приймання
- [ ] Усі ендпоінти `/notes` працюють і описані в OpenAPI (`/docs`, `/openapi.json`) — це джерело істини для контракту.
- [ ] Неіснуюча нотатка → 404, невалідні доменні дані → 422 (обидва `{"detail": "..."}`).
- [ ] `title` після `strip` має 1–1024 символи; `text` після `strip` обов'язковий, але може бути порожнім рядком; `null` для `title`/`text` у `PATCH` → 422.
- [ ] `PATCH {}` повертає 200 з незміненою нотаткою, `updated_at` не змінюється.
- [ ] `GET /notes?q=` шукає без урахування регістру підрядок у `title` АБО `text`; `%` і `_` у `q` екрануються; порожній `q` = без фільтра.
- [ ] `make migrate` застосовує міграцію `0001_create_notes_table` до чистої БД.
- [ ] `make lint` і `make test` проходять.

## Контракт
`POST /notes` (201), `GET /notes`, `GET /notes/{id}`, `PATCH /notes/{id}`, `DELETE /notes/{id}` (204).
`Note`: `id` (UUID, `uuid4`), `title`, `text`, `created_at`, `updated_at` (UTC, виставляються в домені).
Список: `limit` (1–200, за замовчуванням 50), `offset`, `q`; порядок стабільний — `created_at`, `id`.
`PATCH`: відсутнє поле = «не змінювати» (sentinel `UNSET`).
Помилки: `NoteNotFoundError` → 404, `InvalidNoteError` → 422 (обробники в `presentation/main.py`); помилки валідації запиту (у т.ч. `limit`/`offset` поза межами) — стандартні 422 FastAPI.
Репозиторій робить `commit` у кожному методі запису (як у Tasks); видалення — hard delete.

## Припущення
| Припущення | Наслідок, якщо хибне |
|---|---|
| (unconfirmed) Текст із самих пробілів після `strip` стає `""` і приймається | Потрібна валідація «text не порожній» → зміна доменного правила та тестів |
| (unconfirmed) `q` також обрізається через `strip` перед пошуком | Пошук із пробілами по краях поводитиметься інакше → зміна в репозиторії та тестах |
| (unconfirmed) Максимальної довжини `q` немає | Можливі дорогі запити → потрібен ліміт у схемі |
| (unconfirmed) Невалідний UUID у шляху дає стандартний 422 FastAPI | Якщо потрібен 404 — додатковий обробник |
| Міграція `0001_create_notes_table` має `down_revision = None` | Якщо `feature-1` зливається першою, міграцію треба перебазувати (інакше дві Alembic-голови) |
| `feature-1` не змінює файли Notes, а Notes змінює спільні файли лише адитивно | Конфлікти злиття в `main.py`, `dependencies.py`, `env.py`, `tests/unit/conftest.py` |
| Нотатки не залежать від Tasks | Якщо з'явиться зв'язок — окрема фіча та міграція |

## Кроки
Порядок — від внутрішніх шарів назовні; один крок — один коміт. Файли Notes мають власні імена (`note_*`), щоб не конфліктувати з `feature-1`.
- [x] 1. domain: `domain/note.py` — `Note` (`create`, `rename`, `change_text`, `strip` для `title` і `text`, довжина `title` 1–1024), `NoteNotFoundError`, `InvalidNoteError` (готово, коли: `pyright` і `import-linter` проходять, `domain` імпортує лише стандартну бібліотеку).
- [ ] 2. application: `application/note_ports.py` (`NoteRepository`: `add`, `get`, `list_notes(q, limit, offset)`, `update`, `delete`), `application/note_dto.py` (inputs, власний sentinel `UNSET`), use cases `CreateNote`, `GetNote`, `ListNotes`, `UpdateNote`, `DeleteNote` у `application/use_cases/` (готово, коли: `make lint` проходить; `UpdateNote` з порожнім набором полів не викликає `update`).
- [ ] 3. infrastructure: `infrastructure/db/note_models.py` (ORM-модель, `timestamptz`), `infrastructure/db/note_repository.py` (пошук через `ILIKE` з екрануванням `%`/`_`, `commit` у кожному методі запису), міграція `0001_create_notes_table`, імпорт моделі в `migrations/env.py` (готово, коли: `make migrate` застосовує міграцію до чистої БД).
- [ ] 4. presentation: `presentation/note_schemas.py`, `presentation/note_router.py`, DI в `presentation/dependencies.py`, підключення роутера й обробників помилок у `presentation/main.py`, опис 404 в OpenAPI (готово, коли: `/openapi.json` містить усі п'ять маршрутів `/notes`).
- [ ] 5. тести, `make lint`, `make test`: unit-тести сутності та use cases з фейковим репозиторієм (`tests/unit/`, фейк реалізує ту саму семантику `q`); API-тести через `httpx.AsyncClient` + `ASGITransport` проти реального PostgreSQL, включно з пошуком, пагінацією, 404, 422, `PATCH {}` (готово, коли: `make lint` і `make test` проходять).

## Ризики / відкриті питання
- Міграція `0001` і sentinel `UNSET` дублюються з `feature-1` (власні копії для уникнення конфліктів); при злитті розв'язати конфлікт міграцій і за бажанням прибрати дубль `UNSET`.
- Міграції не покриті тестами (схема тестів через `create_all`), як і в Tasks.
- API-тести не покривають мережевий шар і запуск через uvicorn/Docker.
- Пошук через `ILIKE` не використовує індекс; на великих обсягах потрібен окремий підхід (поза цією фічею).
- Невирішені `unconfirmed` пункти з таблиці припущень.
