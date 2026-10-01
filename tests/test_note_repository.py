from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.note import Note
from infrastructure.db.note_repository import SqlAlchemyNoteRepository


@pytest.fixture
def repo(session: AsyncSession) -> SqlAlchemyNoteRepository:
    return SqlAlchemyNoteRepository(session)


async def test_add_get_roundtrip(repo: SqlAlchemyNoteRepository) -> None:
    note = Note.create("title", "body")

    await repo.add(note)

    assert await repo.get(note.id) == note


async def test_get_missing_returns_none(repo: SqlAlchemyNoteRepository) -> None:
    assert await repo.get(uuid4()) is None


async def test_update_persists_changes(repo: SqlAlchemyNoteRepository) -> None:
    note = Note.create("old", "text")
    await repo.add(note)

    note.rename("new")
    note.change_text("changed")
    await repo.update(note)

    stored = await repo.get(note.id)
    assert stored is not None
    assert (stored.title, stored.text, stored.updated_at) == ("new", "changed", note.updated_at)


async def test_delete_returns_whether_row_existed(repo: SqlAlchemyNoteRepository) -> None:
    note = Note.create("a", "b")
    await repo.add(note)

    assert await repo.delete(note.id) is True
    assert await repo.delete(note.id) is False
    assert await repo.get(note.id) is None


async def test_list_orders_and_paginates(repo: SqlAlchemyNoteRepository) -> None:
    notes = [Note.create(str(i), "") for i in range(3)]
    for note in notes:
        await repo.add(note)

    page = await repo.list_notes(q=None, limit=2, offset=1)

    assert [n.id for n in page] == [notes[1].id, notes[2].id]


async def test_search_is_case_insensitive_over_title_and_text(
    repo: SqlAlchemyNoteRepository,
) -> None:
    by_title = Note.create("Groceries", "milk")
    by_text = Note.create("Todo", "buy GROCERIES")
    other = Note.create("Other", "none")
    for note in (by_title, by_text, other):
        await repo.add(note)

    found = await repo.list_notes(q="groceries", limit=50, offset=0)

    assert [n.id for n in found] == [by_title.id, by_text.id]
    assert len(await repo.list_notes(q="", limit=50, offset=0)) == 3


@pytest.mark.parametrize("q", ["%", "_", "\\", "50%", "a_b"])
async def test_search_treats_like_wildcards_literally(
    repo: SqlAlchemyNoteRepository, q: str
) -> None:
    literal = Note.create("x", f"has {q} inside")
    decoy = Note.create("axb", "plain text")
    await repo.add(literal)
    await repo.add(decoy)

    found = await repo.list_notes(q=q, limit=50, offset=0)

    assert [n.id for n in found] == [literal.id]
