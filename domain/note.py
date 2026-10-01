from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self
from uuid import UUID, uuid4

MAX_TITLE_LENGTH = 1024


class NoteNotFoundError(Exception):
    def __init__(self, note_id: UUID) -> None:
        super().__init__(f"Note {note_id} not found")
        self.note_id = note_id


class InvalidNoteError(Exception):
    pass


def _clean_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned or len(cleaned) > MAX_TITLE_LENGTH:
        raise InvalidNoteError(f"Title must be 1-{MAX_TITLE_LENGTH} characters")
    return cleaned


@dataclass
class Note:
    id: UUID
    title: str
    text: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, title: str, text: str) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            title=_clean_title(title),
            text=text.strip(),
            created_at=now,
            updated_at=now,
        )

    def rename(self, title: str) -> None:
        self.title = _clean_title(title)
        self._touch()

    def change_text(self, text: str) -> None:
        self.text = text.strip()
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(UTC)
