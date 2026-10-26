from application.dto import ChangeTaskStatusInput
from application.ports import TaskRepository
from domain.exceptions import TaskNotFoundError
from domain.task import Task


class ChangeTaskStatus:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def execute(self, data: ChangeTaskStatusInput) -> Task:
        task = await self._repo.get(data.task_id)
        if task is None:
            raise TaskNotFoundError(data.task_id)
        task.change_status(data.status)
        await self._repo.update(task)
        return task
