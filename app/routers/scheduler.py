from fastapi import APIRouter, HTTPException
from app.services.scheduler_service import ScheduleUpdateError, SchedulerService
from app.models import ScheduleResponse

router = APIRouter(prefix="/schedule", tags=["scheduler"])


@router.post("", response_model=ScheduleResponse)
async def schedule_today():
    try:
        return await SchedulerService().schedule_today()
    except ScheduleUpdateError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(e),
                "failed_task_ids": e.failed_task_ids,
            },
        ) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
