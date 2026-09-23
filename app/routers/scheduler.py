from fastapi import APIRouter, HTTPException
from app.services.scheduler_service import SchedulerService
from app.models import ScheduleResponse

router = APIRouter(prefix="/schedule", tags=["scheduler"])


@router.post("", response_model=ScheduleResponse)
async def schedule_today():
    try:
        return await SchedulerService().schedule_today()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
