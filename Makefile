.PHONY: dev test migrate lint format

dev:
	docker compose up --build

test:
	docker compose up -d --wait db
	uv run pytest

migrate:
	docker compose up -d --wait db
	uv run alembic upgrade head

lint:
	uv run ruff check .
	uv run pyright
	uv run lint-imports

format:
	uv run ruff format .
