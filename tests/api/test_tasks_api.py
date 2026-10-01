from collections.abc import AsyncIterator
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import models  # noqa: F401  (registers tables for create_all)
from presentation.dependencies import get_session
from presentation.main import app


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_crud_flow(client: AsyncClient) -> None:
    created = await client.post("/tasks", json={"title": "  Buy milk ", "description": "2L"})
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Buy milk"
    assert task["status"] == "todo"

    fetched = await client.get(f"/tasks/{task['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == task

    patched = await client.patch(f"/tasks/{task['id']}", json={"description": None})
    assert patched.status_code == 200
    assert patched.json()["description"] is None
    assert patched.json()["title"] == "Buy milk"

    status_resp = await client.patch(f"/tasks/{task['id']}/status", json={"status": "done"})
    assert status_resp.json()["status"] == "done"

    listed = await client.get("/tasks", params={"status": "done"})
    assert [t["id"] for t in listed.json()] == [task["id"]]

    assert (await client.delete(f"/tasks/{task['id']}")).status_code == 204
    assert (await client.get(f"/tasks/{task['id']}")).status_code == 404


async def test_missing_task_returns_404(client: AsyncClient) -> None:
    missing = uuid4()

    assert (await client.get(f"/tasks/{missing}")).status_code == 404
    assert (await client.patch(f"/tasks/{missing}", json={"title": "x"})).status_code == 404
    assert (await client.delete(f"/tasks/{missing}")).status_code == 404


async def test_validation_errors(client: AsyncClient) -> None:
    assert (await client.post("/tasks", json={"title": "   "})).status_code == 422
    assert (await client.post("/tasks", json={})).status_code == 422
    assert (await client.get("/tasks", params={"limit": 0})).status_code == 422
    assert (await client.get("/tasks/not-a-uuid")).status_code == 422

    created = (await client.post("/tasks", json={"title": "t"})).json()
    assert (await client.patch(f"/tasks/{created['id']}", json={"title": None})).status_code == 422
    bad_status = await client.patch(f"/tasks/{created['id']}/status", json={"status": "nope"})
    assert bad_status.status_code == 422
