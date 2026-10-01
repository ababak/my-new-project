from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.note import InvalidNoteError, NoteNotFoundError
from presentation.note_router import router as note_router

app = FastAPI(title="Task Management API")
app.include_router(note_router)


@app.exception_handler(NoteNotFoundError)
async def note_not_found_handler(_: Request, exc: NoteNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidNoteError)
async def invalid_note_handler(_: Request, exc: InvalidNoteError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
