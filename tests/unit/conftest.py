from uuid import UUID

import pytest

from domain.task import Task, TaskStatus


class FakeTaskRepository:
    def __init__(self) -> None:
        self.tasks: dict[UUID, Task] = {}

    async def add(self, task: Task) -> None:
        self.tasks[task.id] = task

    async def get(self, task_id: UUID) -> Task | None:
        return self.tasks.get(task_id)

    async def list_tasks(self, *, status: TaskStatus | None, limit: int, offset: int) -> list[Task]:
        items = sorted(self.tasks.values(), key=lambda t: t.created_at)
        if status is not None:
            items = [t for t in items if t.status is status]
        return items[offset : offset + limit]

    async def update(self, task: Task) -> None:
        self.tasks[task.id] = task

    async def delete(self, task_id: UUID) -> bool:
        return self.tasks.pop(task_id, None) is not None


@pytest.fixture
def repo() -> FakeTaskRepository:
    return FakeTaskRepository()
