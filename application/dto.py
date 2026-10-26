from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from domain.task import TaskStatus


class _Unset(Enum):
    UNSET = "unset"


# distinguishes "field not provided" from an explicit None (e.g. clearing a description)
UNSET = _Unset.UNSET


@dataclass(frozen=True)
class CreateTaskInput:
    title: str
    description: str | None = None


@dataclass(frozen=True)
class ListTasksInput:
    status: TaskStatus | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class UpdateTaskInput:
    task_id: UUID
    title: str | _Unset = UNSET
    description: str | None | _Unset = UNSET


@dataclass(frozen=True)
class ChangeTaskStatusInput:
    task_id: UUID
    status: TaskStatus
