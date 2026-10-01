from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.note import Note, NoteNotFoundError
from infrastructure.db.note_models import NoteModel

_LIKE_ESCAPE = "\\"


def _to_entity(model: NoteModel) -> Note:
    return Note(
        id=model.id,
        title=model.title,
        text=model.text,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _contains_pattern(q: str) -> str:
    escaped = (
        q.replace(_LIKE_ESCAPE, _LIKE_ESCAPE * 2)
        .replace("%", f"{_LIKE_ESCAPE}%")
        .replace("_", f"{_LIKE_ESCAPE}_")
    )
    return f"%{escaped}%"


class SqlAlchemyNoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, note: Note) -> None:
        self._session.add(
            NoteModel(
                id=note.id,
                title=note.title,
                text=note.text,
                created_at=note.created_at,
                updated_at=note.updated_at,
            )
        )
        await self._session.commit()

    async def get(self, note_id: UUID) -> Note | None:
        model = await self._session.get(NoteModel, note_id)
        return _to_entity(model) if model else None

    async def list_notes(self, *, q: str | None, limit: int, offset: int) -> list[Note]:
        stmt = select(NoteModel).order_by(NoteModel.created_at, NoteModel.id)
        if q:
            pattern = _contains_pattern(q)
            stmt = stmt.where(
                or_(
                    NoteModel.title.ilike(pattern, escape=_LIKE_ESCAPE),
                    NoteModel.text.ilike(pattern, escape=_LIKE_ESCAPE),
                )
            )
        result = await self._session.scalars(stmt.limit(limit).offset(offset))
        return [_to_entity(m) for m in result]

    async def update(self, note: Note) -> None:
        model = await self._session.get(NoteModel, note.id)
        if model is None:
            raise NoteNotFoundError(note.id)
        model.title = note.title
        model.text = note.text
        model.updated_at = note.updated_at
        await self._session.commit()

    async def delete(self, note_id: UUID) -> bool:
        model = await self._session.get(NoteModel, note_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
