from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.ports import TaskRepository
from application.use_cases.change_task_status import ChangeTaskStatus
from application.use_cases.create_task import CreateTask
from application.use_cases.delete_task import DeleteTask
from application.use_cases.get_task import GetTask
from application.use_cases.list_tasks import ListTasks
from application.use_cases.update_task import UpdateTask
from infrastructure.db.session import create_engine, create_session_factory
from infrastructure.db.task_repository import SqlAlchemyTaskRepository
from infrastructure.settings import get_settings


@lru_cache
def _session_factory() -> async_sessionmaker[AsyncSession]:
    return create_session_factory(create_engine(get_settings().database_url))


async def get_session() -> AsyncIterator[AsyncSession]:
    async with _session_factory()() as session:
        yield session


def get_task_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> TaskRepository:
    return SqlAlchemyTaskRepository(session)


_Repository = Annotated[TaskRepository, Depends(get_task_repository)]


def get_create_task(repository: _Repository) -> CreateTask:
    return CreateTask(repository)


def get_get_task(repository: _Repository) -> GetTask:
    return GetTask(repository)


def get_list_tasks(repository: _Repository) -> ListTasks:
    return ListTasks(repository)


def get_update_task(repository: _Repository) -> UpdateTask:
    return UpdateTask(repository)


def get_change_task_status(repository: _Repository) -> ChangeTaskStatus:
    return ChangeTaskStatus(repository)


def get_delete_task(repository: _Repository) -> DeleteTask:
    return DeleteTask(repository)
