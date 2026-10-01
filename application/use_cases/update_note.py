from application.note_dto import UNSET, UpdateNoteInput
from application.note_ports import NoteRepository
from domain.note import Note, NoteNotFoundError


class UpdateNote:
    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    async def execute(self, data: UpdateNoteInput) -> Note:
        note = await self._repository.get(data.note_id)
        if note is None:
            raise NoteNotFoundError(data.note_id)
        if data.title is UNSET and data.text is UNSET:
            return note
        if data.title is not UNSET:
            note.rename(data.title)
        if data.text is not UNSET:
            note.change_text(data.text)
        await self._repository.update(note)
        return note
