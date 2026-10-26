from application.dto import ChangeTaskStatusInput
from application.ports import TaskRepository
from application.use_cases._lookup import get_task_or_raise
from domain.task import Task


class ChangeTaskStatus:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def execute(self, data: ChangeTaskStatusInput) -> Task:
        task = await get_task_or_raise(self._repo, data.task_id)
        task.change_status(data.status)
        await self._repo.update(task)
        return task
