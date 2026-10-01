from uuid import UUID

from application.ports import TaskRepository
from domain.exceptions import TaskNotFoundError


class DeleteTask:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    async def execute(self, task_id: UUID) -> None:
        if not await self._repository.delete(task_id):
            raise TaskNotFoundError(task_id)
