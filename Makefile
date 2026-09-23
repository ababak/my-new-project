.PHONY: dev test migrate lint format

dev:
	docker compose up --build

test:
	uv run pytest

migrate:
	uv run alembic upgrade head

lint:
	uv run ruff check .
	uv run pyright

format:
	uv run ruff format .
