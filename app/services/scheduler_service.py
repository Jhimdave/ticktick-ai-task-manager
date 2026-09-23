import logging

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.clients.ai_client import AIService
from app.clients.ticktick_client import TickTickClient
from app.config import settings
from app.models import ScheduledTask, ScheduleResponse

logger = logging.getLogger("scheduler")


def format_ticktick_datetime(value: datetime) -> str:
    return value.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S+0000")


def parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def compute_free_blocks(day_start: datetime, day_end: datetime, busy: list[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    busy = sorted(busy)
    free = []
    cursor = day_start

    for b_start, b_end in busy:
        if b_end <= cursor:
            continue

        if b_start > cursor:
            free.append((cursor, min(b_start, day_end)))

        cursor = max(cursor, b_end)

        if cursor >= day_end:
            break

    if cursor < day_end:
        free.append((cursor, day_end))

    return [block for block in free if block[1] > block[0]]


def place_tasks(free_blocks: list[tuple[datetime, datetime]], tasks: list[dict], buffer_minutes: int) -> tuple[list[ScheduledTask], list[str]]:
    blocks = list(free_blocks)
    scheduled = []
    unscheduled = []

    for task in tasks:
        duration = timedelta(minutes=task["duration_minutes"])
        placed = False

        for i, (block_start, block_end) in enumerate(blocks):
            if block_end - block_start < duration:
                continue

            end = block_start + duration

            scheduled.append(
                ScheduledTask(task_id=task["id"], title=task["title"], start=block_start, end=end, difficulty=task.get("difficulty"))
            )

            new_start = end + timedelta(minutes=buffer_minutes)
            blocks[i] = (new_start, block_end) if new_start < block_end else (block_end, block_end)

            placed = True
            break

        if not placed:
            unscheduled.append(task["id"])

    return scheduled, unscheduled


class SchedulerService:
    """Milestone 2: schedule overdue and today's tasks from the current time forward."""

    def __init__(self, ticktick: TickTickClient | None = None, ai: AIService | None = None):
        self.ticktick = ticktick or TickTickClient()
        self.ai = ai or AIService()

    async def schedule_today(self) -> ScheduleResponse:
        tz = ZoneInfo(settings.default_timezone)
        now = datetime.now(tz)
        today = now.date()

        projects = await self.ticktick.get_projects()
        project_ids = [p["id"] for p in projects]
        name_by_id = {p["id"]: p["name"] for p in projects}

        all_tasks = await self.ticktick.get_all_tasks(project_ids)

        candidates = []
        fixed_tasks = []

        for task in all_tasks:
            if task.get("status") == 2:
                continue

            start = parse_dt(task.get("startDate"))
            due = parse_dt(task.get("dueDate"))
            ref = start or due

            if not ref:
                continue

            task_date = ref.astimezone(tz).date()

            project_name = name_by_id.get(task.get("projectId"), "")

            if project_name in settings.protected_project_list:
                fixed_tasks.append(task)
                continue

            if task_date <= today:
                candidates.append(task)

        estimated = []

        for task in candidates:
            has_description = bool((task.get("content") or "").strip())
            estimate = {}

            try:
                estimate = self.ai.estimate_duration(
                    task.get("title", ""),
                    task.get("content", ""),
                    task.get("priority", 0),
                    settings.min_task_duration_minutes,
                    settings.max_task_duration_minutes,
                    enhance_content=not has_description
                )

                duration = max(
                    settings.min_task_duration_minutes,
                    min(settings.max_task_duration_minutes, int(estimate.get("duration_minutes", settings.min_task_duration_minutes)))
                )

                difficulty = int(estimate.get("difficulty", 3))

            except Exception:
                logger.exception("estimation failed for %s", task["id"])
                duration = settings.min_task_duration_minutes
                difficulty = 3

            estimated.append(
                {
                    "id": task["id"],
                    "title": task.get("title", ""),
                    "priority": task.get("priority", 0),
                    "duration_minutes": duration,
                    "difficulty": difficulty,
                    "due": parse_dt(task.get("dueDate")),
                    "has_description": has_description,
                    "enhanced_title": estimate.get("enhanced_title"),
                    "description": estimate.get("description")
                }
            )

        far_future = now + timedelta(days=365)

        estimated.sort(
            key=lambda task: (
                0 if task["due"] and task["due"].astimezone(tz).date() < today else 1,
                task["due"] or far_future,
                -task["priority"],
                task["difficulty"]
            )
        )

        scheduled = []
        unscheduled_ids = []

        remaining_tasks = estimated

        for day_offset in range(7):
            if not remaining_tasks:
                break

            schedule_date = today + timedelta(days=day_offset)

            day_start = datetime.combine(schedule_date, settings.working_start_time, tzinfo=tz)
            day_end = datetime.combine(schedule_date, settings.working_end_time, tzinfo=tz)

            if schedule_date == today:
                day_start = max(day_start, now)

            if day_start >= day_end:
                continue

            busy = []

            for task in fixed_tasks:
                start = parse_dt(task.get("startDate"))
                due = parse_dt(task.get("dueDate"))

                if not start and not due:
                    continue

                reference = start or due

                if reference.astimezone(tz).date() != schedule_date:
                    continue

                busy_start = (start or reference).astimezone(tz)
                busy_end = (due or (busy_start + timedelta(minutes=30))).astimezone(tz)

                busy.append((busy_start, busy_end))

            free_blocks = compute_free_blocks(day_start, day_end, busy)

            day_scheduled, day_unscheduled = place_tasks(
                free_blocks,
                remaining_tasks,
                settings.scheduling_buffer_minutes
            )

            scheduled.extend(day_scheduled)

            scheduled_ids = {task.task_id for task in day_scheduled}

            remaining_tasks = [
                task for task in remaining_tasks
                if task["id"] not in scheduled_ids
            ]

        unscheduled_ids = [task["id"] for task in remaining_tasks]

        by_id = {task["id"]: task for task in candidates}
        estimated_by_id = {task["id"]: task for task in estimated}

        for scheduled_task in scheduled:
            task = by_id[scheduled_task.task_id]
            estimate = estimated_by_id[scheduled_task.task_id]

            start_date = format_ticktick_datetime(scheduled_task.start)
            due_date = format_ticktick_datetime(scheduled_task.end)

            update_fields = {
                "startDate": start_date,
                "dueDate": due_date
            }

            if not (task.get("content") or "").strip():
                enhanced_title = estimate.get("enhanced_title") or task.get("title", "")
                description = estimate.get("description") or task.get("content", "")

                update_fields.update(
                    {
                        "title": enhanced_title,
                        "content": description
                    }
                )

            try:
                await self.ticktick.update_task(task["id"], **update_fields)

                logger.info(
                    "scheduled task %s: %s -> %s",
                    scheduled_task.task_id,
                    start_date,
                    due_date
                )

            except Exception:
                logger.exception("failed updating schedule for %s", scheduled_task.task_id)

        return ScheduleResponse(
            scheduled=scheduled,
            unscheduled=unscheduled_ids,
            fixed_appointments=sum(
                1
                for task in fixed_tasks
                if (
                    (parse_dt(task.get("startDate")) or parse_dt(task.get("dueDate")))
                    and (parse_dt(task.get("startDate")) or parse_dt(task.get("dueDate"))).astimezone(tz).date() >= today
                )
            )
        )