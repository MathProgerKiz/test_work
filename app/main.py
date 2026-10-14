from typing import Any

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.core.db import get_session
from app.tasks import add


app = FastAPI(title="Test Work API")


class AddTaskRequest(BaseModel):
    first_number: int
    second_number: int


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "FastAPI is running"}


@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from error

    return {"status": "ok", "database": "ok"}


@app.post("/tasks/add", status_code=status.HTTP_202_ACCEPTED)
def enqueue_add_task(payload: AddTaskRequest) -> dict[str, str]:
    task = add.delay(payload.first_number, payload.second_number)
    return {"task_id": task.id, "status": task.status}


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, Any]:
    task = AsyncResult(task_id, app=celery_app)
    response: dict[str, Any] = {"task_id": task_id, "status": task.status}

    if task.successful():
        response["result"] = task.result
    elif task.failed():
        response["error"] = str(task.result)

    return response
