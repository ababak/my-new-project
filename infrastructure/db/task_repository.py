from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import TaskNotFoundError
from domain.task import Task, TaskStatus
from infrastructure.db.models import TaskModel


def _to_entity(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        title=model.title,
        description=model.description,
        status=TaskStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, task: Task) -> None:
        self._session.add(
            TaskModel(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status.value,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
        )
        await self._session.commit()

    async def get(self, task_id: UUID) -> Task | None:
        model = await self._session.get(TaskModel, task_id)
        return _to_entity(model) if model else None

    async def list_tasks(self, *, status: TaskStatus | None, limit: int, offset: int) -> list[Task]:
        stmt = select(TaskModel).order_by(TaskModel.created_at, TaskModel.id)
        if status is not None:
            stmt = stmt.where(TaskModel.status == status.value)
        result = await self._session.scalars(stmt.limit(limit).offset(offset))
        return [_to_entity(m) for m in result]

    async def update(self, task: Task) -> None:
        model = await self._session.get(TaskModel, task.id)
        if model is None:
            raise TaskNotFoundError(task.id)
        model.title = task.title
        model.description = task.description
        model.status = task.status.value
        model.updated_at = task.updated_at
        await self._session.commit()

    async def delete(self, task_id: UUID) -> bool:
        model = await self._session.get(TaskModel, task_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
