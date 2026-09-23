from fastapi import APIRouter, HTTPException

from app.models import TaskBreakdownRequest, TaskBreakdownResponse
from app.services.task_breakdown_service import TaskBreakdownService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/breakdown", response_model=TaskBreakdownResponse)
async def create_task_breakdown(
    request: TaskBreakdownRequest,
) -> TaskBreakdownResponse:
    try:
        return await TaskBreakdownService().create_breakdown(request)
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
