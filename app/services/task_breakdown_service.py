from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.clients.ai_client import AIService
from app.clients.ticktick_client import TickTickClient
from app.config import settings
from app.models import CreatedTask, TaskBreakdownRequest, TaskBreakdownResponse


class TaskBreakdownService:
    def __init__(
        self,
        ticktick: TickTickClient | None = None,
        ai: AIService | None = None,
    ) -> None:
        self.ticktick = ticktick or TickTickClient()
        self.ai = ai or AIService()

    async def create_breakdown(
        self, request: TaskBreakdownRequest
    ) -> TaskBreakdownResponse:
        timezone = ZoneInfo(settings.default_timezone)
        today = datetime.now(timezone).date()
        proposed_tasks = self.ai.break_down_task(
            request.text, today.isoformat(), settings.default_timezone
        )
        booked: dict[date, list[tuple[datetime, datetime]]] = {}
        created: list[CreatedTask] = []

        for proposed in proposed_tasks:
            title = str(proposed.get("title", "")).strip()
            if not title:
                continue

            content = str(proposed.get("description", "")).strip()
            task_date = self._task_date(proposed.get("date"), today)
            duration = self._duration(proposed.get("duration_minutes"))
            start = self._find_available_start(
                task_date,
                proposed.get("preferred_time"),
                duration,
                booked,
                timezone,
            )
            end = start + timedelta(minutes=duration)
            booked.setdefault(task_date, []).append((start, end))
            start_date = self._format_datetime(start)
            due_date = self._format_datetime(end)
            task = await self.ticktick.create_task(
                {
                    "title": title,
                    "content": content,
                    "projectId": settings.ticktick_default_project_id,
                    "priority": int(proposed.get("priority", 0)),
                    "startDate": start_date,
                    "dueDate": due_date,
                    "timeZone": settings.default_timezone,
                    "isAllDay": False,
                }
            )
            created.append(
                CreatedTask(
                    id=task.get("id"),
                    title=task.get("title", title),
                    content=task.get("content", content),
                    projectId=task.get(
                        "projectId", settings.ticktick_default_project_id
                    ),
                    startDate=start_date,
                    dueDate=due_date,
                )
            )

        if not created:
            raise ValueError("AI did not return any valid tasks")

        return TaskBreakdownResponse(source_text=request.text, created=created)

    @staticmethod
    def _task_date(value: object, today: date) -> date:
        try:
            parsed = date.fromisoformat(str(value))
            return parsed
        except (TypeError, ValueError):
            return today

    @staticmethod
    def _duration(value: object) -> int:
        try:
            duration = int(value)
        except (TypeError, ValueError):
            duration = settings.min_task_duration_minutes
        return max(
            settings.min_task_duration_minutes,
            min(settings.max_task_duration_minutes, duration),
        )

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        return value.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S+0000")

    @staticmethod
    def _find_available_start(
        task_date: date,
        preferred_time: object,
        duration: int,
        booked: dict[date, list[tuple[datetime, datetime]]],
        timezone: ZoneInfo,
    ) -> datetime:
        try:
            requested = time.fromisoformat(str(preferred_time))
        except (TypeError, ValueError):
            requested = settings.working_start_time

        requested_start = datetime.combine(task_date, requested, tzinfo=timezone)
        day_start = datetime.combine(
            task_date, settings.working_start_time, tzinfo=timezone
        )
        day_end = datetime.combine(
            task_date, settings.working_end_time, tzinfo=timezone
        )
        requested_start = max(requested_start, day_start)

        intervals = sorted(booked.get(task_date, []))
        candidates = [requested_start]
        if requested_start != day_start:
            candidates.append(day_start)

        for candidate in candidates:
            start = candidate
            while start + timedelta(minutes=duration) <= day_end:
                conflict = next(
                    (
                        interval
                        for interval in intervals
                        if start < interval[1]
                        and start + timedelta(minutes=duration) > interval[0]
                    ),
                    None,
                )
                if conflict is None:
                    return start
                start = conflict[1] + timedelta(
                    minutes=settings.scheduling_buffer_minutes
                )

        raise ValueError(f"No available schedule time on {task_date.isoformat()}")
