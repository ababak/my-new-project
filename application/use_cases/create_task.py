from application.dto import CreateTaskInput
from application.ports import TaskRepository
from domain.task import Task


class CreateTask:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def execute(self, data: CreateTaskInput) -> Task:
        task = Task.create(data.title, data.description)
        await self._repo.add(task)
        return task
