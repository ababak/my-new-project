from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class Unset(Enum):
    UNSET = "UNSET"


UNSET = Unset.UNSET


@dataclass(frozen=True, slots=True)
class CreateNoteInput:
    title: str
    text: str


@dataclass(frozen=True, slots=True)
class UpdateNoteInput:
    note_id: UUID
    title: str | Unset = UNSET
    text: str | Unset = UNSET


@dataclass(frozen=True, slots=True)
class ListNotesInput:
    q: str | None = None
    limit: int = 50
    offset: int = 0
