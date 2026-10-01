import pytest

from domain.note import MAX_TITLE_LENGTH, InvalidNoteError, Note


def test_create_strips_title_and_text() -> None:
    note = Note.create("  Title  ", "  body \n")

    assert note.title == "Title"
    assert note.text == "body"
    assert note.created_at == note.updated_at


def test_create_allows_empty_text() -> None:
    assert Note.create("a", "").text == ""
    assert Note.create("a", "   ").text == ""


@pytest.mark.parametrize("title", ["", "   ", "x" * (MAX_TITLE_LENGTH + 1)])
def test_create_rejects_invalid_title(title: str) -> None:
    with pytest.raises(InvalidNoteError):
        Note.create(title, "text")


def test_create_accepts_max_length_title() -> None:
    assert len(Note.create("x" * MAX_TITLE_LENGTH, "").title) == MAX_TITLE_LENGTH


def test_rename_validates_and_touches_updated_at() -> None:
    note = Note.create("a", "text")
    created = note.updated_at

    note.rename(" b ")

    assert note.title == "b"
    assert note.updated_at > created
    with pytest.raises(InvalidNoteError):
        note.rename("  ")
    assert note.title == "b"


def test_change_text_strips_and_touches_updated_at() -> None:
    note = Note.create("a", "text")
    created = note.updated_at

    note.change_text("  new  ")

    assert note.text == "new"
    assert note.updated_at > created
