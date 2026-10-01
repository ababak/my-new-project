from uuid import UUID

from domain.note import Note


class FakeNoteRepository:
    def __init__(self) -> None:
        self.notes: dict[UUID, Note] = {}
        self.update_calls = 0

    async def add(self, note: Note) -> None:
        self.notes[note.id] = note

    async def get(self, note_id: UUID) -> Note | None:
        return self.notes.get(note_id)

    async def list_notes(self, *, q: str | None, limit: int, offset: int) -> list[Note]:
        items = sorted(self.notes.values(), key=lambda n: (n.created_at, n.id))
        if q:
            needle = q.casefold()
            items = [
                n for n in items if needle in n.title.casefold() or needle in n.text.casefold()
            ]
        return items[offset : offset + limit]

    async def update(self, note: Note) -> None:
        self.update_calls += 1
        self.notes[note.id] = note

    async def delete(self, note_id: UUID) -> bool:
        return self.notes.pop(note_id, None) is not None
