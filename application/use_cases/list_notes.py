from application.note_dto import ListNotesInput
from application.note_ports import NoteRepository
from domain.note import Note


class ListNotes:
    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    async def execute(self, data: ListNotesInput) -> list[Note]:
        return await self._repository.list_notes(q=data.q, limit=data.limit, offset=data.offset)
