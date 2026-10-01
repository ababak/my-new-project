from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from application.note_dto import ListNotesInput
from application.use_cases.create_note import CreateNote
from application.use_cases.delete_note import DeleteNote
from application.use_cases.get_note import GetNote
from application.use_cases.list_notes import ListNotes
from application.use_cases.update_note import UpdateNote
from presentation.dependencies import (
    get_create_note,
    get_delete_note,
    get_get_note,
    get_list_notes,
    get_update_note,
)
from presentation.note_schemas import ErrorResponse, NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Note not found"}
}


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
)
async def create_note(
    body: NoteCreate, use_case: Annotated[CreateNote, Depends(get_create_note)]
) -> NoteResponse:
    return NoteResponse.from_entity(await use_case.execute(body.to_input()))


@router.get("", response_model=list[NoteResponse], summary="List and search notes")
async def list_notes(
    use_case: Annotated[ListNotes, Depends(get_list_notes)],
    q: Annotated[
        str | None,
        Query(description="Case-insensitive substring match in title or text; empty = no filter"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[NoteResponse]:
    notes = await use_case.execute(ListNotesInput(q=q, limit=limit, offset=offset))
    return [NoteResponse.from_entity(n) for n in notes]


@router.get("/{note_id}", response_model=NoteResponse, summary="Get a note", responses=NOT_FOUND)
async def get_note(
    note_id: UUID, use_case: Annotated[GetNote, Depends(get_get_note)]
) -> NoteResponse:
    return NoteResponse.from_entity(await use_case.execute(note_id))


@router.patch(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update title and/or text; omitted fields stay unchanged",
    responses=NOT_FOUND,
)
async def update_note(
    note_id: UUID, body: NoteUpdate, use_case: Annotated[UpdateNote, Depends(get_update_note)]
) -> NoteResponse:
    return NoteResponse.from_entity(await use_case.execute(body.to_input(note_id)))


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    responses=NOT_FOUND,
)
async def delete_note(
    note_id: UUID, use_case: Annotated[DeleteNote, Depends(get_delete_note)]
) -> Response:
    await use_case.execute(note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
