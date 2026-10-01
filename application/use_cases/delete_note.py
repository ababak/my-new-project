from uuid import UUID

from application.note_ports import NoteRepository
from domain.note import NoteNotFoundError


class DeleteNote:
    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    async def execute(self, note_id: UUID) -> None:
        if not await self._repository.delete(note_id):
            raise NoteNotFoundError(note_id)
