from datetime import datetime

from pydantic import BaseModel, Field


class TaskBreakdownRequest(BaseModel):
    text: str = Field(min_length=1)


class CreatedTask(BaseModel):
    id: str | None = None
    title: str
    content: str = ""
    projectId: str
    startDate: str
    dueDate: str


class TaskBreakdownResponse(BaseModel):
    source_text: str
    created: list[CreatedTask]


class ScheduledTask(BaseModel):
    task_id: str
    title: str
    start: datetime
    end: datetime
    difficulty: int | None = None


class ScheduleResponse(BaseModel):
    scheduled: list[ScheduledTask]
    unscheduled: list[str]
    fixed_appointments: int
