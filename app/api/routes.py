from typing import Any

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, ConfigDict

from app.integration.ticktick import TickTickClient
from app.services.task_service import TaskService


class TaskPayload(BaseModel):
	model_config = ConfigDict(extra="allow")


class DueDatePayload(BaseModel):
	due_date: str | None = None


def get_task_service(request: Request) -> TaskService:
	return request.app.state.task_service


router = APIRouter(prefix="/api")


@router.get("/projects")
async def get_projects(service: TaskService = Depends(get_task_service)) -> Any:
	return await service.get_projects()


@router.get("/projects/{project_id}")
async def get_project(
	project_id: str,
	service: TaskService = Depends(get_task_service),
) -> Any:
	return await service.get_project(project_id)


@router.get("/projects/{project_id}/data")
async def get_project_data(
	project_id: str,
	service: TaskService = Depends(get_task_service),
) -> Any:
	return await service.get_project_data(project_id)


@router.get("/tasks/{task_id}")
async def get_task(
	task_id: str,
	service: TaskService = Depends(get_task_service),
) -> Any:
	return await service.get_task(task_id)


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
	task: TaskPayload,
	service: TaskService = Depends(get_task_service),
) -> Any:
	return await service.create_task(task.model_dump(exclude_unset=True))


@router.patch("/tasks/{task_id}")
async def update_task(
	task_id: str,
	task: TaskPayload,
	service: TaskService = Depends(get_task_service),
) -> Any:
	return await service.update_task(task_id, task.model_dump(exclude_unset=True))


@router.patch("/tasks/{task_id}/due-date")
async def update_task_due_date(
	task_id: str,
	payload: DueDatePayload,
	service: TaskService = Depends(get_task_service),
) -> Any:
	return await service.update_task_due_date(task_id, payload.due_date)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
	task_id: str,
	service: TaskService = Depends(get_task_service),
) -> None:
	await service.delete_task(task_id)
