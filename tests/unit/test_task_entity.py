import pytest

from domain.exceptions import InvalidTaskError
from domain.task import MAX_TITLE_LENGTH, Task, TaskStatus


def test_create_defaults_to_todo_and_strips_title() -> None:
    task = Task.create("  Write tests  ")

    assert task.title == "Write tests"
    assert task.status is TaskStatus.TODO
    assert task.description is None
    assert task.created_at == task.updated_at


@pytest.mark.parametrize("title", ["", "   ", "x" * (MAX_TITLE_LENGTH + 1)])
def test_create_rejects_invalid_title(title: str) -> None:
    with pytest.raises(InvalidTaskError):
        Task.create(title)


def test_mutations_touch_updated_at() -> None:
    task = Task.create("a")
    created = task.updated_at

    task.change_status(TaskStatus.DONE)

    assert task.status is TaskStatus.DONE
    assert task.updated_at > created
