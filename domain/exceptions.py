from uuid import UUID


class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidTaskError(DomainError):
    """Raised when a task would violate a domain invariant."""


class TaskNotFoundError(DomainError):
    def __init__(self, task_id: UUID) -> None:
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id
