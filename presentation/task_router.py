from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from application.dto import ListTasksInput
from application.use_cases.change_task_status import ChangeTaskStatus
from application.use_cases.create_task import CreateTask
from application.use_cases.delete_task import DeleteTask
from application.use_cases.get_task import GetTask
from application.use_cases.list_tasks import ListTasks
from application.use_cases.update_task import UpdateTask
from domain.task import TaskStatus
from presentation.dependencies import (
    get_change_task_status,
    get_create_task,
    get_delete_task,
    get_get_task,
    get_list_tasks,
    get_update_task,
)
from presentation.task_schemas import (
    ErrorResponse,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Task not found"}
}


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
async def create_task(
    body: TaskCreate, use_case: Annotated[CreateTask, Depends(get_create_task)]
) -> TaskResponse:
    return TaskResponse.from_entity(await use_case.execute(body.to_input()))


@router.get("", response_model=list[TaskResponse], summary="List tasks")
async def list_tasks(
    use_case: Annotated[ListTasks, Depends(get_list_tasks)],
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[TaskResponse]:
    tasks = await use_case.execute(ListTasksInput(status=task_status, limit=limit, offset=offset))
    return [TaskResponse.from_entity(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse, summary="Get a task", responses=NOT_FOUND)
async def get_task(
    task_id: UUID, use_case: Annotated[GetTask, Depends(get_get_task)]
) -> TaskResponse:
    return TaskResponse.from_entity(await use_case.execute(task_id))


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update title and/or description",
    responses=NOT_FOUND,
)
async def update_task(
    task_id: UUID, body: TaskUpdate, use_case: Annotated[UpdateTask, Depends(get_update_task)]
) -> TaskResponse:
    return TaskResponse.from_entity(await use_case.execute(body.to_input(task_id)))


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Change task status",
    responses=NOT_FOUND,
)
async def change_task_status(
    task_id: UUID,
    body: TaskStatusUpdate,
    use_case: Annotated[ChangeTaskStatus, Depends(get_change_task_status)],
) -> TaskResponse:
    return TaskResponse.from_entity(await use_case.execute(body.to_input(task_id)))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    responses=NOT_FOUND,
)
async def delete_task(
    task_id: UUID, use_case: Annotated[DeleteTask, Depends(get_delete_task)]
) -> Response:
    await use_case.execute(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
