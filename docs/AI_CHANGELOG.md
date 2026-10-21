
# AI Change Log

This file records meaningful AI-assisted code changes. The newest entry belongs at the top.

## 2026-10-21 — Lock the TickTick Appointments project

**Summary:** Exclude the user's `🤝Appointments` project from schedule updates by protecting its TickTick project ID.

**Files changed:**
- `app/config.py` — Add project ID `6a36da68cf4b116ed0a4150a` to protected project IDs so the scheduler leaves its task dates and times untouched, including overdue tasks and tasks outside working hours.
- `docs/AI_CHANGELOG.md` — Record the project-specific protection and regression validation.

**Tests:** Focused runtime check verified the project ID is protected and a task with an overdue, outside-working-hours schedule is not sent to TickTick for update; `python -m compileall -q app scripts`; `git diff --check`.

**Risks or follow-up:** Protection is tied to this TickTick project ID. If the project is deleted and recreated, its new ID must also be protected.

## 2026-10-21 — Preserve appointment project task dates

**Summary:** Prevent tasks returned by a protected TickTick project from becoming rescheduling candidates when the API omits or returns an inconsistent `projectId`.

**Files changed:**
- `app/clients/ticktick_client.py` — Set each task's `projectId` from the project-data endpoint that returned it, ensuring the scheduler can reliably recognize protected projects such as Appointments.
- `docs/AI_CHANGELOG.md` — Record the root cause and validation.

**Tests:** Focused runtime regression check covered tasks with missing, `null`, empty, and mismatched `projectId` values; `python -m compileall -q app scripts`; `git diff --check`.

**Risks or follow-up:** This treats the project endpoint as authoritative for a task's project association, which is needed to preserve protected-project behavior during scheduling.

## 2026-10-21 — Surface TickTick schedule update failures

**Summary:** Include each task's project ID when writing its scheduled dates to TickTick, and return HTTP 502 from `POST /schedule` when any task update fails.

**Files changed:**
- `app/services/scheduler_service.py` — Pass the task's `projectId` to TickTick, collect failed task IDs while continuing other updates, and raise `ScheduleUpdateError` after all scheduled tasks have been attempted.
- `app/routers/scheduler.py` — Convert `ScheduleUpdateError` into HTTP 502 with a message and the failed task IDs.
- `docs/AI_CHANGELOG.md` — Record this fix and its validation.

**Tests:** `.venv\Scripts\python.exe -m compileall -q app scripts`; focused Pylance runtime check verified project ID forwarding, successful scheduling, and HTTP 502 failure reporting.

**Risks or follow-up:** Some tasks may already be updated before a partial failure returns 502. The response identifies failed task IDs; retrying `/schedule` may schedule and update tasks again.

## 2026-10-21 — Scheduler priority and prompt tightening

**Summary:** Adjusted schedule ordering to prioritize short/easy tasks before work tasks and long personal automation tasks, while preserving fixed appointment slots and reserving short break gaps without creating explicit break tasks. Reduced AI prompt length to keep task generation more stable on long user inputs.

**Files changed:**
- `app/services/scheduler_service.py` — Added scheduling category sorting for easy → work → personal automation, and inserted short automatic break gaps between batches of tasks instead of creating a visible break task.
- `app/clients/ai_client.py` — Shortened the task-breakdown prompt to keep it concise and less likely to hallucinate on longer inputs while preserving project/date constraints.
- `docs/AI_CHANGELOG.md` — Added the change log entry documenting the behavioral shift and validation notes.

**Behavioral impact:** The scheduler now prefers lower-effort tasks earlier in the day, keeps protected appointments fixed, and leaves small gaps for rest without surfacing a fake “Break” task. Longer personal automation tasks are pushed later while work/client tasks remain in the middle.

**Tests:** `python -m compileall -q app scripts`

**Risks or follow-up:** This is heuristic scheduling, so task classification is based on title/content keywords and estimated duration rather than a user-defined project taxonomy. Longer-term improvements could include explicit tags or project categories for more precise automation.
Read .github/copilot-instructions.md and inspect my existing Python/FastAPI project.

Do not create, edit, move or delete files yet.

Report:

1. The project's purpose and application entry point.
2. The current folder and file structure, excluding virtual environments and generated files.
3. How a request flows through FastAPI, business logic and external API calls.
4. Where task creation currently happens and which files are responsible.
5. Problems with the current architecture, duplicated logic or tightly coupled code.
6. How well the code follows OOP and my compact formatting preferences.
7. The dependencies, required environment variables and available test commands.
8. A proposed target structure mapping existing files to their recommended locations.

For every recommended change, briefly explain why it is needed and what behavior might be affected.

Separate confirmed findings from assumptions. Recommend the smallest practical improvements first. Wait for my approval before changing the project.