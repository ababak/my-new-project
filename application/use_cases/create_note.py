from application.note_dto import CreateNoteInput
from application.note_ports import NoteRepository
from domain.note import Note


class CreateNote:
    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    async def execute(self, data: CreateNoteInput) -> Note:
        note = Note.create(title=data.title, text=data.text)
        await self._repository.add(note)
        return note
