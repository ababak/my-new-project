from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from domain.task import TaskStatus


class Unset(Enum):
    UNSET = "UNSET"


UNSET = Unset.UNSET


@dataclass(frozen=True, slots=True)
class CreateTaskInput:
    title: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateTaskInput:
    task_id: UUID
    title: str | Unset = UNSET
    description: str | None | Unset = UNSET


@dataclass(frozen=True, slots=True)
class ChangeTaskStatusInput:
    task_id: UUID
    status: TaskStatus


@dataclass(frozen=True, slots=True)
class ListTasksInput:
    status: TaskStatus | None = None
    limit: int = 50
    offset: int = 0
