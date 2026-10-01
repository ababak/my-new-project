from uuid import UUID

from application.ports import TaskRepository
from domain.exceptions import TaskNotFoundError
from domain.task import Task


class GetTask:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    async def execute(self, task_id: UUID) -> Task:
        task = await self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task
