from application.dto import ListTasksInput
from application.ports import TaskRepository
from domain.task import Task


class ListTasks:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def execute(self, data: ListTasksInput) -> list[Task]:
        return await self._repo.list_tasks(status=data.status, limit=data.limit, offset=data.offset)
