from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import note_models  # noqa: F401  (registers tables for create_all)
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


async def _create(client: AsyncClient, title: str, text: str = "") -> dict[str, str]:
    response = await client.post("/notes", json={"title": title, "text": text})
    assert response.status_code == 201
    return response.json()


async def test_crud_flow(client: AsyncClient) -> None:
    note = await _create(client, "  Buy milk ", "  2L  ")
    assert note["title"] == "Buy milk"
    assert note["text"] == "2L"

    fetched = await client.get(f"/notes/{note['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == note

    patched = await client.patch(f"/notes/{note['id']}", json={"text": "3L"})
    assert patched.status_code == 200
    assert patched.json()["text"] == "3L"
    assert patched.json()["title"] == "Buy milk"
    assert patched.json()["updated_at"] > note["updated_at"]

    assert [n["id"] for n in (await client.get("/notes")).json()] == [note["id"]]

    assert (await client.delete(f"/notes/{note['id']}")).status_code == 204
    assert (await client.get(f"/notes/{note['id']}")).status_code == 404


async def test_empty_patch_is_noop(client: AsyncClient) -> None:
    note = await _create(client, "a", "b")

    response = await client.patch(f"/notes/{note['id']}", json={})

    assert response.status_code == 200
    assert response.json() == note


async def test_missing_note_returns_404(client: AsyncClient) -> None:
    missing = uuid4()

    for response in (
        await client.get(f"/notes/{missing}"),
        await client.patch(f"/notes/{missing}", json={"title": "x"}),
        await client.delete(f"/notes/{missing}"),
    ):
        assert response.status_code == 404
        assert response.json() == {"detail": f"Note {missing} not found"}


async def test_list_search_and_pagination(client: AsyncClient) -> None:
    first = await _create(client, "Groceries", "milk")
    second = await _create(client, "Todo", "buy GROCERIES")
    await _create(client, "Other", "100% done")

    found = await client.get("/notes", params={"q": "groceries"})
    assert [n["id"] for n in found.json()] == [first["id"], second["id"]]

    literal = await client.get("/notes", params={"q": "%"})
    assert len(literal.json()) == 1

    assert len((await client.get("/notes", params={"q": ""})).json()) == 3

    page = await client.get("/notes", params={"limit": 1, "offset": 1})
    assert [n["id"] for n in page.json()] == [second["id"]]


@pytest.mark.parametrize(
    "body",
    [
        {"title": "   ", "text": "x"},
        {"title": "x" * 1025, "text": "x"},
        {"title": "x"},
        {"text": "x"},
        {},
    ],
)
async def test_create_validation_errors(client: AsyncClient, body: dict[str, str]) -> None:
    assert (await client.post("/notes", json=body)).status_code == 422


async def test_create_accepts_max_title_and_empty_text(client: AsyncClient) -> None:
    note = await _create(client, "x" * 1024, "   ")

    assert len(note["title"]) == 1024
    assert note["text"] == ""


async def test_other_validation_errors(client: AsyncClient) -> None:
    note = await _create(client, "t")

    assert (await client.get("/notes", params={"limit": 0})).status_code == 422
    assert (await client.get("/notes", params={"limit": 201})).status_code == 422
    assert (await client.get("/notes", params={"offset": -1})).status_code == 422
    assert (await client.get("/notes/not-a-uuid")).status_code == 422
    assert (await client.patch(f"/notes/{note['id']}", json={"title": None})).status_code == 422
    assert (await client.patch(f"/notes/{note['id']}", json={"text": None})).status_code == 422
    assert (await client.patch(f"/notes/{note['id']}", json={"title": "  "})).status_code == 422


async def test_openapi_documents_all_routes(client: AsyncClient) -> None:
    paths = (await client.get("/openapi.json")).json()["paths"]

    assert set(paths["/notes"]) == {"get", "post"}
    assert set(paths["/notes/{note_id}"]) == {"get", "patch", "delete"}
    assert "404" in paths["/notes/{note_id}"]["get"]["responses"]
