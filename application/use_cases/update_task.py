from application.dto import UNSET, UpdateTaskInput
from application.ports import TaskRepository
from domain.exceptions import TaskNotFoundError
from domain.task import Task


class UpdateTask:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def execute(self, data: UpdateTaskInput) -> Task:
        task = await self._repo.get(data.task_id)
        if task is None:
            raise TaskNotFoundError(data.task_id)
        if data.title is not UNSET:
            task.change_title(data.title)
        if data.description is not UNSET:
            task.change_description(data.description)
        await self._repo.update(task)
        return task
