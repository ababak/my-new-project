from uuid import UUID

from application.ports import TaskRepository
from domain.exceptions import TaskNotFoundError


class DeleteTask:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def execute(self, task_id: UUID) -> None:
        if not await self._repo.delete(task_id):
            raise TaskNotFoundError(task_id)
