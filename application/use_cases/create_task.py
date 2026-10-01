from application.dto import CreateTaskInput
from application.ports import TaskRepository
from domain.task import Task


class CreateTask:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    async def execute(self, data: CreateTaskInput) -> Task:
        task = Task.create(title=data.title, description=data.description)
        await self._repository.add(task)
        return task
