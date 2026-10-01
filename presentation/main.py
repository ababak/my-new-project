from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.exceptions import InvalidTaskError, TaskNotFoundError
from presentation.task_router import router as task_router

app = FastAPI(title="Task Management API")
app.include_router(task_router)


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(_: Request, exc: TaskNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidTaskError)
async def invalid_task_handler(_: Request, exc: InvalidTaskError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
