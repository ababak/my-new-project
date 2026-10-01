from application.dto import Unset, UpdateTaskInput
from application.ports import TaskRepository
from domain.exceptions import TaskNotFoundError
from domain.task import Task


class UpdateTask:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    async def execute(self, data: UpdateTaskInput) -> Task:
        task = await self._repository.get(data.task_id)
        if task is None:
            raise TaskNotFoundError(data.task_id)
        if not isinstance(data.title, Unset):
            task.rename(data.title)
        if not isinstance(data.description, Unset):
            task.change_description(data.description)
        await self._repository.update(task)
        return task
