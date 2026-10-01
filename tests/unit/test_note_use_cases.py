from uuid import uuid4

import pytest

from application.note_dto import UNSET, CreateNoteInput, ListNotesInput, UpdateNoteInput
from application.use_cases.create_note import CreateNote
from application.use_cases.delete_note import DeleteNote
from application.use_cases.get_note import GetNote
from application.use_cases.list_notes import ListNotes
from application.use_cases.update_note import UpdateNote
from domain.note import InvalidNoteError, NoteNotFoundError
from tests.unit.note_fakes import FakeNoteRepository


@pytest.fixture
def repo() -> FakeNoteRepository:
    return FakeNoteRepository()


async def test_create_and_get(repo: FakeNoteRepository) -> None:
    created = await CreateNote(repo).execute(CreateNoteInput(title="a", text="body"))

    assert await GetNote(repo).execute(created.id) == created


async def test_create_invalid_title_raises_and_stores_nothing(repo: FakeNoteRepository) -> None:
    with pytest.raises(InvalidNoteError):
        await CreateNote(repo).execute(CreateNoteInput(title="  ", text="x"))

    assert repo.notes == {}


async def test_get_missing_raises(repo: FakeNoteRepository) -> None:
    with pytest.raises(NoteNotFoundError):
        await GetNote(repo).execute(uuid4())


async def test_list_paginates_in_stable_order(repo: FakeNoteRepository) -> None:
    create = CreateNote(repo)
    first = await create.execute(CreateNoteInput(title="1", text=""))
    second = await create.execute(CreateNoteInput(title="2", text=""))

    page = await ListNotes(repo).execute(ListNotesInput(limit=1, offset=1))

    assert [n.id for n in page] == [second.id]
    assert first.id != second.id


async def test_list_search_matches_title_or_text_case_insensitively(
    repo: FakeNoteRepository,
) -> None:
    create = CreateNote(repo)
    by_title = await create.execute(CreateNoteInput(title="Groceries", text="milk"))
    by_text = await create.execute(CreateNoteInput(title="Todo", text="buy GROCERIES"))
    await create.execute(CreateNoteInput(title="Other", text="none"))

    found = await ListNotes(repo).execute(ListNotesInput(q="groceries"))
    unfiltered = await ListNotes(repo).execute(ListNotesInput(q=""))

    assert [n.id for n in found] == [by_title.id, by_text.id]
    assert len(unfiltered) == 3


async def test_update_changes_only_provided_fields(repo: FakeNoteRepository) -> None:
    note = await CreateNote(repo).execute(CreateNoteInput(title="old", text="keep"))

    updated = await UpdateNote(repo).execute(UpdateNoteInput(note_id=note.id, title="new"))

    assert (updated.title, updated.text) == ("new", "keep")
    assert repo.update_calls == 1


async def test_update_without_fields_is_noop(repo: FakeNoteRepository) -> None:
    note = await CreateNote(repo).execute(CreateNoteInput(title="a", text="b"))
    before = note.updated_at

    result = await UpdateNote(repo).execute(UpdateNoteInput(note_id=note.id, title=UNSET))

    assert result.updated_at == before
    assert repo.update_calls == 0


async def test_update_missing_raises(repo: FakeNoteRepository) -> None:
    with pytest.raises(NoteNotFoundError):
        await UpdateNote(repo).execute(UpdateNoteInput(note_id=uuid4(), title="x"))


async def test_update_invalid_title_raises(repo: FakeNoteRepository) -> None:
    note = await CreateNote(repo).execute(CreateNoteInput(title="a", text="b"))

    with pytest.raises(InvalidNoteError):
        await UpdateNote(repo).execute(UpdateNoteInput(note_id=note.id, title=" "))


async def test_delete_removes_and_missing_raises(repo: FakeNoteRepository) -> None:
    note = await CreateNote(repo).execute(CreateNoteInput(title="a", text="b"))

    await DeleteNote(repo).execute(note.id)

    with pytest.raises(NoteNotFoundError):
        await GetNote(repo).execute(note.id)
    with pytest.raises(NoteNotFoundError):
        await DeleteNote(repo).execute(note.id)
