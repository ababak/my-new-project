from uuid import UUID

from application.ports import TaskRepository
from application.use_cases._lookup import get_task_or_raise
from domain.task import Task


class GetTask:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def execute(self, task_id: UUID) -> Task:
        return await get_task_or_raise(self._repo, task_id)
