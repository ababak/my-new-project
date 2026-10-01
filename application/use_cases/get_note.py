from uuid import UUID

from application.note_ports import NoteRepository
from domain.note import Note, NoteNotFoundError


class GetNote:
    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    async def execute(self, note_id: UUID) -> Note:
        note = await self._repository.get(note_id)
        if note is None:
            raise NoteNotFoundError(note_id)
        return note
