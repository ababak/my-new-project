from uuid import uuid4

import pytest

from application.dto import (
    UNSET,
    ChangeTaskStatusInput,
    CreateTaskInput,
    ListTasksInput,
    UpdateTaskInput,
)
from application.use_cases.change_task_status import ChangeTaskStatus
from application.use_cases.create_task import CreateTask
from application.use_cases.delete_task import DeleteTask
from application.use_cases.get_task import GetTask
from application.use_cases.list_tasks import ListTasks
from application.use_cases.update_task import UpdateTask
from domain.exceptions import TaskNotFoundError
from domain.task import TaskStatus

from .conftest import FakeTaskRepository


async def test_create_and_get(repo: FakeTaskRepository) -> None:
    created = await CreateTask(repo).execute(CreateTaskInput(title="a", description="d"))

    assert await GetTask(repo).execute(created.id) == created


async def test_get_missing_raises(repo: FakeTaskRepository) -> None:
    with pytest.raises(TaskNotFoundError):
        await GetTask(repo).execute(uuid4())


async def test_list_filters_and_paginates(repo: FakeTaskRepository) -> None:
    create = CreateTask(repo)
    first = await create.execute(CreateTaskInput(title="1"))
    await create.execute(CreateTaskInput(title="2"))
    await ChangeTaskStatus(repo).execute(ChangeTaskStatusInput(first.id, TaskStatus.DONE))

    done = await ListTasks(repo).execute(ListTasksInput(status=TaskStatus.DONE))
    page = await ListTasks(repo).execute(ListTasksInput(limit=1, offset=1))

    assert [t.id for t in done] == [first.id]
    assert len(page) == 1


async def test_update_changes_only_provided_fields(repo: FakeTaskRepository) -> None:
    task = await CreateTask(repo).execute(CreateTaskInput(title="old", description="keep"))

    updated = await UpdateTask(repo).execute(UpdateTaskInput(task_id=task.id, title="new"))

    assert (updated.title, updated.description) == ("new", "keep")


async def test_update_can_clear_description(repo: FakeTaskRepository) -> None:
    task = await CreateTask(repo).execute(CreateTaskInput(title="t", description="d"))

    updated = await UpdateTask(repo).execute(
        UpdateTaskInput(task_id=task.id, title=UNSET, description=None)
    )

    assert updated.description is None
    assert updated.title == "t"


async def test_update_and_status_missing_raise(repo: FakeTaskRepository) -> None:
    with pytest.raises(TaskNotFoundError):
        await UpdateTask(repo).execute(UpdateTaskInput(task_id=uuid4(), title="x"))
    with pytest.raises(TaskNotFoundError):
        await ChangeTaskStatus(repo).execute(ChangeTaskStatusInput(uuid4(), TaskStatus.DONE))


async def test_delete(repo: FakeTaskRepository) -> None:
    task = await CreateTask(repo).execute(CreateTaskInput(title="t"))

    await DeleteTask(repo).execute(task.id)

    with pytest.raises(TaskNotFoundError):
        await DeleteTask(repo).execute(task.id)
