from uuid import UUID

from application.ports import TaskRepository
from domain.exceptions import TaskNotFoundError
from domain.task import Task


async def get_task_or_raise(repo: TaskRepository, task_id: UUID) -> Task:
    task = await repo.get(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return task
