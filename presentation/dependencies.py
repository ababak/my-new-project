from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.note_ports import NoteRepository
from application.use_cases.create_note import CreateNote
from application.use_cases.delete_note import DeleteNote
from application.use_cases.get_note import GetNote
from application.use_cases.list_notes import ListNotes
from application.use_cases.update_note import UpdateNote
from infrastructure.db.note_repository import SqlAlchemyNoteRepository
from infrastructure.db.session import create_engine, create_session_factory
from infrastructure.settings import get_settings


@lru_cache
def _session_factory() -> async_sessionmaker[AsyncSession]:
    return create_session_factory(create_engine(get_settings().database_url))


async def get_session() -> AsyncIterator[AsyncSession]:
    async with _session_factory()() as session:
        yield session


def get_note_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> NoteRepository:
    return SqlAlchemyNoteRepository(session)


_NoteRepository = Annotated[NoteRepository, Depends(get_note_repository)]


def get_create_note(repository: _NoteRepository) -> CreateNote:
    return CreateNote(repository)


def get_get_note(repository: _NoteRepository) -> GetNote:
    return GetNote(repository)


def get_list_notes(repository: _NoteRepository) -> ListNotes:
    return ListNotes(repository)


def get_update_note(repository: _NoteRepository) -> UpdateNote:
    return UpdateNote(repository)


def get_delete_note(repository: _NoteRepository) -> DeleteNote:
    return DeleteNote(repository)
