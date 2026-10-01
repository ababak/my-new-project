from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from application.dto import UNSET, ChangeTaskStatusInput, CreateTaskInput, UpdateTaskInput
from domain.task import MAX_TITLE_LENGTH, Task, TaskStatus


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    description: str | None = None

    def to_input(self) -> CreateTaskInput:
        return CreateTaskInput(title=self.title, description=self.description)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=MAX_TITLE_LENGTH)
    description: str | None = None

    @model_validator(mode="after")
    def _title_not_null(self) -> Self:
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title cannot be null")
        return self

    def to_input(self, task_id: UUID) -> UpdateTaskInput:
        provided = self.model_fields_set
        return UpdateTaskInput(
            task_id=task_id,
            title=self.title if "title" in provided and self.title is not None else UNSET,
            description=self.description if "description" in provided else UNSET,
        )


class TaskStatusUpdate(BaseModel):
    status: TaskStatus

    def to_input(self, task_id: UUID) -> ChangeTaskStatusInput:
        return ChangeTaskStatusInput(task_id=task_id, status=self.status)


class ErrorResponse(BaseModel):
    detail: str


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, task: Task) -> Self:
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
