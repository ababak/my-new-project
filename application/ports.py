from typing import Protocol
from uuid import UUID

from domain.task import Task, TaskStatus


class TaskRepository(Protocol):
    async def add(self, task: Task) -> None: ...

    async def get(self, task_id: UUID) -> Task | None: ...

    async def list_tasks(
        self, *, status: TaskStatus | None, limit: int, offset: int
    ) -> list[Task]: ...

    async def update(self, task: Task) -> None: ...

    async def delete(self, task_id: UUID) -> bool: ...
