from uuid import UUID


class DomainError(Exception):
    pass


class InvalidTaskError(DomainError):
    pass


class TaskNotFoundError(DomainError):
    def __init__(self, task_id: UUID) -> None:
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id
