from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from domain.exceptions import InvalidTaskError

MAX_TITLE_LENGTH = 200


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def _validate_title(title: str) -> str:
    title = title.strip()
    if not title or len(title) > MAX_TITLE_LENGTH:
        raise InvalidTaskError(f"Title must be 1..{MAX_TITLE_LENGTH} characters after stripping")
    return title


@dataclass
class Task:
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, title: str, description: str | None = None) -> "Task":
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            title=_validate_title(title),
            description=description,
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )

    def change_title(self, title: str) -> None:
        self.title = _validate_title(title)
        self._touch()

    def change_description(self, description: str | None) -> None:
        self.description = description
        self._touch()

    def change_status(self, status: TaskStatus) -> None:
        self.status = status
        self._touch()

    def _touch(self) -> None:
        # strictly increasing even if the clock does not tick between two mutations
        self.updated_at = max(datetime.now(UTC), self.updated_at + timedelta(microseconds=1))
