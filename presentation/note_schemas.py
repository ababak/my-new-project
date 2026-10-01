from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from application.note_dto import UNSET, CreateNoteInput, UpdateNoteInput
from domain.note import MAX_TITLE_LENGTH, Note


class NoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    text: str

    def to_input(self) -> CreateNoteInput:
        return CreateNoteInput(title=self.title, text=self.text)


class NoteUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=MAX_TITLE_LENGTH)
    text: str | None = None

    @model_validator(mode="after")
    def _fields_not_null(self) -> Self:
        for name in ("title", "text"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self

    def to_input(self, note_id: UUID) -> UpdateNoteInput:
        return UpdateNoteInput(
            note_id=note_id,
            title=self.title if self.title is not None else UNSET,
            text=self.text if self.text is not None else UNSET,
        )


class ErrorResponse(BaseModel):
    detail: str


class NoteResponse(BaseModel):
    id: UUID
    title: str
    text: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, note: Note) -> Self:
        return cls(
            id=note.id,
            title=note.title,
            text=note.text,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
