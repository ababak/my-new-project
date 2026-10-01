from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid4

from domain.exceptions import InvalidTaskError

MAX_TITLE_LENGTH = 200


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def _clean_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned or len(cleaned) > MAX_TITLE_LENGTH:
        raise InvalidTaskError(f"Title must be 1-{MAX_TITLE_LENGTH} characters")
    return cleaned


@dataclass
class Task:
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, title: str, description: str | None = None) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            title=_clean_title(title),
            description=description,
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )

    def rename(self, title: str) -> None:
        self.title = _clean_title(title)
        self._touch()

    def change_description(self, description: str | None) -> None:
        self.description = description
        self._touch()

    def change_status(self, status: TaskStatus) -> None:
        self.status = status
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(UTC)
